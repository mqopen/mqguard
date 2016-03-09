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
import copy

from mqreceive.data import DataIdentifier
from mqguard.alarms import AlarmType
from mqguard.common import DeviceReport

class DeviceRegistry:
    """!
    Group all guarded devices in single registry.
    """

    def __init__(self, reportManager):
        self.reportManager = reportManager
        self.periodicChecker = PeriodicChecker.secondCheck(self, 1)
        self.guardedDevices = {}
        self.alarmStates = {}
        self.presenceMapping = {}

        # Inject device registry to all reporters.
        self.reportManager.injectDeviceRegistry(self)

    def addGuardedDevice(self, device, guard):
        self.guardedDevices[device] = guard
        self.addAlarmTrack(device, guard)

    def addAlarmTrack(self, device, guard):
        self.alarmStates[device] = {}
        guardAlarms = guard.getGuardAlarms()
        for dataIdentifier in guardAlarms:
            self.alarmStates[device][dataIdentifier] = {}
            for alarmClass in guardAlarms[dataIdentifier]:
                self.alarmStates[device][dataIdentifier][alarmClass] = self.createAlarmTrack()
        self.presenceMapping[device] = self.createPresence(guard)

    def createAlarmTrack(self):
        active = False
        changed = False
        updated = False
        message = None
        return active, changed, updated, message

    def createPresence(self, guard):
        active = False
        changed = False
        updated = False
        message = None
        if guard.hasPresence():
            active = True
            message = "Online message not received yet"
        return active, changed, updated, message

    def onMessage(self, broker, topic, data):
        dataIdentifier = DataIdentifier(broker, topic)
        for device, deviceGuard in self.guardedDevices.items():
            result = deviceGuard.messageReceived(dataIdentifier, data)
            for di, alarms in result.updateGuardMapping.items():
                self.setChanges(device, di, alarms)
            if result.hasPresenceUpdate():
                self.updateDevicePresence(device, result.presenceAlarms)
            self.makeReport(device)

    def onPeriodic(self):
        return
        for device, deviceGuard in self.guardedDevices.items():
            for di, alarms in deviceGuard.onPeriodic():
                self.setChanges(device, di, alarms)
            self.makeReport(device)

    def makeReport(self, device):
        report = self.getReport(device)
        self.reportManager.report(report)
        self.clearChanges(device)

    def setChanges(self, device, dataIdentifier, alarms):
        for alarm in alarms:
            active, message = alarms[alarm]
            wasActive, changed, updated, previousMessage = self.alarmStates[device][dataIdentifier][alarm]
            _changed = False
            if active != wasActive:
                _changed = True
            _updated = True
            self.alarmStates[device][dataIdentifier][alarm] = (active, _changed, _updated, message)

    def updateDevicePresence(self, device, presenceAlarms):
        wasActive, changed, updated, previousMessage =  self.presenceMapping[device]
        for alarm in presenceAlarms:
            isActive, message = presenceAlarms[alarm]
            _changed = False
            if isActive != wasActive:
                _changed = True
            _updated = True
            self.presenceMapping[device] = (isActive, _changed, _updated, message)
            break

    def clearChanges(self, device):
        for dataIdentifier in self.alarmStates[device]:
            for alarm in self.alarmStates[device][dataIdentifier]:
                active, changed, updated, message = self.alarmStates[device][dataIdentifier][alarm]
                self.alarmStates[device][dataIdentifier][alarm] = (active, False, False, message)
        active, changed, updated, message = self.presenceMapping[device]
        self.presenceMapping[device] = active, False, False, message

    def start(self):
        """!
        """
        threading.Thread(target = self.periodicChecker).start()

    def stop(self):
        """!
        """
        self.periodicChecker.stop()

    def getDeviceReports(self):
        reports = {}
        for device in self.alarmStates:
            reports[device] = self.getReport(device)
        return reports

    def getReport(self, device):
        presence = copy.deepcopy(self.presenceMapping[device])
        alarms = copy.deepcopy(self.alarmStates[device])
        return DeviceReport(device, presence, alarms)

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
        self.presenceGuard = None
        self.presence = None

    def addPresenceGuard(self, presence, presenceGuard):
        """
        Add check for presence message.
        """
        self.presence = presence
        self.presenceGuard = presenceGuard

    def hasPresence(self):
        return self.presenceGuard is not None

    def addUpdateGuard(self, updateGuard):
        """"!
        Add update guard object.
        """
        self.updateGuards.append(updateGuard)

    def messageReceived(self, dataIdentifier, data):
        """!
        New message was received.

        @return Mapping of DataIdentifier: alarmStates.
        """
        updateGuardMapping = {}
        presenceAlarms = None
        if self.presenceGuard is not None and self.presenceGuard.isUpdateRelevant(dataIdentifier):
            presenceAlarms = self.presenceGuard.getUpdateCheck(dataIdentifier, data)
        for updateGuard in self.updateGuards:
            if updateGuard.isUpdateRelevant(dataIdentifier):
                alarms = updateGuard.getUpdateCheck(dataIdentifier, data)
                updateGuardMapping[dataIdentifier] = alarms
        return DeviceGuardResult(presenceAlarms, updateGuardMapping)

    def onPeriodic(self):
        """!
        Periodic device check.
        """
        updateGuardMapping = {}
        for updateGuard in self.updateGuards:
            alarms = updateGuard.getPeriodicCheck()
        return DeviceGuardResult(None, updateGuardMapping)

    def getGuardAlarms(self):
        """!
        Get mapping of DataIdentifier: Alarm class iterable.
        """
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
        alarms = {}
        # Notify all periodic alarms.
        for alarm in self.periodicAlarms:
            deactivated = alarm.notifyMessage(dataIdentifier, payload)
            if deactivated:
                alarms[alarm.__class__] = (False, None)
        for alarm in self.messageAlarms:
            result = alarm.checkMessage(dataIdentifier, payload)
            alarms[alarm.__class__] = result
        return alarms

    def getPeriodicCheck(self):
        """!
        Periodic checking for update timeouts.

        @return Tuple with check report. If check is OK: (True, None). If error
            is detected: (False, errorMessage).
        """
        alarms = {}
        for alarm in self.periodicAlarms:
            result = alarm.checkPeriodic()
            alarms[alarm] = result
        return alarms

    def isUpdateRelevant(self, updateDataIdentifier):
        """!
        Check if update is relevant to this update guard.

        @return True if relevant, False otherwise.
        """
        return updateDataIdentifier == self.dataIdentifier

    def getAlarms(self):
        for alarm in self.messageAlarms:
            yield alarm
        for alarm in self.periodicAlarms:
            yield alarm

    def getAlarmClasses(self):
        """!
        Get iterable of all used alarm classes.

        @return Iterable of alarm classes
        """
        for alarm in self.getAlarms():
            yield alarm.__class__

class DeviceGuardResult:
    """!
    Package class for device guard result.
    """

    def __init__(self, presenceAlarms, updateGuardMapping):
        self.presenceAlarms = presenceAlarms
        self.updateGuardMapping = updateGuardMapping

    def hasPresenceUpdate(self):
        return self.presenceAlarms is not None

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
