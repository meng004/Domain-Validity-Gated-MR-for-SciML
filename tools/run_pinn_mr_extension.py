"""P2-1: apply the paper's three MRs (rewritten for the PINN family) + the
rollout-accuracy baseline to the trained 2D viscous Burgers PINN.

MR rewrites (parallel to Section 5.3 / 5.4):
  MR-A  Sampling-point permutation equivariance
        For any permutation P of N collocation points,
        ||model(P x)[P^-1] - model(x)||_2 / ||model(x)||_2 < 1e-5.
        (Trivially admissible for a pointwise MLP.)

  MR-B  Mirror-y equivariance
        R: (x, y, t, u_x, u_y) -> (x, -y, t, u_x, -u_y).
        The PINN should satisfy R(model(R x)) = model(x). The verdict
        compares the relative L2 of the violation against the trained PINN's
        PDE residual L2 (the operator floor the verdict tolerance must
        dominate, per the paper's admissibility predicate).

  MR-C  Mass-conservation ratio
        Q(t) = integral u_x dA over the domain. Compared to the FD reference
        snapshot-by-snapshot via Q_pred(t) / Q_ref(t). Verdict gate at 1.5
        (mirroring the cylinder-flow continuity gate in Section 5.5).

  Rollout-accuracy: median relative L2 of (u_x, u_y) prediction vs the FD
  reference over the K snapshot times t in {0, 0.1, 0.2, 0.3, 0.4, 0.5}.

Outputs research_assets/runs/pinn-cross-family/pinn_mr_report.json.
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
SUT_DIR = ROOT / "research_assets/runs/pinn-cross-family"
CKPT = SUT_DIR / "sut/checkpoint.pt"
MANIFEST = SUT_DIR / "checkpoint_manifest.json"
REF = SUT_DIR / "reference_solution.npz"
REPORT = SUT_DIR / "pinn_mr_report.json"

sys.path.insert(0, str(ROOT / "tools"))
from train_pinn_burgers2d import PINN  # noqa: E402


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(b)) + 1e-12
    return float(np.linalg.norm(a - b) / denom)


def load_model() -> tuple[PINN, dict, dict]:
    state = torch.load(CKPT, map_location="cpu", weights_only=False)
    cfg = state["config"]
    model = PINN(hidden=cfg["hidden"], layers=cfg["layers"])
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

    # ---- MR-A: permutation equivariance over a random uniform eval set ----
    xyt = rng.uniform([-1, -1, 0.0], [1, 1, 0.5],
                      (args.n_eval, 3)).astype(np.float32)
    with torch.no_grad():
        u_pred = model(torch.from_numpy(xyt)).numpy()
    perm = rng.permutation(args.n_eval)
    inv = np.empty_like(perm); inv[perm] = np.arange(args.n_eval)
    with torch.no_grad():
        u_perm = model(torch.from_numpy(xyt[perm])).numpy()
    mr_a_violation = relative_l2(u_perm[inv], u_pred)
    if mr_a_violation < 1e-5:
        mr_a_verdict = "pass"
    elif mr_a_violation > 1e-3:
        mr_a_verdict = "fail"
    else:
        mr_a_verdict = "borderline"

    # ---- MR-B: mirror-y equivariance on the same evaluation set ----
    xyt_R = xyt.copy(); xyt_R[:, 1] = -xyt_R[:, 1]
    with torch.no_grad():
        u_pred_R = model(torch.from_numpy(xyt_R)).numpy()
    # R applied to output: u_x unchanged, u_y negated.
    u_via_R = np.column_stack([u_pred_R[:, 0], -u_pred_R[:, 1]])
    mr_b_violation = relative_l2(u_via_R, u_pred)
    mr_b_ratio = mr_b_violation / (floor + 1e-12)
    mr_b_verdict = "pass" if mr_b_ratio < 1.0 else "fail"

    # ---- MR-C: conservation ratio at each snapshot time vs the FD reference ----
    x = ref["x"]; y = ref["y"]; times = ref["snapshots_times"]
    X, Y = np.meshgrid(x, y, indexing="ij")
    dx = float(x[1] - x[0]); dy = float(y[1] - y[0])
    dA = dx * dy
    ratios_ux = []
    rollout_l2 = []
    per_snap = []
    for k, t_eval in enumerate(times):
        t_eval = float(t_eval)
        xyt_g = np.column_stack(
            [X.ravel(), Y.ravel(), np.full(X.size, t_eval)]).astype(np.float32)
        with torch.no_grad():
            u_g = model(torch.from_numpy(xyt_g)).numpy()
        ux_p = u_g[:, 0].reshape(X.shape)
        uy_p = u_g[:, 1].reshape(X.shape)
        ux_r = ref["u_snapshots"][k]
        uy_r = ref["v_snapshots"][k]
        Q_pred = float(np.sum(ux_p) * dA)
        Q_ref = float(np.sum(ux_r) * dA)
        ratio = Q_pred / Q_ref if abs(Q_ref) > 1e-6 else float("nan")
        rl2 = relative_l2(np.stack([ux_p, uy_p]), np.stack([ux_r, uy_r]))
        ratios_ux.append(ratio)
        rollout_l2.append(rl2)
        per_snap.append({"t": t_eval, "Q_pred": Q_pred, "Q_ref": Q_ref,
                         "ratio_ux": ratio, "rollout_rel_l2": rl2})

    ratios_nonzero = [r for r in ratios_ux if np.isfinite(r)]
    mr_c_ratio_median = float(np.median(ratios_nonzero)) if ratios_nonzero else float("nan")
    mr_c_verdict = ("pass" if 0.667 <= mr_c_ratio_median <= 1.5 else "fail") \
        if np.isfinite(mr_c_ratio_median) else "inconclusive"
    rollout_median = float(np.median(rollout_l2))

    report = {
        "record_type": "cross-family-pinn-extension",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sut": {
            "id": "pinn_burgers2d_v1", "model_type": "PINN",
            "pde_id": "burgers2d_viscous", "spatial_dim": 2, "output_dim": 2,
            "has_mirror_symmetry": True,
            "conservation_quantity": "integral of u_x over domain (Dirichlet zero BC)",
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
            "violation": mr_a_violation,
            "tolerance": 1e-5,
            "verdict": mr_a_verdict,
        },
        "mr_B_symmetry_equivariance": {
            "violation": mr_b_violation,
            "floor": floor,
            "ratio": mr_b_ratio,
            "verdict": mr_b_verdict,
        },
        "mr_C_conservation": {
            "ratios_ux_per_snapshot": ratios_ux,
            "median_ratio_ux": mr_c_ratio_median,
            "verdict": mr_c_verdict,
        },
        "rollout_accuracy_baseline": {
            "relative_l2_per_snapshot": rollout_l2,
            "median_relative_l2": rollout_median,
            "note": ("median relative L2 of PINN (u_x, u_y) vs FD reference over "
                     "snapshot times {0, 0.1, 0.2, 0.3, 0.4, 0.5}; the rollout-"
                     "accuracy comparator from Section 5.3"),
        },
        "per_snapshot_raw": per_snap,
        "honesty_boundary": (
            "One PINN (5x50 MLP, seed 20260607), one PDE (2D viscous Burgers, "
            "nu=0.05), one evaluation set, one set of thresholds chosen from "
            "the trained PINN's PDE residual floor. Not a generalization across "
            "PINN architectures, PDEs, or training regimes."
        ),
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {REPORT}")
    print(f"  MR-A violation = {mr_a_violation:.3e}  verdict = {mr_a_verdict}")
    print(f"  MR-B violation = {mr_b_violation:.3e}  floor = {floor:.3e}  "
          f"ratio = {mr_b_ratio:.3f}  verdict = {mr_b_verdict}")
    print(f"  MR-C median_ratio_ux = {mr_c_ratio_median:.3f}  "
          f"verdict = {mr_c_verdict}")
    print(f"  rollout median rel L2 = {rollout_median:.3e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
