# Copyright (C) Ivo Slanina <ivo.slanina@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""!
Supervising at endividual MQTT endpoints.
"""

import threading
import datetime
import pprint

from mqreceive.data import DataIdentifier
from mqguard.alarms import AlarmType

class DeviceRegistry:
    """!
    Group all guarded devices in single registry.
    """

    def __init__(self, reportManager):
        self.reportManager = reportManager
        self.periodicChecker = PeriodicChecker.secondCheck(self, 1)
        self.guardedDevices = {}
        self.alarmStates = {}
        self.pp = pprint.PrettyPrinter()

    def addGuardedDevice(self, device, guard):
        self.guardedDevices[device] = guard
        self.addAlarmTrack(device, guard)

    def addAlarmTrack(self, device, guard):
        self.alarmStates[device] = {}
        guardAlarms = guard.getGuardAlarms()
        for dataIdentifier in guardAlarms:
            self.alarmStates[device][dataIdentifier] = {}
            for alarmClass in guardAlarms[dataIdentifier]:
                self.alarmStates[device][dataIdentifier][alarmClass] = (False, False, None)

    def onMessage(self, broker, topic, data):
        dataIdentifier = DataIdentifier(broker, topic)
        for device, deviceGuard in self.guardedDevices.items():
            for di, alarms in deviceGuard.messageReceived(dataIdentifier, data).items():
                self.alarmStates[device][di]
            self.makeReport(device)

    def onPeriodic(self):
        for device, deviceGuard in self.guardedDevices.items():
            for di, alarms in deviceGuard.onPeriodic():
                pass
            self.makeReport(device)

    def makeReport(self, device):
        #self.reportManager.report(device, self.alarmStates[device])
        self.pp.pprint(self.alarmStates)
        for i in range(5):
            print("")

    def setChange(self):
        pass

    def clearChanges(self):
        for device in self.guardedDevices:
            for dataIdentifier in self.guardedDevices[device]:
                for alarm in self.guardedDevices[device][dataIdentifier]:
                    active, changed, message = self.guardedDevices[device][dataIdentifier][alarm]
                    self.guardedDevices[device][dataIdentifier][alarm] = (active, False, message)

    def start(self):
        """!
        """
        threading.Thread(target = self.periodicChecker).start()

    def stop(self):
        """!
        """
        self.periodicChecker.stop()

class DeviceGuard:
    """!
    Guarding single device. Device guard groups multimple DataIdentifier objectcs and
    their alarms. It also have responsibility for checking presence messages.
    """

    ## @var updateGuards
    # List of update guards objects.

    def __init__(self):
        """!
        Initiate guarded device.

        @param name Device name.
        """
        self.updateGuards = []

    def addPresenceGuard(self, presenceIdentifier, valuesDescription):
        """
        Add check for presence message.
        """

    def addUpdateGuard(self, updateGuard):
        """"!
        Add update guard object.
        """
        self.updateGuards.append(updateGuard)

    def messageReceived(self, dataIdentifier, data):
        """!
        New message was received.
        """
        results = {}
        for updateGuard in self.updateGuards:
            if updateGuard.isUpdateRelevant(dataIdentifier):
                alarms = updateGuard.getUpdateCheck(dataIdentifier, data)
                results[dataIdentifier] = alarms
        return results

    def onPeriodic(self):
        """!
        Periodic device check.
        """
        results = []
        for updateGuard in self.updateGuards:
            result = updateGuard.getPeriodicCheck()
            results.append((updateGuard.dataIdentifier, result))
        return results

    def getGuardAlarms(self):
        alarms = {}
        for updateGuard in self.updateGuards:
            alarms[updateGuard.dataIdentifier] = updateGuard.getAlarmClasses()
        return alarms

class UpdateGuard:
    """!
    Checking single update.
    """

    ## @var name
    # Name of update guard.

    ## @var dataIdentifier
    # DataIdentifier object.

    ## @var messageAlarms
    # List of message driven alarms.

    ## @var periodicAlarms
    # List of periodic alarms.

    def __init__(self, name, dataIdentifier):
        """!
        Initiate update guard object.

        @param name Name of update guard.
        @param dataIdentifier DataIdentifier object.
        """
        self.name = name
        self.dataIdentifier = dataIdentifier
        self.messageAlarms = []
        self.periodicAlarms = []

    def addAlarm(self, alarm):
        """!
        Add alarm check object.
        """
        if alarm.alarmType is AlarmType.messageDriven:
            self.messageAlarms.append(alarm)
        else:
            self.periodicAlarms.append(alarm)

    def getUpdateCheck(self, dataIdentifier, payload):
        """!
        Check update message and return report.

        @param dataIdentifier DataIdentifier object.
        @param payload MQTT data.
        @return Tuple with check report. If check is OK: (True, None). If error
            is detected: (False, errorMessage).
        """
        alarms = []
        # Notify all periodic alarms.
        for alarm in self.periodicAlarms:
            deactivated = alarm.notifyMessage(dataIdentifier, payload)
            if deactivated:
                alarms.append((False, None))
        for alarm in self.messageAlarms:
            result = alarm.checkMessage(dataIdentifier, payload)
            alarms.append(result)
        return alarms

    def getPeriodicCheck(self):
        """!
        Periodic checking for update timeouts.

        @return Tuple with check report. If check is OK: (True, None). If error
            is detected: (False, errorMessage).
        """
        alarms = []
        for alarm in self.periodicAlarms:
            result = alarm.checkPeriodic()
            alarms.append(result)
        return alarms

    def isUpdateRelevant(self, updateDataIdentifier):
        """!
        Check if update is relevant to this update guard.

        @return True if relevant, False otherwise.
        """
        return updateDataIdentifier == self.dataIdentifier

    def getAlarmClasses(self):
        alarmClasses = []
        for alarm in self.messageAlarms:
            alarmClasses.append(alarm.__class__)
        for alarm in self.periodicAlarms:
            alarmClasses.append(alarm.__class__)
        return alarmClasses

class PeriodicChecker:
    """!
    Separate tread which periodicall invokes onPeriodic() method of DeviceRegistry object.
    """

    def __init__(self, registry, period):
        self.registry = registry
        self.period = period
        self.event = threading.Event()
        self.running = False

    @classmethod
    def secondCheck(cls, registry, seconds):
        return cls(registry, datetime.timedelta(seconds = seconds))

    def __call__(self):
        """!
        Periodically invoke check logic.
        """
        self.running = True
        while self.running:
            scheduleExpires = not self.event.wait(self.period.total_seconds())
            if scheduleExpires:
                self.registry.onPeriodic()

    def stop(self):
        """!
        """
        self.running = False
        self.event.set()
