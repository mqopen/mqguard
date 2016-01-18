# mqguard - MQTT monitoring tool

### Configuration file syntax

Configuration file is divided into multiple sections which forms tree-like structure.

#### `[Global]` section

 - `ListenAddress` - Websocket listen address. *Default: `0.0.0.0`*
 - `ListenPort` - Websocket listen port. *Default: `80`*
 - `OutputFormat` - Preffered websocket output format. *Default: `json`*
   - `json` - JSON format.
   - `xml` - XML format.

#### `[Brokers]` section

**Mandatory section.**

 - `Enabled` - List of enabled MQTT brokers. **Mandatory.**

#### Broker section

 - `Username` - Broker username.
 - `Password` - Broker password. *Mandatory if `Username` is defined.*
 - `Host` - Broker listen address. *Default: `localhost`*
 - `Port` - Broker listen port. *Default: `1883`*
 - `PresenceTopic` - Topic name for presence messages.
 - `Devices` - List of monitored devices. **Mandatory.**

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
