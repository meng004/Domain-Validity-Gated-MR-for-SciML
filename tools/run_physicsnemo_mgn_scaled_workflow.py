"""Run the scaled PhysicsNeMo MeshGraphNet cylinder-flow primary workflow.

This runner upgrades the P0c Object-A smoke workflow (single-trajectory,
wiring-test model) to a multi-trajectory CPU evaluation of the OFFICIAL
production MeshGraphNet architecture (15 message-passing steps, 128 hidden
units — the DeepMind/PhysicsNeMo default) on the official DeepMind
cylinder_flow TFRecords:

  - trains on the first N_train official train trajectories (CPU budget,
    documented honestly as not the official 10M-step schedule),
  - evaluates the MR battery per test trajectory on the first N_test official
    test trajectories: node-permutation equivariance, mirror-y OOD stress,
    reference-relative conservation diagnostic, one-step rollout accuracy,
  - writes per-trajectory metric ledgers (denominators in the tens, not 1),
    rubric decisions, raw outputs for the first few trajectories, and a
    workflow report with explicit honesty boundary and forbidden claims.

Data staging happens outside git under /workspace; only ledgers, the report,
the checkpoint, and bounded raw outputs land in the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import struct
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch_geometric.data import Data

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-vortex-shedding-scaled"
RAW_DIR = OUT_DIR / "raw_outputs"
STAGE_DIR = Path("/workspace/physicsnemo_staged_assets/mgn/cylinder_flow_scaled")
BASE_URL = "https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow"
CHECKPOINT = OUT_DIR / "physicsnemo_mgn_scaled_checkpoint.pt"
REPORT = OUT_DIR / "physicsnemo_mgn_scaled_workflow_report.json"
RUBRIC = OUT_DIR / "physicsnemo_mgn_scaled_rubric_decisions.json"
RESUME = STAGE_DIR / "resume_checkpoint.pt"

NODE_PERM_THRESHOLD = 1e-5
MIRROR_OOD_THRESHOLD = 0.1


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_prefix(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def fetch_range(url: str, start: int, length: int) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"Range": f"bytes={start}-{start + length - 1}",
                 "User-Agent": "DVGMR-PhysicsNeMo-scaled/1.0"})
    with urllib.request.urlopen(req, timeout=600) as response:
        return response.read()


def count_complete_records(blob: bytes) -> tuple[int, int]:
    """Return (n_records, end_offset) of complete TFRecord entries in blob."""
    off, n = 0, 0
    while off + 12 <= len(blob):
        rec_len = struct.unpack("<Q", blob[off:off + 8])[0]
        total = 12 + rec_len + 4
        if off + total > len(blob):
            break
        off += total
        n += 1
    return n, off


def stage_split(split: str, n_records: int) -> dict[str, Any]:
    """Range-download the first n_records TFRecord entries of a split."""
    target = STAGE_DIR / f"{split}.tfrecord"
    marker = STAGE_DIR / f"{split}.records.json"
    if target.exists() and marker.exists():
        st = json.loads(marker.read_text())
        if st.get("n_records") == n_records:
            return st
    url = f"{BASE_URL}/{split}.tfrecord"
    head = fetch_range(url, 0, 16)
    rec_len = struct.unpack("<Q", head[:8])[0]
    avg = 12 + rec_len + 4
    blob = b""
    want = int(avg * n_records * 1.2) + 4096
    while True:
        blob += fetch_range(url, len(blob), want - len(blob))
        n, end = count_complete_records(blob)
        if n >= n_records:
            # truncate to exactly n_records complete entries
            _, end = count_complete_records(blob)
            off, m = 0, 0
            while m < n_records:
                rl = struct.unpack("<Q", blob[off:off + 8])[0]
                off += 12 + rl + 4
                m += 1
            blob = blob[:off]
            break
        want += avg * max(n_records - n, 1)
    target.write_bytes(blob)
    st = {
        "split": split,
        "n_records": n_records,
        "bytes": len(blob),
        "sha256_prefix": sha256_prefix(target),
        "source_url": url,
        "staged_at": utc_now(),
    }
    marker.write_text(json.dumps(st, indent=2))
    return st


def stage_data(n_train: int, n_test: int) -> dict[str, Any]:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    meta = STAGE_DIR / "meta.json"
    if not meta.exists() or meta.stat().st_size < 100:
        with urllib.request.urlopen(f"{BASE_URL}/meta.json", timeout=60) as r:
            meta.write_bytes(r.read())
    train_st = stage_split("train", n_train)
    test_st = stage_split("test", n_test)
    valid = STAGE_DIR / "valid.tfrecord"
    if not valid.exists() or valid.stat().st_size != (STAGE_DIR / "test.tfrecord").stat().st_size:
        valid.write_bytes((STAGE_DIR / "test.tfrecord").read_bytes())
    return {
        "stage_dir": str(STAGE_DIR),
        "source_url_prefix": BASE_URL,
        "meta": {"path": str(meta), "bytes": meta.stat().st_size, "sha256_prefix": sha256_prefix(meta)},
        "records": [train_st, test_st],
        "valid_record_reused_from_test_for_datapipe_completeness": True,
        "subset_boundary": (
            f"first {n_train} official train trajectories and first {n_test} official test "
            "trajectories; CPU-scale evaluation of the official architecture, not the full "
            "1000/100-trajectory production benchmark"),
    }


def load_datasets(n_train: int, n_test: int, num_steps: int, noise_std: float):
    from physicsnemo.datapipes.gnn.vortex_shedding_dataset import VortexSheddingDataset

    cwd = Path.cwd()
    os.chdir(STAGE_DIR)
    try:
        train = VortexSheddingDataset(
            data_dir=str(STAGE_DIR), split="train", num_samples=n_train,
            num_steps=num_steps, noise_std=noise_std)
        test = VortexSheddingDataset(
            data_dir=str(STAGE_DIR), split="test", num_samples=n_test,
            num_steps=num_steps, noise_std=0.0)
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


def permuted_graph(graph: Data, seed: int) -> tuple[Data, np.ndarray]:
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
    # Normalized features are (u, v) then one-hot node type; mirror y flips v.
    x[:, 1] *= -1
    edge_attr = graph.edge_attr.clone()
    # Edge features are (dx, dy, norm); mirror y flips dy.
    edge_attr[:, 1] *= -1
    return clone_graph_with(x, graph.edge_index, edge_attr)


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(b.reshape(-1)))
    num = float(np.linalg.norm((a - b).reshape(-1)))
    return num / max(denom, 1e-12)


def train_model(model, train, args, losses_so_far, start_epoch):
    lr_schedule = [args.lr * (args.lr_decay ** e) for e in range(args.epochs)]
    opt = torch.optim.Adam(model.parameters(), lr=lr_schedule[start_epoch] if start_epoch < args.epochs else args.lr)
    losses = list(losses_so_far)
    n = len(train)
    order = np.arange(n)
    for epoch in range(start_epoch, args.epochs):
        for group in opt.param_groups:
            group["lr"] = lr_schedule[epoch]
        rng = np.random.default_rng(args.seed + epoch)
        rng.shuffle(order)
        model.train()
        epoch_loss = 0.0
        for step, idx in enumerate(order):
            graph = train[int(idx)]
            opt.zero_grad(set_to_none=True)
            pred = model(graph.x.float(), graph.edge_attr.float(), graph)
            loss = torch.mean((pred - graph.y.float()) ** 2)
            loss.backward()
            opt.step()
            epoch_loss += float(loss.detach().cpu())
            if (step + 1) % 200 == 0:
                print(f"epoch {epoch} step {step + 1}/{n} mean-loss {epoch_loss / (step + 1):.5f}", flush=True)
        losses.append(epoch_loss / max(n, 1))
        torch.save({"model_state_dict": model.state_dict(),
                    "completed_epochs": epoch + 1,
                    "losses": losses}, RESUME)
        print(f"epoch {epoch} done: mean loss {losses[-1]:.5f}", flush=True)
    return losses


def evaluate(model, test, args) -> dict[str, Any]:
    num_steps = args.num_steps
    snapshots = sorted({0, (num_steps - 2) // 4, (num_steps - 2) // 2,
                        3 * (num_steps - 2) // 4, num_steps - 2})
    mid = snapshots[len(snapshots) // 2]
    n_traj = args.n_test

    rollout_rows, perm_rows, mirror_rows, conservation_rows = [], [], [], []
    raw_saved = 0
    for t in range(n_traj):
        for s in snapshots:
            graph, cells, rollout_mask = test[t * (num_steps - 1) + s]
            source = predict(model, graph).cpu().numpy()
            target = graph.y.detach().cpu().numpy()
            rollout_rows.append({
                "trajectory": t, "snapshot": s,
                "relative_l2": relative_l2(source, target)})
            vel_src = np.abs(np.sum(source[:, :2], axis=0))
            vel_tgt = np.abs(np.sum(target[:, :2], axis=0))
            src_mean, tgt_mean = float(np.mean(vel_src)), float(np.mean(vel_tgt))
            conservation_rows.append({
                "trajectory": t, "snapshot": s,
                "source_mean_abs_sum_velocity_delta": src_mean,
                "reference_mean_abs_sum_velocity_delta": tgt_mean,
                "ratio": src_mean / max(tgt_mean, 1e-12)})

        # __getitem__ mutates a shared graph object in place, so re-fetch the
        # mid-snapshot graph immediately before the follow-up executions.
        graph, cells, rollout_mask = test[t * (num_steps - 1) + mid]
        source = predict(model, graph).cpu().numpy()
        target = graph.y.detach().cpu().numpy()
        pgraph, perm = permuted_graph(graph, seed=args.seed + 1000 + t)
        perm_out = predict(model, pgraph).cpu().numpy()
        unpermuted = np.empty_like(perm_out)
        unpermuted[perm] = perm_out
        perm_rel = relative_l2(unpermuted, source)
        perm_rows.append({
            "trajectory": t, "snapshot": mid, "relative_l2": perm_rel,
            "passes": int(perm_rel <= NODE_PERM_THRESHOLD)})

        mgraph = mirror_y_graph(graph)
        mirror_out = predict(model, mgraph).cpu().numpy()
        expected = source.copy()
        expected[:, 1] *= -1
        mirror_rel = relative_l2(mirror_out, expected)
        mirror_rows.append({
            "trajectory": t, "snapshot": mid, "relative_l2": mirror_rel,
            "passes": int(mirror_rel <= MIRROR_OOD_THRESHOLD)})

        if raw_saved < args.raw_trajectories:
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                RAW_DIR / f"trajectory_{t:03d}_followup_outputs.npz",
                source_prediction=source,
                target=target,
                permutation_unpermuted_prediction=unpermuted,
                mirror_prediction=mirror_out,
                mirror_expected_prediction=expected,
                permutation=perm,
                cells=cells.detach().cpu().numpy(),
                rollout_mask=rollout_mask.detach().cpu().numpy())
            raw_saved += 1
        print(f"eval trajectory {t}: rollout(mid)={rollout_rows[-len(snapshots) + len(snapshots)//2]['relative_l2']:.4f} "
              f"perm={perm_rel:.2e} mirror={mirror_rel:.4f}", flush=True)

    return {
        "snapshots": snapshots,
        "mid_snapshot": mid,
        "rollout_rows": rollout_rows,
        "perm_rows": perm_rows,
        "mirror_rows": mirror_rows,
        "conservation_rows": conservation_rows,
    }


def write_outputs(args, data_record, losses, ev) -> dict[str, Any]:
    rollout = [r["relative_l2"] for r in ev["rollout_rows"]]
    perm_vals = [r["relative_l2"] for r in ev["perm_rows"]]
    mirror_vals = [r["relative_l2"] for r in ev["mirror_rows"]]
    cons_ratios = [r["ratio"] for r in ev["conservation_rows"]]
    perm_pass = sum(r["passes"] for r in ev["perm_rows"])
    mirror_pass = sum(r["passes"] for r in ev["mirror_rows"])
    n_perm, n_mirror = len(ev["perm_rows"]), len(ev["mirror_rows"])

    ledgers = {
        "rollout_accuracy_metric_ledger.json": {
            "relation": "one_step_rollout_accuracy",
            "metric": "relative_l2(predicted_normalized_velocity_pressure_delta, target)",
            "denominator": len(rollout),
            "median_relative_l2": float(np.median(rollout)),
            "p90_relative_l2": float(np.percentile(rollout, 90)),
            "rows": ev["rollout_rows"],
            "verdict": "diagnostic-recorded",
        },
        "node_permutation_metric_ledger.json": {
            "relation": "node_permutation_equivariance",
            "metric": "relative_l2(unpermuted_followup_prediction, source_prediction)",
            "denominator": n_perm,
            "passes": perm_pass,
            "max_relative_l2": float(np.max(perm_vals)),
            "threshold": NODE_PERM_THRESHOLD,
            "rows": ev["perm_rows"],
            "verdict": "pass" if perm_pass == n_perm else "fail",
        },
        "mirror_ood_stress_metric_ledger.json": {
            "relation": "mirror_y_ood_stress",
            "metric": "relative_l2(mirror_prediction, mirrored_source_prediction)",
            "denominator": n_mirror,
            "passes": mirror_pass,
            "min_relative_l2": float(np.min(mirror_vals)),
            "median_relative_l2": float(np.median(mirror_vals)),
            "max_relative_l2": float(np.max(mirror_vals)),
            "threshold": MIRROR_OOD_THRESHOLD,
            "rows": ev["mirror_rows"],
            "verdict": "pass" if mirror_pass == n_mirror else "fail-as-ood-stress",
        },
        "conservation_reference_relative_metric_ledger.json": {
            "relation": "reference_relative_conservation_diagnostic",
            "metric": "abs_sum_velocity_delta_ratio_vs_reference_target",
            "denominator": len(cons_ratios),
            "median_ratio": float(np.median(cons_ratios)),
            "p90_ratio": float(np.percentile(cons_ratios, 90)),
            "rows": ev["conservation_rows"],
            "verdict": "diagnostic-recorded",
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, payload in ledgers.items():
        (OUT_DIR / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rubric = {
        "object_id": "physicsnemo-mgn-vortex-shedding-scaled",
        "admitted_relations": ["node_permutation_equivariance"],
        "downgraded_relations": ["mirror_y_ood_stress", "reference_relative_conservation_diagnostic"],
        "rejected_relations": ["boundary-changing transforms", "geometry-independent validity claims"],
        "execution_boundary": (
            f"PhysicsNeMo MeshGraphNet official architecture (processor_size={args.processor_size}, "
            f"hidden={args.hidden}) trained on CPU for {args.epochs} epochs over the first "
            f"{args.n_train} official DeepMind cylinder_flow train trajectories; evaluated on the "
            f"first {args.n_test} official test trajectories"),
    }
    RUBRIC.write_text(json.dumps(rubric, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "record_type": "physicsnemo-mgn-scaled-primary-workflow",
        "schema_version": "0.1.0",
        "generated_at": utc_now(),
        "object_id": "physicsnemo-mgn-vortex-shedding-scaled",
        "sut_name": "NVIDIA PhysicsNeMo MeshGraphNet (official production architecture)",
        "domain": "DeepMind cylinder_flow / vortex shedding",
        "production_framework": "nvidia-physicsnemo",
        "workflow_status": "completed-scaled-cpu-subset",
        "architecture": {
            "processor_size": args.processor_size,
            "hidden_dim": args.hidden,
            "official_default": args.processor_size == 15 and args.hidden == 128,
            "n_parameters": None,  # filled below
        },
        "data": data_record,
        "training": {
            "n_train_trajectories": args.n_train,
            "num_steps": args.num_steps,
            "noise_std": args.noise_std,
            "epochs": args.epochs,
            "lr": args.lr,
            "lr_decay": args.lr_decay,
            "seed": args.seed,
            "losses": losses,
            "final_loss": losses[-1] if losses else math.nan,
        },
        "evaluation": {
            "n_test_trajectories": args.n_test,
            "snapshots_per_trajectory": ev["snapshots"],
            "mid_snapshot": ev["mid_snapshot"],
        },
        "artifacts": {
            "checkpoint": str(CHECKPOINT.relative_to(ROOT)),
            "raw_outputs_dir": str(RAW_DIR.relative_to(ROOT)),
            "rubric_decisions": str(RUBRIC.relative_to(ROOT)),
            "metric_ledgers": {name.removesuffix(".json"): str((OUT_DIR / name).relative_to(ROOT)) for name in ledgers},
        },
        "metrics": {
            "rollout_median_relative_l2": float(np.median(rollout)),
            "node_permutation_passes": f"{perm_pass}/{n_perm}",
            "node_permutation_max_relative_l2": float(np.max(perm_vals)),
            "mirror_ood_stress_passes": f"{mirror_pass}/{n_mirror}",
            "mirror_ood_stress_median_relative_l2": float(np.median(mirror_vals)),
            "conservation_median_ratio": float(np.median(cons_ratios)),
        },
        "relation_verdicts": {name.removesuffix("_metric_ledger.json"): payload["verdict"] for name, payload in ledgers.items()},
        "honesty_boundary": (
            "This is a CPU-scale evaluation of the official PhysicsNeMo MeshGraphNet "
            f"production architecture trained for {args.epochs} epochs on the first "
            f"{args.n_train} official DeepMind cylinder_flow train trajectories and "
            f"evaluated per-trajectory on the first {args.n_test} official test "
            "trajectories. It is an independent production-framework implementation on "
            "the same task as the in-repo primary workflow, but it is NOT the official "
            "10M-step training schedule, NOT an official NVIDIA checkpoint, and NOT the "
            "full 1000/100-trajectory benchmark; rollout accuracy is one-step, not "
            "closed-loop."),
        "forbidden_claims": [
            "official-checkpoint behaviour",
            "full production-benchmark pass/fail rate",
            "closed-loop rollout accuracy",
            "AeroGraphNet workflow result",
            "DoMINO workflow result",
            "cross-dataset reliability",
            "geometry-independent validity",
        ],
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def run(args: argparse.Namespace) -> dict[str, Any]:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.set_num_threads(args.threads)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data_record = stage_data(args.n_train, args.n_test)
    train, test = load_datasets(args.n_train, args.n_test, args.num_steps, args.noise_std)
    model = build_model(args.hidden, args.processor_size)

    start_epoch, losses = 0, []
    if RESUME.exists():
        state = torch.load(RESUME, map_location="cpu", weights_only=True)
        if state.get("completed_epochs", 0) > 0:
            model.load_state_dict(state["model_state_dict"])
            start_epoch = state["completed_epochs"]
            losses = state["losses"]
            print(f"resuming from epoch {start_epoch}", flush=True)

    losses = train_model(model, train, args, losses, start_epoch)
    ev = evaluate(model, test, args)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "constructor": {"input_dim_nodes": 6, "input_dim_edges": 3, "output_dim": 3,
                            "hidden": args.hidden, "processor_size": args.processor_size},
            "training": {"n_train": args.n_train, "num_steps": args.num_steps,
                         "noise_std": args.noise_std, "epochs": args.epochs,
                         "lr": args.lr, "lr_decay": args.lr_decay, "seed": args.seed,
                         "losses": losses},
            "data": data_record,
        },
        CHECKPOINT,
    )
    report = write_outputs(args, data_record, losses, ev)
    n_params = sum(p.numel() for p in model.parameters())
    report["architecture"]["n_parameters"] = int(n_params)
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-train", type=int, default=25)
    parser.add_argument("--n-test", type=int, default=40)
    parser.add_argument("--num-steps", type=int, default=150)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--processor-size", type=int, default=15)
    parser.add_argument("--noise-std", type=float, default=0.02)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--lr-decay", type=float, default=0.3)
    parser.add_argument("--seed", type=int, default=20260612)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--raw-trajectories", type=int, default=3,
                        help="number of test trajectories whose raw outputs are committed")
    args = parser.parse_args()
    report = run(args)
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"workflow_status={report['workflow_status']}")
    for k, v in report["metrics"].items():
        print(f"  {k}={v}")


if __name__ == "__main__":
    main()
