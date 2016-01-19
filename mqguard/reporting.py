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
Sending reports.
"""

class ReportResult:
    """!
    Representation of report information.
    """

    def __init__(self, device, reasons):
        """!
        Initiate report result object.

        @param device Device representation.
        """
        self.device = device
        self.reasons = reasons

    @classmethod
    def noError(cls, device):
        return cls(device, [])

    def isErrorOccured(self):
        """!
        Check if device error has occured.

        @return True if error occured, False otherwise.
        """
        return len(self.reasons) > 0

class ReportingManager:
    """!
    Managing group of reporters.
    """

    def __init__(self):
        """!
        Initialize report manager.
        """
        self.reporters = []

    def addReporter(self, reporter):
        self.reporters.append(reporter)

    def addDevice(self, device):
        for reporter in self.reporters:
            reporter.addDevice(device)

    def reportStatus(self, event):
        """!
        Report new event.

        @param event Event object.
        """
        for reporter in self.reporters:
            reporter.reportStatus(event)

class BaseReporter:
    """!
    Reporter base class.
    """

    def __init__(self):
        """!
        Initialize reporter.
        """
        self.devices = []

    def addDevice(self, device):
        self.devices.append(device)

    def reportStatus(self, event):
        """!
        Report new event.

        @param event Event object.
        """

class WebsocketReporter(BaseReporter):
    """!
    Sending reports over websockets.
    """

class LogReporter(BaseReporter):
    """!
    Plain text logs.
    """

class DatabaseReporter(BaseReporter):
    """!
    Report errors into database.
    """

class PrintReporter(BaseReporter):
    """!
    Debug reporter.
    """

    def reportStatus(self, result):
        print("registerred {} errors:".format(len(result.reasons)))
        for reason in result.reasons:
            print("{}{}".format(" " * 2, reason))
