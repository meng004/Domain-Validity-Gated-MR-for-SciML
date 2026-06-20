"""EXT (path B): end-to-end seeded-fault detection on the Burgers PINN roster.

Completes path B by reproducing the MeshGraphNets by-class seeded-fault
structure on a fourth, pointwise architecture (physics-informed MLP), using the
already-converged K=6 Burgers PINN roster (research_assets/runs/pinn-k6-roster/
burgers_s0..s5, sharing the committed Burgers FD reference grid).

Detectors = the PINN's two non-trivial admitted MRs (MR-A permutation
equivariance is vacuous for a pointwise MLP and is not a fault detector):
  - MR-B mirror-y equivariance: the velocity field must have u_x even and u_y
    odd in y. A fault is DETECTED when it multiplies the clean mirror-y
    violation by more than a predeclared factor (ratio form, robust to the
    PINN's imperfect clean equivariance).
  - MR-C mass conservation: the conserved quantity is Q(t) = integral of u_x
    over the domain. A fault is DETECTED when it changes Q, relative to the
    clean model, by more than a predeclared tolerance (median over snapshots).

Faults are output-level corruptions of the predicted (u_x, u_y) field, chosen
so the detection is by-class with a genuine blind region -- NOT rigged:
  - scale_ux (u_x x(1+eps)): rescales Q (MR-C detects); the mirror-y violation
    ratio is scale-invariant (MR-B blind).
  - asym_y_ux (u_x += d*rms*y, odd in y): breaks u_x evenness (MR-B detects);
    integrates to zero over the symmetric domain, so Q is unchanged (MR-C blind).
  - upper_half_offset (u_x += d*rms*1[y>0]): breaks evenness AND shifts Q ->
    detected by BOTH.
  - cos_x_blind (u_x += a*rms*cos(pi x)): independent of y (keeps u_x even, so
    mirror-y holds) and integrates to zero in x (keeps Q), yet degrades the
    field -> a genuine blind subspace, the PINN analogue of the MeshGraphNets
    knife-edge blind region.

Honesty boundary: K=6 Burgers PINN checkpoints, one shared FD reference grid,
one author-designed output-level fault catalogue. Bounded by-class detection on
a fourth (pointwise) architecture; NOT a real-world fault-detection rate, NOT a
reliability, baseline-superiority, or cross-architecture generalization claim.
"""
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
ROSTER_DIR = ROOT / "research_assets/runs/pinn-k6-roster"
BURGERS_REF = ROOT / "research_assets/runs/pinn-cross-family/reference_solution.npz"
OUT_DIR = ROOT / "research_assets/runs/pinn-seeded-fault-detection"
SEEDS = [0, 1, 2, 3, 4, 5]

# Predeclared detector thresholds.
MR_B_FACTOR = 3.0     # faulted mirror-y violation / clean > this = detected
MR_C_TOL = 0.10       # median relative change in conserved Q > this = detected

# Fault severities (fraction of the u_x RMS, scale-robust).
EPS_SCALE = 0.15
DELTA_BIAS = 0.30
ALPHA_BLIND = 0.30
BLIND_SWEEP = [0.15, 0.30, 0.60, 1.0]
EVAL_SEED = 20260620
N_EVAL = 5000

sys.path.insert(0, str(ROOT / "tools"))
from train_pinn_burgers2d import PINN  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + 1e-12))


