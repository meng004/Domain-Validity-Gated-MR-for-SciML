"""Generate small closed-form finite-difference datasets for FNO-2D pilots.

The datasets are intentionally modest: they support the FNO third-family roster
as an admissibility-gate evidence point, not as a solver benchmark.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "research_assets/runs/fno-k6-roster/datasets"

PDE_CHANNELS = {"heat": 1, "burgers": 2}


def _grid(n: int) -> tuple[np.ndarray, np.ndarray]:
    x = np.linspace(-1.0, 1.0, n, endpoint=False)
    y = np.linspace(-1.0, 1.0, n, endpoint=False)
    return np.meshgrid(x, y, indexing="ij")


def _initial_field(pde: str, n: int, rng: np.random.Generator) -> np.ndarray:
    x, y = _grid(n)
    cx, cy = rng.uniform(-0.45, 0.45, size=2)
    width = rng.uniform(5.0, 10.0)
    amp = rng.uniform(0.6, 1.1)
    blob = amp * np.exp(-width * ((x - cx) ** 2 + (y - cy) ** 2))
    if pde == "heat":
        return blob[None, :, :].astype(np.float32)
    swirl = rng.uniform(-0.25, 0.25) * np.sin(np.pi * x) * np.sin(np.pi * y)
    return np.stack([blob, swirl], axis=0).astype(np.float32)


def _laplacian(u: np.ndarray, dx: float, bc: str) -> np.ndarray:
    if bc == "periodic":
        return (
            np.roll(u, -1, -2) + np.roll(u, 1, -2)
            + np.roll(u, -1, -1) + np.roll(u, 1, -1) - 4.0 * u
        ) / dx ** 2
    p = np.pad(u, ((0, 0), (1, 1), (1, 1)), mode="constant")
    return (
        p[:, 2:, 1:-1] + p[:, :-2, 1:-1]
        + p[:, 1:-1, 2:] + p[:, 1:-1, :-2] - 4.0 * u
    ) / dx ** 2


def _burgers_step(u: np.ndarray, dx: float, dt: float, nu: float, bc: str) -> np.ndarray:
    ux, uy = u[0], u[1]
    if bc == "periodic":
        ddx = lambda f: (np.roll(f, -1, 0) - np.roll(f, 1, 0)) / (2.0 * dx)
        ddy = lambda f: (np.roll(f, -1, 1) - np.roll(f, 1, 1)) / (2.0 * dx)
    else:
        def ddx(f: np.ndarray) -> np.ndarray:
            p = np.pad(f, 1, mode="constant")
            return (p[2:, 1:-1] - p[:-2, 1:-1]) / (2.0 * dx)

        def ddy(f: np.ndarray) -> np.ndarray:
            p = np.pad(f, 1, mode="constant")
            return (p[1:-1, 2:] - p[1:-1, :-2]) / (2.0 * dx)

    adv_x = ux * ddx(ux) + uy * ddy(ux)
    adv_y = ux * ddx(uy) + uy * ddy(uy)
    out = u + dt * (-np.stack([adv_x, adv_y]) + nu * _laplacian(u, dx, bc))
    if bc == "dirichlet":
        out[:, 0, :] = 0.0
        out[:, -1, :] = 0.0
        out[:, :, 0] = 0.0
        out[:, :, -1] = 0.0
    return out.astype(np.float32)


def evolve(field: np.ndarray, pde: str, bc: str, steps: int = 8) -> np.ndarray:
    n = field.shape[-1]
    dx = 2.0 / n
    if pde == "heat":
        alpha = 0.08
        dt = 0.12 * dx ** 2 / alpha
        cur = field.astype(np.float32)
        for _ in range(steps):
            cur = (cur + dt * alpha * _laplacian(cur, dx, bc)).astype(np.float32)
            if bc == "dirichlet":
                cur[:, 0, :] = 0.0
                cur[:, -1, :] = 0.0
                cur[:, :, 0] = 0.0
                cur[:, :, -1] = 0.0
        return cur
    dt = min(0.08 * dx, 0.08 * dx ** 2 / 0.05)
    cur = field.astype(np.float32)
    for _ in range(steps):
        cur = _burgers_step(cur, dx, dt, 0.05, bc)
    return cur


def make_dataset(
    pde: str,
    bc: str,
    n: int,
    samples: int,
    seed: int,
    steps: int = 8,
) -> dict[str, np.ndarray]:
    if pde not in PDE_CHANNELS:
        raise ValueError(f"unsupported pde: {pde}")
    if bc not in {"periodic", "dirichlet"}:
        raise ValueError(f"unsupported bc: {bc}")
    rng = np.random.default_rng(seed)
    inputs = np.stack([_initial_field(pde, n, rng) for _ in range(samples)])
    targets = np.stack([evolve(row, pde, bc, steps=steps) for row in inputs])
    return {"inputs": inputs.astype(np.float32), "targets": targets.astype(np.float32)}


def write_dataset(outdir: Path, pde: str, bc: str, n: int, samples: int, seed: int, steps: int) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    data = make_dataset(pde, bc, n, samples, seed, steps)
    path = outdir / f"{pde}_{bc}_n{n}_s{seed}.npz"
    np.savez_compressed(path, **data, pde=np.array(pde), bc=np.array(bc), n=np.array(n), steps=np.array(steps))
    manifest = {
        "record_type": "fno-fd-dataset-2d",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pde": pde,
        "boundary_condition": bc,
        "grid_n": n,
        "samples": samples,
        "seed": seed,
        "steps": steps,
        "output": str(path.relative_to(ROOT)),
    }
    path.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pde", choices=sorted(PDE_CHANNELS), default="heat")
    parser.add_argument("--bc", choices=["periodic", "dirichlet"], default="periodic")
    parser.add_argument("--n", type=int, default=16)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    path = write_dataset(args.outdir, args.pde, args.bc, args.n, args.samples, args.seed, args.steps)
    print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
