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

import configparser

from mqreceive.broker import Broker
from mqreceive.data import DataIdentifier

from mqguard.alarms import *
from mqguard.streamingreport import SocketReporter, WebsocketReporter
from mqguard.formatting import JSONFormatter, SystemDataProvider
from mqguard.common import DevicePresence

class ProgramConfig:
    """!
    Program configuration parser.
    """

    ## @var configFile
    # Configuration file name.

    ## @var parser
    # Parser object.

    def __init__(self, configFile):
        """!
        Initiate program configuration object.

        @param configFile Path to configuration file.
        """
        self.configFile = configFile
        self.parser = configparser.ConfigParser()

    def parse(self):
        """!
        Parse config file.

        @return Configuration object.
        """
        self.parser.read(self.configFile)
        self.checkForMandatorySections()
        configCache = ConfigCache()
        for broker, subscriptions in self.getBrokers():
            configCache.addBroker(broker, subscriptions)
        for deviceName, presence, guards in self.getGuardedDevices():
            configCache.addDevice(deviceName, presence, guards)
        for reporterName, reporterType, reporter in self.getReporters():
            configCache.addReporter(reporterName, reporterType, reporter)
        return configCache

    def checkForMandatorySections(self):
        """!
        Check if all necessary sections are mandatory.

        @throws ConfigException if some section is missing.
        """
        self.checkForSectionList(["Brokers", "Devices", "Reporters"])

    def getBrokers(self):
        """!
        Get list of enabled brokers.

        @return Iterable of brokers.
        """
        section = "Brokers"
        self.checkForEnabledOption(section)
        brokerSections = self.getEnabledSectionNames(section)
        self.checkForSectionList(brokerSections)
        for brokerSection in brokerSections:
            self.checkForBrokerMandatoryOptions(brokerSection)
            broker = self.createBroker(brokerSection)
            subscribtions = self.getBrokerSubscribtions(brokerSection)
            yield broker, subscribtions

    def getGuardedDevices(self):
        """!
        Get itarable of all guarded devices.

        @throws ConfigException If '[Devices]' section has no 'Enabled' option.
        @throws ConfigException If some enabled device section is missing.
        """
        section = "Devices"
        self.checkForEnabledOption(section)
        deviceSections = self.getEnabledSectionNames(section)
        self.checkForSectionList(deviceSections)
        for deviceSection in deviceSections:
            self.checkForDeviceMandatoryOptions(deviceSection)
            yield self.createDevice(deviceSection)

    def getReporters(self):
        """!
        Get iterable of enabled reporters.
        """
        section = "Reporters"
        self.checkForEnabledOption(section)
        reporterSections = self.getEnabledSectionNames(section)
        self.checkForSectionList(reporterSections)
        for reporterSection in reporterSections:
            self.checkForReporterMandatoryOptions(reporterSection)
            yield self.createReporter(reporterSection)

### Broker #####################################################################

    def checkForBrokerMandatoryOptions(self, brokerSection):
        """!
        Check for mandatory options of broker section.

        @param brokerSection Broker section name.
        @throws ConfigException If some option is missing.
        """
        self.checkForOptionList(brokerSection, ["Topic"])

    def createBroker(self, brokerSection):
        """!
        Create broker object from broker section.

        @param brokerSection Broker section name.
        @return Broker object
        """
        try:
            options = self.parser.options(brokerSection)
            host = self.parser.get(brokerSection, "Host", fallback = "127.0.0.1")
            port = self.parser.getint(brokerSection, "Port", fallback = 1883)
            broker = Broker(brokerSection, host, port)
            if "user" in options or "password" in options:
                (user, password) = self.getBrokerCredentials(brokerSection)
                broker.setCredentials(user, password)
            return broker
        except ValueError as ex:
            raise ConfigException("Invalid broker port number: {}".format(self.parser.get(brokerSection, "Port")))

    def getBrokerCredentials(self, brokerSection):
        """!
        Get username and password of broker.

        @param brokerSection Broker section name.
        @return Tuple of (username, password).
        @throws ConfigException If username or password is missing in configuration file.
        """
        user = None
        password = None
        try:
            user = self.parser.get(brokerSection, "User")
        except configparser.NoOptionError as ex:
            raise ConfigException("Section {}: User option is missing".format(brokerSection))
        try:
            password = self.parser.get(brokerSection, "Password")
        except configparser.NoOptionError as ex:
            raise ConfigException("Section {}: Password option is missing".format(brokerSection))
        return user, password

    def getBrokerSubscribtions(self, brokerSection):
        """!
        Get list of broker subscribe topics.

        @param brokerSection Broker section name.
        @return List of broker subscribe topics.
        @throws ConfigException If zero topics are specified.
        """
        subscriptions = self.parser.get(brokerSection, "Topic").split()
        if len(subscriptions) == 0:
            raise ConfigException("At least one topic subscribe has to be defined")
        return subscriptions

