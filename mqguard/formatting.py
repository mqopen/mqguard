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

import json

class FormatDataProvider:
    """!
    Interface for providing necessary data for formatters.
    """

    def getBrokerListenDescriptors(self):
        """!
        Get information about connected brokers.
        """

    def getDevices(self):
        """!
        Get guarded devices.

        @return Iterable of tuples (device, guard).
        """

    def injectSystemClass(self, systemClass):
        """!
        """

class SystemDataProvider(FormatDataProvider):
    """!
    Provide data from system static object.
    """

    def injectSystemClass(self, systemClass):
        self.systemClass = systemClass

    def getBrokerListenDescriptors(self):
        return self.systemClass.getBrokerListenDescriptors()

    def getDevices(self):
        return self.systemClass.getDeviceGuards()

class BaseFormatter:
    """!
    Formatter base class
    """

    def __init__(self, dataProvider):
        self.dataProvider = dataProvider

    def injectSystemClass(self, systemClass):
        self.dataProvider.injectSystemClass(systemClass)

class JSONFormatter(BaseFormatter):
    """!
    JSON formatting.
    """

    def __init__(self, dataProvider):
        BaseFormatter.__init__(self, dataProvider)
        self.encoder = json.JSONEncoder(indent = 4)
        self.deviceInitFormatting = JSONDevicesInitFormatting(dataProvider)
        self.brokerInitFormatting = JSONBrokersInitFromatting(dataProvider)
        self.deviceUpdateFormatting = JSONDevicesUpdateFormatting()

    def formatInitialData(self, deviceReports):
        """!
        Get string to initiate session.
        """
        return self.encoder.encode({
            "feed": "init",
            "devices": self.deviceInitFormatting.formatInitialData(deviceReports),
            "brokers": self.brokerInitFormatting.formatInitialData(deviceReports)})

    def formatDeviceReport(self, deviceReport):
        """!
        """
        return self.encoder.encode({
            "feed": "update",
            "devices": self.deviceUpdateFormatting.formatDeviceReport(deviceReport)})

class JSONFormatting:
    """!
    Base class of formatting part of JSON output.
    """

    def formatDataIdentifier(self, dataIdentifier):
        return {
            "broker": dataIdentifier.broker.name,
            "topic": dataIdentifier.topic}

    def formatStatus(self, isInError):
        return ["ok", "error"][int(isInError)]

class JSONInitFormatting(JSONFormatting):

    def __init__(self, dataProvider):
        self.dataProvider = dataProvider

