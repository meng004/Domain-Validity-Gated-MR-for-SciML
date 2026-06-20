"""EXT (path B) guard: PINN end-to-end seeded-fault detection (claim C46).

Verifies the by-class detection structure and the genuine blind region behind
claim C46 on the fourth (pointwise PINN) architecture family:
  - the report exists, covers 4 faults over K=6 Burgers PINN SUTs;
  - by-class localization matches the design (scale -> conservation; odd-in-y
    bias -> mirror; upper-half offset -> both; cos(pi x) -> neither);
  - the blind-spot fault is undetected at full strength and across the sweep,
    while genuinely degrading the field;
  - three of four faults are detected by at least one MR;
  - no "superiority" framing leaks; the ledger C46 entry references the run and
    keeps the no-generalization / no-real-world-rate boundary.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/pinn-seeded-fault-detection/pinn_seeded_fault_report.json"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"

EXPECTED_CLASS = {
    "scale_ux": "conservation",
    "asym_y_ux": "mirror",
    "upper_half_offset": "both",
    "cos_x_blind": "none",
}


def _load():
    assert REPORT.exists(), f"missing PINN seeded-fault report: {REPORT}"
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_report_shape():
    rep = _load()
    assert rep["trained_sut_count"] == 6
    assert set(rep["per_fault"].keys()) == set(EXPECTED_CLASS)
    for pf in rep["per_fault"].values():
        assert pf["n_suts"] == 6


def test_by_class_localization_matches_design():
    rep = _load()
    for fault, expected in EXPECTED_CLASS.items():
        got = rep["per_fault"][fault]["by_class_localization"]
        assert got == expected, f"{fault}: expected {expected}, got {got}"


def test_detected_faults_localize_strongly():
    rep = _load()
    for fault in ("scale_ux", "asym_y_ux", "upper_half_offset"):
        assert rep["per_fault"][fault]["detection_rate"] == 1.0, fault
    assert rep["union_detection"]["faults_detected_majority"] == 3


def test_blind_spot_is_genuinely_blind():
    rep = _load()
    blind = rep["per_fault"]["cos_x_blind"]
    assert blind["detection_rate"] == 0.0
    assert blind["detected_by_mirror"] == 0
    assert blind["detected_by_conservation"] == 0
    assert rep["blind_spot"]["detected_across_severity_sweep"] is False
    perturbs = [sw["output_perturbation_rel_l2"]
                for s in rep["per_sut"] for sw in s["blind_severity_sweep"]]
    assert max(perturbs) > 0.05  # it is a real fault, not a no-op


def test_no_superiority_and_ledger_boundary():
    rep = _load()
    blob = json.dumps(rep).lower()
    for banned in ("outperform", "better than"):
        assert banned not in blob, banned
    assert "baseline-superiority" in blob  # the no-superiority disclaimer is present
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "C46-pinn-seeded-fault-detection" in ledger
    assert "pinn-seeded-fault-detection/pinn_seeded_fault_report.json" in ledger
    assert "not proven general" in ledger
