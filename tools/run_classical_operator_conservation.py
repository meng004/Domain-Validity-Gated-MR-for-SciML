#!/usr/bin/env python3
"""Classical operator-code SUT: executable conservation MR on a finite-volume
scalar conservation law (1D periodic Burgers).

Conservation is ADMISSIBLE here (the flux-form discrete-conservation residual is
floating-point roundoff, ~1e-15, dominated by the 1e-12 verdict tolerance), so the
MR yields a full executable PASS/FAIL -- unlike the MGN cylinder case where the
absolute conservation relation is deferred for want of a calibratable floor. Faults
are injected into the scientist-written flux/update operator (the physics operator),
not the grid/time-stepping framework.

One relation, three typed verdicts: admissible+executable here, deferred on the MGN
cylinder (C12/C32), rejected on the compressible airfoil (C31).

Honesty boundary: one minimal textbook finite-volume exemplar; faults are
hand-constructed operator-code edits. Not a production-solver, reliability,
generalization, or baseline-superiority claim.

Design: paper/39_increment2_classical_operator_sut_design.md.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets" / "runs" / "classical-operator-conservation"

L, N, T_STEPS = 2.0, 200, 50
DX = L / N
CFL = 0.4
CONS_TOL = 1e-12   # verdict tolerance; dominates the ~1e-15 flux-form roundoff floor


def f(u: np.ndarray) -> np.ndarray:
    """Burgers flux f(u) = u^2 / 2."""
    return 0.5 * u * u


def initial_field() -> np.ndarray:
    x = (np.arange(N) + 0.5) * DX
    return 0.5 + 0.4 * np.sin(2 * np.pi * x / L)   # smooth, periodic, total mass != 0


def dt_from_cfl(u: np.ndarray) -> float:
    amax = float(np.max(np.abs(u))) or 1.0
    return CFL * DX / amax


def lf_flux(u: np.ndarray, dt: float) -> np.ndarray:
    """Lax-Friedrichs interface flux F_{i+1/2} (single-valued per interface)."""
    up = np.roll(u, -1)                              # u_{i+1}
    return 0.5 * (f(u) + f(up)) - 0.5 * (DX / dt) * (up - u)


def step(u: np.ndarray, mutant: str) -> np.ndarray:
    """One explicit step. The flux/update operator is the scientist-written code
    under test; mutants edit it. The framework (grid, stepping) is fixed."""
    dt = dt_from_cfl(u)
    if mutant == "nonconservative_form":            # advective (primitive, non-flux) form: not conservative
        # Upwind (backward; the field stays positive here so this is the correct
        # upwind direction) primitive-variable advection u*du/dx -- a realistic
        # "wrote the PDE in primitive form" operator bug that genuinely loses mass.
        # NB: a *centered* advective stencil u_i*(u_{i+1}-u_{i-1})/(2dx) instead
        # conserves the first moment (total mass) to roundoff by periodic
        # anti-symmetry, so it is a documented blind spot of a mass-conservation MR
        # (the MR detects faults that break the flux-difference telescoping
        # structure, not every non-conservative discretization).
        ux = (u - np.roll(u, 1)) / DX
        return u - dt * u * ux
    F = lf_flux(u, dt)                               # F_{i+1/2}, i = 0..N-1
    Fm = np.roll(F, 1)                              # F_{i-1/2}
    if mutant == "drop_boundary_flux":              # mis-index: sum(F-Fm) = F_{N-1} != 0
        Fm = Fm.copy()
        Fm[0] = 0.0
    elif mutant == "double_flux":                   # non-telescoping: sum(2F-roll(F,1)) = sum(F) != 0
        F = 2.0 * F
    return u - (dt / DX) * (F - Fm)


def total_mass(u: np.ndarray) -> float:
    return float(np.sum(u) * DX)


def run_mutant(mutant: str) -> dict:
    u = initial_field()
    m0 = total_mass(u)
    max_abs_dm = 0.0
    for _ in range(T_STEPS):
        u = step(u, mutant)
        max_abs_dm = max(max_abs_dm, abs(total_mass(u) - m0))
    detected = max_abs_dm > CONS_TOL
    return {
        "mutant": mutant,
        "max_abs_delta_mass": max_abs_dm,
        "conservation_MR_pass": (not detected),
        "conservation_MR_detects_fault": detected,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(OUTDIR))
    args = ap.parse_args(argv)

    mutants = ["baseline", "nonconservative_form", "drop_boundary_flux", "double_flux"]
    rows = [run_mutant(m) for m in mutants]
    base = next(r for r in rows if r["mutant"] == "baseline")
    faults = [r for r in rows if r["mutant"] != "baseline"]

    record = {
        "ledger_id": "classical-operator-conservation",
        "schema_version": "0.1.0",
        "evidence_level": "classical-operator-code-sut-executable-conservation",
        "sut": "1D periodic finite-volume Burgers (flux-form Lax-Friedrichs)",
        "operator_under_test": "scientist-written interface flux + flux-form update",
        "framework_libraries": "uniform grid, explicit time-stepping (not under test)",
        "conservation_mr": {
            "quantity": "total mass M = sum(u)*dx",
            "tolerance": CONS_TOL,
            "operator_floor_estimate": "flux-form telescoping residual ~1e-15 (float roundoff)",
            "admissible": True,
            "admissibility_reason": "verdict tolerance 1e-12 dominates the ~1e-15 flux-form floor",
        },
        "grid": {"L": L, "N": N, "dx": DX, "steps": T_STEPS, "cfl": CFL},
        "results": rows,
        "summary": {
            "baseline_pass": base["conservation_MR_pass"],
            "baseline_max_abs_delta_mass": base["max_abs_delta_mass"],
            "faults_detected": sum(r["conservation_MR_detects_fault"] for r in faults),
            "num_faults": len(faults),
        },
        "typed_verdict_contrast": {
            "classical_fv_operator": "admissible + executable (this run)",
            "cylinder_mgn": "deferred (uncalibratable floor; C12/C32)",
            "airfoil_mgn": "rejected (compressible; C31)",
        },
        "honesty_boundary": (
            "One minimal textbook FV exemplar; faults are hand-constructed operator-code "
            "edits. Not a production-solver, reliability, generalization, or "
            "baseline-superiority claim."
        ),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    out = Path(args.outdir)
    (out / "raw").mkdir(parents=True, exist_ok=True)
    (out / "raw" / "metric_ledger.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(f"baseline |dM|max={base['max_abs_delta_mass']:.2e} PASS={base['conservation_MR_pass']}")
    for r in faults:
        print(f"  {r['mutant']:22s} |dM|max={r['max_abs_delta_mass']:.3e} "
              f"detected={r['conservation_MR_detects_fault']}")
    print(f"faults detected: {record['summary']['faults_detected']}/{record['summary']['num_faults']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
