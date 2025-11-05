"""Config flow for myStrom Switch integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .mystrom_api import MyStromAPI

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=5, max=300)
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    session = async_get_clientsession(hass)
    api = MyStromAPI(data[CONF_HOST], session)

    if not await api.test_connection():
        raise CannotConnect

    # Get device info for unique ID
    try:
        info = await api.get_info()
        mac = info.get("mac", data[CONF_HOST].replace(".", "_"))
    except Exception:
        # Fallback if info endpoint doesn't work
        mac = data[CONF_HOST].replace(".", "_")

    return {"title": f"myStrom Switch ({data[CONF_HOST]})", "mac": mac}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for myStrom Switch."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID to prevent duplicate entries
                await self.async_set_unique_id(info["mac"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_discovery(
        self, discovery_info: dict[str, Any]
    ) -> FlowResult:
        """Handle discovery of a myStrom device."""
        host = discovery_info[CONF_HOST]
        mac = discovery_info.get("mac", host.replace(".", "_"))

        # Set unique ID to prevent duplicate entries
        await self.async_set_unique_id(mac)
        self._abort_if_unique_id_configured()

        # Store the discovered host for confirmation step
        self.context["title_placeholders"] = {"host": host}

        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        if user_input is not None:
            host = self.context["title_placeholders"]["host"]
            return self.async_create_entry(
                title=f"myStrom Switch ({host})",
                data={CONF_HOST: host, CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL},
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders=self.context["title_placeholders"],
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
