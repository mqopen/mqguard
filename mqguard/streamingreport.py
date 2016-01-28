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

import socket
import threading
import queue

from mqguard.reporting import BaseReporter
from mqguard.fail import DeviceFailureSupervisor

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
        self.supervisors = {}

    def addDevice(self, device, guard):
        failureSupervisor = DeviceFailureSupervisor(device)
        for updateGuard in guard.updateGuards:
            failureSupervisor.supervise(updateGuard.dataIdentifier, updateGuard.getAlarmClasses())
        self.supervisors[device] = failureSupervisor

    def reportStatus(self, event):
        device, dataIdentifier, alarmActive, reason = event
        #dataIdentifier, alarmClass, message = reason
        supervisor = self.supervisors[device]
        supervisor.update(dataIdentifier, alarmClass, not isOK, message)
        if supervisor.hasChange():
            deviceReport = self.supervisor.getChanges()
            self.updateSessions(deviceReport)
            supervisor.resetChanges()

    def updateSessions(self, deviceReport):
        """!
        Override in sub-class.
        """

    def injectSystemClass(self, systemClass):
        self.outputFormatter.injectSystemClass(systemClass)

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
                session = SocketReporterSession(self, self.outputFormatter, client, address)
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

    def updateSessions(self, deviceReport):
        for session in self.sessions:
            session.update(deviceReport)

class SocketReporterSession:
    """!
    Single SocketReporter client session.
    """

    def __init__(self, sessionManager, formatter, client, address):
        self.sessionManager = sessionManager
        self.formatter = formatter
        self.client = client
        self.address = address
        self.eventQueue = queue.Queue()
        self.running = False

    def __call__(self):
        self.running = True
        toSend = "{}\n".format(self.formatter.formatInitialData())
        self.client.send(toSend.encode("utf-8"))
        while self.running:
            deviceReport = self.eventQueue.get()
            if deviceReport is not None:
                toSend = "{}\n".format(self.formatter.formatDeviceReport(deviceReport))
                self.client.send(toSend.encode("utf-8"))
        self.client.close()
        self.sessionManager.sessionEnd(self)

    def getInitialData(self):
        """!
        Get initial data.
        """

    def stop(self):
        self.running = False
        # Put None into message queue to wake up consumer thread.
        self.eventQueue.put(None)

    def isRunning(self):
        return self.running

    def update(self, deviceReport):
        self.eventQueue.put(deviceReport)

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
