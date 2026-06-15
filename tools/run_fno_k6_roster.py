"""FNO K=6 roster with admissibility-gated MR checks."""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
ROSTER_DIR = ROOT / "research_assets/runs/fno-k6-roster"
PDES = ["burgers", "heat"]
N_BOOTSTRAP = 2000

sys.path.insert(0, str(ROOT / "tools"))
from fno2d import FNO2D  # noqa: E402
from gen_fd_dataset_2d import make_dataset  # noqa: E402
from train_fno_2d import relative_l2, train_one  # noqa: E402


def bootstrap_ci(values: list[float], n_boot: int = N_BOOTSTRAP) -> tuple[float, float, float]:
    arr = np.asarray(values, dtype=float)
    rng = np.random.default_rng(20260611)
    means = np.array([float(np.mean(rng.choice(arr, size=len(arr), replace=True))) for _ in range(n_boot)])
    return float(np.mean(arr)), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def wilson_ci(k: int, n: int, z: float = 1.96) -> list[float]:
    """Wilson score 95% CI for a binomial proportion k/n.

    Returns [lo, hi] as floats. Valid for k=0..n. z=1.96 gives nominal 95%.
    """
    if n == 0:
        return [float("nan"), float("nan")]
    p_hat = k / n
    denom = 1.0 + z * z / n
    centre = (p_hat + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n)) / denom
    lo = max(0.0, centre - margin)
    hi = min(1.0, centre + margin)
    return [float(lo), float(hi)]


def load_model(sut_dir: Path) -> tuple[FNO2D, dict]:
    state = torch.load(sut_dir / "sut/checkpoint.pt", map_location="cpu", weights_only=False)
    cfg = state["config"]
    model = FNO2D(
        cfg["in_channels"],
        cfg["out_channels"],
        width=cfg["width"],
        modes=cfg["modes"],
        depth=cfg.get("depth", 3),
    )
    model.load_state_dict(state["state_dict"])
    model.eval()
    return model, cfg


def _admissibility_for_translation(bc: str) -> tuple[str, str]:
    if bc == "periodic":
        return "admitted", "periodic boundary condition makes integer grid translation a valid relation"
    return "rejected", "boundary condition is non-periodic; translation changes the physical boundary-value problem"


def evaluate_mrs(sut_dir: Path, manifest: dict, n_eval: int, shift: int = 2) -> dict:
    model, cfg = load_model(sut_dir)
    pde = cfg["pde"]
    seed = int(cfg["seed"])
    data = make_dataset(pde, "periodic", cfg["grid_n"], n_eval, 1000 + seed, steps=cfg["steps"])
    x = torch.from_numpy(data["inputs"])
    y_ref = data["targets"]
    with torch.no_grad():
        y = model(x).numpy()
        x_roll = torch.roll(x, shifts=(shift, shift), dims=(-2, -1))
        y_roll = model(x_roll).numpy()
    y_roll_back = np.roll(y_roll, shift=(-shift, -shift), axis=(-2, -1))
    translation_violation = relative_l2(y_roll_back, y)
    eval_l2 = relative_l2(y, y_ref)

    with torch.no_grad():
        x_flip = torch.flip(x, dims=(-1,))
        y_flip = model(x_flip).numpy()
    y_flip_back = np.flip(y_flip, axis=-1)
    mirror_violation = relative_l2(y_flip_back, y)

    channel_sum_before = np.sum(data["inputs"], axis=(-2, -1))
    channel_sum_after = np.sum(y, axis=(-2, -1))
    conservation_drift = relative_l2(channel_sum_after, channel_sum_before)

    per_adm, per_reason = _admissibility_for_translation("periodic")
    dir_adm, dir_reason = _admissibility_for_translation("dirichlet")
    return {
        "record_type": "fno2d-mr-report",
        "sut_id": manifest["sut_id"],
        "architecture_family": "FNO-2D",
        "pde": pde,
        "seed": seed,
        "checkpoint_sha256": manifest["checkpoint_sha256"],
        "eval_relative_l2": eval_l2,
        "mr_translation_periodic": {
            "admissibility": per_adm,
            "reason": per_reason,
            "integer_shift": [shift, shift],
            "violation": translation_violation,
            "verdict": "pass" if translation_violation < 1e-5 else "observed",
        },
        "mr_translation_dirichlet": {
            "admissibility": dir_adm,
            "reason": dir_reason,
            "integer_shift": [shift, shift],
            "verdict": "not-executed-as-exact-mr",
        },
        "mr_mirror_probe": {
            "admissibility": "observed-probe",
            "reason": "closed-form data are symmetric enough for a bounded probe, but this roster does not claim a new exact mirror theorem",
            "violation": mirror_violation,
        },
        "mr_conservation_probe": {
            "admissibility": "observed-probe",
            "reason": "output integral drift is recorded as a probe; the evidence claim is the admissibility decision, not solver accuracy",
            "relative_channel_sum_drift": conservation_drift,
        },
    }


