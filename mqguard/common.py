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

    ## @var _hasPresenceChange
    ## @var _hasPresenceUpdate
    ## @var _hasPresenceFailure
    ## @var _hasAlarmChanges
    ## @var _hasAlarmUpdates
    ## @var _hasAlarmFailures

    def __init__(self, device, presence, alarmMapping):
        """'
        Initialize DeviceReport object.

        @param device Device identifier.
        @param presence Device presence description.
        @param alarmMapping Alam status mapping.
        """
        self.device = device
        self.presence = presence
        self.alarmMapping = alarmMapping
        (self._hasPresenceChange,
            self._hasPresenceUpdate,
            self._hasPresenceFailure) = self.createPresenceFlags()
        (self._hasAlarmChanges,
            self._hasAlarmUpdates,
            self._hasAlarmFailures) = self.createAlarmFlags()

    def createPresenceFlags(self):
        """!
        Get tuple of presence flags.

        @return Tuple of presence flags.
        """
        devicePresence, presenceStatus = self.presence
        hasPresenceFailure, hasPresenceChange, hasPresenceUpdate, _ = presenceStatus
        return hasPresenceChange, hasPresenceUpdate, hasPresenceFailure

    def createAlarmFlags(self):
        """!
        Get tuple of alarm flags:

        @return Tuple of alarm flags.
        """
        hasAlarmChanges = False
        hasAlarmUpdates = False
        hasAlarmFailures = False
        for alarmMapping in self.alarmMapping.values():
            for active, changed, updated, message in alarmMapping.values():
                if active:
                    hasAlarmFailures = True
                if changed:
                    hasAlarmChanges = True
                if updated:
                    hasAlarmUpdates = True
                if hasAlarmFailures and hasAlarmUpdates and hasAlarmChanges:
                    # We don't have to iterate anymore.
                    return hasAlarmChanges, hasAlarmUpdates, hasAlarmFailures
        return hasAlarmChanges, hasAlarmUpdates, hasAlarmFailures

    def hasPresenceChange(self):
        """!
        Check if report has presence change.

        @return True if report has presence change. False otherwise
        """
        return self._hasPresenceChange

    def hasPresenceUpdate(self):
        """!
        Check if report has presence update.

        @return True if report has presence update. False otherwise
        """
        return self._hasPresenceUpdate

    def hasPresenceFailure(self):
        """!
        Check if report has presence failure.

        @return True if report has presence failure. False otherwise
        """
        return self._hasPresenceFailure

    def hasAlarmChanges(self):
        """!
        Check if report has some alarm change.

        @return True if report has some alarm change. False otherwise.
        """
        return self._hasAlarmChanges

    def hasAlarmUpdates(self):
        """!
        Check if report has some alarm update.

        @return True if report has some alarm update. False otherwise.
        """
        return self._hasAlarmUpdates

    def hasAlarmFailures(self):
        """!
        Check if report has some alarm failure.

        @return True if report has some alarm failure. False otherwise.
        """
        return self._hasAlarmFailures

    def getAlarmReport(self):
        """!
        Get status of all alarms.

        @return iterable of all alarm status tuples.
            @li Is alarm active flag.
            @li Is alarm changed flag.
            @li Is alarm updated flag.
            @li Alarm message.
        """
        for dataIdentifier in self.alarmMapping:
            for alarm in self.alarmMapping[dataIdentifier]:
                report = self.alarmMapping[dataIdentifier][alarm]
                yield dataIdentifier, alarm, report

    def getAlarmChanges(self):
        """!
        Get status of changed alarms.

        @return iterable of changed alarm status tuples.
            @li Is alarm active flag.
            @li Is alarm changed flag.
            @li Is alarm updated flag.
            @li Alarm message.
        """
        for dataIdentifier, alarm, report in self.getAlarmReport():
            active, changed, updated, message = report
            if changed:
                yield dataIdentifier, alarm, report

    def getAlarmFailures(self):
        """!
        Get status of failed alarms.

        @return iterable of failed alarm status tuples.
            @li Is alarm active flag.
            @li Is alarm changed flag.
            @li Is alarm updated flag.
            @li Alarm message.
        """
        for dataIdentifier, alarm, report in self.getAlarmReport():
            active, changed, updated, message = report
            if active:
                yield dataIdentifier, alarm, report

    def getAlarmUpdates(self):
        """!
        Get status of updated alarms.

        @return iterable of updated alarm status tuples.
            @li Is alarm active flag.
            @li Is alarm changed flag.
            @li Is alarm updated flag.
            @li Alarm message.
        """
        for dataIdentifier, alarm, report in self.getAlarmReport():
            active, changed, updated, message = report
            if updated:
                yield dataIdentifier, alarm, report

    def getPresence(self):
        """!
        Get presence tuple.

        @return Presence tuple.
            @li DevicePresence object.
            @li Presence status tuple.
                @li Is presence alarm active flag.
                @li Is presence alarm changed flag.
                @li Is presence alarm updated flag.
                @li Presence alarm message.
        """
        return self.presence

    def hasChanges(self):
        """!
        Check if report has presence or alarm changes.

        @return True if report has presence or alarm changes. False otherwise.
        """
        return self._hasAlarmChanges or self._hasPresenceChange

    def hasUpdates(self):
        """!
        Check if report has presence or alarm updates.

        @return True if report has presence or alarm updates. False otherwise.
        """
        return self._hasAlarmUpdates or self._hasPresenceUpdate

    def hasFailures(self):
        """!
        Check if report has presence or alarm failures.

        @return True if report has presence or alarm failures. False otherwise.
        """
        return self._hasAlarmFailures or self._hasPresenceFailure
