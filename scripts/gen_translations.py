"""Generate translations/en.json and translations/de.json."""

import json
from pathlib import Path

OUT = (
    Path(__file__).parent.parent
    / "custom_components"
    / "carbon_savings"
    / "translations"
)

T = {
    "en": {
        "hub_title": "Carbon Savings",
        "hub_desc": "Global factors used by all sources. The grid intensity sensor (e.g. Electricity Maps) is optional; the fallback is used whenever it is missing or unavailable.",
        "grid_sensor": "Grid carbon intensity sensor",
        "grid_sensor_d": "Sensor in gCO2eq/kWh, e.g. from the Electricity Maps integration.",
        "grid_fallback": "Fallback grid intensity",
        "grid_fallback_d": "Used when no sensor is set or it is unavailable.",
        "tree": "CO2 per tree",
        "tree_d": "kg CO2 that equal one planted tree. Calibrate with your SolarEdge portal: CO2 saved ÷ trees.",
        "single": "Carbon Savings is already configured. Add sources (PV, vehicles, heat pump) to the existing entry.",
        "name": "Name",
        "initial": "CO2 already saved",
        "initial_d": "kg CO2 saved before tracking started (e.g. value from the SolarEdge portal).",
        "pv": "PV system",
        "pv_add": "Add PV system",
        "pv_desc": "Every produced kWh is credited with the grid intensity.",
        "production": "Production energy sensor",
        "production_d": "Lifetime (total increasing) PV production, e.g. the inverter's Modbus energy counter.",
        "vehicle": "Electric vehicle",
        "vehicle_add": "Add electric vehicle",
        "vehicle_desc": "Savings per km = combustion reference − EV electricity × grid intensity. All charging (home and public) is charged at grid intensity, PV gets its credit separately.",
        "odometer": "Odometer sensor",
        "ev": "EV consumption",
        "ev_d": "Average consumption of the electric vehicle.",
        "loss": "Charging losses",
        "loss_d": "Added on top of the consumption.",
        "ice": "Combustion reference consumption",
        "ice_d": "Consumption of a comparable combustion car.",
        "fuel": "Reference fuel",
        "initial_fuel": "Fuel already saved",
        "initial_fuel_d": "Litres saved before tracking started.",
        "hp": "Heat pump",
        "hp_add": "Add heat pump",
        "hp_desc": "Savings = heating oil not burned − heat pump electricity × grid intensity.",
        "heat": "Heat energy sensor",
        "heat_d": "Thermal energy delivered by the heat pump (total increasing).",
        "el": "Electrical energy sensor",
        "el_d": "Electrical energy consumed by the heat pump (total increasing).",
        "eff": "Efficiency of the replaced oil boiler",
        "initial_oil": "Heating oil already saved",
        "reconf_ok": "Reconfiguration was successful",
        "reconf": "Reconfigure",
        "co2_total": "CO2 saved total",
        "trees": "Trees equivalent",
        "co2": "CO2 saved",
        "fuel_saved": "Fuel saved",
        "oil_saved": "Heating oil saved",
        "petrol": "Petrol",
        "diesel": "Diesel",
        "unit_trees": "trees",
    },
    "de": {
        "hub_title": "Carbon Savings",
        "hub_desc": "Globale Faktoren für alle Quellen. Der Sensor für die Netz-CO2-Intensität (z. B. Electricity Maps) ist optional; der Ersatzwert wird verwendet, wenn er fehlt oder nicht verfügbar ist.",
        "grid_sensor": "Sensor CO2-Intensität Stromnetz",
        "grid_sensor_d": "Sensor in gCO2eq/kWh, z. B. aus der Electricity-Maps-Integration.",
        "grid_fallback": "Ersatzwert CO2-Intensität",
        "grid_fallback_d": "Wird verwendet, wenn kein Sensor gesetzt oder er nicht verfügbar ist.",
        "tree": "CO2 pro Baum",
        "tree_d": "kg CO2, die einem gepflanzten Baum entsprechen. Kalibrierung über das SolarEdge-Portal: eingespartes CO2 ÷ Bäume.",
        "single": "Carbon Savings ist bereits eingerichtet. Quellen (PV, Fahrzeuge, Wärmepumpe) werden zum bestehenden Eintrag hinzugefügt.",
        "name": "Name",
        "initial": "Bereits eingespartes CO2",
        "initial_d": "kg CO2, die vor Beginn der Erfassung eingespart wurden (z. B. Wert aus dem SolarEdge-Portal).",
        "pv": "PV-Anlage",
        "pv_add": "PV-Anlage hinzufügen",
        "pv_desc": "Jede erzeugte kWh wird mit der Netz-CO2-Intensität gutgeschrieben.",
        "production": "Sensor PV-Erzeugung",
        "production_d": "Gesamtzähler (total increasing) der PV-Erzeugung, z. B. der Modbus-Energiezähler des Wechselrichters.",
        "vehicle": "Elektrofahrzeug",
        "vehicle_add": "Elektrofahrzeug hinzufügen",
        "vehicle_desc": "Einsparung pro km = Verbrenner-Referenz − EV-Strom × Netz-CO2-Intensität. Jedes Laden (zu Hause und unterwegs) zählt mit Netzintensität, die PV bekommt ihre Gutschrift separat.",
        "odometer": "Sensor Kilometerstand",
        "ev": "Verbrauch E-Auto",
        "ev_d": "Durchschnittsverbrauch des Elektrofahrzeugs.",
        "loss": "Ladeverluste",
        "loss_d": "Werden auf den Verbrauch aufgeschlagen.",
        "ice": "Verbrauch Verbrenner-Referenz",
        "ice_d": "Verbrauch eines vergleichbaren Verbrenners.",
        "fuel": "Kraftstoff der Referenz",
        "initial_fuel": "Bereits eingesparter Kraftstoff",
        "initial_fuel_d": "Liter, die vor Beginn der Erfassung eingespart wurden.",
        "hp": "Wärmepumpe",
        "hp_add": "Wärmepumpe hinzufügen",
        "hp_desc": "Einsparung = nicht verbranntes Heizöl − WP-Strom × Netz-CO2-Intensität.",
        "heat": "Sensor Wärmemenge",
        "heat_d": "Von der Wärmepumpe abgegebene Wärme (total increasing).",
        "el": "Sensor Stromverbrauch",
        "el_d": "Elektrische Energie der Wärmepumpe (total increasing).",
        "eff": "Wirkungsgrad der ersetzten Ölheizung",
        "initial_oil": "Bereits eingespartes Heizöl",
        "reconf_ok": "Die Neukonfiguration war erfolgreich",
        "reconf": "Neu konfigurieren",
        "co2_total": "CO2 eingespart gesamt",
        "trees": "Entspricht gepflanzten Bäumen",
        "co2": "CO2 eingespart",
        "fuel_saved": "Kraftstoff eingespart",
        "oil_saved": "Heizöl eingespart",
        "petrol": "Benzin",
        "diesel": "Diesel",
        "unit_trees": "Bäume",
    },
}


