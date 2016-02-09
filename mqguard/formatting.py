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

### Initial Data ###############################################################

    def formatInitialData(self, deviceReports):
        """!
        Get string to initiate session.
        """
        data = {"feed": "init", "devices": [], "brokers": []}
        for deviceName, deviceGuard in self.dataProvider.getDevices():
            data["devices"].append(self.createDevice(deviceName, deviceGuard, deviceReports[deviceName]))
        for broker, subscriptions in self.dataProvider.getBrokerListenDescriptors():
            data["brokers"].append(self.createBroker(broker, subscriptions))
        return self.encoder.encode(data)

    def createDevice(self, deviceName, deviceGuard, deviceReport):
        device = {
            "name": deviceName,
            "description": "Device description not implemented yet",
            "status": ["ok", "error"][int(deviceReport.hasFailures())],
            "reasons": self._getReasons(deviceReport),
            "guards": [guard for guard in self.getGuards(deviceGuard)]}
        return device

    def _getReasons(self, deviceReport):
        """!
        Get list of reasons or None.
        """
        if not deviceReport.hasFailures():
            return None
        else:
            return [self.createReason(reason) for reason in deviceReport.getFailures()]

    def createReason(self, failure):
        return None

    def getGuards(self, deviceGuard):
        """!
        get iterable of device guards.
        """
        for updateGuard in deviceGuard.updateGuards:
            yield self.createGuard(updateGuard)

    def createGuard(self, updateGuard):
        jsonDI = "{}:{}".format(updateGuard.dataIdentifier.broker.name, updateGuard.dataIdentifier.topic)
        guard = {
            "dataIdentifier": jsonDI,
            "alarms": [alarm for alarm in self.getAlarms(updateGuard.getAlarmClasses())]}
        return guard

    def getAlarms(self, alarmClasses):
        for alarmClass in alarmClasses:
            yield self.createAlarm(alarmClass)

    def createAlarm(self, alarmClass):
        alarm = {
            "alarm": alarmClass.__name__}
        return alarm

    def createBroker(self, broker, subscriptions):
        data = {
            "name": broker.name,
            "host": broker.host,
            "port": broker.port,
            "public": not broker.isAuthenticationRequired(),
            "subscriptions": subscriptions,}
        return data

### Update #####################################################################

    def formatDeviceReport(self, deviceReport):
        """!
        """
        data = {
            "feed": "update",
            "devices": [{
                "name": deviceReport.device,
                "status": ["ok", "error"][int(deviceReport.hasFailures())],
                "reasons": [self.createReason(changes) for changes in deviceReport.getChanges()]}]}
        return self.encoder.encode(data)

    def getReasons(self):
        """!
        Get iterable of device reasons.
        """

    def createReason(self, changes):
        dataIdentifier, alarm, report = changes
        active, changed, updated, message = report
        reason = {
            "guard": "{}:{}".format(dataIdentifier.broker.name, dataIdentifier.topic),
            "alarm": "{}".format(alarm.__name__),
            "status": ["ok", "error"][int(active)],
            "message": ["ok", message][int(active)]}
        return reason
