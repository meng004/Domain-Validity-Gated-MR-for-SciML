"""Operationalize the domain-violation axis of the two-dimensional verdict as a
continuous score D in [0, 1), from already-committed geometric precondition
measurements (no new experiment).

Reviewer concern (panel, 2026-06-08): the domain-violation axis of the
two-dimensional verdict is only qualitatively binned. This script turns the
*existing* committed geometric admissibility measurements for the mirror-y
relation into a single continuous inadmissibility score, so the cases the paper
already places qualitatively on the verdict plane get a real coordinate.

Definition. For the mirror-y relation on a mesh, let m be the worst
reflected-node placement error in units of the median edge length (0 = a
reflected node lands exactly on an existing node, i.e. the reflection is
admissible; 1 = it lands one edge length away). The domain-violation score is
the saturating map

    D = m / (m + 1)        in [0, 1),  D = 0.5 at one edge length.

Sources (committed):
  - Real asymmetric eval mesh: m = max_nn_over_edge from the mirror-y OOD-stress
    precondition report (nearest existing node to each reflected node, in edge
    units).
  - Synthetic symmetric admissible mesh: m = reflection_offset_max /
    median_edge_length from the symmetric-mesh metric ledger (the involution
    offset; ~machine epsilon).

This is deliberately a single-relation, geometry-only operationalization; a
calibrated continuous score across all MR classes remains future work.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REAL_PRECOND = ROOT / "research_assets/runs/mirror-y-rate-upgrade/raw/precondition_report.json"
SYM_LEDGER = ROOT / "research_assets/runs/mirror-y-symmetric-mesh/raw/metric_ledger.json"
OUT = ROOT / "research_assets/runs/domain-violation-score/domain_violation_report.json"


def saturating(m: float) -> float:
    return m / (m + 1.0)


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    real = json.loads(REAL_PRECOND.read_text())
    sym = json.loads(SYM_LEDGER.read_text())["precondition_report"]

    # Real asymmetric eval mesh.
    m_real = float(real["max_nn_over_edge"])
    D_real = saturating(m_real)

    # Synthetic symmetric admissible mesh: offset is absolute; normalize by the
    # real mesh median edge length as a common length scale (the symmetric mesh
    # offset is ~1e-17, so any positive edge scale yields D ~ 0).
    edge = float(real["median_edge_length"])
    m_sym = float(sym["reflection_offset_max"]) / edge
    D_sym = saturating(m_sym)

    report = {
        "record_type": "domain-violation-score",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "definition": "D = m/(m+1), m = worst reflected-node placement error in median-edge-length units",
        "relation": "mirror-y equivariance",
        "cases": {
            "node_permutation_relation": {
                "m_edge_units": 0.0, "D": 0.0,
                "note": "permutation has no geometric precondition to violate; admissible by construction",
            },
            "mirror_y_synthetic_symmetric_mesh": {
                "m_edge_units": m_sym, "D": D_sym,
                "bijection": sym.get("bijection"),
                "node_type_match_rate": sym.get("node_type_match_rate"),
                "verdict_region": "low-domain-violation: a violation here reads as SUT inconsistency",
            },
            "mirror_y_real_asymmetric_mesh": {
                "m_edge_units": m_real, "D": D_real,
                "bijection": real.get("bijection"),
                "cylinder_offset_from_axis": real.get("cylinder", {}).get("offset_from_axis")
                if isinstance(real.get("cylinder"), dict) else None,
                "verdict_region": "high-domain-violation: out-of-relation-domain / OOD-stress",
            },
        },
        "honesty_boundary": (
            "Single-relation (mirror-y), geometry-only continuous score from "
            "committed precondition measurements. Not a calibrated cross-MR-class "
            "domain-violation metric; that remains future work."),
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  D(node-perm)            = 0.000")
    print(f"  D(symmetric admissible) = {D_sym:.3g}  (m={m_sym:.3g} edge units)")
    print(f"  D(real asymmetric mesh) = {D_real:.3f}  (m={m_real:.4f} edge units)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
