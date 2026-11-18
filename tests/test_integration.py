"""Config flow and runtime tests."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.config_entries import ConfigSubentryData
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.carbon_savings.const import (
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
    CONF_START_DATE,
    CONF_TREE_FACTOR,
    CONF_TREE_MODE,
    DOMAIN,
    SUBENTRY_GRID,
    SUBENTRY_HEAT_PUMP,
    SUBENTRY_PV,
    SUBENTRY_VEHICLE,
)

PV_SENSOR = "sensor.inverter_energy"
INTENSITY = "sensor.grid_intensity"
ODO = "sensor.enyaq_odometer"
HEAT = "sensor.hp_heat"
EL = "sensor.hp_electricity"


def _kwh(hass: HomeAssistant, entity_id: str, value: float, unit: str = "kWh") -> None:
    hass.states.async_set(
        entity_id,
        str(value),
        {
            "unit_of_measurement": unit,
            "device_class": "energy",
            "state_class": "total_increasing",
        },
    )


def _km(hass: HomeAssistant, value: float, unit: str = "km") -> None:
    hass.states.async_set(
        ODO, str(value), {"unit_of_measurement": unit, "device_class": "distance"}
    )


def _entity(hass: HomeAssistant, unique_id: str) -> str:
    entity_id = er.async_get(hass).async_get_entity_id("sensor", DOMAIN, unique_id)
    assert entity_id, unique_id
    return entity_id


def _value(hass: HomeAssistant, unique_id: str) -> float:
    return float(hass.states.get(_entity(hass, unique_id)).state)


def _entry(subentries: list[ConfigSubentryData], **options: Any) -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        title="Carbon Savings",
        unique_id=DOMAIN,
        options={CONF_GRID_FALLBACK: 400.0, CONF_TREE_FACTOR: 50.0, **options},
        subentries_data=subentries,
    )


def _pv_sub(initial: float = 0.0) -> ConfigSubentryData:
    return ConfigSubentryData(
        data={CONF_PRODUCTION_SENSOR: PV_SENSOR, CONF_INITIAL_VALUE: initial},
        subentry_id="pv1",
        subentry_type=SUBENTRY_PV,
        title="PV",
        unique_id=None,
    )


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_config_flow_single_instance(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_GRID_FALLBACK: 380, CONF_TREE_FACTOR: 60}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_GRID_FALLBACK] == 380
    assert result["options"][CONF_TREE_MODE] == "fixed"

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT


async def test_add_pv_subentry_via_flow(hass: HomeAssistant) -> None:
    _kwh(hass, PV_SENSOR, 1000)
    entry = _entry([])
    await _setup(hass, entry)

    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_PV), context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {CONF_NAME: "Dach", CONF_PRODUCTION_SENSOR: PV_SENSOR, CONF_INITIAL_VALUE: 100},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    subentry_id = next(iter(entry.subentries))
    assert _value(hass, f"{subentry_id}_co2_saved") == 100.0

    _kwh(hass, PV_SENSOR, 1010)
    await hass.async_block_till_done()
    assert _value(hass, f"{subentry_id}_co2_saved") == pytest.approx(104.0)
    assert _value(hass, f"{entry.entry_id}_co2_saved_total") == pytest.approx(104.0)
    assert _value(hass, f"{entry.entry_id}_trees_equivalent") == pytest.approx(
        104.0 / 50
    )


async def test_pv_uses_intensity_sensor_and_units(hass: HomeAssistant) -> None:
    _kwh(hass, PV_SENSOR, 1000)
    hass.states.async_set(INTENSITY, "200", {"unit_of_measurement": "gCO2eq/kWh"})
    entry = _entry([_pv_sub()], **{CONF_GRID_INTENSITY_SENSOR: INTENSITY})
    await _setup(hass, entry)

    _kwh(hass, PV_SENSOR, 1005)
    await hass.async_block_till_done()
    assert _value(hass, "pv1_co2_saved") == pytest.approx(1.0)

    # Unit switch to Wh: 1_006_000 Wh = 1006 kWh -> +1 kWh
    hass.states.async_set(INTENSITY, "unavailable")
    _kwh(hass, PV_SENSOR, 1_006_000, "Wh")
    await hass.async_block_till_done()
    assert _value(hass, "pv1_co2_saved") == pytest.approx(1.4)  # fallback 400 g


async def test_reset_and_unavailable_do_not_count(hass: HomeAssistant) -> None:
    _kwh(hass, PV_SENSOR, 1000)
    entry = _entry([_pv_sub()])
    await _setup(hass, entry)

    hass.states.async_set(PV_SENSOR, "unavailable")
    await hass.async_block_till_done()
    _kwh(hass, PV_SENSOR, 1010)
    await hass.async_block_till_done()
    assert _value(hass, "pv1_co2_saved") == pytest.approx(4.0)

    _kwh(hass, PV_SENSOR, 5)  # counter reset
    await hass.async_block_till_done()
    assert _value(hass, "pv1_co2_saved") == pytest.approx(4.0)
    _kwh(hass, PV_SENSOR, 15)
    await hass.async_block_till_done()
    assert _value(hass, "pv1_co2_saved") == pytest.approx(8.0)


async def test_persistence_and_catch_up(hass: HomeAssistant) -> None:
    _kwh(hass, PV_SENSOR, 1000)
    entry = _entry([_pv_sub(initial=10)])
    await _setup(hass, entry)
    _kwh(hass, PV_SENSOR, 1010)
    await hass.async_block_till_done()
    assert _value(hass, "pv1_co2_saved") == pytest.approx(14.0)

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    _kwh(hass, PV_SENSOR, 1020)  # produced while not loaded
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert _value(hass, "pv1_co2_saved") == pytest.approx(18.0)


async def test_reconfigure_initial_value(hass: HomeAssistant) -> None:
    _kwh(hass, PV_SENSOR, 1000)
    entry = _entry([_pv_sub(initial=10)])
    await _setup(hass, entry)
    _kwh(hass, PV_SENSOR, 1010)
    await hass.async_block_till_done()

    result = await entry.start_subentry_reconfigure_flow(hass, "pv1")
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {CONF_NAME: "PV", CONF_PRODUCTION_SENSOR: PV_SENSOR, CONF_INITIAL_VALUE: 1000},
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    await hass.async_block_till_done()
    assert _value(hass, "pv1_co2_saved") == pytest.approx(1004.0)


async def test_vehicle(hass: HomeAssistant) -> None:
    _km(hass, 20000)
    sub = ConfigSubentryData(
        data={
            CONF_ODOMETER_SENSOR: ODO,
            CONF_EV_CONSUMPTION: 20.0,
            CONF_CHARGING_LOSS: 10.0,
            CONF_ICE_CONSUMPTION: 6.5,
            CONF_FUEL_TYPE: "petrol",
            CONF_INITIAL_VALUE: 0.0,
            CONF_INITIAL_FUEL: 100.0,
        },
        subentry_id="car1",
        subentry_type=SUBENTRY_VEHICLE,
        title="Enyaq",
        unique_id=None,
    )
    entry = _entry([sub])
    await _setup(hass, entry)

    _km(hass, 20100)
    await hass.async_block_till_done()
    expected = 6.5 * 2.37 - 20.0 * 1.1 * 0.4
    assert _value(hass, "car1_co2_saved") == pytest.approx(expected, abs=1e-3)
    assert _value(hass, "car1_fuel_saved") == pytest.approx(106.5)


async def test_heat_pump(hass: HomeAssistant) -> None:
    _kwh(hass, HEAT, 0)
    _kwh(hass, EL, 0)
    sub = ConfigSubentryData(
        data={
            CONF_HEAT_SENSOR: HEAT,
            CONF_ELECTRICITY_SENSOR: EL,
            CONF_BOILER_EFFICIENCY: 85.0,
            CONF_INITIAL_VALUE: 0.0,
            CONF_INITIAL_OIL: 0.0,
        },
        subentry_id="hp1",
        subentry_type=SUBENTRY_HEAT_PUMP,
        title="WP",
        unique_id=None,
    )
    entry = _entry([sub])
    await _setup(hass, entry)

    _kwh(hass, HEAT, 85)
    _kwh(hass, EL, 25)
    await hass.async_block_till_done()
    assert _value(hass, "hp1_oil_saved") == pytest.approx(10.0)
    assert _value(hass, "hp1_co2_saved") == pytest.approx(26.5 - 10.0)


async def test_remove_subentry(hass: HomeAssistant) -> None:
    _kwh(hass, PV_SENSOR, 1000)
    entry = _entry([_pv_sub(initial=10)])
    await _setup(hass, entry)
    assert hass.config_entries.async_remove_subentry(entry, "pv1")
    await hass.async_block_till_done()
    assert (
        er.async_get(hass).async_get_entity_id("sensor", DOMAIN, "pv1_co2_saved")
        is None
    )
    assert _value(hass, f"{entry.entry_id}_co2_saved_total") == 0.0


async def test_vehicle_consumption_sensor(hass: HomeAssistant) -> None:
    _km(hass, 20000)
    cons = "sensor.enyaq_avg_consumption"
    hass.states.async_set(cons, "150", {"unit_of_measurement": "Wh/km"})
    sub = ConfigSubentryData(
        data={
            CONF_ODOMETER_SENSOR: ODO,
            CONF_EV_CONSUMPTION_SENSOR: cons,
            CONF_EV_CONSUMPTION: 22.0,
            CONF_CHARGING_LOSS: 0.0,
            CONF_ICE_CONSUMPTION: 6.0,
            CONF_FUEL_TYPE: "petrol",
            CONF_INITIAL_VALUE: 0.0,
            CONF_INITIAL_FUEL: 0.0,
        },
        subentry_id="car1",
        subentry_type=SUBENTRY_VEHICLE,
        title="Enyaq",
        unique_id=None,
    )
    await _setup(hass, _entry([sub]))

    _km(hass, 20100)  # sensor: 150 Wh/km = 15 kWh/100 km
    await hass.async_block_till_done()
    first = 6.0 * 2.37 - 15.0 * 0.4
    assert _value(hass, "car1_co2_saved") == pytest.approx(first, abs=1e-3)

    hass.states.async_set(cons, "0", {"unit_of_measurement": "kWh/100km"})
    _km(hass, 20200)  # implausible 0 -> fixed 22 kWh/100 km
    await hass.async_block_till_done()
    second = 6.0 * 2.37 - 22.0 * 0.4
    assert _value(hass, "car1_co2_saved") == pytest.approx(first + second, abs=1e-3)


async def test_grid_not_in_total(hass: HomeAssistant) -> None:
    _kwh(hass, PV_SENSOR, 1000)
    _kwh(hass, "sensor.import", 500)
    _kwh(hass, "sensor.export", 800)
    grid = ConfigSubentryData(
        data={CONF_IMPORT_SENSOR: "sensor.import", CONF_EXPORT_SENSOR: "sensor.export"},
        subentry_id="grid1",
        subentry_type=SUBENTRY_GRID,
        title="Netz",
        unique_id=None,
    )
    entry = _entry([_pv_sub(), grid])
    await _setup(hass, entry)

    _kwh(hass, PV_SENSOR, 1010)
    _kwh(hass, "sensor.import", 505)
    _kwh(hass, "sensor.export", 808)
    await hass.async_block_till_done()
    assert _value(hass, "grid1_grid_import_co2") == pytest.approx(2.0)
    assert _value(hass, "grid1_grid_export_co2") == pytest.approx(3.2)
    assert _value(hass, "grid1_grid_balance_co2") == pytest.approx(1.2)
    assert _value(hass, f"{entry.entry_id}_co2_saved_total") == pytest.approx(4.0)


async def test_grid_subentry_flow(hass: HomeAssistant) -> None:
    entry = _entry([])
    await _setup(hass, entry)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_GRID), context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {CONF_NAME: "Netz", CONF_IMPORT_SENSOR: "sensor.import"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_trees_growth_mode(hass: HomeAssistant) -> None:
    from datetime import date, timedelta

    from homeassistant.util import dt as dt_util

    from custom_components.carbon_savings import calc

    _kwh(hass, PV_SENSOR, 1000)
    _km(hass, 1000)
    today = dt_util.now().date()
    pv_start = (today - timedelta(days=round(8 * 365.25))).isoformat()
    pv = ConfigSubentryData(
        data={
            CONF_PRODUCTION_SENSOR: PV_SENSOR,
            CONF_INITIAL_VALUE: 7600.0,
            CONF_START_DATE: pv_start,
        },
        subentry_id="pv1",
        subentry_type=SUBENTRY_PV,
        title="PV",
        unique_id=None,
    )
    car = ConfigSubentryData(
        data={
            CONF_ODOMETER_SENSOR: ODO,
            CONF_EV_CONSUMPTION: 20.0,
            CONF_CHARGING_LOSS: 10.0,
            CONF_ICE_CONSUMPTION: 6.0,
            CONF_FUEL_TYPE: "petrol",
            CONF_INITIAL_VALUE: 500.0,
            CONF_INITIAL_FUEL: 0.0,
        },  # no start date -> fixed factor fallback
        subentry_id="car1",
        subentry_type=SUBENTRY_VEHICLE,
        title="Auto",
        unique_id=None,
    )
    entry = _entry([pv, car], **{CONF_TREE_MODE: "growth"})
    await _setup(hass, entry)

    per_tree = calc.tree_cumulative_uptake(
        (today - date.fromisoformat(pv_start)).days / 365.25, 5.5, 23.5, 18
    )
    expected = 7600.0 / per_tree + 500.0 / 50.0
    state = hass.states.get(_entity(hass, f"{entry.entry_id}_trees_equivalent"))
    assert float(state.state) == pytest.approx(expected, rel=1e-3)
    assert state.attributes["mode"] == "growth"
    assert set(state.attributes["by_source"]) == {"PV", "Auto"}
