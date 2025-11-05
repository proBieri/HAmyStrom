"""Platform for myStrom sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
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
    """Set up myStrom sensors based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    sensors = [
        MyStromPowerSensor(coordinator, entry),
        MyStromEnergySensor(coordinator, entry),
        MyStromTemperatureSensor(coordinator, entry),
    ]

    async_add_entities(sensors, True)


class MyStromSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for myStrom sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "myStrom Switch",
            "manufacturer": "myStrom",
            "model": "WiFi Switch",
            "configuration_url": f"http://{entry.data[CONF_HOST]}",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success


class MyStromPowerSensor(MyStromSensorBase):
    """Representation of myStrom power consumption sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the power sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._attr_name = "Power"

    @property
    def native_value(self) -> float | None:
        """Return the current power consumption."""
        if self.coordinator.data:
            return self.coordinator.data.get("power", 0.0)
        return None


class MyStromEnergySensor(MyStromSensorBase):
    """Representation of myStrom energy consumption sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the energy sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_energy"
        self._attr_name = "Energy"
        self._total_energy = 0.0
        self._last_power = 0.0

    @property
    def native_value(self) -> float | None:
        """Return the total energy consumption in kWh.

        This calculates cumulative energy based on power readings.
        For more accurate energy tracking, the myStrom API would need
        to provide direct energy readings.
        """
        if self.coordinator.data:
            current_power = self.coordinator.data.get("power", 0.0)

            # Simple integration: assume linear power consumption between readings
            # Update interval is typically 30 seconds
            if self._last_power > 0 or current_power > 0:
                avg_power = (self._last_power + current_power) / 2
                # Energy = Power * Time (in hours)
                # 30 seconds = 30/3600 hours
                energy_increment = (avg_power * 30) / 3600000  # Convert to kWh
                self._total_energy += energy_increment

            self._last_power = current_power
            return round(self._total_energy, 3)
        return None


class MyStromTemperatureSensor(MyStromSensorBase):
    """Representation of myStrom temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        """Initialize the temperature sensor."""
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_temperature"
        self._attr_name = "Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the current temperature."""
        if self.coordinator.data:
            return self.coordinator.data.get("temperature", 0.0)
        return None
