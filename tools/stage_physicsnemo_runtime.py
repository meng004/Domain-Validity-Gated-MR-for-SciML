"""Record the P0c PhysicsNeMo runtime staging gate.

This script is intentionally a pre-workflow staging probe. It verifies that the
Python package/runtime imports are available, records official example source
reachability, and keeps all production workflow execution gates closed until
official data/checkpoints/API credentials plus raw outputs and metric ledgers are
present.
"""
from __future__ import annotations

import importlib.metadata
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research_assets/runs/production-grade-sut-extension"
OUT = BASE / "physicsnemo_runtime_staging_report.json"

OBJECTS = [
    {
        "object_id": "physicsnemo-mgn-vortex-shedding",
        "official_doc_url": "https://docs.nvidia.com/physicsnemo/latest/physicsnemo/examples/cfd/vortex_shedding_mgn/README.html",
        "github_example_url": "https://github.com/NVIDIA/physicsnemo/tree/main/examples/cfd/vortex_shedding_mgn",
        "github_raw_probe_url": "https://raw.githubusercontent.com/NVIDIA/physicsnemo/main/examples/cfd/vortex_shedding_mgn/inference.py",
        "official_data_note": "DeepMind cylinder_flow dataset must be downloaded through raw_dataset/download_dataset.sh before PhysicsNeMo inference/training.",
        "official_checkpoint_note": "No committed official PhysicsNeMo MGN checkpoint is staged in this repository.",
        "expected_local_data_dir": "research_assets/runs/production-grade-sut-extension/staged_assets/physicsnemo-mgn-vortex-shedding/data",
        "expected_local_checkpoint": "research_assets/runs/production-grade-sut-extension/staged_assets/physicsnemo-mgn-vortex-shedding/checkpoint.pt",
    },
    {
        "object_id": "physicsnemo-aerographnet-external-aero",
        "official_doc_url": "https://docs.nvidia.com/physicsnemo/latest/physicsnemo/examples/cfd/external_aerodynamics/aero_graph_net/README.html",
        "github_example_url": "https://github.com/NVIDIA/physicsnemo/tree/main/examples/cfd/external_aerodynamics/aero_graph_net",
        "github_raw_probe_url": "https://raw.githubusercontent.com/NVIDIA/physicsnemo/main/examples/cfd/external_aerodynamics/aero_graph_net/inference.py",
        "official_data_note": "Ahmed Body data requires NVIDIA PhysicsNeMo team access; DrivAerNet data must be obtained through the documented external dataset instructions.",
        "official_checkpoint_note": "No official AeroGraphNet checkpoint is staged in this repository.",
        "expected_local_data_dir": "research_assets/runs/production-grade-sut-extension/staged_assets/physicsnemo-aerographnet-external-aero/data",
        "expected_local_checkpoint": "research_assets/runs/production-grade-sut-extension/staged_assets/physicsnemo-aerographnet-external-aero/checkpoint.pt",
    },
    {
        "object_id": "physicsnemo-domino-external-aero",
        "official_doc_url": "https://docs.nvidia.com/physicsnemo/latest/physicsnemo/examples/cfd/external_aerodynamics/domino/README.html",
        "github_example_url": "https://github.com/NVIDIA/physicsnemo/tree/main/examples/cfd/external_aerodynamics/domino",
        "github_raw_probe_url": "https://raw.githubusercontent.com/NVIDIA/physicsnemo/main/examples/cfd/external_aerodynamics/domino/test.py",
        "official_data_note": "DoMINO requires DrivAerML/CAE data curation, scaling factors, and raw STL/VTP/VTU test inputs or a documented pre-trained checkpoint route.",
        "official_checkpoint_note": "No DoMINO pre-trained checkpoint, scaling parameters, or API credential bundle is staged in this repository.",
        "expected_local_data_dir": "research_assets/runs/production-grade-sut-extension/staged_assets/physicsnemo-domino-external-aero/data",
        "expected_local_checkpoint": "research_assets/runs/production-grade-sut-extension/staged_assets/physicsnemo-domino-external-aero/checkpoint.pt",
    },
]

IMPORT_MODULES = [
    "physicsnemo",
    "physicsnemo.models.meshgraphnet",
    "physicsnemo.datapipes.gnn.vortex_shedding_dataset",
    "physicsnemo.datapipes.cae.domino_datapipe",
]


