"""Run an independent periodic-advection primary workflow.

The workflow trains six deterministic periodic-convolution surrogates for a
2D scalar periodic advection step, then records rubric decisions,
source/follow-up outputs, metric ledgers, and typed verdicts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "research_assets/runs/periodic-advection-primary-workflow"
CHECKPOINT_DIR = OUT_DIR / "checkpoints"
GRID_N = 32
TRAIN_CASES = 96
DEFAULT_EVAL_CASES = 10
SEEDS = [0, 1, 2, 3, 4, 5]
ADVECTION_SHIFT = (1, 2)
TRANSLATION_TOL = 1e-10
MASS_TOL = 1e-10
EPS = 1e-12
OFFSETS = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)]
TRANSLATION_SHIFTS = [(3, 5), (7, 2), (11, 13), (16, 4), (5, 17)]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rel_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def smooth_periodic_field(rng: np.random.Generator, n: int = GRID_N) -> np.ndarray:
    noise = rng.normal(size=(n, n))
    spectrum = np.fft.fftn(noise)
    ky = np.fft.fftfreq(n)[:, None]
    kx = np.fft.fftfreq(n)[None, :]
    low_pass = np.exp(-0.5 * ((kx / 0.14) ** 2 + (ky / 0.14) ** 2))
    field = np.fft.ifftn(spectrum * low_pass).real
    field = field - float(np.mean(field))
    rms = float(np.sqrt(np.mean(field**2)))
    return (field / max(rms, EPS)).astype(np.float64)


def exact_advection_step(field: np.ndarray) -> np.ndarray:
    return np.roll(field, shift=ADVECTION_SHIFT, axis=(0, 1))


def feature_stack(field: np.ndarray) -> np.ndarray:
    return np.stack([np.roll(field, shift=offset, axis=(0, 1)) for offset in OFFSETS], axis=-1)


def train_kernel(seed: int) -> tuple[np.ndarray, dict]:
    rng = np.random.default_rng(20260703 + seed)
    x_rows: list[np.ndarray] = []
    y_rows: list[np.ndarray] = []
    for _ in range(TRAIN_CASES):
        field = smooth_periodic_field(rng)
        x_rows.append(feature_stack(field).reshape(-1, len(OFFSETS)))
        y_rows.append(exact_advection_step(field).reshape(-1))
    x_mat = np.concatenate(x_rows, axis=0)
    y_vec = np.concatenate(y_rows, axis=0)
    ridge = 1e-12
    normal = x_mat.T @ x_mat + ridge * np.eye(len(OFFSETS))
    rhs = x_mat.T @ y_vec
    kernel = np.linalg.solve(normal, rhs)
    train_pred = x_mat @ kernel
    train_rel_l2 = float(np.linalg.norm(train_pred - y_vec) / max(np.linalg.norm(y_vec), EPS))
    return kernel.astype(np.float64), {
        "train_cases": TRAIN_CASES,
        "train_grid_cells": int(TRAIN_CASES * GRID_N * GRID_N),
        "ridge": ridge,
        "train_relative_l2": train_rel_l2,
        "kernel_sum": float(np.sum(kernel)),
        "kernel_l1": float(np.sum(np.abs(kernel))),
        "dominant_offset": list(OFFSETS[int(np.argmax(np.abs(kernel)))]),
        "dominant_weight": float(kernel[int(np.argmax(np.abs(kernel)))]),
    }


def predict(field: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    return np.tensordot(feature_stack(field), kernel, axes=([-1], [0]))


def relative_l2(after: np.ndarray, before: np.ndarray) -> float:
    return float(np.linalg.norm(after - before) / max(np.linalg.norm(before), EPS))


def normalized_mean_drift(after: np.ndarray, before: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(before**2)))
    return float(abs(np.mean(after) - np.mean(before)) / max(rms, EPS))


def rubric_decisions() -> list[dict]:
    return [
        {
            "relation_id": "periodic-advection-translation-equivariance",
            "relation_name": "periodic integer-translation equivariance",
            "admissibility": "admitted",
            "predicate": "periodic boundary condition, integer grid translation, and deterministic periodic-convolution inference",
            "source_followup_transform": "roll scalar field by a declared integer (dy, dx)",
            "expected_output_relation": "inverse-rolled follow-up output equals the source output",
            "tolerance_rule": f"relative L2 <= {TRANSLATION_TOL:g}",
        },
        {
            "relation_id": "periodic-advection-mass-conservation",
            "relation_name": "periodic global mean conservation",
            "admissibility": "admitted",
            "predicate": "periodic scalar advection preserves the spatial integral",
            "source_followup_transform": "one periodic advection step predicted by the SUT",
            "expected_output_relation": "predicted output mean equals source input mean",
            "tolerance_rule": f"rms-normalized absolute mean drift <= {MASS_TOL:g}",
        },
        {
            "relation_id": "periodic-advection-fixed-velocity-mirror",
            "relation_name": "mirror reflection under fixed advection velocity",
            "admissibility": "rejected",
            "predicate": "reflection of the scalar field alone does not transform the advection velocity vector",
            "source_followup_transform": "mirror scalar field in y while keeping velocity/shift fixed",
            "expected_output_relation": None,
            "tolerance_rule": "not executed as an exact MR",
        },
    ]


def evaluate_sut(seed: int, kernel: np.ndarray, checkpoint_path: Path, n_eval: int) -> dict:
    rng = np.random.default_rng(20261703 + seed)
    sut_id = f"periodic_advection_conv_s{seed}"
    sut_dir = OUT_DIR / sut_id
    raw_dir = sut_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    translation_cases: list[dict] = []
    mass_cases: list[dict] = []
    accuracy_cases: list[dict] = []
    case_artifacts: list[str] = []

    for case_idx in range(n_eval):
        source = smooth_periodic_field(rng)
        reference = exact_advection_step(source)
        source_output = predict(source, kernel)
        shift = TRANSLATION_SHIFTS[case_idx % len(TRANSLATION_SHIFTS)]
        followup_input = np.roll(source, shift=shift, axis=(0, 1))
        followup_output = predict(followup_input, kernel)
        mapped_followup_output = np.roll(followup_output, shift=(-shift[0], -shift[1]), axis=(0, 1))
        raw_path = raw_dir / f"case_{case_idx:02d}.npz"
        np.savez_compressed(
            raw_path,
            source_input=source,
            followup_input=followup_input,
            reference_output=reference,
            source_output=source_output,
            followup_output=followup_output,
            mapped_followup_output=mapped_followup_output,
            translation_shift=np.asarray(shift, dtype=np.int64),
        )
        case_artifacts.append(rel_path(raw_path))

        translation_violation = relative_l2(mapped_followup_output, source_output)
        mass_drift = normalized_mean_drift(source_output, source)
        accuracy_rel_l2 = relative_l2(source_output, reference)
        translation_cases.append(
            {
                "case_id": f"{sut_id}:translation:{case_idx}",
                "raw_output": rel_path(raw_path),
                "translation_shift": list(shift),
                "violation": translation_violation,
                "threshold": TRANSLATION_TOL,
                "verdict": "pass" if translation_violation <= TRANSLATION_TOL else "fail",
            }
        )
        mass_cases.append(
            {
                "case_id": f"{sut_id}:mass:{case_idx}",
                "raw_output": rel_path(raw_path),
                "rms_normalized_mean_drift": mass_drift,
                "threshold": MASS_TOL,
                "verdict": "pass" if mass_drift <= MASS_TOL else "fail",
            }
        )
        accuracy_cases.append(
            {
                "case_id": f"{sut_id}:accuracy-diagnostic:{case_idx}",
                "relative_l2_to_exact_shift": accuracy_rel_l2,
            }
        )

    ledger = {
        "record_type": "periodic-advection-primary-sut-ledger",
        "generated_at": utc_now(),
        "sut_id": sut_id,
        "task": "2D scalar periodic advection",
        "architecture_family": "NumPy periodic convolution surrogate",
        "seed": seed,
        "checkpoint": rel_path(checkpoint_path),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "rubric_decisions": rubric_decisions(),
        "source_followup_outputs": case_artifacts,
        "relations": {
            "periodic_translation": translation_cases,
            "periodic_mass_conservation": mass_cases,
            "fixed_velocity_mirror_rejection": {
                "admissibility": "rejected",
                "executed_as_exact_mr": False,
                "reason": "Mirroring the scalar field without transforming the fixed advection velocity changes the transport problem.",
            },
        },
        "accuracy_diagnostic": accuracy_cases,
    }
    ledger_path = sut_dir / "metric_ledger.json"
    rubric_path = sut_dir / "rubric_decisions.json"
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    rubric_path.write_text(json.dumps(ledger["rubric_decisions"], indent=2) + "\n", encoding="utf-8")
    return {
        "sut_id": sut_id,
        "seed": seed,
        "checkpoint": rel_path(checkpoint_path),
        "checkpoint_sha256": ledger["checkpoint_sha256"],
        "metric_ledger": rel_path(ledger_path),
        "rubric_decisions": rel_path(rubric_path),
        "raw_output_dir": rel_path(raw_dir),
        "translation_cases": translation_cases,
        "mass_cases": mass_cases,
        "accuracy_cases": accuracy_cases,
        "fixed_velocity_mirror_rejection": ledger["relations"]["fixed_velocity_mirror_rejection"],
    }


def aggregate(per_sut: list[dict], training: dict[int, dict], n_eval: int) -> dict:
    translation_cases = [case for sut in per_sut for case in sut["translation_cases"]]
    mass_cases = [case for sut in per_sut for case in sut["mass_cases"]]
    accuracy_values = [
        case["relative_l2_to_exact_shift"]
        for sut in per_sut
        for case in sut["accuracy_cases"]
    ]
    mirror_rejections = [sut["fixed_velocity_mirror_rejection"] for sut in per_sut]
    translation_passes = sum(case["verdict"] == "pass" for case in translation_cases)
    mass_passes = sum(case["verdict"] == "pass" for case in mass_cases)
    return {
        "record_type": "periodic-advection-primary-workflow",
        "schema_version": "0.1.0",
        "generated_at": utc_now(),
        "task": "2D scalar periodic advection",
        "architecture_family": "NumPy periodic convolution surrogate",
        "grid": [GRID_N, GRID_N],
        "advection_shift_cells": list(ADVECTION_SHIFT),
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
        "periodic_mass_conservation": {
            "admissibility": "admitted",
            "total_case_cells": len(mass_cases),
            "pass_count": mass_passes,
            "fail_count": len(mass_cases) - mass_passes,
            "max_rms_normalized_mean_drift": max(case["rms_normalized_mean_drift"] for case in mass_cases),
            "threshold": MASS_TOL,
            "summary": f"{mass_passes}/{len(mass_cases)} mass-conservation passes",
        },
        "fixed_velocity_mirror_rejection": {
            "admissibility": "rejected",
            "rejected_count": sum(item["admissibility"] == "rejected" for item in mirror_rejections),
            "executed_as_exact_mr_count": sum(item["executed_as_exact_mr"] for item in mirror_rejections),
            "reason": "Fixed-velocity mirror reflection changes the advection problem unless the velocity vector is transformed.",
        },
        "accuracy_diagnostic": {
            "median_relative_l2_to_exact_shift": float(np.median(accuracy_values)),
            "max_relative_l2_to_exact_shift": float(np.max(accuracy_values)),
            "claim_boundary": "Training accuracy is recorded only as a diagnostic; no benchmark or model-superiority claim is made.",
        },
        "training_diagnostics": {str(seed): training[seed] for seed in SEEDS},
        "per_sut": per_sut,
        "honesty_boundary": (
            "This is full rubric-to-verdict evidence for an independent synthetic "
            "2D periodic-advection SciML surrogate task: six trained NumPy periodic "
            "convolution SUTs, source/follow-up outputs, metric ledgers, admitted "
            "translation and mass-conservation verdicts, and a rejected mirror "
            "candidate. It is not CFD evidence, not production-SUT evidence, not "
            "real-defect evidence, and not a broad neural-operator reliability claim."
        ),
        "claim_limitations": [
            "No cylinder-flow, airfoil, PINN, FNO, or production-framework claim is made from this run.",
            "No real-world defect-detection rate, reliability rate, or SOTA accuracy claim is made.",
            "The task is synthetic periodic scalar advection; transfer to open-boundary or compressible CFD requires separate evidence.",
        ],
    }


def write_provenance(report_path: Path, command: str) -> None:
    text = f"""# Periodic Advection Primary Workflow Provenance

