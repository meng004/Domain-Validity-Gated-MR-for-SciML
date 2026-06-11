"""P2: PINN K=6 roster — 3 seeds x 2 PDEs with MR evaluation and bootstrap CIs.

Trains 6 PINN checkpoints (Burgers2D seeds {0,1,2} + Diffusion2D seeds {0,1,2}),
runs MR-A/B/C + rollout accuracy on each, and produces an aggregate report with
B=2000 bootstrap 95% CIs over the seed-replica families — the same pattern as
the MGN E1 multi-checkpoint replication.

Usage:
  python3 tools/run_pinn_k6_roster.py [--iters 8000] [--batch-size 512] [--skip-existing]

Outputs:
  research_assets/runs/pinn-k6-roster/
    burgers_s0/ burgers_s1/ burgers_s2/     (each: sut/checkpoint.pt + mr_report.json)
    diffusion_s0/ diffusion_s1/ diffusion_s2/
    pinn_k6_aggregate.json                   (aggregate with bootstrap CIs)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
ROSTER_DIR = ROOT / "research_assets/runs/pinn-k6-roster"
BURGERS_REF = ROOT / "research_assets/runs/pinn-cross-family/reference_solution.npz"
DIFFUSION_REF = ROOT / "research_assets/runs/pinn-cross-family-diffusion/reference_solution.npz"

SEEDS = [0, 1, 2]
N_BOOTSTRAP = 2000
EVAL_SEED = 42
N_EVAL = 5000

sys.path.insert(0, str(ROOT / "tools"))
from train_pinn_burgers2d import PINN, burgers_pde_residual, NU, T_END as BURGERS_T_END  # noqa: E402
from train_pinn_diffusion2d import PINNScalar, diffusion_pde_residual, ALPHA, T_END as DIFF_T_END  # noqa: E402


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + 1e-12))


def _batch(t: torch.Tensor, rng: np.random.Generator, batch_size: int) -> torch.Tensor:
    if batch_size <= 0 or batch_size >= len(t):
        return t
    idx = rng.choice(len(t), size=batch_size, replace=False)
    return t[torch.as_tensor(idx, dtype=torch.long)]


def train_burgers(seed: int, outdir: Path, iters: int, batch_size: int) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    model = PINN(hidden=50, layers=5)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    sched = torch.optim.lr_scheduler.StepLR(opt, 2000, gamma=0.5)

    coll = rng.uniform([-1, -1, 0], [1, 1, 0.5], (8000, 3)).astype(np.float32)
    ic = np.column_stack([rng.uniform(-1, 1, 1000), rng.uniform(-1, 1, 1000),
                          np.zeros(1000)]).astype(np.float32)
    n_per = 250
    bc_list = []
    for edge in range(4):
        s = rng.uniform(-1, 1, n_per)
        t = rng.uniform(0, 0.5, n_per)
        if edge == 0:
            bc_list.append(np.column_stack([np.full(n_per, -1.0), s, t]))
        elif edge == 1:
            bc_list.append(np.column_stack([np.full(n_per, 1.0), s, t]))
        elif edge == 2:
            bc_list.append(np.column_stack([s, np.full(n_per, -1.0), t]))
        else:
            bc_list.append(np.column_stack([s, np.full(n_per, 1.0), t]))
    bc = np.concatenate(bc_list, 0).astype(np.float32)

    coll_t = torch.tensor(coll)
    ic_t = torch.tensor(ic)
    bc_t = torch.tensor(bc)

    t0 = time.time()
    Lp = torch.tensor(float("nan"))
    for it in range(iters):
        opt.zero_grad()
        coll_b = _batch(coll_t, rng, batch_size)
        ic_b = _batch(ic_t, rng, max(1, batch_size // 4))
        bc_b = _batch(bc_t, rng, max(1, batch_size // 4))
        Lp = burgers_pde_residual(model, coll_b)
        from train_pinn_burgers2d import ic_loss as b_ic_loss, bc_loss as b_bc_loss
        Lic = b_ic_loss(model, ic_b)
        Lbc = b_bc_loss(model, bc_b)
        L = Lp + 10.0 * Lic + 10.0 * Lbc
        L.backward()
        opt.step()
        sched.step()

    # Measure the final PDE residual on the full collocation grid once for the manifest.
    Lp = burgers_pde_residual(model, coll_t)
    elapsed = time.time() - t0
    ckpt_path = outdir / "checkpoint.pt"
    torch.save({"state_dict": model.state_dict(),
                "config": {"seed": seed, "hidden": 50, "layers": 5,
                           "iters": iters, "batch_size": batch_size}},
               ckpt_path)
    sha = hashlib.sha256(ckpt_path.read_bytes()).hexdigest()
    final_res = float(Lp.item() ** 0.5)
    manifest = {
        "sut_id": f"pinn_burgers2d_s{seed}",
        "pde": "burgers2d", "seed": seed,
        "checkpoint_sha256": sha,
        "final_pde_residual_l2": final_res,
        "num_parameters": sum(p.numel() for p in model.parameters()),
        "train_iters": iters,
        "batch_size": batch_size,
        "elapsed_s": elapsed,
    }
    return manifest


def train_diffusion(seed: int, outdir: Path, iters: int, batch_size: int) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    outdir.mkdir(parents=True, exist_ok=True)

    model = PINNScalar(hidden=50, layers=5)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    sched = torch.optim.lr_scheduler.StepLR(opt, 2000, gamma=0.5)

    coll = rng.uniform([-1, -1, 0], [1, 1, 0.5], (8000, 3)).astype(np.float32)
    ic = np.column_stack([rng.uniform(-1, 1, 1000), rng.uniform(-1, 1, 1000),
                          np.zeros(1000)]).astype(np.float32)
    n_per = 250
    bc_pts = []; bc_axis = []
    for edge in range(4):
        s = rng.uniform(-1, 1, n_per)
        t = rng.uniform(0, 0.5, n_per)
        if edge == 0:
            bc_pts.append(np.column_stack([np.full(n_per, -1.0), s, t]))
            bc_axis.append(np.zeros(n_per, dtype=np.int64))
        elif edge == 1:
            bc_pts.append(np.column_stack([np.full(n_per, 1.0), s, t]))
            bc_axis.append(np.zeros(n_per, dtype=np.int64))
        elif edge == 2:
            bc_pts.append(np.column_stack([s, np.full(n_per, -1.0), t]))
            bc_axis.append(np.ones(n_per, dtype=np.int64))
        else:
            bc_pts.append(np.column_stack([s, np.full(n_per, 1.0), t]))
            bc_axis.append(np.ones(n_per, dtype=np.int64))
    bc = np.concatenate(bc_pts, 0).astype(np.float32)
    axis = np.concatenate(bc_axis, 0)

    coll_t = torch.tensor(coll)
    ic_t = torch.tensor(ic)
    bc_t = torch.tensor(bc)
    axis_t = torch.tensor(axis)

    t0 = time.time()
    Lp = torch.tensor(float("nan"))
    for it in range(iters):
        opt.zero_grad()
        coll_b = _batch(coll_t, rng, batch_size)
        ic_b = _batch(ic_t, rng, max(1, batch_size // 4))
        bc_idx = rng.choice(len(bc_t), size=min(max(1, batch_size // 4), len(bc_t)),
                            replace=False)
        bc_b = bc_t[torch.as_tensor(bc_idx, dtype=torch.long)]
        axis_b = axis_t[torch.as_tensor(bc_idx, dtype=torch.long)]
        Lp = diffusion_pde_residual(model, coll_b)
        from train_pinn_diffusion2d import ic_loss as d_ic_loss, neumann_bc_loss
        Lic = d_ic_loss(model, ic_b)
        Lbc = neumann_bc_loss(model, bc_b, axis_b)
        L = Lp + 10.0 * Lic + 10.0 * Lbc
        L.backward()
        opt.step()
        sched.step()

    # Measure the final PDE residual on the full collocation grid once for the manifest.
    Lp = diffusion_pde_residual(model, coll_t)
    elapsed = time.time() - t0
    ckpt_path = outdir / "checkpoint.pt"
    torch.save({"state_dict": model.state_dict(),
                "config": {"seed": seed, "hidden": 50, "layers": 5,
                           "iters": iters, "batch_size": batch_size}},
               ckpt_path)
    sha = hashlib.sha256(ckpt_path.read_bytes()).hexdigest()
    final_res = float(Lp.item() ** 0.5)
    manifest = {
        "sut_id": f"pinn_diffusion2d_s{seed}",
        "pde": "diffusion2d", "seed": seed,
        "checkpoint_sha256": sha,
        "final_pde_residual_l2": final_res,
        "num_parameters": sum(p.numel() for p in model.parameters()),
        "train_iters": iters,
        "batch_size": batch_size,
        "elapsed_s": elapsed,
    }
    return manifest


def eval_burgers_mrs(ckpt_dir: Path, manifest: dict, rng: np.random.Generator) -> dict:
    state = torch.load(ckpt_dir / "checkpoint.pt", map_location="cpu", weights_only=False)
    cfg = state["config"]
    model = PINN(hidden=cfg["hidden"], layers=cfg["layers"])
    model.load_state_dict(state["state_dict"])
    model.eval()
    floor = manifest["final_pde_residual_l2"]
    ref = np.load(BURGERS_REF)

    xyt = rng.uniform([-1, -1, 0.0], [1, 1, 0.5], (N_EVAL, 3)).astype(np.float32)
    with torch.no_grad():
        u_pred = model(torch.from_numpy(xyt)).numpy()
    perm = rng.permutation(N_EVAL)
    inv = np.empty_like(perm); inv[perm] = np.arange(N_EVAL)
    with torch.no_grad():
        u_perm = model(torch.from_numpy(xyt[perm])).numpy()
    mr_a = relative_l2(u_perm[inv], u_pred)

    xyt_R = xyt.copy(); xyt_R[:, 1] = -xyt_R[:, 1]
    with torch.no_grad():
        u_R = model(torch.from_numpy(xyt_R)).numpy()
    u_via_R = np.column_stack([u_R[:, 0], -u_R[:, 1]])
    mr_b = relative_l2(u_via_R, u_pred)
    mr_b_ratio = mr_b / (floor + 1e-12)

    x = ref["x"]; y = ref["y"]; times = ref["snapshots_times"]
    X, Y = np.meshgrid(x, y, indexing="ij")
    dx = float(x[1] - x[0]); dy = float(y[1] - y[0]); dA = dx * dy
    ratios = []; rollout_l2s = []
    for k, t_eval in enumerate(times):
        xyt_g = np.column_stack([X.ravel(), Y.ravel(),
                                 np.full(X.size, float(t_eval))]).astype(np.float32)
        with torch.no_grad():
            u_g = model(torch.from_numpy(xyt_g)).numpy()
        ux_p = u_g[:, 0].reshape(X.shape)
        uy_p = u_g[:, 1].reshape(X.shape)
        ux_r = ref["u_snapshots"][k]; uy_r = ref["v_snapshots"][k]
        Q_pred = float(np.sum(ux_p) * dA)
        Q_ref = float(np.sum(ux_r) * dA)
        ratios.append(Q_pred / Q_ref if abs(Q_ref) > 1e-6 else float("nan"))
        rollout_l2s.append(relative_l2(np.stack([ux_p, uy_p]), np.stack([ux_r, uy_r])))

    finite_r = [r for r in ratios if np.isfinite(r)]
    mr_c_median = float(np.median(finite_r)) if finite_r else float("nan")
    rollout_median = float(np.median(rollout_l2s))

    return {
        "mr_a_violation": mr_a,
        "mr_a_verdict": "pass" if mr_a < 1e-5 else ("fail" if mr_a > 1e-3 else "borderline"),
        "mr_b_violation": mr_b,
        "mr_b_floor": floor,
        "mr_b_ratio": mr_b_ratio,
        "mr_b_verdict": "pass" if mr_b_ratio < 1.0 else "fail",
        "mr_c_median_ratio": mr_c_median,
        "mr_c_verdict": "pass" if 0.667 <= mr_c_median <= 1.5 else "fail",
        "rollout_median_rel_l2": rollout_median,
    }


def eval_diffusion_mrs(ckpt_dir: Path, manifest: dict, rng: np.random.Generator) -> dict:
    state = torch.load(ckpt_dir / "checkpoint.pt", map_location="cpu", weights_only=False)
    cfg = state["config"]
    model = PINNScalar(hidden=cfg["hidden"], layers=cfg["layers"])
    model.load_state_dict(state["state_dict"])
    model.eval()
    floor = manifest["final_pde_residual_l2"]
    ref = np.load(DIFFUSION_REF)

    xyt = rng.uniform([-1, -1, 0.0], [1, 1, 0.5], (N_EVAL, 3)).astype(np.float32)
    with torch.no_grad():
        u_pred = model(torch.from_numpy(xyt)).numpy().squeeze(-1)
    perm = rng.permutation(N_EVAL)
    inv = np.empty_like(perm); inv[perm] = np.arange(N_EVAL)
    with torch.no_grad():
        u_perm = model(torch.from_numpy(xyt[perm])).numpy().squeeze(-1)
    mr_a = relative_l2(u_perm[inv], u_pred)

    xyt_R = xyt.copy(); xyt_R[:, 1] = -xyt_R[:, 1]
    with torch.no_grad():
        u_R = model(torch.from_numpy(xyt_R)).numpy().squeeze(-1)
    mr_b = relative_l2(u_R, u_pred)
    mr_b_ratio = mr_b / (floor + 1e-12)

    x = ref["x"]; y = ref["y"]; times = ref["snapshots_times"]
    X, Y = np.meshgrid(x, y, indexing="ij")
    dx = float(x[1] - x[0]); dA = dx * dx
    ratios = []; rollout_l2s = []
    for k, t_eval in enumerate(times):
        xyt_g = np.column_stack([X.ravel(), Y.ravel(),
                                 np.full(X.size, float(t_eval))]).astype(np.float32)
        with torch.no_grad():
            u_g = model(torch.from_numpy(xyt_g)).numpy().squeeze(-1).reshape(X.shape)
        u_ref = ref["u_snapshots"][k]
        Q_pred = float(np.sum(u_g) * dA)
        Q_ref = float(np.sum(u_ref) * dA)
        ratios.append(Q_pred / Q_ref if abs(Q_ref) > 1e-6 else float("nan"))
        rollout_l2s.append(relative_l2(u_g, u_ref))

    finite_r = [r for r in ratios if np.isfinite(r)]
    mr_c_median = float(np.median(finite_r)) if finite_r else float("nan")
    rollout_median = float(np.median(rollout_l2s))

    return {
        "mr_a_violation": mr_a,
        "mr_a_verdict": "pass" if mr_a < 1e-5 else ("fail" if mr_a > 1e-3 else "borderline"),
        "mr_b_violation": mr_b,
        "mr_b_floor": floor,
        "mr_b_ratio": mr_b_ratio,
        "mr_b_verdict": "pass" if mr_b_ratio < 1.0 else "fail",
        "mr_c_median_ratio": mr_c_median,
        "mr_c_verdict": "pass" if 0.667 <= mr_c_median <= 1.5 else "fail",
        "rollout_median_rel_l2": rollout_median,
    }


def bootstrap_ci(values: list[float], n_boot: int = N_BOOTSTRAP,
                 alpha: float = 0.05) -> tuple[float, float, float]:
    arr = np.array(values)
    rng = np.random.default_rng(12345)
    means = np.array([float(np.mean(rng.choice(arr, size=len(arr), replace=True)))
                      for _ in range(n_boot)])
    lo = float(np.percentile(means, 100 * alpha / 2))
    hi = float(np.percentile(means, 100 * (1 - alpha / 2)))
    return float(np.mean(arr)), lo, hi


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iters", type=int, default=8000)
    p.add_argument("--batch-size", type=int, default=512,
                   help="Stochastic training batch size; <=0 means full batch")
    p.add_argument("--skip-existing", action="store_true")
    args = p.parse_args(argv)

    ROSTER_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for pde in ["burgers", "diffusion"]:
        for seed in SEEDS:
            tag = f"{pde}_s{seed}"
            sut_dir = ROSTER_DIR / tag / "sut"
            ckpt_path = sut_dir / "checkpoint.pt"

            if args.skip_existing and ckpt_path.exists():
                print(f"[{tag}] skip training (checkpoint exists)")
                manifest_path = ROSTER_DIR / tag / "manifest.json"
                if manifest_path.exists():
                    manifest = json.loads(manifest_path.read_text())
                else:
                    state = torch.load(ckpt_path, map_location="cpu", weights_only=False)
                    cfg = state.get("config", {})
                    sha = hashlib.sha256(ckpt_path.read_bytes()).hexdigest()
                    manifest = {
                        "sut_id": f"pinn_{pde}2d_s{seed}", "pde": f"{pde}2d",
                        "seed": seed, "checkpoint_sha256": sha,
                        "final_pde_residual_l2": float("nan"),
                        "num_parameters": 0, "elapsed_s": 0,
                        "train_iters": cfg.get("iters"),
                        "batch_size": cfg.get("batch_size", args.batch_size),
                    }
            else:
                print(f"[{tag}] training ...", flush=True)
                if pde == "burgers":
                    manifest = train_burgers(seed, sut_dir, args.iters, args.batch_size)
                else:
                    manifest = train_diffusion(seed, sut_dir, args.iters, args.batch_size)
                print(f"  done: residual_l2={manifest['final_pde_residual_l2']:.4e} "
                      f"({manifest['elapsed_s']:.1f}s)")

            (ROSTER_DIR / tag / "manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8")

            print(f"[{tag}] evaluating MRs ...", flush=True)
            eval_rng = np.random.default_rng(EVAL_SEED)
            if pde == "burgers":
                mr = eval_burgers_mrs(sut_dir, manifest, eval_rng)
            else:
                mr = eval_diffusion_mrs(sut_dir, manifest, eval_rng)
            mr["sut_id"] = manifest["sut_id"]
            mr["pde"] = pde
            mr["seed"] = seed
            mr["checkpoint_sha256"] = manifest["checkpoint_sha256"]
            mr["final_pde_residual_l2"] = manifest["final_pde_residual_l2"]

            (ROSTER_DIR / tag / "mr_report.json").write_text(
                json.dumps(mr, indent=2), encoding="utf-8")
            print(f"  MR-A={mr['mr_a_violation']:.2e} MR-B ratio={mr['mr_b_ratio']:.3f} "
                  f"MR-C={mr['mr_c_median_ratio']:.4f} rollout={mr['rollout_median_rel_l2']:.3e}")
            results.append(mr)

    # Aggregate with bootstrap CIs per PDE family
    aggregate = {
        "record_type": "pinn-k6-roster-aggregate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_seeds": len(SEEDS), "seeds": SEEDS,
        "train_iters": args.iters,
        "train_batch_size": args.batch_size,
        "n_bootstrap": N_BOOTSTRAP,
        "per_sut": results,
        "per_pde_family": {},
    }

    for pde in ["burgers", "diffusion"]:
        family = [r for r in results if r["pde"] == pde]
        mr_b_ratios = [r["mr_b_ratio"] for r in family]
        mr_c_medians = [r["mr_c_median_ratio"] for r in family]
        rollouts = [r["rollout_median_rel_l2"] for r in family]

        mr_b_mean, mr_b_lo, mr_b_hi = bootstrap_ci(mr_b_ratios)
        mr_c_mean, mr_c_lo, mr_c_hi = bootstrap_ci(mr_c_medians)
        roll_mean, roll_lo, roll_hi = bootstrap_ci(rollouts)

        mr_b_verdict_counts = {lab: sum(1 for r in family if r["mr_b_verdict"] == lab)
                               for lab in sorted({r["mr_b_verdict"] for r in family})}
        mr_c_verdict_counts = {lab: sum(1 for r in family if r["mr_c_verdict"] == lab)
                               for lab in sorted({r["mr_c_verdict"] for r in family})}
        mr_b_same = len(mr_b_verdict_counts) == 1
        mr_c_same = len(mr_c_verdict_counts) == 1

        aggregate["per_pde_family"][pde] = {
            "mr_a_all_pass": all(r["mr_a_verdict"] == "pass" for r in family),
            "mr_b_ratio_mean": mr_b_mean,
            "mr_b_ratio_95ci": [mr_b_lo, mr_b_hi],
            "mr_b_verdict_counts": mr_b_verdict_counts,
            "mr_b_pass_rate": mr_b_verdict_counts.get("pass", 0) / len(family),
            "mr_b_all_same_verdict": mr_b_same,
            "mr_b_verdict": family[0]["mr_b_verdict"] if mr_b_same else "mixed",
            "mr_c_median_mean": mr_c_mean,
            "mr_c_median_95ci": [mr_c_lo, mr_c_hi],
            "mr_c_verdict_counts": mr_c_verdict_counts,
            "mr_c_pass_rate": mr_c_verdict_counts.get("pass", 0) / len(family),
            "mr_c_all_same_verdict": mr_c_same,
            "mr_c_verdict": family[0]["mr_c_verdict"] if mr_c_same else "mixed",
            "rollout_mean": roll_mean,
            "rollout_95ci": [roll_lo, roll_hi],
        }

    out = ROSTER_DIR / "pinn_k6_aggregate.json"
    out.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    print(f"\n=== Aggregate written to {out} ===")
    for pde, fam in aggregate["per_pde_family"].items():
        print(f"  {pde}: MR-A all_pass={fam['mr_a_all_pass']}  "
              f"MR-B ratio={fam['mr_b_ratio_mean']:.3f} CI{fam['mr_b_ratio_95ci']}  "
              f"MR-C={fam['mr_c_median_mean']:.4f} CI{fam['mr_c_median_95ci']}  "
              f"rollout={fam['rollout_mean']:.3e} CI{fam['rollout_95ci']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
