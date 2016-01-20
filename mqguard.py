#!/usr/bin/env python3
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

import sys
import threading

from mqreceive.receiving import BrokerThreadManager

from mqguard.supervising import DeviceRegistry
from mqguard.reporting import ReportingManager
from mqguard.system import System

def main():
    System.initialize()

    reportingManager = ReportingManager()
    for reporter in System.getReporters():
        reportingManager.addReporter(reporter)
    deviceRegistry = DeviceRegistry(reportingManager)

    listenDescriptors = System.getBrokerListenDescriptors()
    brokerThreadManager = BrokerThreadManager(listenDescriptors, deviceRegistry)

    for device in System.getDeviceGuards():
        deviceRegistry.addGuardedDevice(device)

    # Start reporting threads.
    reportingManager.start()

    # Start receiving threads.
    brokerThreadManager.start()

    exitLock = threading.Semaphore(value = 0)

    try:
        # Lock main thread
        exitLock.acquire()
    finally:
        pass

if __name__ == '__main__':
    main()
