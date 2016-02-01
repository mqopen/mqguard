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

import pprint

class GeographicPosition:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

class DeviceReport:
    """!
    """

    def __init__(self, alarmStates):
        self.alarmStates = alarmStates
        self._hasChanges = False
        self._hasUpdates = False
        self._hasFailures = False

        self.pp = pprint.PrettyPrinter()

    def hasChanges(self):
        """!
        """

    def hasUpdates(self):
        """!
        """

    def hasFailures(self):
        """!
        """

    def getReport(self):
        """!
        """
        return self.alarmStates

    def getChanges(self):
        """!
        """

    def getFailures(self):
        """!
        """

    def makePrettyPrint(self):
        #self.pp.pprint(self.alarmStates)
        print(self.alarmStates)
