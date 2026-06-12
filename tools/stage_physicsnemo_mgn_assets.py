"""Record the PhysicsNeMo MGN official data/checkpoint staging attempt.

This is a staging report, not a workflow runner. The official DeepMind
cylinder_flow data source is public, but the complete train/valid/test TFRecord
bundle is large. This script inspects any partially staged files in the external
workspace path and keeps Task 3 closed until complete official data, checkpoint,
raw outputs, and metric ledgers exist.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/production-grade-sut-extension/physicsnemo_mgn_asset_staging_report.json"
STAGE_DIR = Path("/workspace/physicsnemo_staged_assets/mgn/cylinder_flow")
CHECKPOINT = Path("/workspace/physicsnemo_staged_assets/mgn/checkpoints/checkpoint.pt")
REQUIRED = ["meta.json", "train.tfrecord", "valid.tfrecord", "test.tfrecord"]


def file_record(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "bytes": 0, "sha256_prefix": None}
    h = hashlib.sha256()
    with path.open("rb") as fh:
        # Hash only what exists; partial large files are external workspace state and not committed.
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return {"exists": True, "bytes": path.stat().st_size, "sha256_prefix": h.hexdigest()[:16]}


def build_report() -> dict[str, Any]:
    files = {name: file_record(STAGE_DIR / name) for name in REQUIRED}
    present = [name for name, rec in files.items() if rec["exists"]]
    missing = [name for name, rec in files.items() if not rec["exists"]]
    observed_bytes = sum(rec["bytes"] for rec in files.values())
    checkpoint = file_record(CHECKPOINT)
    complete_data = not missing
    complete_checkpoint = checkpoint["exists"]
    if complete_data:
        download_note = "Official DeepMind cylinder_flow train/valid/test TFRecord bundle is completely staged in /workspace/physicsnemo_staged_assets; data is no longer the Task 3 blocker."
        datapipe_reason = "Skipped because Task 3 still lacks an official/new PhysicsNeMo checkpoint and production raw-output/metric-ledger workflow; data completeness alone is not a valid production MR execution."
        blocker_reason = "Official cylinder_flow data is now complete in external staging, but official/new PhysicsNeMo checkpoint, raw outputs, and metric ledgers are absent. Task 3 must remain blocked."
    else:
        download_note = "Official cylinder_flow data download was attempted in /workspace/physicsnemo_staged_assets. The full TFRecord bundle is large and remains incomplete in this coding container."
        datapipe_reason = "Skipped because the required train/valid/test TFRecord bundle is incomplete; instantiating the PhysicsNeMo datapipe on a partial TFRecord would not be a valid smoke test."
        blocker_reason = "Official cylinder_flow data is public but large and incomplete in this environment; official/new PhysicsNeMo checkpoint, raw outputs, and metric ledgers are absent. Task 3 must remain blocked."
    return {
        "record_type": "physicsnemo-mgn-asset-staging-report",
        "schema_version": "0.1.0",
        "generated_on": "2026-06-12",
        "object_id": "physicsnemo-mgn-vortex-shedding",
        "aggregate_status": "ready-for-task3" if complete_data and complete_checkpoint else "blocked-assets-incomplete",
        "official_data_source": {
            "public_gcs_url_prefix": "https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/",
            "required_files": REQUIRED,
            "license_context": "DeepMind MeshGraphNets dataset download script; external data staged outside git due size.",
        },
        "download_attempted": True,
        "download_attempt_note": download_note,
        "data_staging": {
            "external_stage_dir": str(STAGE_DIR),
            "official_data_staged": complete_data,
            "all_required_files_present": complete_data,
            "present_required_files": present,
            "missing_required_files": missing,
            "observed_bytes": observed_bytes,
            "files": files,
        },
        "checkpoint_staging": {
            "expected_checkpoint_path": str(CHECKPOINT),
            "official_checkpoint_staged": complete_checkpoint,
            "checkpoint_file": checkpoint,
            "note": "No official PhysicsNeMo MGN checkpoint or newly trained PhysicsNeMo checkpoint is staged yet.",
        },
        "datapipe_smoke_attempted": False,
        "datapipe_smoke_reason": datapipe_reason,
        "raw_outputs_available": False,
        "metric_ledgers_available": False,
        "task3_workflow_execution_allowed": False,
        "missing_for_task3": [
            item
            for item, ok in (
                ("complete_official_data", complete_data),
                ("official_checkpoint", complete_checkpoint),
                ("raw_outputs", False),
                ("metric_ledgers", False),
            )
            if not ok
        ],
        "blocker_reason": blocker_reason,
        "honesty_boundary": "This artifact records an official data/checkpoint staging attempt only. It is not a PhysicsNeMo MGN workflow execution and provides no production MR verdict.",
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"aggregate_status={report['aggregate_status']}")


if __name__ == "__main__":
    main()
