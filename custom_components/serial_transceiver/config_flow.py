"""
Config and options flows for the Serial Transceiver

This code is derived from https://github.com/RyanMathewson/home-assistant-onkyo-serial
"""
from __future__ import annotations

import os
import voluptuous as vol
from typing import Any
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig, NumberSelectorMode, SelectSelector, SelectSelectorConfig, SelectSelectorMode, TextSelector, TextSelectorConfig
from .const import BAUD_RATE, BAUD_RATES, BY_ID, DOMAIN



def _list_ports() -> list[str]:
    # Return serial ports, stable by-id paths first.
    try:
        by_id = sorted(os.path.join(BY_ID, name) for name in os.listdir(BY_ID))
    except OSError:
        by_id = []
    resolved = {os.path.realpath(path) for path in by_id}
    try:
        devices = sorted(f"/dev/{name}" for name in os.listdir("/dev") if name.startswith(("ttyUSB", "ttyACM")))
    except OSError:
        devices = []
    return by_id + [path for path in devices if path not in resolved]


class RS485ConfigFlow(ConfigFlow, domain=DOMAIN):
    # Handle adding a receiver.

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        # Ask for the serial port
        errors: dict[str, str] = {}
        if user_input is not None:
            port = user_input[CONF_PORT]
            await self.async_set_unique_id(port)
            self._abort_if_unique_id_configured()
            if await self.hass.async_add_executor_job(os.path.exists, port):
                return self.async_create_entry(title="Serial Transceiver", data=user_input)
            errors["base"] = "port_not_found"
        ports = await self.hass.async_add_executor_job(_list_ports)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PORT): SelectSelector(
                        SelectSelectorConfig(options=ports, custom_value=True, mode=SelectSelectorMode.DROPDOWN)
                    ),
                    vol.Optional(BAUD_RATE): SelectSelector(
                        SelectSelectorConfig(options=BAUD_RATES, custom_value=False, mode=SelectSelectorMode.DROPDOWN)
                    )
                }
            ),
            errors=errors,
        )


