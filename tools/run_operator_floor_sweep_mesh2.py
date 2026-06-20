"""EXT-2: cross-topology check of the P1 discrete-divergence operator floor.

The structured sweeps (``run_operator_floor_sweep.py`` /
``..._extended.py``) measure the operator floor on ONE mesh family: a
y=0-symmetric *structured* triangular channel. Their honesty boundary
explicitly disclaims generalization across mesh topologies, and claim C12
forbids it. This script closes that gap by one bounded step: it re-measures the
SAME operator floor on a genuinely DIFFERENT, *unstructured* topology -- a
Delaunay triangulation of a jittered grid (irregular node valence, non-uniform
triangle shapes) -- over the SAME domain and the SAME analytically
divergence-free reference field, then compares the floor magnitude and the
log-log O(h) slope against the structured sweep.

The operator (``conservation_rubric.cell_divergence`` / ``divergence_rms``) and
the analytic field (``run_operator_floor_sweep.analytic_velocity``) are
mesh-agnostic; only the mesh *connectivity* changes. So this isolates the
effect of topology on the calibrated floor.

Acceptance (recorded, not asserted here): the floor is "topology-stable" when
(a) the unstructured log-log slope stays first-order (0.85 <= slope <= 1.15),
i.e. the numerical-decidability verdict does not flip, AND (b) the floor
magnitude stays the same order as the structured family at matched resolution
(max cross-topology RMS ratio <= 3.0). If either fails, the result is reported
honestly as a topology-specific boundary, not hidden.

Honesty boundary: this is TWO specific mesh topologies (structured triangular +
unstructured Delaunay), one smooth analytic field, one domain. It is NOT a
generalization claim across arbitrary mesh families, and NOT a closed-form
bound for unstructured meshes (that remains future work; cf. C32).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.spatial import Delaunay

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from conservation_rubric import divergence_rms, interior_cell_mask  # noqa: E402
from run_operator_floor_sweep import Lx, Ly, analytic_velocity, char_length  # noqa: E402
from run_operator_floor_sweep_extended import linfit_ci  # noqa: E402

NODE_NORMAL, NODE_INFLOW, NODE_OUTFLOW, NODE_WALL = 0, 4, 5, 6

# Eight node densities matching a subset of the structured extended sweep
# (same nx / 2*half_rows+1 grid counts, so h is directly comparable).
LEVELS = [
    dict(nx=24, ny=21, label="m0"),
    dict(nx=36, ny=31, label="m0/1.5"),
    dict(nx=48, ny=41, label="m0/2"),
    dict(nx=72, ny=61, label="m0/3"),
    dict(nx=96, ny=81, label="m0/4"),
    dict(nx=144, ny=121, label="m0/6"),
    dict(nx=192, ny=161, label="m0/8"),
    dict(nx=288, ny=241, label="m0/12"),
]

# Fixed seed so the unstructured mesh (and thus the report) is reproducible.
SEED = 20260620
JITTER = 0.22  # interior node displacement as a fraction of grid spacing


def build_unstructured_delaunay(nx: int, ny: int, Lx: float, Ly: float,
                                jitter: float, seed: int):
    """Return (pos, node_type, cells) for an unstructured Delaunay mesh on
    [0, Lx] x [-Ly, Ly]. Boundary nodes stay exactly on the domain edges; only
    interior nodes are jittered, so the domain stays a clean rectangle while the
    connectivity becomes unstructured."""
    xs = np.linspace(0.0, Lx, nx)
    ys = np.linspace(-Ly, Ly, ny)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    pos = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float64)

    i_idx = np.repeat(np.arange(nx), ny)
    j_idx = np.tile(np.arange(ny), nx)
    on_left, on_right = i_idx == 0, i_idx == nx - 1
    on_bottom, on_top = j_idx == 0, j_idx == ny - 1
    interior = ~(on_left | on_right | on_bottom | on_top)

    rng = np.random.default_rng(seed)
    dx = Lx / (nx - 1)
    dy = (2.0 * Ly) / (ny - 1)
    k = int(interior.sum())
    pos[interior, 0] += (rng.random(k) - 0.5) * 2.0 * jitter * dx
    pos[interior, 1] += (rng.random(k) - 0.5) * 2.0 * jitter * dy

    # node_type, matching the structured convention so interior_cell_mask with
    # interior_types=(0, 5) selects the same kind of bulk cells: WALL first,
    # then INFLOW/OUTFLOW win at the left/right corners (as in build_symmetric_channel).
    node_type = np.full(pos.shape[0], NODE_NORMAL, dtype=np.int32)
    node_type[on_top | on_bottom] = NODE_WALL
    node_type[on_left] = NODE_INFLOW
    node_type[on_right] = NODE_OUTFLOW

    cells = Delaunay(pos).simplices.astype(np.int32)
    return pos, node_type, cells


def min_triangle_angle_deg(pos: np.ndarray, cells: np.ndarray) -> float:
    """Worst (smallest) interior angle over all triangles, in degrees -- a mesh
    quality summary so a degenerate-sliver explanation of any floor inflation is
    auditable."""
    p = pos[cells]
    out = []
    for a, b, c in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        v1 = p[:, b] - p[:, a]
        v2 = p[:, c] - p[:, a]
        cosang = np.sum(v1 * v2, axis=1) / (
            np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1) + 1e-30)
        out.append(np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0))))
    return float(np.min(np.stack(out)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--outdir",
        default=str(ROOT / "research_assets/runs/operator-floor-sweep-mesh2"))
    ap.add_argument(
        "--structured-report",
        default=str(ROOT / "research_assets/runs/operator-floor-sweep-extended/"
                          "operator_floor_extended_report.json"))
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    records = []
    for lv in LEVELS:
        pos, node_type, cells = build_unstructured_delaunay(
            lv["nx"], lv["ny"], Lx, Ly, JITTER, SEED)
        vel = analytic_velocity(pos)
        h = char_length(pos, cells)
        rms_all = divergence_rms(pos, cells, vel)
        mask = interior_cell_mask(cells, node_type, interior_types=(0, 5))
        rms_interior = divergence_rms(pos, cells, vel, mask=mask)
        min_ang = min_triangle_angle_deg(pos, cells)
        records.append({
            "level": lv["label"], "nx": lv["nx"], "ny": lv["ny"],
            "num_nodes": int(pos.shape[0]), "num_cells": int(cells.shape[0]),
            "h_rms_edge": h,
            "divergence_rms_all": rms_all,
            "divergence_rms_interior": rms_interior,
            "interior_cell_count": int(mask.sum()),
            "min_triangle_angle_deg": min_ang,
        })
        print(f"  {lv['label']:7s} nodes={pos.shape[0]:6d} cells={cells.shape[0]:6d} "
              f"h={h:.4g} rms_all={rms_all:.4g} rms_int={rms_interior:.4g} "
              f"min_ang={min_ang:.1f}deg")

    logh = np.array([np.log(r["h_rms_edge"]) for r in records])
    fit_all = linfit_ci(logh, np.array(
        [np.log(r["divergence_rms_all"]) for r in records]))
    fit_int = linfit_ci(logh, np.array(
        [np.log(r["divergence_rms_interior"]) for r in records]))

    # Cross-topology comparison: at each unstructured level, find the
    # structured-sweep level with the nearest h and take the floor RMS ratio.
    cross = {"available": False}
    sref = Path(args.structured_report)
    if sref.exists():
        sdata = json.loads(sref.read_text(encoding="utf-8"))
        s_levels = sdata["levels"]
        s_h = np.array([lv["h_rms_edge"] for lv in s_levels])
        pairs = []
        for r in records:
            k = int(np.argmin(np.abs(np.log(s_h) - np.log(r["h_rms_edge"]))))
            sl = s_levels[k]
            ratio_all = r["divergence_rms_all"] / sl["divergence_rms_all"]
            ratio_int = r["divergence_rms_interior"] / sl["divergence_rms_interior"]
            pairs.append({
                "unstructured_level": r["level"], "unstructured_h": r["h_rms_edge"],
                "matched_structured_level": sl["level"], "structured_h": sl["h_rms_edge"],
                "rms_all_ratio_unstruct_over_struct": ratio_all,
                "rms_interior_ratio_unstruct_over_struct": ratio_int,
            })
        ratios_all = [p["rms_all_ratio_unstruct_over_struct"] for p in pairs]
        ratios_int = [p["rms_interior_ratio_unstruct_over_struct"] for p in pairs]
        cross = {
            "available": True,
            "structured_report": str(sref.relative_to(ROOT)),
            "structured_slope_all": sdata["fit_all_cells"]["slope"],
            "structured_slope_interior": sdata["fit_interior_only"]["slope"],
            "matched_pairs": pairs,
            "rms_all_ratio_max": float(np.max(ratios_all)),
            "rms_all_ratio_median": float(np.median(ratios_all)),
            "rms_interior_ratio_max": float(np.max(ratios_int)),
            "rms_interior_ratio_median": float(np.median(ratios_int)),
        }

    slope_first_order = 0.85 <= fit_all["slope"] <= 1.15
    ratio_same_order = (not cross["available"]) or (cross["rms_all_ratio_max"] <= 3.0)
    topology_stable = slope_first_order and ratio_same_order

    report = {
        "experiment_id": "EXT2-operator-floor-cross-topology",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "purpose": (
            "Re-measure the P1 discrete-divergence operator floor on a SECOND, "
            "unstructured Delaunay mesh topology to test whether the calibrated "
            "floor magnitude and the O(h) numerical-decidability verdict are "
            "topology-stable (cross-topology evidence for the admissibility "
            "predicate, bounded to two topologies)."),
        "mesh_topology": (
            "unstructured Delaunay triangulation of a jittered structured grid "
            f"(seed={SEED}, jitter={JITTER} of grid spacing) on [0,Lx]x[-Ly,Ly]; "
            "boundary nodes fixed on domain edges, interior nodes jittered"),
        "analytic_reference": {
            "stream_function": "psi(x,y) = sin(pi x / Lx) * sin(pi y / Ly)",
            "velocity": "u = (psi_y, -psi_x); div(u) = 0 analytically",
            "Lx": Lx, "Ly": Ly,
        },
        "operator": "P1 constant-per-cell divergence (tools.conservation_rubric.cell_divergence)",
        "norm": "area-weighted RMS",
        "levels": records,
        "fit_all_cells": fit_all,
        "fit_interior_only": fit_int,
        "cross_topology_vs_structured": cross,
        "topology_stability": {
            "slope_first_order": slope_first_order,
            "rms_same_order_max_ratio_le_3": ratio_same_order,
            "topology_stable": topology_stable,
        },
        "verdict": ("operator-floor-topology-stable"
                    if topology_stable else "operator-floor-topology-sensitive"),
        "honesty_boundary": (
            "Two specific mesh topologies (structured y=0-symmetric triangular "
            "channel + unstructured Delaunay), one smooth analytic field, one "
            "domain. This is bounded cross-topology evidence for the "
            "admissibility-predicate operator floor; it is NOT a generalization "
            "claim across arbitrary mesh families or geometries, and NOT a "
            "closed-form bound for unstructured meshes (that remains future "
            "work; cf. C32)."),
    }
    (outdir / "operator_floor_mesh2_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nunstructured fit (all cells): slope={fit_all['slope']:.4f} "
          f"95% CI=[{fit_all['slope_ci95'][0]:.4f}, {fit_all['slope_ci95'][1]:.4f}] "
          f"R^2={fit_all['r_squared']:.6f}")
    if cross["available"]:
        print(f"cross-topology RMS ratio (unstruct/struct): "
              f"median={cross['rms_all_ratio_median']:.3f} "
              f"max={cross['rms_all_ratio_max']:.3f} "
              f"(structured slope {cross['structured_slope_all']:.3f})")
    print(f"verdict: {report['verdict']}")
    print(f"wrote {outdir/'operator_floor_mesh2_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
