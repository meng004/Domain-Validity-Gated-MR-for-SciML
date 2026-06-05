"""Run the mirror-y metamorphic relation as an evidence-gated OOD-stress probe.

Unlike node permutation, mirror-y equivariance is not guaranteed by the model:
it holds only on a mirror-symmetric domain that the model has learned. This
runner:

1. measures the real source mesh's reflection symmetry about a chosen axis;
2. lets ``mirror_y_rubric`` decide whether an EXACT mirror relation is
   admissible or the case is ``out-of-relation-domain`` (downgraded to an
   OOD-stress probe);
3. runs the SUT under an approximate (nearest-neighbour) reflection, measuring
   the mirror-equivariance violation V together with the mapping-error floor of
   the approximate correspondence, so a violation is only asserted when V stands
   clearly above the floor;
4. persists source/follow-up/mapped raw outputs, a precondition report, and a
   relation-level metric ledger (fail-closed: no verdict without raw outputs).

Pure transform/metric helpers carry no SUT dependency and are unit-testable
without torch; only ``run_from_manifest`` imports the SUT.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest_contract import (  # noqa: E402
    METRIC_LEDGER_FIELDS,
    missing_manifest_fields,
    parse_flat_manifest,
)
import mirror_y_rubric as rubric  # noqa: E402
from run_real_sut_mr import relative_l2  # noqa: E402  (shared pure helper)


# --------------------------------------------------------------------------- #
# pure transforms (no SUT dependency)
# --------------------------------------------------------------------------- #
def mirror_velocity_field(v_field: np.ndarray, pi: np.ndarray) -> np.ndarray:
    """Mirrored input velocity: take the reflection partner's value and flip v_y."""
    v_field = np.asarray(v_field)
    pi = np.asarray(pi)
    return np.stack([v_field[pi, 0], -v_field[pi, 1]], axis=-1)


def mirror_prediction(p: np.ndarray, pi: np.ndarray) -> np.ndarray:
    """Mirror of a model prediction: reflection partner's value with v_y flipped."""
    p = np.asarray(p)
    pi = np.asarray(pi)
    return np.stack([p[pi, 0], -p[pi, 1]], axis=-1)


def mirror_y_probe(
    predict: Callable[[np.ndarray], np.ndarray],
    v_field: np.ndarray,
    pi: np.ndarray,
) -> dict[str, object]:
    """Source/follow-up/mapped triple plus violation and mapping-error floor.

    ``predict`` maps a velocity field to a per-node prediction and is the only
    SUT-dependent piece; the caller injects it.
    """
    v_field = np.asarray(v_field)
    source_output = np.asarray(predict(v_field))            # y0 = f(s)
    mirrored_input = mirror_velocity_field(v_field, pi)
    follow_up_output = np.asarray(predict(mirrored_input))  # y_mirror = f(mirror(s))
    # Un-mirror the follow-up and compare to the source, exactly as the MR card
    # formula specifies: norm(unmirror_y(y_mirror) - y0) / norm(y0). This mirrors
    # the node-permutation pattern (restored follow-up vs source).
    mapped_output = mirror_prediction(follow_up_output, pi)  # unmirror(y_mirror)
    violation = relative_l2(mapped_output, source_output)    # denominator = norm(y0)
    # Mapping-error floor, in the SAME (output) space as the violation: the
    # approximate reflection applied twice to the source prediction should be the
    # identity, so its residual bounds the error attributable to the imperfect
    # correspondence rather than to the model.
    source_round_trip = mirror_prediction(mirror_prediction(source_output, pi), pi)
    mapping_error_floor = relative_l2(source_round_trip, source_output)
    return {
        "source_output": source_output,
        "follow_up_output": follow_up_output,
        "mapped_output": mapped_output,
        "violation": float(violation),
        "mapping_error_floor": float(mapping_error_floor),
    }


# --------------------------------------------------------------------------- #
# metric ledger (fail-closed)
# --------------------------------------------------------------------------- #
def aggregate_violation_rate(entries: list[dict]) -> dict[str, object]:
    """Aggregate per-frame OOD-stress verdicts into a within-SUT frame rate.

    Every recorded frame stays in the denominator: ``inconclusive`` and any
    non-fail verdict are counted and reported separately, never silently dropped.
    """
    import statistics

    n = len(entries)
    verdicts = [e.get("verdict") for e in entries]
    counts: dict[str, int] = {}
    for v in verdicts:
        counts[v] = counts.get(v, 0) + 1
    n_fail = counts.get("fail", 0)
    values = [float(e["metric_value"]) for e in entries if "metric_value" in e]
    ratios = [float(e["violation_over_floor"]) for e in entries if "violation_over_floor" in e]
    return {
        "n_frames": n,
        "verdict_counts": counts,
        "n_fail": n_fail,
        "n_pass": counts.get("pass", 0),
        "n_inconclusive": counts.get("inconclusive", 0),
        "violation_rate": (n_fail / n) if n else float("nan"),
        "median_violation": float(statistics.median(values)) if values else float("nan"),
        "median_violation_over_floor": float(statistics.median(ratios)) if ratios else float("nan"),
        "frames": [e.get("frame") for e in entries],
        "denominator_note": "all recorded frames are counted; inconclusive/out-of-relation-domain frames remain in the denominator",
    }


