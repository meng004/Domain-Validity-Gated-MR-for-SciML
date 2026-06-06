"""E3: fault-detection robustness across SUTs/input-seeds and severity sweeps.

Builds on the seeded-fault experiment in ``tools/run_seeded_fault_detection.py``
(re-implemented mutant catalogue from the read-only Minimum-MR-SubSet repo,
which is never modified). For each SUT S0..S5 (the multi-checkpoint roster):

R1. Cross-SUT detection: replay each of the 10 canonical mutants and the
    baseline through the same 3 detectors (node-perm, conservation, mirror-y),
    accumulating per-mutant per-detector detection events across SUTs to give a
    Wilson 95% CI on the across-SUT detection rate for each (mutant, detector).

R2. Severity sweep on NS_double_scale s in {1.1, 1.25, 1.5, 2, 4}: replace the
    canonical 2x scale with parametric s, plot detection vs s per detector.

R3. Severity sweep on PC_zero_vy partial fraction p in {0.25, 0.5, 0.75, 1.0}:
    zero a fraction p of node-wise vy deltas (canonical fault has p=1.0).

Honesty boundary: K=6 checkpoints of one architecture family / one dataset.
Detection rates here are the rate at which a paper-defined detector trips on a
predeclared mutant catalogue, not real-world fault-detection rates.
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from conservation_rubric import divergence_rms  # noqa: E402
from mirror_y_rubric import reflection_map  # noqa: E402
from run_mirror_y_ood_stress import mirror_y_probe  # noqa: E402

SUTS = [
    ("S0", ROOT / "research_assets/runs/real-sut-node-permutation-pilot/sut/checkpoint.pt"),
    ("S1", ROOT / "research_assets/runs/multicheckpoint/S1/checkpoint.pt"),
    ("S2", ROOT / "research_assets/runs/multicheckpoint/S2/checkpoint.pt"),
    ("S3", ROOT / "research_assets/runs/multicheckpoint/S3/checkpoint.pt"),
    ("S4", ROOT / "research_assets/runs/multicheckpoint/S4/checkpoint.pt"),
    ("S5", ROOT / "research_assets/runs/multicheckpoint/S5/checkpoint.pt"),
]
SUT_REPO = Path("/home/user/Minimum-MR-SubSet")
SOURCE_CASE = ROOT / "research_assets/runs/real-sut-node-permutation-pilot/source_case.npz"

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

NODE_PERM_TOL = 1e-5
CONSERVATION_RATIO_TOL = 1.5
MIRROR_Y_REL_CHANGE_TOL = 0.5

INPUT_SEEDS = [20260601, 20260602, 20260603, 20260604, 20260605]
NS_SCALE_LEVELS = [1.1, 1.25, 1.5, 2.0, 4.0]
PC_ZEROY_FRACS = [0.25, 0.5, 0.75, 1.0]


def _sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return p, max(0.0, centre - half), min(1.0, centre + half)


def relative_l2(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, np.float64); b = np.asarray(b, np.float64)
    d = float(np.linalg.norm(b))
    return float(np.linalg.norm(a - b)) / d if d else float("inf")


def inverse_permutation(perm: np.ndarray) -> np.ndarray:
    inv = np.empty_like(perm); inv[perm] = np.arange(perm.shape[0]); return inv


def make_sut_runtime(ckpt_path: Path):
    """Load the SUT and pre-compute everything that does not depend on the mutant."""
    sys.path.insert(0, str(SUT_REPO / "scripts"))
    import torch  # noqa: PLC0415
    from mcmr.cylinder_flow import dm_dataset as ds  # noqa: PLC0415
    from mcmr.cylinder_flow.mgn import (  # noqa: PLC0415
        MeshGraphNet, Normalizer, edge_features, one_hot_node_type)

    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    cfg = ck["config"]
    traj = ds.load_npz(SOURCE_CASE)
    vel_norm = Normalizer.from_dict(ck["vel_norm"])
    delta_norm = Normalizer.from_dict(ck["delta_norm"])
    edge_norm = Normalizer.from_dict(ck["edge_norm"])
    model = MeshGraphNet(node_in=cfg["node_in"], edge_in=cfg["edge_in"],
                         hidden=cfg["hidden"], out_dim=cfg["out_dim"],
                         num_layers=cfg["num_layers"])
    model.load_state_dict(ck["state_dict"]); model.eval()
    base_edge_index = ds.build_edge_index(traj.cells, traj.num_nodes)
    inflow = traj.node_type == ds.NODE_INFLOW
    wall = (traj.node_type == ds.NODE_WALL) | (traj.node_type == ds.NODE_OBSTACLE)
    onehot = torch.as_tensor(one_hot_node_type(traj.node_type))

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

    def mutated_update(mesh_pos, oh, ei_np, v_t, mutant, params=None):
        params = params or {}
        ei_used = ei_np
        if mutant == "MA_drop_edges":
            ei_used = drop_edges(ei_np)
        elif mutant == "MA_permute_edges":
            ei_used = permute_edges(ei_np)
        ef = edge_norm.normalize(torch.as_tensor(edge_features(mesh_pos, ei_used)))
        ei_t = torch.as_tensor(ei_used, dtype=torch.long)
        nf = torch.cat([vel_norm.normalize(torch.as_tensor(v_t)), oh], dim=-1)
        with torch.no_grad():
            dpred = model(nf.to(torch.float32), ef.to(torch.float32), ei_t)
        delta = delta_norm.denormalize(dpred)
        if mutant == "NS_skip_denorm":
            delta = dpred
        elif mutant == "NS_double_scale":
            delta = float(params.get("scale", 2.0)) * delta
        if mutant == "PC_swap_xy":
            delta = delta[:, [1, 0]]
        elif mutant == "PC_zero_vy":
            frac = float(params.get("zero_fraction", 1.0))
            n = delta.shape[0]
            n_zero = int(round(frac * n))
            if frac >= 1.0:
                delta = torch.stack([delta[:, 0], torch.zeros_like(delta[:, 1])], dim=-1)
            elif n_zero > 0:
                seed = int(params.get("zero_seed", 20260606))
                rng = np.random.default_rng(seed)
                idx = rng.choice(n, size=n_zero, replace=False)
                mask = torch.zeros(n, dtype=torch.bool)
                mask[idx] = True
                vy = delta[:, 1].clone()
                vy[mask] = 0.0
                delta = torch.stack([delta[:, 0], vy], dim=-1)
        return delta.detach().numpy()

    def predict(mesh_pos, oh, ei_np, inflow_m, wall_m, v_t, prescribed, mutant, params=None):
        delta = torch.as_tensor(mutated_update(mesh_pos, oh, ei_np, v_t, mutant, params))
        v_t_t = torch.as_tensor(v_t)
        if mutant == "TR_sign_flip":
            v_next = v_t_t - delta
        elif mutant == "TR_double_step":
            v_mid = v_t_t + delta
            d2 = torch.as_tensor(mutated_update(mesh_pos, oh, ei_np, v_mid.numpy(), mutant, params))
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

    return {
        "torch": torch, "traj": traj, "model": model, "base_edge_index": base_edge_index,
        "inflow": inflow, "wall": wall, "onehot": onehot,
        "one_hot_node_type": one_hot_node_type, "ds": ds,
        "mutated_update": mutated_update, "predict": predict,
        "ckpt_sha256": _sha256(ckpt_path),
    }


def detect_for_mutant(rt, mutant: str, params: dict, input_seed: int) -> dict:
    """Run the three detectors over all frames for one (mutant, params) cell."""
    traj = rt["traj"]; base_ei = rt["base_edge_index"]
    onehot = rt["onehot"]; inflow = rt["inflow"]; wall = rt["wall"]
    rng = np.random.default_rng(input_seed)
    perm = rng.permutation(traj.num_nodes)
    inv = inverse_permutation(perm)
    onehot_perm = rt["torch"].as_tensor(rt["one_hot_node_type"](traj.node_type[perm]))
    pi = reflection_map(traj.mesh_pos, 0.205)

    np_vals, cons_vals, mir_vals = [], [], []
    frames = list(range(int(traj.velocity.shape[0]) - 1))
    for t in frames:
        v_t = traj.velocity[t]
        prescribed = traj.velocity[t + 1]
        base = rt["mutated_update"](traj.mesh_pos, onehot, base_ei, v_t, mutant, params)
        out_p = rt["mutated_update"](traj.mesh_pos[perm], onehot_perm,
                                     inv[base_ei], v_t[perm], mutant, params)
        np_vals.append(relative_l2(out_p[inv], base))
        v_next = rt["predict"](traj.mesh_pos, onehot, base_ei, inflow, wall, v_t,
                               prescribed, mutant, params)
        ref_div = divergence_rms(traj.mesh_pos, traj.cells, prescribed)
        pred_div = divergence_rms(traj.mesh_pos, traj.cells, v_next)
        cons_vals.append(pred_div / ref_div if ref_div else float("inf"))

        def _pred(vf):
            return rt["mutated_update"](traj.mesh_pos, onehot, base_ei, vf, mutant, params)
        mir_vals.append(float(mirror_y_probe(_pred, v_t, pi)["violation"]))
    return {
        "node_perm_median": float(np.median(np_vals)),
        "conservation_median": float(np.median(cons_vals)),
        "mirror_y_median": float(np.median(mir_vals)),
    }


def decide_detection(values: dict, baseline_mir: float) -> dict:
    np_det = values["node_perm_median"] > NODE_PERM_TOL
    cons_det = values["conservation_median"] > CONSERVATION_RATIO_TOL
    if baseline_mir > 0:
        mir_rel = abs(values["mirror_y_median"] - baseline_mir) / baseline_mir
    else:
        mir_rel = float("inf")
    mir_det = mir_rel > MIRROR_Y_REL_CHANGE_TOL
    return {"node_perm": bool(np_det), "conservation": bool(cons_det),
            "mirror_y": bool(mir_det), "any": bool(np_det or cons_det or mir_det),
            "mirror_y_relative_change": mir_rel}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(ROOT / "research_assets/runs/fault-robustness-e3"))
    ap.add_argument("--input-seeds", type=int, default=len(INPUT_SEEDS))
    args = ap.parse_args()
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    seeds = INPUT_SEEDS[: max(1, args.input_seeds)]

    cross_sut: dict[str, dict[str, dict]] = {}  # cross_sut[sut][mutant]
    severity_ns: dict[str, dict[float, dict]] = {}  # severity_ns[sut][scale]
    severity_pc: dict[str, dict[float, dict]] = {}

    for sut_id, ckpt in SUTS:
        if not ckpt.exists():
            print(f"!! {sut_id}: missing checkpoint, skipping")
            continue
        print(f"== {sut_id} == load")
        rt = make_sut_runtime(ckpt)
        cross_sut[sut_id] = {}
        # Single permutation seed for R1 (mutant injection itself, not perm,
        # drives detection; we average across SUTs not seeds for the CI).
        per_seed = {}
        for s in seeds:
            per_seed[s] = {}
            print(f"   seed {s}: baseline + 10 mutants")
            baseline = detect_for_mutant(rt, "baseline", {}, s)
            per_seed[s]["baseline"] = baseline
            for mut in MUTANTS:
                v = detect_for_mutant(rt, mut, {}, s)
                d = decide_detection(v, baseline["mirror_y_median"])
                per_seed[s][mut] = {"values": v, "detections": d,
                                    "fault_class": FAULT_CLASS[mut]}
        cross_sut[sut_id]["per_seed"] = per_seed

        # R2: NS severity sweep (use seed 20260606 for permutation; severity is the var of interest)
        print(f"   NS_double_scale severity sweep")
        sweep_ns = {}
        bl = detect_for_mutant(rt, "baseline", {}, 20260606)
        for scale in NS_SCALE_LEVELS:
            v = detect_for_mutant(rt, "NS_double_scale", {"scale": scale}, 20260606)
            d = decide_detection(v, bl["mirror_y_median"])
            sweep_ns[scale] = {"values": v, "detections": d}
        severity_ns[sut_id] = sweep_ns

        print(f"   PC_zero_vy partial-fraction sweep")
        sweep_pc = {}
        for frac in PC_ZEROY_FRACS:
            v = detect_for_mutant(rt, "PC_zero_vy", {"zero_fraction": frac}, 20260606)
            d = decide_detection(v, bl["mirror_y_median"])
            sweep_pc[frac] = {"values": v, "detections": d}
        severity_pc[sut_id] = sweep_pc

    # Aggregate Wilson CI across SUTs x seeds for each (mutant, detector).
    detectors = ["node_perm", "conservation", "mirror_y", "any"]
    r1 = {}
    for mut in MUTANTS:
        per_det = {}
        for det in detectors:
            k = n = 0
            for sut_id, sut_data in cross_sut.items():
                for s, mut_results in sut_data["per_seed"].items():
                    if mut not in mut_results:
                        continue
                    n += 1
                    if mut_results[mut]["detections"][det]:
                        k += 1
            p, lo, hi = wilson_ci(k, n)
            per_det[det] = {"k": k, "n": n, "rate": p, "ci_lo": lo, "ci_hi": hi}
        r1[mut] = {"fault_class": FAULT_CLASS[mut], "per_detector": per_det}

    # Severity sweep: per-level detection rate across SUTs (Wilson over SUTs).
    def sweep_ci(per_sut_sweep: dict, levels: list, detectors_) -> dict:
        out = {}
        for lv in levels:
            per_det = {}
            for det in detectors_:
                k = sum(1 for sut, s in per_sut_sweep.items()
                        if s.get(lv) and s[lv]["detections"][det])
                n = len(per_sut_sweep)
                p, lo, hi = wilson_ci(k, n)
                per_det[det] = {"k": k, "n": n, "rate": p, "ci_lo": lo, "ci_hi": hi}
            out[str(lv)] = per_det
        return out

    r2 = sweep_ci(severity_ns, NS_SCALE_LEVELS, detectors)
    r3 = sweep_ci(severity_pc, PC_ZEROY_FRACS, detectors)

    report = {
        "experiment_id": "E3-fault-detection-robustness",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fault_taxonomy_source": ("re-implemented from read-only Minimum-MR-SubSet "
                                  "scripts/mcmr/cylinder_flow/witness_stage_b.py"),
        "suts": [s for s, _ in SUTS if (ROOT / _).exists() or _.exists()],
        "input_permutation_seeds": seeds,
        "detection_thresholds": {"node_perm_tol": NODE_PERM_TOL,
                                 "conservation_ratio_tol": CONSERVATION_RATIO_TOL,
                                 "mirror_y_relative_change_tol": MIRROR_Y_REL_CHANGE_TOL},
        "R1_cross_sut_detection": r1,
        "R2_NS_double_scale_severity_sweep": {
            "levels": NS_SCALE_LEVELS,
            "per_level_detection_rate": r2,
            "per_sut_raw": {sut: {str(k): v for k, v in d.items()}
                            for sut, d in severity_ns.items()},
        },
        "R3_PC_zero_vy_partial_fraction_sweep": {
            "levels": PC_ZEROY_FRACS,
            "per_level_detection_rate": r3,
            "per_sut_raw": {sut: {str(k): v for k, v in d.items()}
                            for sut, d in severity_pc.items()},
        },
        "per_sut_per_seed_raw": cross_sut,
        "claim_limitations": (
            "K=6 checkpoints of one architecture family / one dataset; "
            "fixed mutant catalogue; detection rates are paper-defined-detector "
            "trip rates, not real-world fault-detection rates. Mirror-y mutant "
            "injection randomness is fixed inside drop_edges/permute_edges to "
            "keep the catalogue reproducible; only the node permutation varies "
            "across input seeds, so the input-seed axis primarily perturbs the "
            "node-perm detector."),
    }
    out = outdir / "fault_robustness_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {out}")
    print("\nR1 per-mutant any-detector rate (across all SUTs x input seeds):")
    for mut, info in r1.items():
        d = info["per_detector"]["any"]
        print(f"  {mut:18s} {info['fault_class']:24s} "
              f"any: {d['k']}/{d['n']} = {d['rate']:.2f} "
              f"CI[{d['ci_lo']:.2f},{d['ci_hi']:.2f}]")
    print("\nR2 NS_double_scale severity sweep (any-detector):")
    for lv in NS_SCALE_LEVELS:
        d = r2[str(lv)]["any"]
        print(f"  scale={lv}: {d['k']}/{d['n']}  rate={d['rate']:.2f} "
              f"CI[{d['ci_lo']:.2f},{d['ci_hi']:.2f}]")
    print("\nR3 PC_zero_vy partial-fraction sweep (any-detector):")
    for lv in PC_ZEROY_FRACS:
        d = r3[str(lv)]["any"]
        print(f"  frac={lv}: {d['k']}/{d['n']}  rate={d['rate']:.2f} "
              f"CI[{d['ci_lo']:.2f},{d['ci_hi']:.2f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
