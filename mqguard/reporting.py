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

import threading

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

    def start(self):
        """!
        Notify all reporters to start.
        """
        for reporter in self.reporters:
            threading.Thread(target = reporter).start()

    def stop(self):
        """
        Stop all reporters.
        """
        for reporter in self.reporters:
            reporter.stop()

class BaseReporter:
    """!
    Reporter base class.
    """

    def __init__(self, synchronizer):
        """!
        Initialize reporter.

        @param synchronizer Synchronizing object. Used for notifying reporter asynchronous events.
        """
        self.synchronizer = synchronizer
        self.running = False

    def addDevice(self, device):
        """!
        Add device to reporter. Reporter implementation can override this method to
        keep track of its devices.
        """

    def reportStatus(self, event):
        """!
        Report new event.

        @param event Event object.
        """

    def __call__(self):
        """!
        Run reporter thread.
        """
        self.threadLock = threading.Semaphore()
        self.running = True
        self.threadLock.acquire()

    def stop(self):
        """!
        Notify reporter about program exit.
        """
        try:
            self.threadLock.release()
            self.running = False
        except AttributeError as ex:
            # __call__() method was't called. Do nothing.
            pass

    def isRunning(self):
        """!
        Check if some reporter logic is running. Used with reporters with separate threads.
        In default implementation is reporter not considerred as running.

        @return False.
        """
        return self.running

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
