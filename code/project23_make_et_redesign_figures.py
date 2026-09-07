"""Create figures for the redesigned Environmental Technology manuscript."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG = RESULTS / "figures"
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "figure.dpi": 150,
        "savefig.dpi": 900,
    }
)


def save(fig, name: str) -> None:
    fig.savefig(FIG / name, dpi=900, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# Figure 1: explicit process denominator and two non-equivalent mass-balance variants.
s = pd.read_csv(RESULTS / "et_redesign_scenario_outputs.csv")
variants = pd.read_csv(RESULTS / "process_mass_balance_variants.csv")
fig, axes = plt.subplots(1, 2, figsize=(7.3, 3.5), gridspec_kw={"width_ratios": [1.15, 1]})
x = np.arange(len(s))
bottom = np.zeros(len(s))
parts = [
    ("gypsum_equivalent_kg", "Gypsum equivalent", "#2a9d8f"),
    ("retained_paper_kg", "Paper", "#e9c46a"),
    ("retained_coating_wood_kg", "Coating/wood", "#f4a261"),
    ("retained_mineral_kg", "Mineral", "#e76f51"),
    ("unrecovered_board_loss_kg", "Board loss", "#8d99ae"),
]
for col, label, color in parts:
    axes[0].bar(x, s[col], bottom=bottom, label=label, color=color, edgecolor="white", linewidth=.25)
    bottom += s[col].to_numpy()
axes[0].axhline(840, color="#173042", linestyle="--", linewidth=.8, label="Board reference = 840 kg")
axes[0].set_xticks(x, ["C0", "C1", "C2", "C3"])
axes[0].set_ylim(0, 1050)
axes[0].set_ylabel("Mass on normalized reference flow (kg)")
axes[0].set_title("A  Primary model: b = 0.84 board share")
axes[0].text(.02, -.18, "Used for all interval outputs", transform=axes[0].transAxes, fontsize=7.2)
axes[0].legend(frameon=False, fontsize=6.5, loc="upper right")

labels = ["b = 0.84\n× yield", "Weimann\nrange", "C0 gypsum\nequivalent"]
lo = variants["lower_output_t_per_reference_input"].to_numpy() * 1000
hi = variants["upper_output_t_per_reference_input"].to_numpy() * 1000
xx = np.arange(len(labels))
axes[1].bar(xx, hi, color=["#457b9d", "#a8dadc", "#2a9d8f"], alpha=.85, edgecolor="black", linewidth=.4)
axes[1].vlines(xx, lo, hi, color="#173042", linewidth=2)
for i, (l, h) in enumerate(zip(lo, hi)):
    axes[1].text(i, h + 18, f"{l:.0f}–{h:.0f}", ha="center", fontsize=7)
axes[1].set_xticks(xx, labels)
axes[1].set_ylim(0, 980)
axes[1].set_ylabel("Output range (kg per 1,000 kg reference)")
axes[1].set_title("B  External Weimann range (not combined with b)")
fig.tight_layout(w_pad=1.2)
save(fig, "fig1_process_mass_balance.png")


# Figure 2: required information burden, not empirical testing performance.
p = pd.read_csv(RESULTS / "screening_policy_comparison.csv")
order = ["C0_clean_selective", "C1_moderate_selective", "C2_high_contamination", "C3_hazardous_exclusion"]
short = {v: v[:2] for v in order}
policies = ["sequential_safe_first", "all_confirmatory_panel_after_safety_gate"]
fig, ax = plt.subplots(figsize=(6.7, 3.5))
xx = np.arange(len(order))
width = .34
for j, policy in enumerate(policies):
    vals = [int(p[(p.scenario == scenario) & (p.policy == policy)]["confirmatory_field_count"].iloc[0]) for scenario in order]
    bars = ax.bar(xx + (j - .5) * width, vals, width, label=("Sequential safety first" if j == 0 else "All confirmatory after safety"), color=("#2a9d8f", "#a8dadc")[j], edgecolor="black", linewidth=.4)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + .12, str(v), ha="center", fontsize=8)
ax.set_xticks(xx, ["C0", "C1", "C2", "C3"])
ax.set_ylabel("Required confirmatory fields (scenario rule)")
ax.set_ylim(0, 6.2)
ax.set_title("Five-field chemistry panel after the safety gate")
ax.text(.02, -.28, "C0 to C2 receive the panel; C3 stops at hazard screening.", transform=ax.transAxes, fontsize=7.5)
ax.legend(frameon=False, fontsize=7, loc="upper left")
fig.tight_layout()
save(fig, "fig2_screening_policy_burden.png")


# Figure 3: measurement hierarchy and non-equivalence of proxy and chemistry.
fig, ax = plt.subplots(figsize=(7.2, 3.7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")

def box(x, y, w, h, text, fc, ec="#173042", fs=8, weight="normal"):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08", facecolor=fc, edgecolor=ec, linewidth=.9)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, fontweight=weight, wrap=True)

box(.25, 4.25, 2.2, 1.0, "Hazard screen\nconfirmed hazard\nroute out", "#f8d7da", fs=7.5, weight="bold")
box(.25, 2.65, 2.2, 1.0, "Visible\nnonhazardous\ncontaminant →\npretreatment", "#fff3cd", fs=7.3)
box(.25, 1.05, 2.2, 1.0, "Mass screen\npaper / wood /\nmineral / moisture", "#d9edf2", fs=7.6)
box(4.0, 4.25, 2.25, 1.0, "Safety exclusion\nother route", "#f8d7da", fs=8, weight="bold")
box(4.0, 2.65, 2.25, 1.0, "Targeted processing\nrecheck feed\nand product", "#e8f5e9", fs=7.6, weight="bold")
box(7.75, 3.55, 2.0, 1.0, "Chemical\nacceptance\nCaSO₄; TOC;\nsalts; pH", "#cde8f6", fs=7.1, weight="bold")
box(7.75, 1.55, 2.0, 1.0, "Decision\nqualified / retest\nother route", "#e2e3e5", fs=7.5)
for start, end in [((2.45, 4.75), (4.0, 4.75)), ((2.45, 3.15), (4.0, 3.15)), ((2.45, 1.55), (4.0, 3.05)), ((6.25, 3.15), (7.75, 4.05)), ((8.75, 3.55), (8.75, 2.55))]:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11, linewidth=.9, color="#173042"))
ax.text(5.1, 5.45, "Measurement hierarchy turns feed information into an actionable route", ha="center", fontsize=9, fontweight="bold", color="#173042")
ax.text(5.1, .35, "Mass fractions are triage proxies. Chemical acceptance variables are measured on the product basis required by the selected specification.", ha="center", fontsize=7.4, color="#444")
save(fig, "fig3_quality_measurement_hierarchy.png")


# Figure 4: direct energy inventory plus the electricity component, without a net-credit subtraction.
energy = pd.read_csv(RESULTS / "direct_energy_inventory.csv")
elec = pd.read_csv(RESULTS / "direct_electricity_component_redesign.csv")
representative = ["Sweden", "France", "Germany", "Spain", "Poland", "Cyprus"]
country = elec[(elec["scenario"] == "C0_clean_selective") & elec["country"].isin(representative)].copy()
country["country"] = pd.Categorical(country["country"], categories=representative, ordered=True)
country = country.sort_values("country")
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), gridspec_kw={"width_ratios": [1, 1.25]})
axes[0].barh(energy["component"], energy["intensity"], color=["#457b9d", "#e9c46a", "#f4a261"], edgecolor="black", linewidth=.4)
for i, (_, row) in enumerate(energy.iterrows()):
    axes[0].text(row["intensity"] + max(energy["intensity"]) * .025, i, f"{row['intensity']:.2f} {row['unit'].split(' ')[0]}", va="center", fontsize=7)
axes[0].set_xlabel("Published process intensity (per t product)")
axes[0].set_title("A  Direct inventory")
axes[0].grid(axis="x", alpha=.2)
axes[1].bar(country["country"], country["electricity_component_kgco2e_per_t_product"], color="#2a9d8f", edgecolor="black", linewidth=.4)
axes[1].set_ylabel("kg CO₂-eq per t product")
axes[1].set_title("B  Electricity component only (2021 factor)")
axes[1].tick_params(axis="x", rotation=35)
axes[1].grid(axis="y", alpha=.2)
fig.text(.5, -.02, "No JRC avoided-credit subtraction; this is not a complete climate comparison.", ha="center", fontsize=7.5)
fig.tight_layout()
save(fig, "fig5_direct_energy_components.png")


# Figure 5: selected UK public observations shown as an external anchor, not validation.
q = pd.read_csv(ROOT / "data" / "castro_uk_acid_leaching_quality_response.csv")
q = q.dropna(subset=["si_al_fe_proxy_wt_pct", "chemical_purity_wt_pct"]).copy()
fig, ax = plt.subplots(figsize=(6.4, 3.6))
for sample, g in q.groupby("sample"):
    ax.scatter(g["si_al_fe_proxy_wt_pct"], g["chemical_purity_wt_pct"], s=22, alpha=.78, label=sample)
ax.axvspan(4, 6, color="#e9c46a", alpha=.22, label="Reported post-sieving contamination scale")
ax.axhline(96, color="#173042", linestyle="--", linewidth=.8, label="Illustrative C1 mass proxy = 96% (not chemical purity)")
ax.set_xlabel("Public dataset inorganic impurity proxy (wt%)")
ax.set_ylabel("Reported chemical purity (wt%)")
ax.set_title("Selected UK observations: chemistry anchor for panel design")
ax.legend(frameon=False, fontsize=6.4, loc="lower right")
ax.text(.02, -.27, "Selected UK batches inform panel design; they do not calibrate the mass proxy.", transform=ax.transAxes, fontsize=7.5)
fig.tight_layout()
save(fig, "fig4_public_anchor_evidence.png")


print("WROTE REDESIGN FIGURES")
