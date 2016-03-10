# mqguard TODO list


## Configuration

 - Check for `[Brokers]`, `[Devices]` and `[Reporters]` sections if they have at least
    one section name in `Enabled` option.
 - Implement default broker. If broker is not specified, suppose first defined broker.
 - Warn for unused setions.

## Alarms

 - Enumeration alarm. Check in list of allowed values (`"open"`, `"closed"`, ...).
 - PID alarm. Check value changes over time.
 - Regex alarm.
