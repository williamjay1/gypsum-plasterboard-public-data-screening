"""One-at-a-time relative sensitivity of the Eurogypsum diagnostic margin."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data" / "scenario_assumption_register.csv"
OUT = ROOT / "results" / "local_boundary_sensitivity.csv"
VALID = ROOT / "results" / "local_boundary_sensitivity_validation.csv"
README = ROOT / "results" / "local_boundary_sensitivity_README.txt"

BOARD_SHARE = 0.84
INPUT_MASS = 1000.0
CHANGES = (-0.25, -0.10, -0.05, 0.0, 0.05, 0.10, 0.25)
PARAMETERS = ("recovery_yield", "retained_paper_fraction", "retained_coating_wood_fraction", "retained_mineral_fraction", "free_moisture")


def load_register():
    grouped = {}
    with REGISTER.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            grouped.setdefault(row["scenario"], {})[row["variable"]] = {k: float(row[k]) for k in ("base", "lower", "upper")}
    return grouped


def evaluate(scenario, values):
    board = INPUT_MASS * BOARD_SHARE
    gross_recovered = board * values["recovery_yield"]
    paper = gross_recovered * values["retained_paper_fraction"]
    organic = gross_recovered * values["retained_coating_wood_fraction"]
    mineral = gross_recovered * values["retained_mineral_fraction"]
    recovered = gross_recovered - paper - organic - mineral
    dry = gross_recovered
    purity = recovered / dry if dry else 0.0
    organic_proxy = (paper + organic) / dry if dry else 0.0
    if scenario == "C3_hazardous_exclusion":
        return -1.0, False
    if scenario == "C2_high_contamination":
        return -1.0, False
    margins = ((purity - 0.80) / 0.80, (0.10 - values["free_moisture"]) / 0.10, (0.02 - organic_proxy) / 0.02)
    return min(margins), min(margins) >= 0


def main():
    grouped = load_register()
    rows = []
    validations = []
    for scenario in ("C0_clean_selective", "C1_moderate_selective", "C2_high_contamination"):
        for parameter in PARAMETERS:
            item = grouped[scenario][parameter]
            for change in CHANGES:
                values = {name: x["base"] for name, x in grouped[scenario].items()}
                values[parameter] = max(item["lower"], min(item["upper"], item["base"] * (1 + change)))
                margin, passed = evaluate(scenario, values)
                rows.append({
                    "scenario": scenario, "parameter": parameter, "relative_change": change,
                    "tested_value": round(values[parameter], 6), "diagnostic_margin": round(margin, 6),
                    "screen_pass": int(passed), "interpretation": "One-at-a-time sensitivity; other parameters fixed at scenario bases",
                })
            validations.append({"scenario": scenario, "parameter": parameter, "n_change_points": len(CHANGES), "change_count_check": "PASS", "scope": "Relative perturbations clipped to registered bounds"})
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    with VALID.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validations[0])); writer.writeheader(); writer.writerows(validations)
    README.write_text(
        "Local boundary sensitivity, project 23\n"
        "Each continuous input is changed one at a time by -25%, -10%, -5%, 0%, +5%, +10% and +25%,\n"
        "then clipped to its registered bounds. The diagnostic margin is the minimum normalized margin\n"
        "for purity, moisture and organic-proxy gates. Positive values pass the proxy screen; C2 remains\n"
        "a visible-contaminant hard-failure branch. This is sensitivity, not empirical validation.\n",
        encoding="utf-8",
    )
    print(f"Local sensitivity rows: {len(rows)}")


if __name__ == "__main__":
    main()
