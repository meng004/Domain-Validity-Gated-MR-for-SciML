"""Render the operator-floor log-log convergence figure (Figure 4).

Source data: research_assets/runs/operator-floor-sweep-extended/operator_floor_extended_report.json
(produced by tools/run_operator_floor_sweep.py). Plots the area-weighted RMS
of the per-cell P1 discrete divergence on the y=0-symmetric structured
triangular channel mesh at nine resolutions from h0*2 down to h0/16, against the
characteristic edge length h. Overlays the log-log linear fit to display the
empirical convergence slope (~ 1, the theoretical P1 rate); the fitted slope is
the headline 0.984 value reported in the manuscript text and claim ledger.

Output:
  manuscript/figures/fig_4_operator_floor_loglog.pdf
  manuscript/figures/fig_4_operator_floor_loglog.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "research_assets/runs/operator-floor-sweep-extended/operator_floor_extended_report.json"
OUT_PDF = ROOT / "manuscript/figures/fig_4_operator_floor_loglog.pdf"
OUT_PNG = ROOT / "manuscript/figures/fig_4_operator_floor_loglog.png"


def main() -> None:
    d = json.loads(REPORT.read_text())
    h = np.array([r["h_rms_edge"] for r in d["levels"]])
    rms_all = np.array([r["divergence_rms_all"] for r in d["levels"]])
    rms_int = np.array([r["divergence_rms_interior"] for r in d["levels"]])
    fit_all = d["fit_all_cells"]
    labels = [r["level"] for r in d["levels"]]

    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.loglog(h, rms_all, "o", color="#1f4e79", markersize=8,
              label="All cells (measured)")
    ax.loglog(h, rms_int, "s", color="#a04040", markersize=6, mfc="none",
              label="Interior only (measured)")
    # Overlay fit line through "all cells" series (the headline slope cited in text).
    hx = np.geomspace(h.min() * 0.85, h.max() * 1.15, 40)
    fit_line = np.exp(fit_all["intercept"]) * hx ** fit_all["slope"]
    ax.loglog(hx, fit_line, "--", color="#1f4e79", lw=1.2,
              label=(f"Fit: slope = {fit_all['slope']:.3f}, "
                     f"$R^2$ = {fit_all['r_squared']:.4f}"))
    # Reference O(h) line for visual comparison.
    ref = rms_all[0] * (hx / h[0])
    ax.loglog(hx, ref, ":", color="#777777", lw=1.0, label="Reference $O(h)$ (slope $= 1$)")

    for hi, ri, lbl in zip(h, rms_all, labels):
        ax.annotate(lbl, (hi, ri), textcoords="offset points",
                    xytext=(8, -3), fontsize=8, color="#333")

    ax.set_xlabel(r"Characteristic edge length $h$ (RMS over cells)", fontsize=10)
    ax.set_ylabel(r"Area-weighted RMS of cell divergence", fontsize=10)
    ax.set_title("P1 discrete-divergence operator: empirical $O(h)$ floor",
                 fontsize=11)
    ax.grid(True, which="both", alpha=0.3, linestyle="--", linewidth=0.5)
    ax.legend(fontsize=8, loc="lower right", framealpha=0.95)
    fig.tight_layout()
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PDF, bbox_inches="tight")
    fig.savefig(OUT_PNG, bbox_inches="tight", dpi=300)
    print(f"wrote {OUT_PDF}")
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
