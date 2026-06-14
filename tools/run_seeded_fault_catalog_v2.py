"""Expanded seeded-fault catalogue (B1) plus a real production-bug witness (B2).

Reviewer concern (every v22--v25 panel): the 10-mutant catalogue is small and the
faults are gross corruptions any divergence/symmetry check would catch. This tool
extends the real-SUT fault battery with realistic, graded engineering faults that
mimic genuine MeshGraphNet implementation mistakes, and adds a documented real bug
found in NVIDIA PhysicsNeMo production code during this study.

B1 -- realistic engineering faults injected into the real MeshGraphNet forward pass
(same SUT, checkpoint, eval trajectory, and three domain-validity MR detectors as
tools/run_seeded_fault_detection.py):
  * MA_self_loops          spurious self-loops added to the mesh graph
  * MA_missing_reverse     reverse half-edges dropped (directed/undirected confusion)
  * EF_abs_position        absolute node positions used as edge features (should be relative)
  * NS_skip_edge_norm      edge features fed unnormalized (forgot edge normalizer)
  * NS_no_input_norm       input velocity fed unnormalized
  * NS_half_denorm         output under-denormalized (half the delta scale)
  * PC_vx_sign             sign of the x-velocity update flipped (coordinate-frame bug)
  * PC_scale_vx            x-velocity update scaled 2x (anisotropic scale bug)
  * TR_half_step           update applied at half magnitude (wrong timestep)
  * TR_frozen              next state frozen to current (update dropped)

B2 -- real production bug witness:
  * REAL_graph_cache       the documented PhysicsNeMo VortexSheddingDataset.__getitem__
                           in-place graph-mutation bug (paper/37): a stale cached graph is
                           reused for the follow-up execution, breaking node-permutation
                           equivariance. Found and fixed during the scaled-workflow bring-up;
                           reconstructed here as an injectable real-SUT fault.

Detection = a detector's metric crosses its predeclared tolerance under the fault while
passing at baseline. Per-detector detection over the catalogue carries a Wilson 95% CI.

Honesty boundary: one SUT, one checkpoint, one eval trajectory. The realistic faults are
hand-constructed (not mined mutation operators), and REAL_graph_cache reconstructs a
documented real bug's behavioural signature on this SUT. Detection rates are for this
catalogue only; not a real-world fault-detection rate, reliability, or cross-SUT claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest_contract import parse_flat_manifest  # noqa: E402
from conservation_rubric import divergence_rms  # noqa: E402
from mirror_y_rubric import reflection_map  # noqa: E402
from run_mirror_y_ood_stress import mirror_y_probe  # noqa: E402
from run_seeded_fault_detection import inverse_permutation, relative_l2  # noqa: E402

NODE_PERM_TOL = 1e-5
CONSERVATION_RATIO_TOL = 1.5
MIRROR_Y_REL_CHANGE_TOL = 0.5

NEW_FAULTS = {
    "MA_self_loops": "mesh_adjacency_fault",
    "MA_missing_reverse": "mesh_adjacency_fault",
    "EF_abs_position": "mesh_adjacency_fault",
    "NS_skip_edge_norm": "normalization_scale_fault",
    "NS_no_input_norm": "normalization_scale_fault",
    "NS_half_denorm": "normalization_scale_fault",
    "PC_vx_sign": "physical_channel_fault",
    "PC_scale_vx": "physical_channel_fault",
    "TR_half_step": "temporal_rollout_fault",
    "TR_frozen": "temporal_rollout_fault",
    "REAL_graph_cache": "representation_fault",
}
FAULT_REALISM = {
    "MA_self_loops": "graph-construction bug (self-loops)",
    "MA_missing_reverse": "directed/undirected edge confusion",
    "EF_abs_position": "absolute vs relative edge-feature bug",
    "NS_skip_edge_norm": "missing edge normalization",
    "NS_no_input_norm": "missing input normalization",
    "NS_half_denorm": "output denormalization scale error",
    "PC_vx_sign": "velocity-component sign / frame bug",
    "PC_scale_vx": "anisotropic output scale bug",
    "TR_half_step": "wrong integration timestep",
    "TR_frozen": "dropped state update",
    "REAL_graph_cache": "documented PhysicsNeMo in-place graph-mutation bug (paper/37)",
}


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [max(0.0, (c - h) / d), min(1.0, (c + h) / d)]


def _sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run_from_manifest(manifest_path: Path) -> dict:
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
    onehot = torch.as_tensor(one_hot_node_type(traj.node_type))

    def edge_feats(mesh_pos, ei, mutant):
        if mutant == "EF_abs_position":               # absolute src position, not relative
            src = ei[0]
            rel = mesh_pos[src]
            norm = np.linalg.norm(rel, axis=1, keepdims=True)
            raw = np.concatenate([rel, norm], axis=1).astype(np.float32)
        else:
            raw = edge_features(mesh_pos, ei)
        t = torch.as_tensor(raw)
        return t if mutant == "NS_skip_edge_norm" else edge_norm.normalize(t)

    def mutate_graph(ei, mutant):
        if mutant == "MA_self_loops":
            n = traj.num_nodes
            loops = np.stack([np.arange(n), np.arange(n)])
            return np.concatenate([ei, loops], axis=1)
        if mutant == "MA_missing_reverse":
            keep = ei[0] < ei[1]
            return ei[:, keep]
        return ei

    def raw_update(mesh_pos, onehot_local, ei, v_t, mutant):
        ei_used = mutate_graph(ei, mutant)
        ef = edge_feats(mesh_pos, ei_used, mutant)
        ei_t = torch.as_tensor(ei_used, dtype=torch.long)
        v_in = torch.as_tensor(v_t)
        v_in = v_in if mutant == "NS_no_input_norm" else vel_norm.normalize(v_in)
        nf = torch.cat([v_in, onehot_local], dim=-1)
        with torch.no_grad():
            dpred = model(nf.to(torch.float32), ef.to(torch.float32), ei_t)
        delta = delta_norm.denormalize(dpred)
        if mutant == "NS_half_denorm":
            delta = 0.5 * delta
        elif mutant == "PC_vx_sign":
            delta = torch.stack([-delta[:, 0], delta[:, 1]], dim=-1)
        elif mutant == "PC_scale_vx":
            delta = torch.stack([2.0 * delta[:, 0], delta[:, 1]], dim=-1)
        return delta.detach().numpy()

    def predict(v_t, prescribed, mutant):
        delta = torch.as_tensor(raw_update(traj.mesh_pos, onehot, base_edge_index, v_t, mutant))
        v_t_t = torch.as_tensor(v_t)
        if mutant == "TR_half_step":
            v_next = v_t_t + 0.5 * delta
        elif mutant == "TR_frozen":
            v_next = v_t_t
        else:
            v_next = v_t_t + delta
        v_next = v_next.detach().numpy().copy()
        v_next[inflow] = prescribed[inflow]
        v_next[wall] = 0.0
        return v_next

    rng = np.random.default_rng(int(fields.get("seed", "20260606")))
    perm = rng.permutation(traj.num_nodes)
    inv = inverse_permutation(perm)
    onehot_perm = torch.as_tensor(one_hot_node_type(traj.node_type[perm]))

    def node_perm_metric(v_t, mutant):
        base = raw_update(traj.mesh_pos, onehot, base_edge_index, v_t, mutant)
        if mutant == "REAL_graph_cache":
            # Real bug: the follow-up reuses the stale (unpermuted) cached graph
            # instead of the permuted one, exactly as the in-place __getitem__ mutation did.
            out_p = raw_update(traj.mesh_pos[perm], onehot_perm, base_edge_index, v_t[perm], mutant)
        else:
            out_p = raw_update(traj.mesh_pos[perm], onehot_perm, inv[base_edge_index], v_t[perm], mutant)
        return relative_l2(out_p[inv], base)

    mirror_axis = float(fields.get("mirror_axis", "0.205"))
    pi = reflection_map(traj.mesh_pos, mirror_axis)

    def mirror_metric(v_t, mutant):
        def _pred(vf):
            return raw_update(traj.mesh_pos, onehot, base_edge_index, vf, mutant)
        return float(mirror_y_probe(_pred, v_t, pi)["violation"])

    def cons_metric(v_t, prescribed, mutant):
        v_next = predict(v_t, prescribed, mutant)
        ref = divergence_rms(traj.mesh_pos, traj.cells, prescribed)
        pred = divergence_rms(traj.mesh_pos, traj.cells, v_next)
        return pred / ref if ref else float("inf")

    frames = list(range(int(traj.velocity.shape[0]) - 1))
    mutants = ["baseline"] + list(NEW_FAULTS)
    med = {}
    for m in mutants:
        npv, cv, mv = [], [], []
        for t in frames:
            v_t, presc = traj.velocity[t], traj.velocity[t + 1]
            npv.append(node_perm_metric(v_t, m))
            cv.append(cons_metric(v_t, presc, m))
            mv.append(mirror_metric(v_t, m))
        med[m] = (float(np.median(npv)), float(np.median(cv)), float(np.median(mv)))

    base_mir = med["baseline"][2]
    detection = []
    for m in NEW_FAULTS:
        npm, cm, mm = med[m]
        np_d = npm > NODE_PERM_TOL
        cons_d = cm > CONSERVATION_RATIO_TOL
        mir_change = abs(mm - base_mir) / base_mir if base_mir else float("inf")
        mir_d = mir_change > MIRROR_Y_REL_CHANGE_TOL
        detection.append({
            "mutant": m, "fault_class": NEW_FAULTS[m], "realism": FAULT_REALISM[m],
            "node_perm_relative_l2_median": npm, "conservation_ratio_median": cm,
            "mirror_y_violation_median": mm, "mirror_y_relative_change_from_baseline": mir_change,
            "node_permutation_MR_detects": bool(np_d),
            "conservation_MR_detects": bool(cons_d),
            "mirror_y_MR_detects": bool(mir_d),
            "detected_by_any": bool(np_d or cons_d or mir_d),
        })

    n = len(NEW_FAULTS)
    union_k = sum(d["detected_by_any"] for d in detection)
    by_class = {}
    for d in detection:
        c = d["fault_class"]
        by_class.setdefault(c, {"n": 0, "detected": 0})
        by_class[c]["n"] += 1
        by_class[c]["detected"] += int(d["detected_by_any"])

    real = next(d for d in detection if d["mutant"] == "REAL_graph_cache")
    ledger = {
        "ledger_id": "seeded-fault-catalog-v2",
        "schema_version": "0.1.0",
        "evidence_level": "real-sut-single-checkpoint-expanded-fault-catalogue",
        "experiment": "B1 realistic graded faults + B2 real production-bug witness",
        "sut_repo": fields["sut_repo"], "sut_commit": fields["sut_commit"],
        "checkpoint_sha256": _sha256(ckpt_path),
        "num_frames": len(frames),
        "detectors": {
            "node_permutation_equivariance": {"tolerance": NODE_PERM_TOL},
            "conservation_divergence": {"reference_relative_regression_threshold": CONSERVATION_RATIO_TOL},
            "mirror_y_ood_stress": {"baseline_violation": base_mir,
                                    "relative_change_detection_threshold": MIRROR_Y_REL_CHANGE_TOL},
        },
        "num_new_mutants": n,
        "detection_matrix": detection,
        "summary": {
            "union_detected": union_k, "union_rate": union_k / n,
            "union_rate_wilson95": wilson(union_k, n),
            "node_permutation_rate": sum(d["node_permutation_MR_detects"] for d in detection) / n,
            "conservation_rate": sum(d["conservation_MR_detects"] for d in detection) / n,
            "mirror_y_rate": sum(d["mirror_y_MR_detects"] for d in detection) / n,
            "by_class": {c: {**v, "rate": v["detected"] / v["n"]} for c, v in by_class.items()},
        },
        "real_bug_witness": {
            "mutant": "REAL_graph_cache",
            "source": "PhysicsNeMo VortexSheddingDataset.__getitem__ in-place graph mutation (paper/37_phase17_gate_closure_execution.md)",
            "detected_by_node_permutation": real["node_permutation_MR_detects"],
            "node_perm_relative_l2_median": real["node_perm_relative_l2_median"],
            "note": "A correct equivariant pipeline reads ~0; the stale-graph bug makes the node-permutation MR read non-zero, which is how the bug was caught during scaled-workflow bring-up.",
        },
        "combined_catalogue_size": {
            "original_canonical_mgn": 10, "adversarial_mgn": 2, "new_realistic_mgn": n - 1,
            "real_bug_witness": 1, "pinn_closed_form_probes": 24, "fno_closed_form_probes": 24,
            "total": 10 + 2 + (n - 1) + 1 + 24 + 24,
        },
        "claim_limitations": (
            "One SUT, one checkpoint, one eval trajectory. Realistic faults are hand-constructed; "
            "REAL_graph_cache reconstructs a documented real bug's signature. Detection rates are for "
            "this catalogue only; not a real-world rate, reliability, or cross-SUT claim."
        ),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    out_dir = _resolve(fields.get("raw_output_dir", "research_assets/runs/seeded-fault-catalog-v2/raw"))
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metric_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ledger


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True)
    args = ap.parse_args(argv)
    led = run_from_manifest(Path(args.manifest))
    s = led["summary"]
    print(f"expanded catalogue: {led['num_new_mutants']} new mutants, "
          f"union {s['union_detected']}/{led['num_new_mutants']} "
          f"({s['union_rate']:.0%}, Wilson95 [{s['union_rate_wilson95'][0]:.2f},{s['union_rate_wilson95'][1]:.2f}])")
    for d in led["detection_matrix"]:
        flag = "DET" if d["detected_by_any"] else "miss"
        print(f"  [{flag:4s}] {d['mutant']:18s} {d['fault_class']:26s} "
              f"np={d['node_perm_relative_l2_median']:.4f} cons={d['conservation_ratio_median']:.3f} "
              f"mir={d['mirror_y_violation_median']:.3f}")
    rw = led["real_bug_witness"]
    print(f"  REAL bug witness: node-perm detects={rw['detected_by_node_permutation']} "
          f"(rel L2 {rw['node_perm_relative_l2_median']:.4f})")
    print(f"  combined catalogue size: {led['combined_catalogue_size']['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
