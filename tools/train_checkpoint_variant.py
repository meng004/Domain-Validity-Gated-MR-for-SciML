"""Train one MeshGraphNet checkpoint variant for the multi-checkpoint roster (E1).

Thin, auditable wrapper around the *read-only* upstream trainer
``mcmr.cylinder_flow.train_stage_a`` (in the Minimum-MR-SubSet repository). It
reuses the upstream ``train`` / ``save_checkpoint`` / ``inference_smoke``
functions verbatim so the produced checkpoints are byte-compatible with the
checkpoints the existing MR runners consume.

Read-only discipline: this wrapper only *reads* the committed training/eval
``.npz`` from the SUT repository and *writes* exclusively under this
repository's ``research_assets/runs/multicheckpoint/``. It never writes into
the SUT repository.

Training is seed-fixed (``torch.manual_seed`` + ``np.random.seed`` +
``np.random.default_rng(seed)``), so re-running with the same seed/config on the
same CPU torch build reproduces the same checkpoint (same sha256). The roster is
therefore regeneratable from this script rather than relying on committed
binaries.

Roster:
  S0  seed=0 hidden=64  num_layers=4  (base; reuses the pilot checkpoint)
  S1  seed=1 hidden=64  num_layers=4  (training-seed replica)
  S2  seed=2 hidden=64  num_layers=4  (training-seed replica)
  S3  seed=3 hidden=64  num_layers=4  (training-seed replica)
  S4  seed=0 hidden=128 num_layers=4  (capacity/configuration variant)
  S5  seed=0 hidden=64  num_layers=6  (depth/configuration variant)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

SUT_REPO = Path("/home/user/Minimum-MR-SubSet")
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = SUT_REPO / "data" / "raw" / "cylinder_flow_deepmind"
TRAIN_NPZ = DATA_DIR / "cylinder_flow_train.npz"
EVAL_NPZ = DATA_DIR / "cylinder_flow_eval.npz"

sys.path.insert(0, str(SUT_REPO / "scripts"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(Path(path).read_bytes())
    return h.hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--sut-id", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--hidden", type=int, default=64)
    p.add_argument("--num-layers", type=int, default=4)
    p.add_argument("--steps", type=int, default=1500)
    p.add_argument("--t-eval", type=int, default=0)
    args = p.parse_args(argv)

    from mcmr.cylinder_flow import dm_dataset as ds  # noqa: PLC0415
    from mcmr.cylinder_flow import train_stage_a as T  # noqa: PLC0415

    if not TRAIN_NPZ.exists():
        raise SystemExit(f"BLOCKED_EXTERNAL_DATA: missing {TRAIN_NPZ}; no checkpoint fabricated.")

    traj = ds.load_npz(TRAIN_NPZ)
    eval_traj = ds.load_npz(EVAL_NPZ)
    with np.load(EVAL_NPZ) as z:
        eval_orig_frames = z["orig_frames"] if "orig_frames" in z else None

    trained = T.train(traj, steps=args.steps, hidden=args.hidden,
                      num_layers=args.num_layers, seed=args.seed)

    out_sut = ROOT / "research_assets" / "runs" / "multicheckpoint" / args.sut_id / "sut"
    out_sut.mkdir(parents=True, exist_ok=True)
    ckpt = out_sut / "checkpoint.pt"
    T.save_checkpoint(ckpt, trained)
    smoke = T.inference_smoke(trained, eval_traj, t_eval=args.t_eval,
                             orig_frames=eval_orig_frames)

    manifest = {
        "record_type": "multicheckpoint-training",
        "sut_id": args.sut_id,
        "generated_at": _utc(),
        "checkpoint": str(ckpt.relative_to(ROOT)),
        "checkpoint_sha256": _sha256(ckpt),
        "config": trained["config"],
        "num_parameters": int(sum(p_.numel() for p_ in trained["model"].parameters())),
        "loss_first": trained["loss_first"],
        "loss_last": trained["loss_last"],
        "inference_smoke": smoke,
        "data_provenance": {
            "train_npz": str(TRAIN_NPZ), "train_npz_sha256": _sha256(TRAIN_NPZ),
            "eval_npz": str(EVAL_NPZ), "eval_npz_sha256": _sha256(EVAL_NPZ),
            "source": f"{ds.GCS_BASE}/train.tfrecord (committed compact npz slice)",
        },
        "sut_repo": str(SUT_REPO),
        "honesty_boundary": (
            "Within-architecture-family roster. S0-S3 are training-seed replicas of "
            "one base config; only S4/S5 vary architecture. Not a cross-family study."
        ),
    }
    (out_sut.parent / "checkpoint_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[{args.sut_id}] {ckpt.relative_to(ROOT)} sha={manifest['checkpoint_sha256'][:12]} "
          f"params={manifest['num_parameters']} loss {trained['loss_first']:.4f}->"
          f"{trained['loss_last']:.4f} smoke_rel_rmse={smoke['relative_rmse']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
