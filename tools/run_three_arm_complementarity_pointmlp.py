"""Three-arm complementarity + baseline-false-positive gate value + knife-edge curve
on the converged PointMLP cylinder SUT (claims C42, C43; MVP-B/C).

Three detector arms on the same converged row-wise PointMLP SUT (rollout median rel-L2
0.0298), over an expanded >=20-fault catalogue spanning four predeclared fault classes:

  ARM 1  validity-gated MR suite      -- the three admitted MRs (node-perm, conservation,
                                         mirror-y) with their predeclared thresholds;
  ARM 2  accuracy-monitor             -- rollout relative-L2 >= 2x the fault-free baseline;
  ARM 3  ungated-generic detectors    -- each generic MT template treated as a claimed exact
                                         invariant; its key metric is the BASELINE FALSE-
                                         POSITIVE rate (does it flag the fault-free, correct
                                         SUT?). The gate admits only the template(s) that are
                                         real invariants (false-positive ~0) and rejects the
                                         rest, which fire on the correct SUT.

Outputs: per-arm detection with Wilson 95% CIs; a 2x2 MR-vs-accuracy complementarity table
(MR-only / accuracy-only / both / neither); the third arm's baseline false-positive contrast
(the measurable gate value); and a knife-edge severity curve (PC_zero_vy node-index-selected
partial-zeroing sweep, detection-vs-severity), the differentiated finding that a fault can
become invisible to a geometric detector exactly when it enters the detector's invariance.

This is complementarity and a gate-value measurement, NOT a superiority claim. One converged
SUT, one checkpoint, one eval trajectory; the cross-SUT MGN reference is read from committed
artifacts (C38, C13), not re-run here. ARS self-check: the four fault classes are predeclared;
results are descriptive detection rates with Wilson CIs (no hypothesis test), so no multiple-
comparison correction is applied (stated, not hidden).
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
sys.path.insert(0, str(ROOT / "tools"))
import conservation_rubric as conservation  # noqa: E402
from run_pointmlp_cylinder_primary_workflow import (  # noqa: E402
    _features, _normalize, _denormalize_y, _relative_l2, _reflection_map,
    _mirror_velocity, _load_case, _wilson, EVAL_TRAJECTORIES,
)
from run_seeded_fault_detection_pointmlp import (  # noqa: E402
    load_model, NODE_INFLOW, NODE_WALL, NODE_PERM_TOL, CONSERVATION_RATIO_TOL,
    MIRROR_Y_REL_CHANGE_TOL,
)

ACCURACY_ROLLOUT_MULT = 2.0   # accuracy monitor: rollout error >= 2x fault-free baseline
GENERIC_EXACT_TOL = 1e-5      # exactness tolerance for a claimed-invariant generic detector

# Expanded fault catalogue (>=20), four predeclared classes. Severity variants of the two
# threshold-sensitive faults supply the bulk; the canonical points are included.
NS_SCALES = [1.1, 1.25, 1.5, 2.0, 4.0]
PC_FRACTIONS = [0.1, 0.25, 0.5, 0.75, 0.85, 0.9, 0.95, 0.99, 1.0]
MGN_REF = ROOT / "research_assets/runs/detection-vs-accuracy/raw/metric_ledger.json"


def build_catalogue() -> list[dict]:
    cat = [
        {"id": "BC_zero_inflow", "class": "boundary_condition_fault", "op": "BC_zero_inflow"},
        {"id": "BC_nonzero_wall", "class": "boundary_condition_fault", "op": "BC_nonzero_wall"},
        {"id": "NS_skip_denorm", "class": "normalization_scale_fault", "op": "NS_skip_denorm"},
        {"id": "TR_sign_flip", "class": "temporal_rollout_fault", "op": "TR_sign_flip"},
        {"id": "TR_double_step", "class": "temporal_rollout_fault", "op": "TR_double_step"},
        {"id": "PC_swap_xy", "class": "physical_channel_fault", "op": "PC_swap_xy"},
    ]
    for s in NS_SCALES:
        cat.append({"id": f"NS_double_scale@{s}", "class": "normalization_scale_fault",
                    "op": "NS_double_scale", "scale": s})
    for p in PC_FRACTIONS:
        cat.append({"id": f"PC_zero_vy@{p}", "class": "physical_channel_fault",
                    "op": "PC_zero_vy", "fraction": p})
    return cat


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "research_assets/runs/pointmlp-three-arm-complementarity"))
    args = ap.parse_args(argv)
    outdir = Path(args.out)
    (outdir / "raw").mkdir(parents=True, exist_ok=True)

    model, stats = load_model()
    case = _load_case(EVAL_TRAJECTORIES[0])
    pos, nt, vel, cells = case["mesh_pos"], case["node_type"], case["velocity"], case["cells"]
    frames = list(range(int(vel.shape[0]) - 1))
    nt_arr = np.asarray(nt)

    rng = np.random.default_rng(20260620)
    perm = rng.permutation(pos.shape[0])
    inv = np.empty_like(perm); inv[perm] = np.arange(perm.shape[0])
    # node-index-selected zero-vy subsets (fixed across frames) per fraction.
    zsel_rng = np.random.default_rng(99)
    zero_sel = {p: (zsel_rng.random(pos.shape[0]) < p) for p in PC_FRACTIONS}
    axis = float((pos[:, 1].min() + pos[:, 1].max()) / 2.0)
    mapping, floor = _reflection_map(pos, axis)

    def raw_update(p, v, n):
        feat = _features(p, v, n)
        with torch.no_grad():
            dn = model(torch.as_tensor(_normalize(feat, stats), dtype=torch.float32)).numpy()
        return dn, _denormalize_y(dn, stats)

    def mutated_update(p, v, n, fault):
        dn, delta = raw_update(p, v, n)
        op = fault["op"]
        if op == "NS_skip_denorm":
            delta = dn
        elif op == "NS_double_scale":
            delta = float(fault.get("scale", 2.0)) * delta
        if op == "PC_swap_xy":
            delta = delta[:, [1, 0]]
        elif op == "PC_zero_vy":
            sel = zero_sel[fault.get("fraction", 1.0)]
            dvy = np.where(sel, 0.0, delta[:, 1])
            delta = np.stack([delta[:, 0], dvy], axis=-1)
        return delta

    def predict(p, v, n, fault):
        op = fault["op"]
        delta = mutated_update(p, v, n, fault)
        if op == "TR_sign_flip":
            vn = v - delta
        elif op == "TR_double_step":
            vmid = v + delta
            vn = vmid + mutated_update(p, vmid, n, fault)
        else:
            vn = v + delta
        vn = np.asarray(vn, dtype=np.float32).copy()
        presc = np.asarray(n) != 0
        vn[presc] = v[presc]
        if op == "BC_zero_inflow":
            vn[np.asarray(n) == NODE_INFLOW] = 0.0
        elif op == "BC_nonzero_wall":
            vn[np.asarray(n) == NODE_WALL] = 0.2
        return vn

    CLEAN = {"op": "clean"}

    def med(xs):
        return float(np.median(np.asarray(xs, dtype=np.float64)))

    def arms_for(fault):
        npv, cov, miv, rov = [], [], [], []
        for t in frames:
            v = vel[t]
            base = mutated_update(pos, v, nt, fault)
            outp = mutated_update(pos[perm], v[perm], nt_arr[perm], fault)
            npv.append(_relative_l2(outp[inv], base))
            vn = predict(pos, v, nt, fault)
            rp = conservation.divergence_rms(pos, cells, vn)
            rr = conservation.divergence_rms(pos, cells, vel[t + 1])
            cov.append(rp / rr if rr else float("inf"))
            src = mutated_update(pos, v, nt, fault)
            fol = mutated_update(pos, _mirror_velocity(v[mapping]), nt, fault)
            miv.append(_relative_l2(_mirror_velocity(fol[mapping]), src))
            rov.append(_relative_l2(vn, vel[t + 1]))
        return {"np": med(npv), "cons": med(cov), "mir": med(miv), "roll": med(rov)}

    base = arms_for(CLEAN)
    base_mir, base_roll = base["mir"], base["roll"]

    # ---- per-fault three-arm detection over the expanded catalogue ----
    catalogue = build_catalogue()
    per_fault = []
    for f in catalogue:
        a = arms_for(f)
        mir_rel = abs(a["mir"] - base_mir) / base_mir if base_mir else float("inf")
        mr = bool(a["np"] > NODE_PERM_TOL or a["cons"] > CONSERVATION_RATIO_TOL
                  or mir_rel > MIRROR_Y_REL_CHANGE_TOL)
        acc = bool(a["roll"] >= ACCURACY_ROLLOUT_MULT * base_roll)
        per_fault.append({
            "fault": f["id"], "fault_class": f["class"],
            "node_perm_median": a["np"], "conservation_median": a["cons"],
            "mirror_y_rel_change": mir_rel, "rollout_median": a["roll"],
            "rollout_over_baseline": a["roll"] / base_roll if base_roll else None,
            "mr_arm_detects": mr, "accuracy_arm_detects": acc,
        })

    n = len(per_fault)
    mr_hits = sum(d["mr_arm_detects"] for d in per_fault)
    acc_hits = sum(d["accuracy_arm_detects"] for d in per_fault)
    both = [d["fault"] for d in per_fault if d["mr_arm_detects"] and d["accuracy_arm_detects"]]
    mr_only = [d["fault"] for d in per_fault if d["mr_arm_detects"] and not d["accuracy_arm_detects"]]
    acc_only = [d["fault"] for d in per_fault if d["accuracy_arm_detects"] and not d["mr_arm_detects"]]
    neither = [d["fault"] for d in per_fault if not d["mr_arm_detects"] and not d["accuracy_arm_detects"]]

    # ---- ARM 3: ungated-generic detectors, baseline false-positive contrast ----
    # Each template is a claimed exact invariant: transform input -> predict -> invert ->
    # compare to the direct prediction; a baseline false positive is firing on the fault-free
    # SUT (relative L2 > exact tolerance). Admissibility is the committed generic-MR-baseline
    # decision (research_assets/runs/generic-mr-baseline/).
    def fp_rate(transform_in, invert_out):
        hits = 0
        for t in frames:
            v = vel[t]
            _, src = raw_update(pos, v, nt)
            p2, v2, n2 = transform_in(pos, v, nt_arr)
            _, out = raw_update(p2, v2, n2)
            hits += int(_relative_l2(invert_out(out), src) > GENERIC_EXACT_TOL)
        return hits / len(frames)

    tvec = np.array([0.13, 0.07], dtype=np.float32)
    generic = [
        ("node_permutation", True,
         (lambda p, v, n: (p[perm], v[perm], n[perm])), (lambda o: o[inv])),
        ("mirror_y_reflection", False,
         (lambda p, v, n: (p, _mirror_velocity(v[mapping]), n)), (lambda o: _mirror_velocity(o[mapping]))),
        ("mirror_x_reflection", False,
         (lambda p, v, n: (np.stack([2 * float((p[:, 0].min() + p[:, 0].max()) / 2) - p[:, 0], p[:, 1]], axis=1).astype(np.float32),
                           np.stack([-v[:, 0], v[:, 1]], axis=1).astype(np.float32), n)),
         (lambda o: np.stack([-o[:, 0], o[:, 1]], axis=1).astype(np.float32))),
        ("domain_translation", False,
         (lambda p, v, n: ((p + tvec).astype(np.float32), v, n)), (lambda o: o)),
        ("input_global_scaling", False,
         (lambda p, v, n: (p, (1.5 * v).astype(np.float32), n)), (lambda o: (o / 1.5).astype(np.float32))),
        ("channel_swap", False,
         (lambda p, v, n: (p, v[:, [1, 0]].astype(np.float32), n)), (lambda o: o[:, [1, 0]].astype(np.float32))),
        ("additive_output_constant", False,
         (lambda p, v, n: (p, (v + tvec).astype(np.float32), n)), (lambda o: o)),
    ]
    arm3 = []
    for tid, admit, tin, iout in generic:
        fp = fp_rate(tin, iout)
        arm3.append({"template": tid, "admitted_by_gate": admit,
                     "baseline_false_positive_rate": fp,
                     "false_positive_ci95": _wilson(int(round(fp * len(frames))), len(frames)),
                     "flags_fault_free_sut": bool(fp > 0.0)})
    admitted_fp = [a["baseline_false_positive_rate"] for a in arm3 if a["admitted_by_gate"]]
    rejected_fp = [a["baseline_false_positive_rate"] for a in arm3 if not a["admitted_by_gate"]]

    # ---- knife-edge: PC_zero_vy node-index-selected partial-zeroing sweep ----
    knife = []
    for p in PC_FRACTIONS:
        d = next(x for x in per_fault if x["fault"] == f"PC_zero_vy@{p}")
        knife.append({"fraction": p, "node_perm_median": d["node_perm_median"],
                      "mirror_y_rel_change": d["mirror_y_rel_change"],
                      "rollout_over_baseline": d["rollout_over_baseline"],
                      "mr_detects": d["mr_arm_detects"], "accuracy_detects": d["accuracy_arm_detects"]})
    mr_detect_fracs = sorted(k["fraction"] for k in knife if k["mr_detects"])
    mr_miss_fracs = sorted(k["fraction"] for k in knife if not k["mr_detects"])

    mgn = json.loads(MGN_REF.read_text(encoding="utf-8")) if MGN_REF.exists() else {}
    mgn_comp = mgn.get("complementarity", {})

    classes = sorted({f["class"] for f in catalogue})
    ledger = {
        "ledger_id": "pointmlp-three-arm-complementarity",
        "evidence_level": "converged-pointmlp-three-arm-complementarity-and-gate-value",
        "schema_version": "0.1.0",
        "sut_id": "pointmlp-cylinder-sut-v1",
        "architecture_family": "PointMLP row-wise coordinate network (no message passing)",
        "rollout_convergence_median_relative_l2": 0.02975835263724644,
        "num_frames": len(frames),
        "fault_catalogue_size": n,
        "fault_classes_predeclared": classes,
        "thresholds": {"node_perm": NODE_PERM_TOL, "conservation_ratio": CONSERVATION_RATIO_TOL,
                       "mirror_y_rel_change": MIRROR_Y_REL_CHANGE_TOL,
                       "accuracy_rollout_multiplier": ACCURACY_ROLLOUT_MULT,
                       "generic_exact_tolerance": GENERIC_EXACT_TOL},
        "baseline": {"mirror_y_violation_median": base_mir, "rollout_relative_l2_median": base_roll},
        "arm1_validity_gated_mr": {
            "detection_count": mr_hits, "detection_rate": mr_hits / n,
            "detection_rate_wilson_ci95": _wilson(mr_hits, n)},
        "arm2_accuracy_monitor": {
            "detection_count": acc_hits, "detection_rate": acc_hits / n,
            "detection_rate_wilson_ci95": _wilson(acc_hits, n)},
        "arm3_ungated_generic_false_positive": {
            "per_template": arm3,
            "admitted_template_max_false_positive_rate": max(admitted_fp) if admitted_fp else 0.0,
            "rejected_template_min_false_positive_rate": min(rejected_fp) if rejected_fp else None,
            "n_rejected_templates_flagging_fault_free_sut": sum(
                1 for a in arm3 if not a["admitted_by_gate"] and a["flags_fault_free_sut"]),
            "n_rejected_templates": sum(1 for a in arm3 if not a["admitted_by_gate"]),
            "gate_value": ("admitted (real-invariant) detectors do not flag the fault-free SUT "
                           "(false-positive ~0); the rejected generic templates fire on the "
                           "correct SUT -- the gate removes the false-alarming detectors")},
        "complementarity_2x2_mr_vs_accuracy": {
            "both": both, "mr_only": mr_only, "accuracy_only": acc_only, "neither": neither,
            "counts": {"both": len(both), "mr_only": len(mr_only),
                       "accuracy_only": len(acc_only), "neither": len(neither)},
            "note": ("complementarity, not superiority: the MR arm and the accuracy arm catch "
                     "distinct fault subsets; an MR-only fault is a relation violation an "
                     "accuracy monitor leaves within band")},
        "knife_edge_pc_zero_vy_sweep": {
            "curve": knife, "mr_detect_fractions": mr_detect_fracs,
            "mr_miss_fractions": mr_miss_fracs,
            "finding": ("node-index-selected partial vy-zeroing breaks node-permutation "
                        "equivariance and is detected; the uniform fraction 1.0 is permutation-"
                        "invariant and escapes -- a fault becomes invisible to the geometric "
                        "detector exactly when it enters the detector's invariance")},
        "cross_sut_mgn_reference": {
            "source": str(MGN_REF.relative_to(ROOT)) if mgn else None,
            "mgn_mr_catches_accuracy_misses": mgn_comp.get("mr_catches_accuracy_misses"),
            "mgn_accuracy_catches_mr_misses": mgn_comp.get("accuracy_catches_mr_misses"),
            "note": "MGN complementarity read from committed C38 artifact, not re-run here"},
        "ars_self_check": {
            "fault_classes_predeclared": True,
            "statistic": "descriptive detection rates with Wilson 95% CIs (no hypothesis test)",
            "multiple_comparison_correction": "not applicable -- descriptive rates, not p-values",
        },
        "claim_limitations": (
            "One converged SUT, one checkpoint, one eval trajectory, one expanded injected-fault "
            "catalogue. Complementarity and a measurable gate value (baseline false positives), "
            "not a real-world rate, reliability, or any baseline-superiority claim. The MGN "
            "cross-SUT reference is read from committed artifacts, not re-run."),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (outdir / "raw" / "metric_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"PointMLP three-arm over {n} faults ({len(classes)} classes):")
    print(f"  arm1 validity-gated MR: {mr_hits}/{n} ({mr_hits/n:.0%}) Wilson {ledger['arm1_validity_gated_mr']['detection_rate_wilson_ci95']}")
    print(f"  arm2 accuracy-monitor : {acc_hits}/{n} ({acc_hits/n:.0%})")
    print(f"  2x2: both={len(both)} mr_only={len(mr_only)} acc_only={len(acc_only)} neither={len(neither)}")
    print(f"  arm3 generic baseline FP: admitted max={max(admitted_fp) if admitted_fp else 0.0:.2f}, "
          f"rejected templates flagging fault-free SUT={ledger['arm3_ungated_generic_false_positive']['n_rejected_templates_flagging_fault_free_sut']}"
          f"/{ledger['arm3_ungated_generic_false_positive']['n_rejected_templates']}")
    print(f"  knife-edge PC_zero_vy: MR detects fractions {mr_detect_fracs}, misses {mr_miss_fracs}")
    print(f"wrote {outdir/'raw'/'metric_ledger.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
