#!/usr/bin/env python3

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
    testDeviceTemperatureGuard.addAlarm(RangeAlarm.doubleRange(-10, 10))

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
