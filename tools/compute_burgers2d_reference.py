"""P2-1 helper: compute a high-resolution FD reference solution for the 2D
viscous Burgers problem the PINN is trained on.

Same PDE / IC / BC as tools/train_pinn_burgers2d.py:
  d_t u + (u . grad) u = nu * Laplacian u
  nu = 0.05, (x, y) in [-1, 1]^2, t in [0, 0.5]
  u_x(x,y,0) = exp(-5(x^2 + y^2)), u_y(x,y,0) = 0
  Dirichlet u = 0 on the boundary.

Scheme: forward Euler in time, FIRST-ORDER UPWIND finite differences for the
advection term and centred differences for the Laplacian, on a 129 x 129 grid
(dx = 2 / 128). Centred FD on the advection term blows up for Burgers; upwind
is monotone and stable. Time step satisfies both the diffusive (dt < 0.5 *
dx^2 / nu) and CFL (dt < dx / max|u|) constraints; we use a safety factor 0.2.

Outputs research_assets/runs/pinn-cross-family/reference_solution.npz
containing snapshots at t in {0.0, 0.1, 0.2, 0.3, 0.4, 0.5}, plus integration
metadata for audit.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/pinn-cross-family/reference_solution.npz"
MANIFEST = ROOT / "research_assets/runs/pinn-cross-family/reference_manifest.json"

NU = 0.05
T_END = 0.5
N = 129  # grid points per axis; dx = 2 / (N - 1)
SAVE_TIMES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]


def _upwind_grad(field: np.ndarray, vel: np.ndarray, axis: int, dx: float) -> np.ndarray:
    """Upwind first derivative of `field` along `axis` using sign of `vel`."""
    back = (field - np.roll(field, 1, axis)) / dx
    fwd = (np.roll(field, -1, axis) - field) / dx
    return np.where(vel >= 0, vel * back, vel * fwd)


def step(u: np.ndarray, v: np.ndarray, dx: float, dt: float, nu: float
         ) -> tuple[np.ndarray, np.ndarray]:
    # Upwind advection (stable for Burgers).
    adv_u = _upwind_grad(u, u, 0, dx) + _upwind_grad(u, v, 1, dx)
    adv_v = _upwind_grad(v, u, 0, dx) + _upwind_grad(v, v, 1, dx)
    # Centred Laplacian for diffusion.
    lap_u = ((np.roll(u, -1, 0) + np.roll(u, 1, 0)
             + np.roll(u, -1, 1) + np.roll(u, 1, 1) - 4 * u) / dx ** 2)
    lap_v = ((np.roll(v, -1, 0) + np.roll(v, 1, 0)
             + np.roll(v, -1, 1) + np.roll(v, 1, 1) - 4 * v) / dx ** 2)
    u_new = u + dt * (-adv_u + nu * lap_u)
    v_new = v + dt * (-adv_v + nu * lap_v)
    u_new[0, :] = 0; u_new[-1, :] = 0; u_new[:, 0] = 0; u_new[:, -1] = 0
    v_new[0, :] = 0; v_new[-1, :] = 0; v_new[:, 0] = 0; v_new[:, -1] = 0
    return u_new, v_new


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dx = 2.0 / (N - 1)
    # Both diffusive (dt < 0.5 dx^2/nu) and CFL (dt < dx/max|u|, max|u|=1) bounds.
    dt_diff = 0.2 * dx ** 2 / NU
    dt_cfl = 0.5 * dx / 1.0
    dt = min(dt_diff, dt_cfl)
    n_steps = int(np.ceil(T_END / dt))
    dt = T_END / n_steps  # adjust so n_steps * dt == T_END exactly

    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y, indexing="ij")
    u = np.exp(-5 * (X ** 2 + Y ** 2)).astype(np.float64)
    v = np.zeros_like(u)
    u[0, :] = 0; u[-1, :] = 0; u[:, 0] = 0; u[:, -1] = 0  # impose Dirichlet 0 on IC at boundary

    snaps_u = {0.0: u.copy()}
    snaps_v = {0.0: v.copy()}
    next_save_idx = 1
    t_now = 0.0
    print(f"reference FD: N={N} dx={dx:.4e} dt={dt:.4e} n_steps={n_steps}", flush=True)
    for k in range(n_steps):
        u, v = step(u, v, dx, dt, NU)
        t_now = (k + 1) * dt
        while (next_save_idx < len(SAVE_TIMES)
               and t_now >= SAVE_TIMES[next_save_idx] - 1e-9):
            ts = SAVE_TIMES[next_save_idx]
            snaps_u[ts] = u.copy()
            snaps_v[ts] = v.copy()
            print(f"  saved t={ts}  ||u||={np.linalg.norm(u):.4f}", flush=True)
            next_save_idx += 1
        if k % max(1, n_steps // 20) == 0:
            print(f"  step {k}/{n_steps}  t={t_now:.4f}  ||u||={np.linalg.norm(u):.4f}",
                  flush=True)

    times = np.array(SAVE_TIMES)
    np.savez_compressed(
        OUT,
        x=x, y=y, snapshots_times=times,
        u_snapshots=np.stack([snaps_u[t] for t in SAVE_TIMES]),
        v_snapshots=np.stack([snaps_v[t] for t in SAVE_TIMES]),
        nu=np.array(NU), dx=np.array(dx), dt=np.array(dt),
        n_steps=np.array(n_steps),
    )
    MANIFEST.write_text(json.dumps({
        "record_type": "pinn-burgers2d-reference",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scheme": "forward Euler, centred FD, Dirichlet 0 BC",
        "grid_N": N, "dx": dx, "dt": dt, "n_steps": n_steps,
        "nu": NU, "snapshot_times": SAVE_TIMES,
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
