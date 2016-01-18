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

"""!
Module with update alarms.
"""

from enum import Enum

class AlarmType(Enum):
    messageDriven = 1
    periodic = 2

class BaseAlarm:
    """!
    Basic alarm implementation.
    """

    def __init__(self, alarmType):
        """!
        Initiate object:

        @param alarmType Type of alarm
        """
        self.alarmType = alarmType

    # TODO: consider raising an exception

    def checkMessage(self, dataIdentifier, data):
        """!
        Check message update

        @param dataIdentifier DataIdentifier object.
        @param data received bytes.
        """
        try:
            return self.checkDecodedMessage(dataIdentifier, data.decode("utf-8"))
        except UnicodeError as ex:
            return (False, "Data decoding error")

    def notifyMessage(self, dataIdentifier, data):
        """!
        Notify incomming message.
        """

    def checkPeriodic(self):
        """!
        Periodic check.
        """
        return (False, "Not implemented")

    def checkDecodedMessage(self, dataIdentifier, data):
        """!
        Convenient method. Decode message
        """
        return (False, "Not implemented")

class TimedAlarm(BaseAlarm):
    """!
    Time related alarm.
    """

    ## @var period
    # Time period

    def __init__(self, alarmType, period):
        BaseAlarm.__init__(self, alarmType)
        self.period = period

class FloodingAlarm(TimedAlarm):
    """!
    Check too many updates in short time period.
    """

    def __init__(self, period):
        TimedAlarm.__init__(self, AlarmType.messageDriven, period)

class TimeoutAlarm(TimedAlarm):
    """!
    Check timeouting.
    """

    def __init__(self, period):
        TimedAlarm.__init__(self, AlarmType.periodic, period)

class RangeAlarm(BaseAlarm):
    """!
    Alarm for checking valid range of data
    """

    def __init__(self, lowerRange, upperRange):
        BaseAlarm.__init__(self, AlarmType.messageDriven)
        self.lowerRange = lowerRange
        self.upperRange = upperRange

    @classmethod
    def doubleRange(cls, lowerRange, upperRange):
        return cls(lowerRange, upperRange)

    @classmethod
    def lowerRange(cls, lowerRange):
        return cls(lowerRange, float('inf'))

    @classmethod
    def upperRange(cls, upperRange):
        return cls(float('-inf'), upperRange)

    def checkDecodedMessage(self, dataIdentifier, data):
        try:
            value = float(data)
            if value < self.lowerRange:
                return (False, "Lower value")
            if value > self.upperRange:
                return (False, "Upper value")
            return (True, None)
        except ValueError as ex:
            return (False, "Can't decode value as number")

class PresenceAlarm(BaseAlarm):
    """!
    Checking device presence message.
    """

    def __init__(self, presenceDataIdentifier, presenceMessages):
        BaseAlarm.__init__(self, AlarmType.messageDriven)
        self.presenceDataIdentifier = presenceDataIdentifier
        self.presenceOnline, self.preseceOffline = presenceMessages

    def checkDecodedMessage(self, dataIdentifier, data):
        if (dataIdentifier == self.presenceDataIdentifier):
            if data == self.presenceOnline:
                return (True, None)
            if data == self.preseceOffline:
                return (False, "Device is down")
            return (False, "Unexpected presence message: {}".format(data))

class ErrorCodesAlarm(BaseAlarm):
    """!
    Check for error codes.
    """

    def __init__(self, errorCodes):
        """!
        Initiate alarm.

        @param errorCodes Iterable of error codes.
        """
        BaseAlarm.__init__(self, AlarmType.messageDriven)
        self.errorCodes = errorCodes

    def checkDecodedMessage(self, dataIdentifier, data):
        if data in self.errorCodes:
            return (False, "Error code detected: {}".format(data))
        else:
            return (True, None)
