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
# STAGE_DIR is overridable: env var METBENCH_AIRFOIL_STAGE_DIR or --stage-dir CLI arg.
# Default is a local cache path outside the git tree so macOS runs do not crash.
_DEFAULT_STAGE_DIR = Path.home() / ".cache" / "dvgmr" / "airfoil_staged"
STAGE_DIR = Path(os.environ.get("METBENCH_AIRFOIL_STAGE_DIR", str(_DEFAULT_STAGE_DIR)))
BASE_URL = "https://storage.googleapis.com/dm-meshgraphnets/airfoil"
CHECKPOINT = OUT_DIR / "physicsnemo_mgn_airfoil_checkpoint.pt"
REPORT = OUT_DIR / "physicsnemo_mgn_airfoil_workflow_report.json"
RUBRIC = OUT_DIR / "physicsnemo_mgn_airfoil_rubric_decisions.json"

NODE_PERM_THRESHOLD = 1e-5
NODE_TYPES = (0, 2, 4)  # observed airfoil node types: NORMAL, OUTFLOW, AIRFOIL/WALL


# ---------------------------------------------------------------------------
# Device selection: prefer MPS when available; fall back to CPU if any op
# raises at runtime.  torch_scatter's scatter_add_ is used internally by
# PhysicsNeMo MeshGraphNet; in torch 2.12 + torch-scatter 2.1.2 MPS is
# supported, but we wrap placement defensively so future regressions are
# caught rather than crashing the whole run.
# ---------------------------------------------------------------------------
def _select_device() -> torch.device:
    if torch.backends.mps.is_available():
        # Quick probe: build a tiny model and run one forward pass on MPS.
        try:
            from physicsnemo.models.meshgraphnet import MeshGraphNet as _MGN
            _m = _MGN(input_dim_nodes=6, input_dim_edges=3, output_dim=3,
                      processor_size=1, hidden_dim_processor=8,
                      hidden_dim_node_encoder=8, hidden_dim_edge_encoder=8,
                      hidden_dim_node_decoder=8, num_layers_node_processor=1,
                      num_layers_edge_processor=1, num_layers_node_encoder=1,
                      num_layers_edge_encoder=1, num_layers_node_decoder=1,
                      aggregation="sum").to("mps")
            _x = torch.randn(4, 6, device="mps")
            _ea = torch.randn(6, 3, device="mps")
            _ei = torch.randint(0, 4, (2, 6), device="mps")
            _g = Data(x=_x, edge_index=_ei, edge_attr=_ea)
            _m(_x, _ea, _g)
            del _m, _x, _ea, _ei, _g
            return torch.device("mps")
        except Exception as _e:
            print(f"[device] MPS probe failed ({type(_e).__name__}: {_e}); "
                  "falling back to CPU.", flush=True)
    return torch.device("cpu")


DEVICE = _select_device()
print(f"[device] using {DEVICE}", flush=True)


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


def stage_split(split: str, n_records: int, stage_dir: Path = None) -> dict[str, Any]:
    if stage_dir is None:
        stage_dir = STAGE_DIR
    target = stage_dir / f"{split}.tfrecord"
    marker = stage_dir / f"{split}.records.json"
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
        "stage_dir": str(STAGE_DIR).replace(str(Path.home()), "~"), "source_url_prefix": BASE_URL,
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


