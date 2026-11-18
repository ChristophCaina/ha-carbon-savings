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
        "tree": "CO2 per tree (fixed)",
        "tree_d": "kg CO2 that equal one planted tree in fixed mode (e.g. 60 kg = seedling grown for 10 years, US EPA). Also used for sources without a start date.",
        "scope": "Fuel emissions scope",
        "scope_d": "Combustion only: petrol 2.37, diesel 2.65, heating oil 2.65 kg CO2/l. Including upstream chain (extraction, refining, transport): petrol 3.09, diesel 3.29, heating oil 3.10 kg CO2e/l. Match it to your grid intensity source: Electricity Maps is life-cycle based, UBA figures are combustion only.",
        "direct": "Combustion only",
        "lifecycle": "Including upstream chain",
        "tree_mode": "Tree calculation",
        "tree_mode_d": "Fixed: CO2 ÷ kg per tree. Growth curve: how many trees planted when each source went into operation would have absorbed its savings by today.",
        "fixed": "Fixed value per tree",
        "growth": "Growth curve since start date",
        "rate_young": "Uptake in the first year",
        "rate_young_d": "kg CO2 per year of a freshly planted tree (growth curve).",
        "rate_mature": "Uptake when fully grown",
        "rate_mature_d": "kg CO2 per year of a mature tree (growth curve).",
        "years_mature": "Years until fully grown",
        "years_mature_d": "Uptake grows linearly from first-year to mature value over this period.",
        "start": "In operation since",
        "start_d": "Date the source went into operation. Used for the tree growth curve.",
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
        "ev": "EV consumption (fixed)",
        "ev_d": "Average consumption of the electric vehicle. Used when no sensor is selected or it is unavailable.",
        "ev_sensor": "EV consumption sensor (optional)",
        "ev_sensor_d": "Long-term average consumption reported by the vehicle integration (kWh/100km, Wh/km or km/kWh). Values outside 5–60 kWh/100 km are ignored.",
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
        "grid": "Grid connection",
        "grid_add": "Add grid connection",
        "grid_desc": "Footprint view: emissions of grid imports and credit for exports. Not part of the savings total (that would double count PV).",
        "import": "Grid import energy sensor",
        "export": "Grid export energy sensor (optional)",
        "grid_import_co2": "CO2 from grid import",
        "grid_export_co2": "CO2 credit for export",
        "grid_balance_co2": "CO2 balance electricity",
    },
    "de": {
        "hub_title": "Carbon Savings",
        "hub_desc": "Globale Faktoren für alle Quellen. Der Sensor für die Netz-CO2-Intensität (z. B. Electricity Maps) ist optional; der Ersatzwert wird verwendet, wenn er fehlt oder nicht verfügbar ist.",
        "grid_sensor": "Sensor CO2-Intensität Stromnetz",
        "grid_sensor_d": "Sensor in gCO2eq/kWh, z. B. aus der Electricity-Maps-Integration.",
        "grid_fallback": "Ersatzwert CO2-Intensität",
        "grid_fallback_d": "Wird verwendet, wenn kein Sensor gesetzt oder er nicht verfügbar ist.",
        "tree": "CO2 pro Baum (fest)",
        "tree_d": "kg CO2, die im festen Modus einem gepflanzten Baum entsprechen (z. B. 60 kg = Setzling nach 10 Jahren, US EPA). Wird auch für Quellen ohne Startdatum verwendet.",
        "scope": "Bilanzgrenze Brennstoffe",
        "scope_d": "Nur Verbrennung: Benzin 2,37, Diesel 2,65, Heizöl 2,65 kg CO2/l. Mit Vorkette (Förderung, Raffinerie, Transport): Benzin 3,09, Diesel 3,29, Heizöl 3,10 kg CO2e/l. Passend zur Quelle der Netz-Intensität wählen: Electricity Maps rechnet mit Lebenszyklus, UBA-Werte nur mit Verbrennung.",
        "direct": "Nur Verbrennung",
        "lifecycle": "Mit Vorkette",
        "tree_mode": "Berechnung der Bäume",
        "tree_mode_d": "Fest: CO2 ÷ kg pro Baum. Wachstumskurve: Wie viele Bäume, gepflanzt bei Inbetriebnahme der jeweiligen Quelle, hätten deren Einsparung bis heute gebunden.",
        "fixed": "Fester Wert pro Baum",
        "growth": "Wachstumskurve ab Inbetriebnahme",
        "rate_young": "Aufnahme im ersten Jahr",
        "rate_young_d": "kg CO2 pro Jahr eines frisch gepflanzten Baums (Wachstumskurve).",
        "rate_mature": "Aufnahme ausgewachsen",
        "rate_mature_d": "kg CO2 pro Jahr eines ausgewachsenen Baums (Wachstumskurve).",
        "years_mature": "Jahre bis ausgewachsen",
        "years_mature_d": "Die Aufnahme steigt in diesem Zeitraum linear vom Wert im ersten Jahr auf den Endwert.",
        "start": "In Betrieb seit",
        "start_d": "Datum der Inbetriebnahme bzw. Anschaffung. Wird für die Wachstumskurve der Bäume verwendet.",
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
        "ev": "Verbrauch E-Auto (fest)",
        "ev_d": "Durchschnittsverbrauch des Elektrofahrzeugs. Wird verwendet, wenn kein Sensor gewählt oder er nicht verfügbar ist.",
        "ev_sensor": "Sensor Verbrauch E-Auto (optional)",
        "ev_sensor_d": "Langzeit-Durchschnittsverbrauch aus der Fahrzeug-Integration (kWh/100km, Wh/km oder km/kWh). Werte außerhalb 5–60 kWh/100 km werden ignoriert.",
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
        "grid": "Stromnetz",
        "grid_add": "Stromnetz hinzufügen",
        "grid_desc": "Bilanz-Sicht: Emissionen des Netzbezugs und Gutschrift für die Einspeisung. Fließt nicht in die Gesamteinsparung ein (sonst würde PV doppelt gezählt).",
        "import": "Sensor Netzbezug",
        "export": "Sensor Einspeisung (optional)",
        "grid_import_co2": "CO2 aus Netzbezug",
        "grid_export_co2": "CO2-Gutschrift Einspeisung",
        "grid_balance_co2": "CO2-Bilanz Strom",
    },
}


