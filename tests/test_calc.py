"""Tests for the pure calculation helpers."""

import pytest

from custom_components.carbon_savings import calc

GRID = 0.4  # kg/kWh


def test_no_double_counting_pv_into_ev() -> None:
    """10 kWh PV into the car for 50 km: PV + EV equals the avoided tailpipe CO2."""
    params = calc.VehicleParams(
        ev_kwh_per_100km=20.0,
        charging_loss_pct=0.0,
        ice_l_per_100km=6.5,
        fuel_kg_co2_per_l=2.37,
    )
    pv = calc.pv_savings(10.0, GRID)
    ev = calc.vehicle_savings(50.0, params, GRID)
    tailpipe = 50.0 * 6.5 / 100 * 2.37
    assert pv == pytest.approx(4.0)
    assert ev == pytest.approx(tailpipe - 4.0)
    assert pv + ev == pytest.approx(tailpipe)


def test_vehicle_charging_loss_and_fuel() -> None:
    params = calc.VehicleParams(18.0, 10.0, 6.0, 2.37)
    assert calc.vehicle_fuel_saved(100.0, params) == pytest.approx(6.0)
    assert calc.vehicle_savings(100.0, params, GRID) == pytest.approx(
        6.0 * 2.37 - 18.0 * 1.1 * GRID
    )


def test_heat_pump() -> None:
    params = calc.HeatPumpParams(
        boiler_efficiency_pct=85.0, fuel_kwh_per_l=10.0, fuel_kg_co2_per_l=2.65
    )
    litres = calc.heat_fuel_saved(85.0, params)
    assert litres == pytest.approx(10.0)
    assert calc.heat_savings(85.0, params) == pytest.approx(26.5)
    assert calc.heat_pump_electricity_cost(25.0, GRID) == pytest.approx(10.0)


def test_heat_pump_zero_efficiency() -> None:
    params = calc.HeatPumpParams(0.0, 10.0, 2.65)
    assert calc.heat_fuel_saved(100.0, params) == 0.0


def test_tree_cumulative_uptake() -> None:
    f = calc.tree_cumulative_uptake
    assert f(0, 5.5, 23.5, 18) == 0.0
    assert f(1, 5.5, 23.5, 18) == pytest.approx(5.5 + 0.5)
    assert f(10, 5.5, 23.5, 18) == pytest.approx(55 + 50)
    at_mature = 5.5 * 18 + 1.0 * 18**2 / 2
    assert f(18, 5.5, 23.5, 18) == pytest.approx(at_mature)
    assert f(20, 5.5, 23.5, 18) == pytest.approx(at_mature + 2 * 23.5)
    assert f(3, 10, 20, 0) == pytest.approx(60)
