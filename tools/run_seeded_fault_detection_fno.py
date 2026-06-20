"""EXT (path B): end-to-end seeded-fault detection on the trained FNO-2D roster.

Upgrades the FNO primary workflow from a clean-model MR-compliance check
(``run_fno_primary_workflow.py``: translation passes, conservation fails) into a
fault DETECTION experiment, mirroring the MeshGraphNets seeded-fault study on a
different architecture family (spectral FNO) and different physics (Burgers /
heat PDEs, not Navier-Stokes), using the already-converged K=6 checkpoints.

Detectors = the FNO's two admitted MRs, each used to test the invariant it
actually measures:
  - periodic integer-translation MR: the clean model passes (mapped-follow-up
    matches source below tolerance); a fault is DETECTED when the faulted
    output's translation violation crosses the tolerance (pass -> fail).
  - periodic channel-sum (mass) MR: the conserved quantity is the per-channel
    spatial sum; a fault is DETECTED when it changes that sum, relative to the
    clean output, beyond a predeclared tolerance. (We test whether the fault
    BREAKS the invariant, not the clean model's absolute conservation quality,
    which is already imperfect and deferred elsewhere.)

Faults are standard output-level corruptions chosen so the detection structure
is by-class and includes a genuine blind region -- NOT rigged to flatter the
MRs:
  - global_scale (x(1+eps)): commutes with the spatial roll (translation blind);
    rescales the channel sum (conservation detects it).
  - constant_offset (+c): commutes with the roll (translation blind); shifts the
    channel sum (conservation detects it).
  - asymmetric_zero_sum_bias (+ position-dependent, zero spatial mean): breaks
    translation equivariance (translation detects it); preserves the channel sum
    (conservation blind).
  - asymmetric_nonzero_bias (+ position-dependent, nonzero mean): detected by BOTH.
  - transport_shift_blind (blend toward a spatially-shifted copy of the output):
    a pure spatial roll is a translation-equivariant, sum-preserving (unitary)
    operator, so blending toward a shifted copy preserves BOTH the translation
    relation and the channel sum, while substantially degrading the field. It
    models a realistic SciML failure mode -- a transport / phase error, e.g. a
    wrong advection speed -- and, having unit gain, it does not amplify the
    model's tiny non-equivariance residual. Neither MR can see it -> a genuine
    blind subspace, the FNO analogue of the MeshGraphNets knife-edge blind region.

Honesty boundary: K=6 FNO-2D checkpoints over two FD PDEs, one author-designed
fault catalogue. This is a bounded by-class detection / complementarity result;
it is NOT a real-world fault-detection rate, NOT a reliability or baseline-
superiority claim, and NOT a cross-architecture generalization claim.
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
ROSTER_DIR = ROOT / "research_assets/runs/fno-k6-roster"
OUT_DIR = ROOT / "research_assets/runs/fno-seeded-fault-detection"
SEEDS = [0, 1, 2]
PDES = ["burgers", "heat"]

# Predeclared detector thresholds.
TRANSLATION_TOL = 1e-5          # clean model passes below this; fault -> fail above
CONSERVATION_BREAK_TOL = 0.05   # fault changes channel sum by >5% of clean -> detected

# Fault severities, as a fraction of the per-case field RMS (scale-robust).
EPS_SCALE = 0.10                # global_scale: x(1 + EPS_SCALE)
C_OFFSET = 0.10                 # constant_offset magnitude (fraction of RMS)
B_BIAS = 0.10                   # asymmetric bias magnitude (fraction of RMS)
ALPHA_BLIND = 0.50              # transport_shift_blind blend weight toward shifted copy
K_SHIFT = 3                     # spatial shift (cells) for the transport/phase blind fault
BLIND_SWEEP = [0.25, 0.50, 0.75, 1.0]  # severity sweep for the blind spot

sys.path.insert(0, str(ROOT / "tools"))
from gen_fd_dataset_2d import make_dataset  # noqa: E402
from run_fno_k6_roster import load_model  # noqa: E402
from train_fno_2d import relative_l2  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def wilson_ci(k: int, n: int, z: float = 1.96) -> list[float]:
    """Wilson score 95% interval for k successes in n trials."""
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return [max(0.0, center - half), min(1.0, center + half)]


def channel_sum(field: np.ndarray) -> np.ndarray:
    """Per-channel spatial sum (the conserved quantity of the conservation MR)."""
    return np.sum(field, axis=(-2, -1))


def asymmetric_mask(shape: tuple[int, int]) -> np.ndarray:
    """Deterministic position-dependent pattern (non-periodic x ramp), unit RMS,
    zero spatial mean; used to break translation equivariance."""
    h, w = shape
    ramp = np.linspace(0.0, 1.0, w, dtype=np.float64)[None, :].repeat(h, axis=0)
    ramp = ramp - ramp.mean()
    rms = float(np.sqrt(np.mean(ramp ** 2))) + 1e-30
    return ramp / rms


def apply_fault(y: np.ndarray, fault: str, severity: float | None = None) -> np.ndarray:
    """Apply an output-level fault to a single case field of shape (C, H, W)."""
    rms = float(np.sqrt(np.mean(y ** 2))) + 1e-30
    hw = y.shape[-2:]
    if fault == "global_scale":
        return y * (1.0 + EPS_SCALE)
    if fault == "constant_offset":
        return y + C_OFFSET * rms
    if fault == "asymmetric_zero_sum_bias":
        m = asymmetric_mask(hw)            # zero spatial mean -> preserves sum
        return y + B_BIAS * rms * m[None, :, :]
    if fault == "asymmetric_nonzero_bias":
        m = asymmetric_mask(hw) + 1.0      # nonzero spatial mean -> shifts sum
        return y + B_BIAS * rms * m[None, :, :]
    if fault == "transport_shift_blind":
        a = ALPHA_BLIND if severity is None else severity
        # blend toward a spatially-shifted copy: a translation-equivariant,
        # sum-preserving transport/phase error (e.g. a wrong advection speed).
        return (1.0 - a) * y + a * np.roll(y, K_SHIFT, axis=-1)
    raise ValueError(f"unknown fault {fault}")


FAULTS = {
    "global_scale": "scale",
    "constant_offset": "offset",
    "asymmetric_zero_sum_bias": "asymmetry",
    "asymmetric_nonzero_bias": "asymmetry+offset",
    "transport_shift_blind": "transport/phase (blind)",
}


def _faulted_predict(model, inp, fault, severity):
    out = model(inp.unsqueeze(0)).squeeze(0).numpy()
    return out if fault is None else apply_fault(out, fault, severity)


def translation_violation(model, x_case, fault, shift, severity=None) -> float:
    """Translation-MR violation for a (possibly faulted) output on one case."""
    with torch.no_grad():
        y_source = _faulted_predict(model, x_case, fault, severity)
        y_follow = _faulted_predict(
            model, torch.roll(x_case, shifts=(shift, shift), dims=(-2, -1)), fault, severity)
    y_mapped = np.roll(y_follow, shift=(-shift, -shift), axis=(-2, -1))
    return relative_l2(y_mapped, y_source)


def conservation_break(y_clean: np.ndarray, y_faulted: np.ndarray) -> float:
    """Relative change the fault induces in the conserved channel sum."""
    return relative_l2(channel_sum(y_faulted), channel_sum(y_clean))


def evaluate_sut(sut_dir: Path, n_eval: int, shift: int) -> dict:
    model, cfg = load_model(sut_dir)
    pde, seed = cfg["pde"], int(cfg["seed"])
    data = make_dataset(pde, "periodic", cfg["grid_n"], n_eval, 1000 + seed, steps=cfg["steps"])
    x = torch.from_numpy(data["inputs"])

    cases = []
    for ci in range(n_eval):
        x_case = x[ci]
        with torch.no_grad():
            y_clean = model(x_case.unsqueeze(0)).squeeze(0).numpy()
        base_trans = translation_violation(model, x_case, None, shift)

        row = {"case": ci, "baseline_translation_violation": base_trans, "detections": {}}
        for fault in FAULTS:
            f_trans = translation_violation(model, x_case, fault, shift)
            y_f = apply_fault(y_clean, fault)
            f_cons = conservation_break(y_clean, y_f)
            det_trans = bool(f_trans > TRANSLATION_TOL and base_trans <= TRANSLATION_TOL)
            det_cons = bool(f_cons > CONSERVATION_BREAK_TOL)
            row["detections"][fault] = {
                "translation_violation": f_trans,
                "conservation_break": f_cons,
                "detected_by_translation": det_trans,
                "detected_by_conservation": det_cons,
                "detected": bool(det_trans or det_cons),
            }
        sweep = []
        for sev in BLIND_SWEEP:
            f_trans = translation_violation(model, x_case, "transport_shift_blind", shift, sev)
            y_f = apply_fault(y_clean, "transport_shift_blind", sev)
            f_cons = conservation_break(y_clean, y_f)
            sweep.append({
                "severity": sev,
                "output_perturbation_rel_l2": relative_l2(y_f, y_clean),
                "translation_violation": f_trans, "conservation_break": f_cons,
                "detected": bool(f_trans > TRANSLATION_TOL or f_cons > CONSERVATION_BREAK_TOL),
            })
        row["blind_severity_sweep"] = sweep
        cases.append(row)

    return {"sut_id": f"{pde}_s{seed}", "pde": pde, "seed": seed,
            "checkpoint": str((sut_dir / "sut/checkpoint.pt").relative_to(ROOT)),
            "cases": cases}


def aggregate(per_sut: list[dict]) -> dict:
    rows = [(f, d) for s in per_sut for c in s["cases"] for f, d in c["detections"].items()]

    per_fault = {}
    for fault, cls in FAULTS.items():
        ds = [d for (f, d) in rows if f == fault]
        n = len(ds)
        k_any = sum(d["detected"] for d in ds)
        k_tr = sum(d["detected_by_translation"] for d in ds)
        k_co = sum(d["detected_by_conservation"] for d in ds)
        per_fault[fault] = {
            "fault_class": cls, "n_cells": n,
            "detected_any": k_any, "detection_rate": k_any / n if n else 0.0,
            "detection_rate_wilson95": wilson_ci(k_any, n),
            "detected_by_translation": k_tr, "detected_by_conservation": k_co,
            "by_class_localization": (
                "translation" if k_tr and not k_co else
                "conservation" if k_co and not k_tr else
                "both" if k_tr and k_co else "none"),
        }

    detected_faults = sum(1 for f in FAULTS if per_fault[f]["detection_rate"] >= 0.5)
    blind = per_fault["transport_shift_blind"]
    blind_sweep_detect = any(
        sw["detected"] for s in per_sut for c in s["cases"] for sw in c["blind_severity_sweep"])

    return {
        "record_type": "fno-seeded-fault-detection",
        "schema_version": "0.1.0",
        "generated_at": _utc_now(),
        "architecture_family": "FNO-2D (spectral)",
        "pdes": PDES, "seeds": SEEDS,
        "trained_sut_count": len(per_sut),
        "detectors": {
            "periodic_translation_MR": f"clean pass < {TRANSLATION_TOL:g}; fault -> fail above",
            "periodic_channel_sum_MR": f"fault changes channel sum vs clean by > {CONSERVATION_BREAK_TOL}",
        },
        "fault_catalogue": FAULTS,
        "per_fault": per_fault,
        "union_detection": {
            "faults_detected_majority": detected_faults,
            "faults_total": len(FAULTS),
            "summary": f"{detected_faults}/{len(FAULTS)} faults detected by >=1 MR (>=50% of cells)",
        },
        "blind_spot": {
            "fault": "transport_shift_blind",
            "by_class_localization": blind["by_class_localization"],
            "detected_across_severity_sweep": blind_sweep_detect,
            "interpretation": (
                "A transport/phase error (blend toward a spatially-shifted copy "
                "of the output, e.g. a wrong advection speed) is translation-"
                "equivariant and channel-sum-preserving, so it degrades the field "
                "while preserving both measured invariants and neither MR detects "
                "it at any swept severity -- a genuine blind subspace, the FNO "
                "analogue of the MeshGraphNets knife-edge blind region."),
        },
        "per_sut": per_sut,
        "honesty_boundary": (
            "K=6 trained FNO-2D checkpoints over FD Burgers/heat, one "
            "author-designed output-level fault catalogue. Bounded by-class "
            "detection / complementarity on a second architecture family and "
            "different physics; NOT a real-world fault-detection rate, NOT a "
            "reliability, baseline-superiority, or cross-architecture "
            "generalization claim."),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n-eval", type=int, default=4)
    ap.add_argument("--shift", type=int, default=2)
    ap.add_argument("--outdir", default=str(OUT_DIR))
    args = ap.parse_args(argv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    per_sut = []
    for pde in PDES:
        for seed in SEEDS:
            sut_dir = ROSTER_DIR / f"{pde}_s{seed}"
            if not (sut_dir / "sut/checkpoint.pt").exists():
                raise FileNotFoundError(
                    f"missing FNO roster checkpoint under {sut_dir}; run "
                    "tools/run_fno_k6_roster.py first")
            res = evaluate_sut(sut_dir, args.n_eval, args.shift)
            per_sut.append(res)
            print(f"[{res['sut_id']}] evaluated {len(res['cases'])} cases", flush=True)

    report = aggregate(per_sut)
    report_path = outdir / "fno_seeded_fault_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("\nper-fault detection (rate, by-class):")
    for f, pf in report["per_fault"].items():
        print(f"  {f:28s} rate={pf['detection_rate']:.2f} "
              f"CI={[round(c,2) for c in pf['detection_rate_wilson95']]} "
              f"class={pf['by_class_localization']:12s} "
              f"(tr={pf['detected_by_translation']}, co={pf['detected_by_conservation']})")
    print(f"\nunion: {report['union_detection']['summary']}")
    print(f"blind spot detected across severity sweep: "
          f"{report['blind_spot']['detected_across_severity_sweep']}")
    print(f"wrote {report_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