def build(t: dict[str, str]) -> dict:
    hub = {
        "title": t["hub_title"],
        "description": t["hub_desc"],
        "data": {
            "grid_intensity_sensor": t["grid_sensor"],
            "grid_fallback": t["grid_fallback"],
            "fuel_scope": t["scope"],
            "tree_mode": t["tree_mode"],
            "tree_factor": t["tree"],
            "tree_rate_young": t["rate_young"],
            "tree_rate_mature": t["rate_mature"],
            "tree_years_to_mature": t["years_mature"],
        },
        "data_description": {
            "grid_intensity_sensor": t["grid_sensor_d"],
            "grid_fallback": t["grid_fallback_d"],
            "fuel_scope": t["scope_d"],
            "tree_mode": t["tree_mode_d"],
            "tree_factor": t["tree_d"],
            "tree_rate_young": t["rate_young_d"],
            "tree_rate_mature": t["rate_mature_d"],
            "tree_years_to_mature": t["years_mature_d"],
        },
    }

    def sub(kind: str, add: str, desc: str, data: dict, data_d: dict) -> dict:
        step = {
            "title": t[kind],
            "description": t[desc],
            "data": {
                "name": t["name"],
                **data,
                "initial_value": t["initial"],
                "start_date": t["start"],
            },
            "data_description": {
                **data_d,
                "initial_value": t["initial_d"],
                "start_date": t["start_d"],
            },
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
                    "ev_consumption_sensor": t["ev_sensor"],
                    "ev_consumption": t["ev"],
                    "charging_loss": t["loss"],
                    "ice_consumption": t["ice"],
                    "fuel_type": t["fuel"],
                    "initial_fuel": t["initial_fuel"],
                },
                {
                    "ev_consumption_sensor": t["ev_sensor_d"],
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
            "grid": {
                "entry_type": t["grid"],
                "initiate_flow": {
                    "user": t["grid_add"],
                    "reconfigure": f"{t['reconf']}: {t['grid']}",
                },
                "step": {
                    step: {
                        "title": t["grid"],
                        "description": t["grid_desc"],
                        "data": {
                            "name": t["name"],
                            "import_sensor": t["import"],
                            "export_sensor": t["export"],
                        },
                    }
                    for step in ("user", "reconfigure")
                },
                "abort": {"reconfigure_successful": t["reconf_ok"]},
            },
        },
        "selector": {
            "fuel_scope": {
                "options": {"direct": t["direct"], "lifecycle": t["lifecycle"]}
            },
            "tree_mode": {"options": {"fixed": t["fixed"], "growth": t["growth"]}},
            "fuel_type": {"options": {"petrol": t["petrol"], "diesel": t["diesel"]}},
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
                "grid_import_co2": {"name": t["grid_import_co2"]},
                "grid_export_co2": {"name": t["grid_export_co2"]},
                "grid_balance_co2": {"name": t["grid_balance_co2"]},
            }
        },
    }


OUT.mkdir(parents=True, exist_ok=True)
for lang, t in T.items():
    (OUT / f"{lang}.json").write_text(
        json.dumps(build(t), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
print("ok")
