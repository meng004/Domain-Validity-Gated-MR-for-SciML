"""E2-extended: 9-resolution sweep of the P1 discrete-divergence operator floor.

Extends ``run_operator_floor_sweep.py`` (4 resolutions: h0, h0/2, h0/4, h0/8)
to nine resolutions (h0*2, h0, h0/2, h0/3, h0/4, h0/6, h0/8, h0/12, h0/16) on
the SAME y=0-symmetric structured triangular channel mesh family and the SAME
analytically divergence-free stream-function reference field. Methodology is
unchanged; only the resolution set is widened so the log-log linear fit of
RMS vs. h carries a slope standard error and a 95% confidence interval,
addressing the reviewer concern that a 4-point R^2 = 1.000 fit reports no
slope uncertainty (P1-5).

The original 4-point artifact under research_assets/runs/operator-floor-sweep/
is left untouched; this script writes to
research_assets/runs/operator-floor-sweep-extended/.

Honesty boundary: this measures the operator floor under one structured
symmetric mesh family and a single smooth analytic field; it is calibration of
the admissibility predicate (numerical decidability), not a generalization
claim across mesh families, geometries, or SUTs, and not a closed-form bound.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from conservation_rubric import divergence_rms, interior_cell_mask  # noqa: E402
from run_mirror_y_symmetric_mesh import build_symmetric_channel  # noqa: E402
from run_operator_floor_sweep import (  # noqa: E402
    Lx, Ly, analytic_velocity, char_length,
)

# Two-sided 97.5% Student-t quantiles for small df (df = n - 2).
T_975 = {2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
         8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179}


def linfit_ci(logh: np.ndarray, logr: np.ndarray) -> dict:
    """OLS fit logr = slope*logh + b with slope SE and 95% CI (Student t)."""
    n = len(logh)
    mx = float(logh.mean()); my = float(logr.mean())
    sxx = float(np.sum((logh - mx) ** 2))
    sxy = float(np.sum((logh - mx) * (logr - my)))
    slope = sxy / sxx
    intercept = my - slope * mx
    resid = logr - (slope * logh + intercept)
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((logr - my) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    df = n - 2
    se = float(np.sqrt(ss_res / df / sxx)) if df > 0 else float("nan")
    t = T_975.get(df)
    if t is None:
        raise ValueError(f"df={df} outside the tabulated t-quantile range")
    return {
        "n_points": n, "slope": slope, "intercept": intercept,
        "r_squared": r2, "slope_se": se, "dof": df,
        "t_975": t,
        "slope_ci95": [slope - t * se, slope + t * se],
        "expected_slope_oh": 1.0,
    }


# Nine resolution levels on the same mesh family. base h0: nx=24, half_rows=10.
LEVELS = [
    dict(nx=12, half_rows=5, label="h0*2"),
    dict(nx=24, half_rows=10, label="h0"),
    dict(nx=48, half_rows=20, label="h0/2"),
    dict(nx=72, half_rows=30, label="h0/3"),
    dict(nx=96, half_rows=40, label="h0/4"),
    dict(nx=144, half_rows=60, label="h0/6"),
    dict(nx=192, half_rows=80, label="h0/8"),
    dict(nx=288, half_rows=120, label="h0/12"),
    dict(nx=384, half_rows=160, label="h0/16"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--outdir",
        default=str(ROOT / "research_assets/runs/operator-floor-sweep-extended"))
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    records = []
    for lv in LEVELS:
        pos, node_type, cells, sigma = build_symmetric_channel(
            nx=lv["nx"], half_rows=lv["half_rows"], Lx=Lx, Ly=Ly)
        vel = analytic_velocity(pos)
        h = char_length(pos, cells)
        rms_all = divergence_rms(pos, cells, vel)
        mask = interior_cell_mask(cells, node_type, interior_types=(0, 5))
        rms_interior = divergence_rms(pos, cells, vel, mask=mask)
        records.append({
            "level": lv["label"], "nx": lv["nx"], "half_rows": lv["half_rows"],
            "num_nodes": int(pos.shape[0]), "num_cells": int(cells.shape[0]),
            "h_rms_edge": h,
            "divergence_rms_all": rms_all,
            "divergence_rms_interior": rms_interior,
            "interior_cell_count": int(mask.sum()),
        })
        print(f"  {lv['label']:6s} nx={lv['nx']:3d} h={h:.4g} "
              f"rms_all={rms_all:.4g} rms_int={rms_interior:.4g} "
              f"(cells={cells.shape[0]})")

    logh = np.array([np.log(r["h_rms_edge"]) for r in records])
    fit_all = linfit_ci(logh, np.array(
        [np.log(r["divergence_rms_all"]) for r in records]))
    fit_int = linfit_ci(logh, np.array(
        [np.log(r["divergence_rms_interior"]) for r in records]))

    report = {
        "experiment_id": "E2-operator-floor-resolution-sweep-extended",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "extends": "research_assets/runs/operator-floor-sweep/operator_floor_report.json",
        "motivation": (
            "Reviewer concern P1-5: 4-resolution R^2=1.000 fit reported no slope "
            "confidence interval. This run widens the same sweep to 9 resolutions "
            "and reports the OLS slope standard error and Student-t 95% CI."),
        "analytic_reference": {
            "stream_function": "psi(x,y) = sin(pi x / Lx) * sin(pi y / Ly)",
            "velocity": "u = (psi_y, -psi_x); div(u) = 0 analytically",
            "Lx": Lx, "Ly": Ly,
        },
        "operator": "P1 constant-per-cell divergence (tools.conservation_rubric.cell_divergence)",
        "norm": "area-weighted RMS",
        "mesh_family": "y=0-symmetric structured triangular channel "
                       "(tools.run_mirror_y_symmetric_mesh.build_symmetric_channel)",
        "levels": records,
        "fit_all_cells": fit_all,
        "fit_interior_only": fit_int,
        "verdict": ("operator-floor-empirically-first-order"
                    if 0.85 <= fit_all["slope"] <= 1.15 else "off-expected-rate"),
        "honesty_boundary": (
            "Single structured y=0-symmetric triangular mesh family and one "
            "smooth analytic stream-function field. This calibrates the "
            "operator-floor magnitude in the admissibility predicate (numerical "
            "decidability); it is NOT a generalization claim across mesh "
            "families, geometries, analytic fields, or SUTs, and NOT a "
            "closed-form bound."),
    }
    (outdir / "operator_floor_extended_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nfit (all cells): slope={fit_all['slope']:.4f} "
          f"SE={fit_all['slope_se']:.4f} "
          f"95% CI=[{fit_all['slope_ci95'][0]:.4f}, {fit_all['slope_ci95'][1]:.4f}] "
          f"R^2={fit_all['r_squared']:.6f}")
    print(f"fit (interior) : slope={fit_int['slope']:.4f} "
          f"SE={fit_int['slope_se']:.4f} "
          f"95% CI=[{fit_int['slope_ci95'][0]:.4f}, {fit_int['slope_ci95'][1]:.4f}] "
          f"R^2={fit_int['r_squared']:.6f}")
    print(f"verdict: {report['verdict']}")
    print(f"wrote {outdir/'operator_floor_extended_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
