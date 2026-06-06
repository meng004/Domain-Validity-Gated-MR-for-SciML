"""E2: empirical resolution sweep of the P1 discrete-divergence operator floor.

Builds the same y=0-symmetric structured triangular channel mesh used by
``run_mirror_y_symmetric_mesh.py`` at four resolutions (h0, h0/2, h0/4, h0/8),
evaluates an analytically divergence-free reference velocity field from a smooth
stream function psi(x,y) = sin(pi x / Lx) * sin(pi y / Ly), and measures the
area-weighted RMS of the per-cell discrete divergence on each mesh. A log-log
linear fit of RMS vs. h gives the empirical convergence slope.

This calibrates the operator floor that the verdict tolerance must dominate in
the admissibility predicate (numerical decidability). Theoretical expectation:
constant-per-cell P1 gradient is first-order accurate on smooth fields, so the
RMS should scale as O(h) (slope ~ 1).

Honesty boundary: this measures the operator floor under a structured symmetric
mesh family and a single smooth analytic field; it is calibration of the
admissibility predicate, not a generalization claim across mesh families.
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
from conservation_rubric import cell_divergence, divergence_rms, interior_cell_mask  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_mirror_y_symmetric_mesh import build_symmetric_channel  # noqa: E402

Lx, Ly = 1.6, 0.4
KX, KY = np.pi / Lx, np.pi / Ly


def analytic_velocity(pos: np.ndarray) -> np.ndarray:
    """u = (psi_y, -psi_x) with psi = sin(KX x) sin(KY y); analytically div-free."""
    x, y = pos[:, 0], pos[:, 1]
    ux = KY * np.sin(KX * x) * np.cos(KY * y)
    uy = -KX * np.cos(KX * x) * np.sin(KY * y)
    return np.stack([ux, uy], axis=1)


def char_length(pos: np.ndarray, cells: np.ndarray) -> float:
    """Characteristic mesh size: RMS of triangle edge lengths."""
    p = pos[cells]
    e = np.concatenate([p[:, 1] - p[:, 0], p[:, 2] - p[:, 1], p[:, 0] - p[:, 2]], axis=0)
    return float(np.sqrt(np.mean(np.sum(e ** 2, axis=1))))


def linfit(logh: np.ndarray, logr: np.ndarray) -> tuple[float, float, float]:
    """Return (slope, intercept, R^2) for logr = slope*logh + intercept."""
    n = len(logh)
    mx = float(logh.mean()); my = float(logr.mean())
    sxx = float(np.sum((logh - mx) ** 2))
    sxy = float(np.sum((logh - mx) * (logr - my)))
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_tot = float(np.sum((logr - my) ** 2))
    ss_res = float(np.sum((logr - (slope * logh + intercept)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return slope, intercept, r2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(ROOT / "research_assets/runs/operator-floor-sweep"))
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Four resolution levels: each step halves h by doubling nx and half_rows.
    levels = [
        dict(nx=24, half_rows=10, label="h0"),
        dict(nx=48, half_rows=20, label="h0/2"),
        dict(nx=96, half_rows=40, label="h0/4"),
        dict(nx=192, half_rows=80, label="h0/8"),
    ]

    records = []
    for lv in levels:
        pos, node_type, cells, sigma = build_symmetric_channel(
            nx=lv["nx"], half_rows=lv["half_rows"], Lx=Lx, Ly=Ly)
        vel = analytic_velocity(pos)
        h = char_length(pos, cells)
        rms_all = divergence_rms(pos, cells, vel)
        mask = interior_cell_mask(cells, node_type, interior_types=(0, 5))
        rms_interior = divergence_rms(pos, cells, vel, mask=mask)
        rec = {
            "level": lv["label"], "nx": lv["nx"], "half_rows": lv["half_rows"],
            "num_nodes": int(pos.shape[0]), "num_cells": int(cells.shape[0]),
            "h_rms_edge": h,
            "divergence_rms_all": rms_all,
            "divergence_rms_interior": rms_interior,
            "interior_cell_count": int(mask.sum()),
        }
        records.append(rec)
        print(f"  {lv['label']:6s} nx={lv['nx']:3d} h={h:.4g} "
              f"rms_all={rms_all:.4g} rms_int={rms_interior:.4g} "
              f"(cells={cells.shape[0]})")

    logh = np.array([np.log(r["h_rms_edge"]) for r in records])
    logr_all = np.array([np.log(r["divergence_rms_all"]) for r in records])
    logr_int = np.array([np.log(r["divergence_rms_interior"]) for r in records])
    slope_all, b_all, r2_all = linfit(logh, logr_all)
    slope_int, b_int, r2_int = linfit(logh, logr_int)

    report = {
        "experiment_id": "E2-operator-floor-resolution-sweep",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
        "fit_all_cells": {"slope": slope_all, "intercept": b_all, "r_squared": r2_all,
                          "expected_slope_oh": 1.0},
        "fit_interior_only": {"slope": slope_int, "intercept": b_int, "r_squared": r2_int,
                              "expected_slope_oh": 1.0},
        "verdict": ("operator-floor-empirically-first-order"
                    if 0.85 <= slope_all <= 1.15 else "off-expected-rate"),
        "claim_limitations": (
            "Structured symmetric mesh family and one smooth stream-function "
            "field. Calibrates the admissibility-predicate operator floor; not a "
            "generalization claim across mesh families or SUTs."),
    }
    (outdir / "operator_floor_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nfit (all cells): slope={slope_all:.3f} R^2={r2_all:.3f}")
    print(f"fit (interior) : slope={slope_int:.3f} R^2={r2_int:.3f}")
    print(f"verdict: {report['verdict']}")
    print(f"wrote {outdir/'operator_floor_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
