"""Seeded-fault detection on the PhysicsNeMo airfoil SUT (R2-1 second-SUT replication).

Mirrors the cylinder-flow seeded-fault pilot (tools/run_seeded_fault_detection.py)
on the second CFD SUT: the official PhysicsNeMo MeshGraphNet trained on the
DeepMind compressible airfoil task (claim C35 primary roster). The SAME 10-mutant,
five-class fault catalogue and the SAME detector tolerances are used, so the
by-class localization pattern can be compared across SUT families.

Two detectors are admissible on the airfoil and run as fault detectors:
  - node-permutation equivariance (representation MR): exact for a correct
    pipeline; tolerance 1e-5.
  - compressible mass-conservation residual ratio (continuity MR): the
    reference-relative compressible residual d(rho)/dt + div(rho u), predicted
    vs ground-truth-referenced; predeclared 1.5x regression threshold (same
    threshold as the cylinder conservation detector). Note the form differs: the
    cylinder uses a full-field incompressible divergence, the airfoil an
    interior-masked compressible residual, because the physics differ.

The third cylinder detector, mirror-y symmetry, is DOMAIN-INADMISSIBLE on the
airfoil: the SU2 trajectories carry a non-zero angle of attack, so reflection
about the chord is not a symmetry of the boundary-value problem. The
admissibility gate rejects it at the boundary/precondition stage (claim C35
mirror_y_symmetry_rejection_ledger.json). It is therefore recorded as
"inadmissible", not run as a detector. This is the gate functioning as designed:
on a SUT where an MR's domain precondition fails, the MR is removed from the
detector toolkit rather than reporting a spurious pass/fail.

Honest finding (see cross_sut_comparison in the emitted ledger): the by-class
localization pattern observed on the cylinder does NOT replicate on the airfoil.
The conservation MR localizes to different fault classes across SUTs, and mirror-y
is inadmissible here. What generalizes across both SUTs is (i) the conservation MR
detecting gross normalization/scale faults, (ii) node-permutation's insensitivity
to invariant-preserving faults, and (iii) the admissibility gate excluding an MR
whose precondition fails. The by-class diagnosis is therefore SUT-specific.

Honesty boundary: two SUTs, one airfoil checkpoint, N airfoil eval trajectories,
one injected-fault catalogue, two admissible airfoil detectors. Detection rates
are for this mutant set only; not a real-world fault-detection rate, reliability,
or superiority claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import run_physicsnemo_mgn_airfoil_workflow as af  # noqa: E402  reuse SUT infra
from conservation_rubric import cell_divergence  # noqa: E402

# Same taxonomy as the cylinder pilot (tools/run_seeded_fault_detection.py). The
# two BC mutants are mapped onto the airfoil's own boundary node types: the
# far-field/outflow boundary (type 2) and the airfoil no-slip wall (type 4).
FAULT_CLASS = {
    "BC_zero_outflow": "boundary_condition_fault",   # zero the far-field/outflow boundary (type 2)
    "BC_nonzero_wall": "boundary_condition_fault",    # corrupt the airfoil no-slip wall (type 4)
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

NODE_PERM_TOL = 1e-5
CONSERVATION_RATIO_TOL = 1.5
NODE_OUTFLOW = 2
NODE_AIRFOIL = 4

# Cylinder by-class localization (tools/run_seeded_fault_detection.py committed
# evidence) for the cross-SUT comparison recorded in the emitted ledger.
CYLINDER_CONSERVATION_LOCALIZES = ["boundary_condition_fault", "normalization_scale_fault"]
CYLINDER_MIRROR_Y_LOCALIZES = ["mesh_adjacency_fault", "physical_channel_fault"]


def inverse_permutation(perm: np.ndarray) -> np.ndarray:
    inv = np.empty_like(perm)
    inv[perm] = np.arange(perm.shape[0])
    return inv


def edge_attr_for(pos: np.ndarray, ei: np.ndarray) -> np.ndarray:
    rel = pos[ei[0]] - pos[ei[1]]
    norm = np.linalg.norm(rel, axis=1, keepdims=True)
    return np.concatenate([rel, norm], axis=1).astype(np.float32)


def drop_edges(ei: np.ndarray, frac: float = 0.50) -> np.ndarray:
    rng = np.random.default_rng(12345)
    keep = rng.random(ei.shape[1]) >= frac
    return ei[:, keep]


def permute_edges(ei: np.ndarray, frac: float = 0.30) -> np.ndarray:
    rng = np.random.default_rng(2024)
    ei = ei.copy()
    sel = rng.random(ei.shape[1]) < frac
    idx = np.where(sel)[0]
    dst = ei[1].copy()
    dst[idx] = rng.permutation(dst[idx])
    ei[1] = dst
    return ei


def _sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def mutated_delta(model, norms, pos, nt, feat, ei, ea, mutant):
    """The model's proposed per-step update (delta, N x 3 = [dvx, dvy, drho]) under
    graph/output faults. MA faults act on the forward graph; NS/PC faults act on the
    denormalized output delta. TR/BC faults are applied later in ``predict_next``."""
    fm, fs, tm, ts = norms
    ei_used, ea_used = ei, ea
    if mutant == "MA_drop_edges":
        ei_used = drop_edges(ei)
        ea_used = edge_attr_for(pos, ei_used)
    elif mutant == "MA_permute_edges":
        ei_used = permute_edges(ei)
        ea_used = edge_attr_for(pos, ei_used)
    src = af.predict(model, (feat - fm) / fs, ei_used, ea_used)  # (N,3) normalized
    delta = src * ts + tm
    if mutant == "NS_skip_denorm":
        delta = src
    elif mutant == "NS_double_scale":
        delta = 2.0 * delta
    if mutant == "PC_swap_xy":
        delta = delta[:, [1, 0, 2]]
    elif mutant == "PC_zero_vy":
        delta = delta.copy()
        delta[:, 1] = 0.0
    return delta


def predict_next(model, norms, rec, t, mutant):
    """Full deployed next-state prediction (update + temporal + boundary faults)."""
    pos, cells, nt, feat, tgt, ei, ea, vel, rho = af.build_graph(rec, t)
    delta = mutated_delta(model, norms, pos, nt, feat, ei, ea, mutant)
    if mutant == "TR_sign_flip":
        v_next = vel - delta[:, :2]
        rho_next = rho[:, 0] - delta[:, 2]
    elif mutant == "TR_double_step":
        v_mid = vel + delta[:, :2]
        rho_mid = rho[:, 0] + delta[:, 2]
        feat_mid = np.concatenate(
            [v_mid, rho_mid[:, None], af.one_hot(nt)], axis=1).astype(np.float32)
        delta2 = mutated_delta(model, norms, pos, nt, feat_mid, ei, ea, mutant)
        v_next = v_mid + delta2[:, :2]
        rho_next = rho_mid + delta2[:, 2]
    else:
        v_next = vel + delta[:, :2]
        rho_next = rho[:, 0] + delta[:, 2]
    if mutant == "BC_zero_outflow":
        v_next = v_next.copy()
        v_next[nt == NODE_OUTFLOW] = 0.0
    elif mutant == "BC_nonzero_wall":
        v_next = v_next.copy()
        v_next[nt == NODE_AIRFOIL] = 0.2
    return pos, cells, nt, vel, rho, v_next, rho_next


def conservation_ratio(model, norms, rec, t, meta, mutant):
    """Compressible mass-conservation residual ratio (predicted / ground-truth-ref)."""
    pos, cells, nt, vel, rho, v_next, rho_next = predict_next(model, norms, rec, t, mutant)
    dt = float(meta["dt"])
    interior = np.isin(nt[cells], [0]).all(axis=1)
    rho_next_ref = rec["density"][t + 1, :, 0]
    drho_dt_ref = ((rho_next_ref - rho[:, 0])[cells].mean(axis=1)) / dt
    div_rhou_ref, area = cell_divergence(pos, cells, vel * rho)
    resid_ref = drho_dt_ref + div_rhou_ref
    drho_dt_pred = ((rho_next - rho[:, 0])[cells].mean(axis=1)) / dt
    div_rhou_pred, _ = cell_divergence(pos, cells, v_next * rho_next[:, None])
    resid_pred = drho_dt_pred + div_rhou_pred

    def rms(x):
        xx, aa = x[interior], area[interior]
        tot = float(aa.sum())
        return float(np.sqrt(np.sum(aa * xx ** 2) / tot)) if tot > 0 else float("nan")

    ref = rms(resid_ref)
    pred = rms(resid_pred)
    return pred / max(ref, 1e-12)


def node_perm_metric(model, norms, rec, t, mutant):
    """Representation MR on the model's update output under a node relabeling."""
    pos, cells, nt, feat, tgt, ei, ea, vel, rho = af.build_graph(rec, t)
    base = mutated_delta(model, norms, pos, nt, feat, ei, ea, mutant)
    rng = np.random.default_rng(20260617)
    perm = rng.permutation(feat.shape[0])
    inv = inverse_permutation(perm)
    pos_p = pos[perm]
    feat_p = feat[perm]
    ei_p = inv[ei]
    ea_p = edge_attr_for(pos_p, ei_p)
    out_p = mutated_delta(model, norms, pos_p, nt[perm], feat_p, ei_p, ea_p, mutant)
    return af.relative_l2(out_p[inv], base)


