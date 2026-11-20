# Universal Serial Transceiver

This Integration allows to connect to a serial device mapped as ttyX on linux systems.

Contrary to Home Assistant's [Raw Serial](https://www.home-assistant.io/integrations/serial) integration, it provides both an inbound and an outbound channel, allowing to send and receive messages.

## Features

* A `sensor` entity that receives messages from the serial line. These messages are not processed further.  
Processing is left for the user, for exampe using templates.
* A `notify` entity that can be used to push messages.  
Any value assigned to this entity will be written onto the serial line. 

## Requirements

- Any adapter that is recognized and mapped as tty device on linux.

### Home Assistant in Docker

The adapter must be visible inside the container. 

## Installation

### HACS

**TODO**

### Manual

Copy `custom_components/serial_transceiver` into your Home Assistant `custom_components` folder and restart Home Assistant.

## Setup

Go to **Settings > Devices & services > Add integration** and search for **Universal Serial Transceiver**. Choose the serial port, and pick a `/dev/serial/by-id/` path if one is listed. 
The integration holds the port with an exclusive lock, so nothing else can use it at the same time. To test the port by hand, disable the integration first.

## Example

[examples/automations.yaml](examples/automations.yaml) shows an automation that echoes any message received via ttyAMA0 back to that serial

## Makefile

The [Makefile](Makefile) included in this repository is for development support only:
When running `make`, it launches a home assistant container in podman an than spawns a virtual terminal inside that container.
The running instance can be used at http://localhost:8123. When the _Universal Serial Transceiver_ integration is added and configured, this terminal will receive messages (Notifications) from the Transmitter. All messages posted in the terminal will be received by the receiver (Sender). 

## License

[MIT](LICENSE)
