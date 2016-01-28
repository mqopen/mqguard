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

class DeviceFailureSupervisor:
    """!
    Keep track of all device MQTT topic updates and their falures.
    """

    ## @var device
    # Device identification of supervised device.

    ## @var dataIdentifiers
    # Mapping of supervised data identifiers. Values are mappings {alarmClass: message}
    #       @li alarmClass
    #       @li message

    def __init__(self, device):
        self.device = device
        self.dataIdentifiers = {}
        self.changes = {}

    def supervise(self, dataIdentifier, alarmClasses):
        diMapping = {}
        for alarm in alarmClasses:
            active = False
            message = None
            diMapping[alarm] = (active, message)
        self.dataIdentifiers[dataIdentifier] = diMapping


    def update(self, dataIdentifier, alarmClass, active, message):
        """!
        Update supervisor.

        @param
        """
        alarmWasActive, perviousMessage = self.dataIdentifiers[dataIdentifier][alarmClass]
        if alarmWasActive:
            if active:
                # Alarm is already active. Nothing changed.
                # Only update message.
                self.dataIdentifiers[dataIdentifier][alarmClass] = (active, message)
            else:
                # Alarm disapeared. Notify change.
                self.dataIdentifiers[dataIdentifier][alarmClass] = (active, message)
                self.changes[dataIdentifier] = {}
                self.changes[dataIdentifier][alarmClass] = (active, message)
        else:
            if active:
                # New alarm activation. Notify change.
                self.dataIdentifiers[dataIdentifier][alarmClass] = (active, message)
                self.changes[dataIdentifier] = {}
                self.changes[dataIdentifier][alarmClass] = (active, message)
            else:
                # Alarm is still iddle. Not nothing.
                pass

    def getChanges(self):
        """!
        Get device report tuple.

        @todo: create copy of object.
        """
        return (self.device, self.changes)

    def resetChanges(self):
        """!
        """
        self.changes = {}

    def hasChanges(self):
        return len(self.changes) > 0
