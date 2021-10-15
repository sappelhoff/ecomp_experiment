# EEG

## General information

The experiment can easily be run without EEG data collection; simply set `SER_ADDRESS = None` in `define_settings.py`.

## Sending event markers (TTL triggers)

Event markers (also called TTL Triggers) can be sent using the pyserial library.
Here we use the [Brain Products Trigger Box](https://pressrelease.brainproducts.com/triggerbox-tips/)
as a device to send serial data via a USB port, which gets transformed into a parallel port TTL signal
to be picked up by the EEG amplifier.

See `define_settings.py` and `define_ttl.py` for more information
