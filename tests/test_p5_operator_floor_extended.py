"""P5 guard: extended operator-floor sweep (>=8 resolutions, slope CI).

Verifies the reviewer-response artifact for P1-5 ("R^2=1.000 over only four
resolutions, no slope confidence interval"):
  - the extended report exists and covers at least 8 resolutions;
  - the fitted slope is first-order (within [0.9, 1.1]) with CI fields present;
  - the reported fit is recomputable from the per-level (h, RMS) data;
  - the claim ledger C12 entry references the extended run.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/operator-floor-sweep-extended/operator_floor_extended_report.json"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


def _load():
    assert REPORT.exists(), f"missing extended report: {REPORT}"
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_report_exists_with_at_least_8_resolutions():
    rep = _load()
    levels = rep["levels"]
    assert len(levels) >= 8, f"expected >=8 resolutions, got {len(levels)}"
    hs = [lv["h_rms_edge"] for lv in levels]
    assert all(h > 0 for h in hs)
    # strictly distinct resolutions
    assert len(set(round(h, 12) for h in hs)) == len(hs)
    for lv in levels:
        assert lv["divergence_rms_all"] > 0
        assert lv["divergence_rms_interior"] > 0


def test_slope_first_order_with_ci_fields():
    rep = _load()
    for key in ("fit_all_cells", "fit_interior_only"):
        fit = rep[key]
        assert 0.9 <= fit["slope"] <= 1.1, f"{key} slope={fit['slope']}"
        assert fit["slope_se"] > 0
        lo, hi = fit["slope_ci95"]
        assert lo < fit["slope"] < hi
        assert fit["dof"] == fit["n_points"] - 2
        assert fit["n_points"] == len(rep["levels"])
        assert fit["r_squared"] > 0.999


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
        resid = logr - (slope * logh + (my - slope * mx))
        se = float(np.sqrt(float(np.sum(resid ** 2)) / (n - 2) / sxx))
        fit = rep[key]
        assert abs(slope - fit["slope"]) < 1e-10
        assert abs(se - fit["slope_se"]) < 1e-10
        half = fit["t_975"] * se
        assert abs((fit["slope_ci95"][1] - fit["slope_ci95"][0]) / 2 - half) < 1e-10


def test_honesty_boundary_and_ledger_reference():
    rep = _load()
    hb = rep["honesty_boundary"]
    assert "mesh family" in hb and "NOT a generalization" in hb
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "operator-floor-sweep-extended/operator_floor_extended_report.json" in ledger
    assert "closed-form bound" in ledger
