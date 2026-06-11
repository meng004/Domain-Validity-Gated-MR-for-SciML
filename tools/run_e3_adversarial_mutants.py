"""P2-3: adversarial mutants that are deliberately invariant under every
domain-validity detector at once.

The R3 PC_zero_vy result (Section 5.6.3) identified one point in input-space
where the geometric MR suite is blind: the exactly-uniform fraction p = 1.0,
where the fault is simultaneously permutation-invariant and mirror-y-symmetric.
This script asks a stronger question: is that point isolated, or is it one
member of an entire blind subspace defined by the conjunction of the three
invariances?

We construct two adversarial mutants by composing functions that we can prove,
on inspection, are invariant under every one of {node permutation, mirror-y
reflection, discrete divergence-free conservation}:

  A1 uniform_vx_offset (c = 0.05): delta_vx += c, delta_vy unchanged
     - node-permutation: yes (uniform per-node modification)
     - mirror-y: yes (vx is invariant under (x,y,vx,vy) -> (x,-y,vx,-vy))
     - conservation: yes (a spatial constant has zero divergence)

  A2 vx_plus_squared_vy (c = 0.05): delta_vx += c * delta_vy^2, delta_vy unchanged
     - node-permutation: yes (same per-node formula applied uniformly)
     - mirror-y: yes (vy^2 is invariant under vy -> -vy)
     - conservation: yes (the added term is constant in x, so d/dx of it is 0)

Each mutant is run against the K=6 multi-checkpoint roster (the same roster
used by E1, E3) and the same three predeclared detectors at the same
predeclared thresholds. The prediction (and so the resulting falsification
question) is "do the detectors flag a deliberately-invariant deviation?", and
the prediction is "no -- the blind region is a subspace, not an isolated
point". Raw outputs are committed at
research_assets/runs/adversarial-mutants-e3-extra/.

What this is NOT
----------------
This is not a real-world fault-detection rate, not a baseline-superiority
claim, and not a generality result across mesh families or SUT architectures.
It is a within-family structural bound on this MR suite: under the three
chosen detectors at the predeclared thresholds, the conjunction of their
three invariances is a fault subspace they cannot resolve.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

import run_e3_fault_robustness as E3

ADVERSARIAL_MUTANTS = [
    ("ADV_uniform_vx_offset",
     "uniform constant offset to vx (node-perm / mirror-y / conservation invariant)",
     {"offset": 0.05}),
    ("ADV_vx_plus_squared_vy",
     "add c * vy^2 to vx (node-perm / mirror-y / conservation invariant)",
     {"coef": 0.05}),
]
INPUT_SEED = 20260606


def _wrap_mutated_update(orig_mutated_update):
    """Return a callable that handles ADV_* mutants on top of the E3 catalogue."""
    def wrapper(mesh_pos, oh, ei_np, v_t, mutant, params=None):
        params = params or {}
        if mutant == "ADV_uniform_vx_offset":
            base = orig_mutated_update(mesh_pos, oh, ei_np, v_t, "baseline")
            c = float(params.get("offset", 0.05))
            out = np.array(base, copy=True)
            out[:, 0] = out[:, 0] + c
            return out
        if mutant == "ADV_vx_plus_squared_vy":
            base = orig_mutated_update(mesh_pos, oh, ei_np, v_t, "baseline")
            c = float(params.get("coef", 0.05))
            out = np.array(base, copy=True)
            out[:, 0] = out[:, 0] + c * (out[:, 1] ** 2)
            return out
        return orig_mutated_update(mesh_pos, oh, ei_np, v_t, mutant, params)
    return wrapper


def _wrap_predict(rt):
    """Wrap predict() so the inner mutated_update is the adversarial-aware one."""
    torch_mod = rt["torch"]
    base_ei = rt["base_edge_index"]  # unused here, kept for parity
    inflow_m = rt["inflow"]; wall_m = rt["wall"]
    mutated = rt["mutated_update"]

    def predict(mesh_pos, oh, ei_np, inflow_m_, wall_m_, v_t, prescribed,
                mutant, params=None):
        delta = torch_mod.as_tensor(
            mutated(mesh_pos, oh, ei_np, v_t, mutant, params))
        v_t_t = torch_mod.as_tensor(v_t)
        v_next = (v_t_t + delta).detach().numpy().copy()
        v_next[inflow_m_] = prescribed[inflow_m_]
        v_next[wall_m_] = 0.0
        return v_next
    return predict


def run_adversarial_for_sut(sut_id: str, ckpt: Path) -> dict:
    rt = E3.make_sut_runtime(ckpt)
    rt["mutated_update"] = _wrap_mutated_update(rt["mutated_update"])
    rt["predict"] = _wrap_predict(rt)
    baseline = E3.detect_for_mutant(rt, "baseline", {}, INPUT_SEED)
    per_mutant = {"baseline": baseline}
    for mut, desc, params in ADVERSARIAL_MUTANTS:
        v = E3.detect_for_mutant(rt, mut, params, INPUT_SEED)
        d = E3.decide_detection(v, baseline["mirror_y_median"])
        per_mutant[mut] = {"values": v, "detections": d,
                           "description": desc, "params": params}
    return per_mutant


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outdir",
                   default=str(E3.ROOT /
                               "research_assets/runs/adversarial-mutants-e3-extra"))
    args = p.parse_args(argv)
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    per_sut: dict[str, dict] = {}
    for sut_id, ckpt in E3.SUTS:
        if not ckpt.exists():
            print(f"!! {sut_id}: missing checkpoint, skipping")
            continue
        print(f"== {sut_id} == adversarial mutants", flush=True)
        per_sut[sut_id] = run_adversarial_for_sut(sut_id, ckpt)

    detectors = ["node_perm", "conservation", "mirror_y", "any"]
    aggregate = {}
    for mut, desc, _params in ADVERSARIAL_MUTANTS:
        per_det = {}
        for det in detectors:
            k = sum(1 for s in per_sut.values()
                    if s.get(mut) and s[mut]["detections"][det])
            n = len(per_sut)
            p_hat, lo, hi = E3.wilson_ci(k, n)
            per_det[det] = {"k": k, "n": n, "rate": p_hat,
                            "ci_lo": lo, "ci_hi": hi}
        aggregate[mut] = {"description": desc, "per_detector": per_det}

    report = {
        "experiment_id": "E3-adversarial-mutants",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "purpose": ("Confirm or refute the hypothesis that the blind region "
                    "identified at R3 (PC_zero_vy, p=1.0) is one point in an "
                    "entire fault subspace defined by the conjunction of the "
                    "three detector invariances."),
        "suts": list(per_sut.keys()),
        "input_seed": INPUT_SEED,
        "adversarial_mutants": [
            {"id": mut, "description": desc, "params": params}
            for mut, desc, params in ADVERSARIAL_MUTANTS],
        "per_sut_per_mutant": per_sut,
        "per_mutant_detection_rate": aggregate,
        "claim_limitations": (
            "Within-family bound: K=6 checkpoints of one architecture / one "
            "dataset, fixed thresholds, fixed input-permutation seed. Not a "
            "real-world fault-detection rate, not cross-architecture-family "
            "generalization, not a baseline-superiority claim."),
    }
    out = outdir / "adversarial_mutants_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {out}")
    for mut, agg in aggregate.items():
        any_ = agg["per_detector"]["any"]
        print(f"  {mut:30s} any-detector: {any_['k']}/{any_['n']} "
              f"= {any_['rate']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
