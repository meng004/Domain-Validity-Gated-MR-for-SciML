"""Audit feasibility for the P0c production-grade PhysicsNeMo SUT extension.

This script deliberately performs only the plan's first gate: official-source
provenance checks plus minimal environment/package smoke attempts. It does not
fabricate toy substitutes when production checkpoints/data/runtime are absent.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import platform
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/production-grade-sut-extension/feasibility_report.json"

OBJECTS: list[dict[str, Any]] = [
    {
        "object_id": "physicsnemo-mgn-vortex-shedding",
        "name": "PhysicsNeMo MeshGraphNet transient vortex shedding",
        "official_url": "https://docs.nvidia.com/physicsnemo/latest/physicsnemo/examples/cfd/vortex_shedding_mgn/README.html",
        "repository": "https://github.com/NVIDIA/physicsnemo/tree/main/examples/cfd/vortex_shedding_mgn",
        "argument_role": "near-domain external-framework replication",
        "expected_command": "python examples/cfd/vortex_shedding_mgn/inference.py (after official data/checkpoint setup)",
        "candidate_relations": ["node/graph representation permutation", "geometry-conditioned mirror/domain relation", "rollout diagnostic"],
    },
    {
        "object_id": "physicsnemo-aerographnet-external-aero",
        "name": "PhysicsNeMo AeroGraphNet external aerodynamic evaluation",
        "official_url": "https://docs.nvidia.com/physicsnemo/latest/physicsnemo/examples/cfd/external_aerodynamics/aero_graph_net/README.html",
        "repository": "https://github.com/NVIDIA/physicsnemo/tree/main/examples/cfd/external_aerodynamics/aero_graph_net",
        "argument_role": "production external-aerodynamics geometry/task broadening",
        "expected_command": "python examples/cfd/external_aerodynamics/aero_graph_net/inference.py (after official data/checkpoint setup)",
        "candidate_relations": ["graph representation permutation", "integrated aerodynamic quantity consistency", "geometry-contract rejection/downgrade"],
    },
    {
        "object_id": "physicsnemo-domino-external-aero",
        "name": "PhysicsNeMo DoMINO external aerodynamics",
        "official_url": "https://docs.nvidia.com/physicsnemo/latest/physicsnemo/examples/cfd/external_aerodynamics/domino/README.html",
        "repository": "https://github.com/NVIDIA/physicsnemo/tree/main/examples/cfd/external_aerodynamics/domino",
        "argument_role": "non-GNN / neural-operator-style architecture broadening",
        "expected_command": "python examples/cfd/external_aerodynamics/domino/inference.py (after official data/checkpoint/API setup)",
        "candidate_relations": ["query/order contract audit", "point-cloud output mapping", "geometry-contract rejection/downgrade"],
    },
]


def probe_url(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "DVGMR-feasibility-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return {"checked": True, "reachable": True, "status_code": response.status, "final_url": response.url}
    except urllib.error.HTTPError as exc:
        return {"checked": True, "reachable": False, "status_code": exc.code, "error": str(exc)}
    except urllib.error.URLError as exc:
        return {"checked": True, "reachable": False, "status_code": None, "error": str(exc)}
    except TimeoutError as exc:
        return {"checked": True, "reachable": False, "status_code": None, "error": str(exc)}


def run_probe(command: list[str], timeout: int = 35) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def physicsnemo_version_probe() -> dict[str, Any]:
    pip_probe = run_probe([sys.executable, "-m", "pip", "index", "versions", "nvidia-physicsnemo"])
    dry_run_probe = run_probe([sys.executable, "-m", "pip", "install", "--dry-run", "nvidia-physicsnemo==2.1.1"], timeout=90)
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "physicsnemo_importable": importlib.util.find_spec("physicsnemo") is not None,
        "torch_importable": importlib.util.find_spec("torch") is not None,
        "pip_index_versions": pip_probe,
        "install_dry_run": dry_run_probe,
        "install_not_performed_reason": "Dependency probe shows a heavy CUDA/Torch stack; production inference remains blocked until a controlled GPU/runtime environment is provisioned.",
    }


def build_object(entry: dict[str, Any], version_probe: dict[str, Any]) -> dict[str, Any]:
    doc_probe = probe_url(entry["official_url"])
    package_missing = not version_probe["physicsnemo_importable"]
    torch_missing = not version_probe["torch_importable"]
    blocker_reasons: list[str] = []
    if not doc_probe["reachable"]:
        blocker_reasons.append("official documentation URL was not reachable during audit")
    if package_missing:
        blocker_reasons.append("nvidia-physicsnemo/physicsnemo is not installed/importable in the current environment")
    if torch_missing:
        blocker_reasons.append("torch is not installed/importable in the current environment")
    blocker_reasons.append("official checkpoint/data/API artifacts have not yet been staged in this repository")

    smoke_outcome = "blocked" if blocker_reasons else "failed"
    status = "blocked" if blocker_reasons else "partial"
    return {
        **entry,
        "provenance": "NVIDIA PhysicsNeMo official example",
        "official_doc_probe": doc_probe,
        "version_probe": {
            "physicsnemo_importable": version_probe["physicsnemo_importable"],
            "torch_importable": version_probe["torch_importable"],
            "python": version_probe["python"],
            "platform": version_probe["platform"],
        },
        "model_checkpoint_availability": "not_staged",
        "data_availability": "not_staged",
        "hardware_need": "GPU-class PhysicsNeMo runtime expected for production inference; torch importability alone is insufficient without PhysicsNeMo plus official data/checkpoint/API staging.",
        "license_note": "Use NVIDIA PhysicsNeMo and dataset licenses before staging checkpoints/data.",
        "status": status,
        "status_reason": "; ".join(blocker_reasons) if blocker_reasons else "Environment probes passed, but no production raw outputs were generated by this audit.",
        "smoke_attempt": {
            "attempted": True,
            "attempt_kind": "official minimal inference preflight",
            "command_target": entry["expected_command"],
            "outcome": smoke_outcome,
            "blocked_before_inference": bool(blocker_reasons),
            "reason": "; ".join(blocker_reasons),
        },
        "artifact_gate": {
            "claim_state": "blocked",
            "workflow_claim_allowed": False,
            "raw_outputs_available": False,
            "metric_ledgers_available": False,
            "source_followup_outputs_available": False,
            "relation_verdicts_available": False,
        },
        "fallback_policy": [
            "blocked rather than replaced",
            "do not substitute a local PointMLP/FNO/MGN variant for this production object",
            "do not add manuscript result wording until raw production outputs and metric ledgers exist",
        ],
    }


def main() -> None:
    version_probe = physicsnemo_version_probe()
    objects = [build_object(entry, version_probe) for entry in OBJECTS]
    report = {
        "record_type": "production-grade-sut-feasibility-audit",
        "created_utc": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "scope": "P0c production-grade external SciML/CFD SUT feasibility",
        "selection_standard": "argument-function-first",
        "aggregate_status": "blocked" if any(obj["status"] == "blocked" for obj in objects) else "partial",
        "manuscript_result_claim_added": False,
        "objects": objects,
        "package_probe_summary": version_probe,
        "honesty_boundary": "This audit establishes official-source feasibility/blockers only. Production workflows have not produced raw outputs yet, so PhysicsNeMo/AeroGraphNet/DoMINO primary workflow results remain unclaimed.",
        "next_gate": "Stage official data/checkpoints/runtime and rerun object-specific workflows only after this blocked feasibility gate is resolved.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"aggregate_status={report['aggregate_status']}")


if __name__ == "__main__":
    main()