Generated: {utc_now()}

Command:

```bash
{command}
```

This run trains deterministic NumPy periodic-convolution surrogates on synthetic
2D scalar periodic-advection fields and records the complete rubric-to-verdict
chain. It uses no external dataset, network access, GPU runtime, or sibling
repository writes.

Aggregate report: `{rel_path(report_path)}`

Claim boundary: independent synthetic PDE/SciML surrogate evidence only; not
production CFD, real-defect, reliability, or model-accuracy evidence.
"""
    (OUT_DIR / "PROVENANCE.md").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-eval", type=int, default=DEFAULT_EVAL_CASES)
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    per_sut: list[dict] = []
    training: dict[int, dict] = {}
    for seed in SEEDS:
        kernel, train_info = train_kernel(seed)
        checkpoint_path = CHECKPOINT_DIR / f"seed_{seed}.npz"
        np.savez_compressed(
            checkpoint_path,
            kernel=kernel,
            offsets=np.asarray(OFFSETS, dtype=np.int64),
            grid_n=np.asarray([GRID_N], dtype=np.int64),
            advection_shift=np.asarray(ADVECTION_SHIFT, dtype=np.int64),
            seed=np.asarray([seed], dtype=np.int64),
        )
        training[seed] = train_info
        result = evaluate_sut(seed, kernel, checkpoint_path, args.n_eval)
        per_sut.append(result)
        tr_pass = sum(case["verdict"] == "pass" for case in result["translation_cases"])
        mass_pass = sum(case["verdict"] == "pass" for case in result["mass_cases"])
        print(
            f"[seed {seed}] translation {tr_pass}/{args.n_eval} pass; "
            f"mass {mass_pass}/{args.n_eval} pass",
            flush=True,
        )

    report = aggregate(per_sut, training, args.n_eval)
    report_path = OUT_DIR / "periodic_advection_primary_workflow_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    smoke = {
        "record_type": "periodic-advection-primary-workflow-smoke-manifest",
        "generated_at": report["generated_at"],
        "command": f"python3 tools/run_periodic_advection_primary_workflow.py --n-eval {args.n_eval}",
        "report": rel_path(report_path),
        "sut_count": report["trained_sut_count"],
        "case_cells": report["periodic_translation"]["total_case_cells"],
    }
    (OUT_DIR / "smoke_manifest.json").write_text(json.dumps(smoke, indent=2) + "\n", encoding="utf-8")
    write_provenance(report_path, smoke["command"])
    print(
        "Periodic advection primary workflow complete: "
        f"{report['periodic_translation']['summary']}, "
        f"{report['periodic_mass_conservation']['summary']}"
    )
    print(f"wrote {rel_path(report_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
