"""Train one tiny PyTorch FNO-2D checkpoint on generated FD data."""
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
sys.path.insert(0, str(ROOT / "tools"))
from fno2d import FNO2D, parameter_count  # noqa: E402
from gen_fd_dataset_2d import PDE_CHANNELS, make_dataset, write_dataset  # noqa: E402


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + 1e-12))


def train_one(
    pde: str,
    seed: int,
    outdir: Path,
    *,
    bc: str = "periodic",
    n: int = 16,
    samples: int = 12,
    epochs: int = 6,
    width: int = 8,
    modes: int = 6,
    steps: int = 8,
) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)
    outdir.mkdir(parents=True, exist_ok=True)
    sut_dir = outdir / "sut"
    sut_dir.mkdir(parents=True, exist_ok=True)
    data = make_dataset(pde, bc, n, samples, seed, steps=steps)
    dataset_path = write_dataset(outdir / "data", pde, bc, n, samples, seed, steps)
    x = torch.from_numpy(data["inputs"])
    y = torch.from_numpy(data["targets"])
    channels = PDE_CHANNELS[pde]
    model = FNO2D(channels, channels, width=width, modes=modes, depth=3)
    opt = torch.optim.Adam(model.parameters(), lr=8e-3)
    t0 = time.time()
    losses: list[float] = []
    for _ in range(epochs):
        opt.zero_grad()
        pred = model(x)
        loss = torch.mean((pred - y) ** 2)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
    elapsed = time.time() - t0
    with torch.no_grad():
        pred_np = model(x).numpy()
    ckpt_path = sut_dir / "checkpoint.pt"
    config = {
        "pde": pde,
        "boundary_condition": bc,
        "seed": seed,
        "grid_n": n,
        "samples": samples,
        "epochs": epochs,
        "width": width,
        "modes": modes,
        "depth": 3,
        "steps": steps,
        "in_channels": channels,
        "out_channels": channels,
    }
    torch.save({"state_dict": model.state_dict(), "config": config}, ckpt_path)
    sha = hashlib.sha256(ckpt_path.read_bytes()).hexdigest()
    manifest = {
        "record_type": "fno2d-checkpoint-manifest",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sut_id": f"fno_{pde}_s{seed}",
        "architecture_family": "FNO-2D",
        "pde": pde,
        "seed": seed,
        "checkpoint_sha256": sha,
        "num_parameters": parameter_count(model),
        "train_loss_final": losses[-1],
        "train_loss_initial": losses[0],
        "train_relative_l2": relative_l2(pred_np, data["targets"]),
        "elapsed_s": elapsed,
        "dataset": str(dataset_path.relative_to(ROOT)),
        **config,
    }
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pde", choices=sorted(PDE_CHANNELS), default="heat")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--bc", choices=["periodic", "dirichlet"], default="periodic")
    parser.add_argument("--n", type=int, default=16)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--epochs", type=int, default=6)
    args = parser.parse_args(argv)
    manifest = train_one(args.pde, args.seed, args.outdir, bc=args.bc, n=args.n, samples=args.samples, epochs=args.epochs)
    print(json.dumps({"sut_id": manifest["sut_id"], "train_relative_l2": manifest["train_relative_l2"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