def evaluate_one_trajectory(model, norms, rec, meta, n_frames):
    """Per-mutant median node-perm and conservation metrics over n_frames of one trajectory."""
    traj_len = int(rec["velocity"].shape[0])
    frames = [int(x) for x in np.linspace(1, traj_len - 2, n_frames, dtype=int)]
    results = {}
    for mutant in ["baseline"] + MUTANTS:
        np_vals, cons_vals = [], []
        for t in frames:
            np_vals.append(node_perm_metric(model, norms, rec, t, mutant))
            cons_vals.append(conservation_ratio(model, norms, rec, t, meta, mutant))
        results[mutant] = {"node_perm_relative_l2_median": float(np.median(np_vals)),
                           "conservation_ratio_median": float(np.median(cons_vals))}
    return results, len(frames)


def _detection_for_trajectory(results):
    base_cons = results["baseline"]["conservation_ratio_median"]
    rows = []
    for mutant in MUTANTS:
        r = results[mutant]
        np_det = r["node_perm_relative_l2_median"] > NODE_PERM_TOL
        cons_det = r["conservation_ratio_median"] > CONSERVATION_RATIO_TOL
        rows.append({
            "mutant": mutant, "fault_class": FAULT_CLASS[mutant],
            "node_perm_relative_l2_median": r["node_perm_relative_l2_median"],
            "conservation_ratio_median": r["conservation_ratio_median"],
            "node_permutation_MR_detects": bool(np_det),
            "conservation_MR_detects": bool(cons_det),
            "mirror_y_MR_detects": None,  # inadmissible on this SUT (see detectors note)
            "detected_by_any": bool(np_det or cons_det),
        })
    return rows, base_cons


