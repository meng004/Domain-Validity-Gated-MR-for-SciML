"""Run a PhysicsNeMo MeshGraphNet validity-gated MR workflow on the DeepMind
*airfoil* dataset --- a genuinely second CFD task (compressible, SU2-simulated
transonic flow over an aerofoil) on a second official dataset, distinct from
the incompressible cylinder-flow case study.

The point of this second task is not another pass/fail table: it is to show
that the *same* four-condition admissibility predicate produces a *different
typed inadmissibility structure* because the physics differs. Concretely:

  - node-permutation equivariance  : ADMITTED (representation contract; holds on
    any mesh), exact-by-construction.
  - incompressible divergence-free continuity : REJECTED at the physical-basis
    gate (condition i). On cylinder flow this relation is physically valid and
    is only DEFERRED at the numerical-decidability gate (condition iv); here the
    measured density varies by >3x across the field, so the incompressible
    assumption is physically false for this SUT and the relation is rejected on
    physical grounds, a categorically different verdict type.
  - compressible unsteady mass conservation d(rho)/dt + div(rho u) = 0 : the
    physically-correct replacement; its absolute discrete form is DEFERRED
    (the P1 operator floor on a coarse transonic mesh is uncalibratable, exactly
    as for cylinder incompressible continuity), and a reference-relative
    diagnostic is recorded.
  - mirror-y symmetry : REJECTED at the boundary/precondition gate --- the SU2
    airfoil trajectories carry a non-zero angle of attack, so reflection about
    the chord is not a physical symmetry of the boundary-value problem.

This runner stages official DeepMind airfoil TFRecord trajectories outside git,
trains a bounded CPU MeshGraphNet (the official architecture), and records the
typed rubric decisions, per-trajectory metric ledgers, and bounded raw outputs.
It is explicitly NOT a full-scale production airfoil benchmark.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch_geometric.data import Data

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from conservation_rubric import cell_divergence  # noqa: E402

OUT_DIR = ROOT / "research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-second-task"
RAW_DIR = OUT_DIR / "raw_outputs"
STAGE_DIR = Path("/workspace/airfoil_staged")
BASE_URL = "https://storage.googleapis.com/dm-meshgraphnets/airfoil"
CHECKPOINT = OUT_DIR / "physicsnemo_mgn_airfoil_checkpoint.pt"
REPORT = OUT_DIR / "physicsnemo_mgn_airfoil_workflow_report.json"
RUBRIC = OUT_DIR / "physicsnemo_mgn_airfoil_rubric_decisions.json"
RESUME = STAGE_DIR / "resume_checkpoint.pt"

NODE_PERM_THRESHOLD = 1e-5
NODE_TYPES = (0, 2, 4)  # observed airfoil node types: NORMAL, OUTFLOW, AIRFOIL/WALL


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
        url, headers={"Range": f"bytes={start}-{start + length - 1}",
                      "User-Agent": "DVGMR-airfoil/1.0"})
    with urllib.request.urlopen(url=req, timeout=600) as response:
        return response.read()


def count_complete_records(blob: bytes) -> tuple[int, int]:
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
    want = int(avg * n_records * 1.15) + 4096
    while True:
        blob += fetch_range(url, len(blob), want - len(blob))
        n, _ = count_complete_records(blob)
        if n >= n_records:
            off, m = 0, 0
            while m < n_records:
                rl = struct.unpack("<Q", blob[off:off + 8])[0]
                off += 12 + rl + 4
                m += 1
            blob = blob[:off]
            break
        want += avg * max(n_records - n, 1)
    target.write_bytes(blob)
    st = {"split": split, "n_records": n_records, "bytes": len(blob),
          "sha256_prefix": sha256_prefix(target), "source_url": url,
          "staged_at": utc_now()}
    marker.write_text(json.dumps(st, indent=2))
    return st


def stage_data(n_train: int, n_test: int) -> dict[str, Any]:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = STAGE_DIR / "meta.json"
    if not meta_path.exists() or meta_path.stat().st_size < 100:
        with urllib.request.urlopen(f"{BASE_URL}/meta.json", timeout=60) as r:
            meta_path.write_bytes(r.read())
    train_st = stage_split("train", n_train)
    test_st = stage_split("test", n_test)
    return {
        "stage_dir": str(STAGE_DIR), "source_url_prefix": BASE_URL,
        "meta": {"path": str(meta_path), "sha256_prefix": sha256_prefix(meta_path)},
        "records": [train_st, test_st],
        "simulator": json.loads(meta_path.read_text()).get("simulator"),
        "subset_boundary": (
            f"first {n_train} official train and {n_test} official test airfoil "
            "trajectories; CPU-scale second-task evaluation, not the full SU2 "
            "airfoil production benchmark"),
    }


def decode_record(rec_bytes: dict, meta: dict) -> dict:
    dm = {"float32": np.float32, "float64": np.float64, "int32": np.int32, "int64": np.int64}
    out = {}
    for k, v in meta["features"].items():
        dtype = dm[v["dtype"]]
        out[k] = np.frombuffer(rec_bytes[k], dtype=dtype).copy().reshape(v["shape"])
    return out


def iter_trajectories(split: str, meta: dict, limit: int):
    from tfrecord.torch.dataset import TFRecordDataset
    desc = {k: "byte" for k in meta["field_names"]}
    ds = TFRecordDataset(str(STAGE_DIR / f"{split}.tfrecord"), None, desc,
                         transform=lambda rec: decode_record(rec, meta))
    for i, rec in enumerate(ds):
        if i >= limit:
            break
        yield rec


def cell_to_edges(cells: np.ndarray) -> np.ndarray:
    src = cells[:, [0, 1, 2]].reshape(-1)
    dst = cells[:, [1, 2, 0]].reshape(-1)
    edge = np.stack([np.concatenate([src, dst]), np.concatenate([dst, src])], axis=0)
    return np.unique(edge, axis=1)


def one_hot(nt: np.ndarray) -> np.ndarray:
    oh = np.zeros((nt.shape[0], len(NODE_TYPES)), dtype=np.float32)
    for j, t in enumerate(NODE_TYPES):
        oh[:, j] = (nt == t).astype(np.float32)
    return oh


class AirfoilStats:
    """Online mean/std for node features and targets (z-score normalization)."""
    def __init__(self):
        self.n = 0
        self.feat_sum = None
        self.feat_sq = None
        self.tgt_sum = None
        self.tgt_sq = None

    def update(self, feat: np.ndarray, tgt: np.ndarray):
        if self.feat_sum is None:
            self.feat_sum = np.zeros(feat.shape[1]); self.feat_sq = np.zeros(feat.shape[1])
            self.tgt_sum = np.zeros(tgt.shape[1]); self.tgt_sq = np.zeros(tgt.shape[1])
        self.feat_sum += feat.sum(0); self.feat_sq += (feat ** 2).sum(0)
        self.tgt_sum += tgt.sum(0); self.tgt_sq += (tgt ** 2).sum(0)
        self.n += feat.shape[0]

    def finalize(self):
        fm = self.feat_sum / self.n
        fs = np.sqrt(np.maximum(self.feat_sq / self.n - fm ** 2, 1e-12))
        tm = self.tgt_sum / self.n
        ts = np.sqrt(np.maximum(self.tgt_sq / self.n - tm ** 2, 1e-12))
        # do not normalize one-hot node-type columns (indices 3..)
        fs[3:] = 1.0; fm[3:] = 0.0
        return fm.astype(np.float32), fs.astype(np.float32), tm.astype(np.float32), ts.astype(np.float32)


def build_graph(rec: dict, t: int):
    pos = rec["mesh_pos"][0].astype(np.float32)            # (N,2)
    cells = rec["cells"][0].astype(np.int64)               # (C,3)
    nt = rec["node_type"][0, :, 0].astype(np.int64)        # (N,)
    vel = rec["velocity"][t].astype(np.float32)            # (N,2)
    rho = rec["density"][t, :, 0:1].astype(np.float32)     # (N,1)
    vel1 = rec["velocity"][t + 1].astype(np.float32)
    rho1 = rec["density"][t + 1, :, 0:1].astype(np.float32)
    feat = np.concatenate([vel, rho, one_hot(nt)], axis=1)          # (N,6)
    tgt = np.concatenate([vel1 - vel, rho1 - rho], axis=1)          # (N,3) next-step deltas
    edge_index = cell_to_edges(cells)                              # (2,E)
    rel = pos[edge_index[0]] - pos[edge_index[1]]
    norm = np.linalg.norm(rel, axis=1, keepdims=True)
    edge_attr = np.concatenate([rel, norm], axis=1).astype(np.float32)  # (E,3)
    return pos, cells, nt, feat, tgt, edge_index, edge_attr, vel, rho


def build_model(hidden: int, processor_size: int):
    from physicsnemo.models.meshgraphnet import MeshGraphNet
    return MeshGraphNet(
        input_dim_nodes=6, input_dim_edges=3, output_dim=3,
        processor_size=processor_size,
        hidden_dim_processor=hidden, hidden_dim_node_encoder=hidden,
        hidden_dim_edge_encoder=hidden, hidden_dim_node_decoder=hidden,
        num_layers_node_processor=2, num_layers_edge_processor=2,
        num_layers_node_encoder=2, num_layers_edge_encoder=2,
        num_layers_node_decoder=2, aggregation="sum")


def to_data(feat, edge_index, edge_attr, tgt=None):
    d = Data(x=torch.as_tensor(feat), edge_index=torch.as_tensor(edge_index, dtype=torch.long),
             edge_attr=torch.as_tensor(edge_attr))
    if tgt is not None:
        d.y = torch.as_tensor(tgt)
    return d


def predict(model, feat, edge_index, edge_attr):
    model.eval()
    with torch.no_grad():
        g = to_data(feat, edge_index, edge_attr)
        return model(g.x.float(), g.edge_attr.float(), g).cpu().numpy()


def relative_l2(a, b):
    return float(np.linalg.norm((a - b).reshape(-1)) / max(np.linalg.norm(b.reshape(-1)), 1e-12))


def div_rms_masked(pos, cells, field, mask_cells=None):
    div, area = cell_divergence(pos, cells, field)
    if mask_cells is not None:
        div, area = div[mask_cells], area[mask_cells]
    tot = float(area.sum())
    return float(np.sqrt(np.sum(area * div ** 2) / tot)) if tot > 0 else float("nan")


def run(args):
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    torch.set_num_threads(args.threads)
    OUT_DIR.mkdir(parents=True, exist_ok=True); RAW_DIR.mkdir(parents=True, exist_ok=True)
    data_record = stage_data(args.n_train, args.n_test)
    meta = json.loads((STAGE_DIR / "meta.json").read_text())

    # --- accumulate normalization stats over a subset of train snapshots ---
    stats = AirfoilStats()
    train_cache = []
    for rec in iter_trajectories("train", meta, args.n_train):
        steps = np.linspace(0, args.traj_len - 2, args.snaps_per_traj_train, dtype=int)
        for t in steps:
            _, _, _, feat, tgt, ei, ea, _, _ = build_graph(rec, int(t))
            stats.update(feat, tgt)
            train_cache.append((feat, tgt, ei, ea))
    fm, fs, tm, ts = stats.finalize()

    def nf(feat):  # normalize node features
        return (feat - fm) / fs

    def nt_(tgt):  # normalize targets
        return (tgt - tm) / ts

    model = build_model(args.hidden, args.processor_size)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    losses = []
    start_epoch = 0
    if RESUME.exists():
        st = torch.load(RESUME, map_location="cpu", weights_only=True)
        if st.get("completed_epochs", 0) > 0:
            model.load_state_dict(st["model_state_dict"]); start_epoch = st["completed_epochs"]; losses = st["losses"]
            print(f"resuming from epoch {start_epoch}", flush=True)

    order = np.arange(len(train_cache))
    for epoch in range(start_epoch, args.epochs):
        rng = np.random.default_rng(args.seed + epoch); rng.shuffle(order)
        model.train(); eloss = 0.0
        for step, idx in enumerate(order):
            feat, tgt, ei, ea = train_cache[int(idx)]
            g = to_data(nf(feat), ei, ea, nt_(tgt))
            opt.zero_grad(set_to_none=True)
            pred = model(g.x.float(), g.edge_attr.float(), g)
            loss = torch.mean((pred - g.y.float()) ** 2)
            loss.backward(); opt.step(); eloss += float(loss.detach())
            if (step + 1) % 100 == 0:
                print(f"epoch {epoch} step {step+1}/{len(order)} loss {eloss/(step+1):.4f}", flush=True)
        losses.append(eloss / max(len(order), 1))
        torch.save({"model_state_dict": model.state_dict(), "completed_epochs": epoch + 1, "losses": losses}, RESUME)
        print(f"epoch {epoch} done: {losses[-1]:.4f}", flush=True)

    # --- evaluation: MR battery per test trajectory ---
    perm_rows, cons_rows, incompr_rows, rollout_rows = [], [], [], []
    density_var = []
    raw_saved = 0
    dt = float(meta["dt"])
    for ti, rec in enumerate(iter_trajectories("test", meta, args.n_test)):
        mid = args.traj_len // 2
        pos, cells, nt, feat, tgt, ei, ea, vel, rho = build_graph(rec, mid)
        interior = np.isin(nt[cells], [0]).all(axis=1)  # NORMAL-only interior cells

        src = predict(model, nf(feat), ei, ea)  # normalized-delta prediction
        # de-normalize predicted delta and form next-state velocity for diagnostics
        src_delta = src * ts + tm
        pred_vel = vel + src_delta[:, :2]
        pred_rho = rho[:, 0] + src_delta[:, 2]
        rollout_rows.append({"trajectory": ti, "snapshot": mid,
                             "relative_l2": relative_l2(src, nt_(tgt))})

        # node-permutation equivariance (ADMITTED)
        rng = np.random.default_rng(args.seed + 1000 + ti)
        p = rng.permutation(feat.shape[0]); inv = np.empty_like(p); inv[p] = np.arange(len(p))
        ei_p = inv[ei]
        out_p = predict(model, nf(feat)[p], ei_p, ea)
        unperm = np.empty_like(out_p); unperm[p] = out_p
        perm_rel = relative_l2(unperm, src)
        perm_rows.append({"trajectory": ti, "relative_l2": perm_rel,
                          "passes": int(perm_rel <= NODE_PERM_THRESHOLD)})

        # incompressible divergence-free (REJECTED at physical-basis gate): measure ref div(u) and density variation
        rho_var = float(rho.max() / max(rho.min(), 1e-12))
        density_var.append(rho_var)
        ref_div_u = div_rms_masked(pos, cells, vel, interior)
        incompr_rows.append({"trajectory": ti, "density_max_over_min": rho_var,
                             "ref_incompressible_div_u_rms": ref_div_u})

        # compressible mass conservation (DEFERRED absolute; reference-relative diagnostic)
        rho_next = rec["density"][mid + 1, :, 0]
        drho_dt = ((rho_next - rho[:, 0])[cells].mean(axis=1)) / dt
        div_rhou_ref, area = cell_divergence(pos, cells, vel * rho)
        resid_ref = drho_dt + div_rhou_ref
        # surrogate predicted next-state compressible residual
        drho_dt_pred = ((pred_rho - rho[:, 0])[cells].mean(axis=1)) / dt
        div_rhou_pred, _ = cell_divergence(pos, cells, pred_vel * pred_rho[:, None])
        resid_pred = drho_dt_pred + div_rhou_pred
        def rms(x, m=interior):
            xx, aa = x[m], area[m]; tot = float(aa.sum())
            return float(np.sqrt(np.sum(aa * xx ** 2) / tot)) if tot > 0 else float("nan")
        ref_rms = rms(resid_ref); pred_rms = rms(resid_pred)
        cons_rows.append({"trajectory": ti, "ref_residual_rms": ref_rms,
                          "pred_residual_rms": pred_rms,
                          "ratio": pred_rms / max(ref_rms, 1e-12)})

        if raw_saved < args.raw_trajectories:
            np.savez_compressed(RAW_DIR / f"airfoil_test_{ti:03d}.npz",
                                source_prediction=src, target=nt_(tgt),
                                permutation_unpermuted_prediction=unperm,
                                permutation=p, ref_div_u=ref_div_u,
                                density_max_over_min=rho_var)
            raw_saved += 1
        print(f"test traj {ti}: perm={perm_rel:.2e} rho_var={rho_var:.2f}x div_u={ref_div_u:.2e} cons_ratio={cons_rows[-1]['ratio']:.3f}", flush=True)

    torch.save({"model_state_dict": model.state_dict(),
                "constructor": {"input_dim_nodes": 6, "input_dim_edges": 3, "output_dim": 3,
                                "hidden": args.hidden, "processor_size": args.processor_size},
                "normalization": {"feat_mean": fm.tolist(), "feat_std": fs.tolist(),
                                  "tgt_mean": tm.tolist(), "tgt_std": ts.tolist()},
                "training": {"epochs": args.epochs, "losses": losses, "seed": args.seed},
                "data": data_record}, CHECKPOINT)

    write_outputs(args, data_record, losses, perm_rows, incompr_rows, cons_rows,
                  rollout_rows, density_var, model)
    return REPORT


def write_outputs(args, data_record, losses, perm_rows, incompr_rows, cons_rows,
                  rollout_rows, density_var, model):
    perm_pass = sum(r["passes"] for r in perm_rows)
    n = len(perm_rows)
    med_density_var = float(np.median(density_var))
    med_div_u = float(np.median([r["ref_incompressible_div_u_rms"] for r in incompr_rows]))
    med_cons_ratio = float(np.median([r["ratio"] for r in cons_rows]))
    med_rollout = float(np.median([r["relative_l2"] for r in rollout_rows]))

    ledgers = {
        "node_permutation_metric_ledger.json": {
            "relation": "node_permutation_equivariance", "rubric_decision": "admitted",
            "metric": "relative_l2(unpermuted_followup, source)", "denominator": n,
            "passes": perm_pass, "max_relative_l2": float(max(r["relative_l2"] for r in perm_rows)),
            "threshold": NODE_PERM_THRESHOLD, "rows": perm_rows,
            "verdict": "pass" if perm_pass == n else "fail"},
        "incompressible_continuity_rejection_ledger.json": {
            "relation": "incompressible_divergence_free_continuity",
            "rubric_decision": "rejected-domain-invalid-physical-basis",
            "rejection_basis": (
                "Condition (i) physical-basis gate fails: the SU2 airfoil flow is "
                "compressible (median density max/min = "
                f"{med_density_var:.2f}x across the field, n={n} trajectories), so the "
                "incompressible continuity assumption div(u)=0 is physically false for "
                "this SUT. On cylinder flow the same relation passes condition (i) and is "
                "only deferred at condition (iv); here it is rejected on physical grounds."),
            "denominator": n, "median_density_max_over_min": med_density_var,
            "median_reference_incompressible_div_u_rms": med_div_u, "rows": incompr_rows,
            "verdict": "rejected-domain-invalid"},
        "compressible_conservation_metric_ledger.json": {
            "relation": "compressible_unsteady_mass_conservation",
            "rubric_decision": "deferred-uncalibratable-absolute-then-reference-relative-diagnostic",
            "metric": "rms(drho/dt + div(rho u)) surrogate vs reference, interior cells",
            "denominator": n, "median_pred_over_ref_residual_ratio": med_cons_ratio,
            "rows": cons_rows, "verdict": "reference-relative-diagnostic-recorded",
            "honesty_boundary": (
                "The absolute compressible-continuity residual has a large discrete "
                "operator floor on this coarse transonic mesh (uncalibratable, as for "
                "cylinder incompressible continuity), so only a reference-relative "
                "diagnostic is reported; this asserts no absolute mass conservation.")},
        "mirror_y_symmetry_rejection_ledger.json": {
            "relation": "mirror_y_chord_symmetry",
            "rubric_decision": "rejected-domain-invalid-boundary-precondition",
            "rejection_basis": (
                "The SU2 airfoil trajectories carry a non-zero angle of attack, so "
                "reflection about the chord line is not a symmetry of the boundary-value "
                "problem; condition (iii) boundary-compatibility fails. Recorded as a "
                "rubric rejection rather than executed."),
            "verdict": "rejected-domain-invalid"},
        "rollout_accuracy_metric_ledger.json": {
            "relation": "one_step_rollout_accuracy", "denominator": n,
            "median_relative_l2": med_rollout, "rows": rollout_rows,
            "verdict": "diagnostic-recorded"},
    }
    for name, payload in ledgers.items():
        (OUT_DIR / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rubric = {
        "object_id": "physicsnemo-mgn-airfoil-second-task",
        "task": "DeepMind airfoil / SU2 compressible transonic flow",
        "admitted_relations": ["node_permutation_equivariance"],
        "rejected_relations": [
            "incompressible_divergence_free_continuity (physical-basis gate, condition i)",
            "mirror_y_chord_symmetry (boundary-precondition gate, condition iii)"],
        "deferred_then_diagnostic_relations": ["compressible_unsteady_mass_conservation (numerical-decidability gate, condition iv)"],
        "cross_task_contrast": (
            "Same four-condition admissibility predicate as the cylinder-flow case study; "
            "the typed inadmissibility structure differs because the physics differs. "
            "Incompressible continuity is DEFERRED on cylinder (valid physics, uncalibratable "
            "floor) but REJECTED here (invalid physics, compressible flow) --- a different "
            "verdict TYPE produced by the same gate on a second task."),
    }
    RUBRIC.write_text(json.dumps(rubric, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    n_params = sum(p.numel() for p in model.parameters())
    report = {
        "record_type": "physicsnemo-mgn-airfoil-second-task-workflow",
        "schema_version": "0.1.0", "generated_at": utc_now(),
        "object_id": "physicsnemo-mgn-airfoil-second-task",
        "sut_name": "NVIDIA PhysicsNeMo MeshGraphNet (official architecture)",
        "task": "DeepMind airfoil / SU2 compressible transonic flow over an aerofoil",
        "second_task_contrast_to_cylinder": "compressible vs incompressible; second official dataset",
        "production_framework": "nvidia-physicsnemo",
        "workflow_status": "completed-second-task-cpu-subset",
        "architecture": {"processor_size": args.processor_size, "hidden_dim": args.hidden,
                         "n_parameters": int(n_params)},
        "data": data_record,
        "training": {"n_train_trajectories": args.n_train,
                     "snaps_per_traj_train": args.snaps_per_traj_train,
                     "epochs": args.epochs, "lr": args.lr, "seed": args.seed,
                     "losses": losses, "final_loss": losses[-1] if losses else None},
        "evaluation": {"n_test_trajectories": args.n_test},
        "headline_typed_verdict_structure": {
            "node_permutation_equivariance": "admitted (exact-by-construction)",
            "incompressible_continuity": "rejected-domain-invalid (physical-basis, condition i)",
            "compressible_mass_conservation": "deferred-absolute / reference-relative-diagnostic",
            "mirror_y_symmetry": "rejected-domain-invalid (boundary-precondition, condition iii)"},
        "metrics": {
            "node_permutation_passes": f"{perm_pass}/{n}",
            "node_permutation_max_relative_l2": float(max(r["relative_l2"] for r in perm_rows)),
            "median_density_max_over_min": med_density_var,
            "median_reference_incompressible_div_u_rms": med_div_u,
            "median_compressible_residual_ratio": med_cons_ratio,
            "median_one_step_rollout_relative_l2": med_rollout},
        "artifacts": {
            "checkpoint": str(CHECKPOINT.relative_to(ROOT)),
            "rubric_decisions": str(RUBRIC.relative_to(ROOT)),
            "raw_outputs_dir": str(RAW_DIR.relative_to(ROOT)),
            "metric_ledgers": {k.removesuffix(".json"): str((OUT_DIR / k).relative_to(ROOT)) for k in ledgers}},
        "honesty_boundary": (
            "A bounded CPU-scale second-task evaluation of the official PhysicsNeMo "
            "MeshGraphNet architecture on official DeepMind airfoil (SU2 compressible) "
            "trajectories. The contribution is the cross-task demonstration that the same "
            "admissibility predicate yields a different typed inadmissibility structure, "
            "NOT a production-scale airfoil benchmark, NOT an official NVIDIA checkpoint, "
            "and NOT a cross-dataset reliability rate. One-step rollout only."),
        "forbidden_claims": [
            "production-scale airfoil pass/fail rate", "official NVIDIA checkpoint behaviour",
            "closed-loop rollout accuracy", "cross-dataset reliability",
            "absolute compressible mass conservation"],
    }
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"  node_perm={perm_pass}/{n}  density_var={med_density_var:.2f}x  div_u={med_div_u:.2e}  cons_ratio={med_cons_ratio:.3f}  rollout={med_rollout:.3f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-train", type=int, default=6)
    ap.add_argument("--n-test", type=int, default=10)
    ap.add_argument("--traj-len", type=int, default=600)
    ap.add_argument("--snaps-per-traj-train", type=int, default=20)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--processor-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=20260613)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--raw-trajectories", type=int, default=3)
    args = ap.parse_args()
    run(args)


if __name__ == "__main__":
    main()
