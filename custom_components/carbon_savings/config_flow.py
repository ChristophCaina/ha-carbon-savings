"""Config flow for the Carbon Savings integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector
import voluptuous as vol

from .const import (
    CONF_BOILER_EFFICIENCY,
    CONF_CHARGING_LOSS,
    CONF_ELECTRICITY_SENSOR,
    CONF_EV_CONSUMPTION,
    CONF_EV_CONSUMPTION_SENSOR,
    CONF_EXPORT_SENSOR,
    CONF_FUEL_SCOPE,
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
    CONF_TREE_RATE_MATURE,
    CONF_TREE_RATE_YOUNG,
    CONF_TREE_YEARS_TO_MATURE,
    DEFAULT_BOILER_EFFICIENCY,
    DEFAULT_CHARGING_LOSS,
    DEFAULT_GRID_FALLBACK,
    DEFAULT_TREE_FACTOR,
    DEFAULT_TREE_RATE_MATURE,
    DEFAULT_TREE_RATE_YOUNG,
    DEFAULT_TREE_YEARS_TO_MATURE,
    DOMAIN,
    FUEL_DIESEL,
    FUEL_PETROL,
    SCOPE_DIRECT,
    SCOPE_LIFECYCLE,
    SUBENTRY_GRID,
    SUBENTRY_HEAT_PUMP,
    SUBENTRY_PV,
    SUBENTRY_VEHICLE,
    TREE_MODE_FIXED,
    TREE_MODE_GROWTH,
)


def _number(
    unit: str, min_value: float = 0, max_value: float = 1_000_000, step: float = 0.1
) -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=min_value,
            max=max_value,
            step=step,
            unit_of_measurement=unit,
            mode=selector.NumberSelectorMode.BOX,
        )
    )


def _sensor(device_class: SensorDeviceClass) -> selector.EntitySelector:
    return selector.EntitySelector(
        selector.EntitySelectorConfig(domain="sensor", device_class=device_class)
    )


HUB_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_GRID_INTENSITY_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_GRID_FALLBACK, default=DEFAULT_GRID_FALLBACK): _number(
            "g/kWh", max_value=2000, step=1
        ),
        vol.Required(CONF_FUEL_SCOPE, default=SCOPE_DIRECT): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[SCOPE_DIRECT, SCOPE_LIFECYCLE],
                translation_key=CONF_FUEL_SCOPE,
            )
        ),
        vol.Required(CONF_TREE_MODE, default=TREE_MODE_FIXED): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[TREE_MODE_FIXED, TREE_MODE_GROWTH],
                translation_key=CONF_TREE_MODE,
            )
        ),
        vol.Required(CONF_TREE_FACTOR, default=DEFAULT_TREE_FACTOR): _number(
            "kg", min_value=0.1, max_value=10000
        ),
        vol.Required(CONF_TREE_RATE_YOUNG, default=DEFAULT_TREE_RATE_YOUNG): _number(
            "kg/a", max_value=1000
        ),
        vol.Required(CONF_TREE_RATE_MATURE, default=DEFAULT_TREE_RATE_MATURE): _number(
            "kg/a", max_value=1000
        ),
        vol.Required(
            CONF_TREE_YEARS_TO_MATURE, default=DEFAULT_TREE_YEARS_TO_MATURE
        ): _number("a", max_value=200, step=1),
    }
)


class CarbonSavingsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the main config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the single hub entry."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(
                title="Carbon Savings", data={}, options=user_input
            )
        return self.async_show_form(step_id="user", data_schema=HUB_SCHEMA)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return CarbonSavingsOptionsFlow()

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return the supported subentry types."""
        return {
            SUBENTRY_PV: PvSubentryFlow,
            SUBENTRY_VEHICLE: VehicleSubentryFlow,
            SUBENTRY_HEAT_PUMP: HeatPumpSubentryFlow,
            SUBENTRY_GRID: GridSubentryFlow,
        }


class CarbonSavingsOptionsFlow(OptionsFlow):
    """Edit grid intensity and tree factor."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                HUB_SCHEMA, self.config_entry.options
            ),
        )


class _BaseSubentryFlow(ConfigSubentryFlow):
    """Shared user/reconfigure handling; subclasses provide the schema."""

    def _schema(self) -> vol.Schema:
        raise NotImplementedError

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a new source."""
        if user_input is not None:
            name = user_input.pop(CONF_NAME)
            return self.async_create_entry(title=name, data=user_input)
        return self.async_show_form(step_id="user", data_schema=self._schema())

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Edit an existing source."""
        subentry = self._get_reconfigure_subentry()
        if user_input is not None:
            name = user_input.pop(CONF_NAME)
            return self.async_update_and_abort(
                self._get_entry(), subentry, title=name, data=user_input
            )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                self._schema(), {CONF_NAME: subentry.title, **subentry.data}
            ),
        )


class PvSubentryFlow(_BaseSubentryFlow):
    """PV system."""

    def _schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_NAME, default="PV"): str,
                vol.Required(CONF_PRODUCTION_SENSOR): _sensor(SensorDeviceClass.ENERGY),
                vol.Required(CONF_INITIAL_VALUE, default=0): _number("kg"),
                vol.Optional(CONF_START_DATE): selector.DateSelector(),
            }
        )


class VehicleSubentryFlow(_BaseSubentryFlow):
    """Electric vehicle."""

    def _schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_ODOMETER_SENSOR): _sensor(SensorDeviceClass.DISTANCE),
                vol.Optional(CONF_EV_CONSUMPTION_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_EV_CONSUMPTION, default=18.0): _number(
                    "kWh/100 km", max_value=100
                ),
                vol.Required(
                    CONF_CHARGING_LOSS, default=DEFAULT_CHARGING_LOSS
                ): _number("%", max_value=50, step=1),
                vol.Required(CONF_ICE_CONSUMPTION, default=6.0): _number(
                    "l/100 km", max_value=50
                ),
                vol.Required(
                    CONF_FUEL_TYPE, default=FUEL_PETROL
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[FUEL_PETROL, FUEL_DIESEL],
                        translation_key=CONF_FUEL_TYPE,
                    )
                ),
                vol.Required(CONF_INITIAL_VALUE, default=0): _number("kg"),
                vol.Optional(CONF_START_DATE): selector.DateSelector(),
                vol.Required(CONF_INITIAL_FUEL, default=0): _number("l"),
            }
        )


class HeatPumpSubentryFlow(_BaseSubentryFlow):
    """Heat pump replacing an oil boiler."""

    def _schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_NAME, default="Heat pump"): str,
                vol.Required(CONF_HEAT_SENSOR): _sensor(SensorDeviceClass.ENERGY),
                vol.Required(CONF_ELECTRICITY_SENSOR): _sensor(
                    SensorDeviceClass.ENERGY
                ),
                vol.Required(
                    CONF_BOILER_EFFICIENCY, default=DEFAULT_BOILER_EFFICIENCY
                ): _number("%", min_value=10, max_value=110, step=1),
                vol.Required(CONF_INITIAL_VALUE, default=0): _number("kg"),
                vol.Optional(CONF_START_DATE): selector.DateSelector(),
                vol.Required(CONF_INITIAL_OIL, default=0): _number("l"),
            }
        )


class GridSubentryFlow(_BaseSubentryFlow):
    """Grid connection (footprint view)."""

    def _schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_NAME, default="Grid"): str,
                vol.Required(CONF_IMPORT_SENSOR): _sensor(SensorDeviceClass.ENERGY),
                vol.Optional(CONF_EXPORT_SENSOR): _sensor(SensorDeviceClass.ENERGY),
            }
        )