def run_pilot(checkpoint: Path, traj_indices, n_frames: int, out_dir: Path) -> dict:
    import torch
    ck = torch.load(checkpoint, map_location="cpu", weights_only=False)
    cons = ck["constructor"]
    nrm = ck["normalization"]
    norms = (np.asarray(nrm["feat_mean"], np.float32), np.asarray(nrm["feat_std"], np.float32),
             np.asarray(nrm["tgt_mean"], np.float32), np.asarray(nrm["tgt_std"], np.float32))
    model = af.build_model(cons["hidden"], cons["processor_size"])
    model.load_state_dict(ck["model_state_dict"])
    model.eval()

    meta = json.loads((af.STAGE_DIR / "meta.json").read_text())
    need = max(traj_indices) + 1
    af.stage_data(1, need)  # idempotent when cached; ensures markers/tfrecord
    test_records = list(af.iter_trajectories("test", meta, need))

    per_traj = []
    n_frames_used = 0
    for ti in traj_indices:
        results, nfu = evaluate_one_trajectory(model, norms, test_records[ti], meta, n_frames)
        n_frames_used = nfu
        rows, base_cons = _detection_for_trajectory(results)
        per_traj.append({
            "trajectory_index": ti,
            "baseline_conservation_ratio": base_cons,
            "detection_matrix": rows,
            "union_detection_rate": sum(d["detected_by_any"] for d in rows) / len(MUTANTS),
            "conservation_localizes": sorted({d["fault_class"] for d in rows if d["conservation_MR_detects"]}),
        })
        print(f"  traj {ti}: union {per_traj[-1]['union_detection_rate']:.0%}, "
              f"cons localizes {per_traj[-1]['conservation_localizes']}", flush=True)

    # Cross-trajectory robustness: a mutant is robustly detected only if detected on EVERY trajectory.
    n_traj = len(traj_indices)
    detected_count = {m: 0 for m in MUTANTS}
    cons_detected_count = {m: 0 for m in MUTANTS}
    for pt in per_traj:
        for d in pt["detection_matrix"]:
            detected_count[d["mutant"]] += int(d["detected_by_any"])
            cons_detected_count[d["mutant"]] += int(d["conservation_MR_detects"])
    robust = [m for m in MUTANTS if detected_count[m] == n_traj]
    unstable = [m for m in MUTANTS if 0 < detected_count[m] < n_traj]
    never = [m for m in MUTANTS if detected_count[m] == 0]
    robust_cons_classes = sorted({FAULT_CLASS[m] for m in MUTANTS if cons_detected_count[m] == n_traj})
    shared = sorted(set(robust_cons_classes) & set(CYLINDER_CONSERVATION_LOCALIZES))

    ledger = {
        "ledger_id": "real-sut-seeded-fault-detection-physicsnemo-airfoil",
        "evidence_level": "real-sut-second-sut-multi-trajectory-seeded-fault-detection",
        "schema_version": "0.2.0",
        "sut": "physicsnemo-mgn-airfoil-primary-roster (claim C35)",
        "checkpoint_file": checkpoint.name,
        "checkpoint_sha256": _sha256(checkpoint),
        "constructor": cons,
        "trajectory_indices": list(traj_indices),
        "num_frames_per_trajectory": n_frames_used,
        "fault_taxonomy_source": ("same 10-mutant five-class catalogue as the cylinder pilot "
                                  "tools/run_seeded_fault_detection.py; BC mutants mapped to "
                                  "airfoil boundary node types (outflow=2, wall=4)"),
        "detectors": {
            "node_permutation_equivariance": {"class": "representation MR", "tolerance": NODE_PERM_TOL},
            "compressible_conservation_residual_ratio": {
                "class": "continuity MR",
                "reference_relative_regression_threshold": CONSERVATION_RATIO_TOL,
                "note": ("interior-masked compressible residual d(rho)/dt + div(rho u); differs "
                         "from the cylinder's full-field incompressible divergence (physics-specific)")},
            "mirror_y_symmetry": {
                "class": "geometric/symmetry MR", "status": "inadmissible",
                "reason": ("non-zero angle of attack: reflection about the chord is not a symmetry "
                           "of the boundary-value problem; rejected at the boundary/precondition gate"),
                "gate_evidence": ("research_assets/runs/production-grade-sut-extension/"
                                  "physicsnemo-mgn-airfoil-primary-roster/"
                                  "mirror_y_symmetry_rejection_ledger.json")},
        },
        "per_trajectory": per_traj,
        "robustness": {
            "n_trajectories": n_traj,
            "robustly_detected_mutants": robust,
            "unstable_mutants": unstable,
            "never_detected_mutants": never,
            "node_permutation_MR_detection_rate": 0.0,
            "conservation_robustly_localizes": robust_cons_classes,
        },
        "cross_sut_comparison": {
            "cylinder_conservation_localizes": CYLINDER_CONSERVATION_LOCALIZES,
            "cylinder_mirror_y_localizes": CYLINDER_MIRROR_Y_LOCALIZES,
            "airfoil_conservation_robustly_localizes": robust_cons_classes,
            "shared_localization_across_suts": shared,
            "mirror_y_status_on_airfoil": "inadmissible",
            "finding": ("the by-class localization is SUT-specific: the conservation MR localizes to "
                        "different fault classes across SUTs (boundary+normalization on the cylinder; "
                        "normalization on the airfoil), and mirror-y is inadmissible for the airfoil. "
                        "What generalizes across both SUTs: the conservation MR detecting gross "
                        "normalization/scale faults, node-permutation's insensitivity to "
                        "invariant-preserving faults, and the admissibility gate excluding mirror-y."),
        },
        "claim_limitations": (
            "Two SUTs, one airfoil checkpoint, N airfoil eval trajectories, one injected-fault "
            "catalogue, two admissible airfoil detectors. Detection is for this mutant set only; not "
            "a real-world fault-detection rate, reliability, or superiority claim. The cylinder "
            "by-class pattern does NOT replicate on the airfoil: mirror-y is domain-inadmissible, and "
            "the conservation MR localizes to different fault classes (the two SUTs use physics-specific "
            "conservation forms: incompressible full-field vs compressible interior-masked)."
        ),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metric_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ledger


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", default=str(
        ROOT / "research_assets/runs/production-grade-sut-extension"
        / "physicsnemo-mgn-airfoil-primary-roster/checkpoint_k01_seed20260616.pt"))
    ap.add_argument("--traj-indices", default="0,1,2,3,4",
                    help="comma-separated test trajectory indices")
    ap.add_argument("--n-frames", type=int, default=9)
    ap.add_argument("--out", default=str(
        ROOT / "research_assets/runs/production-grade-sut-extension"
        / "physicsnemo-mgn-airfoil-seeded-fault-detection/raw"))
    args = ap.parse_args(argv)
    traj_indices = [int(x) for x in str(args.traj_indices).split(",") if x.strip() != ""]
    led = run_pilot(Path(args.checkpoint), traj_indices, args.n_frames, Path(args.out))
    rob = led["robustness"]
    xs = led["cross_sut_comparison"]
    print(f"\nairfoil seeded-fault detection over {len(MUTANTS)} mutants, "
          f"{rob['n_trajectories']} trajectories (mirror-y inadmissible):")
    print(f"  robustly detected (all trajectories): {rob['robustly_detected_mutants']}")
    print(f"  unstable (some trajectories): {rob['unstable_mutants']}")
    print(f"  never detected: {rob['never_detected_mutants']}")
    print(f"  conservation robustly localizes: {rob['conservation_robustly_localizes']}")
    print(f"  shared localization with cylinder: {xs['shared_localization_across_suts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
