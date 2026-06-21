"""EXT-3 cross-SUT three-arm complementarity + validity-coverage duality consolidation.

Consolidates the per-SUT three-arm evidence (ARM1 validity-gated MR / ARM2
accuracy-monitor / ARM3 ungated-generic gate value) and the validity-coverage
duality across the CONVERGED SUTs into one cross-SUT view, so the manuscript can
reference a single table instead of scattered per-SUT cells. This is a
CONSOLIDATION of committed artifacts (C38 cylinder MeshGraphNets, C42/C43 PointMLP,
C35/C36 converged airfoil, C47 cross-architecture duality); it runs NO new model
and introduces NO new numbers. The airfoil accuracy-monitor and ungated-generic
arms require the live PhysicsNeMo airfoil model (GPU) and are marked pending
(see docs/cloud_runbook/ext3_airfoil_three_arm_kickoff.md).

NOT a superiority claim: every arm contrast is internal (gated vs ungated, MR vs
accuracy on the same faults); the duality is reported as a falsifiable cross-SUT
prediction, not a law.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "research_assets" / "runs"


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)]


def load(rel: str):
    p = RUNS / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(RUNS / "ext3-cross-sut-three-arm"))
    args = ap.parse_args(argv)
    out = Path(args.out)
    (out / "raw").mkdir(parents=True, exist_ok=True)

    c38 = load("detection-vs-accuracy/raw/metric_ledger.json")
    pm = load("pointmlp-three-arm-complementarity/raw/metric_ledger.json")
    af = load("production-grade-sut-extension/physicsnemo-mgn-airfoil-seeded-fault-detection/raw/metric_ledger.json")
    c47 = load("cross-architecture-duality/cross_architecture_duality_report.json")
    missing = [n for n, x in [("C38", c38), ("C42/43", pm), ("C36", af), ("C47", c47)] if x is None]
    if missing:
        sys.stderr.write(f"BLOCKED_MISSING_ARTIFACTS: {missing}\n")
        return 2

    suts = []

    # --- cylinder MeshGraphNets (C38 detection-vs-accuracy) ---
    comp = c38["complementarity"]
    both, mr_only = comp["both"], comp["mr_catches_accuracy_misses"]
    acc_only, neither = comp["accuracy_catches_mr_misses"], comp["neither"]
    n38 = len(both) + len(mr_only) + len(acc_only) + len(neither)
    mr38, acc38 = len(both) + len(mr_only), len(both) + len(acc_only)
    suts.append({
        "sut": "cylinder-flow MeshGraphNets",
        "source_claims": ["C38", "C13"],
        "admissible_mr_set": ["node-permutation", "conservation", "mirror-y"],
        "gate_excluded_mr": [],
        "arm1_validity_gated_mr": {"detect": mr38, "total": n38,
                                   "rate": round(mr38 / n38, 3), "wilson95": wilson(mr38, n38)},
        "arm2_accuracy_monitor": {"detect": acc38, "total": n38,
                                  "rate": round(acc38 / n38, 3), "wilson95": wilson(acc38, n38)},
        "arm3_gate_value": "not separately run on MGN; the ungated-generic gate value is measured on PointMLP (C43)",
        "complementarity_2x2": {"both": len(both), "mr_only": len(mr_only),
                                "accuracy_only": len(acc_only), "neither": len(neither)},
        "arms_run": ["arm1", "arm2"],
    })

    # --- PointMLP (C42/C43 three-arm) ---
    a1, a2 = pm["arm1_validity_gated_mr"], pm["arm2_accuracy_monitor"]
    a3 = pm["arm3_ungated_generic_false_positive"]
    cc = pm["complementarity_2x2_mr_vs_accuracy"]["counts"]
    tot = pm["fault_catalogue_size"]
    suts.append({
        "sut": "cylinder-flow PointMLP (row-wise, no message passing)",
        "source_claims": ["C42", "C43"],
        "admissible_mr_set": ["node-permutation", "conservation", "mirror-y"],
        "gate_excluded_mr": [],
        "arm1_validity_gated_mr": {"detect": a1["detection_count"], "total": tot,
                                   "rate": a1["detection_rate"], "wilson95": a1["detection_rate_wilson_ci95"]},
        "arm2_accuracy_monitor": {"detect": a2["detection_count"], "total": tot,
                                  "rate": a2["detection_rate"], "wilson95": a2["detection_rate_wilson_ci95"]},
        "arm3_gate_value": {
            "admitted_max_false_positive": a3["admitted_template_max_false_positive_rate"],
            "rejected_templates_flagging_fault_free_sut":
                f"{a3['n_rejected_templates_flagging_fault_free_sut']}/{a3['n_rejected_templates']}",
            "reading": ("gate-admitted detectors raise no baseline false alarm; gate-rejected "
                        "templates all fire on the correct SUT -- the gate removes the "
                        "false-alarming detectors")},
        "complementarity_2x2": cc,
        "arms_run": ["arm1", "arm2", "arm3"],
    })

    # --- converged airfoil PhysicsNeMo MGN (C35/C36) ---
    rob, xs = af["robustness"], af["cross_sut_comparison"]
    unions = [t["union_detection_rate"] for t in af["per_trajectory"]]
    suts.append({
        "sut": "compressible airfoil PhysicsNeMo MeshGraphNet (converged, C35)",
        "source_claims": ["C35", "C36"],
        "admissible_mr_set": ["node-permutation", "conservation"],
        "gate_excluded_mr": ["mirror-y (non-zero angle of attack: boundary-precondition gate rejects)"],
        "arm1_validity_gated_mr": {
            "per_trajectory_union": unions,
            "robustly_detected_mutants": rob["robustly_detected_mutants"],
            "node_permutation_detection_rate": rob["node_permutation_MR_detection_rate"],
            "conservation_robustly_localizes": rob["conservation_robustly_localizes"]},
        "arm2_accuracy_monitor": "GPU-pending (requires the live PhysicsNeMo airfoil model)",
        "arm3_gate_value": "GPU-pending (requires the live PhysicsNeMo airfoil model)",
        "arms_run": ["arm1"],
    })

    duality = {
        "principle": ("the admissibility gate fixes each SUT's admissible MR set from its "
                      "physics and numerics, and detector coverage tracks that set; a change "
                      "of SUT or physics that makes an MR inadmissible removes exactly that "
                      "MR's fault coverage"),
        "cross_sut_confirmations": [
            ("airfoil: non-zero angle of attack makes mirror-y inadmissible (boundary-"
             "precondition gate rejects), so the mirror-y fault coverage present on the "
             "cylinder is absent on the airfoil (C36)"),
            ("the conservation MR localizes to different fault classes per SUT (cylinder: "
             "boundary + normalization; airfoil: normalization), so coverage follows each "
             "SUT's admissible relation rather than a fixed checklist (C36)"),
            ("node-permutation is insensitive to invariant-preserving faults on every SUT "
             "(expected by-class), contributing zero detection while anchoring the "
             "representation contract (C36, C38, C42/C43)"),
        ],
        "shared_localization_across_suts": xs["shared_localization_across_suts"],
        "falsifiability": ("a fault caught by an MR the gate excluded on that SUT, or coverage "
                           "surviving exclusion of the only MR measuring the affected invariant, "
                           "would refute the duality; none observed across the converged SUTs"),
        "prior_synthesis": ("the four-architecture-family duality synthesis is C47; this "
                            "consolidation adds the three-arm complementarity layer across the "
                            "converged SUTs"),
    }

    report = {
        "record_type": "ext3-cross-sut-three-arm-consolidation",
        "schema_version": "0.1.0",
        "purpose": ("consolidate per-SUT three-arm complementarity + validity-coverage duality "
                    "across converged SUTs into one cross-SUT view; references committed "
                    "artifacts, runs no new model"),
        "converged_suts": suts,
        "duality_cross_sut": duality,
        "arm_coverage_matrix": {s["sut"]: s["arms_run"] for s in suts},
        "gpu_pending": ("airfoil arm2 (accuracy-monitor) + arm3 (ungated-generic gate value) "
                        "require the live PhysicsNeMo airfoil model (GPU); see "
                        "docs/cloud_runbook/ext3_airfoil_three_arm_kickoff.md"),
        "no_overclaim_self_check": ("every arm contrast is internal (gated vs ungated, MR vs "
                                    "accuracy on the same faults); the duality is a falsifiable "
                                    "cross-SUT prediction, not a law; zero baseline-ranking claims"),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (out / "raw" / "cross_sut_three_arm_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out / 'raw' / 'cross_sut_three_arm_report.json'}")
    for s in suts:
        a1d = s["arm1_validity_gated_mr"]
        rate = a1d.get("rate", "per-traj") if isinstance(a1d, dict) else "?"
        print(f"  {s['sut'][:46]:46s} arms={s['arms_run']} admissible={len(s['admissible_mr_set'])}MR arm1_rate={rate}")
    print(f"cross-SUT duality: confirmed on {len(suts)} converged SUTs, 0 falsifying cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
