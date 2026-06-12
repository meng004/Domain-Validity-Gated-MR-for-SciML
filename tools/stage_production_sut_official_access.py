"""Record official access/data/checkpoint/API staging for P0c production SUTs.

This script is deliberately a staging auditor, not a workflow runner. It records
what official sources are reachable or locally staged and keeps Task 3--5 closed
until each selected production object has complete official data/checkpoint/API
artifacts plus raw outputs and metric ledgers.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/production-grade-sut-extension/official_access_staging_report.json"
NGC_ARCHIVE = Path("/workspace/physicsnemo_staged_assets/mgn/ngc/modulus_datasets_cylinder-flow_v1.zip")
NGC_DATASET_ZIP = Path("/workspace/physicsnemo_staged_assets/mgn/ngc/dataset.zip")
DEEPMIND_TFRECORD_DIR = Path("/workspace/physicsnemo_staged_assets/mgn/cylinder_flow")
REQUIRED_DEEPMIND = ["meta.json", "train.tfrecord", "valid.tfrecord", "test.tfrecord"]


def sha256_prefix(path: Path, prefix: int = 16) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:prefix]


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
        "sha256_prefix": sha256_prefix(path),
    }


def zip_entries(path: Path, limit: int = 20) -> list[str]:
    if not path.exists():
        return []
    try:
        with zipfile.ZipFile(path) as zf:
            return zf.namelist()[:limit]
    except zipfile.BadZipFile:
        return []


def http_probe(url: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["curl", "-L", "-I", "--max-time", "20", url],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return {"checked": False, "reachable": False, "status_code": None, "reason": "curl not available"}
    status_codes: list[int] = []
    for line in result.stdout.splitlines():
        if line.startswith("HTTP/"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                status_codes.append(int(parts[1]))
    final_status = status_codes[-1] if status_codes else None
    return {
        "checked": True,
        "reachable": final_status is not None and 200 <= final_status < 400,
        "status_code": final_status,
        "status_chain": status_codes,
        "stderr_tail": result.stderr[-300:],
    }


def build_report() -> dict[str, Any]:
    deepmind_files = {name: file_record(DEEPMIND_TFRECORD_DIR / name) for name in REQUIRED_DEEPMIND}
    deepmind_complete = all(rec["exists"] for rec in deepmind_files.values())
    deepmind_observed_bytes = sum(rec["bytes"] for rec in deepmind_files.values())
    mgn_checkpoint_staged = Path("/workspace/physicsnemo_staged_assets/mgn/checkpoints/checkpoint.pt").exists()

    ngc_archive = file_record(NGC_ARCHIVE)
    ngc_dataset = file_record(NGC_DATASET_ZIP)
    ngc_entries = zip_entries(NGC_ARCHIVE)
    dataset_entries = zip_entries(NGC_DATASET_ZIP)

    objects = [
        {
            "object_id": "physicsnemo-mgn-vortex-shedding",
            "official_doc_url": "https://docs.nvidia.com/physicsnemo/latest/physicsnemo/examples/cfd/vortex_shedding_mgn/README.html",
            "official_doc_reachable": True,
            "access_status": "partial-data-staged-but-workflow-blocked",
            "ngc_cylinder_flow_archive": {
                "resource_url": "https://api.ngc.nvidia.com/v2/resources/nvidia/modulus/modulus_datasets_cylinder-flow/versions/v1/zip",
                "resource_probe": http_probe("https://api.ngc.nvidia.com/v2/resources/nvidia/modulus/modulus_datasets_cylinder-flow/versions/v1/zip"),
                "local_archive_exists": ngc_archive["exists"],
                "local_archive_bytes": ngc_archive["bytes"],
                "local_archive_sha256_prefix": ngc_archive["sha256_prefix"],
                "nested_entries": ngc_entries,
                "dataset_zip_exists": ngc_dataset["exists"],
                "dataset_zip_bytes": ngc_dataset["bytes"],
                "dataset_zip_sha256_prefix": ngc_dataset["sha256_prefix"],
                "dataset_entries_preview": dataset_entries,
                "sufficiency_note": "This NGC archive is official cylinder-flow data for a PhysicsNeMo vortex-shedding example, but it is not the DeepMind train/valid/test TFRecord bundle required by vortex_shedding_mgn Task 3.",
            },
            "deepmind_tfrecord_bundle": {
                "source_prefix": "https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/",
                "external_stage_dir": str(DEEPMIND_TFRECORD_DIR),
                "required_files": REQUIRED_DEEPMIND,
                "files": deepmind_files,
            },
            "deepmind_tfrecord_bundle_complete": deepmind_complete,
            "deepmind_tfrecord_observed_bytes": deepmind_observed_bytes,
            "checkpoint_or_api_staged": mgn_checkpoint_staged,
            "raw_outputs_available": False,
            "metric_ledgers_available": False,
            "workflow_execution_allowed": False,
            "missing_for_workflow": [
                item
                for item, ok in (
                    ("complete_deepmind_tfrecord_bundle", deepmind_complete),
                    ("official_or_new_physicsnemo_checkpoint", mgn_checkpoint_staged),
                    ("raw_outputs", False),
                    ("metric_ledgers", False),
                )
                if not ok
            ],
            "blocker_reason": "Official NGC cylinder-flow archive and complete DeepMind TFRecord bundle are staged externally, but the MGN example still lacks a PhysicsNeMo checkpoint, raw outputs, and metric ledgers.",
        },
        {
            "object_id": "physicsnemo-aerographnet-external-aero",
            "official_doc_url": "https://docs.nvidia.com/deeplearning/physicsnemo/physicsnemo-core/examples/cfd/external_aerodynamics/aero_graph_net/README.html",
            "official_doc_reachable": True,
            "access_status": "blocked-access-request-required",
            "dataset_access_note": "The official docs state that full Ahmed Body dataset access must be requested from the NVIDIA PhysicsNeMo team; DrivAerNet has separate external download instructions.",
            "checkpoint_or_api_staged": False,
            "raw_outputs_available": False,
            "metric_ledgers_available": False,
            "workflow_execution_allowed": False,
            "missing_for_workflow": ["dataset_access", "checkpoint", "raw_outputs", "metric_ledgers"],
            "blocker_reason": "Full dataset/checkpoint access has not been granted by the NVIDIA PhysicsNeMo team, and no raw AeroGraphNet production outputs or ledgers exist.",
        },
        {
            "object_id": "physicsnemo-domino-external-aero",
            "official_doc_url": "https://docs.nvidia.com/physicsnemo/26.03/physicsnemo/examples/cfd/external_aerodynamics/domino/README.html",
            "official_nim_url": "https://catalog.ngc.nvidia.com/orgs/nim/teams/nvidia/containers/domino-automotive-aero",
            "official_doc_reachable": True,
            "access_status": "blocked-ngc-auth-and-gpu-container-required",
            "ngc_container_tag_probe": http_probe("https://api.ngc.nvidia.com/v2/org/nim/team/nvidia/containers/domino-automotive-aero/tags"),
            "nim_access_note": "DoMINO-Automotive-Aero NIM is a pre-trained containerized model, but pulling/running it requires NGC/API access, a large container, and GPU-capable runtime not staged here.",
            "checkpoint_or_api_staged": False,
            "raw_outputs_available": False,
            "metric_ledgers_available": False,
            "workflow_execution_allowed": False,
            "missing_for_workflow": ["ngc_api_key", "gpu_container_runtime", "checkpoint_or_service_endpoint", "raw_outputs", "metric_ledgers"],
            "blocker_reason": "NGC API key/container access and GPU-capable runtime are not staged, so no DoMINO production endpoint/checkpoint/raw outputs/ledgers exist.",
        },
    ]
    objects_by_id = {item["object_id"]: item for item in objects}
    return {
        "record_type": "production-sut-official-access-staging-report",
        "schema_version": "0.1.0",
        "generated_on": "2026-06-12",
        "aggregate_status": "blocked-official-access-incomplete",
        "task3_to_task5_workflows_allowed": False,
        "objects": objects,
        "objects_by_id": objects_by_id,
        "honesty_boundary": "This report records official source/access staging only. It is not a production workflow execution and contains no production MR verdicts.",
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"aggregate_status={report['aggregate_status']}")


if __name__ == "__main__":
    main()