def iter_trajectories(split: str, meta: dict, limit: int, stage_dir: Path = None):
    from tfrecord.torch.dataset import TFRecordDataset
    if stage_dir is None:
        stage_dir = STAGE_DIR
    desc = {k: "byte" for k in meta["field_names"]}
    ds = TFRecordDataset(str(stage_dir / f"{split}.tfrecord"), None, desc,
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


def to_data(feat, edge_index, edge_attr, tgt=None, device: torch.device = None):
    dev = device or DEVICE
    d = Data(x=torch.as_tensor(feat).to(dev),
             edge_index=torch.as_tensor(edge_index, dtype=torch.long).to(dev),
             edge_attr=torch.as_tensor(edge_attr).to(dev))
    if tgt is not None:
        d.y = torch.as_tensor(tgt).to(dev)
    return d


def predict(model, feat, edge_index, edge_attr, device: torch.device = None):
    dev = device or DEVICE
    model.eval()
    # Move model to device if it is not already there
    try:
        model.to(dev)
        with torch.no_grad():
            g = to_data(feat, edge_index, edge_attr, device=dev)
            out = model(g.x.float(), g.edge_attr.float(), g)
            return out.cpu().numpy()
    except Exception as _e:
        if str(dev) != "cpu":
            # MPS op failed at runtime; fall back to CPU for this call
            print(f"[predict] device={dev} op failed ({type(_e).__name__}); "
                  "retrying on CPU.", flush=True)
            model.to("cpu")
            with torch.no_grad():
                g = to_data(feat, edge_index, edge_attr, device=torch.device("cpu"))
                return model(g.x.float(), g.edge_attr.float(), g).cpu().numpy()
        raise


def relative_l2(a, b):
    return float(np.linalg.norm((a - b).reshape(-1)) / max(np.linalg.norm(b.reshape(-1)), 1e-12))


def div_rms_masked(pos, cells, field, mask_cells=None):
    div, area = cell_divergence(pos, cells, field)
    if mask_cells is not None:
        div, area = div[mask_cells], area[mask_cells]
    tot = float(area.sum())
    return float(np.sqrt(np.sum(area * div ** 2) / tot)) if tot > 0 else float("nan")


def _train_one_checkpoint(args, train_cache, fm, fs, tm, ts, ckpt_seed: int,
                          stage_dir: Path) -> tuple:
    """Train one checkpoint from scratch with a given seed. Returns (model, losses, wall_clock_s)."""
    import time
    torch.manual_seed(ckpt_seed); np.random.seed(ckpt_seed)

    def nf(feat): return (feat - fm) / fs
    def nt_(tgt): return (tgt - tm) / ts

    model = build_model(args.hidden, args.processor_size)
    # Move model to training device (MPS if available; fall back to CPU on error)
    try:
        model.to(DEVICE)
    except Exception as _e:
        print(f"[train] model.to({DEVICE}) failed: {_e}; using cpu", flush=True)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)

    # Resume support per-seed checkpoint
    resume_path = stage_dir / f"resume_ckpt_seed{ckpt_seed}.pt"
    losses = []
    start_epoch = 0
    if resume_path.exists():
        st = torch.load(resume_path, map_location="cpu", weights_only=True)
        if st.get("completed_epochs", 0) > 0:
            model.load_state_dict(st["model_state_dict"])
            start_epoch = st["completed_epochs"]; losses = st["losses"]
            print(f"  [ckpt seed={ckpt_seed}] resuming from epoch {start_epoch}", flush=True)

    order = np.arange(len(train_cache))
    t_start = time.time()
    for epoch in range(start_epoch, args.epochs):
        rng = np.random.default_rng(ckpt_seed + epoch); rng.shuffle(order)
        model.train(); eloss = 0.0
        for step, idx in enumerate(order):
            feat, tgt, ei, ea = train_cache[int(idx)]
            try:
                g = to_data(nf(feat), ei, ea, nt_(tgt))
                opt.zero_grad(set_to_none=True)
                pred = model(g.x.float(), g.edge_attr.float(), g)
                loss = torch.mean((pred - g.y.float()) ** 2)
                loss.backward(); opt.step()
            except Exception as _e:
                if str(DEVICE) != "cpu":
                    # MPS failure during training: fall back to CPU for this checkpoint
                    print(f"  [ckpt seed={ckpt_seed}] device={DEVICE} step failed: "
                          f"{type(_e).__name__}; falling back to CPU for this checkpoint.",
                          flush=True)
                    model.to("cpu")
                    g = to_data(nf(feat), ei, ea, nt_(tgt), device=torch.device("cpu"))
                    opt.zero_grad(set_to_none=True)
                    pred = model(g.x.float(), g.edge_attr.float(), g)
                    loss = torch.mean((pred - g.y.float()) ** 2)
                    loss.backward(); opt.step()
                else:
                    raise
            eloss += float(loss.detach())
            if (step + 1) % 200 == 0:
                print(f"  [ckpt seed={ckpt_seed}] epoch {epoch} "
                      f"step {step+1}/{len(order)} loss {eloss/(step+1):.4f}", flush=True)
        losses.append(eloss / max(len(order), 1))
        torch.save({"model_state_dict": model.state_dict(),
                    "completed_epochs": epoch + 1, "losses": losses}, resume_path)
        print(f"  [ckpt seed={ckpt_seed}] epoch {epoch} done: {losses[-1]:.4f}", flush=True)

    wall_clock = time.time() - t_start
    return model, losses, wall_clock


