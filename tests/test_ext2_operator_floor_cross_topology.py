"""EXT-2 guard: cross-topology operator-floor sweep (unstructured Delaunay).

Verifies the bounded cross-topology evidence behind claim C44:
  - the unstructured-mesh report exists and covers at least 8 resolutions;
  - the fitted slope is first-order (within [0.85, 1.15]) with CI fields, so the
    numerical-decidability verdict does not flip on the second topology;
  - the fit is recomputable from the per-level (h, RMS) data;
  - the cross-topology floor-magnitude ratio vs the structured sweep is the same
    order (max <= 3.0) and the report's topology_stable verdict agrees;
  - the claim ledger C44 entry references this run and keeps the
    no-generalization / no-closed-form-bound boundary.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/operator-floor-sweep-mesh2/operator_floor_mesh2_report.json"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


def _load():
    assert REPORT.exists(), f"missing mesh2 report: {REPORT}"
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_report_exists_with_at_least_8_resolutions():
    rep = _load()
    levels = rep["levels"]
    assert len(levels) >= 8, f"expected >=8 resolutions, got {len(levels)}"
    hs = [lv["h_rms_edge"] for lv in levels]
    assert all(h > 0 for h in hs)
    assert len(set(round(h, 12) for h in hs)) == len(hs)
    for lv in levels:
        assert lv["divergence_rms_all"] > 0
        assert lv["divergence_rms_interior"] > 0
        # mesh quality is auditable: no degenerate slivers explaining the floor
        assert lv["min_triangle_angle_deg"] > 5.0


def test_unstructured_slope_first_order_with_ci():
    rep = _load()
    for key in ("fit_all_cells", "fit_interior_only"):
        fit = rep[key]
        assert 0.85 <= fit["slope"] <= 1.15, f"{key} slope={fit['slope']}"
        assert fit["slope_se"] > 0
        lo, hi = fit["slope_ci95"]
        assert lo < fit["slope"] < hi
        assert fit["dof"] == fit["n_points"] - 2
        assert fit["n_points"] == len(rep["levels"])
        assert fit["r_squared"] > 0.99


def test_fit_recomputable_from_levels():
    rep = _load()
    logh = np.array([np.log(lv["h_rms_edge"]) for lv in rep["levels"]])
    for key, field in (("fit_all_cells", "divergence_rms_all"),
                       ("fit_interior_only", "divergence_rms_interior")):
        logr = np.array([np.log(lv[field]) for lv in rep["levels"]])
        n = len(logh)
        mx, my = logh.mean(), logr.mean()
        sxx = float(np.sum((logh - mx) ** 2))
        slope = float(np.sum((logh - mx) * (logr - my)) / sxx)
        assert abs(slope - rep[key]["slope"]) < 1e-10


def test_cross_topology_same_order_and_verdict():
    rep = _load()
    cross = rep["cross_topology_vs_structured"]
    assert cross["available"], "structured comparison must be available"
    # floor magnitude stays the same order across the two topologies
    assert cross["rms_all_ratio_max"] <= 3.0, cross["rms_all_ratio_max"]
    # structured and unstructured slopes are both O(h)
    assert 0.85 <= cross["structured_slope_all"] <= 1.15
    stab = rep["topology_stability"]
    assert stab["slope_first_order"] is True
    assert stab["rms_same_order_max_ratio_le_3"] is True
    assert stab["topology_stable"] is True
    assert rep["verdict"] == "operator-floor-topology-stable"


def test_ledger_c44_reference_and_boundary():
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "C44-operator-floor-cross-topology" in ledger
    assert "operator-floor-sweep-mesh2/operator_floor_mesh2_report.json" in ledger
    # the no-generalization / no-closed-form-bound boundary must remain explicit
    assert "closed-form bound or a general unstructured-mesh guarantee" in ledger
    rep = _load()
    hb = rep["honesty_boundary"]
    assert "two specific mesh topologies" in hb.lower()
    assert "NOT a generalization" in hb
