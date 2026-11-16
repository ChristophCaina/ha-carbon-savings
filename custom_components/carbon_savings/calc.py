"""Pure calculation helpers – no Home Assistant dependencies.

Accounting model
----------------
Every source is compared against its own fossil alternative and every
electrical consumer is charged the full grid intensity, regardless of whether
the kWh actually came from PV, battery or grid. PV in turn is credited the
grid intensity for *every* kWh it produces. The sum of all components is then
exactly the difference between "no PV / combustion car / oil boiler" and the
real household – without double counting and without having to know where a
particular kWh came from.
"""

from __future__ import annotations

from dataclasses import dataclass


def grams_to_kg(value_g_per_kwh: float) -> float:
    """Convert g/kWh to kg/kWh."""
    return value_g_per_kwh / 1000.0


def pv_savings(delta_kwh: float, grid_kg_per_kwh: float) -> float:
    """CO2 (kg) avoided by producing delta_kwh of PV energy."""
    return delta_kwh * grid_kg_per_kwh


@dataclass(frozen=True, slots=True)
class VehicleParams:
    """Parameters describing an EV and its combustion reference."""

    ev_kwh_per_100km: float
    charging_loss_pct: float
    ice_l_per_100km: float
    fuel_kg_co2_per_l: float


def vehicle_fuel_saved(delta_km: float, params: VehicleParams) -> float:
    """Litres of fuel the reference combustion car would have burned."""
    return delta_km * params.ice_l_per_100km / 100.0


def vehicle_savings(
    delta_km: float, params: VehicleParams, grid_kg_per_kwh: float
) -> float:
    """Net CO2 (kg) saved by driving delta_km electrically."""
    ice = vehicle_fuel_saved(delta_km, params) * params.fuel_kg_co2_per_l
    ev_kwh = (
        delta_km
        * params.ev_kwh_per_100km
        / 100.0
        * (1.0 + params.charging_loss_pct / 100.0)
    )
    return ice - ev_kwh * grid_kg_per_kwh


@dataclass(frozen=True, slots=True)
class HeatPumpParams:
    """Parameters describing the replaced fossil heating."""

    boiler_efficiency_pct: float
    fuel_kwh_per_l: float
    fuel_kg_co2_per_l: float


def heat_fuel_saved(delta_heat_kwh: float, params: HeatPumpParams) -> float:
    """Litres of fuel the old boiler would have burned for delta_heat_kwh."""
    useful_kwh_per_l = params.fuel_kwh_per_l * params.boiler_efficiency_pct / 100.0
    if useful_kwh_per_l <= 0:
        return 0.0
    return delta_heat_kwh / useful_kwh_per_l


def heat_savings(delta_heat_kwh: float, params: HeatPumpParams) -> float:
    """Gross CO2 (kg) avoided by not burning fuel for delta_heat_kwh."""
    return heat_fuel_saved(delta_heat_kwh, params) * params.fuel_kg_co2_per_l


def heat_pump_electricity_cost(delta_el_kwh: float, grid_kg_per_kwh: float) -> float:
    """CO2 (kg) attributed to the heat pump's electricity (to be subtracted)."""
    return delta_el_kwh * grid_kg_per_kwh
