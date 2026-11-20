"""
Serial Transceiver via TTY
-------------------------

Sets up a serial transceiver that can be used to receive and send messages via TTY serial devices

This code is derived from https://github.com/RyanMathewson/home-assistant-onkyo-serial
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .connection import RS485Connection

PLATFORMS = [Platform.NOTIFY, Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Open the port in the background and set up the entity.
    entry.runtime_data = RS485Connection(entry.data[CONF_PORT])
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_create_background_task(hass, entry.runtime_data.run(), "serial_transceiver")
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Unload the entity. Home Assistant cancels the connection task.
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    # Reload so that changed options take effect.
    await hass.config_entries.async_reload(entry.entry_id)
