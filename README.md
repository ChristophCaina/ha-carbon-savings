# Carbon Savings for Home Assistant

Local, cloud-free calculation of the CO₂ your household avoids – from **PV**, **electric vehicles** and a **heat pump** – including the "equivalent planted trees" known from the SolarEdge monitoring portal.

All values are derived from sensors you already have (inverter counters, odometers, heat pump energy meters). No vendor API required.

## Accounting model

Every component is compared with its fossil alternative, and **every electrical consumer is charged the full grid carbon intensity** – no matter whether the kWh actually came from PV, battery or grid. PV in turn is credited the grid intensity for *every* kWh it produces.

| Source | CO₂ saved |
|---|---|
| PV | produced kWh × grid intensity |
| Electric vehicle | km × combustion reference (l/100 km × kg/l) − km × EV consumption × (1 + charging losses) × grid intensity |
| Heat pump | heat kWh ÷ (boiler efficiency × 10 kWh/l) × 2.65 kg/l − heat pump kWh × grid intensity |
| Trees | total CO₂ ÷ kg CO₂ per tree |

The sum is exactly the difference between "no PV, combustion car, oil boiler" and the real household – **without double counting**, and without having to know where a particular kWh came from. Public charging is covered automatically.

**Example:** 10 kWh of PV go into the car, which drives 50 km (grid 0.4 kg/kWh, reference 6.5 l/100 km petrol).
PV: 10 × 0.4 = 4.0 kg · EV: 7.7 kg tailpipe − 4.0 kg electricity = 3.7 kg · **Total 7.7 kg** = exactly the avoided tailpipe emissions.

## Installation

HACS → ⋮ → *Custom repositories* → `https://github.com/ChristophCaina/ha-carbon-savings` (Integration), install, restart Home Assistant.

## Configuration

1. *Settings → Devices & services → Add integration → Carbon Savings*
   - **Grid carbon intensity sensor** (optional), e.g. from the [Electricity Maps](https://www.home-assistant.io/integrations/co2signal/) integration (g CO₂eq/kWh)
   - **Fallback intensity** used when the sensor is missing/unavailable
   - **CO₂ per tree** – calibrate against SolarEdge: *CO₂ saved ÷ trees* from the portal
2. On the integration entry, add sources:
   - **PV system** – lifetime production counter (e.g. Modbus `total_increasing` kWh)
   - **Electric vehicle** – odometer, EV consumption (fixed value and/or an optional sensor with the vehicle's long-term average, e.g. kWh/100km, Wh/km, km/kWh), charging losses, combustion reference, fuel type
   - **Heat pump** – heat energy counter, electrical energy counter, efficiency of the replaced oil boiler
   - **Grid connection** (optional) – import and export counters for a footprint view (see below)

Any kWh counter works as a PV source – a large rooftop system via Modbus as well as a **balcony power plant** measured by a Shelly, a smart plug or the micro-inverter's own integration.

Each source has an **initial value** for savings achieved before tracking started (e.g. the SolarEdge portal value, or historical km × yearly grid mix). It can be changed later without losing the tracked history.

## Sensors

| Device | Sensor |
|---|---|
| Carbon Savings | CO₂ saved total (kg), Trees equivalent |
| each source | CO₂ saved (kg) |
| vehicle | Fuel saved (l) |
| heat pump | Heating oil saved (l) |
| grid connection | CO₂ from grid import, CO₂ credit for export, CO₂ balance electricity (credit − import) |

The grid connection is a separate **footprint view** and is *not* added to "CO₂ saved total": PV already gets credited for every produced kWh, so adding the export credit (or subtracting imports) would count the same kWh twice. A positive balance means the household is net carbon-negative on electricity.

## Notes

- Counters are tracked by deltas. A decreasing value is treated as a counter reset; `unavailable`/`unknown` is ignored. Deltas that happen while Home Assistant is stopped are added on the next start (with the then-current intensity).
- Electricity Maps reports **life-cycle** CO₂eq, which is noticeably higher than direct-emission figures (e.g. UBA). Use the same basis for your initial values to avoid a jump.
- Heat pump savings can temporarily go down (electricity is counted, no heat yet); the CO₂ sensors therefore use `state_class: total`.

## Examples

- [`examples/heat_pump_oil_equivalent.yaml`](examples/heat_pump_oil_equivalent.yaml) – template sensor that converts heat pump heat into the fuel energy the old oil boiler would have burned, to continue an oil/gas statistic in the energy dashboard.

## Icon

The integration ships its own icon in `custom_components/carbon_savings/brand/` (shown by Home Assistant 2026.3 and newer). The source is `assets/icon.svg`; regenerate the PNGs with:

```bash
rsvg-convert -w 256 -h 256 assets/icon.svg -o custom_components/carbon_savings/brand/icon.png
rsvg-convert -w 512 -h 512 assets/icon.svg -o custom_components/carbon_savings/brand/icon@2x.png
```

## Development

```bash
pip install -r requirements_test.txt ruff
pytest
ruff check . && ruff format --check .
```

Translations are generated from `scripts/gen_translations.py`.

## License

[MIT](LICENSE)
