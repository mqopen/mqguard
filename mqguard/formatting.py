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

    def formatInitialData(self):
        """!
        Get string to initiate session.
        """
        data = {"feed": "init", "devices": [], "brokers": []}
        for deviceName, deviceGuard in self.dataProvider.getDevices():
            data["devices"].append(self.createDevice(deviceName, deviceGuard))
        for broker, subscriptions in self.dataProvider.getBrokerListenDescriptors():
            data["brokers"].append(self.createBroker(broker, subscriptions))
        return self.encoder.encode(data)

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

    def createReason(self, changes):
        dataIdentifier, alarm, report = changes
        active, changed, updated, message = report
        reason = {
            "guard": "{}:{}".format(dataIdentifier.broker.name, dataIdentifier.topic),
            "alarm": "{}".format(alarm.__name__),
            "status": ["ok", "error"][int(active)],
            "message": ["ok", message][int(active)]}
        return reason

    def createDevice(self, deviceName, deviceGuard):
        device = {
            "name": deviceName,
            "description": None,
            "guards": [guard for guard in self.getGuards(deviceGuard)]}
        return device

    def getGuards(self, deviceGuard):
        """!
        get iterable of device guards.
        """
        for updateGuard in deviceGuard.updateGuards:
            yield self.createGuard(updateGuard)

    def createGuard(self, updateGuard):
        guard = {
            "name": updateGuard.name,
            "di": str(updateGuard.dataIdentifier)}
        return guard

    def createBroker(self, broker, subscriptions):
        data = {
            "name": broker.name,
            "host": broker.host,
            "port": broker.port,
            "public": not broker.isAuthenticationRequired(),
            "subscriptions": subscriptions,}
        return data
