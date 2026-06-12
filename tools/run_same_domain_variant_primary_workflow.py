"""Assemble the same-domain second-SUT primary workflow for MGN variants.

This runner promotes the already executed S4/S5 cylinder-flow MeshGraphNet
configuration variants into a separate rubric-to-verdict evidence package.  It
uses only committed raw outputs and metric ledgers from the primary scope
upgrade / multicheckpoint runs, and fails closed if any referenced raw artifact
is missing.  The purpose is not to create a new architecture-family claim, but
to add a second same-domain checkpoint family (wider and deeper MGN variants)
with the full primary workflow shape: rubric decisions, source/follow-up raw
outputs, metric ledgers, relation verdicts, and an explicit honesty boundary.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets/runs/same-domain-variant-primary-workflow"
CHECKPOINTS = ["S4", "S5"]
TRAJECTORIES = [0, 1, 2]
EXACT_SEEDS = [20260606, 20260607, 20260608]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_path(recorded: str) -> Path:
    path = Path(recorded)
    return path if path.is_absolute() else ROOT / path


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"required evidence artifact is missing: {_rel(path)}")


def _require_ledger_artifacts(ledger_path: Path, ledger: dict) -> None:
    _require_file(ledger_path)
    raw_outputs = ledger.get("raw_outputs", {})
    if isinstance(raw_outputs, dict):
        for recorded in raw_outputs.values():
            _require_file(_as_path(recorded))
    for entry in ledger.get("entries", []):
        evidence = entry.get("evidence_artifact")
        if evidence:
            _require_file(_as_path(evidence))


def _wilson(successes: int, n: int, z: float = 1.959963984540054) -> list[float]:
    if n == 0:
        return [float("nan"), float("nan")]
    p = successes / n
    z2 = z * z
    denom = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) / n) + (z2 / (4 * n * n))) / denom
    return [max(0.0, center - margin), min(1.0, center + margin)]


def _median(values: Iterable[float]) -> float:
    seq = sorted(float(v) for v in values)
    if not seq:
        return float("nan")
    mid = len(seq) // 2
    return seq[mid] if len(seq) % 2 else (seq[mid - 1] + seq[mid]) / 2.0


def _rubric_decisions() -> list[dict[str, object]]:
    return [
        {
            "relation_id": "mgn-node-permutation-equivariance",
            "relation_name": "node-permutation equivariance",
            "admissibility": "admitted",
            "predicate": "MeshGraphNets message passing is invariant to node relabeling when node features and edge endpoints are relabelled consistently.",
            "source_followup_transform": "apply a bijective node permutation and consistently relabel edge_index",
            "expected_output_relation": "inverse-mapped follow-up output equals the source output",
            "tolerance_rule": "relative L2 <= 1e-6",
        },
        {
            "relation_id": "mirror_y_ood_stress",
            "relation_name": "mirror-y OOD stress probe",
            "admissibility": "downgraded-to-ood-stress",
            "predicate": "the held-out asymmetric cylinder-flow meshes do not satisfy exact mirror-y preconditions",
            "source_followup_transform": "reflect y-coordinates/velocity channels through the measured channel midline",
            "expected_output_relation": "reported only as out-of-relation-domain stress, not as exact-MR inconsistency",
            "tolerance_rule": "relative L2 <= 1e-6 with mapping-floor ratio recorded",
        },
        {
            "relation_id": "conservation_reference_relative",
            "relation_name": "reference-relative discrete-divergence diagnostic",
            "admissibility": "diagnostic-not-absolute-mr",
            "predicate": "absolute incompressibility tolerance is not calibrated on these unstructured cells; reference-relative regression threshold is executable",
            "source_followup_transform": "one predicted transition compared with the reference next-state transition",
            "expected_output_relation": "predicted divergence should not exceed 1.5x the reference divergence diagnostic",
            "tolerance_rule": "divergence_pred_over_reference_ratio <= 1.5",
        },
        {
            "relation_id": "mirror_y_exact_symmetric_mesh",
            "relation_name": "exact mirror-y on synthetic symmetric mesh",
            "admissibility": "admitted-on-synthetic-symmetric-input",
            "predicate": "synthetic no-obstacle channel mesh has an exact reflection bijection and symmetric node types",
            "source_followup_transform": "reflect a deterministic symmetric input through the channel midline",
            "expected_output_relation": "inverse-mapped reflected output equals the source output with vy sign mapping",
            "tolerance_rule": "relative L2 <= 1e-6",
        },
    ]


def _collect_node_perm() -> list[dict[str, object]]:
    rows = []
    for checkpoint in CHECKPOINTS:
        ledger_path = ROOT / f"research_assets/runs/multicheckpoint/{checkpoint}/node_perm/raw/metric_ledger.json"
        ledger = _load_json(ledger_path)
        _require_ledger_artifacts(ledger_path, ledger)
        entry = ledger["entries"][0]
        rows.append({
            "checkpoint": checkpoint,
            "ledger": _rel(ledger_path),
            "checkpoint_sha256": ledger["checkpoint_sha256"],
            "metric_value": entry["metric_value"],
            "threshold": entry["tolerance"]["threshold"],
            "verdict": entry["verdict"],
            "raw_outputs": ledger["raw_outputs"],
        })
    return rows


def _collect_mirror_ood() -> list[dict[str, object]]:
    rows = []
    for trajectory in TRAJECTORIES:
        for checkpoint in CHECKPOINTS:
            ledger_path = ROOT / (
                f"research_assets/runs/primary-scope-upgrade/T{trajectory:03d}/"
                f"{checkpoint}/mirror_ood/raw/metric_ledger.json"
            )
            ledger = _load_json(ledger_path)
            _require_ledger_artifacts(ledger_path, ledger)
            for entry in ledger["entries"]:
                rows.append({
                    "checkpoint": checkpoint,
                    "trajectory_index": trajectory,
                    "frame": entry["frame"],
                    "ledger": _rel(ledger_path),
                    "metric_value": entry["metric_value"],
                    "mapping_error_floor": entry["mapping_error_floor"],
                    "violation_over_floor": entry["violation_over_floor"],
                    "exact_relation_verdict": entry["exact_relation_verdict"],
                    "verdict": entry["verdict"],
                    "evidence_artifact": entry["evidence_artifact"],
                })
    return rows


def _collect_conservation() -> list[dict[str, object]]:
    rows = []
    for trajectory in TRAJECTORIES:
        for checkpoint in CHECKPOINTS:
            ledger_path = ROOT / (
                f"research_assets/runs/primary-scope-upgrade/T{trajectory:03d}/"
                f"{checkpoint}/conservation/raw/metric_ledger.json"
            )
            ledger = _load_json(ledger_path)
            _require_ledger_artifacts(ledger_path, ledger)
            for entry in ledger["entries"]:
                rows.append({
                    "checkpoint": checkpoint,
                    "trajectory_index": trajectory,
                    "frame": entry["frame"],
                    "ledger": _rel(ledger_path),
                    "metric_value": entry["metric_value"],
                    "ratio_interior": entry.get("ratio_interior"),
                    "exact_relation_status": entry["exact_relation_status"],
                    "verdict": entry["verdict"],
                    "evidence_artifact": entry["evidence_artifact"],
                })
    return rows


def _collect_exact_symmetric() -> list[dict[str, object]]:
    rows = []
    for checkpoint in CHECKPOINTS:
        for seed in EXACT_SEEDS:
            ledger_path = ROOT / (
                "research_assets/runs/primary-scope-upgrade/exact_symmetric_mesh/"
                f"{checkpoint}/seed{seed}/raw/metric_ledger.json"
            )
            ledger = _load_json(ledger_path)
            _require_file(ledger_path)
            for recorded in (
                "source_output.npy", "follow_up_output.npy", "mapped_output.npy",
                "mesh_pos.npy", "cells.npy", "node_type.npy", "input_velocity.npy",
            ):
                _require_file(ledger_path.parent / recorded)
            rows.append({
                "checkpoint": checkpoint,
                "seed": seed,
                "ledger": _rel(ledger_path),
                "metric_value": ledger["metric_value"],
                "threshold": ledger["tolerance"]["threshold"],
                "verdict": ledger["verdict"],
                "normalizer_induced_share": ledger["normalizer_equivariance_control"]["normalizer_induced_share"],
                "raw_output_dir": _rel(ledger_path.parent),
            })
    return rows


def _summarize_binary(rows: list[dict[str, object]], success_verdict: str) -> dict[str, object]:
    n = len(rows)
    successes = sum(row["verdict"] == success_verdict for row in rows)
    return {
        "total_case_cells": n,
        f"{success_verdict}_count": successes,
        "other_count": n - successes,
        f"{success_verdict}_rate": successes / n if n else float("nan"),
        f"{success_verdict}_rate_wilson_ci95": _wilson(successes, n),
        "median_metric_value": _median(row["metric_value"] for row in rows),
        "max_metric_value": max(float(row["metric_value"]) for row in rows) if rows else float("nan"),
    }


def build_report() -> dict[str, object]:
    node_perm = _collect_node_perm()
    mirror_ood = _collect_mirror_ood()
    conservation = _collect_conservation()
    exact = _collect_exact_symmetric()
    rubric_path = OUTDIR / "rubric_decisions.json"
    OUTDIR.mkdir(parents=True, exist_ok=True)
    rubric = _rubric_decisions()
    rubric_path.write_text(json.dumps(rubric, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = {
        "record_type": "same-domain-variant-primary-workflow",
        "schema_version": "0.1.0",
        "generated_at": _utc_now(),
        "domain": "DeepMind cylinder_flow",
        "architecture_family": "MeshGraphNet configuration variants",
        "second_sut_family_definition": "S4 is a wider hidden=128 MGN variant; S5 is a deeper num_layers=6 MGN variant.",
        "checkpoints": CHECKPOINTS,
        "heldout_test_trajectories": TRAJECTORIES,
        "source_case_dir": "research_assets/runs/primary-scope-upgrade/source_cases",
        "full_workflow_flags": {
            "trained_checkpoints": True,
            "rubric_decisions": True,
            "source_followup_outputs": True,
            "metric_ledgers": True,
            "relation_verdicts": True,
            "same_domain_real_dataset": True,
        },
        "rubric_decisions": _rel(rubric_path),
        "node_permutation": {
            "admissibility": "admitted",
            **_summarize_binary(node_perm, "pass"),
            "summary": f"{sum(r['verdict'] == 'pass' for r in node_perm)}/{len(node_perm)} node-permutation passes",
        },
        "mirror_ood_stress": {
            "admissibility": "downgraded-to-ood-stress",
            **_summarize_binary(mirror_ood, "fail"),
            "median_violation_over_floor": _median(row["violation_over_floor"] for row in mirror_ood),
            "summary": f"{sum(r['verdict'] == 'fail' for r in mirror_ood)}/{len(mirror_ood)} mirror-y OOD-stress failures",
        },
        "conservation_reference_relative": {
            "admissibility": "diagnostic-not-absolute-mr",
            **_summarize_binary(conservation, "pass"),
            "max_ratio_interior": max(float(row["ratio_interior"]) for row in conservation),
            "summary": f"{sum(r['verdict'] == 'pass' for r in conservation)}/{len(conservation)} conservation diagnostic passes",
            "honesty_boundary": "Absolute mass conservation remains deferred; this is a reference-relative regression diagnostic.",
        },
        "exact_symmetric_mesh": {
            "admissibility": "admitted-on-synthetic-symmetric-input",
            **_summarize_binary(exact, "fail"),
            "summary": f"{sum(r['verdict'] == 'fail' for r in exact)}/{len(exact)} exact-symmetric mirror-y failures",
        },
        "rows": {
            "node_permutation": node_perm,
            "mirror_ood_stress": mirror_ood,
            "conservation_reference_relative": conservation,
            "exact_symmetric_mesh": exact,
        },
        "honesty_boundary": (
            "This is a second same-domain real cylinder-flow SUT/checkpoint-family package, "
            "not a new external architecture family: S4/S5 are MeshGraphNet configuration "
            "variants trained on the same DeepMind cylinder_flow domain. The trajectory-dependent "
            "cells use real held-out test trajectories and committed source/follow-up raw outputs. "
            "The exact symmetric-mesh relation remains synthetic-admissible evidence, and the "
            "conservation item is a reference-relative diagnostic rather than an absolute incompressibility MR."
        ),
        "claim_limitations": [
            "No PhysicsNeMo/EchoWave checkpoint is claimed.",
            "No cross-dataset generalization rate is claimed.",
            "No model-accuracy or reliability superiority claim is made.",
        ],
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    report = build_report()
    report_path = OUTDIR / "same_domain_variant_primary_workflow_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    smoke = {
        "record_type": "same-domain-variant-primary-workflow-smoke-manifest",
        "generated_at": report["generated_at"],
        "command": "python3 tools/run_same_domain_variant_primary_workflow.py",
        "report": _rel(report_path),
        "checkpoints": CHECKPOINTS,
        "case_cells": {
            "node_permutation": report["node_permutation"]["total_case_cells"],
            "mirror_ood_stress": report["mirror_ood_stress"]["total_case_cells"],
            "conservation_reference_relative": report["conservation_reference_relative"]["total_case_cells"],
            "exact_symmetric_mesh": report["exact_symmetric_mesh"]["total_case_cells"],
        },
    }
    (OUTDIR / "smoke_manifest.json").write_text(json.dumps(smoke, indent=2) + "\n", encoding="utf-8")
    print(
        "same-domain variant primary workflow complete: "
        f"{report['node_permutation']['summary']}; "
        f"{report['mirror_ood_stress']['summary']}; "
        f"{report['conservation_reference_relative']['summary']}; "
        f"{report['exact_symmetric_mesh']['summary']}"
    )
    print(f"wrote {_rel(report_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
