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

import socket
import threading
import queue

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

class StreamingReporter(BaseReporter):
    """!
    Base class for reporters providing live diagnostic service.
    """

    def __init__(self, synchronizer, outputFormatter):
        """!
        Initialize streaming reporter.

        @param outputFormatter Formatter object for final report result
        """
        BaseReporter.__init__(self, synchronizer)
        self.outputFormatter = outputFormatter
        self.devices = []

    def addDevice(self, device):
        self.devices.append(device)

class SocketReporter(StreamingReporter):
    """!
    Sending reports over TCP/IP socket.
    """

    def __init__(self, synchronizer, outputFormatter, bindAddress):
        """!
        Initialize socket reporter.

        @param outputFormatter Formatter object for final report result
        """
        StreamingReporter.__init__(self, synchronizer, outputFormatter)
        self.bindAddress = bindAddress
        self.server = socket.socket()
        self.sessions = set()

    def __call__(self):
        try:
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(self.bindAddress)
            self.server.listen(127)
            self.running = True
            while self.running:
                client, address = self.server.accept()
                session = SocketReporterSession(self, client, address)
                self.sessions.add(session)
                threading.Thread(target = session).start()
        finally:
            self.running = False

    def stop(self):
        if self.running:
            for session in self.sessions:
                session.stop()
        # TODO: block until all runnin sessions will be terminated
        self.running = False

    def sessionEnd(self, session):
        self.sessions.remove(session)

    def reportStatus(self, event):
        for session in self.sessions:
            for message in event.reasons:
                session.newMessage(message)

class SocketReporterSession:
    """!
    Single SocketReporter client session.
    """

    def __init__(self, sessionManager, client, address):
        self.sessionManager = sessionManager
        self.client = client
        self.address = address
        self.messageQueue = queue.Queue()
        self.running = False

    def __call__(self):
        self.running = True
        while self.running:
            message = self.messageQueue.get()
            if message is not None:
                toSend = "{}\n".format(message)
                self.client.send(toSend.encode("utf-8"))
        self.client.close()
        self.sessionManager.sessionEnd(self)

    def stop(self):
        self.running = False
        # Put None into message queue to wake up consumer thread.
        self.messageQueue.put(None)

    def isRunning(self):
        return self.running

    def newMessage(self, message):
        self.messageQueue.put(message)

class WebsocketReporter(StreamingReporter):
    """!
    Sending reports over websockets.
    """

    def __init__(self, synchronizer, outputFormatter):
        """!
        Initialize websocket reporter.

        @param outputFormatter Formatter object for final report result
        """
        StreamingReporter.__init__(self, synchronizer, outputFormatter)

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
