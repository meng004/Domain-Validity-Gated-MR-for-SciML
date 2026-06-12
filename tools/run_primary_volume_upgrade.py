"""Expand the primary MGN evidence grid for the empirical-scope revision.

This runner reuses the committed real-SUT MR runners and only orchestrates a
larger denominator over the K=6 MeshGraphNets checkpoint roster:

* mirror-y OOD stress: 6 checkpoints x 10 recorded eval frames;
* conservation diagnostic: 6 checkpoints x 9 recorded transitions;
* exact symmetric-mesh mirror-y: 6 checkpoints x 3 deterministic input seeds.

The output is a compact report suitable for the claim ledger and manuscript. The
rows are descriptive checkpoint/frame or checkpoint/input cells; they are still
clustered by one source trajectory and one architecture family.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_conservation_diagnostic import run_from_manifest as run_conservation  # noqa: E402
from run_mirror_y_ood_stress import run_from_manifest as run_mirror_ood  # noqa: E402
from run_mirror_y_symmetric_mesh import run_from_manifest as run_exact_sym  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets/runs/primary-volume-upgrade"
SOURCE_CASE = ROOT / "research_assets/runs/real-sut-node-permutation-pilot/source_case.npz"
SOURCE_REPO = "https://github.com/meng004/Minimum-MR-SubSet"
SOURCE_HEAD = "9ef862ec37335b4834d0a1fb38b4b613af702f34"
CHECKPOINTS = {
    "S0": ROOT / "research_assets/runs/multicheckpoint/S0/sut/checkpoint.pt",
    "S1": ROOT / "research_assets/runs/multicheckpoint/S1/checkpoint.pt",
    "S2": ROOT / "research_assets/runs/multicheckpoint/S2/checkpoint.pt",
    "S3": ROOT / "research_assets/runs/multicheckpoint/S3/checkpoint.pt",
    "S4": ROOT / "research_assets/runs/multicheckpoint/S4/checkpoint.pt",
    "S5": ROOT / "research_assets/runs/multicheckpoint/S5/checkpoint.pt",
}
MIRROR_FRAMES = list(range(10))
CONSERVATION_FRAMES = list(range(9))
EXACT_SEEDS = [20260606, 20260607, 20260608]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_git_head(repo: Path) -> str:
    git_dir = repo / ".git"
    if git_dir.is_file():
        text = git_dir.read_text(encoding="utf-8").strip()
        if text.startswith("gitdir:"):
            git_dir = (repo / text.split(":", 1)[1].strip()).resolve()
    head_path = git_dir / "HEAD"
    head = head_path.read_text(encoding="utf-8").strip()
    if not head.startswith("ref:"):
        return head
    ref = head.split(" ", 1)[1]
    ref_path = git_dir / ref
    if ref_path.exists():
        return ref_path.read_text(encoding="utf-8").strip()
    packed_refs = git_dir / "packed-refs"
    if packed_refs.exists():
        for line in packed_refs.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#") and line.endswith(f" {ref}"):
                return line.split(" ", 1)[0]
    raise ValueError(f"could not resolve git HEAD for {repo}")


def _rel(path: Path) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def _write_manifest(path: Path, fields: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in fields.items():
        lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _framework_version() -> str:
    import torch  # noqa: PLC0415

    return f"torch {torch.__version__}"


def _common_manifest_fields(
    *,
    run_id: str,
    sut_repo: Path,
    checkpoint: Path,
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
        "source_case_path": _rel(SOURCE_CASE),
        "mr_id": mr_id,
        "command": command,
        "raw_output_dir": _rel(raw_output_dir),
        "seed": seed,
        "device": "cpu",
        "python_version": _python_version(),
        "framework_version": _framework_version(),
    }


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


def _summarize_mirror(rows: list[dict[str, object]]) -> dict[str, object]:
    n = len(rows)
    fail = sum(1 for row in rows if row["verdict"] == "fail")
    return {
        "n_checkpoints": len({row["checkpoint"] for row in rows}),
        "frames_per_checkpoint": len(MIRROR_FRAMES),
        "total_frame_cells": n,
        "fail_count": fail,
        "pass_count": sum(1 for row in rows if row["verdict"] == "pass"),
        "inconclusive_count": sum(1 for row in rows if row["verdict"] == "inconclusive"),
        "fail_rate": fail / n if n else float("nan"),
        "wilson_fail_rate_ci95": _wilson(fail, n),
        "median_violation_rel_l2": _median(float(row["metric_value"]) for row in rows),
        "median_violation_over_floor": _median(
            float(row["violation_over_floor"]) for row in rows
        ),
        "frames": MIRROR_FRAMES,
        "honesty_boundary": (
            "OOD-stress frame cells are clustered by checkpoint and frame over one "
            "source trajectory; this removes the literal 10-frame denominator but "
            "is not a geometry-independent or multi-trajectory rate estimate. "
            "Wilson bounds are descriptive cell-level summaries, not "
            "independent-trial inference."
        ),
    }


def _summarize_conservation(rows: list[dict[str, object]]) -> dict[str, object]:
    n = len(rows)
    passed = sum(1 for row in rows if row["verdict"] == "pass")
    ratios = [float(row["metric_value"]) for row in rows]
    interior = [float(row["ratio_interior"]) for row in rows]
    return {
        "n_checkpoints": len({row["checkpoint"] for row in rows}),
        "transition_frames_per_checkpoint": len(CONSERVATION_FRAMES),
        "total_transition_cells": n,
        "pass_count": passed,
        "fail_count": sum(1 for row in rows if row["verdict"] == "fail"),
        "pass_rate": passed / n if n else float("nan"),
        "wilson_pass_rate_ci95": _wilson(passed, n),
        "max_ratio": max(ratios) if ratios else float("nan"),
        "median_ratio": _median(ratios),
        "max_ratio_interior": max(interior) if interior else float("nan"),
        "transition_frames": CONSERVATION_FRAMES,
        "exact_relation_status": "deferred-uncalibrated-absolute-tolerance",
        "honesty_boundary": (
            "Reference-relative conservation-transition cells are clustered by "
            "checkpoint and frame over one source trajectory. The absolute "
            "mass-conservation relation remains deferred; this is a non-regression "
            "diagnostic, not proof of divergence-free flow. Wilson bounds are "
            "descriptive cell-level summaries, not independent-trial inference."
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
        "wilson_fail_rate_ci95": _wilson(fail, n),
        "median_rel_l2": _median(float(row["metric_value"]) for row in rows),
        "input_seeds": EXACT_SEEDS,
        "honesty_boundary": (
            "Exact-symmetric-mesh cells use synthetic no-obstacle channel inputs. "
            "They test structural mirror equivariance on an admissible relation, "
            "not in-distribution accuracy or calibrated cylinder-flow severity. "
            "Wilson bounds are descriptive cell-level summaries, not "
            "independent-trial inference."
        ),
    }


def run_upgrade(sut_repo: Path) -> dict[str, object]:
    sut_repo = Path(sut_repo).resolve()
    head = _read_git_head(sut_repo)
    if head != SOURCE_HEAD:
        raise ValueError(f"Minimum-MR-SubSet HEAD mismatch: expected {SOURCE_HEAD}, got {head}")
    if not SOURCE_CASE.exists():
        raise FileNotFoundError(SOURCE_CASE)
    missing = [str(path) for path in CHECKPOINTS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing checkpoint(s): {missing}")

    mirror_rows: list[dict[str, object]] = []
    conservation_rows: list[dict[str, object]] = []
    exact_rows: list[dict[str, object]] = []
    manifests: list[str] = []

    for checkpoint_id, checkpoint in CHECKPOINTS.items():
        mirror_dir = OUTDIR / checkpoint_id / "mirror_ood/raw"
        mirror_manifest = OUTDIR / checkpoint_id / "mirror_ood/manifest.yml"
        _write_manifest(
            mirror_manifest,
            {
                **_common_manifest_fields(
                    run_id=f"phase11-primary-volume-{checkpoint_id}-mirror-ood-001",
                    sut_repo=sut_repo,
                    checkpoint=checkpoint,
                    mr_id="mirror_y_ood_stress",
                    command=(
                        "python3 tools/run_mirror_y_ood_stress.py --manifest "
                        f"{_rel(mirror_manifest)} --frames 0,1,2,3,4,5,6,7,8,9"
                    ),
                    raw_output_dir=mirror_dir,
                    seed=20260612,
                ),
                "mirror_axis": 0.205,
                "ratio_threshold": 2.0,
            },
        )
        manifests.append(_rel(mirror_manifest))
        mirror_ledger = run_mirror_ood(mirror_manifest, frames=MIRROR_FRAMES)
        for entry in mirror_ledger["entries"]:
            mirror_rows.append(
                {
                    "checkpoint": checkpoint_id,
                    "checkpoint_sha256": mirror_ledger["checkpoint_sha256"],
                    "frame": entry["frame"],
                    "metric_value": entry["metric_value"],
                    "mapping_error_floor": entry["mapping_error_floor"],
                    "violation_over_floor": entry["violation_over_floor"],
                    "verdict": entry["verdict"],
                    "ledger": _rel(mirror_dir / "metric_ledger.json"),
                }
            )

        conservation_dir = OUTDIR / checkpoint_id / "conservation/raw"
        conservation_manifest = OUTDIR / checkpoint_id / "conservation/manifest.yml"
        _write_manifest(
            conservation_manifest,
            {
                **_common_manifest_fields(
                    run_id=f"phase11-primary-volume-{checkpoint_id}-conservation-001",
                    sut_repo=sut_repo,
                    checkpoint=checkpoint,
                    mr_id="discrete_divergence_reference_relative",
                    command=(
                        "python3 tools/run_conservation_diagnostic.py --manifest "
                        f"{_rel(conservation_manifest)} --frames 0,1,2,3,4,5,6,7,8"
                    ),
                    raw_output_dir=conservation_dir,
                    seed=20260612,
                ),
                "regression_threshold": 1.5,
                "absolute_divergence_tol": 0.000001,
            },
        )
        manifests.append(_rel(conservation_manifest))
        conservation_ledger = run_conservation(conservation_manifest, frames=CONSERVATION_FRAMES)
        for entry in conservation_ledger["entries"]:
            conservation_rows.append(
                {
                    "checkpoint": checkpoint_id,
                    "checkpoint_sha256": conservation_ledger["checkpoint_sha256"],
                    "frame": entry["frame"],
                    "metric_value": entry["metric_value"],
                    "ratio_interior": entry["ratio_interior"],
                    "verdict": entry["verdict"],
                    "ledger": _rel(conservation_dir / "metric_ledger.json"),
                }
            )

        for seed in EXACT_SEEDS:
            exact_dir = OUTDIR / checkpoint_id / f"exact_symmetric_seed{seed}/raw"
            exact_manifest = OUTDIR / checkpoint_id / f"exact_symmetric_seed{seed}/manifest.yml"
            _write_manifest(
                exact_manifest,
                {
                    **_common_manifest_fields(
                        run_id=f"phase11-primary-volume-{checkpoint_id}-exact-sym-{seed}",
                        sut_repo=sut_repo,
                        checkpoint=checkpoint,
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
                    "checkpoint_sha256": exact_ledger["checkpoint_sha256"],
                    "seed": seed,
                    "metric_value": exact_ledger["metric_value"],
                    "verdict": exact_ledger["verdict"],
                    "ledger": _rel(exact_dir / "metric_ledger.json"),
                }
            )

    report = {
        "record_type": "primary-empirical-volume-upgrade",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_repo": SOURCE_REPO,
        "source_head": SOURCE_HEAD,
        "sut_repo_local_path": str(sut_repo),
        "source_case": _rel(SOURCE_CASE),
        "mgn_checkpoints": list(CHECKPOINTS.keys()),
        "manifests": manifests,
        "mirror_ood": _summarize_mirror(mirror_rows),
        "conservation": _summarize_conservation(conservation_rows),
        "exact_symmetric_mesh": _summarize_exact(exact_rows),
        "per_checkpoint": {
            checkpoint_id: {
                "mirror_ood": _summarize_mirror(
                    [row for row in mirror_rows if row["checkpoint"] == checkpoint_id]
                ),
                "conservation": _summarize_conservation(
                    [row for row in conservation_rows if row["checkpoint"] == checkpoint_id]
                ),
                "exact_symmetric_mesh": _summarize_exact(
                    [row for row in exact_rows if row["checkpoint"] == checkpoint_id]
                ),
            }
            for checkpoint_id in CHECKPOINTS
        },
        "rows": {
            "mirror_ood": mirror_rows,
            "conservation": conservation_rows,
            "exact_symmetric_mesh": exact_rows,
        },
        "honesty_boundary": (
            "The upgraded cells are clustered by checkpoint and frame over one source "
            "trajectory from the DeepMind cylinder-flow eval artifact. They remove the "
            "literal 10-frame mirror-y, 2-frame conservation, and 1-input exact-symmetry "
            "pilot denominators, but they are not independent multi-trajectory estimates, "
            "not cross-SUT rates, and not reliability or accuracy claims. Report-level "
            "Wilson intervals are descriptive cell-count summaries, not "
            "independent-trial inference."
        ),
    }
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "primary_volume_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sut-repo", default="/private/tmp/minimum-mr-subset-audit")
    args = parser.parse_args(argv)
    report = run_upgrade(Path(args.sut_repo))
    mirror = report["mirror_ood"]
    conservation = report["conservation"]
    exact = report["exact_symmetric_mesh"]
    print(
        "primary volume upgrade complete: "
        f"mirror {mirror['fail_count']}/{mirror['total_frame_cells']} fail, "
        f"conservation {conservation['pass_count']}/{conservation['total_transition_cells']} pass, "
        f"exact-sym {exact['fail_count']}/{exact['total_input_cells']} fail"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
