"""Seeded-fault detection on the converged PointMLP cylinder SUT (claim C41).

MVP-A of the 1-区 empirical expansion: give the already-converged, different-architecture
PointMLP cylinder surrogate (row-wise, no message passing; rollout median rel-L2 0.0298,
research_assets/runs/pointmlp-cylinder-primary-workflow/) the seeded-fault-detection step the
main MeshGraphNets SUT already has (claim C10), so the "5/10 + by-class localization" reading
is exercised on a SECOND genuinely different architecture family (addressing the
speculative-claims gap "K=6 checkpoints share one architecture family").

The fault catalogue and the three domain-validity MR detectors are reused verbatim from the
MGN runner (tools/run_seeded_fault_detection.py) with the SAME predeclared thresholds
(node-perm 1e-5, conservation ratio 1.5, mirror-y relative-change 0.5), wired to the PointMLP
predict interface. Eight of the ten mutants apply; the two mesh-adjacency mutants
(MA_drop_edges, MA_permute_edges) act on a graph edge set that a row-wise PointMLP does not
have, so they are recorded as NOT APPLICABLE (a no-op on this architecture) rather than as a
detector miss -- the fault surface itself is architecture-dependent.

Honesty boundary: one converged SUT, one checkpoint, one eval trajectory, the same injected-
fault catalogue. Detection rates are for this mutant set only; this is not a real-world
fault-detection rate, a reliability claim, a baseline-superiority claim, or proof that the
by-class pattern generalizes across architectures (at most it REPRODUCES on these two).
"""
from __future__ import annotations

import argparse
import hashlib
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
    PointMLP, _features, _normalize, _denormalize_y, _relative_l2,
    _reflection_map, _mirror_velocity, _load_case, _wilson, EVAL_TRAJECTORIES,
)

# Same taxonomy as the MGN runner (tools/run_seeded_fault_detection.py).
FAULT_CLASS = {
    "BC_zero_inflow": "boundary_condition_fault",
    "BC_nonzero_wall": "boundary_condition_fault",
    "MA_drop_edges": "mesh_adjacency_fault",
    "MA_permute_edges": "mesh_adjacency_fault",
    "NS_skip_denorm": "normalization_scale_fault",
    "NS_double_scale": "normalization_scale_fault",
    "TR_sign_flip": "temporal_rollout_fault",
    "TR_double_step": "temporal_rollout_fault",
    "PC_swap_xy": "physical_channel_fault",
    "PC_zero_vy": "physical_channel_fault",
}
MUTANTS = list(FAULT_CLASS)
# A row-wise PointMLP has no mesh adjacency / edge connectivity, so the two graph-edge
# mutants cannot act (they are no-ops). Recorded as not-applicable, not as detector misses.
NOT_APPLICABLE = {
    "MA_drop_edges": "row-wise PointMLP has no mesh adjacency / edge set to drop (no-op)",
    "MA_permute_edges": "row-wise PointMLP has no mesh adjacency / edge set to permute (no-op)",
}

# Predeclared thresholds, aligned to the MGN runner.
NODE_PERM_TOL = 1e-5
CONSERVATION_RATIO_TOL = 1.5
MIRROR_Y_REL_CHANGE_TOL = 0.5

# DeepMind cylinder_flow node types present in the eval trajectory.
NODE_INFLOW, NODE_WALL = 4, 6

CKPT = ROOT / "research_assets/runs/pointmlp-cylinder-primary-workflow/sut/checkpoint.pt"
MGN_REF = ROOT / "research_assets/runs/seeded-fault-detection/raw/metric_ledger.json"


def _sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _median(xs) -> float:
    return float(np.median(np.asarray(xs, dtype=np.float64)))


def load_model():
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    cfg = ck["config"]
    stats = {k: np.asarray(v, dtype=np.float32) for k, v in ck["stats"].items()}
    model = PointMLP(cfg["in_dim"], hidden=cfg["hidden"], depth=cfg["depth"])
    model.load_state_dict(ck["state_dict"])
    model.eval()
    return model, stats


