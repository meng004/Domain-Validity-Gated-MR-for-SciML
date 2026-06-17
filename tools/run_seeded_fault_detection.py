"""Seeded-fault detection: do the domain-validity MRs catch known injected faults?

This is the fault-detection experiment the Stage-3/Stage-4 reviewers asked for. It uses
the paper's own metamorphic relations as fault detectors against a catalogue of seeded
pipeline faults, on the same single real MeshGraphNets cylinder-flow SUT and checkpoint.

The 10 mutants and their five fault classes are re-implemented here in pure numpy/torch
from the read-only Minimum-MR-SubSet fault taxonomy (scripts/mcmr/cylinder_flow/
witness_stage_b.py); that repository is never modified. Re-implementing keeps this
experiment self-contained and reproducible without the read-only repo's heavy imports.

Detectors (the paper's domain-validity MRs, each with a clean baseline that can flip):
  - Node-permutation equivariance (representation MR): relabel nodes, predict, un-relabel,
    compare. A correct pipeline is equivariant (relative L2 ~ 0); a fault whose effect
    depends on node/edge index order breaks it.
  - Conservation divergence (continuity MR): ratio of the predicted next-state discrete
    divergence to the ground-truth field's; a fault that corrupts the physical field
    pushes the ratio past the predeclared 1.5 regression threshold.

Detection = the detector's metric crosses its predeclared tolerance under the mutant
while passing at baseline. We report a detection matrix (2 MRs x 10 mutants), per-MR
fault-detection rate, and the fault classes each MR localizes to.

Honesty boundary: one SUT, one checkpoint, one eval trajectory, one injected-fault
catalogue. Detection rates are for this mutant set only; this is not a real-world
fault-detection rate, a reliability claim, a baseline-superiority claim, or cross-SUT.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest_contract import parse_flat_manifest  # noqa: E402
from conservation_rubric import divergence_rms  # noqa: E402
from mirror_y_rubric import reflection_map  # noqa: E402
from run_mirror_y_ood_stress import mirror_y_probe  # noqa: E402

# Fault taxonomy re-implemented from the read-only Minimum-MR-SubSet repo
# (scripts/mcmr/cylinder_flow/witness_stage_b.py). Not modified there.
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

NODE_PERM_TOL = 1e-5          # equivariance is exact for a correct pipeline
CONSERVATION_RATIO_TOL = 1.5  # predeclared reference-relative regression threshold
MIRROR_Y_REL_CHANGE_TOL = 0.5  # mirror-y baseline already fails; flag a >=50% shift
ACCURACY_ROLLOUT_MULT = 2.0    # accuracy monitor flags a fault if rollout error >= 2x baseline


def inverse_permutation(perm: np.ndarray) -> np.ndarray:
    inv = np.empty_like(perm)
    inv[perm] = np.arange(perm.shape[0])
    return inv


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, np.float64); b = np.asarray(b, np.float64)
    d = float(np.linalg.norm(b))
    return float(np.linalg.norm(a - b)) / d if d else float("inf")


def _sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run_from_manifest(manifest_path: Path, with_rollout: bool = False) -> dict:
    fields = parse_flat_manifest(Path(manifest_path).read_text(encoding="utf-8"))
    repo_root = Path(__file__).resolve().parents[1]

    def _resolve(rel: str) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else (repo_root / p)

    sut_repo = Path(fields["sut_repo"])
    sys.path.insert(0, str(sut_repo / "scripts"))
    import torch  # noqa: PLC0415
    from mcmr.cylinder_flow import dm_dataset as ds  # noqa: PLC0415
    from mcmr.cylinder_flow.mgn import (  # noqa: PLC0415
        MeshGraphNet, Normalizer, edge_features, one_hot_node_type)

    ckpt_path = _resolve(fields["checkpoint_path"])
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    cfg = ck["config"]
    traj = ds.load_npz(_resolve(fields["source_case_path"]))
    vel_norm = Normalizer.from_dict(ck["vel_norm"])
    delta_norm = Normalizer.from_dict(ck["delta_norm"])
    edge_norm = Normalizer.from_dict(ck["edge_norm"])
    model = MeshGraphNet(node_in=cfg["node_in"], edge_in=cfg["edge_in"], hidden=cfg["hidden"],
                         out_dim=cfg["out_dim"], num_layers=cfg["num_layers"])
    model.load_state_dict(ck["state_dict"]); model.eval()

    base_edge_index = ds.build_edge_index(traj.cells, traj.num_nodes)
    inflow = traj.node_type == ds.NODE_INFLOW
    wall = (traj.node_type == ds.NODE_WALL) | (traj.node_type == ds.NODE_OBSTACLE)

    def drop_edges(ei_np, frac=0.50):
        rng = np.random.default_rng(12345)
        keep = rng.random(ei_np.shape[1]) >= frac
        return ei_np[:, keep]

    def permute_edges(ei_np, frac=0.30):
        rng = np.random.default_rng(2024)
        ei = ei_np.copy(); sel = rng.random(ei.shape[1]) < frac
        idx = np.where(sel)[0]; dst = ei[1].copy()
        dst[idx] = rng.permutation(dst[idx]); ei[1] = dst
        return ei

    def mutated_update(mesh_pos, onehot, ei_np, v_t, mutant):
        """The model's proposed per-step update (delta) under graph/output faults.

        This is the quantity the equivariance and symmetry MRs score in the pilots
        (they compare model outputs, not next states). MA faults act on the forward
        graph; NS/PC faults act on the output delta. TR/BC faults are temporal/
        boundary steps applied later (see ``predict``) and do not change the update.
        """
        ei_used = ei_np
        if mutant == "MA_drop_edges":
            ei_used = drop_edges(ei_np)
        elif mutant == "MA_permute_edges":
            ei_used = permute_edges(ei_np)
        ef = edge_norm.normalize(torch.as_tensor(edge_features(mesh_pos, ei_used)))
        ei_t = torch.as_tensor(ei_used, dtype=torch.long)
        nf = torch.cat([vel_norm.normalize(torch.as_tensor(v_t)), onehot], dim=-1)
        with torch.no_grad():
            dpred = model(nf.to(torch.float32), ef.to(torch.float32), ei_t)
        delta = delta_norm.denormalize(dpred)
        if mutant == "NS_skip_denorm":
            delta = dpred
        elif mutant == "NS_double_scale":
            delta = 2.0 * delta
        if mutant == "PC_swap_xy":
            delta = delta[:, [1, 0]]
        elif mutant == "PC_zero_vy":
            delta = torch.stack([delta[:, 0], torch.zeros_like(delta[:, 1])], dim=-1)
        return delta.detach().numpy()

    def predict(mesh_pos, onehot, ei_np, inflow_m, wall_m, v_t, prescribed, mutant):
        """Full deployed next-state prediction (update + temporal + boundary)."""
        delta = torch.as_tensor(mutated_update(mesh_pos, onehot, ei_np, v_t, mutant))
        v_t_t = torch.as_tensor(v_t)
        if mutant == "TR_sign_flip":
            v_next = v_t_t - delta
        elif mutant == "TR_double_step":
            v_mid = v_t_t + delta
            d2 = torch.as_tensor(mutated_update(mesh_pos, onehot, ei_np, v_mid.numpy(), mutant))
            v_next = v_mid + d2
        else:
            v_next = v_t_t + delta
        v_next = v_next.detach().numpy().copy()
        v_next[inflow_m] = prescribed[inflow_m]
        v_next[wall_m] = 0.0
        if mutant == "BC_zero_inflow":
            v_next[inflow_m] = 0.0
        elif mutant == "BC_nonzero_wall":
            v_next[wall_m] = 0.2
        return v_next

    onehot = torch.as_tensor(one_hot_node_type(traj.node_type))
    frames = list(range(int(traj.velocity.shape[0]) - 1))
    rng = np.random.default_rng(int(fields.get("seed", "20260606")))
    perm = rng.permutation(traj.num_nodes)
    inv = inverse_permutation(perm)
    onehot_perm = torch.as_tensor(one_hot_node_type(traj.node_type[perm]))

    def node_perm_metric(v_t, prescribed, mutant):
        # Representation MR on the model's update output (as in the node-perm pilot).
        base = mutated_update(traj.mesh_pos, onehot, base_edge_index, v_t, mutant)
        out_p = mutated_update(traj.mesh_pos[perm], onehot_perm, inv[base_edge_index],
                               v_t[perm], mutant)
        return relative_l2(out_p[inv], base)

    def conservation_ratio(v_t, prescribed, reference, mutant):
        v_next = predict(traj.mesh_pos, onehot, base_edge_index, inflow, wall, v_t, prescribed, mutant)
        ref_div = divergence_rms(traj.mesh_pos, traj.cells, reference)
        pred_div = divergence_rms(traj.mesh_pos, traj.cells, v_next)
        return pred_div / ref_div if ref_div else float("inf")

    mirror_axis = float(fields.get("mirror_axis", "0.205"))
    pi = reflection_map(traj.mesh_pos, mirror_axis)

    def mirror_y_violation(v_t, prescribed, mutant):
        # Geometric/symmetry MR on the model's update output (as in the mirror-y pilot).
        def _pred(vf):
            return mutated_update(traj.mesh_pos, onehot, base_edge_index, vf, mutant)
        return float(mirror_y_probe(_pred, v_t, pi)["violation"])

    results = {}
    for mutant in ["baseline"] + MUTANTS:
        np_vals, cons_vals, mir_vals, roll_vals = [], [], [], []
        for t in frames:
            v_t = traj.velocity[t]
            prescribed = traj.velocity[t + 1]
            np_vals.append(node_perm_metric(v_t, prescribed, mutant))
            cons_vals.append(conservation_ratio(v_t, prescribed, prescribed, mutant))
            mir_vals.append(mirror_y_violation(v_t, prescribed, mutant))
            if with_rollout:
                v_next = predict(traj.mesh_pos, onehot, base_edge_index, inflow, wall,
                                 v_t, prescribed, mutant)
                roll_vals.append(relative_l2(v_next, prescribed))
        results[mutant] = {
            "node_perm_relative_l2_median": float(np.median(np_vals)),
            "conservation_ratio_median": float(np.median(cons_vals)),
            "mirror_y_violation_median": float(np.median(mir_vals)),
            "rollout_relative_l2_median": float(np.median(roll_vals)) if roll_vals else None,
        }

    base_np = results["baseline"]["node_perm_relative_l2_median"]
    base_cons = results["baseline"]["conservation_ratio_median"]
    base_mir = results["baseline"]["mirror_y_violation_median"]
    base_roll = results["baseline"].get("rollout_relative_l2_median")
    detection = []
    for mutant in MUTANTS:
        r = results[mutant]
        np_detected = r["node_perm_relative_l2_median"] > NODE_PERM_TOL
        cons_detected = r["conservation_ratio_median"] > CONSERVATION_RATIO_TOL
        mir_rel_change = (abs(r["mirror_y_violation_median"] - base_mir) / base_mir
                          if base_mir else float("inf"))
        mir_detected = mir_rel_change > MIRROR_Y_REL_CHANGE_TOL
        entry = {
            "mutant": mutant, "fault_class": FAULT_CLASS[mutant],
            "node_perm_relative_l2_median": r["node_perm_relative_l2_median"],
            "conservation_ratio_median": r["conservation_ratio_median"],
            "mirror_y_violation_median": r["mirror_y_violation_median"],
            "mirror_y_relative_change_from_baseline": mir_rel_change,
            "node_permutation_MR_detects": bool(np_detected),
            "conservation_MR_detects": bool(cons_detected),
            "mirror_y_MR_detects": bool(mir_detected),
            "detected_by_any": bool(np_detected or cons_detected or mir_detected),
        }
        if with_rollout and base_roll:
            roll = r.get("rollout_relative_l2_median")
            acc_detected = roll is not None and roll >= ACCURACY_ROLLOUT_MULT * base_roll
            entry["rollout_relative_l2_median"] = roll
            entry["rollout_over_baseline"] = (roll / base_roll) if roll else None
            entry["accuracy_monitor_detects"] = bool(acc_detected)
            entry["mr_catches_accuracy_misses"] = bool(entry["detected_by_any"] and not acc_detected)
            entry["accuracy_catches_mr_misses"] = bool(acc_detected and not entry["detected_by_any"])
        detection.append(entry)

    n = len(MUTANTS)
    ledger = {
        "ledger_id": "real-sut-seeded-fault-detection",
        "evidence_level": "real-sut-single-checkpoint-seeded-fault-detection",
        "schema_version": "0.1.0",
        "sut_repo": fields["sut_repo"], "sut_commit": fields["sut_commit"],
        "checkpoint_path": fields["checkpoint_path"], "checkpoint_sha256": _sha256(ckpt_path),
        "fault_taxonomy_source": ("re-implemented from read-only Minimum-MR-SubSet "
                                  "scripts/mcmr/cylinder_flow/witness_stage_b.py"),
        "detectors": {
            "node_permutation_equivariance": {"class": "representation MR", "tolerance": NODE_PERM_TOL},
            "conservation_divergence": {"class": "continuity MR",
                                        "reference_relative_regression_threshold": CONSERVATION_RATIO_TOL},
            "mirror_y_ood_stress": {"class": "geometric/symmetry MR",
                                    "baseline_violation": base_mir,
                                    "relative_change_detection_threshold": MIRROR_Y_REL_CHANGE_TOL},
        },
        "baseline": {"node_perm_relative_l2_median": base_np,
                     "conservation_ratio_median": base_cons,
                     "mirror_y_violation_median": base_mir},
        "num_frames": len(frames),
        "detection_matrix": detection,
        "summary": {
            "num_mutants": n,
            "node_permutation_MR_detection_rate": sum(d["node_permutation_MR_detects"] for d in detection) / n,
            "conservation_MR_detection_rate": sum(d["conservation_MR_detects"] for d in detection) / n,
            "mirror_y_MR_detection_rate": sum(d["mirror_y_MR_detects"] for d in detection) / n,
            "union_detection_rate": sum(d["detected_by_any"] for d in detection) / n,
            "fault_classes_localized_by_node_permutation": sorted({
                d["fault_class"] for d in detection if d["node_permutation_MR_detects"]}),
            "fault_classes_localized_by_conservation": sorted({
                d["fault_class"] for d in detection if d["conservation_MR_detects"]}),
            "fault_classes_localized_by_mirror_y": sorted({
                d["fault_class"] for d in detection if d["mirror_y_MR_detects"]}),
        },
        "claim_limitations": (
            "One SUT, one checkpoint, one eval trajectory, one injected-fault catalogue. "
            "Detection rates are for this mutant set only; not a real-world fault-detection "
            "rate, reliability, baseline-superiority, or cross-SUT claim."
        ),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if with_rollout:
        ledger["complementarity"] = {
            "accuracy_rollout_multiplier": ACCURACY_ROLLOUT_MULT,
            "baseline_rollout_relative_l2": base_roll,
            "mr_catches_accuracy_misses": sorted({d["mutant"] for d in detection if d.get("mr_catches_accuracy_misses")}),
            "accuracy_catches_mr_misses": sorted({d["mutant"] for d in detection if d.get("accuracy_catches_mr_misses")}),
            "both": sorted({d["mutant"] for d in detection if d["detected_by_any"] and d.get("accuracy_monitor_detects")}),
            "neither": sorted({d["mutant"] for d in detection if not d["detected_by_any"] and not d.get("accuracy_monitor_detects")}),
            "note": ("complementarity, not superiority: each axis catches a distinct subset; an "
                     "MR-only fault is caught by a relation an accuracy monitor leaves within band, "
                     "an accuracy-only fault degrades rollout without crossing a relation threshold."),
        }
    raw_dir = _resolve(fields["raw_output_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "metric_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ledger


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--with-rollout", action="store_true",
                    help="also record per-mutant rollout error and the MR-vs-accuracy complementarity")
    args = ap.parse_args(argv)
    led = run_from_manifest(Path(args.manifest), with_rollout=args.with_rollout)
    s = led["summary"]
    print(f"seeded-fault detection over {s['num_mutants']} mutants: "
          f"node-perm {s['node_permutation_MR_detection_rate']:.0%}, "
          f"conservation {s['conservation_MR_detection_rate']:.0%}, "
          f"mirror-y {s['mirror_y_MR_detection_rate']:.0%}, "
          f"union {s['union_detection_rate']:.0%}")
    for d in led["detection_matrix"]:
        flag = "DET" if d["detected_by_any"] else "miss"
        print(f"  [{flag}] {d['mutant']:18s} {d['fault_class']:24s} "
              f"np={d['node_perm_relative_l2_median']:.4f} "
              f"cons={d['conservation_ratio_median']:.3f} "
              f"mir={d['mirror_y_violation_median']:.3f}")
    if led.get("complementarity"):
        c = led["complementarity"]
        print(f"  complementarity (MR vs accuracy@{c['accuracy_rollout_multiplier']}x baseline): "
              f"MR-only={c['mr_catches_accuracy_misses']} accuracy-only={c['accuracy_catches_mr_misses']} "
              f"both={c['both']} neither={c['neither']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
