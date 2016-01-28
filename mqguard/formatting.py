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
        return []

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
        """
        data = {"feed": "update", "devices": [], "brokers": []}
        for device in self.dataProvider.getDevices():
            data["devices"].append(device)
        for broker, subscriptions in self.dataProvider.getBrokerListenDescriptors():
            data["brokers"].append(self.createBroker(broker, subscriptions))
        return self.encoder.encode(data)

    def formatUpdate(self, event):
        """!
        """
        device, isOK, reason = event
        dataIdentifier, alarmClass, message = reason
        data = {
            "feed": "update",
            "devices": [{
                "name": device,
                "status": ["ok", "error"][int(isOK)],
                "reason": {
                    "alarm": alarmClass.__name__,
                    "message": message}}]}
        return self.encoder.encode(data)

    def formatDeviceReport(self, deviceReport):
        """!
        """
        device, guardsMapping = deviceReport
        data = {
            "feed": "update",
            "devices": [{
                "name": device,
                "status": ["ok", "error"][int(len(guardsMapping) > 0)],
                "reasons": [
                    self.createDeviceReportReason(di, alarmMapping) for di, alarmMapping in guardsMapping.items()]}]}
        return self.encoder.encode(data)

    def createDeviceReportReason(self, dataIdentifier, alarmMapping):
        reason = {dataIdentifier: alarmMapping}
        return reason

    def createBroker(self, broker, subscriptions):
        data = {
            "name": broker.name,
            "host": broker.host,
            "port": broker.port,
            "public": not broker.isAuthenticationRequired(),
            "subscriptions": subscriptions,}
        return data

    def createDevice(self, device):
        data = {}
        return data