def build(t: dict[str, str]) -> dict:
    hub = {
        "title": t["hub_title"],
        "description": t["hub_desc"],
        "data": {
            "grid_intensity_sensor": t["grid_sensor"],
            "grid_fallback": t["grid_fallback"],
            "tree_factor": t["tree"],
        },
        "data_description": {
            "grid_intensity_sensor": t["grid_sensor_d"],
            "grid_fallback": t["grid_fallback_d"],
            "tree_factor": t["tree_d"],
        },
    }

    def sub(kind: str, add: str, desc: str, data: dict, data_d: dict) -> dict:
        step = {
            "title": t[kind],
            "description": t[desc],
            "data": {"name": t["name"], **data, "initial_value": t["initial"]},
            "data_description": {**data_d, "initial_value": t["initial_d"]},
        }
        return {
            "entry_type": t[kind],
            "initiate_flow": {
                "user": t[add],
                "reconfigure": f"{t['reconf']}: {t[kind]}",
            },
            "step": {"user": step, "reconfigure": step},
            "abort": {"reconfigure_successful": t["reconf_ok"]},
        }

    return {
        "config": {
            "step": {"user": hub},
            "abort": {"already_configured": t["single"]},
        },
        "options": {"step": {"init": hub}},
        "config_subentries": {
            "pv": sub(
                "pv",
                "pv_add",
                "pv_desc",
                {"production_sensor": t["production"]},
                {"production_sensor": t["production_d"]},
            ),
            "vehicle": sub(
                "vehicle",
                "vehicle_add",
                "vehicle_desc",
                {
                    "odometer_sensor": t["odometer"],
                    "ev_consumption": t["ev"],
                    "charging_loss": t["loss"],
                    "ice_consumption": t["ice"],
                    "fuel_type": t["fuel"],
                    "initial_fuel": t["initial_fuel"],
                },
                {
                    "ev_consumption": t["ev_d"],
                    "charging_loss": t["loss_d"],
                    "ice_consumption": t["ice_d"],
                    "initial_fuel": t["initial_fuel_d"],
                },
            ),
            "heat_pump": sub(
                "hp",
                "hp_add",
                "hp_desc",
                {
                    "heat_sensor": t["heat"],
                    "electricity_sensor": t["el"],
                    "boiler_efficiency": t["eff"],
                    "initial_oil": t["initial_oil"],
                },
                {"heat_sensor": t["heat_d"], "electricity_sensor": t["el_d"]},
            ),
        },
        "selector": {
            "fuel_type": {"options": {"petrol": t["petrol"], "diesel": t["diesel"]}}
        },
        "entity": {
            "sensor": {
                "co2_saved_total": {"name": t["co2_total"]},
                "trees_equivalent": {
                    "name": t["trees"],
                    "unit_of_measurement": t["unit_trees"],
                },
                "co2_saved": {"name": t["co2"]},
                "fuel_saved": {"name": t["fuel_saved"]},
                "oil_saved": {"name": t["oil_saved"]},
            }
        },
    }


OUT.mkdir(parents=True, exist_ok=True)
for lang, t in T.items():
    (OUT / f"{lang}.json").write_text(
        json.dumps(build(t), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
print("ok")
