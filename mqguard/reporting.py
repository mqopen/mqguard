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

    def report(self, deviceReport):
        """!
        Report new event.
        """
        for reporter in self.reporters:
            reporter.report(deviceReport)

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

    def injectDeviceRegistry(self, deviceRegistry):
        """!
        Inject device registry to all registered reporters.
        """
        for reporter in self.reporters:
            reporter.injectDeviceRegistry(deviceRegistry)

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
        self.deviceRegistry = None
        self.running = False

    def addDevice(self, device, guard):
        """!
        Add device to reporter. Reporter implementation can override this method to
        keep track of its devices.

        @param device Device object.
        @param guard DeviceGuard object.
        """

    def report(self, deviceReport):
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

    def injectDeviceRegistry(self, deviceRegistry):
        self.deviceRegistry = deviceRegistry

    def hasDeviceRegistry(self):
        """!
        Check if device registry object has been injected.

        @return True if device registry is injected, False otherwise.
        """
        return self.deviceRegistry is not None

class DatabaseReporter(BaseReporter):
    """!
    Report errors into database.
    """

class LineReporter(BaseReporter):
    """!
    Base class for line based reporting
    """

    def report(self, deviceReport):
        if deviceReport.hasChanges() or deviceReport.hasPresenceUpdate():
            self.doReport(deviceReport)

    def doReport(self, deviceReport):
        """!
        Do report. Override this in subclass.
        """

class LogReporter(LineReporter):
    """!
    Plain text logs.
    """

class PrintReporter(LineReporter):
    """!
    Debug reporter.
    """

    def report(self, deviceReport):
        if deviceReport.hasPresenceUpdate():
            print(deviceReport.getPresenceMessage())
        for dataIdentifier, alarm, report in deviceReport.getChanges():
            active, _, _, message = report
            if active:
                print("{}: {}.".format(dataIdentifier.topic, message))
            else:
                print("{}: Is OK now.".format(dataIdentifier.topic))
