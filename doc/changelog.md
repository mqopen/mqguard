# mqguard changelog

## v0.1.0

 - Initial version.
 - Implemented alarms:
   - FloodingAlarm - Detect message flooding.
   - TimeoutAlarm - Message timeouting.
   - RangeAlarm - Check numeric range.
   - ErrorCodesAlarm - Check for error codes.
   - DataTypeAlarm - Check for message characters.
     - numeric - Digits only.
     - alphanumeric - Characters and digits.
     - alphabetic - Characters only.
   - PresenceAlarm - Check for device presence messages.
 - Implemented reportes:
   - SocketReporter - Plain TCP socket server.
   - WebsocketReporter - Websocket server.
   - PrintReporter - Log updates to stdout.
 - Implemented formatters:
   - JSONFormatter - Format data in JSON syntax.
     - Feed types: _init_, _update_.
     - Brokers sections is transmitted in init message only.
     - Differential updates.
 - Application configuration at _.ini_ style config file.
 - Parsing command line arguments.
 - Designed output JSON format.
