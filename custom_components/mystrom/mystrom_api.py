"""API client for myStrom devices."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class MyStromAPI:
    """Class to communicate with myStrom WiFi Switch via REST API."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.host = host
        self.session = session
        self._base_url = f"http://{host}"

    async def get_state(self) -> dict[str, Any]:
        """Get current state of the device.

        Returns:
            Dict with keys:
            - power: Current power consumption in W
            - relay: Relay state (True/False)
            - temperature: Device temperature in °C
        """
        try:
            async with self.session.get(
                f"{self._base_url}/report",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                data = await response.json()

                return {
                    "power": data.get("power", 0.0),
                    "relay": data.get("relay", False),
                    "temperature": data.get("temperature", 0.0),
                }
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching myStrom state: %s", err)
            raise
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout fetching myStrom state")
            raise

    async def turn_on(self) -> bool:
        """Turn on the switch."""
        try:
            async with self.session.get(
                f"{self._base_url}/relay",
                params={"state": "1"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return True
        except aiohttp.ClientError as err:
            _LOGGER.error("Error turning on myStrom switch: %s", err)
            return False

    async def turn_off(self) -> bool:
        """Turn off the switch."""
        try:
            async with self.session.get(
                f"{self._base_url}/relay",
                params={"state": "0"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return True
        except aiohttp.ClientError as err:
            _LOGGER.error("Error turning off myStrom switch: %s", err)
            return False

    async def toggle(self) -> bool:
        """Toggle the switch."""
        try:
            async with self.session.get(
                f"{self._base_url}/toggle",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return True
        except aiohttp.ClientError as err:
            _LOGGER.error("Error toggling myStrom switch: %s", err)
            return False

    async def get_info(self) -> dict[str, Any]:
        """Get device information.

        Returns:
            Dict with device info like MAC address, version, etc.
        """
        try:
            async with self.session.get(
                f"{self._base_url}/info",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching myStrom info: %s", err)
            raise

    async def test_connection(self) -> bool:
        """Test if the device is reachable."""
        try:
            await self.get_state()
            return True
        except Exception:
            return False
