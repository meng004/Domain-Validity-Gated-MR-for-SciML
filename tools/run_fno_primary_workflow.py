"""Promote the FNO roster to a full rubric-to-verdict primary workflow.

This script intentionally reuses the committed FNO K=6 trained checkpoints and
emits a separate evidence package with source/follow-up outputs, per-case metric
ledgers, rubric decisions, and relation verdicts.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
ROSTER_DIR = ROOT / "research_assets/runs/fno-k6-roster"
OUT_DIR = ROOT / "research_assets/runs/fno-primary-workflow"
SEEDS = [0, 1, 2]
PDES = ["burgers", "heat"]
TRANSLATION_TOL = 1e-5
CONSERVATION_TOL_MIN = 1e-5

sys.path.insert(0, str(ROOT / "tools"))
from gen_fd_dataset_2d import make_dataset  # noqa: E402
from run_fno_k6_roster import load_model  # noqa: E402
from train_fno_2d import relative_l2  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _relative_channel_sum_drift(after: np.ndarray, before: np.ndarray) -> float:
    before_sum = np.sum(before, axis=(-2, -1))
    after_sum = np.sum(after, axis=(-2, -1))
    return relative_l2(after_sum, before_sum)


def _load_manifest(sut_dir: Path) -> dict:
    manifest_path = sut_dir / "manifest.json"
    checkpoint_path = sut_dir / "sut/checkpoint.pt"
    if not manifest_path.exists() or not checkpoint_path.exists():
        raise FileNotFoundError(
            f"missing FNO roster artifact under {sut_dir}; run "
            "tools/run_fno_k6_roster.py first"
        )
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _rubric_decisions(shift: int) -> list[dict]:
    return [
        {
            "relation_id": "fno-periodic-translation",
            "relation_name": "periodic integer-translation MR",
            "admissibility": "admitted",
            "predicate": "periodic boundary condition and integer grid shift",
            "source_followup_transform": f"roll input by ({shift}, {shift}) cells",
            "expected_output_relation": "rolled follow-up output maps back to source output",
            "tolerance_rule": f"relative L2 < {TRANSLATION_TOL:g}",
        },
        {
            "relation_id": "fno-periodic-discrete-conservation",
            "relation_name": "periodic discrete-conservation MR",
            "admissibility": "admitted-with-reference-floor",
            "predicate": "periodic finite-difference target has a measured channel-sum drift floor",
            "source_followup_transform": "one periodic finite-difference evolution step",
            "expected_output_relation": "output channel sums should not exceed the calibrated reference floor",
            "tolerance_rule": (
                "relative channel-sum drift <= max(1e-5, 10 * reference_floor + 1e-6)"
            ),
        },
        {
            "relation_id": "fno-dirichlet-translation",
            "relation_name": "Dirichlet-boundary translation candidate",
            "admissibility": "rejected",
            "predicate": "non-periodic boundary condition changes the boundary-value problem",
            "source_followup_transform": f"roll input by ({shift}, {shift}) cells",
            "expected_output_relation": None,
            "tolerance_rule": "not executed as an exact MR",
        },
    ]


def evaluate_sut(sut_dir: Path, manifest: dict, outdir: Path, n_eval: int, shift: int) -> dict:
    model, cfg = load_model(sut_dir)
    pde = cfg["pde"]
    seed = int(cfg["seed"])
    data = make_dataset(pde, "periodic", cfg["grid_n"], n_eval, 1000 + seed, steps=cfg["steps"])
    x = torch.from_numpy(data["inputs"])
    target = data["targets"]

    with torch.no_grad():
        y_source = model(x).numpy()
        x_follow = torch.roll(x, shifts=(shift, shift), dims=(-2, -1))
        y_follow = model(x_follow).numpy()

    y_follow_mapped = np.roll(y_follow, shift=(-shift, -shift), axis=(-2, -1))
    raw_dir = outdir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    translation_cases: list[dict] = []
    conservation_cases: list[dict] = []
    case_artifacts: list[str] = []

    for case_idx in range(n_eval):
        raw_path = raw_dir / f"case_{case_idx:02d}.npz"
        np.savez_compressed(
            raw_path,
            source_input=data["inputs"][case_idx],
            followup_input=np.roll(data["inputs"][case_idx], shift=(shift, shift), axis=(-2, -1)),
            reference_target=target[case_idx],
            source_output=y_source[case_idx],
            followup_output=y_follow[case_idx],
            mapped_followup_output=y_follow_mapped[case_idx],
        )
        case_artifacts.append(_rel_path(raw_path))

        translation_violation = relative_l2(y_follow_mapped[case_idx], y_source[case_idx])
        translation_cases.append(
            {
                "case_id": f"{manifest['sut_id']}:translation:{case_idx}",
                "raw_output": _rel_path(raw_path),
                "violation": translation_violation,
                "threshold": TRANSLATION_TOL,
                "verdict": "pass" if translation_violation < TRANSLATION_TOL else "fail",
            }
        )

        reference_floor = _relative_channel_sum_drift(target[case_idx], data["inputs"][case_idx])
        model_drift = _relative_channel_sum_drift(y_source[case_idx], data["inputs"][case_idx])
        threshold = max(CONSERVATION_TOL_MIN, 10.0 * reference_floor + 1e-6)
        conservation_cases.append(
            {
                "case_id": f"{manifest['sut_id']}:conservation:{case_idx}",
                "raw_output": _rel_path(raw_path),
                "reference_floor": reference_floor,
                "model_relative_channel_sum_drift": model_drift,
                "threshold": threshold,
                "verdict": "pass" if model_drift <= threshold else "fail",
            }
        )

    ledger = {
        "record_type": "fno-primary-sut-ledger",
        "generated_at": _utc_now(),
        "sut_id": manifest["sut_id"],
        "architecture_family": "FNO-2D",
        "pde": pde,
        "seed": seed,
        "checkpoint_sha256": manifest["checkpoint_sha256"],
        "checkpoint": _rel_path(sut_dir / "sut/checkpoint.pt"),
        "rubric_decisions": _rubric_decisions(shift),
        "source_followup_outputs": case_artifacts,
        "relations": {
            "periodic_translation": translation_cases,
            "periodic_discrete_conservation": conservation_cases,
            "dirichlet_translation_rejection": {
                "admissibility": "rejected",
                "executed_as_exact_mr": False,
                "reason": "Dirichlet translation changes the boundary-value problem.",
            },
        },
    }
    ledger_path = outdir / "metric_ledger.json"
    rubric_path = outdir / "rubric_decisions.json"
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    rubric_path.write_text(json.dumps(ledger["rubric_decisions"], indent=2) + "\n", encoding="utf-8")

    return {
        "sut_id": manifest["sut_id"],
        "pde": pde,
        "seed": seed,
        "checkpoint_sha256": manifest["checkpoint_sha256"],
        "metric_ledger": _rel_path(ledger_path),
        "rubric_decisions": _rel_path(rubric_path),
        "raw_output_dir": _rel_path(raw_dir),
        "translation_cases": translation_cases,
        "conservation_cases": conservation_cases,
        "dirichlet_translation_rejection": ledger["relations"]["dirichlet_translation_rejection"],
    }


def aggregate(per_sut: list[dict], n_eval: int) -> dict:
    translation_cases = [case for sut in per_sut for case in sut["translation_cases"]]
    conservation_cases = [case for sut in per_sut for case in sut["conservation_cases"]]
    dirichlet_rejections = [sut["dirichlet_translation_rejection"] for sut in per_sut]

    translation_passes = sum(case["verdict"] == "pass" for case in translation_cases)
    conservation_fails = sum(case["verdict"] == "fail" for case in conservation_cases)
    reference_floors = [case["reference_floor"] for case in conservation_cases]
    model_drifts = [case["model_relative_channel_sum_drift"] for case in conservation_cases]

    return {
        "record_type": "fno-primary-workflow",
        "schema_version": "0.1.0",
        "generated_at": _utc_now(),
        "architecture_family": "FNO-2D",
        "pdes": PDES,
        "seeds": SEEDS,
        "trained_sut_count": len(per_sut),
        "n_eval_per_sut": n_eval,
        "full_workflow_flags": {
            "trained_checkpoints": True,
            "rubric_decisions": True,
            "source_followup_outputs": True,
            "metric_ledgers": True,
            "relation_verdicts": True,
        },
        "periodic_translation": {
            "admissibility": "admitted",
            "total_case_cells": len(translation_cases),
            "pass_count": translation_passes,
            "fail_count": len(translation_cases) - translation_passes,
            "max_violation": max(case["violation"] for case in translation_cases),
            "threshold": TRANSLATION_TOL,
            "summary": f"{translation_passes}/{len(translation_cases)} translation passes",
        },
        "periodic_discrete_conservation": {
            "admissibility": "admitted-with-reference-floor",
            "total_case_cells": len(conservation_cases),
            "pass_count": len(conservation_cases) - conservation_fails,
            "fail_count": conservation_fails,
            "reference_floor_max": max(reference_floors),
            "reference_floor_mean": float(np.mean(reference_floors)),
            "model_drift_min": min(model_drifts),
            "model_drift_max": max(model_drifts),
            "threshold_rule": "max(1e-5, 10 * reference_floor + 1e-6)",
            "summary": f"{conservation_fails}/{len(conservation_cases)} conservation failures",
            "honesty_boundary": (
                "The periodic discrete-conservation MR is executable and not deferred for "
                "this FNO roster because the FD reference floor is measured case by case; "
                "the observed failures are FNO channel-sum drift relative to that floor."
            ),
        },
        "dirichlet_translation_rejection": {
            "admissibility": "rejected",
            "rejected_count": sum(item["admissibility"] == "rejected" for item in dirichlet_rejections),
            "executed_as_exact_mr_count": sum(item["executed_as_exact_mr"] for item in dirichlet_rejections),
            "reason": "Dirichlet translation changes the boundary-value problem.",
        },
        "per_sut": per_sut,
        "honesty_boundary": (
            "This is full rubric-to-verdict primary workflow evidence on trained FNO-2D "
            "checkpoints over finite-difference Burgers/heat data; it is not only "
            "admissibility evidence, and it remains outside cylinder-flow, performance "
            "benchmarking, reliability, and broad neural-operator generalization claims."
        ),
        "claim_limitations": [
            "No cylinder-flow FNO evidence is claimed.",
            "No FNO-vs-MGN or FNO-vs-PINN performance superiority is claimed.",
            "No broad neural-operator reliability or external-validity rate is claimed.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-eval", type=int, default=4)
    parser.add_argument("--shift", type=int, default=2)
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    per_sut: list[dict] = []
    for pde in PDES:
        for seed in SEEDS:
            tag = f"{pde}_s{seed}"
            sut_dir = ROSTER_DIR / tag
            manifest = _load_manifest(sut_dir)
            sut_out = OUT_DIR / tag
            sut_out.mkdir(parents=True, exist_ok=True)
            result = evaluate_sut(sut_dir, manifest, sut_out, args.n_eval, args.shift)
            per_sut.append(result)
            tr_pass = sum(case["verdict"] == "pass" for case in result["translation_cases"])
            cons_fail = sum(case["verdict"] == "fail" for case in result["conservation_cases"])
            print(
                f"[{tag}] translation {tr_pass}/{args.n_eval} pass; "
                f"conservation {cons_fail}/{args.n_eval} fail",
                flush=True,
            )

    report = aggregate(per_sut, args.n_eval)
    report_path = OUT_DIR / "fno_primary_workflow_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    smoke = {
        "record_type": "fno-primary-workflow-smoke-manifest",
        "generated_at": report["generated_at"],
        "command": f"python3 tools/run_fno_primary_workflow.py --n-eval {args.n_eval}",
        "report": _rel_path(report_path),
        "sut_count": report["trained_sut_count"],
        "case_cells": report["periodic_translation"]["total_case_cells"],
    }
    (OUT_DIR / "smoke_manifest.json").write_text(json.dumps(smoke, indent=2) + "\n", encoding="utf-8")
    print(
        "FNO primary workflow complete: "
        f"{report['periodic_translation']['summary']}, "
        f"{report['periodic_discrete_conservation']['summary']}"
    )
    print(f"wrote {_rel_path(report_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
