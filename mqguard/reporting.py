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

class DeviceReport:
    """!
    Group of device failures. Single device is represented by multiple topics and broker
    paris. Each of this pair has multiple alarms.

    Device can report failure for each pair. This class groups togeteher all these failures.
    """

    ## @var device
    # Device identification object.

    def __init__(self, device):
        """!
        Initialize report object.

        @param device Device identification object.
        """
        self.device = device
        self.reasons = []

    def addFailureReason(self, reason):
        """!
        Add failure to report.

        @param reason Failure reason object.
        """
        self.reasons.append(reason)

    def hasFailures(self):
        """!
        Check if device has any failures.

        @return True if device has failures, False otherwise.
        """
        return len(self.reasons) > 0

class DeviceFailureReason:
    """!
    Single device failure
    """

    def __init__(self, failureDataIdentifier, alarm, message):
        """!
        Initialize failure object.

        @param failureDataIdentifier DataIdentifier which causes failure.
        @param alarm Identification of alarm which detected wrong message.
        @param message Alarm message.
        """

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

    def addDevice(self, device, guard):
        for reporter in self.reporters:
            reporter.addDevice(device, guard)

    def addBroker(self, broker):
        """!
        Add broker object.
        """

    def reportStatus(self, event):
        """!
        Report new event.

        @param event Tuple with following fields: (device, isOK, reason).
            @li device Device identification.
            @li isOK Boolean flag indicating if any error occured.
            @li reason Reason tuple (dataIdentifier, alarmClass, message).
                @li dataIdentifier DataIdentifier object.
                @li alarmClass Alarm class.
                @li message Alarm message.
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

    def addDevice(self, device, guard):
        """!
        Add device to reporter. Reporter implementation can override this method to
        keep track of its devices.

        @param device Device object.
        @param guard DeviceGuard object.
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

    def injectSystemClass(self, systemClass):
        """!
        Oppotunity for reporter to get system reference.
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
