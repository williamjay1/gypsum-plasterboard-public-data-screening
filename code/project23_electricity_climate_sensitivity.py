from pathlib import Path
import pandas as pd

WORK = Path(__file__).resolve().parents[1]
factors = pd.read_csv(WORK / "data" / "jrc_electricity_emission_factors_2024.csv")
factors = factors[factors["year"] == 2021].copy()

# Pedreno-Rojas et al. (2020), Table 2: Spanish plant inventory for 1 t
# manufactured gypsum, plasterboard-waste route. This is an external process
# benchmark, not an EU-27 post-consumer average.
electricity_kwh_per_t_product = 60.35
factors["pedreno_electricity_kwh_per_t_product"] = electricity_kwh_per_t_product
factors["electricity_gwp_kgco2e_per_t_product"] = (
    factors["factor_kgco2e_per_kwh"] * electricity_kwh_per_t_product
)
factors["jrc_saving_lower_kgco2e_per_t_gypsum_fraction"] = 66.0
factors["jrc_saving_point_kgco2e_per_t_gypsum_fraction"] = 85.0
factors["jrc_saving_upper_kgco2e_per_t_gypsum_fraction"] = 104.0
factors["screening_note"] = (
    "Electricity component only; comparison with JRC/Caro saving benchmark is not a full LCA verdict"
)

out_cols = [
    "iso2", "country", "year", "factor_scope", "factor_kgco2e_per_kwh",
    "pedreno_electricity_kwh_per_t_product", "electricity_gwp_kgco2e_per_t_product",
    "jrc_saving_lower_kgco2e_per_t_gypsum_fraction",
    "jrc_saving_point_kgco2e_per_t_gypsum_fraction",
    "jrc_saving_upper_kgco2e_per_t_gypsum_fraction", "screening_note",
]
out = factors[out_cols].sort_values("electricity_gwp_kgco2e_per_t_product")
out.to_csv(WORK / "results" / "electricity_gwp_component_2021.csv", index=False)

qa = pd.DataFrame([
    {"check": "EU27 country count", "value": int(out["iso2"].nunique()), "expected": 27, "pass": int(out["iso2"].nunique()) == 27},
    {"check": "one year", "value": int(out["year"].nunique()), "expected": 1, "pass": int(out["year"].nunique()) == 1},
    {"check": "nonnegative electricity component", "value": float(out["electricity_gwp_kgco2e_per_t_product"].min()), "expected": ">=0", "pass": bool((out["electricity_gwp_kgco2e_per_t_product"] >= 0).all())},
    {"check": "energy inventory fixed", "value": electricity_kwh_per_t_product, "expected": 60.35, "pass": electricity_kwh_per_t_product == 60.35},
])
qa.to_csv(WORK / "results" / "electricity_gwp_component_2021_validation.csv", index=False)

summary = out["electricity_gwp_kgco2e_per_t_product"].describe()
(WORK / "results" / "electricity_gwp_component_2021_README.txt").write_text(
    "Purpose: country electricity climate-component sensitivity for an open Spanish gypsum recycling inventory.\n"
    "Source factor: JRC CoM Table3_EU_LC, annual national life-cycle GHG factors through 2021.\n"
    "Process inventory: Pedreno-Rojas et al. (2020), Table 2, 60.35 kWh/t manufactured gypsum.\n"
    "Interpretation restriction: this is one process component and does not include gas, diesel, transport,\n"
    "drying allocation, avoided virgin gypsum, landfill credits/burdens, product quality, or market substitution.\n"
    "The JRC/Caro 66–104 kg CO2-eq/t gypsum-fraction saving range is an external published benchmark,\n"
    "not an allowable threshold or result of this study.\n"
    f"Summary of electricity component (kg CO2-eq/t product):\n{summary.to_string()}\n",
    encoding="utf-8",
)
print(out.to_string(index=False))
print("\nQA")
print(qa.to_string(index=False))
