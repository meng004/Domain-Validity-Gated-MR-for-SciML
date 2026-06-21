"""EXT-1 airfoil convergence recipe sweep (single process, one cache build, batched GPU).

Builds train_cache / norm-stats / test_records ONCE (the expensive 5GB read), then trains
several recipes sequentially with graph mini-batching so each run saturates the RTX 3090.
Goal: find a recipe that escapes the loss==1.0 (normalized-mean) plateau caused by the
heavy-tailed airfoil deltas, and drives one-step rollout median rel-L2 down.

Fixed: n_train=100, n_test=40, hidden=128, processor_size=15 (C35 architecture), snaps=20.
Varies: loss {mse,huber,l1}, grad_clip, lr -- all with batch_size=32.
"""
from __future__ import annotations
import sys, json, time
from types import SimpleNamespace
import numpy as np
sys.path.insert(0, "tools")
import run_physicsnemo_mgn_airfoil_workflow as af

N_TRAIN, N_TEST, SNAPS, TRAJ_LEN = 100, 40, 20, 600
HIDDEN, PROC, BATCH, EPOCHS = 128, 15, 12, 10
EVAL_TRAJ = 6   # sweep eval on a subset for speed; full 40 only in the final convergence run

# Focused fast comparison: which LOSS gives the best rollout once grad-clip lets it escape
# the 1.0 plateau. (huber tames outliers but may under-fit shocks -> higher rollout; mse/l1
# may fit outliers better.) Fixed clip=1.0, lr=1e-3; rank by rollout_median_relL2.
CONFIGS = [
    dict(tag="huber_clip1_lr1e3", loss="huber", grad_clip=1.0, lr=1e-3, seed=5001),
    dict(tag="l1_clip1_lr1e3",    loss="l1",    grad_clip=1.0, lr=1e-3, seed=5003),
    dict(tag="mse_clip1_lr1e3",   loss="mse",   grad_clip=1.0, lr=1e-3, seed=5004),
]

def main():
    import torch, pickle, os
    from pathlib import Path
    # Ampere TF32 + cudnn autotune: faster matmuls, negligible accuracy impact.
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    print(f"[sweep] device={af.DEVICE} cuda={torch.cuda.is_available()} bs={BATCH} tf32=on", flush=True)
    af.stage_data(N_TRAIN, N_TEST)
    meta = json.loads((af.STAGE_DIR / "meta.json").read_text())

    # Disk-cache the expensive 5GB read (train_cache + stats + test_records) so repeated
    # sweep/convergence iterations skip it. Keyed by (n_train, snaps, traj_len, n_test).
    cache_dir = Path(os.path.expanduser("~/ext1_cache")); cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / f"airfoil_nt{N_TRAIN}_s{SNAPS}_tl{TRAJ_LEN}_te{N_TEST}.pkl"
    t0 = time.time()
    if cache_file.exists():
        with cache_file.open("rb") as fh:
            blob = pickle.load(fh)
        train_cache, fm, fs, tm, ts, test_records = (
            blob["train_cache"], blob["fm"], blob["fs"], blob["tm"], blob["ts"], blob["test_records"])
        print(f"[sweep] cache LOADED from disk: {len(train_cache)} train graphs, "
              f"{len(test_records)} test traj in {time.time()-t0:.0f}s", flush=True)
    else:
        stats = af.AirfoilStats(); train_cache = []
        for rec in af.iter_trajectories("train", meta, N_TRAIN):
            for t in np.linspace(0, TRAJ_LEN - 2, SNAPS, dtype=int):
                _, _, _, feat, tgt, ei, ea, _, _ = af.build_graph(rec, int(t))
                stats.update(feat, tgt); train_cache.append((feat, tgt, ei, ea))
        fm, fs, tm, ts = stats.finalize()
        test_records = list(af.iter_trajectories("test", meta, N_TEST))
        with cache_file.open("wb") as fh:
            pickle.dump(dict(train_cache=train_cache, fm=fm, fs=fs, tm=tm, ts=ts,
                             test_records=test_records), fh, protocol=4)
        print(f"[sweep] cache BUILT+saved: {len(train_cache)} train graphs, "
              f"{len(test_records)} test traj in {time.time()-t0:.0f}s", flush=True)
    def nf(feat): return (feat - fm) / fs
    def nt_(tgt): return (tgt - tm) / ts

    results = []
    for cfg in CONFIGS:
        args = SimpleNamespace(
            hidden=HIDDEN, processor_size=PROC, lr=cfg["lr"], epochs=EPOCHS,
            loss=cfg["loss"], grad_clip=cfg["grad_clip"], huber_delta=1.0,
            batch_size=BATCH, traj_len=TRAJ_LEN, seed=cfg["seed"], threads=8)
        # fresh resume file per seed (distinct), so each config trains from scratch
        rp = af.STAGE_DIR / f"resume_ckpt_seed{cfg['seed']}.pt"
        if rp.exists(): rp.unlink()
        tcfg = time.time()
        model, losses, wc = af._train_one_checkpoint(args, train_cache, fm, fs, tm, ts,
                                                     cfg["seed"], af.STAGE_DIR)
        ev = af._eval_one_checkpoint(model, args, meta, test_records[:EVAL_TRAJ], nf, nt_, ts, tm, 0)
        roll = float(np.median([r["relative_l2"] for r in ev["rollout_rows"]]))
        cons = float(np.median([r["ratio"] for r in ev["cons_rows"]]))
        perm_pass = sum(r["passes"] for r in ev["perm_rows"]); n = len(ev["perm_rows"])
        r = dict(tag=cfg["tag"], loss=cfg["loss"], grad_clip=cfg["grad_clip"], lr=cfg["lr"],
                 final_loss=round(losses[-1], 5), loss_first=round(losses[0], 5),
                 loss_min=round(min(losses), 5), rollout_median_relL2=round(roll, 5),
                 cons_ratio=round(cons, 4), node_perm=f"{perm_pass}/{n}",
                 train_s=round(wc, 1), loss_curve=[round(x, 4) for x in losses])
        results.append(r)
        print(f"[sweep] {cfg['tag']}: rollout={roll:.4f} final_loss={losses[-1]:.4f} "
              f"loss_min={min(losses):.4f} cons={cons:.3f} node_perm={perm_pass}/{n} "
              f"({wc:.0f}s)", flush=True)
        del model
        torch.cuda.empty_cache()

    results.sort(key=lambda x: x["rollout_median_relL2"])
    print("\nSWEEP_RESULTS " + json.dumps(results))
    print("\n=== ranked by rollout_median_relL2 (lower=better; baseline under-trained ~1.0) ===")
    for r in results:
        print(f"  {r['rollout_median_relL2']:.4f}  {r['tag']:22s} "
              f"loss {r['loss_first']:.3f}->{r['final_loss']:.3f} (min {r['loss_min']:.3f}) "
              f"cons {r['cons_ratio']:.3f} perm {r['node_perm']}")

if __name__ == "__main__":
    main()
