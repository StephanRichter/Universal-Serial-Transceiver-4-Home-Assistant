"""
Sensor entity implementation of the Serial Transceiver

This creates a Sensor Entity when the connection is set up.
This sensor receives incoming messages from the serial line.
"""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.components.notify import NotifyEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, UnitOfTemperature
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .connection import SerialConnection

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([SerialReceiver(entry)])

class SerialReceiver(SensorEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "receiver"
    _attr_icon = "mdi:download-network"
    _attr_should_poll = False
    _attr_native_value = None

    def __init__(self, entry: ConfigEntry) -> None:
        port = entry.data[CONF_PORT].split('/')[-1]
        self._attr_unique_id = f"{port}_receiver"
        _LOGGER.debug(f"SerialReceiver.__init(entry)__, id: {self._attr_unique_id}")
        self._attr_translation_placeholders = {"port": port}
        self._connection : SerialConnection = entry.runtime_data

    async def async_added_to_hass(self) -> None:
        """register at connection"""
        self.async_on_remove(
            self._connection.link_receiver(self)
        )

    def handle_value(self, text: str):
        """called by connection, this sets the internal value and notifies the home assistant code"""
        self._attr_native_value = text
        self.async_write_ha_state()