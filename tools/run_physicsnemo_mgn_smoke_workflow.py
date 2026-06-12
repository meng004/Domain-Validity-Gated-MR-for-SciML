"""Run an artifact-gated PhysicsNeMo MeshGraphNet cylinder-flow smoke workflow.

This runner closes the P0c Object-A checkpoint/raw-output/metric-ledger gap for a
minimal CPU-executable slice: it uses the official PhysicsNeMo MeshGraphNet class
and first-record DeepMind cylinder_flow TFRecord smoke subset staged outside git.
It intentionally does not claim a full production-scale benchmark or Object-B/C
coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import struct
import urllib.request
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch_geometric.data import Data

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-vortex-shedding"
STAGE_DIR = Path("/workspace/physicsnemo_staged_assets/mgn/cylinder_flow_smoke")
BASE_URL = "https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow"
RAW_DIR = OUT_DIR / "raw_outputs"
CHECKPOINT = OUT_DIR / "physicsnemo_mgn_smoke_checkpoint.pt"
REPORT = OUT_DIR / "physicsnemo_mgn_smoke_workflow_report.json"
RUBRIC = OUT_DIR / "physicsnemo_mgn_smoke_rubric_decisions.json"
SMOKE = OUT_DIR / "physicsnemo_mgn_smoke_manifest.json"


def sha256_prefix(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def fetch_url(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response:
        target.write_bytes(response.read())


def fetch_first_tfrecord_record(split: str, target: Path) -> dict[str, Any]:
    url = f"{BASE_URL}/{split}.tfrecord"
    if target.exists() and target.stat().st_size > 16:
        return {"split": split, "path": str(target), "bytes": target.stat().st_size, "sha256_prefix": sha256_prefix(target), "downloaded": False}
    head_req = urllib.request.Request(url, headers={"Range": "bytes=0-15", "User-Agent": "DVGMR-PhysicsNeMo-smoke/1.0"})
    with urllib.request.urlopen(head_req, timeout=60) as response:
        head = response.read(16)
    if len(head) != 16:
        raise RuntimeError(f"Could not read TFRecord header for {split}: got {len(head)} bytes")
    record_len = struct.unpack("<Q", head[:8])[0]
    total = 12 + record_len + 4
    data_req = urllib.request.Request(url, headers={"Range": f"bytes=0-{total - 1}", "User-Agent": "DVGMR-PhysicsNeMo-smoke/1.0"})
    with urllib.request.urlopen(data_req, timeout=180) as response:
        data = response.read()
    if len(data) != total:
        raise RuntimeError(f"Partial first-record download for {split}: expected {total}, got {len(data)}")
    target.write_bytes(data)
    return {"split": split, "path": str(target), "bytes": total, "payload_bytes": record_len, "sha256_prefix": sha256_prefix(target), "downloaded": True}


def stage_smoke_data() -> dict[str, Any]:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    meta = STAGE_DIR / "meta.json"
    if not meta.exists():
        fetch_url(f"{BASE_URL}/meta.json", meta)
    records = [fetch_first_tfrecord_record(split, STAGE_DIR / f"{split}.tfrecord") for split in ("train", "test")]
    valid = STAGE_DIR / "valid.tfrecord"
    if not valid.exists():
        shutil.copyfile(STAGE_DIR / "test.tfrecord", valid)
    return {
        "stage_dir": str(STAGE_DIR),
        "source_url_prefix": BASE_URL,
        "meta": {"path": str(meta), "bytes": meta.stat().st_size, "sha256_prefix": sha256_prefix(meta)},
        "records": records,
        "valid_record_reused_from_test_for_datapipe_completeness": True,
        "subset_boundary": "first complete TFRecord trajectory for train and test only; used for CPU smoke workflow, not full production-scale evaluation",
    }


def load_datasets(num_steps: int):
    from physicsnemo.datapipes.gnn.vortex_shedding_dataset import VortexSheddingDataset

    # PhysicsNeMo's datapipe writes/reads edge_stats.json and node_stats.json in
    # the current working directory. Keep those generated stats outside git in
    # the staging directory rather than polluting the repository root.
    cwd = Path.cwd()
    os.chdir(STAGE_DIR)
    try:
        train = VortexSheddingDataset(data_dir=str(STAGE_DIR), split="train", num_samples=1, num_steps=num_steps, noise_std=0.0)
        test = VortexSheddingDataset(data_dir=str(STAGE_DIR), split="test", num_samples=1, num_steps=num_steps, noise_std=0.0)
    finally:
        os.chdir(cwd)
    return train, test


def build_model(hidden: int, processor_size: int):
    from physicsnemo.models.meshgraphnet import MeshGraphNet

    return MeshGraphNet(
        input_dim_nodes=6,
        input_dim_edges=3,
        output_dim=3,
        processor_size=processor_size,
        hidden_dim_processor=hidden,
        hidden_dim_node_encoder=hidden,
        hidden_dim_edge_encoder=hidden,
        hidden_dim_node_decoder=hidden,
        num_layers_node_processor=2,
        num_layers_edge_processor=2,
        num_layers_node_encoder=2,
        num_layers_edge_encoder=2,
        num_layers_node_decoder=2,
        aggregation="sum",
    )


def clone_graph_with(x: torch.Tensor, edge_index: torch.Tensor, edge_attr: torch.Tensor) -> Data:
    return Data(edge_index=edge_index.clone(), edge_attr=edge_attr.clone(), x=x.clone())


def predict(model: torch.nn.Module, graph: Data) -> torch.Tensor:
    model.eval()
    with torch.no_grad():
        return model(graph.x.float(), graph.edge_attr.float(), graph)


def permuted_graph(graph: Data, seed: int = 17) -> tuple[Data, np.ndarray]:
    rng = np.random.default_rng(seed)
    n = int(graph.x.shape[0])
    perm = rng.permutation(n)
    inv = np.empty_like(perm)
    inv[perm] = np.arange(n)
    edge_index = graph.edge_index.detach().cpu().numpy()
    edge_index_p = torch.as_tensor(inv[edge_index], dtype=torch.long)
    x_p = graph.x[torch.as_tensor(perm, dtype=torch.long)]
    return clone_graph_with(x_p, edge_index_p, graph.edge_attr), perm


def mirror_y_graph(graph: Data) -> Data:
    x = graph.x.clone()
    # Velocity feature order is (u, v) followed by one-hot node type; mirror y flips v.
    x[:, 1] *= -1
    edge_attr = graph.edge_attr.clone()
    # Edge features are (dx, dy, norm); mirror y flips dy.
    edge_attr[:, 1] *= -1
    return clone_graph_with(x, graph.edge_index, edge_attr)


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(b.reshape(-1)))
    num = float(np.linalg.norm((a - b).reshape(-1)))
    return num / max(denom, 1e-12)


def run(args: argparse.Namespace) -> dict[str, Any]:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    data_record = stage_smoke_data()
    train, test = load_datasets(args.num_steps)
    model = build_model(args.hidden, args.processor_size)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    losses: list[float] = []
    for _ in range(args.epochs):
        model.train()
        epoch_loss = 0.0
        for idx in range(len(train)):
            graph = train[idx]
            opt.zero_grad(set_to_none=True)
            pred = model(graph.x.float(), graph.edge_attr.float(), graph)
            loss = torch.mean((pred - graph.y.float()) ** 2)
            loss.backward()
            opt.step()
            epoch_loss += float(loss.detach().cpu())
        losses.append(epoch_loss / max(len(train), 1))

    test_graph, cells, rollout_mask = test[0]
    source = predict(model, test_graph).cpu().numpy()
    target = test_graph.y.detach().cpu().numpy()
    rollout_rel_l2 = relative_l2(source, target)

    perm_graph, perm = permuted_graph(test_graph)
    perm_out = predict(model, perm_graph).cpu().numpy()
    unpermuted = np.empty_like(perm_out)
    unpermuted[perm] = perm_out
    perm_rel = relative_l2(unpermuted, source)

    mirror_graph = mirror_y_graph(test_graph)
    mirror_out = predict(model, mirror_graph).cpu().numpy()
    expected_mirror = source.copy()
    expected_mirror[:, 1] *= -1
    mirror_rel = relative_l2(mirror_out, expected_mirror)

    vel_diff_source = source[:, :2]
    vel_diff_target = target[:, :2]
    source_mean_abs = float(np.mean(np.abs(np.sum(vel_diff_source, axis=0))))
    target_mean_abs = float(np.mean(np.abs(np.sum(vel_diff_target, axis=0))))
    conservation_ratio = source_mean_abs / max(target_mean_abs, 1e-12)

    np.savez_compressed(
        RAW_DIR / "source_followup_outputs.npz",
        source_prediction=source,
        target=target,
        permutation_unpermuted_prediction=unpermuted,
        mirror_prediction=mirror_out,
        mirror_expected_prediction=expected_mirror,
        permutation=perm,
        cells=cells.detach().cpu().numpy(),
        rollout_mask=rollout_mask.detach().cpu().numpy(),
    )
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "constructor": {"input_dim_nodes": 6, "input_dim_edges": 3, "output_dim": 3, "hidden": args.hidden, "processor_size": args.processor_size},
            "training": {"epochs": args.epochs, "lr": args.lr, "seed": args.seed, "losses": losses},
            "data": data_record,
        },
        CHECKPOINT,
    )

    ledgers = {
        "rollout_accuracy_metric_ledger.json": {
            "relation": "one_step_rollout_accuracy_smoke",
            "metric": "relative_l2(predicted_normalized_velocity_pressure_delta, target)",
            "denominator": 1,
            "median_relative_l2": rollout_rel_l2,
            "verdict": "diagnostic-recorded",
        },
        "node_permutation_metric_ledger.json": {
            "relation": "node_permutation_equivariance",
            "metric": "relative_l2(unpermuted_followup_prediction, source_prediction)",
            "denominator": 1,
            "max_relative_l2": perm_rel,
            "threshold": 1e-5,
            "passes": int(perm_rel <= 1e-5),
            "verdict": "pass" if perm_rel <= 1e-5 else "fail",
        },
        "mirror_ood_stress_metric_ledger.json": {
            "relation": "mirror_y_ood_stress",
            "metric": "relative_l2(mirror_prediction, mirrored_source_prediction)",
            "denominator": 1,
            "max_relative_l2": mirror_rel,
            "threshold": 0.1,
            "passes": int(mirror_rel <= 0.1),
            "verdict": "pass" if mirror_rel <= 0.1 else "fail-as-ood-stress",
        },
        "conservation_reference_relative_metric_ledger.json": {
            "relation": "reference_relative_conservation_diagnostic",
            "metric": "abs_sum_velocity_delta_ratio_vs_reference_target",
            "denominator": 1,
            "source_mean_abs_sum_velocity_delta": source_mean_abs,
            "reference_mean_abs_sum_velocity_delta": target_mean_abs,
            "ratio": conservation_ratio,
            "verdict": "diagnostic-recorded",
        },
    }
    for name, payload in ledgers.items():
        (OUT_DIR / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rubric = {
        "object_id": "physicsnemo-mgn-vortex-shedding",
        "admitted_relations": ["node_permutation_equivariance"],
        "downgraded_relations": ["mirror_y_ood_stress", "reference_relative_conservation_diagnostic"],
        "rejected_relations": ["boundary-changing transforms", "geometry-independent validity claims"],
        "execution_boundary": "PhysicsNeMo MeshGraphNet CPU smoke workflow on first-record official DeepMind cylinder_flow subset",
    }
    RUBRIC.write_text(json.dumps(rubric, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    smoke = {
        "physicsnemo_imported": True,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "checkpoint_path": str(CHECKPOINT.relative_to(ROOT)),
        "raw_outputs": str((RAW_DIR / "source_followup_outputs.npz").relative_to(ROOT)),
        "metric_ledgers": sorted(ledgers),
    }
    SMOKE.write_text(json.dumps(smoke, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = {
        "record_type": "physicsnemo-mgn-smoke-primary-workflow",
        "schema_version": "0.1.0",
        "generated_on": "2026-06-12",
        "object_id": "physicsnemo-mgn-vortex-shedding",
        "sut_name": "NVIDIA PhysicsNeMo MeshGraphNet",
        "domain": "DeepMind cylinder_flow / vortex shedding",
        "production_framework": "nvidia-physicsnemo",
        "workflow_status": "completed-smoke-subset",
        "task3_minimal_workflow_completed": True,
        "task3_full_scale_workflow_completed": False,
        "data": data_record,
        "training": {"epochs": args.epochs, "lr": args.lr, "seed": args.seed, "losses": losses, "final_loss": losses[-1] if losses else math.nan},
        "artifacts": {
            "checkpoint": str(CHECKPOINT.relative_to(ROOT)),
            "raw_outputs": str((RAW_DIR / "source_followup_outputs.npz").relative_to(ROOT)),
            "rubric_decisions": str(RUBRIC.relative_to(ROOT)),
            "smoke_manifest": str(SMOKE.relative_to(ROOT)),
            "metric_ledgers": {name.removesuffix(".json"): str((OUT_DIR / name).relative_to(ROOT)) for name in ledgers},
        },
        "metrics": {
            "rollout_relative_l2": rollout_rel_l2,
            "node_permutation_relative_l2": perm_rel,
            "mirror_ood_stress_relative_l2": mirror_rel,
            "reference_relative_conservation_ratio": conservation_ratio,
        },
        "relation_verdicts": {name.removesuffix("_metric_ledger.json"): payload["verdict"] for name, payload in ledgers.items() if name.endswith("_metric_ledger.json")},
        "honesty_boundary": "This is an executable PhysicsNeMo Object-A smoke workflow with a newly trained checkpoint, raw outputs, and metric ledgers on the first official TFRecord trajectory. It is not a full production-scale PhysicsNeMo benchmark and does not cover AeroGraphNet or DoMINO.",
        "forbidden_claims": [
            "production-scale PhysicsNeMo MGN pass/fail rate",
            "AeroGraphNet workflow result",
            "DoMINO workflow result",
            "cross-dataset reliability",
            "geometry-independent validity",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--num-steps", type=int, default=4)
    parser.add_argument("--hidden", type=int, default=16)
    parser.add_argument("--processor-size", type=int, default=1)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=20260612)
    args = parser.parse_args()
    report = run(args)
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"workflow_status={report['workflow_status']}")
    print(f"node_permutation_relative_l2={report['metrics']['node_permutation_relative_l2']:.3e}")


if __name__ == "__main__":
    main()
