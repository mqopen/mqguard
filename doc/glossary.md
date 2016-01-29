# Code glossary

This glossary should explain some terms used in code. This document is not intended for application user, but for its developers.

## Describing device failure event

### `event` tuple

Contains following fields:

 - `device` - Identification of guarded device.
 - `dataIdentifier` - Instance of `DataIdentifier` class. It describes MQTT broker which
    sends the data and MQTT topic.
 - `alarms` - Iterable of assigned `alarm` tuples.

### `alarm` tuple

 - `alarmClass` - Reference to class of alarm which detected device failure.
 - `active` - Boolean flag indicating if an alarm was triggered.
 - `message` - Message provided by alarm.

## Reporting structures for long term reporters.

Long term reporters are those reporters which have to keep track device state over time
and report only device changes.

Main structure is device report. It can be used to describe device complete status of for
sending its changes.

### `DeviceReport` tuple

 - `device` - Device identification.
 - `guardsMapping` - Mapping of guarded data identifiers.

### `guardsMapping` mapping

 - Mapping of `dataIdentifier`: `alarmMapping`

### `alarmMapping` mapping

 - Mapping of `alarm`: `alarmStatus`

### `alarmStatus`

 - `active` - Boolean flag. `True` if alarm is active `False` if alarm is not trigerred.
 - `message` - Alarm message. `None` if `active` flag is `False`.