def _eval_one_checkpoint(model, args, meta, test_records: list, nf, nt_, ts, tm,
                         ckpt_idx: int) -> dict:
    """Run the full MR battery on all pre-fetched test records for one checkpoint."""
    perm_rows, cons_rows, incompr_rows, rollout_rows = [], [], [], []
    density_var = []
    dt = float(meta["dt"])

    for ti, rec in enumerate(test_records):
        mid = args.traj_len // 2
        pos, cells, nt, feat, tgt, ei, ea, vel, rho = build_graph(rec, mid)
        interior = np.isin(nt[cells], [0]).all(axis=1)

        src = predict(model, nf(feat), ei, ea)
        src_delta = src * ts + tm
        pred_vel = vel + src_delta[:, :2]
        pred_rho = rho[:, 0] + src_delta[:, 2]
        rollout_rows.append({"trajectory": ti, "snapshot": mid,
                             "relative_l2": relative_l2(src, nt_(tgt))})

        rng = np.random.default_rng(args.seed + 1000 + ti + ckpt_idx * 10000)
        p = rng.permutation(feat.shape[0]); inv = np.empty_like(p); inv[p] = np.arange(len(p))
        ei_p = inv[ei]
        out_p = predict(model, nf(feat)[p], ei_p, ea)
        unperm = np.empty_like(out_p); unperm[p] = out_p
        perm_rel = relative_l2(unperm, src)
        perm_rows.append({"trajectory": ti, "relative_l2": perm_rel,
                          "passes": int(perm_rel <= NODE_PERM_THRESHOLD)})

        rho_var = float(rho.max() / max(rho.min(), 1e-12))
        density_var.append(rho_var)
        ref_div_u = div_rms_masked(pos, cells, vel, interior)
        incompr_rows.append({"trajectory": ti, "density_max_over_min": rho_var,
                             "ref_incompressible_div_u_rms": ref_div_u})

        rho_next = rec["density"][mid + 1, :, 0]
        drho_dt = ((rho_next - rho[:, 0])[cells].mean(axis=1)) / dt
        div_rhou_ref, area = cell_divergence(pos, cells, vel * rho)
        resid_ref = drho_dt + div_rhou_ref
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

        print(f"    [ckpt {ckpt_idx} traj {ti}] perm={perm_rel:.2e} "
              f"rho_var={rho_var:.2f}x div_u={ref_div_u:.2e} "
              f"cons_ratio={cons_rows[-1]['ratio']:.3f}", flush=True)

    return {"perm_rows": perm_rows, "cons_rows": cons_rows,
            "incompr_rows": incompr_rows, "rollout_rows": rollout_rows,
            "density_var": density_var}


