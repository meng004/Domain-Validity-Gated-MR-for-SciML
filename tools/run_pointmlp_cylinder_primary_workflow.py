"""Train and evaluate a non-MGN PointMLP cylinder-flow SUT.

This is the P0b external-architecture step that is feasible inside this repo: a
row-wise coordinate/velocity/node-type MLP trained on committed DeepMind
cylinder_flow source-case trajectories.  It is intentionally not a graph neural
network and does not consume edge connectivity; the experiment is therefore a
real different architecture-family SUT on the same cylinder-flow domain, while
still not claiming PhysicsNeMo/EchoWave or cross-dataset generality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import torch
from torch import nn

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import conservation_rubric as conservation  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "research_assets/runs/primary-scope-upgrade/source_cases"
OUTDIR = ROOT / "research_assets/runs/pointmlp-cylinder-primary-workflow"
TRAIN_TRAJECTORIES = [0, 1]
EVAL_TRAJECTORIES = [2]
NODE_TYPE_CARDINALITY = 7
NODE_PERM_TOL = 1e-6
MIRROR_TOL = 1e-6
CONSERVATION_RATIO_TOL = 1.5
EXACT_SEEDS = [20260612, 20260613, 20260614]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _relative_l2(left: np.ndarray, right: np.ndarray) -> float:
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    denom = float(np.linalg.norm(right))
    num = float(np.linalg.norm(left - right))
    if denom == 0:
        return 0.0 if num == 0 else float("inf")
    return num / denom


def _median(values: Iterable[float]) -> float:
    seq = sorted(float(v) for v in values)
    if not seq:
        return float("nan")
    mid = len(seq) // 2
    return seq[mid] if len(seq) % 2 else (seq[mid - 1] + seq[mid]) / 2.0


def _wilson(successes: int, n: int, z: float = 1.959963984540054) -> list[float]:
    if n == 0:
        return [float("nan"), float("nan")]
    p = successes / n
    z2 = z * z
    denom = 1 + z2 / n
    center = (p + z2 / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) / n) + (z2 / (4 * n * n))) / denom
    return [max(0.0, center - margin), min(1.0, center + margin)]


def _case_path(idx: int) -> Path:
    return SOURCE_DIR / f"test_traj{idx:03d}_frames000_009.npz"


def _load_case(idx: int) -> dict[str, np.ndarray]:
    path = _case_path(idx)
    if not path.exists():
        raise FileNotFoundError(path)
    data = dict(np.load(path))
    data["path"] = np.asarray(str(path))
    return data


class PointMLP(nn.Module):
    def __init__(self, in_dim: int, hidden: int = 96, depth: int = 3) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        cur = in_dim
        for _ in range(depth):
            layers += [nn.Linear(cur, hidden), nn.Tanh()]
            cur = hidden
        layers.append(nn.Linear(cur, 2))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def _features(pos: np.ndarray, vel: np.ndarray, node_type: np.ndarray) -> np.ndarray:
    node_type = np.asarray(node_type, dtype=np.int64)
    onehot = np.eye(NODE_TYPE_CARDINALITY, dtype=np.float32)[np.clip(node_type, 0, NODE_TYPE_CARDINALITY - 1)]
    return np.concatenate([pos.astype(np.float32), vel.astype(np.float32), onehot], axis=1)


def _fit_normalizer(x: np.ndarray, y: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "x_mean": x.mean(axis=0).astype(np.float32),
        "x_std": (x.std(axis=0) + 1e-6).astype(np.float32),
        "y_mean": y.mean(axis=0).astype(np.float32),
        "y_std": (y.std(axis=0) + 1e-6).astype(np.float32),
    }


def _normalize(x: np.ndarray, stats: dict[str, np.ndarray]) -> np.ndarray:
    return (x - stats["x_mean"]) / stats["x_std"]


def _denormalize_y(y: np.ndarray, stats: dict[str, np.ndarray]) -> np.ndarray:
    return y * stats["y_std"] + stats["y_mean"]


def _make_training_arrays(cases: dict[int, dict[str, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for idx in TRAIN_TRAJECTORIES:
        case = cases[idx]
        pos = case["mesh_pos"]
        node_type = case["node_type"]
        vel = case["velocity"]
        for frame in range(vel.shape[0] - 1):
            xs.append(_features(pos, vel[frame], node_type))
            ys.append((vel[frame + 1] - vel[frame]).astype(np.float32))
    return np.concatenate(xs, axis=0), np.concatenate(ys, axis=0)


def train_pointmlp(epochs: int, hidden: int, lr: float) -> tuple[PointMLP, dict[str, np.ndarray], dict[str, object]]:
    torch.manual_seed(20260612)
    np.random.seed(20260612)
    random.seed(20260612)
    cases = {idx: _load_case(idx) for idx in TRAIN_TRAJECTORIES + EVAL_TRAJECTORIES}
    x, y = _make_training_arrays(cases)
    stats = _fit_normalizer(x, y)
    xt = torch.as_tensor(_normalize(x, stats), dtype=torch.float32)
    yt = torch.as_tensor((y - stats["y_mean"]) / stats["y_std"], dtype=torch.float32)
    model = PointMLP(xt.shape[1], hidden=hidden)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    losses: list[float] = []
    batch_size = min(4096, xt.shape[0])
    gen = torch.Generator().manual_seed(20260612)
    for _ in range(epochs):
        idx = torch.randint(0, xt.shape[0], (batch_size,), generator=gen)
        opt.zero_grad(set_to_none=True)
        pred = model(xt[idx])
        loss = torch.mean((pred - yt[idx]) ** 2)
        loss.backward()
        opt.step()
        losses.append(float(loss.detach()))
    model.eval()
    meta = {
        "train_samples": int(x.shape[0]),
        "train_trajectories": TRAIN_TRAJECTORIES,
        "eval_trajectories": EVAL_TRAJECTORIES,
        "epochs": epochs,
        "hidden": hidden,
        "learning_rate": lr,
        "batch_size": int(batch_size),
        "final_train_mse_normalized_delta": losses[-1],
    }
    return model, stats, meta


def _predict_next(model: PointMLP, stats: dict[str, np.ndarray], pos: np.ndarray, vel: np.ndarray, node_type: np.ndarray) -> np.ndarray:
    feat = _features(pos, vel, node_type)
    with torch.no_grad():
        delta_n = model(torch.as_tensor(_normalize(feat, stats), dtype=torch.float32)).numpy()
    delta = _denormalize_y(delta_n, stats)
    pred = vel.astype(np.float32) + delta.astype(np.float32)
    # Respect prescribed obstacle/wall/inflow nodes as a conservative implementation contract.
    prescribed = np.asarray(node_type) != 0
    pred[prescribed] = vel[prescribed]
    return pred.astype(np.float32)


def _reflection_map(pos: np.ndarray, axis: float) -> tuple[np.ndarray, float]:
    reflected = pos.copy()
    reflected[:, 1] = 2 * axis - reflected[:, 1]
    diff = reflected[:, None, :] - pos[None, :, :]
    dist2 = np.sum(diff * diff, axis=2)
    mapping = np.argmin(dist2, axis=1)
    nearest = np.sqrt(dist2[np.arange(pos.shape[0]), mapping])
    # Normalize by median edge-like nearest-neighbour spacing.
    nn = np.partition(np.where(dist2 == 0, np.inf, dist2), 0, axis=1)[:, 0]
    spacing = float(np.median(np.sqrt(nn)))
    floor = float(np.max(nearest) / spacing) if spacing > 0 else float("inf")
    return mapping.astype(np.int64), floor


def _mirror_velocity(v: np.ndarray) -> np.ndarray:
    out = np.asarray(v).copy()
    out[:, 1] *= -1
    return out


def _evaluate_node_perm(model: PointMLP, stats: dict[str, np.ndarray], case: dict[str, np.ndarray], outdir: Path) -> list[dict[str, object]]:
    rows = []
    rng = np.random.default_rng(20260612)
    pos, node_type, vel = case["mesh_pos"], case["node_type"], case["velocity"]
    for frame in range(vel.shape[0] - 1):
        source = _predict_next(model, stats, pos, vel[frame], node_type)
        perm = rng.permutation(pos.shape[0])
        inv = np.empty_like(perm)
        inv[perm] = np.arange(perm.shape[0])
        follow = _predict_next(model, stats, pos[perm], vel[frame][perm], node_type[perm])
        mapped = follow[inv]
        metric = _relative_l2(mapped, source)
        verdict = "pass" if metric <= NODE_PERM_TOL else "fail"
        raw = outdir / "node_permutation" / f"frame{frame:02d}.npz"
        raw.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(raw, source_output=source, followup_output=follow, mapped_output=mapped, permutation=perm, inverse_permutation=inv)
        rows.append({"frame": frame, "metric_value": metric, "threshold": NODE_PERM_TOL, "verdict": verdict, "raw_output": _rel(raw)})
    return rows


def _evaluate_mirror_ood(model: PointMLP, stats: dict[str, np.ndarray], case: dict[str, np.ndarray], outdir: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows = []
    pos, node_type, vel = case["mesh_pos"], case["node_type"], case["velocity"]
    axis = float((pos[:, 1].min() + pos[:, 1].max()) / 2.0)
    mapping, floor_units = _reflection_map(pos, axis)
    mapped_pos_error_floor = max(floor_units / (floor_units + 1.0), 1e-12)
    for frame in range(vel.shape[0]):
        source = _predict_next(model, stats, pos, vel[frame], node_type)
        follow_input_vel = _mirror_velocity(vel[frame][mapping])
        follow = _predict_next(model, stats, pos, follow_input_vel, node_type)
        mapped = _mirror_velocity(follow[mapping])
        metric = _relative_l2(mapped, source)
        verdict = "fail" if metric > MIRROR_TOL else "pass"
        raw = outdir / "mirror_ood" / f"frame{frame:02d}.npz"
        raw.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(raw, source_output=source, followup_output=follow, mapped_output=mapped, reflection_map=mapping)
        rows.append({
            "frame": frame,
            "metric_value": metric,
            "threshold": MIRROR_TOL,
            "mapping_error_floor": mapped_pos_error_floor,
            "violation_over_floor": float(metric / mapped_pos_error_floor),
            "verdict": verdict,
            "exact_relation_verdict": "out-of-relation-domain",
            "raw_output": _rel(raw),
        })
    precondition = {
        "mirror_axis": axis,
        "reflection_floor_median_edge_units": floor_units,
        "domain_violation_score": mapped_pos_error_floor,
        "decision": "downgraded-to-ood-stress",
    }
    return rows, precondition


def _evaluate_conservation(model: PointMLP, stats: dict[str, np.ndarray], case: dict[str, np.ndarray], outdir: Path) -> list[dict[str, object]]:
    rows = []
    pos, cells, node_type, vel = case["mesh_pos"], case["cells"], case["node_type"], case["velocity"]
    mask = conservation.interior_cell_mask(cells, node_type)
    for frame in range(vel.shape[0] - 1):
        pred = _predict_next(model, stats, pos, vel[frame], node_type)
        ref = vel[frame + 1]
        div_pred, _ = conservation.cell_divergence(pos, cells, pred)
        div_ref, _ = conservation.cell_divergence(pos, cells, ref)
        pred_rms = conservation.divergence_rms(pos, cells, pred)
        ref_rms = conservation.divergence_rms(pos, cells, ref)
        ratio = float(pred_rms / ref_rms) if ref_rms > 0 else float("inf")
        pred_i = conservation.divergence_rms(pos, cells, pred, mask=mask)
        ref_i = conservation.divergence_rms(pos, cells, ref, mask=mask)
        ratio_i = float(pred_i / ref_i) if ref_i > 0 else float("inf")
        verdict = "pass" if ratio <= CONSERVATION_RATIO_TOL else "fail"
        raw = outdir / "conservation" / f"frame{frame:02d}.npz"
        raw.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(raw, predicted_next_velocity=pred, reference_next_velocity=ref, cell_divergence_pred=div_pred, cell_divergence_reference=div_ref)
        rows.append({
            "frame": frame,
            "metric_value": ratio,
            "threshold": CONSERVATION_RATIO_TOL,
            "ratio_interior": ratio_i,
            "divergence_pred_rms": float(pred_rms),
            "divergence_reference_rms": float(ref_rms),
            "exact_relation_status": conservation.DEFERRED_UNCALIBRATED,
            "verdict": verdict,
            "raw_output": _rel(raw),
        })
    return rows


def _synthetic_symmetric_input(seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    nx, half = 32, 14
    x = np.linspace(0.0, 1.6, nx, dtype=np.float32)
    y_top = np.linspace(0.02, 0.39, half, dtype=np.float32)
    y = np.concatenate([y_top, 0.41 - y_top[::-1]]).astype(np.float32)
    xx, yy = np.meshgrid(x, y, indexing="xy")
    pos = np.stack([xx.ravel(), yy.ravel()], axis=1).astype(np.float32)
    profile = 4.0 * (yy.ravel() - y.min()) * (y.max() - yy.ravel()) / ((y.max() - y.min()) ** 2)
    vx = profile + 0.02 * rng.normal(size=profile.shape)
    vy = 0.03 * np.sin(2 * np.pi * xx.ravel() / 1.6) * (yy.ravel() - 0.205)
    vel = np.stack([vx, vy], axis=1).astype(np.float32)
    node_type = np.zeros(pos.shape[0], dtype=np.int32)
    # Exact pair map by construction: rows are mirrored in y.
    mapping = np.arange(pos.shape[0]).reshape(y.shape[0], x.shape[0])[::-1].ravel()
    return pos, vel, node_type, mapping.astype(np.int64)


def _evaluate_exact_symmetric(model: PointMLP, stats: dict[str, np.ndarray], outdir: Path) -> list[dict[str, object]]:
    rows = []
    for seed in EXACT_SEEDS:
        pos, vel, node_type, mapping = _synthetic_symmetric_input(seed)
        source = _predict_next(model, stats, pos, vel, node_type)
        follow_input_vel = _mirror_velocity(vel[mapping])
        follow = _predict_next(model, stats, pos, follow_input_vel, node_type)
        mapped = _mirror_velocity(follow[mapping])
        metric = _relative_l2(mapped, source)
        verdict = "pass" if metric <= MIRROR_TOL else "fail"
        raw = outdir / "exact_symmetric_mesh" / f"seed{seed}.npz"
        raw.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(raw, mesh_pos=pos, input_velocity=vel, node_type=node_type, reflection_map=mapping, source_output=source, followup_output=follow, mapped_output=mapped)
        rows.append({"seed": seed, "metric_value": metric, "threshold": MIRROR_TOL, "verdict": verdict, "raw_output": _rel(raw)})
    return rows


def _evaluate_rollout(model: PointMLP, stats: dict[str, np.ndarray], case: dict[str, np.ndarray], outdir: Path) -> list[dict[str, object]]:
    rows = []
    pos, node_type, vel = case["mesh_pos"], case["node_type"], case["velocity"]
    for frame in range(vel.shape[0] - 1):
        pred = _predict_next(model, stats, pos, vel[frame], node_type)
        metric = _relative_l2(pred, vel[frame + 1])
        raw = outdir / "rollout" / f"frame{frame:02d}.npz"
        raw.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(raw, predicted_next_velocity=pred, reference_next_velocity=vel[frame + 1])
        rows.append({"frame": frame, "relative_l2": metric, "raw_output": _rel(raw)})
    return rows



def _write_metric_ledger(name: str, rows: list[dict[str, object]], *, relation_id: str, evidence_level: str) -> str:
    ledger_path = OUTDIR / f"{name}_metric_ledger.json"
    for row in rows:
        raw = ROOT / str(row["raw_output"])
        if not raw.exists():
            raise FileNotFoundError(f"metric ledger row references missing raw output: {raw}")
    ledger = {
        "ledger_id": f"pointmlp-cylinder-{name}-metric-ledger",
        "schema_version": "0.1.0",
        "sut_id": "pointmlp-cylinder-sut-v1",
        "relation_id": relation_id,
        "evidence_level": evidence_level,
        "entries": rows,
        "raw_outputs": [row["raw_output"] for row in rows],
    }
    ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    return _rel(ledger_path)

def _summarize(rows: list[dict[str, object]], pass_label: str = "pass") -> dict[str, object]:
    n = len(rows)
    passes = sum(row.get("verdict") == pass_label for row in rows)
    return {
        "total_case_cells": n,
        f"{pass_label}_count": passes,
        "other_count": n - passes,
        f"{pass_label}_rate_wilson_ci95": _wilson(passes, n),
        "median_metric_value": _median(row["metric_value"] for row in rows),
        "max_metric_value": max(float(row["metric_value"]) for row in rows) if rows else float("nan"),
    }


def _rubric_decisions() -> list[dict[str, object]]:
    return [
        {
            "relation_id": "pointmlp-node-permutation-equivariance",
            "admissibility": "admitted",
            "basis": "row-wise point network shares weights across nodes and ignores node order",
            "tolerance_rule": f"relative L2 <= {NODE_PERM_TOL:g}",
        },
        {
            "relation_id": "pointmlp-mirror-y-ood-stress",
            "admissibility": "downgraded-to-ood-stress",
            "basis": "official cylinder-flow held-out meshes are not exact mirror-y domains",
            "tolerance_rule": f"relative L2 <= {MIRROR_TOL:g}; mapping floor recorded",
        },
        {
            "relation_id": "pointmlp-conservation-reference-relative",
            "admissibility": "diagnostic-not-absolute-mr",
            "basis": "absolute divergence-free tolerance remains uncalibrated on these cells",
            "tolerance_rule": f"pred/reference divergence RMS ratio <= {CONSERVATION_RATIO_TOL:g}",
        },
        {
            "relation_id": "pointmlp-mirror-y-exact-symmetric-mesh",
            "admissibility": "admitted-on-synthetic-symmetric-input",
            "basis": "synthetic structured channel input has exact y-reflection pairs",
            "tolerance_rule": f"relative L2 <= {MIRROR_TOL:g}",
        },
    ]


def run_workflow(epochs: int, hidden: int, lr: float) -> dict[str, object]:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    model, stats, train_meta = train_pointmlp(epochs, hidden, lr)
    ckpt_dir = OUTDIR / "sut"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    ckpt_path = ckpt_dir / "checkpoint.pt"
    torch.save({
        "state_dict": model.state_dict(),
        "stats": {k: v.tolist() for k, v in stats.items()},
        "config": {"in_dim": 11, "hidden": hidden, "depth": 3, "architecture": "PointMLP"},
        "train_meta": train_meta,
    }, ckpt_path)
    checkpoint_sha = _sha256(ckpt_path)

    case = _load_case(EVAL_TRAJECTORIES[0])
    rows_node = _evaluate_node_perm(model, stats, case, OUTDIR / "raw")
    rows_mirror, precondition = _evaluate_mirror_ood(model, stats, case, OUTDIR / "raw")
    rows_cons = _evaluate_conservation(model, stats, case, OUTDIR / "raw")
    rows_exact = _evaluate_exact_symmetric(model, stats, OUTDIR / "raw")
    rows_rollout = _evaluate_rollout(model, stats, case, OUTDIR / "raw")

    metric_ledgers = {
        "node_permutation": _write_metric_ledger(
            "node_permutation", rows_node,
            relation_id="pointmlp-node-permutation-equivariance",
            evidence_level="different-architecture-cylinder-flow-primary-workflow",
        ),
        "mirror_ood_stress": _write_metric_ledger(
            "mirror_ood_stress", rows_mirror,
            relation_id="pointmlp-mirror-y-ood-stress",
            evidence_level="different-architecture-cylinder-flow-primary-workflow",
        ),
        "conservation_reference_relative": _write_metric_ledger(
            "conservation_reference_relative", rows_cons,
            relation_id="pointmlp-conservation-reference-relative",
            evidence_level="different-architecture-cylinder-flow-primary-workflow",
        ),
        "exact_symmetric_mesh": _write_metric_ledger(
            "exact_symmetric_mesh", rows_exact,
            relation_id="pointmlp-mirror-y-exact-symmetric-mesh",
            evidence_level="different-architecture-cylinder-flow-primary-workflow",
        ),
        "rollout_accuracy": _write_metric_ledger(
            "rollout_accuracy", rows_rollout,
            relation_id="pointmlp-rollout-accuracy-diagnostic",
            evidence_level="different-architecture-cylinder-flow-primary-workflow",
        ),
    }

    rubric_path = OUTDIR / "rubric_decisions.json"
    rubric_path.write_text(json.dumps(_rubric_decisions(), indent=2) + "\n", encoding="utf-8")
    report = {
        "record_type": "pointmlp-cylinder-primary-workflow",
        "schema_version": "0.1.0",
        "generated_at": _utc_now(),
        "domain": "DeepMind cylinder_flow",
        "architecture_family": "PointMLP row-wise coordinate network",
        "sut_id": "pointmlp-cylinder-sut-v1",
        "checkpoint_path": _rel(ckpt_path),
        "checkpoint_sha256": checkpoint_sha,
        "train_meta": train_meta,
        "source_cases": {str(i): _rel(_case_path(i)) for i in TRAIN_TRAJECTORIES + EVAL_TRAJECTORIES},
        "full_workflow_flags": {
            "trained_checkpoint": True,
            "rubric_decisions": True,
            "source_followup_outputs": True,
            "metric_ledgers": True,
            "relation_verdicts": True,
            "different_architecture_from_mgn": True,
            "same_domain_real_dataset": True,
        },
        "rubric_decisions": _rel(rubric_path),
        "metric_ledgers": metric_ledgers,
        "rollout_accuracy": {
            "transition_cells": len(rows_rollout),
            "median_relative_l2": _median(row["relative_l2"] for row in rows_rollout),
            "max_relative_l2": max(float(row["relative_l2"]) for row in rows_rollout),
            "rows": rows_rollout,
        },
        "node_permutation": {"admissibility": "admitted", **_summarize(rows_node, "pass"), "rows": rows_node},
        "mirror_ood_stress": {
            "admissibility": "downgraded-to-ood-stress",
            **_summarize(rows_mirror, "fail"),
            "median_violation_over_floor": _median(row["violation_over_floor"] for row in rows_mirror),
            "precondition_report": precondition,
            "rows": rows_mirror,
        },
        "conservation_reference_relative": {
            "admissibility": "diagnostic-not-absolute-mr",
            **_summarize(rows_cons, "pass"),
            "max_ratio_interior": max(float(row["ratio_interior"]) for row in rows_cons),
            "honesty_boundary": "Absolute mass conservation remains deferred; this is a reference-relative diagnostic.",
            "rows": rows_cons,
        },
        "exact_symmetric_mesh": {"admissibility": "admitted-on-synthetic-symmetric-input", **_summarize(rows_exact, "fail"), "rows": rows_exact},
        "honesty_boundary": (
            "This is a newly trained non-MGN PointMLP SUT on committed DeepMind cylinder_flow "
            "source-case trajectories. It is a different architecture family from MeshGraphNet "
            "because it is row-wise and uses no graph message passing. It is not PhysicsNeMo, "
            "not EchoWave, not a production-quality CFD surrogate, and not a cross-dataset or "
            "geometry-independent reliability estimate."
        ),
    }
    report_path = OUTDIR / "pointmlp_cylinder_primary_workflow_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    smoke = {
        "record_type": "pointmlp-cylinder-primary-workflow-smoke-manifest",
        "generated_at": report["generated_at"],
        "command": f"python3 tools/run_pointmlp_cylinder_primary_workflow.py --epochs {epochs} --hidden {hidden} --lr {lr}",
        "report": _rel(report_path),
        "checkpoint": _rel(ckpt_path),
    }
    (OUTDIR / "smoke_manifest.json").write_text(json.dumps(smoke, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--lr", type=float, default=2e-3)
    args = parser.parse_args(argv)
    report = run_workflow(args.epochs, args.hidden, args.lr)
    print(
        "PointMLP cylinder primary workflow complete: "
        f"node_perm {report['node_permutation']['pass_count']}/{report['node_permutation']['total_case_cells']} pass; "
        f"mirror {report['mirror_ood_stress']['fail_count']}/{report['mirror_ood_stress']['total_case_cells']} fail; "
        f"conservation {report['conservation_reference_relative']['pass_count']}/{report['conservation_reference_relative']['total_case_cells']} pass; "
        f"exact {report['exact_symmetric_mesh']['fail_count']}/{report['exact_symmetric_mesh']['total_case_cells']} fail"
    )
    print("wrote research_assets/runs/pointmlp-cylinder-primary-workflow/pointmlp_cylinder_primary_workflow_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
