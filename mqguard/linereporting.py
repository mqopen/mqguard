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

import logging
import logging.handlers
from mqguard.reporting import BaseReporter

class LineReporter(BaseReporter):
    """!
    Base class for line based reporting
    """

    def __init__(self, synchronizer, logger):
        """!
        Initialize line reporter object.

        @param synchronizer
        @param logger Logger object.
        """
        BaseReporter.__init__(self, synchronizer)
        self.logger = logger

    def report(self, deviceReport):
        """!
        @copydoc BaseReporter::report()
        """
        if deviceReport.hasPresenceUpdate():
            self.reportPresence(deviceReport)
        self.reportGuards(deviceReport)

    def reportPresence(self, deviceReport):
        """!
        Report presence update.

        @param deviceReport DeviceReport object.
        """
        devicePresence, track = deviceReport.getPresence()
        _, _, _, msg = track
        presenceDataIdentifier = devicePresence.getDataIdentifier()
        self.logger.warning("{} {} Presence \"{}\"".format(
            presenceDataIdentifier.broker.name,
            presenceDataIdentifier.topic,
            msg))

    def reportGuards(self, deviceReport):
        """!
        Report alarm changes.

        @param deviceReport DeviceReport object.
        """
        for dataIdentifier, alarm, report in deviceReport.getAlarmChanges():
            active, _, _, message = report
            if not active:
                message = "Is OK now"
            self.logger.warning("{} {} {} \"{}\"".format(
                dataIdentifier.broker.name,
                dataIdentifier.topic,
                alarm.getName(),
                message))

class LogReporter(LineReporter):
    """!
    Plain text logs.
    """

    def __init__(self, synchronizer, logfile):
        """!
        Initialize log reporter object.

        @param synchronizer
        @param logfile Path to log file.
        """
        LineReporter.__init__(self, synchronizer, self.createLogger(logfile))
        self.logfile = logfile

    def createLogger(self, logfile):
        """!
        Create logger object.

        @param logfile Path to log file.
        @return Logger object.
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler(
            logfile,
            when="M",
            interval=1)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

class PrintReporter(LineReporter):
    """!
    Print messages to stdout.
    """

    def __init__(self, synchronizer):
        """!
        Initialize print reporter object.

        @param synchronizer
        """
        LineReporter.__init__(self, synchronizer, self.createLogger())

    def createLogger(self):
         """!
        Create logger object.

        @return Logger object.
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("%(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger
