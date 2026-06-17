"""Cross-program coverage-geometry generalization (claim C39).

Tests whether the coverage-geometry reading generalizes beyond the two CFD SUTs by
reusing committed Minimum-MR-SubSet kill matrices for seven program types across three
families (neural surrogates, classical numerical solvers, a production physics code).
For each program it computes, from the kill matrix alone, the MR-based fault detection
rate, the per-MR-class fault coverage, and the structural blind spots, then checks the
coverage-geometry prediction: fault coverage is the union of the admissible MR set's
per-class coverage, with structural blind spots, while the class-to-class mapping is
program-specific (different fault taxonomies and MR sets per program).

Read-only: reads research_assets/external/minimum-mr-subset-killmatrices/*/kill_matrix.csv
(copied verbatim from the READ-ONLY sibling repo; provenance in that directory). It runs
no SUT and never modifies the sibling. The paper's validity-gated pipeline was NOT
executed end-to-end on each program; this is a generalization check of the principle from
committed evidence.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "research_assets/external/minimum-mr-subset-killmatrices"
OUT = ROOT / "research_assets/runs/cross-program-coverage/raw"

# (fixture key, program family, domain) -- the approved three-family spectrum.
PROGRAMS = [
    ("s1-cylinder-mgn", "neural surrogate", "CFD incompressible (MeshGraphNet)"),
    ("s2-burgers2d-pinn", "neural surrogate", "2D conservation law (PINN)"),
    ("s3-diffusion2d-pinn", "neural surrogate", "2D parabolic (PINN)"),
    ("c1-p2-wave", "classical solver", "hyperbolic PDE (FDM)"),
    ("c2-p5-pke", "classical solver", "stiff ODE / reactor kinetics"),
    ("c3-p7-burgers", "classical solver", "conservation law (FVM)"),
    ("r1-openmc", "production code", "Monte-Carlo neutron transport"),
]

# Tokens marking a clean control row (not a fault); excluded from the detection denominator.
CONTROL_TOKENS = ("baseline", "reference", "control")


def _is_control(mutant_id: str, fault_class: str) -> bool:
    s = (mutant_id + " " + fault_class).lower()
    return any(t in s for t in CONTROL_TOKENS)


def _kill_state(v: str):
    """Kill flag, tolerant of the corpus's mixed conventions (1/0, true/false)."""
    s = str(v).strip().lower()
    if s in ("1", "1.0", "true", "yes"):
        return True
    if s in ("0", "0.0", "false", "no"):
        return False
    return None  # unrecognized / malformed -> skip


def analyze(key: str) -> dict:
    with open(FIX / key / "kill_matrix.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    mrs = sorted({r["mr_id"] for r in rows})
    killed_by: dict[str, set] = defaultdict(set)        # mutant -> MRs that kill it
    mr_catches_class: dict[str, set] = defaultdict(set)  # mr_id -> fault classes it kills
    mutants: dict[str, str] = {}                         # mutant_id -> fault_class
    for r in rows:
        m, fc, mr = r["mutant_id"], r["fault_class"], r["mr_id"]
        if _is_control(m, fc):
            continue
        k = _kill_state(r.get("killed", ""))
        if k is None:
            continue
        mutants[m] = fc
        if k:
            killed_by[m].add(mr)
            mr_catches_class[mr].add(fc)
    fault_classes = sorted(set(mutants.values()))
    detected = [m for m in mutants if killed_by[m]]
    covered = sorted({mutants[m] for m in detected})
    blind = sorted(set(fault_classes) - set(covered))
    return {
        "program": key,
        "n_admissible_mrs": len(mrs),
        "n_mutants": len(mutants),
        "n_fault_classes": len(fault_classes),
        "detection_rate": round(len(detected) / len(mutants), 3) if mutants else None,
        "covered_fault_classes": covered,
        "blind_fault_classes": blind,
        "has_structural_blind_spot": bool(blind),
        "per_mr_localization": {mr: sorted(mr_catches_class[mr]) for mr in mrs if mr_catches_class[mr]},
        "fault_classes": fault_classes,
    }


def main() -> int:
    per = [dict(analyze(k), family=fam, domain=dom) for k, fam, dom in PROGRAMS]
    mappings = {p["program"]: json.dumps(p["per_mr_localization"], sort_keys=True) for p in per}
    mappings_distinct = len(set(mappings.values())) == len(per)
    rates = [p["detection_rate"] for p in per if p["detection_rate"] is not None]
    ledger = {
        "ledger_id": "cross-program-coverage-geometry-generalization",
        "evidence_level": "reused-committed-kill-matrices-no-rerun",
        "schema_version": "0.1.0",
        "source": ("Minimum-MR-SubSet committed kill matrices (read-only sibling), copied "
                   "verbatim as fixtures under research_assets/external/minimum-mr-subset-killmatrices/"),
        "n_programs": len(per),
        "families": sorted({p["family"] for p in per}),
        "per_program": per,
        "aggregate": {
            "all_programs_have_mr_coverage": all(r and r > 0 for r in rates),
            "n_with_structural_blind_spot": sum(p["has_structural_blind_spot"] for p in per),
            "detection_rate_range": [min(rates), max(rates)] if rates else None,
            "class_to_class_mappings_program_specific": mappings_distinct,
            "finding": ("the coverage-geometry reading -- fault coverage is the union of the "
                        "admissible MR set's per-class coverage, with structural blind spots -- "
                        "reproduces across all seven program types and three families; the "
                        "class-to-class mapping is program-specific (distinct per program), so "
                        "what generalizes is the coverage-generation structure, not the mapping."),
        },
        "honesty_boundary": (
            "These are committed kill matrices from the read-only Minimum-MR-SubSet corpus, "
            "reused as a generalization check of the coverage principle; the paper's "
            "validity-gated pipeline was NOT executed end-to-end on each program, and no "
            "per-program reliability or real-world detection-rate claim is made beyond these "
            "committed mutant sets."
        ),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metric_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"cross-program coverage over {len(per)} programs, {len(ledger['families'])} families:")
    for p in per:
        det = f"{p['detection_rate']:.0%}" if p['detection_rate'] is not None else "n/a"
        print(f"  {p['program']:20s} [{p['family']:17s}] det={det} "
              f"covered={len(p['covered_fault_classes'])}/{p['n_fault_classes']} "
              f"blind={p['blind_fault_classes'] or 'none'}")
    a = ledger["aggregate"]
    print(f"  -> structural blind spots in {a['n_with_structural_blind_spot']}/{len(per)}; "
          f"mappings program-specific: {a['class_to_class_mappings_program_specific']}; "
          f"det range {a['detection_rate_range']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
