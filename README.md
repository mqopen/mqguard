# mqguard - MQTT monitoring tool

### Configuration file syntax

Configuration file is divided into multiple sections which forms tree-like structure.

#### `[Global]` section

Just for future versions of mqguard. Empty section for now. Any ideas for configuration options?

#### `[Brokers]` section

Specifies group of MQTT brokers for collecting data. **Mandatory section.**

 - `Enabled` - List of enabled MQTT brokers. **Mandatory.**

#### `[Devices]` section

Specifies group of guarded devices. **Mandatory section.**

 - `Enabled` - List of monitored devices. **Mandatory.**

#### `[Reporters]` section

Specifies group of reporters for program output. **Mandatory section.**

 - `Enabled` - List of enabled reporter sections. **Mandatory.**

#### Broker section

Broker section describes connection to MQTT broker. By enabling this section in
`[Brokers]` section, mqguard will connect to this broker and start collect data.
Brokers are defined by combination of its name, host and port. Broker name must be unique.

 - `Username` - Broker username.
 - `Password` - Broker password. *Mandatory if `Username` is defined.*
 - `Host` - Broker listen address. *Default: `localhost`*
 - `Port` - Broker listen port. *Default: `1883`*
 - `Topic` - Space separated list of topic subscriptions. **Mandatory.**

#### Device section

Device section describes guarded device. It is defined by name, which must be unique.
Name is taken from `Name` option or from section name.

 - `Name` - Device name. Must be unique across all guarded devices.
 - `Description` - Device description string. It is used by some reporters.
 - `PresenceTopic` - Device presence topic.
 - `PresenceOnline` - Presence online message. *Mandatory if `PresenceTopic` is defined*
 - `PresenceOffline` - Presence offline message. *Mandatory if `PresenceTopic` is defined*
 - `Guard` - Name of device guard section. **Mandatory.**

_TODO: Consider to add following options. It may be useful._

 - `Latitude` - Device latitude.
 - `Longitude` - Device longitude.
 - `Elevation` - Elevation of the device.
 - `Tags` - List of keywords for making device groups. Used for some advanced filtering, etc.

#### Guard section

Guard section contains broker name and MQTT topic as key and update sections as value.
There must be at least one section specified.

Example: `my-broker my/device/topic = update-section`

#### Update section

 - `Type` - Update type. *Default: `alphanumeric`*
   - `numeric` - Only numeric values.
   - `alphanumeric` - Alphanumeric values.
   - `alphabetic` - Only letters.
 - `PeriodMax` - Maximum update period. Check if device simply stopped sending
    data for some reason.
 - `PeriodMin` - Minimum update period. Protect network from message flooding.
 - `ErrorCodes` - List of update error codes.
 - `ValidRangeMin` - Minimum update value. *Numeric type only.*
 - `ValidRangeMax` - Maximum update value. *Numeric type only.*

#### Reporter section

Reporter is object for program output. Its responsibility is notify user about device
problems, or provide real time diagnostic information.

 - `Type` - Reporter type.
   - `socket` - TCP/IP socket reporter.
   - `websocket` - Websocket reporter.
   - `logging` - Logging errors into plain log file or to standard output.
   - `database` - Log errors into database.
   - `mail` - Notify error via e-mail.
   - `sms` - SMS notification.
   - `trigger` - Execute shell script.

_TODO:_

 - Add specification which devices should be reported. It is nonsense to send SMS
    for all devices, while user is interested only about few ones. This mechanism
    should be implemented as some kind of report domain.

##### Options for `socket` and `websocket` reporter

 - `ListenAddress` - Websocket listen address. *Default: `0.0.0.0`*
 - `ListenPort` - Websocket listen port. *Default: `80`*
 - `OutputFormat` - Preffered websocket output format. *Default: `json`*
   - `json` - JSON format.
   - `xml` - XML format.
   - `plain` - Plain text format. Similar to `logging` reporter type, except logs
    are send over websocket channel.

##### Options for `logging` reporter

 - _**TODO**_

##### Options for `mail` reporter

 - _**TODO**_