def run() -> dict:
    model, stats = load_model()

    def raw_update(pos, vel, nt):
        feat = _features(pos, vel, nt)
        with torch.no_grad():
            dn = model(torch.as_tensor(_normalize(feat, stats), dtype=torch.float32)).numpy()
        return dn, _denormalize_y(dn, stats)  # (normalized delta, denormalized delta)

    def mutated_update(pos, vel, nt, mutant):
        """Model update (delta) under output-/normalization-/channel-level faults."""
        dn, delta = raw_update(pos, vel, nt)
        if mutant == "NS_skip_denorm":
            delta = dn
        elif mutant == "NS_double_scale":
            delta = 2.0 * delta
        if mutant == "PC_swap_xy":
            delta = delta[:, [1, 0]]
        elif mutant == "PC_zero_vy":
            delta = np.stack([delta[:, 0], np.zeros_like(delta[:, 1])], axis=-1)
        return delta

    def predict(pos, vel, nt, mutant):
        """Full next-state prediction (update + temporal step + boundary prescription)."""
        delta = mutated_update(pos, vel, nt, mutant)
        if mutant == "TR_sign_flip":
            v_next = vel - delta
        elif mutant == "TR_double_step":
            v_mid = vel + delta
            v_next = v_mid + mutated_update(pos, v_mid, nt, mutant)
        else:
            v_next = vel + delta
        v_next = np.asarray(v_next, dtype=np.float32).copy()
        presc = np.asarray(nt) != 0          # PointMLP prescribes non-NORMAL nodes
        v_next[presc] = vel[presc]
        if mutant == "BC_zero_inflow":
            v_next[np.asarray(nt) == NODE_INFLOW] = 0.0
        elif mutant == "BC_nonzero_wall":
            v_next[np.asarray(nt) == NODE_WALL] = 0.2
        return v_next

    case = _load_case(EVAL_TRAJECTORIES[0])
    pos, nt, vel, cells = case["mesh_pos"], case["node_type"], case["velocity"], case["cells"]
    frames = list(range(int(vel.shape[0]) - 1))

    rng = np.random.default_rng(20260620)
    perm = rng.permutation(pos.shape[0])
    inv = np.empty_like(perm)
    inv[perm] = np.arange(perm.shape[0])

    axis = float((pos[:, 1].min() + pos[:, 1].max()) / 2.0)
    mapping, floor = _reflection_map(pos, axis)

    def node_perm_metric(vel_t, mutant):
        base = mutated_update(pos, vel_t, nt, mutant)
        outp = mutated_update(pos[perm], vel_t[perm], nt[perm], mutant)
        return _relative_l2(outp[inv], base)

    def conservation_ratio(vel_t, ref, mutant):
        v_next = predict(pos, vel_t, nt, mutant)
        rp = conservation.divergence_rms(pos, cells, v_next)
        rr = conservation.divergence_rms(pos, cells, ref)
        return rp / rr if rr else float("inf")

    def mirror_violation(vel_t, mutant):
        src = mutated_update(pos, vel_t, nt, mutant)
        follow_in = _mirror_velocity(vel_t[mapping])
        fol = mutated_update(pos, follow_in, nt, mutant)
        mapped = _mirror_velocity(fol[mapping])
        return _relative_l2(mapped, src)

    # Per-mutant medians over frames (the MGN runner's detection statistic) + per-frame
    # detection fractions for frame-robustness.
    series = {}
    for mutant in ["baseline"] + [m for m in MUTANTS if m not in NOT_APPLICABLE]:
        npv, cov, miv = [], [], []
        for t in frames:
            npv.append(node_perm_metric(vel[t], mutant))
            cov.append(conservation_ratio(vel[t], vel[t + 1], mutant))
            miv.append(mirror_violation(vel[t], mutant))
        series[mutant] = {"np": npv, "cons": cov, "mir": miv}

    base_mir = _median(series["baseline"]["mir"])

    detection = []
    for mutant in MUTANTS:
        if mutant in NOT_APPLICABLE:
            detection.append({
                "mutant": mutant, "fault_class": FAULT_CLASS[mutant],
                "applicable": False, "not_applicable_reason": NOT_APPLICABLE[mutant],
            })
            continue
        s = series[mutant]
        np_med, cons_med, mir_med = _median(s["np"]), _median(s["cons"]), _median(s["mir"])
        mir_rel = abs(mir_med - base_mir) / base_mir if base_mir else float("inf")
        # per-frame detection fractions (frame-robustness)
        np_frac = float(np.mean([v > NODE_PERM_TOL for v in s["np"]]))
        cons_frac = float(np.mean([v > CONSERVATION_RATIO_TOL for v in s["cons"]]))
        mir_frac = float(np.mean([
            (abs(v - base_mir) / base_mir if base_mir else float("inf")) > MIRROR_Y_REL_CHANGE_TOL
            for v in s["mir"]]))
        npd, consd, mird = np_med > NODE_PERM_TOL, cons_med > CONSERVATION_RATIO_TOL, mir_rel > MIRROR_Y_REL_CHANGE_TOL
        detection.append({
            "mutant": mutant, "fault_class": FAULT_CLASS[mutant], "applicable": True,
            "node_perm_relative_l2_median": np_med,
            "conservation_ratio_median": cons_med,
            "mirror_y_violation_median": mir_med,
            "mirror_y_relative_change_from_baseline": mir_rel,
            "node_permutation_MR_detects": bool(npd),
            "conservation_MR_detects": bool(consd),
            "mirror_y_MR_detects": bool(mird),
            "detected_by_any": bool(npd or consd or mird),
            "frame_detection_fraction": {"node_permutation": np_frac,
                                         "conservation": cons_frac, "mirror_y": mir_frac},
        })

    applied = [d for d in detection if d.get("applicable")]
    n = len(applied)
    detected = [d for d in applied if d["detected_by_any"]]

    def _rate(key):
        return sum(d[key] for d in applied) / n if n else 0.0

    def _classes(key):
        return sorted({d["fault_class"] for d in applied if d[key]})

    mgn = json.loads(MGN_REF.read_text(encoding="utf-8")) if MGN_REF.exists() else {}
    mgn_sum = mgn.get("summary", {})

    summary = {
        "num_mutants_total": len(MUTANTS),
        "num_applicable_mutants": n,
        "num_not_applicable_mutants": len(NOT_APPLICABLE),
        "not_applicable_mutants": sorted(NOT_APPLICABLE),
        "node_permutation_MR_detection_rate": _rate("node_permutation_MR_detects"),
        "conservation_MR_detection_rate": _rate("conservation_MR_detects"),
        "mirror_y_MR_detection_rate": _rate("mirror_y_MR_detects"),
        "union_detection_rate": len(detected) / n if n else 0.0,
        "union_detected_count_over_applicable": [len(detected), n],
        "union_detection_rate_wilson_ci95": _wilson(len(detected), n),
        "fault_classes_localized_by_node_permutation": _classes("node_permutation_MR_detects"),
        "fault_classes_localized_by_conservation": _classes("conservation_MR_detects"),
        "fault_classes_localized_by_mirror_y": _classes("mirror_y_MR_detects"),
    }

    comparison_to_mgn = {
        "mgn_ledger": str(MGN_REF.relative_to(ROOT)),
        "mgn_union_detection_rate_over_10": mgn_sum.get("union_detection_rate"),
        "mgn_by_class_conservation": mgn_sum.get("fault_classes_localized_by_conservation"),
        "mgn_by_class_mirror_y": mgn_sum.get("fault_classes_localized_by_mirror_y"),
        "pointmlp_union_detection_rate_over_applicable": summary["union_detection_rate"],
        "pointmlp_by_class_conservation": summary["fault_classes_localized_by_conservation"],
        "pointmlp_by_class_mirror_y": summary["fault_classes_localized_by_mirror_y"],
        "node_permutation_zero_on_both": (
            summary["node_permutation_MR_detection_rate"] == 0.0
            and mgn_sum.get("node_permutation_MR_detection_rate") == 0.0),
        "interpretation": (
            "The mesh-adjacency fault class exists only for the message-passing MGN; on the "
            "row-wise PointMLP it is a no-op, so the fault surface differs by architecture. "
            "Among the eight applicable mutants the by-class localization (conservation to "
            "boundary/scale faults, mirror-y to physical-channel faults, node-permutation to "
            "none) is compared with the MGN result above; agreement REPRODUCES the pattern "
            "across two architecture families, it does not prove it generalizes."),
    }

    ledger = {
        "ledger_id": "pointmlp-cylinder-seeded-fault-detection",
        "evidence_level": "different-architecture-cylinder-flow-seeded-fault-detection",
        "schema_version": "0.1.0",
        "sut_id": "pointmlp-cylinder-sut-v1",
        "architecture_family": "PointMLP row-wise coordinate network (no message passing)",
        "checkpoint_path": str(CKPT.relative_to(ROOT)),
        "checkpoint_sha256": _sha256(CKPT),
        "rollout_convergence": {
            "median_relative_l2": 0.02975835263724644, "max_relative_l2": 0.09275380284264478,
            "source": "research_assets/runs/pointmlp-cylinder-primary-workflow/pointmlp_cylinder_primary_workflow_report.json",
            "note": "converged SUT (iron rule: comparisons only on converged SUTs)"},
        "fault_taxonomy_source": ("same 10-mutant five-class catalogue as the MGN runner "
                                  "tools/run_seeded_fault_detection.py (re-implemented from "
                                  "read-only Minimum-MR-SubSet witness_stage_b.py)"),
        "thresholds_aligned_to_mgn": True,
        "detectors": {
            "node_permutation_equivariance": {"class": "representation MR", "tolerance": NODE_PERM_TOL},
            "conservation_divergence": {"class": "continuity MR",
                                        "reference_relative_regression_threshold": CONSERVATION_RATIO_TOL},
            "mirror_y_ood_stress": {"class": "geometric/symmetry MR",
                                    "baseline_violation": base_mir,
                                    "relative_change_detection_threshold": MIRROR_Y_REL_CHANGE_TOL},
        },
        "num_frames": len(frames),
        "baseline": {
            "node_perm_relative_l2_median": _median(series["baseline"]["np"]),
            "conservation_ratio_median": _median(series["baseline"]["cons"]),
            "mirror_y_violation_median": base_mir,
        },
        "not_applicable_mutants": NOT_APPLICABLE,
        "detection_matrix": detection,
        "summary": summary,
        "comparison_to_mgn": comparison_to_mgn,
        "claim_limitations": (
            "One converged SUT, one checkpoint, one eval trajectory, the same injected-fault "
            "catalogue (eight applicable mutants on a row-wise architecture). Detection rates "
            "are for this mutant set only; not a real-world fault-detection rate, reliability, "
            "baseline-superiority, or proof of cross-architecture generalization (at most a "
            "reproduction across two architecture families)."),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return ledger


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "research_assets/runs/pointmlp-cylinder-seeded-fault-detection"))
    args = ap.parse_args(argv)
    outdir = Path(args.out)
    (outdir / "raw").mkdir(parents=True, exist_ok=True)
    led = run()
    (outdir / "raw" / "metric_ledger.json").write_text(
        json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    s = led["summary"]
    print(f"PointMLP seeded-fault detection over {s['num_applicable_mutants']} applicable "
          f"mutants ({s['num_not_applicable_mutants']} not-applicable: "
          f"{', '.join(s['not_applicable_mutants'])}):")
    print(f"  node-perm {s['node_permutation_MR_detection_rate']:.0%}, "
          f"conservation {s['conservation_MR_detection_rate']:.0%}, "
          f"mirror-y {s['mirror_y_MR_detection_rate']:.0%}, "
          f"union {s['union_detection_rate']:.0%} "
          f"(Wilson95 {s['union_detection_rate_wilson_ci95']})")
    for d in led["detection_matrix"]:
        if not d.get("applicable"):
            print(f"  [N/A ] {d['mutant']:18s} {d['fault_class']:24s} ({d['not_applicable_reason']})")
            continue
        flag = "DET" if d["detected_by_any"] else "miss"
        print(f"  [{flag}] {d['mutant']:18s} {d['fault_class']:24s} "
              f"np={d['node_perm_relative_l2_median']:.4f} "
              f"cons={d['conservation_ratio_median']:.3f} "
              f"mirΔ={d['mirror_y_relative_change_from_baseline']:.3f}")
    c = led["comparison_to_mgn"]
    print(f"  vs MGN: PointMLP union {s['union_detection_rate']:.0%}/applicable, "
          f"MGN {c['mgn_union_detection_rate_over_10']:.0%}/10; "
          f"node-perm 0 on both: {c['node_permutation_zero_on_both']}")
    print(f"wrote {outdir/'raw'/'metric_ledger.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
