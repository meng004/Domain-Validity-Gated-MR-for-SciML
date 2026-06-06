"""Rollout-accuracy baseline for the real MeshGraphNets cylinder-flow SUT.

This is the accuracy comparator requested by the Stage-3/Stage-4 reviewers: it
reports the SUT's one-step next-state prediction error on the SAME single eval
trajectory used by the mirror-y OOD-stress probe, so the manuscript can state
whether the mirror-y violation is visible, correlated, or distinct relative to
ordinary rollout error. It introduces no new SUT, dataset, or checkpoint.

Convention (verified against the SUT trainer, train_stage_a.py:277-278):
    v_pred(t+1) = v(t) + delta_norm.denormalize(model(node_feat_t, edge_feat, edge_index))
The metric is the per-transition relative L2 of v_pred against the ground-truth
next-state velocity, for transitions 0->1 ... 8->9 of the recorded trajectory.

Honesty boundary: this is one SUT, one checkpoint, one eval trajectory. It is an
accuracy diagnostic, not a reliability, baseline-superiority, or cross-SUT claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest_contract import parse_flat_manifest  # noqa: E402


def relative_l2(pred: np.ndarray, true: np.ndarray) -> float:
    pred = np.asarray(pred, dtype=np.float64)
    true = np.asarray(true, dtype=np.float64)
    denom = float(np.linalg.norm(true))
    num = float(np.linalg.norm(pred - true))
    if denom == 0.0:
        return 0.0 if num == 0.0 else float("inf")
    return num / denom


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def run_from_manifest(manifest_path: Path) -> dict[str, object]:
    manifest_path = Path(manifest_path)
    fields = parse_flat_manifest(manifest_path.read_text(encoding="utf-8"))
    repo_root = Path(__file__).resolve().parents[1]

    def _resolve(rel: str) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else (repo_root / p)

    sut_repo = Path(fields["sut_repo"])
    sys.path.insert(0, str(sut_repo / "scripts"))

    import torch  # noqa: PLC0415
    from mcmr.cylinder_flow import dm_dataset as ds  # noqa: PLC0415
    from mcmr.cylinder_flow.mgn import (  # noqa: PLC0415
        MeshGraphNet,
        Normalizer,
        edge_features,
        one_hot_node_type,
    )

    ckpt_path = _resolve(fields["checkpoint_path"])
    checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    cfg = checkpoint["config"]
    traj = ds.load_npz(_resolve(fields["source_case_path"]))

    edge_index_np = ds.build_edge_index(traj.cells, traj.num_nodes)
    vel_norm = Normalizer.from_dict(checkpoint["vel_norm"])
    delta_norm = Normalizer.from_dict(checkpoint["delta_norm"])
    edge_norm = Normalizer.from_dict(checkpoint["edge_norm"])
    onehot = torch.as_tensor(one_hot_node_type(traj.node_type))

    model = MeshGraphNet(node_in=cfg["node_in"], edge_in=cfg["edge_in"],
                         hidden=cfg["hidden"], out_dim=cfg["out_dim"],
                         num_layers=cfg["num_layers"])
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    edge_feat = edge_norm.normalize(
        torch.as_tensor(edge_features(traj.mesh_pos, edge_index_np))
    )
    edge_index = torch.as_tensor(edge_index_np, dtype=torch.long)

    def predict_next(v_t: np.ndarray) -> np.ndarray:
        v_t_t = torch.as_tensor(v_t)
        node_feat = torch.cat([vel_norm.normalize(v_t_t), onehot], dim=-1)
        with torch.no_grad():
            pred_dn = model(node_feat.to(torch.float32),
                            edge_feat.to(torch.float32), edge_index)
        delta = delta_norm.denormalize(pred_dn)
        return (v_t_t + delta).detach().numpy()

    raw_dir = _resolve(fields["raw_output_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)

    n_frames = int(traj.velocity.shape[0])
    transitions = []
    for t in range(n_frames - 1):
        v_pred = predict_next(traj.velocity[t])
        v_true = traj.velocity[t + 1]
        rel = relative_l2(v_pred, v_true)
        np.save(raw_dir / f"v_pred_{t:02d}_to_{t + 1:02d}.npy", v_pred)
        transitions.append({"from_frame": t, "to_frame": t + 1,
                            "metric_name": "one_step_relative_l2",
                            "metric_value": rel})

    rates = np.array([e["metric_value"] for e in transitions], dtype=np.float64)
    ledger = {
        "ledger_id": "real-sut-rollout-accuracy-baseline",
        "evidence_level": "real-sut-single-trajectory-accuracy-diagnostic",
        "schema_version": "0.1.0",
        "sut_repo": fields["sut_repo"],
        "sut_commit": fields["sut_commit"],
        "checkpoint_path": fields["checkpoint_path"],
        "checkpoint_sha256": _sha256(ckpt_path),
        "claim_limitations": (
            "Accuracy diagnostic: one real SUT, one checkpoint, one eval "
            "trajectory, one-step next-state prediction. Not a reliability, "
            "baseline-superiority, cross-SUT, or multi-trajectory claim."
        ),
        "metric_name": "one_step_relative_l2",
        "transitions": transitions,
        "summary": {
            "num_transitions": int(rates.shape[0]),
            "median_relative_l2": float(np.median(rates)),
            "mean_relative_l2": float(np.mean(rates)),
            "min_relative_l2": float(np.min(rates)),
            "max_relative_l2": float(np.max(rates)),
        },
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "num_nodes": int(traj.num_nodes),
        "num_edges": int(edge_index_np.shape[1]),
        "device": fields.get("device", "cpu"),
        "framework_version": fields.get("framework_version", f"torch {torch.__version__}"),
    }
    (raw_dir / "metric_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ledger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args(argv)
    ledger = run_from_manifest(Path(args.manifest))
    s = ledger["summary"]
    print(f"rollout-accuracy one-step relative L2 over {s['num_transitions']} "
          f"transitions: median={s['median_relative_l2']:.4f} "
          f"min={s['min_relative_l2']:.4f} max={s['max_relative_l2']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
