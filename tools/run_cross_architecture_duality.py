"""EXT-3: cross-architecture synthesis of the validity-coverage duality.

The validity-coverage duality (the admissibility gate that decides whether an MR
yields a meaningful verdict also fixes which faults that MR can detect) was first
read on the MeshGraphNets cylinder/airfoil pair. This script aggregates the four
already-committed end-to-end seeded-fault reports --- MeshGraphNets, PointMLP,
FNO, PINN --- and checks, by reading each report (no new model runs), whether the
duality's two QUALITATIVE, falsifiable predictions reproduce on every one of the
four architecture families:

  P1 (coverage follows the admitted MR set): detected faults localize by class to
     the MR that measures the perturbed invariant, and at least two distinct MRs
     cover distinct fault classes -- coverage is the union of per-MR per-class
     coverage, not a single uniform detector.
  P2 (a structural blind region exists): at least one fault preserves all of the
     suite's measured invariants and is therefore detected by no MR.

This is a synthesis over committed artifacts; it strengthens the duality from two
CFD SUTs to four architecture families but remains a qualitative, falsifiable
organizing principle -- NOT a validated or quantitative predictive coverage
model, and NOT proven for all MRs or architectures.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "research_assets/runs/cross-architecture-duality"

REPORTS = {
    "MeshGraphNets": ("research_assets/runs/seeded-fault-detection/raw/metric_ledger.json", "matrix"),
    "PointMLP": ("research_assets/runs/pointmlp-cylinder-seeded-fault-detection/raw/metric_ledger.json", "matrix"),
    "FNO-2D": ("research_assets/runs/fno-seeded-fault-detection/fno_seeded_fault_report.json", "byfault"),
    "PINN": ("research_assets/runs/pinn-seeded-fault-detection/pinn_seeded_fault_report.json", "byfault"),
}


def _detector_names(raw) -> list[str]:
    return list(raw.keys()) if isinstance(raw, dict) else list(raw)


def extract_matrix(d: dict) -> dict:
    """Normalize a MeshGraphNets/PointMLP detection_matrix report."""
    detectors = _detector_names(d["detectors"])
    dm = d["detection_matrix"]
    mr_keys = [k for k in dm[0] if k.endswith("_MR_detects")]
    by_invariant: dict[str, set] = {}
    detected = blind = 0
    blind_faults = []
    for row in dm:
        if row.get("applicable", True) is False:
            continue
        if row["detected_by_any"]:
            detected += 1
            for mk in mr_keys:
                if row[mk]:
                    by_invariant.setdefault(mk.replace("_MR_detects", ""), set()).add(row["fault_class"])
        else:
            blind += 1
            blind_faults.append(row["mutant"])
    return _signature(detectors, by_invariant, detected, blind, blind_faults,
                      d.get("summary", {}).get("union_detection_rate"))


def extract_byfault(d: dict) -> dict:
    """Normalize an FNO/PINN per_fault report."""
    detectors = _detector_names(d["detectors"])
    by_invariant: dict[str, set] = {}
    detected = blind = 0
    blind_faults = []
    both_faults = []
    for fault, pf in d["per_fault"].items():
        loc = pf["by_class_localization"]
        if loc == "none":
            blind += 1
            blind_faults.append(fault)
        elif loc == "both":
            detected += 1
            both_faults.append(fault)        # detected by both MRs; assigned below
        else:
            detected += 1
            by_invariant.setdefault(loc, set()).add(fault)
    # a "both" fault is detected by every single-invariant detector present
    for fault in both_faults:
        for inv in list(by_invariant):
            by_invariant[inv].add(fault)
    ud = d["union_detection"]
    return _signature(detectors, by_invariant, detected, blind, blind_faults,
                      ud["faults_detected_majority"] / ud["faults_total"])


def _signature(detectors, by_invariant, detected, blind, blind_faults, union_rate) -> dict:
    invariants_with_coverage = {k: sorted(v) for k, v in by_invariant.items() if v}
    # P1: coverage is partitioned across >=2 distinct invariants
    p1_partitioned = len(invariants_with_coverage) >= 2
    # P2: at least one structural blind fault (detected by no MR)
    p2_blind_region = blind >= 1
    return {
        "detectors": detectors,
        "coverage_by_invariant": invariants_with_coverage,
        "num_detected_faults": detected,
        "num_blind_faults": blind,
        "blind_faults": blind_faults,
        "union_detection_rate": union_rate,
        "duality_P1_coverage_partitioned_by_admitted_MR": p1_partitioned,
        "duality_P2_structural_blind_region": p2_blind_region,
        "duality_holds": bool(p1_partitioned and p2_blind_region),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(OUT_DIR))
    args = ap.parse_args(argv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    per_arch = {}
    for family, (rel, schema) in REPORTS.items():
        path = ROOT / rel
        if not path.exists():
            raise FileNotFoundError(f"missing seeded-fault report for {family}: {path}")
        d = json.loads(path.read_text(encoding="utf-8"))
        sig = extract_matrix(d) if schema == "matrix" else extract_byfault(d)
        sig["report"] = rel
        per_arch[family] = sig
        print(f"  {family:14s} detectors={len(sig['detectors'])} "
              f"invariants_covering={len(sig['coverage_by_invariant'])} "
              f"blind={sig['num_blind_faults']} "
              f"P1={sig['duality_P1_coverage_partitioned_by_admitted_MR']} "
              f"P2={sig['duality_P2_structural_blind_region']} "
              f"holds={sig['duality_holds']}", flush=True)

    n = len(per_arch)
    n_hold = sum(s["duality_holds"] for s in per_arch.values())
    report = {
        "record_type": "cross-architecture-validity-coverage-duality",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "purpose": (
            "Aggregate four committed end-to-end seeded-fault reports and check "
            "whether the validity-coverage duality's two qualitative falsifiable "
            "predictions (coverage follows the admitted MR set; a structural blind "
            "region exists) reproduce on every architecture family."),
        "architecture_families": list(per_arch.keys()),
        "per_architecture": per_arch,
        "duality_predictions": {
            "P1_coverage_partitioned_by_admitted_MR": "detected faults localize by class to the measuring MR, with >=2 distinct invariants covering distinct fault classes",
            "P2_structural_blind_region": "at least one fault preserves all measured invariants and evades every MR",
        },
        "summary": {
            "architecture_families": n,
            "families_where_duality_holds": n_hold,
            "duality_reproduces_on_all_families": bool(n_hold == n),
            "statement": (
                f"The validity-coverage duality's two qualitative predictions reproduce "
                f"on {n_hold}/{n} architecture families (MeshGraphNets, PointMLP, FNO, PINN)."),
        },
        "honesty_boundary": (
            "Synthesis over committed seeded-fault artifacts (no new model runs). "
            "The duality remains a qualitative, falsifiable organizing principle "
            "strengthened from two CFD SUTs to four architecture families; it is "
            "NOT a validated or quantitative predictive coverage model, NOT proven "
            "for all MRs or architectures, and asserts no fault-detection rate or "
            "baseline superiority."),
    }
    (outdir / "cross_architecture_duality_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\n{report['summary']['statement']}")
    print(f"wrote {(outdir / 'cross_architecture_duality_report.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
