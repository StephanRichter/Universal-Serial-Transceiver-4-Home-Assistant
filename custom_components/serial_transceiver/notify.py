"""
Notify entity implementation of the Serial Transceiver

This creates a Notify Entity when the connection is set up.
Messages posted to this entity will be written to the serial line.
"""
import logging
from homeassistant.components.notify import NotifyEntity
from homeassistant.const import CONF_PORT
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .connection import SerialConnection
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    async_add_entities([SerialTransmitter(entry)])


class SerialTransmitter(NotifyEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "sender"
    _attr_icon = "mdi:upload-network"

    def __init__(self, entry: ConfigEntry) -> None:
        port = entry.data[CONF_PORT].split('/')[-1]
        self._attr_unique_id = f"{port}_transmitter"
        _LOGGER.debug(f"SerialTransmitter.__init(entry)__, id: {self._attr_unique_id}")
        self._connection: SerialConnection = entry.runtime_data
        self._attr_translation_placeholders = {"port": port}


    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """hand over message to connection.send(…)"""
        _LOGGER.debug(f"async_send_message('{message}', {title}) (ignoring {title})")
        await self._connection.send(message)
