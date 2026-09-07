"""Reproducible public-data sensitivity table for project 23.

The table combines researcher-specified quality scenarios, the published
Pedreno-Rojas foreground electricity inventory, dated JRC country electricity
life-cycle factors, and the JRC gypsum allowable-burden benchmark. It is a
partial climate screen, not a full LCA.
"""
from pathlib import Path
import pandas as pd

WORK = Path(__file__).resolve().parents[1]
scenario = pd.read_csv(WORK / "results" / "public_threshold_screening.csv")
ef = pd.read_csv(WORK / "data" / "jrc_electricity_emission_factors_2024.csv")
benchmark = pd.read_csv(WORK / "results" / "jrc_gypsum_climate_benchmark.csv").iloc[0]

elec_kwh_per_t_product = 60.35
rows = []
for _, s in scenario.iterrows():
    recovered_t_per_input = float(s["recovered_gypsum_equivalent_kg"]) / 1000.0
    allowable_low = recovered_t_per_input * float(benchmark["published_saving_lower_kgco2e_per_t"])
    allowable_point = recovered_t_per_input * float(benchmark["published_saving_point_kgco2e_per_t"])
    allowable_high = recovered_t_per_input * float(benchmark["published_saving_upper_kgco2e_per_t"])
    for _, f in ef[ef["year"] == 2021].iterrows():
        factor_t_per_mwh = float(f["factor_tco2e_per_mwh"])
        electricity_component = elec_kwh_per_t_product / 1000.0 * factor_t_per_mwh * 1000.0 * recovered_t_per_input
        rows.append({
            "scenario": s["scenario"],
            "country_scope": "EU27",
            "geo": f["iso2"],
            "year": int(f["year"]),
            "recovered_gypsum_t_per_t_input": recovered_t_per_input,
            "jrc_electricity_factor_tco2e_per_mwh": factor_t_per_mwh,
            "pedreno_electricity_inventory_kwh_per_t_product": elec_kwh_per_t_product,
            "electricity_climate_component_kgco2e_per_t_input": electricity_component,
            "allowable_additional_burden_low_kgco2e_per_t_input": allowable_low,
            "allowable_additional_burden_point_kgco2e_per_t_input": allowable_point,
            "allowable_additional_burden_high_kgco2e_per_t_input": allowable_high,
            "partial_point_headroom_after_electricity_kgco2e_per_t_input": allowable_point - electricity_component,
            "interpretation": "Electricity component only; excludes thermal energy, diesel, transport, rejects, end-of-life and substitution uncertainty",
        })

out = pd.DataFrame(rows)
out.to_csv(WORK / "results" / "public_boundary_climate_sensitivity.csv", index=False)

qa = pd.DataFrame([
    {"check": "scenario_count", "value": scenario["scenario"].nunique(), "expected": 4, "pass": scenario["scenario"].nunique() == 4},
    {"check": "eu27_factor_count_2021", "value": int((ef["year"] == 2021).sum()), "expected": 27, "pass": int((ef["year"] == 2021).sum()) == 27},
    {"check": "rows", "value": len(out), "expected": 108, "pass": len(out) == 108},
    {"check": "c3_hazardous_has_zero_recovered_output", "value": float(scenario.loc[scenario["scenario"] == "C3_hazardous_exclusion", "recovered_gypsum_equivalent_kg"].iloc[0]), "expected": 0, "pass": float(scenario.loc[scenario["scenario"] == "C3_hazardous_exclusion", "recovered_gypsum_equivalent_kg"].iloc[0]) == 0},
])
qa.to_csv(WORK / "results" / "public_boundary_climate_sensitivity_validation.csv", index=False)
(WORK / "results" / "public_boundary_climate_sensitivity_README.txt").write_text(
    "This file is a partial climate sensitivity table, not a complete LCA.\n"
    "For each scenario and EU27 country, it scales the published JRC gypsum climate-saving benchmark to the scenario recovered gypsum equivalent and subtracts only the published Pedreno-Rojas electricity inventory multiplied by the dated 2021 JRC country factor.\n"
    "Thermal energy, diesel, transport, reject treatment, acid or water treatment, allocation, substitution, market acceptance and the remaining life-cycle inventory are not included.\n"
    "C0-C3 are transparent researcher-defined scenario bundles, not observed EU27 contamination frequencies.\n",
    encoding="utf-8",
)
if not qa["pass"].all():
    raise ValueError("Climate sensitivity QA failed")
print(f"Rows: {len(out)}; QA passed: {qa['pass'].all()}")
