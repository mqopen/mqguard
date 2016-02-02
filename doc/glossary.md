# Code glossary

This glossary should explain some terms used in code. This document is not intended for application user, but for its developers.

## Describing device failure event

### Alarm status

Mapping of all alarms and their states

`device`: `dataIdentifier`: `alarm`: `DeviceReport`

 - `device` - Identification of guarded device.
 - `dataIdentifier` - Instance of `DataIdentifier` class. It describes MQTT broker which
    sends the data and MQTT topic.
 - `alarm` - Alarm class object.

### `DeviceReport` object

`DeviceReport` contains state of all device alarms and keeps track their changes and updates.

 - `active` - Boolean flag indicating whether alarm is active (failure occurred) or not.
 - `changed` - Boolean flag indicating whether active flash was recently changed.
 - `updated` - Boolean flag indicating failure re-occurrence.
 - `message` - Alarm message.
