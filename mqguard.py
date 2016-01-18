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

import asyncio
import websockets
import sys

from mqreceive.broker import Broker
from mqreceive.receiving import BrokerReceiver
from mqreceive.broker import Broker
from mqreceive.data import DataIdentifier

from mqguard.supervising import DeviceGuard, UpdateGuard, DeviceRegistry
from mqguard.alarms import RangeAlarm

def _main():
    @asyncio.coroutine
    def hello(websocket, path):
        print(path)
        i = 0
        while True:
            yield from websocket.send("{}".format(i))
            i += 1
            yield from asyncio.sleep(1)
    start_server = websockets.serve(hello, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

def main():

    deviceRegistry = DeviceRegistry()

    # Create broker object.
    testBroker = Broker("Test", sys.argv[1])
    testBroker.setCredentials(sys.argv[2], sys.argv[3])
    brokerReceiver = BrokerReceiver("Test", (testBroker, ["#"]), deviceRegistry)

    # Define device.
    testDevice = DeviceGuard("cr-livingroom-sensor")

    # Create update guards.
    testDeviceTemperatureGuard = UpdateGuard("temperature-guard", DataIdentifier(testBroker, "chrudim/living-room-up/temperature"))
    testDeviceTemperatureGuard.addPresenceGuard(DataIdentifier(testBroker, "chrudim/presence/living-room-up-dht"), ("online", "offline"))
    testDeviceTemperatureGuard.addAlarm(RangeAlarm.atInterval(-10, 10))

    testDeviceHumidityGuard = UpdateGuard("humidity-guard", DataIdentifier(testBroker, "chrudim/living-room-up/humidity"))

    # Add device into registry.
    deviceRegistry.addGuardedDevice(testDevice)

    # Add guard object to device.
    testDevice.addUpdateGuard(testDeviceTemperatureGuard)
    testDevice.addUpdateGuard(testDeviceHumidityGuard)

    # Start receiver thread.
    brokerReceiver()

if __name__ == '__main__':
    main()
