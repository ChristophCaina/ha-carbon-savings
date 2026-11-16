"""Accumulating trackers that turn counter deltas into CO2 savings."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfEnergy,
    UnitOfLength,
)
from homeassistant.core import (
    Event,
    EventStateChangedData,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.storage import Store
from homeassistant.util.unit_conversion import DistanceConverter, EnergyConverter

from .const import DOMAIN, SIGNAL_SAVINGS_UPDATED

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
SAVE_DELAY = 30

KIND_ENERGY = "energy"
KIND_DISTANCE = "distance"

# Delta handler: canonical delta (kWh or km) -> (kg CO2, secondary quantity)
DeltaHandler = Callable[[float], tuple[float, float]]


@dataclass(slots=True)
class TrackedSource:
    """A monotonically increasing counter that feeds a tracker."""

    key: str
    entity_id: str
    kind: str
    handler: DeltaHandler


def _to_canonical(state: State, kind: str) -> float | None:
    """Return the state value in kWh (energy) or km (distance)."""
    if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN, "", None):
        return None
    try:
        value = float(state.state)
    except (TypeError, ValueError):
        return None
    unit = state.attributes.get("unit_of_measurement")
    try:
        if kind == KIND_ENERGY:
            if unit and unit != UnitOfEnergy.KILO_WATT_HOUR:
                return EnergyConverter.convert(value, unit, UnitOfEnergy.KILO_WATT_HOUR)
        elif kind == KIND_DISTANCE:
            if unit and unit != UnitOfLength.KILOMETERS:
                return DistanceConverter.convert(value, unit, UnitOfLength.KILOMETERS)
    except Exception:  # noqa: BLE001 - unknown unit
        _LOGGER.warning(
            "Unsupported unit '%s' on %s, assuming %s",
            unit,
            state.entity_id,
            "kWh" if kind == KIND_ENERGY else "km",
        )
    return value


class SavingsTracker:
    """Accumulates CO2 (and a secondary quantity) from counter deltas.

    Persisted values exclude the configured initial values, so changing an
    initial value later simply shifts the total without losing history.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        tracker_id: str,
        sources: list[TrackedSource],
        initial_co2: float = 0.0,
        initial_secondary: float = 0.0,
        include_in_total: bool = True,
    ) -> None:
        """Initialize the tracker."""
        self.hass = hass
        self.tracker_id = tracker_id
        self.sources = {source.key: source for source in sources}
        self.initial_co2 = initial_co2
        self.initial_secondary = initial_secondary
        self.include_in_total = include_in_total
        self.accumulated_co2 = 0.0
        self.accumulated_secondary = 0.0
        self.last_values: dict[str, float] = {}
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.{tracker_id}"
        )
        self._unsub: Callable[[], None] | None = None

    @property
    def signal(self) -> str:
        """Dispatcher signal fired after each update."""
        return SIGNAL_SAVINGS_UPDATED.format(self.tracker_id)

    @property
    def co2_total(self) -> float:
        """Total CO2 saved in kg including the initial value."""
        return self.initial_co2 + self.accumulated_co2

    @property
    def secondary_total(self) -> float:
        """Total secondary quantity (e.g. litres) including the initial value."""
        return self.initial_secondary + self.accumulated_secondary

    async def async_load(self) -> None:
        """Load persisted data (call before entities are created)."""
        if data := await self._store.async_load():
            self.accumulated_co2 = float(data.get("co2", 0.0))
            self.accumulated_secondary = float(data.get("secondary", 0.0))
            self.last_values = {
                key: float(value)
                for key, value in data.get("last_values", {}).items()
                if key in self.sources
            }

    async def async_start(self) -> None:
        """Catch up on deltas missed while stopped and start listening."""
        for source in self.sources.values():
            if (state := self.hass.states.get(source.entity_id)) is not None:
                self._process(source, state)

        self._unsub = async_track_state_change_event(
            self.hass,
            [source.entity_id for source in self.sources.values()],
            self._handle_event,
        )
        async_dispatcher_send(self.hass, self.signal)

    async def async_stop(self) -> None:
        """Stop listening and persist immediately."""
        if self._unsub:
            self._unsub()
            self._unsub = None
        await self._store.async_save(self._data())

    async def async_remove(self) -> None:
        """Delete persisted data (subentry removed)."""
        await self._store.async_remove()

    def _data(self) -> dict[str, Any]:
        return {
            "co2": self.accumulated_co2,
            "secondary": self.accumulated_secondary,
            "last_values": self.last_values,
        }

    @callback
    def _handle_event(self, event: Event[EventStateChangedData]) -> None:
        new_state = event.data["new_state"]
        if new_state is None:
            return
        for source in self.sources.values():
            if source.entity_id == new_state.entity_id:
                self._process(source, new_state)

    @callback
    def _process(self, source: TrackedSource, state: State) -> None:
        value = _to_canonical(state, source.kind)
        if value is None:
            return

        last = self.last_values.get(source.key)
        self.last_values[source.key] = value

        if last is None:
            _LOGGER.debug(
                "%s: baseline for %s = %s", self.tracker_id, source.key, value
            )
        elif value < last:
            _LOGGER.info(
                "%s: counter %s decreased (%s -> %s), treating as reset",
                self.tracker_id,
                source.entity_id,
                last,
                value,
            )
        elif value > last:
            co2, secondary = source.handler(value - last)
            self.accumulated_co2 += co2
            self.accumulated_secondary += secondary
            async_dispatcher_send(self.hass, self.signal)

        self._store.async_delay_save(self._data, SAVE_DELAY)