def build_entry(
    *,
    fields: dict[str, str],
    frame: int,
    violation: float,
    floor: float,
    verdict: str,
    tolerance: dict,
    evidence_artifact: str,
) -> dict[str, object]:
    source_case_id = f"{Path(fields['source_case_path']).stem}-frame{frame}"
    ratio = float(violation / floor) if floor > 0 else float("inf")
    return {
        "run_id": fields["run_id"],
        "sut_id": fields["sut_id"],
        "mr_id": fields["mr_id"],
        "source_case_id": source_case_id,
        "follow_up_case_id": f"{source_case_id}-mirror-y",
        "metric_name": "mirror_y_relative_l2_error",
        "metric_value": float(violation),
        "tolerance": tolerance,
        "verdict": verdict,
        "evidence_artifact": evidence_artifact,
        "frame": frame,
        "mapping_error_floor": float(floor),
        "violation_over_floor": ratio,
        "exact_relation_verdict": "out-of-relation-domain",
    }


def build_mirror_metric_ledger(
    *,
    fields: dict[str, str],
    entries: list[dict],
    raw_output_paths: dict[str, Path],
    precondition_decision: str,
    repo_root: Path | None = None,
    precondition_report: dict | None = None,
) -> dict[str, object]:
    """Assemble the mirror-y metric ledger. Fail-closed: every raw output path
    must already exist, so no verdict is recorded without backing evidence."""
    for name, path in raw_output_paths.items():
        if not Path(path).exists():
            raise ValueError(
                f"refusing to write metric ledger: raw output '{name}' missing at {path}"
            )
    for entry in entries:
        missing = [f for f in METRIC_LEDGER_FIELDS if f not in entry]
        if missing:
            raise ValueError(f"metric ledger entry missing fields: {missing}")

    def _record(path: Path) -> str:
        path = Path(path)
        if repo_root is not None:
            try:
                return str(path.resolve().relative_to(Path(repo_root).resolve()))
            except ValueError:
                return str(path)
        return str(path)

    return {
        "ledger_id": "real-sut-mirror-y-ood-stress-metric-ledger",
        "evidence_level": "real-sut-single-mr-ood-stress-pilot",
        "schema_version": "0.1.0",
        "sut_repo": fields["sut_repo"],
        "sut_commit": fields["sut_commit"],
        "checkpoint_path": fields["checkpoint_path"],
        "checkpoint_sha256": fields["checkpoint_sha256"],
        "exact_relation_verdict": "out-of-relation-domain",
        "precondition_decision": precondition_decision,
        "rubric_downgrade": rubric.DOWNGRADE_OOD_STRESS,
        "precondition_report": precondition_report or {},
        "claim_limitations": (
            "One real SUT and checkpoint, one metamorphic relation (mirror-y), the "
            "recorded eval frames of a single trajectory. The exact mirror relation "
            "is out-of-relation-domain for this mesh (measured non-mirror-symmetric "
            "geometry); the reported violation is an approximate within-SUT OOD-stress "
            "measurement relative to its mapping-error floor. Any frame-level rate is a "
            "bounded within-SUT rate only -- not a geometry-independent or cross-SUT "
            "violation rate, and not a reliability, accuracy, or baseline claim."
        ),
        "raw_outputs": {name: _record(path) for name, path in raw_output_paths.items()},
        "entries": entries,
    }


# --------------------------------------------------------------------------- #
# real SUT execution
# --------------------------------------------------------------------------- #
def _cylinder_offset(pos: np.ndarray, node_type: np.ndarray, axis: float) -> dict:
    ymin, ymax = float(pos[:, 1].min()), float(pos[:, 1].max())
    wall = pos[node_type == 6]
    eps = 0.02 * (ymax - ymin)
    interior = wall[(wall[:, 1] > ymin + eps) & (wall[:, 1] < ymax - eps)]
    if interior.shape[0] == 0:
        return {}
    cx, cy = float(interior[:, 0].mean()), float(interior[:, 1].mean())
    r = float(np.linalg.norm(interior - np.array([cx, cy]), axis=1).mean())
    return {
        "center": [cx, cy],
        "mean_radius": r,
        "offset_from_axis": float(cy - axis),
        "interior_wall_nodes": int(interior.shape[0]),
    }


