# mqguard - MQTT monitoring tool

### Configuration file syntax

Configuration file is divided into multiple sections which forms tree-like structure.

#### `[Brokers]` section

**Mandatory section.**

 - `Enabled` - List of enabled MQTT brokers. **Mandatory.**

#### `[Devices]` section

**Mandatory section.**

 - `Enabled` - List of monitored devices. **Mandatory.**

#### `[Reporters]` section

**Mandatory section.**

 - `Enabled` - List of enabled reporter sections. **Mandatory.**

#### Broker section

 - `Username` - Broker username.
 - `Password` - Broker password. *Mandatory if `Username` is defined.*
 - `Host` - Broker listen address. *Default: `localhost`*
 - `Port` - Broker listen port. *Default: `1883`*
 - `PresenceTopic` - Topic name for presence messages.

#### Device section

 - `PresenceTopic` - Device presence topic.
 - `PresenceOnline` - Presence online message. *Mandatory if `PresenceTopic` is defined*
 - `PresenceOffline` - Presence offline message. *Mandatory if `PresenceTopic` is defined*
 - `Guard` - Name of device guard section. **Mandatory.**

#### Guard section

Guard section contains broker name and MQTT topic as key and update sections as value.
There must be at least one section specified.

Example: `my-broker my/broker/topic = update-section`

#### Update section

 - `Type` - Update type. *Default: `alphanumeric`*
   - `numeric` - Only numeric values.
   - `alphanumeric` - Alphanumeric values.
   - `alphabetic` - Only letters.
 - `PeriodMax` - Maximum update period.
 - `PeriodMin` - Minimum update period.
 - `ErrorCodes` - List of update error codes.
 - `ValidRangeMin` - Minimum update value. *Numeric type only.*
 - `ValidRangeMax` - Maximum update value. *Numeric type only.*

#### Reporter section

 - `Type` - Reporter type.
   - `websocket` - Websocket reporter.
   - `logging` - Logging errors into log file.
   - `database` - Log errors into database.
   - `mail` - Notify error via e-mail.

##### Options for `websocket` reporter

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
