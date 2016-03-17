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
import asyncio
import websockets

from mqguard.reporting import BaseReporter

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

    def report(self, deviceReport):
        if deviceReport.hasAlarmChanges() or deviceReport.hasPresenceUpdate():
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
        self.reportQueue = queue.Queue()
        self.running = False

    def __call__(self):
        self.running = True
        toSend = "{}\n".format(self.formatter.formatInitialData())
        self.client.send(toSend.encode("utf-8"))
        while self.running:
            deviceReport = self.reportQueue.get()
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
        self.reportQueue.put(None)

    def isRunning(self):
        return self.running

    def update(self, deviceReport):
        self.reportQueue.put(deviceReport)

class WebsocketReporter(StreamingReporter):
    """!
    Sending reports over websockets.
    """

    def __init__(self, synchronizer, outputFormatter, bindAddress):
        """!
        Initialize websocket reporter.

        @param outputFormatter Formatter object for final report result
        """
        StreamingReporter.__init__(self, synchronizer, outputFormatter)
        self.bindAddress = bindAddress
        self.sessions = set()
        self.server = websockets.serve(self.handleClient, 'localhost', 8765)

    def __call__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.set_debug(True)
        self.loop.create_task(self.server)
        self.loop.run_forever()

    def stop(self):
        self.server.close()

    def report(self, deviceReport):
        if deviceReport.hasAlarmChanges() or deviceReport.hasPresenceUpdate():
            for session in self.sessions:
                self.loop.call_soon_threadsafe(self.addUpdate, session, deviceReport)

    def addUpdate(self, session, deviceReport):
        self.loop.create_task(session.update(deviceReport))

    @asyncio.coroutine
    def handleClient(self, websocket, path):
        session = WebsocketReporterSession(self, self.outputFormatter, websocket, path)
        self.sessions.add(session)
        yield from session.handleSession()

class WebsocketReporterSession:
    """!
    Single websocket session.
    """

    def __init__(self, sessionManager, formatter, websocket, path):
        self.sessionManager = sessionManager
        self.formatter = formatter
        self.websocket = websocket
        self.path = path
        self.reportQueue = asyncio.Queue()
        self.running = False

    @asyncio.coroutine
    def handleSession(self):
        self.running = True
        # TODO: Really need to fix this!!
        toSend = "{}\n".format(self.formatter.formatInitialData(self.sessionManager.deviceRegistry.getDeviceReports()))
        yield from self.websocket.send(toSend)
        while self.running:
            deviceReport = yield from self.reportQueue.get()
            if deviceReport is not None:
                toSend = "{}\n".format(self.formatter.formatDeviceReport(deviceReport))
                yield from self.websocket.send(toSend)

    @asyncio.coroutine
    def update(self, deviceReport):
        yield from self.reportQueue.put(deviceReport)
