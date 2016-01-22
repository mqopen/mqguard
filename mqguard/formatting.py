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

    def getBrokers(self):
        """!
        Get information about connected brokers.
        """

    def getDevices(self):
        """!
        Get guarded devices.

        @return Iterable of tuples (device, guard).
        """

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

    def getInitialData(self):
        """!
        """
        data = {"foo": "bar", "seq": [x for x in range(10)]}
        data["feed"] = "init"
        return self.encoder.encode(data)

    def formatUpdate(self, event):
        """!
        """
        data = {}
        data["feed"] = "update"
        data["devices"] = []

        device = {}
        device["name"] = event.device
        device["messages"] = []
        device["messages"].append(event.reason)

        data["devices"].append(device)
        return self.encoder.encode(data)
