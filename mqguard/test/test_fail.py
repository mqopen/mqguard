import unittest
import random

from mqreceive.data import DataIdentifier
from mqreceive.broker import Broker

from mqguard.fail import DeviceFailureSupervisor
from mqguard.alarms import *

class TestDeviceFailureSupervisor(unittest.TestCase):
    def setUp(self):
        self.device = "test-device"
        self.supervisor = DeviceFailureSupervisor(self.device)
    def test_device(self):
        self.assertEqual(self.device, self.supervisor.device)
    def test_noChangesAfterInit(self):
        self.assertFalse(self.supervisor.hasChanges())
    def test_superviseDevice(self):
        self.supervise()
    def test_updateFailure(self):
        di, alarms = self.supervise()
        self.supervisor.update(di, random.choice(alarms), True, "alarm message")
        self.assertTrue(self.supervisor.hasChanges())
        self.assertEqual(1, len(self.supervisor.getChanges()))

### Helper methods #############################################################

    def supervise(self):
        di = self.createDataIdentifier()
        alarms = [TimeoutAlarm]
        self.supervisor.supervise(di, alarms)
        return di, alarms
    def createDataIdentifier(self):
        return DataIdentifier(self.createBroker(), "my/topic")
    def createBroker(self):
        return Broker("broker-name", "localhost", random.randint(1, 2**(16-1)))