### Device #####################################################################

    def checkForDeviceMandatoryOptions(self, deviceSection):
        """!
        Check for mandatory options of single device section
        """
        self.checkForOptionList(deviceSection, ["Guard"])

    def createDevice(self, deviceSection):
        deviceName = deviceSection
        presenceFactory = self.getDevicePresenceFactory(deviceSection)
        guardSection = self.parser.get(deviceSection, "Guard")
        self.checkForSection(guardSection)
        guards = self.getDeviceGuards(guardSection)
        return (deviceName, presenceFactory, guards)

    def getDevicePresenceFactory(self, deviceSection):
        try:
            brokerName, presenceTopic = self.parser.get(deviceSection, "PresenceTopic").split()
            presenceValues = self.getDevicePresenceValues(deviceSection)
            return PresenceFactory(brokerName, presenceTopic, presenceValues)
        except configparser.NoOptionError as ex:
            return NoPresenceFactory()

    def getDevicePresenceValues(self, deviceSection):
        presenceOnline = None
        presenceOffline = None
        try:
            presenceOnline = self.parser.get(deviceSection, "PresenceOnline")
        except configparser.NoOptionError as ex:
            raise ConfigException("Device {}: 'PresenceOnline' value is missing".deviceSection)
        try:
            presenceOffline = self.parser.get(deviceSection, "PresenceOffline")
        except configparser.NoOptionError as ex:
            raise ConfigException("Device {}: 'PresenceOffline' value is missing".deviceSection)
        return (presenceOnline, presenceOffline)

    def getDeviceGuards(self, guardSection):
        """!
        Get update guards specified in single guard section
        """
        for updateGuardLine in self.parser.options(guardSection):
            brokerName, topic = updateGuardLine.split()
            updateGuardSection = self.parser.get(guardSection, updateGuardLine)
            updateGuard = self.createUpdateGuard(updateGuardSection)
            yield (guardSection, (brokerName, topic), updateGuard)

    def createUpdateGuard(self, updateGuardSection):
        """!
        """
        alarms = self.createUpdateAlarms(updateGuardSection)
        if len(alarms) == 0:
            raise ConfigException("Update guard {} doesn't specify any alarms", updateGuardSection)
        return alarms

    def createUpdateAlarms(self, updateGuardSection):
        alarmsBuilder = AlarmBuilder()
        alarmsBuilder.add(self.getDataTypeAlarm(updateGuardSection))
        alarmsBuilder.add(self.getRangeAlarm(updateGuardSection))
        alarmsBuilder.add(self.getPeriodMinAlarm(updateGuardSection))
        alarmsBuilder.add(self.getPeriodMaxAlarm(updateGuardSection))
        alarmsBuilder.add(self.getErrorCodesAlarm(updateGuardSection))
        return alarmsBuilder.getAlarms()

    def getDataTypeAlarm(self, updateGuardSection):
        if self.parser.has_option(updateGuardSection, "Type"):
            dataTypeAlarmName = self.parser.get(updateGuardSection, "Type")
            return self.createDataTypeAlarm(dataTypeAlarmName)
        else:
            return None

    def createDataTypeAlarm(self, dataType):
        dt = dataType.lower()
        if dt == "numeric":
            return DataTypeAlarm.numeric()
        elif dt == "alphanumeric":
            return DataTypeAlarm.alphanumeric()
        elif dt == "alphabetic":
            return DataTypeAlarm.alphabetic()
        else:
            raise ConfigException("Unsuppoted alarm type: {}".format(dataType))

    def getRangeAlarm(self, updateGuardSection):
        hasMinRange = self.parser.has_option(updateGuardSection, "ValidRangeMin")
        hasMaxRange = self.parser.has_option(updateGuardSection, "ValidRangeMax")

        minRange = None
        maxRange = None
        if hasMinRange:
            minRange = self.parser.getfloat(updateGuardSection, "ValidRangeMin")
        if hasMaxRange:
            maxRange = self.parser.getfloat(updateGuardSection, "ValidRangeMax")
        if hasMinRange and hasMaxRange:
            return RangeAlarm.atInterval(minRange, maxRange)
        elif hasMinRange:
            return RangeAlarm.lowerLimit(minRange)
        elif hasMaxRange:
            return RangeAlarm.upperLimit(maxRange)
        else:
            return None

    def getPeriodMinAlarm(self, updateGuardSection):
        periodMinOption = "PeriodMin"
        if self.parser.has_option(updateGuardSection, periodMinOption):
            try:
                periodMin = self.parser.getint(updateGuardSection, periodMinOption)
                return FloodingAlarm.fromSeconds(periodMin)
            except ValueError as ex:
                raise ConfigException("Section {}: option {} can't be interpreted as number ({})".format(
                        updateGuardSection,
                        periodMinOption,
                        self.parser.get(updateGuardSection, periodMinOption)))
        else:
            return None

    def getPeriodMaxAlarm(self, updateGuardSection):
        periodMaxOption = "PeriodMax"
        if self.parser.has_option(updateGuardSection, periodMaxOption):
            try:
                periodMax = self.parser.getint(updateGuardSection, periodMaxOption)
                return TimeoutAlarm.fromSeconds(periodMax)
            except ValueError as ex:
                raise ConfigException("Section {}: option {} can't be interpreted as number ({})".format(
                        updateGuardSection,
                        periodMaxOption,
                        self.parser.get(updateGuardSection, periodMaxOption)))
        else:
            return None

    def getErrorCodesAlarm(self, updateGuardSection):
        if self.parser.has_option(updateGuardSection, "ErrorCodes"):
            errorCodes = self.parser.get(updateGuardSection, "ErrorCodes").split()
            return ErrorCodesAlarm(errorCodes)
        else:
            return None