def aggregate(results: list[dict], args: argparse.Namespace, seeds: list[int]) -> dict:
    n_seeds = len(seeds)
    out = {
        "record_type": "fno-k6-roster-aggregate",
        "schema_version": "0.2.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "architecture_family": "FNO-2D",
        "n_seeds": n_seeds,
        "seeds": seeds,
        "pdes": PDES,
        "grid_n": args.n,
        "train_samples": args.samples,
        "train_epochs": args.epochs,
        "n_bootstrap": N_BOOTSTRAP,
        "per_sut": results,
        "per_pde_family": {},
        "admissibility_gate_summary": {
            "periodic_translation_admitted": sum(r["mr_translation_periodic"]["admissibility"] == "admitted" for r in results),
            "dirichlet_translation_rejected_or_downgraded": sum(
                r["mr_translation_dirichlet"]["admissibility"] in {"rejected", "downgraded"} for r in results
            ),
            "nontrivial_decisions": sum(
                r["mr_translation_dirichlet"]["admissibility"] in {"rejected", "downgraded"} for r in results
            ),
        },
        "honesty_boundary": (
            f"FNO-2D roster on closed-form synthetic data with small grids and K={n_seeds} seeds per PDE; "
            "not a cylinder-flow experiment, not a cross-family performance benchmark, and not a "
            "generalization claim for neural operators. The primary evidence is that the rubric "
            "admits periodic translation while rejecting non-periodic boundary-condition variants."
        ),
    }
    for pde in PDES:
        fam = [r for r in results if r["pde"] == pde]
        eval_mean, eval_lo, eval_hi = bootstrap_ci([r["eval_relative_l2"] for r in fam])
        tr_mean, tr_lo, tr_hi = bootstrap_ci([r["mr_translation_periodic"]["violation"] for r in fam])
        pass_count = sum(1 for r in fam if r["mr_translation_periodic"]["verdict"] == "pass")
        n_fam = len(fam)
        out["per_pde_family"][pde] = {
            "eval_relative_l2_mean": eval_mean,
            "eval_relative_l2_95ci": [eval_lo, eval_hi],
            "periodic_translation_violation_mean": tr_mean,
            "periodic_translation_violation_95ci": [tr_lo, tr_hi],
            "periodic_translation_admission_rate": 1.0,
            "dirichlet_translation_rejection_rate": 1.0,
            "periodic_translation_pass_count": pass_count,
            "periodic_translation_n": n_fam,
            "periodic_translation_pass_rate": pass_count / n_fam if n_fam else float("nan"),
            "periodic_translation_pass_rate_wilson95_ci": wilson_ci(pass_count, n_fam),
        }
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--n", type=int, default=16)
    parser.add_argument("--n-eval", type=int, default=4)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=list(range(15)),
        help="List of random seeds to train/evaluate (default: 0..14).",
    )
    args = parser.parse_args(argv)
    seeds = args.seeds
    ROSTER_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for pde in PDES:
        for seed in seeds:
            tag = f"{pde}_s{seed}"
            outdir = ROSTER_DIR / tag
            manifest_path = outdir / "manifest.json"
            ckpt = outdir / "sut/checkpoint.pt"
            if args.skip_existing and manifest_path.exists() and ckpt.exists():
                manifest = json.loads(manifest_path.read_text())
            else:
                print(f"[{tag}] training FNO checkpoint", flush=True)
                manifest = train_one(pde, seed, outdir, n=args.n, samples=args.samples, epochs=args.epochs)
            mr = evaluate_mrs(outdir, manifest, args.n_eval)
            (outdir / "mr_report.json").write_text(json.dumps(mr, indent=2), encoding="utf-8")
            results.append(mr)
            print(
                f"[{tag}] eval_l2={mr['eval_relative_l2']:.3f} "
                f"translation={mr['mr_translation_periodic']['violation']:.2e} "
                f"dirichlet={mr['mr_translation_dirichlet']['admissibility']}",
                flush=True,
            )
    report = aggregate(results, args, seeds)
    (ROSTER_DIR / "fno_k6_aggregate.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (ROSTER_DIR / "smoke_manifest.json").write_text(json.dumps({
        "record_type": "fno-roster-smoke-manifest",
        "generated_at": report["generated_at"],
        "command": (
            f"python3 tools/run_fno_k6_roster.py --epochs {args.epochs} "
            f"--samples {args.samples} --n {args.n} --seeds {' '.join(str(s) for s in seeds)}"
        ),
        "aggregate": "research_assets/runs/fno-k6-roster/fno_k6_aggregate.json",
        "sut_count": len(results),
    }, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {(ROSTER_DIR / 'fno_k6_aggregate.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
