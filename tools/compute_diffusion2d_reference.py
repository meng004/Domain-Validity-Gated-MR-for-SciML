"""P2-1 fallback companion: FD reference solution for the 2D heat-equation
PINN with Neumann zero-flux BC.

Same PDE / IC / BC as tools/train_pinn_diffusion2d.py:
  d_t u = alpha * (u_xx + u_yy)
  alpha = 0.1, (x, y) in [-1, 1]^2, t in [0, 0.5]
  u(x, y, 0) = exp(-10(x^2 + y^2))
  homogeneous Neumann (zero-flux) on the four edges (so integral u dA is
  strictly conserved at the PDE level).

Scheme: forward Euler in time, centred FD for the Laplacian, Neumann zero-
flux implemented via edge-replicating ghost cells (np.pad mode='edge'). The
129 x 129 grid uses dt = 0.2 * dx^2 / alpha for stability.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/pinn-cross-family-diffusion/reference_solution.npz"
MANIFEST = ROOT / "research_assets/runs/pinn-cross-family-diffusion/reference_manifest.json"

ALPHA = 0.1
T_END = 0.5
N = 129
SAVE_TIMES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]


def step(u: np.ndarray, dx: float, dt: float, alpha: float) -> np.ndarray:
    p = np.pad(u, 1, mode="edge")  # Neumann zero-flux via ghost-cell replication
    lap = (p[2:, 1:-1] + p[:-2, 1:-1] + p[1:-1, 2:] + p[1:-1, :-2] - 4 * u) / dx ** 2
    return u + dt * alpha * lap


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dx = 2.0 / (N - 1)
    dt = 0.2 * dx ** 2 / ALPHA
    n_steps = int(np.ceil(T_END / dt))
    dt = T_END / n_steps

    x = np.linspace(-1, 1, N); y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y, indexing="ij")
    u = np.exp(-10 * (X ** 2 + Y ** 2)).astype(np.float64)

    snaps = {0.0: u.copy()}
    next_save = 1
    print(f"FD reference: N={N} dx={dx:.4e} dt={dt:.4e} n_steps={n_steps}", flush=True)
    for k in range(n_steps):
        u = step(u, dx, dt, ALPHA)
        t = (k + 1) * dt
        while (next_save < len(SAVE_TIMES)
               and t >= SAVE_TIMES[next_save] - 1e-9):
            snaps[SAVE_TIMES[next_save]] = u.copy()
            print(f"  saved t={SAVE_TIMES[next_save]}  "
                  f"||u||={np.linalg.norm(u):.4f}  "
                  f"sum={u.sum():.4f}", flush=True)
            next_save += 1

    dA = dx * dx
    masses = [float(snaps[ts].sum() * dA) for ts in SAVE_TIMES]
    drift_pct = 100.0 * (masses[-1] - masses[0]) / max(abs(masses[0]), 1e-12)
    print(f"\nmass per snapshot = {[f'{m:.6f}' for m in masses]}")
    print(f"mass drift over T_END = {drift_pct:+.4f}%")

    np.savez_compressed(
        OUT,
        x=x, y=y, snapshots_times=np.array(SAVE_TIMES),
        u_snapshots=np.stack([snaps[ts] for ts in SAVE_TIMES]),
        alpha=np.array(ALPHA), dx=np.array(dx), dt=np.array(dt),
        n_steps=np.array(n_steps),
    )
    MANIFEST.write_text(json.dumps({
        "record_type": "pinn-diffusion2d-reference",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scheme": ("forward Euler, centred FD Laplacian, Neumann zero-flux "
                   "via edge-replicating ghost cells"),
        "grid_N": N, "dx": dx, "dt": dt, "n_steps": n_steps,
        "alpha": ALPHA, "snapshot_times": SAVE_TIMES,
        "mass_per_snapshot": masses,
        "mass_drift_percent_over_T_END": drift_pct,
        "output": str(OUT.relative_to(ROOT)),
    }, indent=2), encoding="utf-8")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
