from __future__ import annotations

import csv
import itertools
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data" / "scenario_assumption_register.csv"
OUT = ROOT / "results" / "robust_quality_gate_sensitivity.csv"
VALID = ROOT / "results" / "robust_quality_gate_sensitivity_validation.csv"
README = ROOT / "results" / "robust_quality_gate_sensitivity_README.txt"

BOARD_SHARE = 0.84
INPUT_MASS = 1000.0

GATES = {
    "EUROGYPSUM_DIAGNOSTIC_PROXY": {
        "purity_min": 0.80,
        "moisture_max": 0.10,
        "organic_proxy_max": 0.02,
        "source_note": "Eurogypsum 2024 voluntary screening values; proxies are not chemistry",
    },
    "GERMANY_TECHNICAL_PROXY_COMPARATOR": {
        "purity_min": 0.85,
        "moisture_max": 0.05,
        "organic_proxy_max": 0.01,
        "source_note": "German RC-gypsum technical comparator; CaSO4 and TOC values mapped only as diagnostic proxies",
    },
}


def load_register():
    grouped = {}
    with REGISTER.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            grouped.setdefault(row["scenario"], {})[row["variable"]] = {
                "lower": float(row["lower"]),
                "upper": float(row["upper"]),
            }
    return grouped


def evaluate(scenario, values, gate):
    board_feed = INPUT_MASS * BOARD_SHARE
    gross_recovered = board_feed * values["recovery_yield"]
    paper = gross_recovered * values["retained_paper_fraction"]
    coating_wood = gross_recovered * values["retained_coating_wood_fraction"]
    mineral = gross_recovered * values["retained_mineral_fraction"]
    recovered = gross_recovered - paper - coating_wood - mineral
    dry = gross_recovered
    purity = recovered / dry if dry else 0.0
    organic = (paper + coating_wood) / dry if dry else 0.0
    moisture = values["free_moisture"]
    visible = int(scenario == "C2_high_contamination" or scenario == "C3_hazardous_exclusion")
    hazard = int(scenario == "C3_hazardous_exclusion")
    passed = (
        hazard == 0
        and visible == 0
        and purity >= gate["purity_min"]
        and moisture <= gate["moisture_max"]
        and organic <= gate["organic_proxy_max"]
    )
    return {
        "recovered": recovered,
        "purity": purity,
        "organic": organic,
        "moisture": moisture,
        "passed": passed,
    }


def main():
    grouped = load_register()
    rows = []
    validation = []
    for scenario, variables in grouped.items():
        names = list(variables)
        corners = [dict(zip(names, vals)) for vals in itertools.product(*[(variables[n]["lower"], variables[n]["upper"]) for n in names])]
        for gate_name, gate in GATES.items():
            outcomes = [evaluate(scenario, corner, gate) for corner in corners]
            n_pass = sum(int(o["passed"]) for o in outcomes)
            if n_pass == len(outcomes):
                robust_status = "ALL_CORNERS_PASS"
            elif n_pass == 0:
                robust_status = "NO_CORNERS_PASS"
            else:
                robust_status = "BOUNDARY_INDETERMINATE"
            rows.append({
                "scenario": scenario,
                "gate": gate_name,
                "n_parameter_corners": len(outcomes),
                "n_pass": n_pass,
                "pass_fraction": round(n_pass / len(outcomes), 6),
                "min_recovered_gypsum_equivalent_kg": round(min(o["recovered"] for o in outcomes), 6),
                "max_recovered_gypsum_equivalent_kg": round(max(o["recovered"] for o in outcomes), 6),
                "min_purity_proxy": round(min(o["purity"] for o in outcomes), 6),
                "max_purity_proxy": round(max(o["purity"] for o in outcomes), 6),
                "min_organic_proxy": round(min(o["organic"] for o in outcomes), 6),
                "max_organic_proxy": round(max(o["organic"] for o in outcomes), 6),
                "min_moisture": round(min(o["moisture"] for o in outcomes), 6),
                "max_moisture": round(max(o["moisture"] for o in outcomes), 6),
                "robust_status": robust_status,
                "gate_source_note": gate["source_note"],
            })
            validation.append({
                "scenario": scenario,
                "gate": gate_name,
                "corner_count_check": "PASS" if len(outcomes) == 32 else "FAIL",
                "pass_count_range_check": "PASS" if 0 <= n_pass <= len(outcomes) else "FAIL",
                "proxy_range_check": "PASS" if all(0 <= o["purity"] <= 1 and 0 <= o["organic"] <= 1 for o in outcomes) else "FAIL",
                "scope": "Corner enumeration of researcher-specified scenario bounds; not empirical batch validation",
            })
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with VALID.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validation[0]))
        writer.writeheader()
        writer.writerows(validation)
    with README.open("w", encoding="utf-8") as handle:
        handle.write(
            "All-corners boundary sensitivity, project 23\n"
            "The script enumerates all 2^5 lower/upper parameter corners in the scenario assumption register.\n"
            "The two gates are engineering diagnostics: Eurogypsum 2024 voluntary values and a German technical comparator.\n"
            "Purity and organic values are transparent mass proxies, not CaSO4 or TOC measurements.\n"
            "ALL_CORNERS_PASS means every enumerated corner passes; NO_CORNERS_PASS means none passes; BOUNDARY_INDETERMINATE means the\n"
            "decision changes within the stated bounds. Hazardous and visible-contaminant flags are hard routing gates.\n"
            "This is a parametric boundary-sensitivity result, not a European batch prevalence estimate or legal acceptance rule.\n"
        )
    if not all(v["corner_count_check"] == "PASS" and v["pass_count_range_check"] == "PASS" and v["proxy_range_check"] == "PASS" for v in validation):
        raise SystemExit("Robust gate validation failed")
    print(f"robust gate rows: {len(rows)}")


if __name__ == "__main__":
    main()
