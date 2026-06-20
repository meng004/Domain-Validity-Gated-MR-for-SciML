"""EXT-3 guard: cross-architecture validity-coverage duality synthesis (claim C47).

Verifies that the duality's two qualitative falsifiable predictions reproduce on
all four committed architecture families:
  - the report exists and covers MeshGraphNets, PointMLP, FNO, PINN;
  - on every family P1 (coverage partitioned across >=2 admitted-MR invariants)
    and P2 (>=1 structural blind fault) both hold;
  - duality_reproduces_on_all_families is True;
  - no superiority framing; the ledger C47 entry references the run and keeps the
    qualitative / no-validated-coverage-model boundary.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/cross-architecture-duality/cross_architecture_duality_report.json"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"

FAMILIES = {"MeshGraphNets", "PointMLP", "FNO-2D", "PINN"}


def _load():
    assert REPORT.exists(), f"missing cross-architecture duality report: {REPORT}"
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_covers_four_architecture_families():
    rep = _load()
    assert set(rep["per_architecture"].keys()) == FAMILIES
    assert rep["summary"]["architecture_families"] == 4


def test_duality_holds_on_every_family():
    rep = _load()
    for fam, sig in rep["per_architecture"].items():
        assert sig["duality_P1_coverage_partitioned_by_admitted_MR"] is True, fam
        assert sig["duality_P2_structural_blind_region"] is True, fam
        assert sig["duality_holds"] is True, fam
        # P1: at least two admitted-MR invariants carry coverage
        assert len(sig["coverage_by_invariant"]) >= 2, fam
        # P2: at least one structural blind fault
        assert sig["num_blind_faults"] >= 1, fam
    assert rep["summary"]["families_where_duality_holds"] == 4
    assert rep["summary"]["duality_reproduces_on_all_families"] is True


def test_no_superiority_and_ledger_boundary():
    rep = _load()
    blob = json.dumps(rep).lower()
    for banned in ("outperform", "better than"):
        assert banned not in blob, banned
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "C47-cross-architecture-coverage-duality" in ledger
    assert "cross-architecture-duality/cross_architecture_duality_report.json" in ledger
    # the qualitative / no-validated-model boundary must remain explicit
    assert "qualitative falsifiable principle reproduced on four committed families" in ledger
