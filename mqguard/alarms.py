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
import datetime

class AlarmType(Enum):
    messageDriven = 1
    periodic = 2

class AlarmPriority(Enum):
    errorCode = 1
    dataType = 2
    value = 3
    other = 4

class BaseAlarm:
    """!
    Basic alarm implementation.
    """

    def __init__(self, alarmType, alarmPriority):
        """!
        Initiate object:

        @param alarmType Type of alarm
        """
        self.alarmType = alarmType
        self.alarmPriority = alarmPriority

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
    Time related alarm. Base class.
    """

    ## @var period
    # Time period.

    def __init__(self, alarmType, alarmPriority, period):
        BaseAlarm.__init__(self, alarmType, alarmPriority)
        self.period = period
        self.lastMessageTime = None

    def isLastTimeKnown(self):
        return self.lastMessageTime is not None

class FloodingAlarm(TimedAlarm):
    """!
    Check too many updates in short time period.
    """

    def __init__(self, period):
        TimedAlarm.__init__(self, AlarmType.messageDriven, AlarmPriority.other, period)

    @classmethod
    def fromSeconds(cls, seconds):
        return cls(datetime.timedelta(seconds = seconds))

    @classmethod
    def fromMiliseconds(cls, ms):
        return cls(datetime.timedelta(milliseconds = ms))

class TimeoutAlarm(TimedAlarm):
    """!
    Check timeouting.
    """

    def __init__(self, period):
        TimedAlarm.__init__(self, AlarmType.periodic, AlarmPriority.other, period)

    @classmethod
    def fromSeconds(cls, seconds):
        return cls(datetime.timedelta(seconds = seconds))

    def notifyMessage(self):
        self.updateMessageTime()

    def checkPeriodic(self):
        if self.isLastTimeKnown():
            currentTime = datetime.datetime.now()
            delta = currentTime - self.lastMessageTime
            if delta > self.period:
                return (False, "Update timeouted: {} seconds".format(delta.total_seconds()))
        else:
            # First message is still not received. Update its timestamp. It will trigger
            # alarm in case that it never be received.
            self.updateMessageTime()
        return (True, None)

    def updateMessageTime(self):
        self.lastMessageTime = datetime.datetime.now()

class RangeAlarm(BaseAlarm):
    """!
    Alarm for checking valid range of data
    """

    def __init__(self, lowerLimit, upperLimit):
        BaseAlarm.__init__(self, AlarmType.messageDriven, AlarmPriority.value)
        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit

    @classmethod
    def atInterval(cls, lowerLimit, upperLimit):
        return cls(lowerLimit, upperLimit)

    @classmethod
    def lowerLimit(cls, lowerLimit):
        return cls(lowerLimit, float('inf'))

    @classmethod
    def upperLimit(cls, upperLimit):
        return cls(float('-inf'), upperLimit)

    def checkDecodedMessage(self, dataIdentifier, data):
        try:
            value = float(data)
            if value < self.lowerLimit:
                return (False, "Value {} exceeds minimum allowed range ({})".format(value, self.lowerLimit))
            if value > self.upperLimit:
                return (False, "Value {} exceeds maximum allowed range ({})".format(value, self.upperLimit))
            return (True, None)
        except ValueError as ex:
            return (False, "Can't decode value '{}' as a number".format(data))

class PresenceAlarm(BaseAlarm):
    """!
    Checking device presence message.
    """

    def __init__(self, presenceDataIdentifier, presenceMessages):
        BaseAlarm.__init__(self, AlarmType.messageDriven, AlarmPriority.value)
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
        BaseAlarm.__init__(self, AlarmType.messageDriven, AlarmPriority.errorCode)
        self.errorCodes = errorCodes

    def checkDecodedMessage(self, dataIdentifier, data):
        if data in self.errorCodes:
            return (False, "Error code detected: {}".format(data))
        else:
            return (True, None)

class DataTypeAlarm(BaseAlarm):
    def __init__(self, dataFilter):
        BaseAlarm.__init__(self, AlarmType.messageDriven, AlarmPriority.dataType)
    @classmethod
    def numeric(cls, additions = []):
        return None
    @classmethod
    def alphanumeric(cls, additions = []):
        return None
    @classmethod
    def alphabetic(cls, additions = []):
        return None
