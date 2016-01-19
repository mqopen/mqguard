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

from mqreceive.data import DataIdentifier
from mqguard.alarms import AlarmType
from mqguard.reporting import ReportResult

class DeviceRegistry:
    """!
    Group all guarded devices in single registry.
    """

    def __init__(self, reportManager):
        self.reportManager = reportManager
        self.periodicChecker = PeriodicChecker(self)
        self.guardedDevices = []

    def addGuardedDevice(self, deviceGuard):
        self.guardedDevices.append(deviceGuard)

    def onMessage(self, broker, topic, data):
        dataIdentifier = DataIdentifier(broker, topic)
        for deviceGuard in self.guardedDevices:
            reportResult = deviceGuard.messageReceived(dataIdentifier, data)
            if reportResult.isErrorOccured():
                self.reportManager.reportStatus(reportResult)

    def onPeriodicCheck(self):
        for deviceGuard in self.guardedDevices:
            deviceGuard.onPeriodic()

class PeriodicChecker:

    # TODO: refactor registry to more meaningful name
    def __init__(self, registry):
        self.registry = registry

    def __call__(self):
        """!
        Periodically invoke check logic.
        """

class DeviceGuard:
    """!
    Guarding single device.
    """

    ## @var name
    # Device name.

    ## @var updateGuards
    # List of update guards objects.

    def __init__(self, name):
        """!
        Initiate guarded device.

        @param name Device name.
        """
        self.name = name
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
        errors = []
        for updateGuard in self.updateGuards:
            if updateGuard.isUpdateRelevant(dataIdentifier):
                isOK, message = updateGuard.getUpdateCheck(dataIdentifier, data)
                if not isOK:
                    errors.append(message)
        return ReportResult(self.name, errors)

    def onPeriodic(self):
        """!
        Periodic device check.
        """

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
        for alarm in self.messageAlarms:
            result, message = alarm.checkMessage(dataIdentifier, payload)
            if not result:
                return (result, message)
        return (True, None)

    def getPeriodicCheck(self):
        """!
        Periodic checking for update timeouts.

        @return Tuple with check report. If check is OK: (True, None). If error
            is detected: (False, errorMessage).
        """
        for alarm in self.periodicAlarms:
            result, message = alarm.checkPeriodic()
            if result is False:
                return (False, message)
        return (True, None)

    def isUpdateRelevant(self, updateDataIdentifier):
        """!
        Check if update is relevant to this update guard.

        @return True if relevant, False otherwise.
        """
        return updateDataIdentifier == self.dataIdentifier
