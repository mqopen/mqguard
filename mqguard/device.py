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

class Device:
    """!
    Guarded device.
    """

    def __init__(self, name):
        self.name = name
        self.presence = None

    def setPresence(self, dataIdentifier, values):
        """!
        Add device presence message.
        """
        self.presence = (dataIdentifier, values)

    def getPresence(self):
        """!
        Get device presence description.

        @return Presence tuple (DataIdentification, ("online message", "offline message"))
        """
        if self.presence is not None:
            return self.presence
        else:
            raise ValueError("Device {} has not presence message".format(self.name))

    def hasPresence(self):
        return self.presence is not None

class DevicePresence:
    """!
    Device presence message description object.
    """

    ## @var dataIdentifier
    # Presence data identifier.

    ## @var values
    # Expected presence online and offline values tuple.

    def __init__(self, dataIdentifier, values):
        """!
        Initiate DevicePresence object.

        @param dataIdentifier Presence data identifier.
        @parameters value Expected presence online and offline values tuple.
            @li Online value
            @li Offline value
        """
        self.dataIdentifier = dataIdentifier
        self.values = values

    @classmethod
    def noPresence(cls):
        """!
        Create no presence object.

        @return DevicePresence with no presence information.
        """
        return cls(None, None)

    def hasPresence(self):
        """!
        Check if object contains presence information.

        @return True if object contains presence, False otherwise.
        """
        return self.dataIdentifier is not None or self.values is not None

    def getDataIdentifier(self):
        """!
        Get device presence data identifier.

        @return device presence DataIdentifier object.
        """
        return self.dataIdentifier
