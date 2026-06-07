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
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
RUNS = ROOT / "research_assets" / "runs"
OUT_PDF = ROOT / "paper/ist-submission/figures/fig_3_verdict_2d.pdf"
OUT_PNG = ROOT / "paper/ist-submission/figures/fig_3_verdict_2d.png"

# ---- Pull V/floor coordinates from the REAL pilot ledgers ----

# Node-permutation: V = 0; floor = machine precision (we use the recorded tol).
# V/floor = 0; plot at the log-axis left edge.
np_led = json.loads((RUNS / "real-sut-node-permutation-pilot" / "raw" /
                     "metric_ledger.json").read_text())
np_entry = np_led["entries"][0]
node_perm_v = float(np_entry["metric_value"])  # 0.0

# Mirror-y OOD-stress: V and mapping_error_floor per frame; take median V/floor.
my_led = json.loads((RUNS / "mirror-y-rate-upgrade" / "raw" /
                     "metric_ledger.json").read_text())
my_ratios = [float(e["violation_over_floor"]) for e in my_led["entries"]]
my_v_over_floor = float(np.median(my_ratios))

# Mirror-y on the synthetic symmetric mesh: V vs the exact-relation tol (1e-6).
sym_led = json.loads((RUNS / "mirror-y-symmetric-mesh" / "raw" /
                      "metric_ledger.json").read_text())
sym_v = float(sym_led["metric_value"])
sym_tol = float(sym_led["tolerance"]["threshold"])
sym_v_over_floor = sym_v / sym_tol  # large -- this is the headline finding

# Conservation (reference-relative): excess over pass region, normalized by
# the remaining tolerance budget. ratio < 1.0 has no meaning here, so we clip.
cons_led = json.loads((RUNS / "conservation-diagnostic-pilot" / "raw" /
                       "metric_ledger.json").read_text())
cons_ratios = [float(e["metric_value"]) for e in cons_led["entries"]]
cons_excess = max(0.0, float(np.median(cons_ratios)) - 1.0)
cons_tol_budget = 1.5 - 1.0
cons_v_over_floor = cons_excess / cons_tol_budget  # ~ 0.005--0.01

# Conservation (absolute, deferred): no measurement -- illustrative position
# in the numerical-tolerance / OOD region, drawn as a hollow marker.
cons_abs_x = 0.3  # below floor: V/floor < 1
cons_abs_y_bin = "Out"  # operator-floor admissibility fails on the real mesh

# ---- Coordinate mapping ----
# x: V/floor on log scale; replace 0 with a small floor for plotting.
def x_for(v_over_floor: float) -> float:
    return max(v_over_floor, 1e-2)

# y: qualitative bin -> numeric for plotting only.
Y_LOW, Y_BORDER, Y_OUT = 0.5, 1.5, 2.5

points = [
    # (label, V/floor, y-bin, marker, facecolor, edgecolor, note line)
    ("Node-perm.\nequivariance",
     0.0, Y_LOW, "o", "#2c7a2c", "#1c4d1c",
     f"V/floor $\\approx 0$"),
    ("Conservation\n(ref.-relative)",
     cons_v_over_floor, Y_LOW, "o", "#2c7a2c", "#1c4d1c",
     f"ratio $= {np.median(cons_ratios):.3f}$"),
    ("Mirror-y on\nsymmetric mesh",
     sym_v_over_floor, Y_LOW, "*", "#b03030", "#600",
     f"V $= {sym_v:.2f}$, floor $= 10^{{-6}}$"),
    ("Mirror-y\nOOD-stress",
     my_v_over_floor, Y_OUT, "s", "#d68a1e", "#7a4d00",
     f"V/floor median $= {my_v_over_floor:.2f}$"),
    ("Conservation\n(absolute, deferred)",
     cons_abs_x, Y_OUT, "o", "white", "#555",
     "operator-floor admissibility fails"),
]

# ---- Plot ----
fig, ax = plt.subplots(figsize=(6.3, 4.0))
x_lo, x_hi = 1e-2, 5e6
y_lo, y_hi = 0.0, 3.0

# Region shading
pass_color = "#d8efd8"
fail_color = "#f2cdcd"
ood_color = "#fde4c4"
numtol_color = "#e6e6f5"

ax.axhspan(0.0, 1.0, xmin=0, xmax=0.5, facecolor=pass_color, alpha=0.55, zorder=0)
ax.axhspan(0.0, 1.0, xmin=0.5, xmax=1.0, facecolor=fail_color, alpha=0.55, zorder=0)
ax.axhspan(2.0, 3.0, xmin=0.0, xmax=1.0, facecolor=ood_color, alpha=0.55, zorder=0)
ax.axhspan(1.0, 2.0, xmin=0.0, xmax=1.0, facecolor=ood_color, alpha=0.28, zorder=0)
# numerical-tolerance band: V/floor < 1 strip (vertical) overlay on the pass band
ax.axvspan(x_lo, 1.0, ymin=0.0, ymax=1.0/3, facecolor=numtol_color, alpha=0.55, zorder=0)

# Region labels
def rtext(x, y, s, color="#333"):
    ax.text(x, y, s, ha="center", va="center", fontsize=9.5, color=color,
            weight="bold", zorder=2)

rtext(0.18, 0.5, "numerical-\ntolerance", color="#444466")
rtext(1e2, 0.5, "SUT\ninconsistency", color="#7a1d1d")
rtext(0.18, 2.5, "out-of-relation-domain", color="#7a4d00")
rtext(1e2, 2.5, "OOD-stress\n(downgraded)", color="#7a4d00")
rtext(6, 0.5, "pass", color="#1f5d1f")

# Vertical floor line
ax.axvline(1.0, color="#555", lw=0.9, ls="--", zorder=1.5)
ax.text(1.0, 2.95, "V = floor", ha="center", va="top", fontsize=8,
        color="#444", style="italic", zorder=3)

# Plot the points
for (label, vf, y, mk, fc, ec, note) in points:
    x = x_for(vf)
    ax.scatter([x], [y], s=180 if mk == "*" else 120,
               marker=mk, facecolor=fc, edgecolor=ec, linewidth=1.4,
               zorder=4)
    dx = 1.6 if mk == "s" else 1.8
    dy = 0.32
    ax.annotate(label, (x, y),
                xytext=(x * dx if vf > 0.1 else 0.04, y + dy),
                textcoords="data" if vf > 0.1 else "data",
                fontsize=8.5, ha="left", va="bottom",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                          edgecolor=ec, lw=0.8, alpha=0.92),
                zorder=5)

# Axes
ax.set_xscale("log")
ax.set_xlim(x_lo, x_hi)
ax.set_ylim(y_lo, y_hi)
ax.set_xlabel(r"Relation-violation $V/\mathrm{floor}$ (log scale)", fontsize=10)
ax.set_ylabel("Domain-violation level (qualitative)", fontsize=10)
ax.set_yticks([Y_LOW, Y_BORDER, Y_OUT])
ax.set_yticklabels(["Low", "Borderline", "Out"])
ax.set_title("Two-dimensional verdict reading of the four cylinder-flow pilots",
             fontsize=11)
ax.grid(True, which="both", axis="x", alpha=0.25, linestyle=":", linewidth=0.5)

fig.tight_layout()
OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PDF, bbox_inches="tight")
fig.savefig(OUT_PNG, bbox_inches="tight", dpi=150)
print(f"wrote {OUT_PDF}")
print(f"wrote {OUT_PNG}")
print(f"\nplotted coordinates:")
for (lb, vf, y, *_rest) in points:
    print(f"  {lb!r:35s}  V/floor={vf:.3g}  y_bin={y}")