### Reporter ###################################################################

    def checkForReporterMandatoryOptions(self, reporterSection):
        """!
        Check for reporter mandatory options.
        """
        self.checkForOptionList(reporterSection, ["Type"])

    def createReporter(self, reporterSection):
        """!
        Create reporter.
        """
        reporterName = reporterSection
        reporterType = self.parser.get(reporterSection, "Type")
        reporter = None
        if reporterType == "socket":
            reporter = self.createSocketReporter(reporterSection)
        elif reporterType == "websocket":
            reporter = self.createWebsocketReporter(reporterSection)
        else:
            raise ConfigException("Unsupported reporter type: {}".format(reporterType))
        return (reporterName, reporterType, reporter)

    def createSocketReporter(self, reporterSection):
        """!
        Create socket reporter.
        """
        listenAddress = self.parser.get(reporterSection, "ListenAddress")
        listenPort = self.parser.getint(reporterSection, "ListenPort")
        return SocketReporter(None, JSONFormatter(SystemDataProvider()), (listenAddress, listenPort))

    def createWebsocketReporter(self, reporterSection):
        listenAddress = self.parser.get(reporterSection, "ListenAddress")
        listenPort = self.parser.getint(reporterSection, "ListenPort")
        return WebsocketReporter(None, JSONFormatter(SystemDataProvider()), (listenAddress, listenPort))

### Common #####################################################################

    def getEnabledSectionNames(self, section):
        return self.parser.get(section, "Enabled").split()

    def checkForSectionList(self, sectionList):
        """!
        Check for list of sections in configuration file.

        @param sectionList
        @throws ConfigException
        """
        for section in sectionList:
            self.checkForSection(section)

    def checkForSection(self, section):
        """!
        Check for section in configuration file.

        @param section
        @throws ConfigException
        """
        if not self.parser.has_section(section):
            raise ConfigException("{} section is missing".format(section))

    def checkForEnabledOption(self, section):
        """!
        Check for "Enabled" option in given section.

        @param section Section name.
        @throws ConfigException If "Enabled" option is missing in section.
        """
        self.checkForOption(section, "Enabled")

    def checkForOptionList(self, section, optionList):
        """!
        Check for list of options in single section.

        @param section
        @param optionList
        @throws ConfigException
        """
        for option in optionList:
            self.checkForOption(section, option)

    def checkForOption(self, section, option):
        """!
        Check for option in configuration file.

        @param section Section name.
        @param option Option name.
        @throws ConfigException If given section doesn't contain specified option.
        """
        if not self.parser.has_option(section, option):
            raise ConfigException("Section {}: {} option is missing".format(section, option))

class AlarmBuilder:
    def __init__(self):
        self.alarms = []
    def add(self, alarm):
        if alarm is not None:
            self.alarms.append(alarm)
    def getAlarms(self):
        return self.alarms

class ConfigCache:
    """!
    Cache object for storing app configuration.
    """

    def __init__(self):
        self.brokers = []
        self.devices = []
        self.reporters = []

    def addBroker(self, broker, subscriptions):
        self.brokers.append((broker, subscriptions))

    def addDevice(self, deviceName, presence, guards):
        self.devices.append((deviceName, presence, guards))

    def addReporter(self, reporterName, reporterType, reporter):
        self.reporters.append((reporterName, reporterType, reporter))

    def getBrokerByName(self, brokerName):
        """!
        Get broker object identified by its't name.

        @param @brokerName
        @throws ConfigException If the name don't match to any stored broker object.
        """
        for broker, subscriptions in self.brokers:
            if brokerName == broker.name:
                return broker
        raise ConfigException("Unknown broker name: {}".format(brokerName))

class BasePresenceFactory:
    """!
    Presence factory base class
    """

class PresenceFactory:
    def __init__(self, brokerName, presenceTopic, presenceValues):
        """!
        Initiate presence factory object.
        """
        self.brokerName = brokerName
        self.presenceTopic = presenceTopic
        self.presenceValues = presenceValues

    def build(self, brokerNameResolver):
        """!
        Build presence object
        """
        broker = brokerNameResolver.getBrokerByName(self.brokerName)
        dataIdentifier = DataIdentifier(broker, self.presenceTopic)
        return DevicePresence(dataIdentifier, self.presenceValues)

class NoPresenceFactory:
    def build(self, brokerNameResolver):
        """!
        Build empty presence object.
        """
        return DevicePresence.noPresence()

class ConfigException(Exception):
    """!
    Exception raised during parsing configuration file
    """