def run_from_manifest(manifest_path: Path, *, frames: list[int] | None = None) -> dict:
    manifest_path = Path(manifest_path)
    fields = parse_flat_manifest(manifest_path.read_text(encoding="utf-8"))
    missing = missing_manifest_fields(fields)
    if missing:
        raise ValueError(f"manifest missing required fields: {missing}")
    frames = frames if frames is not None else [0]
    repo_root = Path(__file__).resolve().parents[1]

    def _resolve(rel: str) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else (repo_root / p)

    sys.path.insert(0, str(Path(fields["sut_repo"]) / "scripts"))
    import torch  # noqa: PLC0415
    from mcmr.cylinder_flow import dm_dataset as ds  # noqa: PLC0415
    from mcmr.cylinder_flow.mgn import (  # noqa: PLC0415
        MeshGraphNet, Normalizer, edge_features, one_hot_node_type)

    checkpoint = torch.load(_resolve(fields["checkpoint_path"]), map_location="cpu",
                            weights_only=False)
    cfg = checkpoint["config"]
    traj = ds.load_npz(_resolve(fields["source_case_path"]))
    pos, node_type = traj.mesh_pos, traj.node_type
    edge_index_np = ds.build_edge_index(traj.cells, traj.num_nodes)
    vel_norm = Normalizer.from_dict(checkpoint["vel_norm"])
    edge_norm = Normalizer.from_dict(checkpoint["edge_norm"])
    onehot = torch.as_tensor(one_hot_node_type(node_type))
    edge_feat0 = edge_norm.normalize(torch.as_tensor(edge_features(pos, edge_index_np)))
    edge_index0 = torch.as_tensor(edge_index_np, dtype=torch.long)

    model = MeshGraphNet(node_in=cfg["node_in"], edge_in=cfg["edge_in"],
                         hidden=cfg["hidden"], out_dim=cfg["out_dim"],
                         num_layers=cfg["num_layers"])
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    def predict(v_field: np.ndarray) -> np.ndarray:
        nf = torch.cat([vel_norm.normalize(torch.as_tensor(np.asarray(v_field),
                                                           dtype=torch.float32)), onehot], dim=-1)
        with torch.no_grad():
            return model(nf, edge_feat0, edge_index0).detach().numpy()

    axis = float(fields["mirror_axis"])
    metrics = rubric.measure_reflection_symmetry(pos, node_type, traj.cells, axis)
    precondition_decision = rubric.classify_mirror_preconditions(metrics)
    pi = rubric.reflection_map(pos, axis)
    cyl = _cylinder_offset(np.asarray(pos, np.float64), node_type, axis)

    card = json.loads(
        (repo_root / "research_assets" / "mr_cards"
         / "mirror_y_equivariance.json").read_text(encoding="utf-8"))
    tolerance = card["tolerance"]
    ratio_threshold = float(fields.get("ratio_threshold", "2.0"))

    raw_dir = _resolve(fields["raw_output_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    np.save(raw_dir / "reflection_map.npy", pi)

    entries: list[dict] = []
    raw_outputs: dict[str, Path] = {}
    for idx, frame in enumerate(frames):
        result = mirror_y_probe(predict, traj.velocity[frame], pi)
        suffix = f"_f{frame}"
        for name in ("source_output", "follow_up_output", "mapped_output"):
            per_frame = raw_dir / f"{name}{suffix}.npy"
            np.save(per_frame, result[name])
            raw_outputs[f"{name}{suffix}"] = per_frame  # every frame is gate-checked
            if idx == 0:  # canonical (gate-compatible) names from the first frame
                np.save(raw_dir / f"{name}.npy", result[name])
                raw_outputs[name] = raw_dir / f"{name}.npy"
        verdict = rubric.classify_ood_stress_verdict(
            result["violation"], result["mapping_error_floor"],
            tolerance=float(tolerance["threshold"]), ratio_threshold=ratio_threshold)
        entries.append(build_entry(
            fields=fields, frame=frame, violation=result["violation"],
            floor=result["mapping_error_floor"], verdict=verdict, tolerance=tolerance,
            evidence_artifact=str((raw_dir / f"source_output{suffix}.npy").relative_to(repo_root))))

    precondition_report = {
        **metrics,
        "cylinder": cyl,
        "precondition_decision": precondition_decision,
        "rubric_downgrade": rubric.DOWNGRADE_OOD_STRESS,
        "ratio_threshold": ratio_threshold,
        "axis_source": "channel centerline (geometric mid of y-extent)",
    }
    (raw_dir / "precondition_report.json").write_text(
        json.dumps(precondition_report, indent=2) + "\n", encoding="utf-8")

    ledger = build_mirror_metric_ledger(
        fields=fields, entries=entries, raw_output_paths=raw_outputs,
        precondition_decision=precondition_decision, repo_root=repo_root,
        precondition_report=precondition_report)
    ledger["rate_summary"] = aggregate_violation_rate(entries)
    ledger["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ledger["frames"] = frames
    ledger["num_nodes"] = int(traj.num_nodes)
    ledger["num_edges"] = int(edge_index_np.shape[1])
    ledger["device"] = fields["device"]
    ledger["framework_version"] = fields["framework_version"]
    (raw_dir / "metric_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ledger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--frames", default="0")
    args = parser.parse_args(argv)
    frames = [int(x) for x in args.frames.split(",") if x.strip()]
    ledger = run_from_manifest(Path(args.manifest), frames=frames)
    print(f"precondition_decision={ledger['precondition_decision']} "
          f"exact_relation_verdict={ledger['exact_relation_verdict']}")
    for e in ledger["entries"]:
        print(f"  frame={e['frame']} {e['metric_name']}={e['metric_value']:.3e} "
              f"floor={e['mapping_error_floor']:.3e} V/floor={e['violation_over_floor']:.2f} "
              f"ood_stress_verdict={e['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
