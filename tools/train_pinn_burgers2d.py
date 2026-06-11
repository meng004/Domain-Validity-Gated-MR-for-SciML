"""P2-1: train a 2D viscous Burgers PINN as the cross-family SUT.

PDE: d_t u + (u . grad) u = nu * Laplacian u on (x,y) in [-1,1]^2, t in [0, 0.5].
Vector field u = (u_x, u_y). nu = 0.05.

IC:  u_x(x,y,0) = exp(-5(x^2 + y^2)), u_y(x,y,0) = 0
     -- symmetric under (x, y, u_x, u_y) -> (x, -y, u_x, -u_y) so MR-B is admissible.
BC:  Dirichlet u = 0 on the boundary.

Architecture: MLP (default 5 x 50 + tanh), input (x,y,t) in R^3, output (u_x, u_y).
Training:  Adam lr=1e-3 + StepLR (gamma=0.5 every 2000 iter), default 8000 iter.
Loss:      pde + 10*ic + 10*bc.

Seed-deterministic (torch + numpy + np.random.default_rng); the produced
checkpoint sha256 is recorded alongside the loss log and final PDE residual
under research_assets/runs/pinn-cross-family/sut/.
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
OUTDIR = ROOT / "research_assets/runs/pinn-cross-family/sut"

NU = 0.05
T_END = 0.5


class PINN(nn.Module):
    def __init__(self, hidden: int = 50, layers: int = 5,
                 in_dim: int = 3, out_dim: int = 2):
        super().__init__()
        mods = []
        for i in range(layers):
            mods += [nn.Linear(in_dim if i == 0 else hidden, hidden), nn.Tanh()]
        mods += [nn.Linear(hidden, out_dim)]
        self.net = nn.Sequential(*mods)

    def forward(self, x):
        return self.net(x)


def burgers_pde_residual(model: PINN, xyt: torch.Tensor, nu: float = NU) -> torch.Tensor:
    xyt = xyt.clone().requires_grad_(True)
    u = model(xyt)
    ux = u[:, 0]
    uy = u[:, 1]
    grad_ux = torch.autograd.grad(ux.sum(), xyt, create_graph=True)[0]
    grad_uy = torch.autograd.grad(uy.sum(), xyt, create_graph=True)[0]
    ux_x, ux_y, ux_t = grad_ux[:, 0], grad_ux[:, 1], grad_ux[:, 2]
    uy_x, uy_y, uy_t = grad_uy[:, 0], grad_uy[:, 1], grad_uy[:, 2]
    ux_xx = torch.autograd.grad(ux_x.sum(), xyt, create_graph=True)[0][:, 0]
    ux_yy = torch.autograd.grad(ux_y.sum(), xyt, create_graph=True)[0][:, 1]
    uy_xx = torch.autograd.grad(uy_x.sum(), xyt, create_graph=True)[0][:, 0]
    uy_yy = torch.autograd.grad(uy_y.sum(), xyt, create_graph=True)[0][:, 1]
    lap_x = ux_xx + ux_yy
    lap_y = uy_xx + uy_yy
    res_x = ux_t + ux * ux_x + uy * ux_y - nu * lap_x
    res_y = uy_t + ux * uy_x + uy * uy_y - nu * lap_y
    return (res_x ** 2 + res_y ** 2).mean()


def ic_loss(model: PINN, xy0: torch.Tensor) -> torch.Tensor:
    u = model(xy0)
    ux_target = torch.exp(-5.0 * (xy0[:, 0] ** 2 + xy0[:, 1] ** 2))
    return ((u[:, 0] - ux_target) ** 2 + u[:, 1] ** 2).mean()


def bc_loss(model: PINN, xyt_bc: torch.Tensor) -> torch.Tensor:
    u = model(xyt_bc)
    return (u ** 2).sum(-1).mean()


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
    p.add_argument("--early-stop-residual", type=float, default=None,
                   help="if set, stop when PDE residual L2 < this")
    p.add_argument("--log-every", type=int, default=200)
    args = p.parse_args(argv)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    rng = np.random.default_rng(args.seed)

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    model = PINN(hidden=args.hidden, layers=args.layers)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.StepLR(opt, args.lr_step, gamma=args.lr_gamma)

    # Fixed-sample-set training (small sandbox; resamping per iter is overkill).
    coll = rng.uniform([-1, -1, 0], [1, 1, T_END],
                       size=(args.n_collocation, 3)).astype(np.float32)
    ic = np.column_stack([
        rng.uniform(-1, 1, args.n_ic),
        rng.uniform(-1, 1, args.n_ic),
        np.zeros(args.n_ic),
    ]).astype(np.float32)
    n_per_edge = max(1, args.n_bc // 4)
    bc_list = []
    for edge in range(4):
        s = rng.uniform(-1, 1, n_per_edge)
        t = rng.uniform(0, T_END, n_per_edge)
        if edge == 0:
            bc_list.append(np.column_stack([np.full(n_per_edge, -1.0), s, t]))
        elif edge == 1:
            bc_list.append(np.column_stack([np.full(n_per_edge, 1.0), s, t]))
        elif edge == 2:
            bc_list.append(np.column_stack([s, np.full(n_per_edge, -1.0), t]))
        else:
            bc_list.append(np.column_stack([s, np.full(n_per_edge, 1.0), t]))
    bc = np.concatenate(bc_list, 0).astype(np.float32)

    coll_t = torch.tensor(coll)
    ic_t = torch.tensor(ic)
    bc_t = torch.tensor(bc)

    loss_log = []
    t0 = time.time()
    Lp = torch.tensor(float("nan"))
    for it in range(args.iters):
        opt.zero_grad()
        Lp = burgers_pde_residual(model, coll_t)
        Lic = ic_loss(model, ic_t)
        Lbc = bc_loss(model, bc_t)
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
            if args.early_stop_residual and Lp.item() < args.early_stop_residual:
                print(f"early-stop at iter {it} pde={Lp.item():.4e} "
                      f"< {args.early_stop_residual}")
                break

    ckpt = outdir / "checkpoint.pt"
    torch.save({"state_dict": model.state_dict(), "config": vars(args),
                "loss_log": loss_log}, ckpt)
    sha = hashlib.sha256(ckpt.read_bytes()).hexdigest()
    manifest = {
        "record_type": "pinn-burgers2d-training",
        "sut_id": "pinn_burgers2d_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checkpoint": str(ckpt.relative_to(ROOT)),
        "checkpoint_sha256": sha,
        "config": vars(args),
        "loss_first": loss_log[0] if loss_log else None,
        "loss_last": loss_log[-1] if loss_log else None,
        "final_pde_residual_l2_sq": float(Lp.item()),
        "final_pde_residual_l2": float(Lp.item() ** 0.5),
        "num_parameters": sum(pp.numel() for pp in model.parameters()),
        "pde": "2D viscous Burgers, nu=0.05, domain [-1,1]^2 x [0, 0.5]",
        "ic": "u_x = exp(-5(x^2 + y^2)), u_y = 0 (symmetric under y -> -y)",
        "bc": "Dirichlet u = 0 on boundary",
        "honesty_boundary": (
            "One PINN, one PDE, one seed, one set of hyperparameters. "
            "Not a generalization across PINN architectures or PDEs."
        ),
    }
    (outdir.parent / "checkpoint_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nwrote {ckpt}\n  sha={sha[:12]} "
          f"final_pde_res_l2={manifest['final_pde_residual_l2']:.4e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