def version_or_missing(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def run_python(code: str, timeout: int = 30) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr_tail": completed.stderr[-1200:],
    }


def import_probe(module: str) -> dict[str, Any]:
    probe = run_python(f"import {module}; print('ok')")
    return {
        "module": module,
        "status": "ok" if probe["returncode"] == 0 else "failed",
        **probe,
    }


def url_probe(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "DVGMR-runtime-staging/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return {"checked": True, "reachable": True, "status_code": response.status, "final_url": response.url}
    except urllib.error.HTTPError as exc:
        return {"checked": True, "reachable": False, "status_code": exc.code, "error": str(exc)}
    except urllib.error.URLError as exc:
        return {"checked": True, "reachable": False, "status_code": None, "error": str(exc)}
    except TimeoutError as exc:
        return {"checked": True, "reachable": False, "status_code": None, "error": str(exc)}


def runtime_summary(import_probes: list[dict[str, Any]]) -> dict[str, Any]:
    torch_probe = run_python("import torch; print(torch.__version__); print(torch.cuda.is_available())")
    torchvision_probe = run_python("import torchvision; print(torchvision.__version__)")
    cuda_available = "\nTrue" in f"\n{torch_probe['stdout']}"
    return {
        "nvidia_physicsnemo_version": version_or_missing("nvidia-physicsnemo"),
        "torch_version": version_or_missing("torch"),
        "torchvision_version": version_or_missing("torchvision"),
        "physicsnemo_importable": any(item["module"] == "physicsnemo" and item["returncode"] == 0 for item in import_probes),
        "torch_importable": torch_probe["returncode"] == 0,
        "torchvision_importable": torchvision_probe["returncode"] == 0,
        "cuda_available": cuda_available,
        "gpu_runtime_available": cuda_available,
        "torch_probe": torch_probe,
        "torchvision_probe": torchvision_probe,
    }


def object_record(obj: dict[str, str]) -> dict[str, Any]:
    data_dir = ROOT / obj["expected_local_data_dir"]
    checkpoint = ROOT / obj["expected_local_checkpoint"]
    api_credentials = bool(False)
    raw_outputs_available = False
    metric_ledgers_available = False
    data_staged = data_dir.exists()
    checkpoint_staged = checkpoint.exists()
    missing = []
    if not data_staged:
        missing.append("official_data")
    if not checkpoint_staged:
        missing.append("official_checkpoint")
    if obj["object_id"] == "physicsnemo-domino-external-aero" and not api_credentials:
        missing.append("api_credentials_or_pretrained_checkpoint_route")
    if not raw_outputs_available:
        missing.append("raw_outputs")
    if not metric_ledgers_available:
        missing.append("metric_ledgers")
    return {
        **obj,
        "runtime_import_ready": True,
        "official_data_staged": data_staged,
        "official_checkpoint_staged": checkpoint_staged,
        "api_credentials_staged": api_credentials,
        "raw_outputs_available": raw_outputs_available,
        "metric_ledgers_available": metric_ledgers_available,
        "workflow_execution_allowed": False,
        "missing_for_workflow": missing,
        "github_source_probe": url_probe(obj["github_raw_probe_url"]),
    }


def build_report() -> dict[str, Any]:
    import_probes = [import_probe(module) for module in IMPORT_MODULES]
    runtime = runtime_summary(import_probes)
    objects = [object_record(obj) for obj in OBJECTS]
    return {
        "record_type": "physicsnemo-runtime-staging-report",
        "schema_version": "0.1.0",
        "generated_on": "2026-06-12",
        "aggregate_status": "partial-runtime-staged" if runtime["physicsnemo_importable"] else "blocked-runtime-not-importable",
        "runtime": runtime,
        "import_probes": import_probes,
        "objects": objects,
        "workflow_execution_allowed": False,
        "honesty_boundary": "PhysicsNeMo package/runtime imports are partially staged, but official data/checkpoints/API credentials, raw production outputs, and metric ledgers are still absent. Do not execute or claim Task 3--5 production workflows yet.",
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"aggregate_status={report['aggregate_status']}")


if __name__ == "__main__":
    main()
