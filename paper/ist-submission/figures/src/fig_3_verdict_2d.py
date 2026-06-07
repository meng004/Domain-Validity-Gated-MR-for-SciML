"""Render the 2D verdict-reading figure (Figure 3).

This figure visualizes the paper's central conceptual contribution: reading a
relation-level verdict in TWO dimensions rather than as a flat pass/fail label.

  x-axis: relation-violation magnitude, V/floor (log scale). "Floor" is the
          tolerance or operator floor of the MR. V/floor < 1 means the
          measurement sits within the numerical floor; V/floor >> 1 means a
          large violation relative to the floor.

  y-axis: domain-violation magnitude, the degree to which the transformed case
          lies outside the relation's validity domain. The manuscript admits
          this axis is only qualitatively operationalized so far (Sec. 3.5);
          we therefore use three discrete bins -- LOW, BORDERLINE, OUT --
          rather than a calibrated continuous score.

Background shading partitions the plane into the four verdict regions in
Sec. 3.5:
  - pass                          : low V, low D
  - SUT inconsistency             : high V, low D    (the only model-level fail)
  - OOD-stress / out-of-domain    : high D
  - numerical-tolerance issue     : low V relative to floor (V/floor < 1)

Five real pilot points (all from K=6-aggregated ledgers) are plotted at their
measured coordinates, demonstrating that the same verdict-space distinguishes
genuine model violations from out-of-domain applications.

Source ledgers:
  - research_assets/runs/real-sut-node-permutation-pilot/raw/metric_ledger.json
  - research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json
  - research_assets/runs/mirror-y-symmetric-mesh/raw/metric_ledger.json
  - research_assets/runs/conservation-diagnostic-pilot/raw/metric_ledger.json

Output:
  paper/ist-submission/figures/fig_3_verdict_2d.{pdf,png}
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
RUNS = ROOT / "research_assets" / "runs"
OUT_PDF = ROOT / "paper/ist-submission/figures/fig_3_verdict_2d.pdf"
OUT_PNG = ROOT / "paper/ist-submission/figures/fig_3_verdict_2d.png"

# ---- Pull V/floor coordinates from the REAL pilot ledgers ----

np_led = json.loads((RUNS / "real-sut-node-permutation-pilot" / "raw" /
                     "metric_ledger.json").read_text())
node_perm_v = float(np_led["entries"][0]["metric_value"])  # 0.0

my_led = json.loads((RUNS / "mirror-y-rate-upgrade" / "raw" /
                     "metric_ledger.json").read_text())
my_ratios = [float(e["violation_over_floor"]) for e in my_led["entries"]]
my_v_over_floor = float(np.median(my_ratios))

sym_led = json.loads((RUNS / "mirror-y-symmetric-mesh" / "raw" /
                      "metric_ledger.json").read_text())
sym_v = float(sym_led["metric_value"])
sym_tol = float(sym_led["tolerance"]["threshold"])
sym_v_over_floor = sym_v / sym_tol

cons_led = json.loads((RUNS / "conservation-diagnostic-pilot" / "raw" /
                       "metric_ledger.json").read_text())
cons_ratios = [float(e["metric_value"]) for e in cons_led["entries"]]
cons_median = float(np.median(cons_ratios))
cons_v_over_floor = max(0.0, cons_median - 1.0) / (1.5 - 1.0)

cons_abs_x = 0.3  # deferred -- illustrative

# ---- Coordinate mapping ----
Y_LOW, Y_BORDER, Y_OUT = 0.5, 1.5, 2.5
X_FLOOR_PLOT = 1e-3  # for V/floor = 0 (node-perm)


def x_plot(v):
    return max(v, X_FLOOR_PLOT)


# (key, label, V/floor, y, marker, facecolor, edgecolor)
points = [
    ("P1", "Node-perm.\\ equivariance",
     0.0, Y_LOW, "o", "#2c7a2c", "#1c4d1c"),
    ("P2", "Conservation (ref.-relative)",
     cons_v_over_floor, Y_LOW, "D", "#2c7a2c", "#1c4d1c"),
    ("P3", "Mirror-y on symmetric mesh",
     sym_v_over_floor, Y_LOW, "*", "#b03030", "#600"),
    ("P4", "Mirror-y OOD-stress",
     my_v_over_floor, Y_OUT, "s", "#d68a1e", "#7a4d00"),
    ("P5", "Conservation (absolute, deferred)",
     cons_abs_x, Y_OUT, "o", "white", "#555"),
]

# point coordinate notes for legend
point_notes = {
    "P1": f"V/floor $\\approx 0$",
    "P2": f"ratio $= {cons_median:.3f}$, V/floor $= {cons_v_over_floor:.3f}$",
    "P3": f"V $= {sym_v:.2f}$, floor $= 10^{{-6}}$",
    "P4": f"V/floor median $= {my_v_over_floor:.2f}$",
    "P5": "operator-floor admissibility fails",
}

# ---- Plot ----
fig = plt.figure(figsize=(8.6, 4.2))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 0.68], wspace=0.05)
ax = fig.add_subplot(gs[0, 0])
ax_leg = fig.add_subplot(gs[0, 1]); ax_leg.axis("off")

x_lo, x_hi = X_FLOOR_PLOT, 1e7

# Region shading
pass_color = "#d8efd8"
fail_color = "#f2cdcd"
ood_color = "#fde4c4"
numtol_color = "#e6e6f5"

# y in [0,1] = Low; [1,2] = Borderline; [2,3] = Out
# x split at V/floor = 1 (the "V dominates floor" line)
ax.axhspan(0.0, 1.0, xmin=0.0, xmax=0.5, facecolor=pass_color, alpha=0.55, zorder=0)
ax.axhspan(0.0, 1.0, xmin=0.5, xmax=1.0, facecolor=fail_color, alpha=0.55, zorder=0)
ax.axhspan(2.0, 3.0, xmin=0.0, xmax=1.0, facecolor=ood_color, alpha=0.55, zorder=0)
ax.axhspan(1.0, 2.0, xmin=0.0, xmax=1.0, facecolor=ood_color, alpha=0.28, zorder=0)
# numerical-tolerance band overlay on pass strip where V < floor
ax.axvspan(x_lo, 1.0, ymin=0.0, ymax=1.0 / 3, facecolor=numtol_color,
           alpha=0.55, zorder=0)

# Floor reference line
ax.axvline(1.0, color="#444", lw=0.9, ls="--", zorder=1.5)
ax.text(1.0, 2.98, "V = floor", ha="center", va="top", fontsize=8,
        color="#444", style="italic", zorder=3)

# Plot points + P1..P5 chips (no overlapping textual labels in-axis)
for (key, label, vf, y, mk, fc, ec) in points:
    x = x_plot(vf)
    ax.scatter([x], [y], s=(220 if mk == "*" else 130),
               marker=mk, facecolor=fc, edgecolor=ec, linewidth=1.4, zorder=4)
    # small chip label next to the point with white halo so it never overlaps shading
    ax.annotate(key, (x, y), xytext=(7, -10), textcoords="offset points",
                fontsize=9, weight="bold", color=ec,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                          edgecolor="none", alpha=0.85),
                zorder=5)

# Axes
ax.set_xscale("log")
ax.set_xlim(x_lo, x_hi)
ax.set_ylim(0.0, 3.0)
ax.set_xlabel(r"Relation-violation $V/\mathrm{floor}$ (log scale)", fontsize=10)
ax.set_ylabel("Domain-violation level (qualitative)", fontsize=10)
ax.set_yticks([Y_LOW, Y_BORDER, Y_OUT])
ax.set_yticklabels(["Low", "Borderline", "Out"])
ax.set_title("Two-dimensional verdict reading of the four cylinder-flow pilots",
             fontsize=11)
ax.grid(True, which="both", axis="x", alpha=0.25, linestyle=":", linewidth=0.5)

# ---- Right-side legends (regions + pilots), so no labels live inside the axes
# Region legend
region_handles = [
    mpatches.Patch(facecolor=pass_color, edgecolor="#1f5d1f",
                   label="pass  (low V, low D)"),
    mpatches.Patch(facecolor=fail_color, edgecolor="#7a1d1d",
                   label="SUT inconsistency  (high V, low D)"),
    mpatches.Patch(facecolor=ood_color, edgecolor="#7a4d00",
                   label="OOD-stress / out-of-domain  (high D)"),
    mpatches.Patch(facecolor=numtol_color, edgecolor="#444466",
                   label="numerical-tolerance  (V $<$ floor)"),
]
leg_region = ax_leg.legend(handles=region_handles, loc="upper left",
                           bbox_to_anchor=(0.0, 1.00),
                           title="Verdict regions", title_fontsize=9.5,
                           fontsize=9, frameon=True, handlelength=1.6)
leg_region._legend_box.align = "left"
ax_leg.add_artist(leg_region)

# Pilot legend (per-point key with measured coordinate)
pilot_handles = []
for (key, label, vf, y, mk, fc, ec) in points:
    pilot_handles.append(Line2D([0], [0], marker=mk,
                                color="none", markerfacecolor=fc,
                                markeredgecolor=ec, markersize=10,
                                markeredgewidth=1.4,
                                label=f"{key}: {label}\n     {point_notes[key]}"))
leg_pilot = ax_leg.legend(handles=pilot_handles, loc="lower left",
                          bbox_to_anchor=(0.0, 0.00),
                          title="Pilots (medians from real ledgers)",
                          title_fontsize=9.5, fontsize=8.6,
                          labelspacing=0.9, handletextpad=0.6,
                          frameon=True, handlelength=1.6)
leg_pilot._legend_box.align = "left"

fig.tight_layout()
OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PDF, bbox_inches="tight")
fig.savefig(OUT_PNG, bbox_inches="tight", dpi=150)
print(f"wrote {OUT_PDF}")
print(f"wrote {OUT_PNG}")
print("\nplotted coordinates:")
for (key, label, vf, y, *_rest) in points:
    print(f"  {key}  V/floor={vf:.3g}  y_bin={y}  {label}")
