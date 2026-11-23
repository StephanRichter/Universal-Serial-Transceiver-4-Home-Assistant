# Universal Serial Transceiver

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=serial_transceiver)

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

## License

[MIT](LICENSE)
