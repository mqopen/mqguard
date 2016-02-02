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

from mqreceive.data import DataIdentifier
from mqreceive.broker import Broker

from mqguard.supervising import UpdateGuard

class TestUpdateGuard(unittest.TestCase):
    def setUp(self):
        self.name = "update-guard-name"
        self.broker = Broker("test-broker", "localhost", 1883)
        self.guardedDataIdentifier = DataIdentifier(self.broker, "test/topic")
        self.updateGuard = UpdateGuard(self.name, self.guardedDataIdentifier)
    def test_name(self):
        self.assertEqual(self.name, self.updateGuard.name)
    def test_dataIdentifier(self):
        self.assertEqual(self.guardedDataIdentifier, self.updateGuard.dataIdentifier)
    def test_isRelevant(self):
        di = DataIdentifier(self.guardedDataIdentifier.broker, self.guardedDataIdentifier.topic)
        self.assertIsNot(di, self.guardedDataIdentifier)
        self.assertTrue(self.updateGuard.isUpdateRelevant(di))
    def test_isNotRelevant(self):
        di = DataIdentifier(self.guardedDataIdentifier.broker, self.guardedDataIdentifier.topic[::-1])
        self.assertFalse(self.updateGuard.isUpdateRelevant(di))
