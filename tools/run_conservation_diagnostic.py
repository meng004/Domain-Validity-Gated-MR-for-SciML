"""Run the discrete divergence / mass-conservation MR as an evidence-gated,
reference-relative diagnostic on a real cylinder-flow surrogate.

The absolute "divergence-free" relation stays deferred (an absolute ``div ~ 0``
tolerance is not calibratable on a coarse mesh, where even the ground-truth field
has a non-negligible discrete divergence). This runner instead executes the
calibrated diagnostic: it compares the surrogate's predicted next-state discrete
divergence to the ground-truth next-state divergence on the same mesh, and flags
a conservation regression only when the ratio exceeds a documented factor.

Pure helpers carry no SUT dependency and are unit-testable without torch; only
``run_from_manifest`` imports the SUT.
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
import conservation_rubric as rubric  # noqa: E402

REQUIRED_RAW_OUTPUTS = [
    "predicted_next_velocity",
    "reference_next_velocity",
    "cell_divergence_pred",
    "cell_divergence_reference",
]


# --------------------------------------------------------------------------- #
# pure probe (no SUT dependency)
# --------------------------------------------------------------------------- #
def conservation_probe(
    predict_next: Callable[[np.ndarray], np.ndarray],
    pos: np.ndarray,
    cells: np.ndarray,
    vel_t: np.ndarray,
    vel_t1: np.ndarray,
) -> dict[str, object]:
    """Compare the surrogate's predicted next-state divergence to the reference.

    ``predict_next`` maps the current velocity field to the predicted next-state
    field and is the only SUT-dependent piece; the caller injects it.
    """
    pred = np.asarray(predict_next(vel_t), dtype=np.float64)
    ref = np.asarray(vel_t1, dtype=np.float64)
    div_pred_cells, _ = rubric.cell_divergence(pos, cells, pred)
    div_ref_cells, _ = rubric.cell_divergence(pos, cells, ref)
    pred_rms = rubric.divergence_rms(pos, cells, pred)
    ref_rms = rubric.divergence_rms(pos, cells, ref)
    ratio = pred_rms / ref_rms if ref_rms > 0 else float("inf")
    return {
        "predicted_next_velocity": pred,
        "reference_next_velocity": ref,
        "cell_divergence_pred": div_pred_cells,
        "cell_divergence_reference": div_ref_cells,
        "divergence_pred_rms": float(pred_rms),
        "divergence_reference_rms": float(ref_rms),
        "ratio": float(ratio),
    }


# --------------------------------------------------------------------------- #
# metric ledger (fail-closed)
# --------------------------------------------------------------------------- #
def build_entry(
    *,
    fields: dict[str, str],
    frame: int,
    ratio: float,
    pred_div: float,
    ref_div: float,
    verdict: str,
    tolerance: dict,
    evidence_artifact: str,
) -> dict[str, object]:
    source_case_id = f"{Path(fields['source_case_path']).stem}-frame{frame}"
    return {
        "run_id": fields["run_id"],
        "sut_id": fields["sut_id"],
        "mr_id": fields["mr_id"],
        "source_case_id": source_case_id,
        "follow_up_case_id": f"{source_case_id}-predicted-next-state",
        "metric_name": "divergence_pred_over_reference_ratio",
        "metric_value": float(ratio),
        "tolerance": tolerance,
        "verdict": verdict,
        "evidence_artifact": evidence_artifact,
        "frame": frame,
        "divergence_pred_rms": float(pred_div),
        "divergence_reference_rms": float(ref_div),
        "exact_relation_status": rubric.DEFERRED_UNCALIBRATED,
    }


def build_conservation_metric_ledger(
    *,
    fields: dict[str, str],
    entries: list[dict],
    raw_output_paths: dict[str, Path],
    repo_root: Path | None = None,
    report: dict | None = None,
) -> dict[str, object]:
    """Assemble the conservation diagnostic ledger. Fail-closed: every raw output
    path must already exist, so no verdict is recorded without backing evidence."""
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
        "ledger_id": "real-sut-conservation-diagnostic-metric-ledger",
        "evidence_level": "real-sut-single-mr-conservation-diagnostic-pilot",
        "schema_version": "0.1.0",
        "sut_repo": fields["sut_repo"],
        "sut_commit": fields["sut_commit"],
        "checkpoint_path": fields["checkpoint_path"],
        "checkpoint_sha256": fields["checkpoint_sha256"],
        "exact_relation_status": rubric.DEFERRED_UNCALIBRATED,
        "diagnostic": "reference-relative discrete-divergence regression flag",
        "required_raw_outputs": list(REQUIRED_RAW_OUTPUTS),
        "report": report or {},
        "claim_limitations": (
            "Pilot evidence: one real SUT, a few eval frames. The absolute "
            "divergence-free relation stays deferred (its absolute tolerance is "
            "not calibratable: the reference field's discrete divergence is "
            "non-negligible on this mesh). This is a reference-relative diagnostic "
            "only; it asserts no absolute conservation, no violation rate, no "
            "reliability, accuracy, or baseline result."
        ),
        "raw_outputs": {name: _record(path) for name, path in raw_output_paths.items()},
        "entries": entries,
    }


# --------------------------------------------------------------------------- #
# real SUT execution
# --------------------------------------------------------------------------- #
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
    pos = np.asarray(traj.mesh_pos, np.float64)
    cells = np.asarray(traj.cells)
    nt = traj.node_type
    edge_index_np = ds.build_edge_index(traj.cells, traj.num_nodes)
    vel_norm = Normalizer.from_dict(checkpoint["vel_norm"])
    delta_norm = Normalizer.from_dict(checkpoint["delta_norm"])
    edge_norm = Normalizer.from_dict(checkpoint["edge_norm"])
    onehot = torch.as_tensor(one_hot_node_type(nt))
    edge_feat0 = edge_norm.normalize(torch.as_tensor(edge_features(pos, edge_index_np)))
    edge_index0 = torch.as_tensor(edge_index_np, dtype=torch.long)
    model = MeshGraphNet(node_in=cfg["node_in"], edge_in=cfg["edge_in"], hidden=cfg["hidden"],
                         out_dim=cfg["out_dim"], num_layers=cfg["num_layers"])
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    n_inflow, n_wall = ds.NODE_INFLOW, ds.NODE_WALL

    def make_predict_next(frame: int):
        def predict_next(_v_field):
            v_t = torch.as_tensor(traj.velocity[frame])
            nf = torch.cat([vel_norm.normalize(v_t), onehot], dim=-1)
            with torch.no_grad():
                delta = delta_norm.denormalize(model(nf, edge_feat0, edge_index0))
            v_next = (v_t + delta).numpy().copy()
            prescribed = traj.velocity[frame + 1]
            v_next[nt == n_inflow] = prescribed[nt == n_inflow]
            v_next[nt == n_wall] = 0.0
            return v_next
        return predict_next

    threshold = float(fields.get("regression_threshold", "1.5"))
    abs_tol = float(fields.get("absolute_divergence_tol", "1e-6"))
    raw_dir = _resolve(fields["raw_output_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)

    char_len = float(np.median(np.linalg.norm(
        pos[edge_index_np[0]] - pos[edge_index_np[1]], axis=1)))

    entries: list[dict] = []
    raw_outputs: dict[str, Path] = {}
    tolerance = {
        "assertion": "less_or_equal",
        "threshold": threshold,
        "basis": "reference-relative conservation-regression flag (pred/reference RMS divergence)",
    }
    ref_nondim_values = []
    for idx, frame in enumerate(frames):
        result = conservation_probe(make_predict_next(frame), pos, cells,
                                    traj.velocity[frame], traj.velocity[frame + 1])
        suffix = f"_f{frame}"
        arrays = {
            "predicted_next_velocity": result["predicted_next_velocity"],
            "reference_next_velocity": result["reference_next_velocity"],
            "cell_divergence_pred": result["cell_divergence_pred"],
            "cell_divergence_reference": result["cell_divergence_reference"],
        }
        for name, arr in arrays.items():
            np.save(raw_dir / f"{name}{suffix}.npy", arr)
            raw_outputs[f"{name}{suffix}"] = raw_dir / f"{name}{suffix}.npy"
            if idx == 0:
                np.save(raw_dir / f"{name}.npy", arr)
                raw_outputs[name] = raw_dir / f"{name}.npy"
        speed = float(np.linalg.norm(traj.velocity[frame], axis=1).mean())
        ref_nondim = result["divergence_reference_rms"] * char_len / max(speed, 1e-12)
        ref_nondim_values.append(ref_nondim)
        verdict = rubric.classify_conservation_verdict(
            result["divergence_pred_rms"], result["divergence_reference_rms"],
            threshold=threshold)
        entry = build_entry(
            fields=fields, frame=frame, ratio=result["ratio"],
            pred_div=result["divergence_pred_rms"], ref_div=result["divergence_reference_rms"],
            verdict=verdict, tolerance=tolerance,
            evidence_artifact=str((raw_dir / f"predicted_next_velocity{suffix}.npy").relative_to(repo_root)))
        entry["divergence_pred_nondim"] = float(result["divergence_pred_rms"] * char_len / max(speed, 1e-12))
        entry["divergence_reference_nondim"] = float(ref_nondim)
        entries.append(entry)

    absolute_decision = rubric.classify_absolute_admissible(
        float(np.mean(ref_nondim_values)), abs_tol=abs_tol)
    report = {
        "characteristic_length": char_len,
        "absolute_relation_decision": absolute_decision,
        "absolute_divergence_tol": abs_tol,
        "mean_reference_nondim_divergence": float(np.mean(ref_nondim_values)),
        "regression_threshold": threshold,
        "operator": "P1 constant-per-cell divergence, area-weighted RMS",
    }
    (raw_dir / "conservation_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")

    ledger = build_conservation_metric_ledger(
        fields=fields, entries=entries, raw_output_paths=raw_outputs,
        repo_root=repo_root, report=report)
    ledger["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ledger["frames"] = frames
    ledger["num_nodes"] = int(traj.num_nodes)
    ledger["num_cells"] = int(cells.shape[0])
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
    print(f"absolute_relation={ledger['exact_relation_status']} "
          f"absolute_decision={ledger['report']['absolute_relation_decision']}")
    for e in ledger["entries"]:
        print(f"  frame={e['frame']} ratio={e['metric_value']:.4f} "
              f"div_pred={e['divergence_pred_rms']:.4e} div_ref={e['divergence_reference_rms']:.4e} "
              f"verdict={e['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