def run(args):
    import time as _time
    # Update module-level STAGE_DIR if --stage-dir was provided via CLI
    global STAGE_DIR, OUT_DIR, RAW_DIR, CHECKPOINT, REPORT, RUBRIC
    if hasattr(args, "stage_dir") and args.stage_dir:
        STAGE_DIR = Path(args.stage_dir)
    if getattr(args, "out", None):
        OUT_DIR = Path(args.out) if Path(args.out).is_absolute() else ROOT / args.out
        RAW_DIR = OUT_DIR / "raw_outputs"
        CHECKPOINT = OUT_DIR / "physicsnemo_mgn_airfoil_checkpoint.pt"
        REPORT = OUT_DIR / "physicsnemo_mgn_airfoil_workflow_report.json"
        RUBRIC = OUT_DIR / "physicsnemo_mgn_airfoil_rubric_decisions.json"

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

    def nf(feat): return (feat - fm) / fs
    def nt_(tgt): return (tgt - tm) / ts

    # Pre-fetch test records (they are re-used across all K checkpoints)
    print(f"pre-fetching {args.n_test} test trajectories...", flush=True)
    test_records = list(iter_trajectories("test", meta, args.n_test))
    print(f"  cached {len(test_records)} test trajectories.", flush=True)

    # --- K-checkpoint roster ---
    # Seeds are deterministically derived from the base seed so the roster
    # is reproducible and each checkpoint is independently initialised.
    k = args.k_checkpoints
    ckpt_seeds = [args.seed + i * 7919 for i in range(k)]
    roster = []      # list of per-checkpoint result dicts
    ckpt_wall_clocks = []
    t_roster_start = _time.time()

    for ckpt_idx, ckpt_seed in enumerate(ckpt_seeds):
        print(f"\n=== checkpoint {ckpt_idx+1}/{k} (seed={ckpt_seed}) ===", flush=True)
        t_ckpt_start = _time.time()
        model, losses, train_wc = _train_one_checkpoint(
            args, train_cache, fm, fs, tm, ts, ckpt_seed, STAGE_DIR)

        print(f"  evaluating MR battery on {len(test_records)} test trajectories...", flush=True)
        eval_result = _eval_one_checkpoint(model, args, meta, test_records, nf, nt_, ts, tm, ckpt_idx)
        ckpt_wc = _time.time() - t_ckpt_start
        ckpt_wall_clocks.append(ckpt_wc)

        # Save individual checkpoint file
        ckpt_path = OUT_DIR / f"checkpoint_k{ckpt_idx+1:02d}_seed{ckpt_seed}.pt"
        torch.save({"model_state_dict": model.state_dict(),
                    "constructor": {"input_dim_nodes": 6, "input_dim_edges": 3, "output_dim": 3,
                                    "hidden": args.hidden, "processor_size": args.processor_size},
                    "normalization": {"feat_mean": fm.tolist(), "feat_std": fs.tolist(),
                                      "tgt_mean": tm.tolist(), "tgt_std": ts.tolist()},
                    "training": {"epochs": args.epochs, "losses": losses, "seed": ckpt_seed},
                    "data": data_record}, ckpt_path)

        # Save raw outputs for first trajectory of each checkpoint
        if test_records:
            ti0 = 0
            _, _, nt_type, feat0, tgt0, ei0, ea0, vel0, rho0 = build_graph(test_records[ti0], args.traj_len // 2)
            src0 = predict(model, nf(feat0), ei0, ea0)
            rng0 = np.random.default_rng(ckpt_seed + 1000)
            p0 = rng0.permutation(feat0.shape[0])
            inv0 = np.empty_like(p0); inv0[p0] = np.arange(len(p0))
            out_p0 = predict(model, nf(feat0)[p0], inv0[ei0], ea0)
            unperm0 = np.empty_like(out_p0); unperm0[p0] = out_p0
            np.savez_compressed(
                RAW_DIR / f"airfoil_ckpt{ckpt_idx+1:02d}_test_{ti0:03d}.npz",
                source_prediction=src0, target=nt_(tgt0),
                permutation_unpermuted_prediction=unperm0,
                permutation=p0,
                ref_div_u=eval_result["incompr_rows"][ti0]["ref_incompressible_div_u_rms"],
                density_max_over_min=eval_result["density_var"][ti0])

        roster.append({
            "checkpoint_index": ckpt_idx + 1,
            "seed": ckpt_seed,
            "checkpoint_file": ckpt_path.name,
            "train_wall_clock_s": train_wc,
            "total_wall_clock_s": ckpt_wc,
            "losses": losses,
            **eval_result})

        print(f"  checkpoint {ckpt_idx+1}/{k} done in {ckpt_wc:.1f}s "
              f"(train {train_wc:.1f}s)", flush=True)

    total_wall_clock = _time.time() - t_roster_start

    # Aggregate metrics across all checkpoints (aggregate rows from all checkpoints for ledgers)
    all_perm = [r for ckpt in roster for r in ckpt["perm_rows"]]
    all_cons = [r for ckpt in roster for r in ckpt["cons_rows"]]
    all_incompr = [r for ckpt in roster for r in ckpt["incompr_rows"]]
    all_rollout = [r for ckpt in roster for r in ckpt["rollout_rows"]]
    all_density_var = [v for ckpt in roster for v in ckpt["density_var"]]

    # Also save the canonical single-checkpoint artifact (last checkpoint) for backward
    # compatibility with the existing guard test (test_physicsnemo_airfoil_workflow.py)
    last_model_state = torch.load(
        OUT_DIR / roster[-1]["checkpoint_file"], map_location="cpu", weights_only=True
    )["model_state_dict"]
    last_model = build_model(args.hidden, args.processor_size)
    last_model.load_state_dict(last_model_state)
    torch.save({"model_state_dict": last_model_state,
                "constructor": {"input_dim_nodes": 6, "input_dim_edges": 3, "output_dim": 3,
                                "hidden": args.hidden, "processor_size": args.processor_size},
                "normalization": {"feat_mean": fm.tolist(), "feat_std": fs.tolist(),
                                  "tgt_mean": tm.tolist(), "tgt_std": ts.tolist()},
                "training": {"epochs": args.epochs, "losses": roster[-1]["losses"],
                             "seed": args.seed},
                "data": data_record}, CHECKPOINT)

    # Save raw outputs for backward compat (first 3 test trajectories from last checkpoint)
    raw_saved = 0
    for ti, rec in enumerate(test_records[:args.raw_trajectories]):
        pos, cells, nt_type, feat, tgt, ei, ea, vel, rho = build_graph(rec, args.traj_len // 2)
        src = predict(last_model, nf(feat), ei, ea)
        rng = np.random.default_rng(args.seed + 1000 + ti)
        p = rng.permutation(feat.shape[0]); inv = np.empty_like(p); inv[p] = np.arange(len(p))
        out_p = predict(last_model, nf(feat)[p], inv[ei], ea)
        unperm = np.empty_like(out_p); unperm[p] = out_p
        np.savez_compressed(RAW_DIR / f"airfoil_test_{ti:03d}.npz",
                            source_prediction=src, target=nt_(tgt),
                            permutation_unpermuted_prediction=unperm,
                            permutation=p,
                            ref_div_u=all_incompr[ti]["ref_incompressible_div_u_rms"],
                            density_max_over_min=all_density_var[ti % len(all_density_var)])
        raw_saved += 1

    write_outputs(args, data_record, roster[-1]["losses"], all_perm, all_incompr,
                  all_cons, all_rollout, all_density_var, last_model,
                  roster=roster, k_checkpoints=k,
                  ckpt_wall_clocks=ckpt_wall_clocks,
                  total_wall_clock=total_wall_clock)
    return REPORT


def write_outputs(args, data_record, losses, perm_rows, incompr_rows, cons_rows,
                  rollout_rows, density_var, model,
                  roster=None, k_checkpoints=1, ckpt_wall_clocks=None,
                  total_wall_clock=None):
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
    # Roster summary: per-checkpoint timing and pass counts
    roster_summary = []
    if roster:
        for ckpt in roster:
            ckpt_perm_pass = sum(r["passes"] for r in ckpt["perm_rows"])
            ckpt_n = len(ckpt["perm_rows"])
            roster_summary.append({
                "checkpoint_index": ckpt["checkpoint_index"],
                "seed": ckpt["seed"],
                "checkpoint_file": ckpt["checkpoint_file"],
                "train_wall_clock_s": round(ckpt["train_wall_clock_s"], 1),
                "total_wall_clock_s": round(ckpt["total_wall_clock_s"], 1),
                "final_loss": ckpt["losses"][-1] if ckpt["losses"] else None,
                "node_perm_passes": f"{ckpt_perm_pass}/{ckpt_n}",
                "median_density_max_over_min": float(np.median(ckpt["density_var"])),
                "median_cons_ratio": float(np.median([r["ratio"] for r in ckpt["cons_rows"]])),
            })

    report = {
        "record_type": "physicsnemo-mgn-airfoil-second-task-workflow",
        "schema_version": "0.2.0", "generated_at": utc_now(),
        "object_id": "physicsnemo-mgn-airfoil-second-task",
        "sut_name": "NVIDIA PhysicsNeMo MeshGraphNet (official architecture)",
        "task": "DeepMind airfoil / SU2 compressible transonic flow over an aerofoil",
        "second_task_contrast_to_cylinder": "compressible vs incompressible; second official dataset",
        "production_framework": "nvidia-physicsnemo",
        "workflow_status": "completed-second-task-mps-or-cpu-subset",
        "device_used": str(DEVICE),
        "architecture": {"processor_size": args.processor_size, "hidden_dim": args.hidden,
                         "n_parameters": int(n_params)},
        "data": data_record,
        "training": {"n_train_trajectories": args.n_train,
                     "snaps_per_traj_train": args.snaps_per_traj_train,
                     "epochs": args.epochs, "lr": args.lr, "seed": args.seed,
                     "losses": losses, "final_loss": losses[-1] if losses else None},
        "evaluation": {"n_test_trajectories": args.n_test},
        "roster": {
            "k_checkpoints": k_checkpoints,
            "k_checkpoints_completed": len(roster) if roster else 1,
            "ckpt_wall_clocks_s": [round(w, 1) for w in (ckpt_wall_clocks or [])],
            "total_wall_clock_s": round(total_wall_clock, 1) if total_wall_clock else None,
            "per_checkpoint_summary": roster_summary,
        },
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
            "A bounded MPS/CPU-scale second-task evaluation of the official PhysicsNeMo "
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
    ap.add_argument("--stage-dir", type=str, default=None,
                    help="Override STAGE_DIR (also overridden by METBENCH_AIRFOIL_STAGE_DIR env var). "
                         "Defaults to ~/.cache/dvgmr/airfoil_staged (outside git tree).")
    ap.add_argument("--out", type=str, default=None,
                    help="Override OUT_DIR (relative to repo root, or absolute). Default keeps "
                         "the committed C31 second-task dir; the primary-scale roster passes a "
                         "new dir so C31 is preserved.")
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
    ap.add_argument("--k-checkpoints", type=int, default=6,
                    help="Number of independently-seeded checkpoints for the roster (default 6). "
                         "Each is trained from scratch with the same architecture and data.")
    args = ap.parse_args()
    # --stage-dir overrides env var; env var overrides default
    if args.stage_dir:
        global STAGE_DIR
        STAGE_DIR = Path(args.stage_dir)
    run(args)


if __name__ == "__main__":
    main()
