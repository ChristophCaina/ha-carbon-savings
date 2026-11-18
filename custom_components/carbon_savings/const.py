"""Constants for the Carbon Savings integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "carbon_savings"

# Subentry types
SUBENTRY_PV: Final = "pv"
SUBENTRY_VEHICLE: Final = "vehicle"
SUBENTRY_HEAT_PUMP: Final = "heat_pump"
SUBENTRY_GRID: Final = "grid"

# Hub (main entry) options
CONF_GRID_INTENSITY_SENSOR: Final = "grid_intensity_sensor"
CONF_GRID_FALLBACK: Final = "grid_fallback"  # g CO2 / kWh
CONF_TREE_FACTOR: Final = "tree_factor"  # kg CO2 per tree (fixed mode)
CONF_TREE_MODE: Final = "tree_mode"
CONF_TREE_RATE_YOUNG: Final = "tree_rate_young"  # kg CO2 / year in year 1
CONF_TREE_RATE_MATURE: Final = "tree_rate_mature"  # kg CO2 / year when mature
CONF_TREE_YEARS_TO_MATURE: Final = "tree_years_to_mature"

TREE_MODE_FIXED: Final = "fixed"
TREE_MODE_GROWTH: Final = "growth"

# Common subentry options
CONF_INITIAL_VALUE: Final = "initial_value"  # kg CO2 already saved before tracking
CONF_START_DATE: Final = "start_date"  # in operation since (YYYY-MM-DD)

# PV
CONF_PRODUCTION_SENSOR: Final = "production_sensor"

# Vehicle
CONF_ODOMETER_SENSOR: Final = "odometer_sensor"
CONF_EV_CONSUMPTION: Final = "ev_consumption"  # kWh / 100 km
CONF_EV_CONSUMPTION_SENSOR: Final = "ev_consumption_sensor"  # optional entity
CONF_CHARGING_LOSS: Final = "charging_loss"  # % on top of consumption
CONF_ICE_CONSUMPTION: Final = "ice_consumption"  # l / 100 km
CONF_FUEL_TYPE: Final = "fuel_type"
CONF_INITIAL_FUEL: Final = "initial_fuel"  # l fuel already saved

# Heat pump
CONF_HEAT_SENSOR: Final = "heat_sensor"  # thermal energy delivered
CONF_ELECTRICITY_SENSOR: Final = "electricity_sensor"  # electrical energy consumed
CONF_REPLACED_FUEL: Final = "replaced_fuel"
CONF_BOILER_EFFICIENCY: Final = "boiler_efficiency"  # %
CONF_INITIAL_OIL: Final = "initial_oil"  # l oil already saved

# Grid (footprint view, not part of the savings total)
CONF_IMPORT_SENSOR: Final = "import_sensor"
CONF_EXPORT_SENSOR: Final = "export_sensor"

FUEL_PETROL: Final = "petrol"
FUEL_DIESEL: Final = "diesel"
FUEL_HEATING_OIL: Final = "heating_oil"

# kg CO2 per litre (direct combustion, tank-to-wheel)
FUEL_CO2_PER_LITRE: Final[dict[str, float]] = {
    FUEL_PETROL: 2.37,
    FUEL_DIESEL: 2.65,
    FUEL_HEATING_OIL: 2.65,
}

# Lower heating value, kWh per litre
FUEL_KWH_PER_LITRE: Final[dict[str, float]] = {
    FUEL_HEATING_OIL: 10.0,
}

DEFAULT_GRID_FALLBACK: Final = 380.0
DEFAULT_TREE_FACTOR: Final = 60.0
DEFAULT_TREE_RATE_YOUNG: Final = 5.5
DEFAULT_TREE_RATE_MATURE: Final = 23.5
DEFAULT_TREE_YEARS_TO_MATURE: Final = 18.0
MIN_TREE_AGE_YEARS: Final = 1.0
DEFAULT_CHARGING_LOSS: Final = 10.0
DEFAULT_BOILER_EFFICIENCY: Final = 85.0

SIGNAL_SAVINGS_UPDATED: Final = f"{DOMAIN}_savings_updated_{{}}"
