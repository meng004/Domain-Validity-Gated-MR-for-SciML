#!/usr/bin/env python3
"""Closed-form a-priori bound on the P1 cell-divergence operator floor.

Reviewer concern (v22/v23/v24 DomainExpert + DevilsAdvocate): the operator-floor
sweep (E2) validates only the *slope* (O(h) order), while the absolute floor used
to defer the conservation MR is estimated empirically from the reference field.
This experiment closes that gap for the concrete deployed-scale structured mesh by
deriving a *closed-form* leading-order predictor and a *rigorous a-priori upper
bound* for the per-cell truncation error, and verifying that the empirically
measured floor (a) matches the closed-form predictor and (b) is dominated by the
closed-form bound.

Derivation (exact, not fitted)
------------------------------
The constant-per-cell divergence operator div_h (tools.conservation_rubric.
cell_divergence) is *exact on affine velocity fields*: div_h(T) = div(u)(c) for
any affine T, where c is the cell centroid. For the analytic reference field
u = (psi_y, -psi_x), psi = sin(KX x) sin(KY y), div(u) == 0 everywhere, so the
affine Taylor polynomial of u about c contributes exactly 0. By the second-order
Lagrange remainder, each nodal sample is u_i = T_i + R_i with
R_i = 1/2 (p_i - c)^T H_u(xi_i) (p_i - c) for some xi_i on the segment [c, p_i].
Hence the measured divergence is, EXACTLY,

    div_h(u_sampled) = (1/2A) [ sum_i Rx_i b_i + sum_i Ry_i c_i ],

with b_i = y_j - y_k, c_i = x_k - x_j the standard P1 gradient coefficients.

  * Closed-form leading-order predictor E_pred uses the analytic Hessian at the
    centroid (R_i ~ 1/2 (p_i-c)^T H_u(c) (p_i-c)); it matches the measured floor
    to O(h^3).
  * Rigorous a-priori upper bound B_K uses the analytic *global* spectral-norm
    bound M2 = sup ||H_u||_2 over the domain (closed form in KX, KY), giving
        |div_h| <= (1/(2|A|)) * (1/2) * M2 * (max_i |p_i-c|^2) * sum_i(|b_i|+|c_i|),
    a strict upper bound on the per-cell operator error.

Scope: one concrete structured mesh family and one smooth analytic field. This is
a closed-form floor for that concrete case, not a general bound for arbitrary
unstructured cylinder meshes (which remains future work).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from conservation_rubric import cell_divergence, interior_cell_mask  # noqa: E402
from run_mirror_y_symmetric_mesh import build_symmetric_channel  # noqa: E402
from run_operator_floor_sweep import Lx, Ly, KX, KY, analytic_velocity, char_length  # noqa: E402

OUTDIR = ROOT / "research_assets" / "runs" / "operator-floor-analytic-bound"

# Deployed-scale level plus two finer levels to show the predictor ratio -> 1.
LEVELS = [
    {"level": "h0", "nx": 24, "half_rows": 10},
    {"level": "h0/2", "nx": 48, "half_rows": 20},
    {"level": "h0/4", "nx": 96, "half_rows": 40},
]


def hessian_x(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Hessian of u_x = KY sin(KX x) cos(KY y). Returns (...,2,2)."""
    s_x, c_x = np.sin(KX * x), np.cos(KX * x)
    s_y, c_y = np.sin(KY * y), np.cos(KY * y)
    hxx = -KY * KX**2 * s_x * c_y
    hyy = -KY**3 * s_x * c_y
    hxy = -KX * KY**2 * c_x * s_y
    return np.stack([np.stack([hxx, hxy], -1), np.stack([hxy, hyy], -1)], -2)


