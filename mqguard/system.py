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

from mqreceive.data import DataIdentifier

from mqguard import args
from mqguard.config import ProgramConfig, ConfigException
from mqguard.supervising import DeviceGuard, UpdateGuard
from mqguard.alarms import PresenceAlarm

class System:
    """!
    System initialization object. This object encapsulates program configuration state
    defined by command line arguments and parsed configuration file.
    """

    @classmethod
    def initialize(cls):
        """!
        Initiate system configuration.
        """
        cls.cliArgs = args.parse_args()
        config = ProgramConfig(cls.cliArgs.config)
        # TODO: handle config exceptions
        try:
            cls.configCache = config.parse()
            cls.dataIdentifierFactory = DataIdentifierFactory(cls.configCache)
        except ConfigException as ex:
            print("Configuration error: {}".format(ex), file=sys.stderr)
            exit(1)
        cls.verbose = cls.cliArgs.verbose
        cls._brokerListenDescriptors = None
        cls._deviceGuards = None
        cls._reporters = None

    @classmethod
    def getBrokerListenDescriptors(cls):
        """!
        Get list of tuples (broker, ["subscribeTopic"]).

        @return (broker, ["subscribeTopic"])
        """
        if cls._brokerListenDescriptors is None:
            cls._brokerListenDescriptors = []
            for i in cls._createBrokerListenDescriptors():
                cls._brokerListenDescriptors.append(i)
        return cls._brokerListenDescriptors

    @classmethod
    def getDeviceGuards(cls):
        """!
        Get neabled device guards.

        @return Iterable of tuples (device, guard)
        """
        if cls._deviceGuards is None:
            cls._deviceGuards = []
            for i in cls._createDeviceGuards():
                cls._deviceGuards.append(i)
        return cls._deviceGuards

    @classmethod
    def getReporters(cls):
        """!
        Get enabled reporters.
        """
        if cls._reporters is None:
            cls._reporters = []
            for i in cls._createReporters():
                cls._reporters.append(i)
        return cls._reporters

    @classmethod
    def _createBrokerListenDescriptors(cls):
        for broker, subscriptions in cls.configCache.brokers:
            yield (broker, subscriptions)

    @classmethod
    def _createDeviceGuards(cls):
        """!
        Get iterable of tuples with device and its guard object.

        @return Tuple of (Device, DeviceGuard)
        """
        for deviceName, presenceFactory, guards in cls.configCache.devices:
            deviceGuard = DeviceGuard()
            devicePresence = presenceFactory.build(cls.configCache)
            deviceGuard.addPresenceGuard(
                devicePresence,
                cls.createDevicePresenceGuard(deviceName, devicePresence))
            for guardName, dataIdentificationPrototype, alarms in guards:
                brokerName, topic = dataIdentificationPrototype
                dataIdentifier = cls.dataIdentifierFactory.build(brokerName, topic)
                updateGuard = UpdateGuard(guardName, dataIdentifier)
                for alarm in alarms:
                    updateGuard.addAlarm(alarm)
                deviceGuard.addUpdateGuard(updateGuard)
            yield deviceName, deviceGuard

    @classmethod
    def createDevicePresenceGuard(cls, device, presence):
        presenceUpdateGuard = UpdateGuard(device, presence.dataIdentifier)
        alarm = PresenceAlarm(presence.values)
        presenceUpdateGuard.addAlarm(alarm)
        return presenceUpdateGuard

    @classmethod
    def _createReporters(cls):
        for reporterName, reporterType, reporter in cls.configCache.reporters:
            reporter.injectSystemClass(cls)
            yield reporter

class DataIdentifierFactory:
    def __init__(self, brokerNameResolver):
        self.brokerNameResolver = brokerNameResolver
    def build(self, brokerName, topic):
        broker = self.brokerNameResolver.getBrokerByName(brokerName)
        return DataIdentifier(broker, topic)