def wilson_ci(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return [max(0.0, center - half), min(1.0, center + half)]


def load_pinn(seed: int) -> PINN:
    ckpt = ROSTER_DIR / f"burgers_s{seed}" / "sut" / "checkpoint.pt"
    if not ckpt.exists():
        raise FileNotFoundError(f"missing PINN checkpoint {ckpt}; run run_pinn_k6_roster.py")
    state = torch.load(ckpt, map_location="cpu", weights_only=False)
    cfg = state["config"]
    model = PINN(hidden=cfg["hidden"], layers=cfg["layers"])
    model.load_state_dict(state["state_dict"])
    model.eval()
    return model


def predict(model: PINN, xyt: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        return model(torch.from_numpy(xyt.astype(np.float32))).numpy()


FAULTS = {
    "scale_ux": "conservation",
    "asym_y_ux": "mirror",
    "upper_half_offset": "both",
    "cos_x_blind": "shape-preserving (blind)",
}


def apply_fault(u: np.ndarray, coords: np.ndarray, fault: str,
                severity: float | None = None) -> np.ndarray:
    """Apply an output-level fault to the predicted (u_x, u_y) field. ``u`` is
    (N, 2); ``coords`` is (N, 3) = (x, y, t)."""
    x, y = coords[:, 0], coords[:, 1]
    rms = float(np.sqrt(np.mean(u[:, 0] ** 2))) + 1e-30
    uf = u.copy()
    if fault == "scale_ux":
        uf[:, 0] = u[:, 0] * (1.0 + EPS_SCALE)
    elif fault == "asym_y_ux":
        uf[:, 0] = u[:, 0] + DELTA_BIAS * rms * y          # odd in y -> zero integral
    elif fault == "upper_half_offset":
        uf[:, 0] = u[:, 0] + DELTA_BIAS * rms * (y > 0.0)  # asymmetric + nonzero integral
    elif fault == "cos_x_blind":
        a = ALPHA_BLIND if severity is None else severity
        uf[:, 0] = u[:, 0] + a * rms * np.cos(np.pi * x)   # even in y, zero x-integral
    else:
        raise ValueError(f"unknown fault {fault}")
    return uf


def mr_b_violation(model: PINN, xyt: np.ndarray, fault: str | None,
                   severity: float | None = None) -> float:
    """Mirror-y violation of the (possibly faulted) model on eval set xyt."""
    u = predict(model, xyt)
    xyt_R = xyt.copy(); xyt_R[:, 1] = -xyt_R[:, 1]
    uR = predict(model, xyt_R)
    if fault is not None:
        u = apply_fault(u, xyt, fault, severity)
        uR = apply_fault(uR, xyt_R, fault, severity)
    u_via_R = np.column_stack([uR[:, 0], -uR[:, 1]])
    return relative_l2(u_via_R, u)


def conserved_q(model: PINN, grid_xyt: list[np.ndarray], dA: float,
                fault: str | None, severity: float | None = None) -> np.ndarray:
    """Per-snapshot conserved quantity Q(t) = integral u_x dA for the (faulted) model."""
    qs = []
    for xyt_g in grid_xyt:
        u = predict(model, xyt_g)
        if fault is not None:
            u = apply_fault(u, xyt_g, fault, severity)
        qs.append(float(np.sum(u[:, 0]) * dA))
    return np.array(qs)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(OUT_DIR))
    args = ap.parse_args(argv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(EVAL_SEED)
    xyt = rng.uniform([-1, -1, 0.0], [1, 1, 0.5], (N_EVAL, 3)).astype(np.float32)

    ref = np.load(BURGERS_REF)
    gx, gy, times = ref["x"], ref["y"], ref["snapshots_times"]
    X, Y = np.meshgrid(gx, gy, indexing="ij")
    dA = float(gx[1] - gx[0]) * float(gy[1] - gy[0])
    grid_xyt = [np.column_stack([X.ravel(), Y.ravel(),
                                 np.full(X.size, float(t))]).astype(np.float32)
                for t in times]

    per_sut = []
    for seed in SEEDS:
        model = load_pinn(seed)
        base_b = mr_b_violation(model, xyt, None)
        base_q = conserved_q(model, grid_xyt, dA, None)

        dets = {}
        for fault in FAULTS:
            f_b = mr_b_violation(model, xyt, fault)
            f_q = conserved_q(model, grid_xyt, dA, fault)
            b_ratio = f_b / (base_b + 1e-30)
            q_change = float(np.median(np.abs(f_q / (base_q + 1e-30) - 1.0)))
            det_b = bool(b_ratio > MR_B_FACTOR)
            det_c = bool(q_change > MR_C_TOL)
            dets[fault] = {
                "mirror_violation_ratio": b_ratio,
                "conservation_q_change": q_change,
                "detected_by_mirror": det_b,
                "detected_by_conservation": det_c,
                "detected": bool(det_b or det_c),
            }
        sweep = []
        for sev in BLIND_SWEEP:
            f_b = mr_b_violation(model, xyt, "cos_x_blind", sev)
            f_q = conserved_q(model, grid_xyt, dA, "cos_x_blind", sev)
            u0 = predict(model, xyt)
            perturb = relative_l2(apply_fault(u0, xyt, "cos_x_blind", sev), u0)
            sweep.append({
                "severity": sev, "output_perturbation_rel_l2": perturb,
                "mirror_violation_ratio": f_b / (base_b + 1e-30),
                "conservation_q_change": float(np.median(np.abs(f_q / (base_q + 1e-30) - 1.0))),
                "detected": bool(f_b / (base_b + 1e-30) > MR_B_FACTOR
                                 or float(np.median(np.abs(f_q / (base_q + 1e-30) - 1.0))) > MR_C_TOL),
            })
        per_sut.append({"sut_id": f"burgers_s{seed}", "seed": seed,
                        "baseline_mirror_violation": base_b,
                        "detections": dets, "blind_severity_sweep": sweep})
        print(f"[burgers_s{seed}] base mirror-violation={base_b:.3e}", flush=True)

    per_fault = {}
    for fault, cls in FAULTS.items():
        ds = [s["detections"][fault] for s in per_sut]
        n = len(ds)
        k_any = sum(d["detected"] for d in ds)
        k_b = sum(d["detected_by_mirror"] for d in ds)
        k_c = sum(d["detected_by_conservation"] for d in ds)
        per_fault[fault] = {
            "fault_class": cls, "n_suts": n,
            "detected_any": k_any, "detection_rate": k_any / n if n else 0.0,
            "detection_rate_wilson95": wilson_ci(k_any, n),
            "detected_by_mirror": k_b, "detected_by_conservation": k_c,
            "by_class_localization": (
                "mirror" if k_b and not k_c else
                "conservation" if k_c and not k_b else
                "both" if k_b and k_c else "none"),
        }
    detected_faults = sum(1 for f in FAULTS if per_fault[f]["detection_rate"] >= 0.5)
    blind = per_fault["cos_x_blind"]
    blind_sweep_detect = any(sw["detected"] for s in per_sut for sw in s["blind_severity_sweep"])

    report = {
        "record_type": "pinn-seeded-fault-detection",
        "schema_version": "0.1.0",
        "generated_at": _utc_now(),
        "architecture_family": "PINN (pointwise physics-informed MLP)",
        "pde": "burgers2d_viscous", "seeds": SEEDS,
        "trained_sut_count": len(per_sut),
        "detectors": {
            "mr_B_mirror_y": f"faulted mirror-y violation / clean > {MR_B_FACTOR}",
            "mr_C_conservation": f"median relative change in integral(u_x) > {MR_C_TOL}",
        },
        "fault_catalogue": FAULTS,
        "per_fault": per_fault,
        "union_detection": {
            "faults_detected_majority": detected_faults,
            "faults_total": len(FAULTS),
            "summary": f"{detected_faults}/{len(FAULTS)} faults detected by >=1 MR (>=50% of SUTs)",
        },
        "blind_spot": {
            "fault": "cos_x_blind",
            "by_class_localization": blind["by_class_localization"],
            "detected_across_severity_sweep": blind_sweep_detect,
            "interpretation": (
                "A y-independent, x-zero-integral perturbation (cos(pi x) added to "
                "u_x) keeps u_x even in y (mirror-y holds) and preserves the "
                "conserved integral, yet degrades the field, so neither MR detects "
                "it at any swept severity -- a genuine blind subspace, the PINN "
                "analogue of the MeshGraphNets knife-edge blind region."),
        },
        "per_sut": per_sut,
        "honesty_boundary": (
            "K=6 Burgers PINN checkpoints, one shared FD reference grid, one "
            "author-designed output-level fault catalogue. Bounded by-class "
            "detection on a fourth (pointwise) architecture family; NOT a "
            "real-world fault-detection rate, NOT a reliability, baseline-"
            "superiority, or cross-architecture generalization claim."),
    }
    (outdir / "pinn_seeded_fault_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("\nper-fault detection (rate, by-class):")
    for f, pf in per_fault.items():
        print(f"  {f:20s} rate={pf['detection_rate']:.2f} "
              f"CI={[round(c,2) for c in pf['detection_rate_wilson95']]} "
              f"class={pf['by_class_localization']:12s} "
              f"(mir={pf['detected_by_mirror']}, con={pf['detected_by_conservation']})")
    print(f"\nunion: {report['union_detection']['summary']}")
    print(f"blind spot detected across severity sweep: "
          f"{report['blind_spot']['detected_across_severity_sweep']}")
    print(f"wrote {(outdir / 'pinn_seeded_fault_report.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