def hessian_y(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Hessian of u_y = -KX cos(KX x) sin(KY y). Returns (...,2,2)."""
    s_x, c_x = np.sin(KX * x), np.cos(KX * x)
    s_y, c_y = np.sin(KY * y), np.cos(KY * y)
    hxx = KX**3 * c_x * s_y
    hyy = KX * KY**2 * c_x * s_y
    hxy = KX**2 * KY * s_x * c_y
    return np.stack([np.stack([hxx, hxy], -1), np.stack([hxy, hyy], -1)], -2)


def global_spectral_bound() -> float:
    """Rigorous closed-form sup ||H_u||_2 over the domain (Frobenius dominates
    spectral; each entry bounded by its trig-free amplitude)."""
    m2x = np.sqrt((KY * KX**2) ** 2 + 2 * (KX * KY**2) ** 2 + (KY**3) ** 2)
    m2y = np.sqrt((KX**3) ** 2 + 2 * (KX**2 * KY) ** 2 + (KX * KY**2) ** 2)
    return float(max(m2x, m2y))


def quad_form(dp: np.ndarray, H: np.ndarray) -> np.ndarray:
    """0.5 * dp^T H dp for batched dp (...,3,2) and H (...,2,2)."""
    # dp: (C,3,2); H: (C,2,2) -> (C,3)
    Hdp = np.einsum("cij,ckj->cki", H, dp)        # (C,3,2)
    return 0.5 * np.einsum("cki,cki->ck", dp, Hdp)  # (C,3)


def area_weighted_rms(vals: np.ndarray, area: np.ndarray) -> float:
    total = float(area.sum())
    return float(np.sqrt(np.sum(area * vals**2) / total)) if total > 0 else float("nan")


def analyse_level(nx: int, half_rows: int) -> dict:
    pos, node_type, cells, _ = build_symmetric_channel(nx=nx, half_rows=half_rows, Lx=Lx, Ly=Ly)
    vel = analytic_velocity(pos)
    mask = interior_cell_mask(cells, node_type)

    p = pos[cells]                                  # (C,3,2)
    x0, x1, x2 = p[:, 0, 0], p[:, 1, 0], p[:, 2, 0]
    y0, y1, y2 = p[:, 0, 1], p[:, 1, 1], p[:, 2, 1]
    two_a = x0 * (y1 - y2) + x1 * (y2 - y0) + x2 * (y0 - y1)
    b = np.stack([y1 - y2, y2 - y0, y0 - y1], -1)   # (C,3)
    c = np.stack([x2 - x1, x0 - x2, x1 - x0], -1)   # (C,3)
    centroid = p.mean(axis=1)                        # (C,2)
    dp = p - centroid[:, None, :]                    # (C,3,2)

    # Measured floor (exact operator output on sampled field).
    div_meas, area = cell_divergence(pos, cells, vel)

    # Closed-form leading-order predictor: div_h of the centroid-Hessian quadratic.
    Hx = hessian_x(centroid[:, 0], centroid[:, 1])
    Hy = hessian_y(centroid[:, 0], centroid[:, 1])
    Rx = quad_form(dp, Hx)                            # (C,3)
    Ry = quad_form(dp, Hy)
    div_pred = (np.sum(Rx * b, axis=1) + np.sum(Ry * c, axis=1)) / two_a

    # Rigorous closed-form a-priori upper bound per cell.
    m2 = global_spectral_bound()
    max_d2 = np.max(np.sum(dp**2, axis=2), axis=1)   # max_i |p_i - c|^2
    sum_bc = np.sum(np.abs(b) + np.abs(c), axis=1)
    bound = (1.0 / (2.0 * np.abs(two_a))) * 0.5 * m2 * max_d2 * sum_bc

    meas_rms = area_weighted_rms(div_meas[mask], area[mask])
    pred_rms = area_weighted_rms(div_pred[mask], area[mask])
    bound_rms = area_weighted_rms(bound[mask], area[mask])
    bound_max = float(np.max(bound[mask]))
    meas_max = float(np.max(np.abs(div_meas[mask])))

    return {
        "nx": nx, "half_rows": half_rows,
        "interior_cells": int(mask.sum()),
        "h_rms_edge": char_length(pos, cells),
        "measured_floor_rms": meas_rms,
        "predicted_floor_rms": pred_rms,
        "bound_rms": bound_rms,
        "bound_max": bound_max,
        "measured_max_abs": meas_max,
        "predictor_ratio_meas_over_pred": meas_rms / pred_rms if pred_rms else float("nan"),
        "bound_dominates_rms": bool(bound_rms >= meas_rms),
        "bound_dominates_pointwise": bool(bound_max >= meas_max),
        "headroom_bound_over_measured_rms": bound_rms / meas_rms if meas_rms else float("nan"),
    }


def main() -> int:
    levels = [analyse_level(lv["nx"], lv["half_rows"]) for lv in LEVELS]
    deployed = levels[0]
    record = {
        "experiment_id": "E2b-operator-floor-analytic-bound",
        "schema_version": "0.1.0",
        "extends": "research_assets/runs/operator-floor-sweep-extended/operator_floor_extended_report.json",
        "motivation": (
            "Upgrade the measurement-floor gate from an empirically estimated floor "
            "to a closed-form leading-order predictor plus a rigorous a-priori upper "
            "bound, for the concrete deployed-scale structured mesh. Answers the "
            "DomainExpert/DevilsAdvocate concern that the O(h) sweep validates the "
            "slope but not the absolute floor."
        ),
        "operator": "P1 constant-per-cell divergence (tools.conservation_rubric.cell_divergence)",
        "analytic_reference": {
            "stream_function": "psi(x,y) = sin(KX x) sin(KY y); KX=pi/Lx, KY=pi/Ly",
            "velocity": "u = (psi_y, -psi_x); div(u) = 0 analytically",
            "Lx": Lx, "Ly": Ly,
        },
        "global_hessian_spectral_bound_M2": global_spectral_bound(),
        "method": (
            "div_h is exact on affine fields; div(u)==0 so the affine Taylor part "
            "contributes 0 and div_h(u_sampled) equals the geometry-weighted sum of "
            "the second-order Lagrange remainders, EXACTLY. Predictor uses the "
            "centroid Hessian (leading order); bound uses the global spectral-norm "
            "sup M2 (strict)."
        ),
        "levels": levels,
        "deployed_level": "h0",
        "verdict": {
            "predictor_matches_measured": bool(abs(deployed["predictor_ratio_meas_over_pred"] - 1.0) < 0.15),
            "bound_dominates_measured": bool(deployed["bound_dominates_rms"] and deployed["bound_dominates_pointwise"]),
            "closed_form_floor_available_for_concrete_mesh": True,
            "general_unstructured_bound": "future work",
        },
        "honesty_boundary": (
            "Closed-form floor for one structured mesh family and one analytic field. "
            "Not a general a-priori bound for arbitrary unstructured cylinder meshes, "
            "and not a model-accuracy or reliability claim."
        ),
    }
    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / "operator_floor_analytic_bound_report.json"
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    for lv in levels:
        print(f"  {lv['nx']:>3}x: meas_rms={lv['measured_floor_rms']:.4f} "
              f"pred_rms={lv['predicted_floor_rms']:.4f} "
              f"ratio={lv['predictor_ratio_meas_over_pred']:.4f} "
              f"bound_rms={lv['bound_rms']:.3f} "
              f"dominates={lv['bound_dominates_rms'] and lv['bound_dominates_pointwise']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
