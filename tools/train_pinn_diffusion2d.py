"""P2-1 fallback: train a 2D heat-equation PINN as the second cross-family SUT.

PDE:  d_t u = alpha * (u_xx + u_yy), alpha = 0.1.
Domain (x, y) in [-1, 1]^2, t in [0, 0.5].
IC:   u(x, y, 0) = exp(-10 (x^2 + y^2))  -- symmetric under y -> -y so MR-B
      is admissible.
BC:   homogeneous Neumann (zero flux) on the four edges  -- so the integral
      conservation MR-C is STRICTLY exact (d/dt integral u dA = 0).

Architecture:  MLP 5 x 50 + tanh, input (x, y, t) -> output u (scalar).
Training:      Adam lr=1e-3 + StepLR (gamma=0.5, step=2000), 8000 iter.
Loss:          pde + 10*ic + 10*bc.
Seed:          torch.manual_seed(20260607).

This complements the Burgers 2D PINN (tools/train_pinn_burgers2d.py): the
Burgers SUT uses Dirichlet zero BC (near-conservation, ~0.4% boundary leakage)
while this Diffusion SUT uses Neumann zero-flux (strict conservation), so the
two SUTs jointly cover both BC families and the cross-family applicability
map gets a second bounded point.
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
import torch.nn as nn

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets/runs/pinn-cross-family-diffusion/sut"

ALPHA = 0.1
T_END = 0.5


class PINNScalar(nn.Module):
    def __init__(self, hidden: int = 50, layers: int = 5,
                 in_dim: int = 3, out_dim: int = 1):
        super().__init__()
        mods = []
        for i in range(layers):
            mods += [nn.Linear(in_dim if i == 0 else hidden, hidden), nn.Tanh()]
        mods += [nn.Linear(hidden, out_dim)]
        self.net = nn.Sequential(*mods)

    def forward(self, x):
        return self.net(x)


def diffusion_pde_residual(model: PINNScalar, xyt: torch.Tensor,
                           alpha: float = ALPHA) -> torch.Tensor:
    xyt = xyt.clone().requires_grad_(True)
    u = model(xyt).squeeze(-1)  # (N,)
    grad = torch.autograd.grad(u.sum(), xyt, create_graph=True)[0]
    u_x, u_y, u_t = grad[:, 0], grad[:, 1], grad[:, 2]
    u_xx = torch.autograd.grad(u_x.sum(), xyt, create_graph=True)[0][:, 0]
    u_yy = torch.autograd.grad(u_y.sum(), xyt, create_graph=True)[0][:, 1]
    res = u_t - alpha * (u_xx + u_yy)
    return (res ** 2).mean()


def ic_loss(model: PINNScalar, xy0: torch.Tensor) -> torch.Tensor:
    u = model(xy0).squeeze(-1)
    target = torch.exp(-10.0 * (xy0[:, 0] ** 2 + xy0[:, 1] ** 2))
    return ((u - target) ** 2).mean()


def neumann_bc_loss(model: PINNScalar, xyt_bc: torch.Tensor,
                    axis: torch.Tensor) -> torch.Tensor:
    """xyt_bc: (N, 3) points on the boundary.

    axis[i] in {0, 1} indicates whether the outward normal at that point is
    along x (axis=0) or along y (axis=1). The Neumann condition is
    du / d(normal) = 0; with axis-aligned domain the normal derivative is just
    u_x or u_y.
    """
    xyt = xyt_bc.clone().requires_grad_(True)
    u = model(xyt).squeeze(-1)
    grad = torch.autograd.grad(u.sum(), xyt, create_graph=True)[0]
    # Select grad along the relevant axis per-point.
    normal_grad = torch.where(axis == 0, grad[:, 0], grad[:, 1])
    return (normal_grad ** 2).mean()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seed", type=int, default=20260607)
    p.add_argument("--hidden", type=int, default=50)
    p.add_argument("--layers", type=int, default=5)
    p.add_argument("--iters", type=int, default=8000)
    p.add_argument("--n-collocation", type=int, default=8000)
    p.add_argument("--n-ic", type=int, default=1000)
    p.add_argument("--n-bc", type=int, default=1000)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--lr-step", type=int, default=2000)
    p.add_argument("--lr-gamma", type=float, default=0.5)
    p.add_argument("--outdir", default=str(OUTDIR))
    p.add_argument("--log-every", type=int, default=200)
    args = p.parse_args(argv)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    rng = np.random.default_rng(args.seed)

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    model = PINNScalar(hidden=args.hidden, layers=args.layers)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.StepLR(opt, args.lr_step, gamma=args.lr_gamma)

    coll = rng.uniform([-1, -1, 0], [1, 1, T_END],
                       size=(args.n_collocation, 3)).astype(np.float32)
    ic = np.column_stack([
        rng.uniform(-1, 1, args.n_ic),
        rng.uniform(-1, 1, args.n_ic),
        np.zeros(args.n_ic),
    ]).astype(np.float32)
    n_per_edge = max(1, args.n_bc // 4)
    bc_pts = []; bc_axis = []
    for edge in range(4):
        s = rng.uniform(-1, 1, n_per_edge)
        t = rng.uniform(0, T_END, n_per_edge)
        if edge == 0:    # x = -1, normal along x
            bc_pts.append(np.column_stack([np.full(n_per_edge, -1.0), s, t]))
            bc_axis.append(np.zeros(n_per_edge, dtype=np.int64))
        elif edge == 1:  # x = +1, normal along x
            bc_pts.append(np.column_stack([np.full(n_per_edge, 1.0), s, t]))
            bc_axis.append(np.zeros(n_per_edge, dtype=np.int64))
        elif edge == 2:  # y = -1, normal along y
            bc_pts.append(np.column_stack([s, np.full(n_per_edge, -1.0), t]))
            bc_axis.append(np.ones(n_per_edge, dtype=np.int64))
        else:            # y = +1, normal along y
            bc_pts.append(np.column_stack([s, np.full(n_per_edge, 1.0), t]))
            bc_axis.append(np.ones(n_per_edge, dtype=np.int64))
    bc = np.concatenate(bc_pts, 0).astype(np.float32)
    axis = np.concatenate(bc_axis, 0)

    coll_t = torch.tensor(coll); ic_t = torch.tensor(ic)
    bc_t = torch.tensor(bc); axis_t = torch.tensor(axis)

    loss_log = []
    t0 = time.time()
    Lp = torch.tensor(float("nan"))
    for it in range(args.iters):
        opt.zero_grad()
        Lp = diffusion_pde_residual(model, coll_t)
        Lic = ic_loss(model, ic_t)
        Lbc = neumann_bc_loss(model, bc_t, axis_t)
        L = Lp + 10.0 * Lic + 10.0 * Lbc
        L.backward()
        opt.step()
        sched.step()
        if it % args.log_every == 0 or it == args.iters - 1:
            entry = {"iter": it, "pde": float(Lp), "ic": float(Lic),
                     "bc": float(Lbc), "total": float(L),
                     "elapsed_s": time.time() - t0}
            loss_log.append(entry)
            print(f"iter {it:5d}/{args.iters} pde={Lp.item():.4e} "
                  f"ic={Lic.item():.4e} bc={Lbc.item():.4e} "
                  f"t={entry['elapsed_s']:.1f}s", flush=True)

    ckpt = outdir / "checkpoint.pt"
    torch.save({"state_dict": model.state_dict(), "config": vars(args),
                "loss_log": loss_log}, ckpt)
    sha = hashlib.sha256(ckpt.read_bytes()).hexdigest()
    manifest = {
        "record_type": "pinn-diffusion2d-training",
        "sut_id": "pinn_diffusion2d_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checkpoint": str(ckpt.relative_to(ROOT)),
        "checkpoint_sha256": sha,
        "config": vars(args),
        "loss_first": loss_log[0] if loss_log else None,
        "loss_last": loss_log[-1] if loss_log else None,
        "final_pde_residual_l2_sq": float(Lp.item()),
        "final_pde_residual_l2": float(Lp.item() ** 0.5),
        "num_parameters": sum(pp.numel() for pp in model.parameters()),
        "pde": "2D heat equation, alpha=0.1, domain [-1,1]^2 x [0, 0.5]",
        "ic": "u = exp(-10(x^2 + y^2)) (symmetric under y -> -y)",
        "bc": "homogeneous Neumann (zero-flux) on the four edges",
        "honesty_boundary": (
            "One PINN, one PDE, one seed. Not a generalization across PINN "
            "architectures or PDEs."
        ),
    }
    (outdir.parent / "checkpoint_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nwrote {ckpt}\n  sha={sha[:12]} "
          f"final_pde_res_l2={manifest['final_pde_residual_l2']:.4e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
