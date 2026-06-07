"""Render the 2D verdict-reading figure (Figure 3).

Visualises the paper's central conceptual contribution: reading a relation-
level verdict in TWO dimensions rather than as a flat pass/fail label.

  x-axis: relation-violation V/tolerance (log scale). "Tolerance" is the
          per-MR verdict threshold (machine-precision floor for exact
          relations, the reference-relative regression threshold for
          conservation, the mapping-error floor for the downgraded mirror-y
          OOD-stress probe). x < 1 = within tolerance; x = 1 is the pass/fail
          border; x >> 1 = the verdict's measured quantity violates the
          tolerance.

  y-axis: domain-violation, kept categorical (In-domain / Boundary /
          Out-of-domain), matching the manuscript's honest note that this
          axis is so far only qualitatively operationalized (Sec. 3.5).

Background shading partitions the plane into the four verdict regions of
Sec. 3.5:
  - pass                          : x < 1, In-domain
  - SUT inconsistency             : x >= 1, In-domain    (only model fail)
  - OOD-stress / out-of-domain    : Out-of-domain row    (downgraded probe)
  - boundary                      : Boundary row         (transition strip)

Five real pilot points, all read from committed metric ledgers, are plotted
at their measured (V/tolerance, D-bin) coordinates. Pass-region differentia-
tion between machine-precision exactness (P1) and within-tolerance regression
(P2) is shown by their x positions (orders of magnitude apart), not by colour.

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

# ---------------------------------------------------------------------------
# Read every coordinate from the real metric ledgers. Compute the per-MR
# tolerance-normalised violation: x = V / tolerance (log scale on the axis).
# ---------------------------------------------------------------------------
np_led = json.loads((RUNS / "real-sut-node-permutation-pilot" / "raw" /
                     "metric_ledger.json").read_text())
np_entry = np_led["entries"][0]
node_perm_v = float(np_entry["metric_value"])                            # 0.0
node_perm_tol = float(np_entry["tolerance"]["threshold"])                # 1e-6
node_perm_v_over_tol = node_perm_v / node_perm_tol                       # 0.0

my_led = json.loads((RUNS / "mirror-y-rate-upgrade" / "raw" /
                     "metric_ledger.json").read_text())
# Mirror-y is a DOWNGRADED probe: exact relation rejected by the rubric, the
# effective tolerance is the mapping-error floor of the approximate
# correspondence. The ledger already records V/floor per frame.
my_v_over_eff_tol = float(np.median([float(e["violation_over_floor"])
                                     for e in my_led["entries"]]))       # 3.96

sym_led = json.loads((RUNS / "mirror-y-symmetric-mesh" / "raw" /
                      "metric_ledger.json").read_text())
sym_v = float(sym_led["metric_value"])                                   # 1.10
sym_tol = float(sym_led["tolerance"]["threshold"])                       # 1e-6
sym_v_over_tol = sym_v / sym_tol                                        # 1.1e6

cons_led = json.loads((RUNS / "conservation-diagnostic-pilot" / "raw" /
                       "metric_ledger.json").read_text())
cons_ratios = [float(e["metric_value"]) for e in cons_led["entries"]]
cons_median = float(np.median(cons_ratios))                             # 1.005
cons_tol = 1.5
# Normalise into the per-MR pass-budget: V_normalised = (ratio - 1) / (tol - 1)
cons_v_over_tol = max(0.0, cons_median - 1.0) / (cons_tol - 1.0)        # ~0.01

# ---------------------------------------------------------------------------
# Plot layout
# ---------------------------------------------------------------------------
Y_IN, Y_BORDER, Y_OUT = 0.5, 1.5, 2.5
X_PLOT_FLOOR = 1e-4   # for V/tol = 0 (machine-precision exact)

def x_plot(v):
    return max(v, X_PLOT_FLOOR)


# (key, pilot label, mechanism note, V/tolerance, y-bin, marker, fc, ec)
points = [
    ("P1", "Node-perm.\\ equivariance",
     "structurally exact ($V \\equiv 0$)",
     node_perm_v_over_tol, Y_IN, "o", "#2c7a2c", "#1c4d1c"),
    ("P2", "Conservation (ref.-relative)",
     f"ratio $= {cons_median:.3f}$, within tol.\\ budget",
     cons_v_over_tol, Y_IN, "D", "#2c7a2c", "#1c4d1c"),
    ("P3", "Mirror-y on symmetric mesh",
     f"$V = {sym_v:.2f}$, $\\mathrm{{tol}} = 10^{{-6}}$",
     sym_v_over_tol, Y_IN, "*", "#b03030", "#600"),
    ("P4", "Mirror-y OOD-stress (downgraded)",
     f"$V/\\mathrm{{floor}} = {my_v_over_eff_tol:.2f}$ (floor as eff.\\ tol.)",
     my_v_over_eff_tol, Y_OUT, "s", "#d68a1e", "#7a4d00"),
]
# P5 is "admissibility-failed", does NOT enter the verdict plane; rendered
# as an off-plane callout to the right of the axes (see legend).
p5_key = "P5"
p5_label = "Conservation (absolute, deferred)"
p5_note = "admissibility predicate fails: tol.\\ $\\leq$ operator floor"

# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(11.4, 5.0))
gs = fig.add_gridspec(2, 2, width_ratios=[1.55, 0.78],
                      height_ratios=[1.0, 1.45], wspace=0.05, hspace=0.05)
ax = fig.add_subplot(gs[:, 0])
ax_leg_top = fig.add_subplot(gs[0, 1]); ax_leg_top.axis("off")
ax_leg_bot = fig.add_subplot(gs[1, 1]); ax_leg_bot.axis("off")

x_lo, x_hi = X_PLOT_FLOOR, 1e7

# Region shading with hatch patterns so the figure survives grayscale print.
# Each region gets a distinct pattern in addition to colour, and the legend
# echoes the same pattern so colour is never the only signal.
pass_color = "#d8efd8"
fail_color = "#f2cdcd"
boundary_color = "#fde4c4"
ood_color = "#fbcb88"

# Use hatch for pattern-based encoding. Light edgecolor keeps hatch readable
# without overpowering the markers.
plt.rcParams["hatch.linewidth"] = 0.6
plt.rcParams["hatch.color"] = "#666666"

ax.axhspan(0.0, 1.0, xmin=0.0, xmax=0.5,
           facecolor=pass_color, alpha=0.55, zorder=0, hatch="..",
           edgecolor="#1f5d1f")
ax.axhspan(0.0, 1.0, xmin=0.5, xmax=1.0,
           facecolor=fail_color, alpha=0.55, zorder=0, hatch="///",
           edgecolor="#7a1d1d")
ax.axhspan(1.0, 2.0, xmin=0.0, xmax=1.0,
           facecolor=boundary_color, alpha=0.40, zorder=0, hatch="---",
           edgecolor="#7a4d00")
ax.axhspan(2.0, 3.0, xmin=0.0, xmax=1.0,
           facecolor=ood_color, alpha=0.55, zorder=0, hatch="xx",
           edgecolor="#7a4d00")

# Vertical pass/fail border at V/tol = 1
ax.axvline(1.0, color="#444", lw=0.9, ls="--", zorder=1.5)
ax.text(1.0, 2.97, r"$V = \mathrm{tolerance}$", ha="center", va="top",
        fontsize=8.5, color="#444", style="italic", zorder=3,
        bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                  edgecolor="none", alpha=0.85))

# Data points + tiny bold key labels (white halo, never occludes shading)
for (key, label, note, vt, y, mk, fc, ec) in points:
    x = x_plot(vt)
    ax.scatter([x], [y], s=(230 if mk == "*" else 140),
               marker=mk, facecolor=fc, edgecolor=ec, linewidth=1.4, zorder=4)
    ax.annotate(key, (x, y), xytext=(8, -11), textcoords="offset points",
                fontsize=9.5, weight="bold", color=ec,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                          edgecolor="none", alpha=0.85),
                zorder=5)

# Hint that P1 sits at V/tol = 0 (clipped to the plot floor for log display)
ax.annotate("(P1 plotted at axis floor;\nactual $V/\\mathrm{tol} = 0$)",
            (X_PLOT_FLOOR, Y_IN), xytext=(4, 18),
            textcoords="offset points", fontsize=7.6, style="italic",
            color="#1c4d1c", zorder=5,
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                      edgecolor="#1c4d1c", lw=0.5, alpha=0.92))

# Axes
ax.set_xscale("log")
ax.set_xlim(x_lo, x_hi)
ax.set_ylim(0.0, 3.0)
ax.set_xlabel(r"Relation-violation $V/\mathrm{tolerance}$ (log scale)",
              fontsize=10)
ax.set_ylabel("Domain-violation", fontsize=10)
ax.set_yticks([Y_IN, Y_BORDER, Y_OUT])
ax.set_yticklabels(["In-domain", "Boundary", "Out-of-domain"])
ax.set_title("Two-dimensional verdict reading of the cylinder-flow pilots",
             fontsize=11)
ax.grid(True, which="both", axis="x", alpha=0.25, linestyle=":", linewidth=0.5)

# ---------------------------------------------------------------------------
# Right-hand legends
# ---------------------------------------------------------------------------
region_handles = [
    mpatches.Patch(facecolor=pass_color, edgecolor="#1f5d1f", hatch="..",
                   label="pass  ($V < $ tol., In-domain)"),
    mpatches.Patch(facecolor=fail_color, edgecolor="#7a1d1d", hatch="///",
                   label="SUT inconsistency  ($V \\geq$ tol., In-domain)"),
    mpatches.Patch(facecolor=boundary_color, edgecolor="#7a4d00", hatch="---",
                   label="boundary  (Boundary row)"),
    mpatches.Patch(facecolor=ood_color, edgecolor="#7a4d00", hatch="xx",
                   label="OOD-stress / out-of-domain  (Out row)"),
]
leg_region = ax_leg_top.legend(handles=region_handles, loc="upper left",
                               bbox_to_anchor=(0.0, 1.00),
                               title="Verdict regions", title_fontsize=9.5,
                               fontsize=9, frameon=True, handlelength=1.6,
                               borderpad=0.8, handletextpad=0.7)
leg_region._legend_box.align = "left"

pilot_handles = []
for (key, label, note, vt, y, mk, fc, ec) in points:
    pilot_handles.append(Line2D([0], [0], marker=mk, color="none",
                                markerfacecolor=fc, markeredgecolor=ec,
                                markersize=10, markeredgewidth=1.4,
                                label=f"{key}: {label}\n     {note}"))

leg_pilot = ax_leg_bot.legend(handles=pilot_handles, loc="upper left",
                              bbox_to_anchor=(0.0, 1.00),
                              title="Pilots in verdict space "
                                    "(medians from real ledgers)",
                              title_fontsize=9.5, fontsize=8.6,
                              labelspacing=1.0, handletextpad=0.7,
                              frameon=True, handlelength=1.6,
                              borderpad=0.9)
leg_pilot._legend_box.align = "left"

# ---------------------------------------------------------------------------
# Off-plane callout for P5: rendered as a single-row figure-level legend
# below the main axes, physically detached from the verdict plane and from
# the pilot legend, so legend entries map one-to-one onto markers in the
# main plot.
# ---------------------------------------------------------------------------
p5_handle = Line2D(
    [0], [0], marker="o", color="none",
    markerfacecolor="white", markeredgecolor="#555",
    markersize=10, markeredgewidth=1.4, linestyle=":",
    label=(f"Off-plane: {p5_key} {p5_label} -- {p5_note}; "
           "not admitted to the verdict space (Sec.~3.2)."),
)
# Reserve vertical space at the bottom of the figure so the callout does
# not collide with the x-axis 10^k tick labels of the log-scaled main axes.
fig.subplots_adjust(bottom=0.20)
fig.legend(handles=[p5_handle], loc="lower left",
           bbox_to_anchor=(0.01, 0.015),
           frameon=True, fontsize=9, handlelength=1.6,
           handletextpad=0.8, borderpad=0.8)

OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PDF, bbox_inches="tight", pad_inches=0.18)
fig.savefig(OUT_PNG, bbox_inches="tight", dpi=150, pad_inches=0.18)
print(f"wrote {OUT_PDF}")
print(f"wrote {OUT_PNG}")
print("\nplotted coordinates (V/tolerance, y_bin):")
for (key, label, note, vt, y, *_rest) in points:
    print(f"  {key}  V/tol={vt:.4g}  y={y}  {label}")
print(f"  {p5_key}  (off-plane callout)  {p5_label}")
