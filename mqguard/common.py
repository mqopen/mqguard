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

    def __init__(self, device, alarmStates):
        self.device = device
        self.alarmStates = alarmStates
        self._hasChanges, self._hasUpdates, self._hasFailures = self.createFlags()

    def createFlags(self):
        hasChanges = False
        hasUpdates = False
        hasFailures = False
        for alarmMapping in self.alarmStates.values():
            for active, changed, updated, message in alarmMapping.values():
                if active:
                    hasFailures = True
                if changed:
                    hasChanges = True
                if updated:
                    hasUpdates = True
                if hasFailures and hasUpdates and hasChanges:
                    return hasChanges, hasUpdates, hasFailures
        return hasChanges, hasUpdates, hasFailures

    def hasChanges(self):
        """!
        """
        return self._hasChanges

    def hasUpdates(self):
        """!
        """
        return self._hasUpdates

    def hasFailures(self):
        """!
        """
        return self._hasFailures

    def getReport(self):
        """!
        """
        return self.alarmStates

    def getChanges(self):
        """!
        """
        for dataIdentifier in self.alarmStates:
            for alarm in self.alarmStates[dataIdentifier]:
                active, changed, updated, message = self.alarmStates[dataIdentifier][alarm]
                if changed:
                    yield (dataIdentifier, alarm, message)

    def getFailures(self):
        """!
        """

    def getSummary(self):
        """!
        Get summary string.
        """
        return "{} - failures: {}, changes: {}, updates: {}".format(
                self.device,
                self.hasFailures(),
                self.hasChanges(),
                self.hasUpdates())
