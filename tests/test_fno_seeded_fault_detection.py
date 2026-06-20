"""EXT (path B) guard: FNO end-to-end seeded-fault detection (claim C45).

Verifies the by-class detection structure and the genuine blind region behind
claim C45:
  - the report exists, covers 5 faults over 24 cells each (K=6 x 4 cases);
  - by-class localization matches the design (scale/offset -> conservation;
    zero-sum asymmetry -> translation; nonzero asymmetry -> both;
    smooth blur -> neither);
  - the blind-spot fault is undetected at full strength AND across the whole
    severity sweep;
  - four of five faults are detected by at least one MR;
  - no "superiority" framing leaks; the ledger C45 entry references the run and
    keeps the no-generalization / no-real-world-rate boundary.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/fno-seeded-fault-detection/fno_seeded_fault_report.json"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"

EXPECTED_CLASS = {
    "global_scale": "conservation",
    "constant_offset": "conservation",
    "asymmetric_zero_sum_bias": "translation",
    "asymmetric_nonzero_bias": "both",
    "transport_shift_blind": "none",
}


def _load():
    assert REPORT.exists(), f"missing FNO seeded-fault report: {REPORT}"
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_report_shape():
    rep = _load()
    assert rep["trained_sut_count"] == 6
    assert set(rep["per_fault"].keys()) == set(EXPECTED_CLASS)
    for pf in rep["per_fault"].values():
        assert pf["n_cells"] == 24  # K=6 x 4 cases


def test_by_class_localization_matches_design():
    rep = _load()
    for fault, expected in EXPECTED_CLASS.items():
        got = rep["per_fault"][fault]["by_class_localization"]
        assert got == expected, f"{fault}: expected {expected}, got {got}"


def test_detected_faults_localize_strongly():
    rep = _load()
    # the four non-blind faults are detected on every cell by their MR(s)
    for fault in ("global_scale", "constant_offset",
                  "asymmetric_zero_sum_bias", "asymmetric_nonzero_bias"):
        assert rep["per_fault"][fault]["detection_rate"] == 1.0, fault
    assert rep["union_detection"]["faults_detected_majority"] == 4


def test_blind_spot_is_genuinely_blind():
    rep = _load()
    blind = rep["per_fault"]["transport_shift_blind"]
    assert blind["detection_rate"] == 0.0
    assert blind["detected_by_translation"] == 0
    assert blind["detected_by_conservation"] == 0
    assert rep["blind_spot"]["detected_across_severity_sweep"] is False
    # the blind fault really does perturb the field (it is a fault, not a no-op)
    perturbs = [sw["output_perturbation_rel_l2"]
                for s in rep["per_sut"] for c in s["cases"]
                for sw in c["blind_severity_sweep"]]
    assert max(perturbs) > 0.05


def test_no_superiority_and_ledger_boundary():
    rep = _load()
    blob = json.dumps(rep).lower()
    # ban positive superiority claims; "baseline-superiority" appears only inside
    # the no-superiority honesty disclaimer, which is allowed.
    for banned in ("outperform", "better than"):
        assert banned not in blob, banned
    assert "baseline-superiority" in blob  # the disclaimer is present
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "C45-fno-seeded-fault-detection" in ledger
    assert "fno-seeded-fault-detection/fno_seeded_fault_report.json" in ledger
    assert "not proven general" in ledger
