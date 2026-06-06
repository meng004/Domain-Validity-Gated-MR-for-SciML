"""Render the R3 non-monotone detection figure for PC_zero_vy by mirror-y across
the K=6 multi-checkpoint roster.

Source data: research_assets/runs/fault-robustness-e3/fault_robustness_report.json.
Output: paper/ist-submission/figures/r3_pc_zero_vy_nonmonotone.pdf (and .png).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[4]
REPORT = ROOT / "research_assets/runs/fault-robustness-e3/fault_robustness_report.json"
OUT_PDF = ROOT / "paper/ist-submission/figures/r3_pc_zero_vy_nonmonotone.pdf"
OUT_PNG = ROOT / "paper/ist-submission/figures/r3_pc_zero_vy_nonmonotone.png"


def main() -> None:
    d = json.loads(REPORT.read_text())
    levels = d["R3_PC_zero_vy_partial_fraction_sweep"]["levels"]
    rates_per_level = d["R3_PC_zero_vy_partial_fraction_sweep"]["per_level_detection_rate"]

    xs = [float(lv) for lv in levels]
    rate = [rates_per_level[str(lv)]["any"]["rate"] for lv in levels]
    lo = [rates_per_level[str(lv)]["any"]["ci_lo"] for lv in levels]
    hi = [rates_per_level[str(lv)]["any"]["ci_hi"] for lv in levels]
    err_low = [max(0.0, r - l) for r, l in zip(rate, lo)]
    err_high = [max(0.0, h - r) for r, h in zip(rate, hi)]
    ks = [rates_per_level[str(lv)]["any"]["k"] for lv in levels]
    ns = [rates_per_level[str(lv)]["any"]["n"] for lv in levels]

    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.errorbar(xs, rate, yerr=[err_low, err_high], fmt="o-", color="#1f4e79",
                ecolor="#1f4e79", capsize=4, lw=1.5, markersize=7,
                label="Detection rate across K=6 SUTs")
    ax.set_xlabel(r"PC\_zero\_vy partial-fraction $p$ (canonical: $p=1.0$)",
                  fontsize=10)
    ax.set_ylabel("Detection rate (any MR; mirror-y here)", fontsize=10)
    ax.set_ylim(-0.05, 1.1)
    ax.set_xticks(xs)
    ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.grid(True, axis="y", alpha=0.3, linestyle="--", linewidth=0.5)
    for x, r, k, n in zip(xs, rate, ks, ns):
        ax.annotate(f"{k}/{n}", (x, r), textcoords="offset points",
                    xytext=(8, -3), fontsize=8, color="#333")
    ax.axhspan(-0.05, 0.0, color="#fdecec", alpha=0.5)
    ax.set_title("R3: non-monotone detection of PC\\_zero\\_vy by mirror-y",
                 fontsize=11)
    fig.text(0.5, -0.04,
             r"Uniform $v_y=0$ at $p=1.0$ is itself mirror-y-symmetric ($0=-0$); "
             r"only partial zeroing breaks the symmetry the MR scores.",
             ha="center", fontsize=8, style="italic")
    fig.tight_layout()
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PDF, bbox_inches="tight")
    fig.savefig(OUT_PNG, bbox_inches="tight", dpi=150)
    print(f"wrote {OUT_PDF}")
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
