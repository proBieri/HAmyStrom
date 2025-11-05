"""Platform for myStrom switch integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up myStrom switch based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    async_add_entities([MyStromSwitch(coordinator, api, entry)], True)


class MyStromSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a myStrom WiFi Switch."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator, api, entry: ConfigEntry) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._api = api
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_switch"
        device_name = entry.data.get(CONF_NAME, "myStrom Switch")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "myStrom",
            "model": "WiFi Switch",
            "configuration_url": f"http://{entry.data[CONF_HOST]}",
        }

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if self.coordinator.data:
            return self.coordinator.data.get("relay", False)
        return False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "power": self.coordinator.data.get("power", 0),
            "temperature": self.coordinator.data.get("temperature", 0),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if await self._api.turn_on():
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if await self._api.turn_off():
            await self.coordinator.async_request_refresh()

    async def async_toggle(self, **kwargs: Any) -> None:
        """Toggle the switch."""
        if await self._api.toggle():
            await self.coordinator.async_request_refresh()
