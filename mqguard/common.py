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

    def __init__(self, device, presence, alarmStates):
        self.device = device
        self.presence = presence
        self.alarmStates = alarmStates
        (self._hasChanges,
            self._hasUpdates,
            self._hasFailures,
            self._hasPresenceChange,
            self._hasPresenceUpdate,
            self._hasPresenceFailure) = self.createFlags()

    def createFlags(self):
        hasChanges = False
        hasUpdates = False
        hasFailures = False
        hasPresenceFailure, hasPresenceChange, hasPresenceUpdate, _ = self.presence
        for alarmMapping in self.alarmStates.values():
            for active, changed, updated, message in alarmMapping.values():
                if active:
                    hasFailures = True
                if changed:
                    hasChanges = True
                if updated:
                    hasUpdates = True
                if hasFailures and hasUpdates and hasChanges:
                    return hasChanges, hasUpdates, hasFailures, hasPresenceChange, hasPresenceUpdate, hasPresenceFailure
        return hasChanges, hasUpdates, hasFailures, hasPresenceChange, hasPresenceUpdate, hasPresenceFailure

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

    def hasPresenceChange(self):
        return self._hasPresenceChange

    def hasPresenceUpdate(self):
        return self._hasPresenceUpdate

    def hasPresenceFailure(self):
        return self._hasPresenceFailure

    def getReport(self):
        """!
        """
        for dataIdentifier in self.alarmStates:
            for alarm in self.alarmStates[dataIdentifier]:
                report = self.alarmStates[dataIdentifier][alarm]
                yield dataIdentifier, alarm, report

    def getChanges(self):
        """!
        """
        for dataIdentifier, alarm, report in self.getReport():
            active, changed, updated, message = report
            if changed:
                yield dataIdentifier, alarm, report

    def getFailures(self):
        """!
        """
        for dataIdentifier, alarm, report in self.getReport():
            active, changed, updated, message = report
            if active:
                yield dataIdentifier, alarm, report

    def getUpdates(self):
        for dataIdentifier, alarm, report in self.getReport():
            active, changed, updated, message = report
            if updated:
                yield dataIdentifier, alarm, report

    def getSummary(self):
        """!
        Get summary string.
        """
        return "{} - failures: {}, changes: {}, updates: {}".format(
                self.device,
                self.hasFailures(),
                self.hasChanges(),
                self.hasUpdates())

    def getPresenceMessage(self):
        _, _, _, msg = self.presence
        return msg

class DevicePresence:
    """!
    Device presence message description object.
    """

    def __init__(self, dataIdentifier, values):
        self.dataIdentifier = dataIdentifier
        self.values = values

    @classmethod
    def noPresence(cls):
        return cls(None, None)

    def hasPresence(self):
        return self.dataIdentifier is not None or self.values is not None
