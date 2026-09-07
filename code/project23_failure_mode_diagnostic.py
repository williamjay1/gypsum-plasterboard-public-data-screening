"""Diagnose which registered corner constraints drive quality-screen failure."""
from __future__ import annotations

import csv
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data" / "scenario_assumption_register.csv"
OUT = ROOT / "results" / "failure_mode_diagnostic.csv"
VALID = ROOT / "results" / "failure_mode_diagnostic_validation.csv"
README = ROOT / "results" / "failure_mode_diagnostic_README.txt"

BOARD_SHARE = 0.84
INPUT_MASS = 1000.0

GATES = {
    "EUROGYPSUM_DIAGNOSTIC_PROXY": {"purity_min": 0.80, "moisture_max": 0.10, "organic_proxy_max": 0.02},
    "GERMANY_TECHNICAL_PROXY_COMPARATOR": {"purity_min": 0.85, "moisture_max": 0.05, "organic_proxy_max": 0.01},
}


def load_register():
    grouped = {}
    with REGISTER.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            grouped.setdefault(row["scenario"], {})[row["variable"]] = {
                "lower": float(row["lower"]), "upper": float(row["upper"])
            }
    return grouped


def evaluate(scenario, values, gate):
    board_feed = INPUT_MASS * BOARD_SHARE
    recovered = board_feed * values["recovery_yield"]
    paper = board_feed * values["retained_paper_fraction"]
    coating_wood = board_feed * values["retained_coating_wood_fraction"]
    mineral = board_feed * values["retained_mineral_fraction"]
    dry = recovered + paper + coating_wood + mineral
    purity = recovered / dry if dry else 0.0
    organic = (paper + coating_wood) / dry if dry else 0.0
    moisture = values["free_moisture"]
    visible = int(scenario in {"C2_high_contamination", "C3_hazardous_exclusion"})
    hazard = int(scenario == "C3_hazardous_exclusion")
    failures = []
    if hazard:
        failures.append("hazard_routing")
    if visible:
        failures.append("visible_contaminant")
    if purity < gate["purity_min"]:
        failures.append("purity_proxy")
    if moisture > gate["moisture_max"]:
        failures.append("moisture")
    if organic > gate["organic_proxy_max"]:
        failures.append("organic_proxy")
    return {
        "recovered": recovered, "purity": purity, "organic": organic, "moisture": moisture,
        "failures": failures, "passed": not failures,
    }


def primary_failure(failures):
    if not failures:
        return "pass"
    if "hazard_routing" in failures:
        return "hazard_routing"
    if "visible_contaminant" in failures:
        return "visible_contaminant"
    if len(failures) > 1:
        return "multiple_quality_constraints"
    return failures[0]


def main():
    grouped = load_register()
    rows = []
    validation = []
    for scenario, variables in grouped.items():
        names = list(variables)
        corners = [dict(zip(names, vals)) for vals in itertools.product(*[(variables[n]["lower"], variables[n]["upper"]) for n in names])]
        for gate_name, gate in GATES.items():
            outcomes = [evaluate(scenario, corner, gate) for corner in corners]
            counts = {}
            for outcome in outcomes:
                key = primary_failure(outcome["failures"])
                counts[key] = counts.get(key, 0) + 1
            for mode, count in sorted(counts.items()):
                rows.append({
                    "scenario": scenario,
                    "gate": gate_name,
                    "failure_mode": mode,
                    "n_corners": len(outcomes),
                    "n_corners_in_mode": count,
                    "fraction_of_corners": round(count / len(outcomes), 6),
                    "interpretation": {
                        "pass": "All diagnostic constraints pass at this corner",
                        "hazard_routing": "Hazardous branch is routed out before quality trade-offs",
                        "visible_contaminant": "Visible-contaminant hard gate fails before chemistry",
                        "multiple_quality_constraints": "More than one quality constraint fails",
                        "purity_proxy": "Dry-basis mass purity proxy is below the diagnostic minimum",
                        "moisture": "Free-moisture proxy exceeds the diagnostic maximum",
                        "organic_proxy": "Paper/coating/wood mass proxy exceeds the diagnostic maximum",
                    }[mode],
                })
            validation.append({
                "scenario": scenario,
                "gate": gate_name,
                "corner_count": len(outcomes),
                "mode_count_sum": sum(counts.values()),
                "corner_count_check": "PASS" if len(outcomes) == 32 else "FAIL",
                "mode_partition_check": "PASS" if sum(counts.values()) == len(outcomes) else "FAIL",
                "scope": "Diagnostic decomposition of researcher-specified lower/upper corners; not empirical batch evidence",
            })
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    with VALID.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validation[0])); writer.writeheader(); writer.writerows(validation)
    with README.open("w", encoding="utf-8") as handle:
        handle.write(
            "Failure-mode diagnostic, project 23\n"
            "Each row partitions the 32 lower/upper parameter corners by the first routing failure or the\n"
            "most useful quality diagnosis. This output is a pre-engineering diagnostic: it identifies which\n"
            "measurement or process check should be performed first, but it is not a facility recommendation\n"
            "and does not replace chemical, hazardous-material or product-performance testing.\n"
        )
    if not all(v["corner_count_check"] == "PASS" and v["mode_partition_check"] == "PASS" for v in validation):
        raise SystemExit("Failure-mode validation failed")
    print(f"failure-mode rows: {len(rows)}")


if __name__ == "__main__":
    main()
