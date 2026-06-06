"""Train a MeshGraphNets cylinder-flow config variant (capacity/depth) for the
multi-checkpoint robustness study (E1).

The read-only Minimum-MR-SubSet trainer exposes hidden/num_layers as train() kwargs but
not on its CLI. This thin wrapper imports the read-only train()/save_checkpoint() and
trains a variant, writing the checkpoint and a provenance manifest INTO THIS repo (never
into the read-only repo). It is byte-compatible with the existing checkpoint format
(state_dict, config, vel_norm, delta_norm, edge_norm), so all MR runners load it unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SUT_REPO = Path("/home/user/Minimum-MR-SubSet")


def _sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--hidden", type=int, default=64)
    ap.add_argument("--num-layers", type=int, default=4)
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    sys.path.insert(0, str(SUT_REPO / "scripts"))
    from mcmr.cylinder_flow.train_stage_a import (  # noqa: PLC0415
        acquire_trajectory, train, save_checkpoint,
    )

    traj, data_manifest = acquire_trajectory(SUT_REPO)
    trained = train(traj, steps=args.steps, seed=args.seed,
                    hidden=args.hidden, num_layers=args.num_layers)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ckpt = outdir / "checkpoint.pt"
    save_checkpoint(ckpt, trained)

    manifest = {
        "checkpoint": str(ckpt),
        "checkpoint_sha256": _sha256(ckpt),
        "config": trained["config"],
        "loss_first": trained.get("loss_first"),
        "loss_last": trained.get("loss_last"),
        "num_parameters": int(sum(p.numel() for p in trained["model"].parameters())),
        "train_command": f"train_config_variant --hidden {args.hidden} "
                         f"--num-layers {args.num_layers} --steps {args.steps} --seed {args.seed}",
        "sut_repo": str(SUT_REPO),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "config variant for E1 multi-checkpoint robustness; same arch family + dataset.",
    }
    (outdir / "checkpoint_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {ckpt} sha256={manifest['checkpoint_sha256'][:16]}... "
          f"hidden={args.hidden} layers={args.num_layers} params={manifest['num_parameters']} "
          f"loss {manifest['loss_first']}->{manifest['loss_last']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
