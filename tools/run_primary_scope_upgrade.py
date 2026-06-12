"""Expand the primary MGN evidence grid across held-out test trajectories.

Phase 11 removed the literal 10-frame / 2-frame / one-input pilot denominators
but still clustered all real-MGN frame cells on one source trajectory. This
runner keeps the same Minimum-MR-SubSet-derived K=6 checkpoint roster and replays
the two trajectory-dependent diagnostics on the first three official DeepMind
held-out test trajectories:

* mirror-y OOD stress: 6 checkpoints x 3 trajectories x 10 frames;
* conservation diagnostic: 6 checkpoints x 3 trajectories x 9 transitions;
* exact symmetric-mesh mirror-y: 6 checkpoints x 3 deterministic input seeds.

The output is still one architecture family and one dataset. It is no longer a
single-source-trajectory estimate.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_conservation_diagnostic import run_from_manifest as run_conservation  # noqa: E402
from run_mirror_y_ood_stress import run_from_manifest as run_mirror_ood  # noqa: E402
from run_mirror_y_symmetric_mesh import run_from_manifest as run_exact_sym  # noqa: E402
from run_primary_volume_upgrade import (  # noqa: E402
    CHECKPOINTS,
    EXACT_SEEDS,
    SOURCE_HEAD,
    SOURCE_REPO,
    _framework_version,
    _read_git_head,
    _rel,
    _sha256,
    _write_manifest,
    _python_version,
)


ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets/runs/primary-scope-upgrade"
SOURCE_CASE_DIR = OUTDIR / "source_cases"
MIRROR_FRAMES = list(range(10))
CONSERVATION_FRAMES = list(range(9))
TRAJECTORY_INDICES = [0, 1, 2]
TEST_SPLIT_URL = "https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/test.tfrecord"


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
    values = list(values)
    return float(statistics.median(values)) if values else float("nan")


def _load_dm_dataset(sut_repo: Path):
    sys.path.insert(0, str(Path(sut_repo) / "scripts"))
    from mcmr.cylinder_flow import dm_dataset as ds  # noqa: PLC0415

    return ds


def _case_path(trajectory_index: int) -> Path:
    return SOURCE_CASE_DIR / f"test_traj{trajectory_index:03d}_frames000_009.npz"


def _save_source_cases(sut_repo: Path, *, force_download: bool) -> tuple[list[dict], dict]:
    """Save compact first-10-frame npz files for the selected test trajectories."""
    ds = _load_dm_dataset(sut_repo)
    SOURCE_CASE_DIR.mkdir(parents=True, exist_ok=True)
    expected = [_case_path(i) for i in TRAJECTORY_INDICES]
    download_report: dict[str, object] = {
        "split": "test",
        "source_tfrecord": TEST_SPLIT_URL,
        "trajectory_indices": TRAJECTORY_INDICES,
        "frames_saved": list(range(10)),
        "reused_existing_source_cases": False,
    }
    if not force_download and all(path.exists() for path in expected):
        download_report["reused_existing_source_cases"] = True
    else:
        download_dir = Path(tempfile.gettempdir()) / "primary_scope_upgrade_dm"
        meta = ds.fetch_meta(download_dir)
        prefix = ds.acquire_prefix(
            download_dir, split="test", num_records=max(TRAJECTORY_INDICES) + 1
        )
        trajectories = ds.parse_trajectories(
            prefix, meta, limit=max(TRAJECTORY_INDICES) + 1
        )
        for idx in TRAJECTORY_INDICES:
            ds.save_npz(_case_path(idx), trajectories[idx], max_steps=10, include_pressure=True)
        download_report.update(
            {
                "meta_json": str(download_dir / "meta.json"),
                "downloaded_prefix_path": str(prefix),
                "downloaded_prefix_bytes": prefix.stat().st_size,
                "downloaded_prefix_sha256": _sha256(prefix),
            }
        )

    source_cases = []
    for idx in TRAJECTORY_INDICES:
        path = _case_path(idx)
        traj = ds.load_npz(path)
        y = traj.mesh_pos[:, 1]
        source_cases.append(
            {
                "trajectory_index": idx,
                "path": _rel(path),
                "sha256": _sha256(path),
                "num_nodes": int(traj.num_nodes),
                "num_cells": int(traj.cells.shape[0]),
                "num_steps_saved": int(traj.num_steps),
                "mirror_axis": float((float(y.min()) + float(y.max())) / 2.0),
            }
        )
    return source_cases, download_report


def _common_manifest_fields(
    *,
    run_id: str,
    sut_repo: Path,
    checkpoint: Path,
    source_case: Path,
    mr_id: str,
    command: str,
    raw_output_dir: Path,
    seed: int,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "sut_id": "cylinder_flow_meshgraphnet",
        "sut_repo": str(sut_repo),
        "sut_commit": SOURCE_HEAD,
        "checkpoint_path": _rel(checkpoint),
        "checkpoint_sha256": _sha256(checkpoint),
        "dataset_root": str(sut_repo / "data/raw/cylinder_flow_deepmind"),
        "source_case_path": _rel(source_case),
        "mr_id": mr_id,
        "command": command,
        "raw_output_dir": _rel(raw_output_dir),
        "seed": seed,
        "device": "cpu",
        "python_version": _python_version(),
        "framework_version": _framework_version(),
    }


def _summarize_mirror(rows: list[dict[str, object]]) -> dict[str, object]:
    n = len(rows)
    fail = sum(1 for row in rows if row["verdict"] == "fail")
    return {
        "n_checkpoints": len({row["checkpoint"] for row in rows}),
        "n_trajectories": len({row["trajectory_index"] for row in rows}),
        "frames_per_checkpoint_trajectory": len(MIRROR_FRAMES),
        "total_frame_cells": n,
        "fail_count": fail,
        "pass_count": sum(1 for row in rows if row["verdict"] == "pass"),
        "inconclusive_count": sum(1 for row in rows if row["verdict"] == "inconclusive"),
        "fail_rate": fail / n if n else float("nan"),
        "descriptive_cell_level_wilson_fail_rate_ci95": _wilson(fail, n),
        "median_violation_rel_l2": _median(float(row["metric_value"]) for row in rows),
        "median_violation_over_floor": _median(
            float(row["violation_over_floor"]) for row in rows
        ),
        "frames": MIRROR_FRAMES,
        "honesty_boundary": (
            "OOD-stress frame cells are clustered by checkpoint, held-out test "
            "trajectory, and frame. This is not a single-source-trajectory estimate, "
            "but it remains one dataset and one architecture family; Wilson bounds "
            "are descriptive cell-level summaries, not independent-trial inference."
        ),
    }


def _summarize_conservation(rows: list[dict[str, object]]) -> dict[str, object]:
    n = len(rows)
    passed = sum(1 for row in rows if row["verdict"] == "pass")
    ratios = [float(row["metric_value"]) for row in rows]
    interior = [float(row["ratio_interior"]) for row in rows]
    return {
        "n_checkpoints": len({row["checkpoint"] for row in rows}),
        "n_trajectories": len({row["trajectory_index"] for row in rows}),
        "transition_frames_per_checkpoint_trajectory": len(CONSERVATION_FRAMES),
        "total_transition_cells": n,
        "pass_count": passed,
        "fail_count": sum(1 for row in rows if row["verdict"] == "fail"),
        "pass_rate": passed / n if n else float("nan"),
        "descriptive_cell_level_wilson_pass_rate_ci95": _wilson(passed, n),
        "max_ratio": max(ratios) if ratios else float("nan"),
        "median_ratio": _median(ratios),
        "max_ratio_interior": max(interior) if interior else float("nan"),
        "transition_frames": CONSERVATION_FRAMES,
        "exact_relation_status": "deferred-uncalibrated-absolute-tolerance",
        "honesty_boundary": (
            "Reference-relative conservation-transition cells are clustered by "
            "checkpoint, held-out test trajectory, and frame. The absolute "
            "mass-conservation relation remains deferred; this is a non-regression "
            "diagnostic, not proof of divergence-free flow. This is not a "
            "single-source-trajectory estimate."
        ),
    }


def _summarize_exact(rows: list[dict[str, object]]) -> dict[str, object]:
    n = len(rows)
    fail = sum(1 for row in rows if row["verdict"] == "fail")
    return {
        "n_checkpoints": len({row["checkpoint"] for row in rows}),
        "input_seeds_per_checkpoint": len(EXACT_SEEDS),
        "total_input_cells": n,
        "fail_count": fail,
        "pass_count": sum(1 for row in rows if row["verdict"] == "pass"),
        "fail_rate": fail / n if n else float("nan"),
        "descriptive_cell_level_wilson_fail_rate_ci95": _wilson(fail, n),
        "median_rel_l2": _median(float(row["metric_value"]) for row in rows),
        "input_seeds": EXACT_SEEDS,
        "honesty_boundary": (
            "Exact-symmetric-mesh cells use synthetic no-obstacle channel inputs. "
            "They test structural mirror equivariance on an admissible relation, "
            "not in-distribution accuracy or calibrated cylinder-flow severity."
        ),
    }


def run_upgrade(sut_repo: Path, *, force_download: bool = False) -> dict[str, object]:
    sut_repo = Path(sut_repo).resolve()
    head = _read_git_head(sut_repo)
    if head != SOURCE_HEAD:
        raise ValueError(f"Minimum-MR-SubSet HEAD mismatch: expected {SOURCE_HEAD}, got {head}")
    missing = [str(path) for path in CHECKPOINTS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing checkpoint(s): {missing}")

    source_cases, download_report = _save_source_cases(
        sut_repo, force_download=force_download
    )
    source_by_index = {
        int(case["trajectory_index"]): ROOT / str(case["path"]) for case in source_cases
    }
    axis_by_index = {
        int(case["trajectory_index"]): float(case["mirror_axis"]) for case in source_cases
    }

    mirror_rows: list[dict[str, object]] = []
    conservation_rows: list[dict[str, object]] = []
    exact_rows: list[dict[str, object]] = []
    manifests: list[str] = []

    for trajectory_index in TRAJECTORY_INDICES:
        source_case = source_by_index[trajectory_index]
        for checkpoint_id, checkpoint in CHECKPOINTS.items():
            mirror_dir = OUTDIR / f"T{trajectory_index:03d}" / checkpoint_id / "mirror_ood/raw"
            mirror_manifest = (
                OUTDIR / f"T{trajectory_index:03d}" / checkpoint_id / "mirror_ood/manifest.yml"
            )
            _write_manifest(
                mirror_manifest,
                {
                    **_common_manifest_fields(
                        run_id=(
                            "phase12-primary-scope-"
                            f"T{trajectory_index:03d}-{checkpoint_id}-mirror-ood-001"
                        ),
                        sut_repo=sut_repo,
                        checkpoint=checkpoint,
                        source_case=source_case,
                        mr_id="mirror_y_ood_stress",
                        command=(
                            "python3 tools/run_mirror_y_ood_stress.py --manifest "
                            f"{_rel(mirror_manifest)} --frames 0,1,2,3,4,5,6,7,8,9"
                        ),
                        raw_output_dir=mirror_dir,
                        seed=20260612 + trajectory_index,
                    ),
                    "mirror_axis": axis_by_index[trajectory_index],
                    "ratio_threshold": 2.0,
                },
            )
            manifests.append(_rel(mirror_manifest))
            mirror_ledger = run_mirror_ood(mirror_manifest, frames=MIRROR_FRAMES)
            for row in mirror_ledger["entries"]:
                mirror_rows.append(
                    {
                        **row,
                        "checkpoint": checkpoint_id,
                        "trajectory_index": trajectory_index,
                        "source_case_path": _rel(source_case),
                    }
                )

            conservation_dir = (
                OUTDIR / f"T{trajectory_index:03d}" / checkpoint_id / "conservation/raw"
            )
            conservation_manifest = (
                OUTDIR / f"T{trajectory_index:03d}" / checkpoint_id / "conservation/manifest.yml"
            )
            _write_manifest(
                conservation_manifest,
                {
                    **_common_manifest_fields(
                        run_id=(
                            "phase12-primary-scope-"
                            f"T{trajectory_index:03d}-{checkpoint_id}-conservation-001"
                        ),
                        sut_repo=sut_repo,
                        checkpoint=checkpoint,
                        source_case=source_case,
                        mr_id="conservation_reference_relative",
                        command=(
                            "python3 tools/run_conservation_diagnostic.py --manifest "
                            f"{_rel(conservation_manifest)} --frames 0,1,2,3,4,5,6,7,8"
                        ),
                        raw_output_dir=conservation_dir,
                        seed=20260612 + trajectory_index,
                    ),
                    "regression_threshold": 1.5,
                    "absolute_divergence_tol": 1e-6,
                },
            )
            manifests.append(_rel(conservation_manifest))
            conservation_ledger = run_conservation(
                conservation_manifest, frames=CONSERVATION_FRAMES
            )
            for row in conservation_ledger["entries"]:
                conservation_rows.append(
                    {
                        **row,
                        "checkpoint": checkpoint_id,
                        "trajectory_index": trajectory_index,
                        "source_case_path": _rel(source_case),
                    }
                )

    for checkpoint_id, checkpoint in CHECKPOINTS.items():
        for seed in EXACT_SEEDS:
            exact_dir = OUTDIR / "exact_symmetric_mesh" / checkpoint_id / f"seed{seed}/raw"
            exact_manifest = (
                OUTDIR / "exact_symmetric_mesh" / checkpoint_id / f"seed{seed}/manifest.yml"
            )
            _write_manifest(
                exact_manifest,
                {
                    **_common_manifest_fields(
                        run_id=f"phase12-primary-scope-{checkpoint_id}-exact-sym-{seed}",
                        sut_repo=sut_repo,
                        checkpoint=checkpoint,
                        source_case=source_by_index[TRAJECTORY_INDICES[0]],
                        mr_id="mirror_y_exact_symmetric_mesh",
                        command=(
                            "python3 tools/run_mirror_y_symmetric_mesh.py --manifest "
                            f"{_rel(exact_manifest)}"
                        ),
                        raw_output_dir=exact_dir,
                        seed=seed,
                    ),
                    "nx": 48,
                    "half_rows": 20,
                    "Lx": 1.6,
                    "Ly": 0.4,
                },
            )
            manifests.append(_rel(exact_manifest))
            exact_ledger = run_exact_sym(exact_manifest)
            exact_rows.append(
                {
                    "checkpoint": checkpoint_id,
                    "seed": seed,
                    "metric_value": exact_ledger["metric_value"],
                    "verdict": exact_ledger["verdict"],
                    "normalizer_induced_share": exact_ledger[
                        "normalizer_equivariance_control"
                    ]["normalizer_induced_share"],
                    "manifest": _rel(exact_manifest),
                    "raw_output_dir": _rel(exact_dir),
                }
            )

    report = {
        "record_type": "primary-empirical-scope-upgrade",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_repo": SOURCE_REPO,
        "source_head": SOURCE_HEAD,
        "source_split": "DeepMind cylinder_flow held-out test split",
        "data_acquisition": download_report,
        "heldout_test_trajectories": TRAJECTORY_INDICES,
        "n_independent_test_trajectories": len(TRAJECTORY_INDICES),
        "source_cases": source_cases,
        "mgn_checkpoints": list(CHECKPOINTS),
        "manifests": manifests,
        "mirror_ood": _summarize_mirror(mirror_rows),
        "conservation": _summarize_conservation(conservation_rows),
        "exact_symmetric_mesh": _summarize_exact(exact_rows),
        "rows": {
            "mirror_ood": mirror_rows,
            "conservation": conservation_rows,
            "exact_symmetric_mesh": exact_rows,
        },
        "honesty_boundary": (
            "The trajectory-dependent MGN cells are clustered by checkpoint, "
            "held-out test trajectory, and frame across the first three official "
            "DeepMind cylinder_flow test trajectories acquired with the "
            "Minimum-MR-SubSet loader. This is not a single-source-trajectory "
            "estimate, but it is not a cross-SUT, cross-dataset, reliability, "
            "model-accuracy, or broad neural-simulator generalization claim."
        ),
    }
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "primary_scope_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sut-repo", required=True)
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="redownload the DeepMind test TFRecord prefix even if compact source cases exist",
    )
    args = parser.parse_args(argv)
    report = run_upgrade(Path(args.sut_repo), force_download=args.force_download)
    print(
        "primary scope upgrade complete: "
        f"mirror {report['mirror_ood']['fail_count']}/"
        f"{report['mirror_ood']['total_frame_cells']} fail, "
        f"conservation {report['conservation']['pass_count']}/"
        f"{report['conservation']['total_transition_cells']} pass, "
        f"exact-sym {report['exact_symmetric_mesh']['fail_count']}/"
        f"{report['exact_symmetric_mesh']['total_input_cells']} fail"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
