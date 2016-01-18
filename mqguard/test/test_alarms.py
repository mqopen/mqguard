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

import unittest
from mqguard.alarms import *
from mqreceive.data import DataIdentifier
from mqreceive.broker import Broker

class TestBaseAlarm(unittest.TestCase):
    def setUp(self):
        self.messageAlarm = BaseAlarm(AlarmType.messageDriven)
        self.periodicAlarm = BaseAlarm(AlarmType.periodic)
    def test_init(self):
        self.assertEqual(AlarmType.messageDriven, self.messageAlarm.alarmType)
        self.assertEqual(AlarmType.periodic, self.periodicAlarm.alarmType)
class BaseTestRangeAlarm:
    def createDataIdentifier(self):
        self.dataIdentifier = DataIdentifier(Broker("test", "127.0.0.1", 1883), "test/topic")
    def test_messageDrivenType(self):
        self.assertEqual(AlarmType.messageDriven, self.alarm.alarmType)
class TestRangeAlarm(BaseTestRangeAlarm, unittest.TestCase):
    def setUp(self):
        self.createDataIdentifier()
        self.alarm = RangeAlarm.atInterval(-1, 1)
    def test_lowerLimit(self):
        self.assertEqual(-1, self.alarm.lowerLimit)
    def test_upperLimit(self):
        self.assertEqual(1, self.alarm.upperLimit)
    def test_lowerLimitOK(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, -1)
        self.assertTrue(result)
    def test_lowerLimitFail(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, -2)
        self.assertFalse(result)
    def test_upperLimitOK(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, 1)
        self.assertTrue(result)
    def test_upperLimitFail(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, 2)
        self.assertFalse(result)
class TestLowerLimitRangeAlarm(BaseTestRangeAlarm, unittest.TestCase):
    def setUp(self):
        self.createDataIdentifier()
        self.alarm = RangeAlarm.lowerLimit(-1)
    def test_lowerLimit(self):
        self.assertEqual(-1, self.alarm.lowerLimit)
    def test_upperLimit(self):
        self.assertEqual(float('inf'), self.alarm.upperLimit)
    def test_lowerLimitOK(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, -1)
        self.assertTrue(result)
    def test_lowerLimitFail(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, -2)
        self.assertFalse(result)
    def test_upperLimitOK(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, 1000)
        self.assertTrue(result)
class TestUpperLimitRangeAlarm(BaseTestRangeAlarm, unittest.TestCase):
    def setUp(self):
        self.createDataIdentifier()
        self.alarm = RangeAlarm.upperLimit(1)
    def test_lowerLimit(self):
        self.assertEqual(float('-inf'), self.alarm.lowerLimit)
    def test_upperLimit(self):
        self.assertEqual(1, self.alarm.upperLimit)
    def test_lowerLimitOK(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, -1000)
        self.assertTrue(result)
    def test_upperLimitOK(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, 1)
        self.assertTrue(result)
    def test_upperLimitFail(self):
        result, _ = self.alarm.checkDecodedMessage(self.dataIdentifier, 2)
        self.assertFalse(result)
