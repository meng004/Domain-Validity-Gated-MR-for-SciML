"""P2-4: refine the R3 PC_zero_vy severity sweep around the detection cliff.

The committed E3 report sweeps PC_zero_vy partial-zeroing fraction p over
{0.25, 0.5, 0.75, 1.0} and finds the any-detector rate collapses from 6/6 at
p=0.75 to 0/6 at p=1.0 -- the mirror-y blind region. That leaves the *location*
of the collapse unresolved across a wide gap. This script adds finer levels
{0.85, 0.9, 0.95, 0.99} and merges them into the existing
fault_robustness_report.json R3 sweep, recomputing the per-level Wilson CIs over
the full sorted level set. It reuses the read-only E3 machinery verbatim
(make_sut_runtime / detect_for_mutant / decide_detection / wilson_ci) so the new
points are computed identically to the originals.
"""
from __future__ import annotations

import json
from pathlib import Path

import run_e3_fault_robustness as E3

NEW_FRACS = [0.85, 0.9, 0.95, 0.99]
PERM_SEED = 20260606  # same permutation seed the original R3 sweep used
REPORT = E3.ROOT / "research_assets/runs/fault-robustness-e3/fault_robustness_report.json"
DETECTORS = ["node_perm", "conservation", "mirror_y", "any"]


def _sweep_ci(per_sut_sweep: dict, levels: list) -> dict:
    out = {}
    for lv in levels:
        per_det = {}
        for det in DETECTORS:
            k = sum(1 for _sut, s in per_sut_sweep.items()
                    if s.get(lv) and s[lv]["detections"][det])
            n = len(per_sut_sweep)
            p, lo, hi = E3.wilson_ci(k, n)
            per_det[det] = {"k": k, "n": n, "rate": p, "ci_lo": lo, "ci_hi": hi}
        out[str(lv)] = per_det
    return out


def main() -> int:
    report = json.loads(REPORT.read_text())
    r3 = report["R3_PC_zero_vy_partial_fraction_sweep"]
    raw = r3["per_sut_raw"]  # {sut: {str(frac): {...}}}

    # Recompute new fractions per SUT, reusing the existing baseline-per-SUT.
    for sut_id, ckpt in E3.SUTS:
        if not ckpt.exists():
            print(f"!! {sut_id}: missing checkpoint, skipping")
            continue
        print(f"== {sut_id} == load + R3 refine {NEW_FRACS}", flush=True)
        rt = E3.make_sut_runtime(ckpt)
        bl = E3.detect_for_mutant(rt, "baseline", {}, PERM_SEED)
        sut_raw = raw.setdefault(sut_id, {})
        for frac in NEW_FRACS:
            v = E3.detect_for_mutant(rt, "PC_zero_vy", {"zero_fraction": frac}, PERM_SEED)
            d = E3.decide_detection(v, bl["mirror_y_median"])
            sut_raw[str(frac)] = {"values": v, "detections": d}
            print(f"   p={frac}: any={d['any']} mirror_y={d['mirror_y']} "
                  f"node_perm={d['node_perm']} conservation={d['conservation']}")

    # Rebuild the level list (sorted unique floats) and per-level CIs.
    all_levels = sorted({float(k) for sut in raw.values() for k in sut})
    # per_sut_raw is keyed by str(frac); _sweep_ci expects float keys, so adapt.
    raw_float = {sut: {float(k): val for k, val in d.items()} for sut, d in raw.items()}
    r3["levels"] = all_levels
    r3["per_level_detection_rate"] = _sweep_ci(raw_float, all_levels)
    r3["refinement_note"] = (
        "Levels {0.85,0.9,0.95,0.99} added (P2-4) to resolve the any-detector "
        "collapse between p=0.75 (6/6) and p=1.0 (0/6); same permutation seed "
        f"({PERM_SEED}) and detection machinery as the original sweep.")
    report["R3_PC_zero_vy_partial_fraction_sweep"] = r3

    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {REPORT}")
    print("R3 refined any-detector rate by level:")
    for lv in all_levels:
        pd = r3["per_level_detection_rate"][str(lv)]["any"]
        print(f"  p={lv:<5} any {pd['k']}/{pd['n']} = {pd['rate']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
