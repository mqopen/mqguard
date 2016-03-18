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

    ## @var reportManager
    ## @var periodicChecker
    ## @var guardedDevices

    ## @var alarmMapping
    # Mapping device : DataIdentifier : alarm : alarmTrack

    ## @var presenceMapping
    # Mapping device : presenceTrack

    def __init__(self, reportManager):
        """!
        Initiate DeviceRegistry object.

        @param reportManager ReportingManager object.
        """
        self.reportManager = reportManager
        self.periodicChecker = PeriodicChecker.secondCheck(self, 1)
        self.guardedDevices = {}
        self.alarmMapping = {}
        self.presenceMapping = {}

        # Inject device registry to all reporters.
        self.reportManager.injectDeviceRegistry(self)

    def addGuardedDevice(self, device, guard):
        """!
        Register new guarded device.

        @param device Device identifier.
        @param guard DeviceGuard object.
        """
        self.guardedDevices[device] = guard
        self.addAlarmTrack(device, guard)

    def addAlarmTrack(self, device, guard):
        """!
        Add guarded device into alarmMapping object and initialize presenceMapping object.

        @param device Device identifier.
        @param guard DeviceGuard object.
        """
        self.alarmMapping[device] = {}
        guardAlarms = guard.getGuardAlarms()
        for dataIdentifier in guardAlarms:
            self.alarmMapping[device][dataIdentifier] = {}
            for alarm in guardAlarms[dataIdentifier]:
                self.alarmMapping[device][dataIdentifier][alarm] = self.createAlarmTrack()
        self.presenceMapping[device] = self.createPresence(guard)

    def createAlarmTrack(self):
        """!
        Create initial alarm track tuple.

        @return Initial alarm track tuple.
        """
        active = False
        changed = False
        updated = False
        message = None
        return active, changed, updated, message

    def createPresence(self, guard):
        """
        Create presence track object.
        """
        devicePresence = guard.getPresence()
        track = self.createPresenceTrack(guard.hasPresence())
        return devicePresence, track

    def createPresenceTrack(self, hasPresence):
        """!
        Create initial presence status tuple.

        @param hasPresence Boolean object indication whether device has configured
            presence topic. Devices with presence topic set has initial alarm state
            active, until first presence message is received.
        @return Initial presence status tuple.
        """
        active = False
        changed = False
        updated = False
        message = None
        if hasPresence:
            active = True
            message = "Presence message not received yet"
        return active, changed, updated, message

    def onMessage(self, broker, topic, data):
        """'
        Message event.

        @param broker Broker object which message came from.
        @param topic Message topic.
        @param data Message bytes.
        """
        dataIdentifier = DataIdentifier(broker, topic)
        for device, deviceGuard in self.guardedDevices.items():
            result = deviceGuard.messageReceived(dataIdentifier, data)
            for di, alarms in result.updateGuardMapping.items():
                self.setChanges(device, di, alarms)
            if result.hasPresenceUpdate():
                self.updateDevicePresence(device, result.presenceAlarms)
            self.makeReport(device)

    def onPeriodic(self):
        """!
        Periodic alarm check.
        """
        for device, deviceGuard in self.guardedDevices.items():
            result = deviceGuard.onPeriodic();
            for di, alarms in result.updateGuardMapping.items():
                self.setChanges(device, di, alarms)
            self.makeReport(device)

    def makeReport(self, device):
        """!
        Notify report manager with new report. After that clear all changes for the device.

        @param device Reported device.
        """
        report = self.getReport(device)
        self.reportManager.report(report)
        self.clearChanges(device)

    def setChanges(self, device, dataIdentifier, alarms):
        for alarm in alarms:
            active, message = alarms[alarm]
            wasActive, changed, updated, previousMessage = self.alarmMapping[device][dataIdentifier][alarm]
            _changed = False
            if active != wasActive:
                _changed = True
            _updated = True
            self.alarmMapping[device][dataIdentifier][alarm] = (active, _changed, _updated, message)

    def updateDevicePresence(self, device, presenceAlarms):
        devicePresence, track = self.presenceMapping[device]
        wasActive, changed, updated, previousMessage = track
        for alarm in presenceAlarms:
            isActive, message = presenceAlarms[alarm]
            _changed = False
            if isActive != wasActive:
                _changed = True
            _updated = True
            track = isActive, _changed, _updated, message
            self.presenceMapping[device] = devicePresence, track
            break

    def clearChanges(self, device):
        for dataIdentifier in self.alarmMapping[device]:
            for alarm in self.alarmMapping[device][dataIdentifier]:
                active, changed, updated, message = self.alarmMapping[device][dataIdentifier][alarm]
                self.alarmMapping[device][dataIdentifier][alarm] = (active, False, False, message)
        devicePresence, track = self.presenceMapping[device]
        active, changed, updated, message = track
        track = active, False, False, message
        self.presenceMapping[device] = devicePresence, track

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
        for device in self.alarmMapping:
            reports[device] = self.getReport(device)
        return reports

    def getReport(self, device):
        """!
        Create report object for device.

        @param device Reported device.
        @return DeviceReport object.
        """
        presence = copy.deepcopy(self.presenceMapping[device])
        alarms = copy.deepcopy(self.alarmMapping[device])
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

        @param presence DevicePresence object.
        @param presenceGuard Presence UpdateGuard object.
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

        @return Mapping of DataIdentifier: alarmMapping.
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
            updateGuardMapping[updateGuard.dataIdentifier] = alarms
        return DeviceGuardResult(None, updateGuardMapping)

    def getGuardAlarms(self):
        """!
        Get mapping of DataIdentifier: Alarm iterable.
        """
        alarms = {}
        for updateGuard in self.updateGuards:
            alarms[updateGuard.dataIdentifier] = updateGuard.getAlarms()
        return alarms

    def getPresence(self):
        """
        Get presence object.

        @return DevicePresence object.
        """
        return self.presence

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
        @return Tuple with check report. If check is OK: (False, None). If error
            is detected: (False, errorMessage).
        """
        alarms = {}
        # Notify all periodic alarms.
        for alarm in self.periodicAlarms:
            deactivated = alarm.notifyMessage(dataIdentifier, payload)
            if deactivated:
                alarms[alarm] = (False, None)
        for alarm in self.messageAlarms:
            alarms[alarm] = alarm.checkMessage(dataIdentifier, payload)
        return alarms

    def getPeriodicCheck(self):
        """!
        Periodic checking for update timeouts.

        @return Tuple with check report. If check is OK: (False, None). If error
            is detected: (False, errorMessage).
        """
        alarms = {}
        for alarm in self.periodicAlarms:
            alarms[alarm] = alarm.checkPeriodic()
        return alarms

    def isUpdateRelevant(self, updateDataIdentifier):
        """!
        Check if update is relevant to this update guard.

        @param updateDataIdentifier Update DataIdentifier object.
        @return True if relevant, False otherwise.
        """
        return updateDataIdentifier == self.dataIdentifier

    def getAlarms(self):
        """!
        Get all registered alarms.

        @return Alarms iterable.
        """
        for alarm in self.messageAlarms:
            yield alarm
        for alarm in self.periodicAlarms:
            yield alarm

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

    ## @var registry
    ## @var period
    ## @var event
    ## @var running

    def __init__(self, registry, period):
        """'
        Initialize PeriodicChecker object.

        @param registry DeviceRegistry object.
        @param period timedelta object defining check period.
        """
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
        Stop periodic checker thread.
        """
        self.running = False
        self.event.set()
