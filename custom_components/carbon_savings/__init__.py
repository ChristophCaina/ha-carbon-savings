"""The Carbon Savings integration."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    Platform,
    UnitOfEnergyDistance,
)
from homeassistant.core import HomeAssistant
from homeassistant.util.unit_conversion import EnergyDistanceConverter

from . import calc
from .const import (
    CONF_BOILER_EFFICIENCY,
    CONF_CHARGING_LOSS,
    CONF_ELECTRICITY_SENSOR,
    CONF_EV_CONSUMPTION,
    CONF_EV_CONSUMPTION_SENSOR,
    CONF_EXPORT_SENSOR,
    CONF_FUEL_TYPE,
    CONF_GRID_FALLBACK,
    CONF_GRID_INTENSITY_SENSOR,
    CONF_HEAT_SENSOR,
    CONF_ICE_CONSUMPTION,
    CONF_IMPORT_SENSOR,
    CONF_INITIAL_FUEL,
    CONF_INITIAL_OIL,
    CONF_INITIAL_VALUE,
    CONF_ODOMETER_SENSOR,
    CONF_PRODUCTION_SENSOR,
    CONF_TREE_FACTOR,
    DEFAULT_BOILER_EFFICIENCY,
    DEFAULT_CHARGING_LOSS,
    DEFAULT_GRID_FALLBACK,
    DEFAULT_TREE_FACTOR,
    FUEL_CO2_PER_LITRE,
    FUEL_HEATING_OIL,
    FUEL_KWH_PER_LITRE,
    FUEL_PETROL,
    SUBENTRY_GRID,
    SUBENTRY_HEAT_PUMP,
    SUBENTRY_PV,
    SUBENTRY_VEHICLE,
)
from .tracker import KIND_DISTANCE, KIND_ENERGY, SavingsTracker, TrackedSource

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass
class CarbonSavingsData:
    """Runtime data of a config entry."""

    hass: HomeAssistant
    entry: ConfigEntry
    trackers: dict[str, SavingsTracker] = field(default_factory=dict)

    @property
    def tree_factor(self) -> float:
        """kg CO2 per tree equivalent."""
        return float(self.entry.options.get(CONF_TREE_FACTOR, DEFAULT_TREE_FACTOR))

    def grid_g_per_kwh(self) -> float:
        """Current grid carbon intensity in g/kWh (sensor or fallback)."""
        fallback = float(
            self.entry.options.get(CONF_GRID_FALLBACK, DEFAULT_GRID_FALLBACK)
        )
        entity_id = self.entry.options.get(CONF_GRID_INTENSITY_SENSOR)
        if not entity_id:
            return fallback
        state = self.hass.states.get(entity_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return fallback
        try:
            value = float(state.state)
        except ValueError:
            return fallback
        unit = str(state.attributes.get("unit_of_measurement") or "").lower()
        if unit.startswith("kg"):
            value *= 1000.0
        return value

    def ev_consumption(self, entity_id: str | None, fallback: float) -> float:
        """EV consumption in kWh/100 km from a sensor, or the fixed fallback."""
        if not entity_id:
            return fallback
        state = self.hass.states.get(entity_id)
        if state is None:
            return fallback
        try:
            value = float(state.state)
        except ValueError:
            return fallback
        unit = state.attributes.get("unit_of_measurement")
        if unit and unit != UnitOfEnergyDistance.KILO_WATT_HOUR_PER_100_KM:
            try:
                value = EnergyDistanceConverter.convert(
                    value, unit, UnitOfEnergyDistance.KILO_WATT_HOUR_PER_100_KM
                )
            except Exception:  # noqa: BLE001 - unknown unit
                _LOGGER.warning(
                    "Unsupported unit '%s' on %s, using fixed consumption",
                    unit,
                    entity_id,
                )
                return fallback
        # Ignore implausible values (e.g. 0 right after a trip reset)
        if not 5.0 <= value <= 60.0:
            return fallback
        return value

    def grid_kg_per_kwh(self) -> float:
        """Current grid carbon intensity in kg/kWh."""
        return calc.grams_to_kg(self.grid_g_per_kwh())

    @property
    def co2_total(self) -> float:
        """Sum of all trackers in kg."""
        return sum(
            tracker.co2_total
            for tracker in self.trackers.values()
            if tracker.include_in_total
        )


type CarbonSavingsConfigEntry = ConfigEntry[CarbonSavingsData]


def _build_tracker(
    data: CarbonSavingsData, subentry: ConfigSubentry
) -> SavingsTracker | None:
    """Create the tracker matching a subentry."""
    hass = data.hass
    conf = subentry.data
    initial_co2 = float(conf.get(CONF_INITIAL_VALUE, 0.0))

    if subentry.subentry_type == SUBENTRY_PV:

        def _pv(delta: float) -> tuple[float, float]:
            return calc.pv_savings(delta, data.grid_kg_per_kwh()), delta

        return SavingsTracker(
            hass,
            subentry.subentry_id,
            [
                TrackedSource(
                    "production", conf[CONF_PRODUCTION_SENSOR], KIND_ENERGY, _pv
                )
            ],
            initial_co2=initial_co2,
        )

    if subentry.subentry_type == SUBENTRY_VEHICLE:
        consumption_sensor = conf.get(CONF_EV_CONSUMPTION_SENSOR)
        fixed_consumption = float(conf[CONF_EV_CONSUMPTION])
        charging_loss = float(conf.get(CONF_CHARGING_LOSS, DEFAULT_CHARGING_LOSS))
        ice = float(conf[CONF_ICE_CONSUMPTION])
        fuel_co2 = FUEL_CO2_PER_LITRE[conf.get(CONF_FUEL_TYPE, FUEL_PETROL)]

        def _vehicle(delta: float) -> tuple[float, float]:
            params = calc.VehicleParams(
                ev_kwh_per_100km=data.ev_consumption(
                    consumption_sensor, fixed_consumption
                ),
                charging_loss_pct=charging_loss,
                ice_l_per_100km=ice,
                fuel_kg_co2_per_l=fuel_co2,
            )
            return (
                calc.vehicle_savings(delta, params, data.grid_kg_per_kwh()),
                calc.vehicle_fuel_saved(delta, params),
            )

        return SavingsTracker(
            hass,
            subentry.subentry_id,
            [
                TrackedSource(
                    "odometer", conf[CONF_ODOMETER_SENSOR], KIND_DISTANCE, _vehicle
                )
            ],
            initial_co2=initial_co2,
            initial_secondary=float(conf.get(CONF_INITIAL_FUEL, 0.0)),
        )

    if subentry.subentry_type == SUBENTRY_HEAT_PUMP:
        params_hp = calc.HeatPumpParams(
            boiler_efficiency_pct=float(
                conf.get(CONF_BOILER_EFFICIENCY, DEFAULT_BOILER_EFFICIENCY)
            ),
            fuel_kwh_per_l=FUEL_KWH_PER_LITRE[FUEL_HEATING_OIL],
            fuel_kg_co2_per_l=FUEL_CO2_PER_LITRE[FUEL_HEATING_OIL],
        )

        def _heat(delta: float) -> tuple[float, float]:
            return (
                calc.heat_savings(delta, params_hp),
                calc.heat_fuel_saved(delta, params_hp),
            )

        def _electricity(delta: float) -> tuple[float, float]:
            return -calc.heat_pump_electricity_cost(delta, data.grid_kg_per_kwh()), 0.0

        return SavingsTracker(
            hass,
            subentry.subentry_id,
            [
                TrackedSource("heat", conf[CONF_HEAT_SENSOR], KIND_ENERGY, _heat),
                TrackedSource(
                    "electricity",
                    conf[CONF_ELECTRICITY_SENSOR],
                    KIND_ENERGY,
                    _electricity,
                ),
            ],
            initial_co2=initial_co2,
            initial_secondary=float(conf.get(CONF_INITIAL_OIL, 0.0)),
        )

    if subentry.subentry_type == SUBENTRY_GRID:
        # co2 = credit for exported kWh, secondary = emissions of imported kWh

        def _import(delta: float) -> tuple[float, float]:
            return 0.0, delta * data.grid_kg_per_kwh()

        def _export(delta: float) -> tuple[float, float]:
            return delta * data.grid_kg_per_kwh(), 0.0

        sources = [
            TrackedSource("import", conf[CONF_IMPORT_SENSOR], KIND_ENERGY, _import)
        ]
        if export := conf.get(CONF_EXPORT_SENSOR):
            sources.append(TrackedSource("export", export, KIND_ENERGY, _export))
        return SavingsTracker(
            hass, subentry.subentry_id, sources, include_in_total=False
        )

    _LOGGER.warning("Unknown subentry type %s", subentry.subentry_type)
    return None


async def async_setup_entry(
    hass: HomeAssistant, entry: CarbonSavingsConfigEntry
) -> bool:
    """Set up Carbon Savings from a config entry."""
    data = CarbonSavingsData(hass, entry)
    for subentry in entry.subentries.values():
        if (tracker := _build_tracker(data, subentry)) is not None:
            await tracker.async_load()
            data.trackers[subentry.subentry_id] = tracker
    entry.runtime_data = data

    # Trackers start after the sensors exist so first updates are not missed.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    for tracker in data.trackers.values():
        await tracker.async_start()

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: CarbonSavingsConfigEntry
) -> bool:
    """Unload a config entry."""
    for tracker in entry.runtime_data.trackers.values():
        await tracker.async_stop()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(
    hass: HomeAssistant, entry: CarbonSavingsConfigEntry
) -> None:
    """Reload on option or subentry changes; drop storage of removed subentries."""
    removed = set(entry.runtime_data.trackers) - set(entry.subentries)
    old_trackers = dict(entry.runtime_data.trackers)
    await hass.config_entries.async_reload(entry.entry_id)
    for subentry_id in removed:
        await old_trackers[subentry_id].async_remove()


async def async_remove_entry(
    hass: HomeAssistant, entry: CarbonSavingsConfigEntry
) -> None:
    """Delete stored data when the whole entry is removed."""
    for subentry in entry.subentries.values():
        await SavingsTracker(hass, subentry.subentry_id, []).async_remove()