class JSONDevicesInitFormatting(JSONInitFormatting):
    """!
    Generate device part of JSON report.
    """

    def formatInitialData(self, deviceReports):
        """!
        """
        devices = []
        for deviceName, deviceGuard in self.dataProvider.getDevices():
            devices.append(
                self.createDevice(deviceName, deviceGuard, deviceReports[deviceName]))
        return devices

    def createDevice(self, deviceName, deviceGuard, deviceReport):
        return {
            "name": deviceName,
            "description": "Device description not implemented yet",
            "status": self.formatStatus(deviceReport.hasFailures() or deviceReport.hasPresenceFailure()),
            "presence": self.createPresence(deviceName, deviceGuard),
            "guards": [guard for guard in self.getGuards(deviceGuard)],
            "reasons": self.getReasons(deviceReport)}

    def createPresence(self, deviceName, deviceGuard):
        """!
        """
        if deviceGuard.hasPresence():
            return self.createEnabledPresence(deviceName, deviceGuard)
        else:
            return self.createDisabledPresence(deviceName, deviceGuard)

    def createEnabledPresence(self, deviceName, deviceGuard):
        diStr = self.formatDataIdentifier(deviceGuard.presence.dataIdentifier)
        online, offline = deviceGuard.getPresence().values
        return {
            "isEnabled": True,
            "dataIdentifier": diStr,
            "onlineMessage": online,
            "offlineMessage": offline}

    def createDisabledPresence(self, deviceName, deviceGuard):
        return {
            "isEnabled": False,
            "dataIdentifier": None,
            "onlineMessage": None,
            "offlineMessage": None}

    def getGuards(self, deviceGuard):
        """!
        get iterable of device guards.
        """
        for updateGuard in deviceGuard.updateGuards:
            yield self.createGuard(updateGuard)

    def getReasons(self, deviceReport):
        """!
        Get list of reasons or None.
        """
        return {
            "presence": self.getPresenceReason(deviceReport),
            "guards": self.getGuardsReasons(deviceReport)}

    def getPresenceReason(self, deviceReport):
        """!
        """
        if deviceReport.hasPresenceFailure():
            devicePresence, track = deviceReport.getPresence()
            _, _, _, msg = track
            return {
                "status": self.formatStatus(deviceReport.hasPresenceFailure()),
                "message": msg}
        else:
            return None

    def getGuardsReasons(self, deviceReport):
        """!
        """
        return [self.createReason(failures) for failures in deviceReport.getFailures()]

    def createReason(self, changes):
        dataIdentifier, alarm, report = changes
        active, changed, updated, message = report
        return {
            "guard": self.formatDataIdentifier(dataIdentifier),
            "alarm": "{}".format(alarm.getName()),
            "status": self.formatStatus(active),
            "message": self.formatStatus(active)}

    def createGuard(self, updateGuard):
        return {
            "dataIdentifier": self.formatDataIdentifier(updateGuard.dataIdentifier),
            "alarms": [alarm for alarm in self.getAlarms(updateGuard.getAlarms())]}

    def getAlarms(self, alarms):
        for alarm in alarms:
            yield self.createAlarm(alarm)

    def createAlarm(self, alarm):
        return {
            "alarm": alarm.getName(),
            "criteria": alarm.getCriteria()}

class JSONBrokersInitFromatting(JSONInitFormatting):
    """!
    Generate broker part of JSON report.
    """

    def formatInitialData(self, deviceReports):
        """!
        """
        brokers = []
        for broker, subscriptions in self.dataProvider.getBrokerListenDescriptors():
            brokers.append(self.createBroker(broker, subscriptions))
        return brokers

    def createBroker(self, broker, subscriptions):
        return {
            "name": broker.name,
            "host": broker.host,
            "port": broker.port,
            "public": not broker.isAuthenticationRequired(),
            "subscriptions": subscriptions}

class JSONUpdateFormatting(JSONFormatting):
    """!
    """

class JSONDevicesUpdateFormatting(JSONUpdateFormatting):
    """!
    """

    def formatDeviceReport(self, deviceReport):
        return [self.createDevice(deviceReport)]

    def createDevice(self, deviceReport):
        return {
            "name": deviceReport.device,
            "status": self.formatStatus(deviceReport.hasFailures()),
            "reasons": self.createReasons(deviceReport)}

    def createReasons(self, deviceReport):
        return {
            "presnce": self.createPresenceReason(deviceReport),
            "guards": self.createGuardsReasons(deviceReport)}

    def createPresenceReason(self, deviceReport):
        if deviceReport.hasPresenceUpdate():
            devicePresence, track = deviceReport.getPresence()
            _, _, _, msg = track
            return {
                "status": self.formatStatus(deviceReport.hasPresenceFailure()),
                "message": msg}
        else:
            return None

    def createGuardsReasons(self, deviceReport):
        return [self.createGuardsReason(reason) for reason in deviceReport.getChanges()]

    def createGuardsReason(self, change):
        dataIdentifier, alarm, report = change
        active, changed, updated, message = report
        return {
            "guard": self.formatDataIdentifier(dataIdentifier),
            "alarm": "{}".format(alarm.getName()),
            "status": self.formatStatus(active),
            "message": ["ok", message][int(active)]}
