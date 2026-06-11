"""P2-1 fallback: apply the three MRs + rollout-accuracy baseline to the
2D Diffusion (heat-equation) PINN.

Parallel to tools/run_pinn_mr_extension.py (the Burgers analogue); the scalar
field requires a slightly different mirror-y rewrite and a single-channel
conservation integral, otherwise the same thresholds and procedure.

MR rewrites for the heat-equation PINN:
  MR-A  Permutation equivariance for the pointwise MLP (trivially admissible,
        verdict tolerance 1e-5).
  MR-B  Mirror-y equivariance R: (x, y, t, u) -> (x, -y, t, u). Verdict
        compares relative-L2 violation against the trained PINN's PDE residual
        L2 as the operator floor.
  MR-C  Strict mass conservation. The FD reference conserves integral u dA
        exactly via the edge-pad ghost cell scheme, so the per-snapshot ratio
        Q_pred(t) / Q_ref(t) directly bounds the PINN's mass error. Verdict
        gate at 1.5x (the same conservation gate as Section 5.5).

Outputs research_assets/runs/pinn-cross-family-diffusion/pinn_mr_report.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SUT_DIR = ROOT / "research_assets/runs/pinn-cross-family-diffusion"
CKPT = SUT_DIR / "sut/checkpoint.pt"
MANIFEST = SUT_DIR / "checkpoint_manifest.json"
REF = SUT_DIR / "reference_solution.npz"
REPORT = SUT_DIR / "pinn_mr_report.json"

sys.path.insert(0, str(ROOT / "tools"))
from train_pinn_diffusion2d import PINNScalar  # noqa: E402


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + 1e-12))


def load_model() -> tuple[PINNScalar, dict, dict]:
    state = torch.load(CKPT, map_location="cpu", weights_only=False)
    cfg = state["config"]
    model = PINNScalar(hidden=cfg["hidden"], layers=cfg["layers"])
    model.load_state_dict(state["state_dict"])
    model.eval()
    manifest = json.loads(MANIFEST.read_text())
    return model, cfg, manifest


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n-eval", type=int, default=5000)
    p.add_argument("--seed", type=int, default=20260607)
    args = p.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    model, cfg, manifest = load_model()
    ref = np.load(REF)
    floor = float(manifest["final_pde_residual_l2"])

    # ---- MR-A: permutation equivariance ----
    xyt = rng.uniform([-1, -1, 0.0], [1, 1, 0.5],
                      (args.n_eval, 3)).astype(np.float32)
    with torch.no_grad():
        u_pred = model(torch.from_numpy(xyt)).numpy().squeeze(-1)
    perm = rng.permutation(args.n_eval)
    inv = np.empty_like(perm); inv[perm] = np.arange(args.n_eval)
    with torch.no_grad():
        u_perm = model(torch.from_numpy(xyt[perm])).numpy().squeeze(-1)
    mr_a_violation = relative_l2(u_perm[inv], u_pred)
    if mr_a_violation < 1e-5:
        mr_a_verdict = "pass"
    elif mr_a_violation > 1e-3:
        mr_a_verdict = "fail"
    else:
        mr_a_verdict = "borderline"

    # ---- MR-B: mirror-y equivariance (scalar invariant) ----
    xyt_R = xyt.copy(); xyt_R[:, 1] = -xyt_R[:, 1]
    with torch.no_grad():
        u_pred_R = model(torch.from_numpy(xyt_R)).numpy().squeeze(-1)
    # For a scalar field u, R applied to output is identity: R(u) = u.
    mr_b_violation = relative_l2(u_pred_R, u_pred)
    mr_b_ratio = mr_b_violation / (floor + 1e-12)
    mr_b_verdict = "pass" if mr_b_ratio < 1.0 else "fail"

    # ---- MR-C: mass conservation ratio vs FD reference ----
    x = ref["x"]; y = ref["y"]; times = ref["snapshots_times"]
    X, Y = np.meshgrid(x, y, indexing="ij")
    dx = float(x[1] - x[0]); dA = dx * dx
    ratios = []
    rollout_l2 = []
    per_snap = []
    for k, t_eval in enumerate(times):
        t_eval = float(t_eval)
        xyt_g = np.column_stack(
            [X.ravel(), Y.ravel(), np.full(X.size, t_eval)]).astype(np.float32)
        with torch.no_grad():
            u_g = model(torch.from_numpy(xyt_g)).numpy().squeeze(-1).reshape(X.shape)
        u_ref = ref["u_snapshots"][k]
        Q_pred = float(np.sum(u_g) * dA)
        Q_ref = float(np.sum(u_ref) * dA)
        ratio = Q_pred / Q_ref if abs(Q_ref) > 1e-6 else float("nan")
        rl2 = relative_l2(u_g, u_ref)
        ratios.append(ratio); rollout_l2.append(rl2)
        per_snap.append({"t": t_eval, "Q_pred": Q_pred, "Q_ref": Q_ref,
                         "ratio": ratio, "rollout_rel_l2": rl2})

    finite = [r for r in ratios if np.isfinite(r)]
    mr_c_ratio_median = float(np.median(finite)) if finite else float("nan")
    mr_c_verdict = ("pass" if 0.667 <= mr_c_ratio_median <= 1.5
                    else "fail") if np.isfinite(mr_c_ratio_median) else "inconclusive"
    rollout_median = float(np.median(rollout_l2))

    report = {
        "record_type": "cross-family-pinn-extension",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sut": {
            "id": "pinn_diffusion2d_v1", "model_type": "PINN",
            "pde_id": "heat2d", "spatial_dim": 2, "output_dim": 1,
            "has_mirror_symmetry": True,
            "conservation_quantity": "integral of u over domain (Neumann zero-flux)",
            "checkpoint_sha256": manifest["checkpoint_sha256"],
            "training_provenance": (
                f"trained {manifest['generated_at']} with Adam+StepLR, "
                f"{cfg['iters']} iter, final PDE residual L2 = {floor:.4e}"
            ),
            "num_parameters": manifest["num_parameters"],
        },
        "evaluation_set": {
            "n_points": args.n_eval,
            "sampling": "uniform on [-1,1]^2 x [0, 0.5]",
            "rng_seed": args.seed,
        },
        "mr_A_permutation_equivariance": {
            "violation": mr_a_violation, "tolerance": 1e-5,
            "verdict": mr_a_verdict,
        },
        "mr_B_symmetry_equivariance": {
            "violation": mr_b_violation, "floor": floor,
            "ratio": mr_b_ratio, "verdict": mr_b_verdict,
        },
        "mr_C_conservation": {
            "ratios_per_snapshot": ratios,
            "median_ratio": mr_c_ratio_median,
            "verdict": mr_c_verdict,
        },
        "rollout_accuracy_baseline": {
            "relative_l2_per_snapshot": rollout_l2,
            "median_relative_l2": rollout_median,
            "note": ("median relative L2 of PINN scalar field vs FD reference "
                     "over snapshot times {0, 0.1, 0.2, 0.3, 0.4, 0.5}"),
        },
        "per_snapshot_raw": per_snap,
        "honesty_boundary": (
            "One PINN (5x50 MLP scalar, seed 20260607), one PDE (2D heat "
            "equation, alpha=0.1, Neumann zero-flux), one evaluation set, one "
            "set of thresholds chosen from the trained PINN's PDE residual "
            "floor. Not a generalization across PINN architectures or PDEs."
        ),
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {REPORT}")
    print(f"  MR-A violation = {mr_a_violation:.3e}  verdict = {mr_a_verdict}")
    print(f"  MR-B violation = {mr_b_violation:.3e}  floor = {floor:.3e}  "
          f"ratio = {mr_b_ratio:.3f}  verdict = {mr_b_verdict}")
    print(f"  MR-C median_ratio = {mr_c_ratio_median:.4f}  "
          f"verdict = {mr_c_verdict}")
    print(f"  rollout median rel L2 = {rollout_median:.3e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
