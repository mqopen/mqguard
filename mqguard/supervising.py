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

from mqreceive.data import DataIdentifier
from mqguard.alarms import AlarmType

class DeviceRegistry:
    """!
    Group all guarded devices in single registry.
    """

    def __init__(self, reportManager):
        self.reportManager = reportManager
        self.periodicChecker = PeriodicChecker.secondCheck(self, 1)
        self.guardedDevices = []

    def addGuardedDevice(self, device, guard):
        self.guardedDevices.append((device, guard))

    def onMessage(self, broker, topic, data):
        dataIdentifier = DataIdentifier(broker, topic)
        for device, guard in self.guardedDevices:
            di, alarmActive, reason = guard.messageReceived(dataIdentifier, data)
            event = (device, dataIdentifier, alarmActive, reason)
            self.reportManager.reportStatus(event)

    def onPeriodic(self):
        for device, guard in self.guardedDevices:
            di, alarmActive, reason = guard.onPeriodic()
            event = (device, di, alarmActive, reason)
            self.reportManager.reportStatus(event)

    def start(self):
        """!
        """
        threading.Thread(target = self.periodicChecker).start()

    def stop(self):
        """!
        """
        self.periodicChecker.stop()

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

class DeviceGuard:
    """!
    Guarding single device. Device guard groups multimple DataIdentifier objectcs and
    theie alarms. It also have responsibility for checking presence messages.
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
        for updateGuard in self.updateGuards:
            if updateGuard.isUpdateRelevant(dataIdentifier):
                di, active, reason = updateGuard.getUpdateCheck(dataIdentifier, data)
                if active:
                    return (di, active, reason)
        return (di, False, None)

    def onPeriodic(self):
        """!
        Periodic device check.
        """
        for updateGuard in self.updateGuards:
            di, active, reason = updateGuard.getPeriodicCheck()
            if active:
                return (di, active, reason)
        return (None, False, None)

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
        # Notify all periodic alarms.
        for alarm in self.periodicAlarms:
            alarm.notifyMessage(dataIdentifier, payload)
        for alarm in self.messageAlarms:
            active, message = alarm.checkMessage(dataIdentifier, payload)
            if active:
                return (self.dataIdentifier, active, (alarm.__class__, message))
        return (self.dataIdentifier, False, None)

    def getPeriodicCheck(self):
        """!
        Periodic checking for update timeouts.

        @return Tuple with check report. If check is OK: (True, None). If error
            is detected: (False, errorMessage).
        """
        for alarm in self.periodicAlarms:
            active, message = alarm.checkPeriodic()
            if active:
                return (self.dataIdentifier, active, (alarm.__class__, message))
        return (self.dataIdentifier, False, None)

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
