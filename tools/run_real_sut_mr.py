"""Run a real-SUT node-permutation equivariance metamorphic relation.

This runner consumes a flat run manifest (see
``research_assets/experiments/manifests/node_permutation_real_sut.example.yml``)
and executes one metamorphic-relation run against a real trained
MeshGraphNets-family cylinder-flow surrogate:

1. load the source case from the dataset,
2. run the SUT to obtain the **source** output,
3. apply a node permutation (a bijection over node indices, with the mesh
   connectivity relabelled consistently),
4. run the SUT again to obtain the **follow-up** output,
5. inverse-map the follow-up output back to the source node order (**mapped**),
6. score relative L2 against the source output and compare to the MR tolerance,
7. persist every raw output plus a relation-level metric ledger.

Honesty boundaries enforced in code:

- No verdict is written unless the source/follow-up/mapped raw outputs were
  saved first (``build_metric_ledger`` refuses otherwise).
- The pure-numpy transform/metric helpers carry no SUT dependency, so they are
  unit-testable without torch; only ``run_from_manifest`` imports the SUT.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np

# Shared run-manifest contract (single source of truth). The tools/ directory
# has no package init, so make it importable regardless of how this file is
# loaded (CLI, import, or importlib spec).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest_contract import (  # noqa: E402
    METRIC_LEDGER_FIELDS,
    missing_manifest_fields,
    parse_flat_manifest,
)


def load_manifest(path: Path) -> dict[str, str]:
    return parse_flat_manifest(Path(path).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# pure transform + metric helpers (no SUT dependency)
# --------------------------------------------------------------------------- #
def inverse_permutation(perm: np.ndarray) -> np.ndarray:
    perm = np.asarray(perm)
    inv = np.empty_like(perm)
    inv[perm] = np.arange(perm.shape[0])
    return inv


def validate_permutation(perm: np.ndarray) -> None:
    perm = np.asarray(perm)
    if perm.ndim != 1 or not np.array_equal(np.sort(perm), np.arange(perm.shape[0])):
        raise ValueError("permutation must be a bijection over node indices")


def relative_l2(left: np.ndarray, right: np.ndarray) -> float:
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    denom = float(np.linalg.norm(right))
    num = float(np.linalg.norm(left - right))
    if denom == 0.0:
        return 0.0 if num == 0.0 else float("inf")
    return num / denom


def node_permutation_equivariance(
    forward: Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray],
    node_feat: np.ndarray,
    edge_feat: np.ndarray,
    edge_index: np.ndarray,
    perm: np.ndarray,
) -> dict[str, object]:
    """Execute the source/follow-up/mapped triple for one node permutation.

    ``forward`` maps ``(node_feat, edge_feat, edge_index) -> (N, D)`` output and
    is the only SUT-dependent piece; the caller injects it.
    """
    validate_permutation(perm)
    perm = np.asarray(perm)
    inv = inverse_permutation(perm)

    source_output = np.asarray(forward(node_feat, edge_feat, edge_index))
    node_feat_perm = node_feat[perm]
    edge_index_perm = inv[edge_index]          # relabel endpoints consistently
    follow_up_output = np.asarray(forward(node_feat_perm, edge_feat, edge_index_perm))
    mapped_output = follow_up_output[inv]      # restore source node order

    metric_value = relative_l2(mapped_output, source_output)
    return {
        "permutation": perm,
        "inverse_permutation": inv,
        "source_output": source_output,
        "follow_up_output": follow_up_output,
        "mapped_output": mapped_output,
        "metric_value": metric_value,
    }


def classify_verdict(metric_value: float, threshold: float, assertion: str) -> str:
    if not np.isfinite(metric_value):
        return "numerical-tolerance-issue"
    if assertion == "less_or_equal":
        return "pass" if metric_value <= threshold else "fail"
    raise ValueError(f"unsupported tolerance assertion: {assertion}")


# --------------------------------------------------------------------------- #
# metric ledger (refuses to score without saved raw outputs)
# --------------------------------------------------------------------------- #
def build_metric_ledger(
    *,
    fields: dict[str, str],
    source_case_id: str,
    follow_up_case_id: str,
    metric_name: str,
    metric_value: float,
    tolerance: dict,
    verdict: str,
    raw_output_paths: dict[str, Path],
    evidence_artifact: str,
    repo_root: Path | None = None,
) -> dict[str, object]:
    """Assemble the relation-level metric ledger.

    Fails closed: every raw output path must already exist on disk, so a verdict
    can never be recorded without its backing evidence. When ``repo_root`` is
    given, raw-output paths are recorded relative to it so the committed ledger
    stays portable.
    """
    for name, path in raw_output_paths.items():
        if not Path(path).exists():
            raise ValueError(
                f"refusing to write metric ledger: raw output '{name}' missing at {path}"
            )

    def _record(path: Path) -> str:
        path = Path(path)
        if repo_root is not None:
            try:
                return str(path.resolve().relative_to(Path(repo_root).resolve()))
            except ValueError:
                return str(path)
        return str(path)
    entry = {
        "run_id": fields["run_id"],
        "sut_id": fields["sut_id"],
        "mr_id": fields["mr_id"],
        "source_case_id": source_case_id,
        "follow_up_case_id": follow_up_case_id,
        "metric_name": metric_name,
        "metric_value": metric_value,
        "tolerance": tolerance,
        "verdict": verdict,
        "evidence_artifact": evidence_artifact,
    }
    missing = [f for f in METRIC_LEDGER_FIELDS if f not in entry]
    if missing:
        raise ValueError(f"metric ledger entry missing fields: {missing}")
    return {
        "ledger_id": "real-sut-node-permutation-metric-ledger",
        "evidence_level": "real-sut-single-mr-pilot",
        "schema_version": "0.1.0",
        "sut_repo": fields["sut_repo"],
        "sut_commit": fields["sut_commit"],
        "checkpoint_path": fields["checkpoint_path"],
        "checkpoint_sha256": fields["checkpoint_sha256"],
        "claim_limitations": (
            "Pilot evidence: one real SUT, one metamorphic relation (node "
            "permutation equivariance), a single source case. It does not report "
            "violation rates, model reliability, baseline comparison, or seeded-"
            "fault detection."
        ),
        "raw_outputs": {name: _record(path) for name, path in raw_output_paths.items()},
        "entries": [entry],
    }


# --------------------------------------------------------------------------- #
# real SUT execution (imports the SUT; needs torch + the SUT repo on disk)
# --------------------------------------------------------------------------- #
def _save_array(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, np.asarray(array))


def run_from_manifest(manifest_path: Path, *, frame: int = 0) -> dict[str, object]:
    manifest_path = Path(manifest_path)
    fields = load_manifest(manifest_path)
    missing = missing_manifest_fields(fields)
    if missing:
        raise ValueError(f"manifest missing required fields: {missing}")

    # Repo root is this runner's own location (tools/..), so artifact paths
    # resolve correctly no matter where the manifest file lives.
    repo_root = Path(__file__).resolve().parents[1]

    # Resolve artifacts relative to the asset repo root.
    def _resolve(rel: str) -> Path:
        p = Path(rel)
        return p if p.is_absolute() else (repo_root / p)

    sut_repo = Path(fields["sut_repo"])
    sys.path.insert(0, str(sut_repo / "scripts"))

    import torch  # noqa: PLC0415 -- SUT dependency, intentionally local
    from mcmr.cylinder_flow import dm_dataset as ds  # noqa: PLC0415
    from mcmr.cylinder_flow.mgn import (  # noqa: PLC0415
        MeshGraphNet,
        Normalizer,
        edge_features,
        one_hot_node_type,
    )

    checkpoint = torch.load(_resolve(fields["checkpoint_path"]), map_location="cpu",
                            weights_only=False)
    cfg = checkpoint["config"]
    traj = ds.load_npz(_resolve(fields["source_case_path"]))

    edge_index_np = ds.build_edge_index(traj.cells, traj.num_nodes)
    vel_norm = Normalizer.from_dict(checkpoint["vel_norm"])
    edge_norm = Normalizer.from_dict(checkpoint["edge_norm"])
    onehot = torch.as_tensor(one_hot_node_type(traj.node_type))

    model = MeshGraphNet(node_in=cfg["node_in"], edge_in=cfg["edge_in"],
                         hidden=cfg["hidden"], out_dim=cfg["out_dim"],
                         num_layers=cfg["num_layers"])
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    v_t = torch.as_tensor(traj.velocity[frame])
    node_feat0 = torch.cat([vel_norm.normalize(v_t), onehot], dim=-1)
    edge_feat0 = edge_norm.normalize(
        torch.as_tensor(edge_features(traj.mesh_pos, edge_index_np))
    )
    edge_index0 = torch.as_tensor(edge_index_np, dtype=torch.long)

    def forward(node_feat, edge_feat, edge_index) -> np.ndarray:
        with torch.no_grad():
            out = model(
                torch.as_tensor(np.asarray(node_feat), dtype=torch.float32),
                torch.as_tensor(np.asarray(edge_feat), dtype=torch.float32),
                torch.as_tensor(np.asarray(edge_index), dtype=torch.long),
            )
        return out.detach().numpy()

    rng = np.random.default_rng(int(fields["seed"]))
    perm = rng.permutation(traj.num_nodes)

    result = node_permutation_equivariance(
        forward,
        node_feat0.detach().numpy(),
        edge_feat0.detach().numpy(),
        edge_index_np,
        perm,
    )

    raw_dir = _resolve(fields["raw_output_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "source_output": raw_dir / "source_output.npy",
        "follow_up_output": raw_dir / "follow_up_output.npy",
        "mapped_output": raw_dir / "mapped_output.npy",
        "permutation": raw_dir / "permutation.npy",
        "inverse_permutation": raw_dir / "inverse_permutation.npy",
    }
    _save_array(paths["source_output"], result["source_output"])
    _save_array(paths["follow_up_output"], result["follow_up_output"])
    _save_array(paths["mapped_output"], result["mapped_output"])
    _save_array(paths["permutation"], result["permutation"])
    _save_array(paths["inverse_permutation"], result["inverse_permutation"])

    # MR card tolerance.
    card = json.loads(
        (repo_root / "research_assets" / "mr_cards"
         / "node_permutation_equivariance.json").read_text(encoding="utf-8")
    )
    tolerance = card["tolerance"]
    metric_value = float(result["metric_value"])
    verdict = classify_verdict(metric_value, float(tolerance["threshold"]),
                               tolerance["assertion"])

    source_case_id = f"{Path(fields['source_case_path']).stem}-frame{frame}"
    ledger = build_metric_ledger(
        fields=fields,
        source_case_id=source_case_id,
        follow_up_case_id=f"{source_case_id}-node-permuted-seed{fields['seed']}",
        metric_name=card["metric"]["name"],
        metric_value=metric_value,
        tolerance=tolerance,
        verdict=verdict,
        raw_output_paths=paths,
        evidence_artifact=str(raw_dir.relative_to(repo_root)),
        repo_root=repo_root,
    )
    ledger["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ledger["frame"] = frame
    ledger["num_nodes"] = int(traj.num_nodes)
    ledger["num_edges"] = int(edge_index_np.shape[1])
    ledger["device"] = fields["device"]
    ledger["framework_version"] = fields["framework_version"]

    ledger_path = raw_dir / "metric_ledger.json"
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    return ledger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--frame", type=int, default=0)
    args = parser.parse_args(argv)
    ledger = run_from_manifest(Path(args.manifest), frame=args.frame)
    entry = ledger["entries"][0]
    print(f"run_id={entry['run_id']} mr_id={entry['mr_id']} "
          f"metric={entry['metric_name']}={entry['metric_value']:.3e} "
          f"verdict={entry['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
