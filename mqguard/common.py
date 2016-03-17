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

class GeographicPosition:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

class DeviceReport:
    """!
    Device alarm report.
    """

    ## @var device
    # Device identifier.

    ## @var presence
    # Presence description tuple.
    #   @li DevicePresence object.
    #   @li Presence status tuple.
    #       @li Is presence alarm active flag.
    #       @li Is presence alarm changed flag.
    #       @li Is presence alarm updated flag.
    #       @li Presence alarm message.

    ## @var alarmMapping

    def __init__(self, device, presence, alarmMapping):
        self.device = device
        self.presence = presence
        self.alarmMapping = alarmMapping
        (self._hasChanges,
            self._hasUpdates,
            self._hasFailures) = self.createUpdateFlags()
        (self._hasPresenceChange,
            self._hasPresenceUpdate,
            self._hasPresenceFailure) = self.createPresenceFlags()

    def createUpdateFlags(self):
        hasChanges = False
        hasUpdates = False
        hasFailures = False
        for alarmMapping in self.alarmMapping.values():
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

    def createPresenceFlags(self):
        devicePresence, presenceStatus = self.presence
        hasPresenceFailure, hasPresenceChange, hasPresenceUpdate, _ = presenceStatus
        return hasPresenceChange, hasPresenceUpdate, hasPresenceFailure

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
        for dataIdentifier in self.alarmMapping:
            for alarm in self.alarmMapping[dataIdentifier]:
                report = self.alarmMapping[dataIdentifier][alarm]
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

    def getPresence(self):
        return self.presence
