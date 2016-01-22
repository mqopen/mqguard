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
from mqguard.system import System

class FormatDataProvider:
    """!
    Interface for providing necessary data for formatters.
    """

    def getBrokers(self):
        """!
        Get information about connected brokers.
        """

    def getDevices(self):
        """!
        Get guarded devices.

        @return Iterable of tuples (device, guard).
        """

class SystemDataProvider(FormatDataProvider):
    """!
    Provide data from system static object.
    """

    def getBrokers(self):
        return System.getBrokerListenDescriptors()

class BaseFormatter:
    """!
    Formatter base class
    """

    def __init__(self, dataProvider):
        self.dataProvider = dataProvider

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
        for broker in self.dataProvider.getBrokers():
            data["brokers"].append(broker)
        return self.encoder.encode(data)

    def formatUpdate(self, event):
        """!
        """
        data = {"feed": "update"}
        data["devices"] = []

        device = {}
        device["name"] = event.device
        device["status"] = ["ok", "error"][int(event.isErrorOccured())]
        device["reason"] = None
        if event.isErrorOccured():
            device["reason"] = {}
            device["reason"]["message"] = event.reason

        data["devices"].append(device)
        return self.encoder.encode(data)
