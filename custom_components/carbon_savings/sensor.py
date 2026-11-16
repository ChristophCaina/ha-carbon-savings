"""Sensors for the Carbon Savings integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import UnitOfMass, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import CarbonSavingsConfigEntry, CarbonSavingsData
from .const import DOMAIN, SUBENTRY_GRID, SUBENTRY_HEAT_PUMP, SUBENTRY_VEHICLE
from .tracker import SavingsTracker

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CarbonSavingsConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for the hub and every subentry."""
    data = entry.runtime_data

    async_add_entities([TotalCo2Sensor(entry, data), TreesSensor(entry, data)])

    for subentry_id, tracker in data.trackers.items():
        subentry = entry.subentries[subentry_id]
        if subentry.subentry_type == SUBENTRY_GRID:
            async_add_entities(
                [
                    GridSensor(subentry, tracker, "grid_import_co2"),
                    GridSensor(subentry, tracker, "grid_export_co2"),
                    GridSensor(subentry, tracker, "grid_balance_co2"),
                ],
                config_subentry_id=subentry_id,
            )
            continue
        entities: list[SensorEntity] = [SubentryCo2Sensor(subentry, tracker)]
        if subentry.subentry_type == SUBENTRY_VEHICLE:
            entities.append(SubentryLitreSensor(subentry, tracker, "fuel_saved"))
        elif subentry.subentry_type == SUBENTRY_HEAT_PUMP:
            entities.append(SubentryLitreSensor(subentry, tracker, "oil_saved"))
        async_add_entities(entities, config_subentry_id=subentry_id)


class _BaseSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False


class _HubSensor(_BaseSensor):
    """Sensor aggregating all subentries."""

    def __init__(
        self, entry: CarbonSavingsConfigEntry, data: CarbonSavingsData
    ) -> None:
        self._data = data
        self._attr_unique_id = f"{entry.entry_id}_{self.entity_description_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            entry_type=DeviceEntryType.SERVICE,
        )

    entity_description_key = ""

    async def async_added_to_hass(self) -> None:
        for tracker in self._data.trackers.values():
            self.async_on_remove(
                async_dispatcher_connect(self.hass, tracker.signal, self._updated)
            )

    @callback
    def _updated(self) -> None:
        self.async_write_ha_state()


class TotalCo2Sensor(_HubSensor):
    """Total CO2 saved across all sources."""

    entity_description_key = "co2_saved_total"
    _attr_translation_key = "co2_saved_total"
    _attr_device_class = SensorDeviceClass.WEIGHT
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_suggested_display_precision = 1

    @property
    def native_value(self) -> float:
        return round(self._data.co2_total, 3)


class TreesSensor(_HubSensor):
    """Total CO2 saved expressed as planted trees."""

    entity_description_key = "trees_equivalent"
    _attr_translation_key = "trees_equivalent"
    _attr_state_class = SensorStateClass.TOTAL
    # Unit comes from translations ("trees" / "Bäume")
    _attr_suggested_display_precision = 1

    @property
    def native_value(self) -> float | None:
        factor = self._data.tree_factor
        if factor <= 0:
            return None
        return round(self._data.co2_total / factor, 3)

    @property
    def extra_state_attributes(self) -> dict[str, float]:
        return {"kg_co2_per_tree": self._data.tree_factor}


class _SubentrySensor(_BaseSensor):
    """Sensor bound to a subentry's tracker."""

    def __init__(self, subentry: ConfigSubentry, tracker: SavingsTracker) -> None:
        self._tracker = tracker
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=subentry.title,
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, self._tracker.signal, self._updated)
        )

    @callback
    def _updated(self) -> None:
        self.async_write_ha_state()


class SubentryCo2Sensor(_SubentrySensor):
    """CO2 saved by a single source."""

    _attr_translation_key = "co2_saved"
    _attr_device_class = SensorDeviceClass.WEIGHT
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_suggested_display_precision = 1

    def __init__(self, subentry: ConfigSubentry, tracker: SavingsTracker) -> None:
        super().__init__(subentry, tracker)
        self._attr_unique_id = f"{subentry.subentry_id}_co2_saved"

    @property
    def native_value(self) -> float:
        return round(self._tracker.co2_total, 3)


class SubentryLitreSensor(_SubentrySensor):
    """Litres of fuel / heating oil not burned."""

    _attr_device_class = SensorDeviceClass.VOLUME
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_suggested_display_precision = 1

    def __init__(
        self, subentry: ConfigSubentry, tracker: SavingsTracker, key: str
    ) -> None:
        super().__init__(subentry, tracker)
        self._attr_translation_key = key
        self._attr_unique_id = f"{subentry.subentry_id}_{key}"

    @property
    def native_value(self) -> float:
        return round(self._tracker.secondary_total, 3)


class GridSensor(_SubentrySensor):
    """Grid footprint: emissions of imports, credit for exports, balance."""

    _attr_device_class = SensorDeviceClass.WEIGHT
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_suggested_display_precision = 1

    def __init__(
        self, subentry: ConfigSubentry, tracker: SavingsTracker, key: str
    ) -> None:
        super().__init__(subentry, tracker)
        self._key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{subentry.subentry_id}_{key}"

    @property
    def native_value(self) -> float:
        imported = self._tracker.secondary_total
        exported = self._tracker.co2_total
        if self._key == "grid_import_co2":
            return round(imported, 3)
        if self._key == "grid_export_co2":
            return round(exported, 3)
        return round(exported - imported, 3)
