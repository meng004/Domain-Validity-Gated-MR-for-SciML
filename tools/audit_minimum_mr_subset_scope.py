"""Build a scoped external-evidence audit from Minimum-MR-SubSet.

The audit widens the empirical context available to the manuscript without
claiming that this paper has executed additional primary SUTs. It reads the
committed ABD witness reports from the sibling repository and emits a compact
JSON record that can be cited from the manuscript and ledgers.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_REPO = Path("/private/tmp/minimum-mr-subset-audit")
DEFAULT_OUTPUT = Path(
    "research_assets/runs/minimum-mr-subset-external-scope-audit/"
    "minimum_mr_subset_scope_audit.json"
)
SOURCE_REPO = "https://github.com/meng004/Minimum-MR-SubSet"

WITNESS_PATHS = {
    "cylinder_flow_meshgraphnet": Path(
        "runs/abd-witness-cylinder-flow-mgn-runtime-20260605T021457Z/"
        "abd_witness_report.json"
    ),
    "burgers2d_pinn": Path(
        "runs/abd-witness-burgers2d-pinn-20260607T161215Z/"
        "abd_witness_report.json"
    ),
    "diffusion2d_pinn": Path(
        "runs/abd-witness-diffusion2d-pinn-20260608T032704Z/"
        "abd_witness_report.json"
    ),
}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"required witness report is missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"witness report must be an object: {path}")
    return data


def source_head(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"cannot read git HEAD from {repo}") from exc


def parse_report_counts(report_path: Path) -> dict[str, int]:
    text = report_path.read_text(encoding="utf-8")
    patterns = {
        "report_total_instances": r"Total parsed instances:\s*(\d+)",
        "report_real_instances": r"Real instances:\s*(\d+)",
        "report_pilot_instances": r"Pilot instances:\s*(\d+)",
        "report_real_true_fault_class_instances": (
            r"Real true-fault-class instances:\s*(\d+)"
        ),
    }
    counts: dict[str, int] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if not match:
            raise ValueError(f"missing report count {key} in {report_path}")
        counts[key] = int(match.group(1))
    return counts


def parse_instances_csv(instances_path: Path) -> dict[str, int]:
    rows = list(csv.DictReader(instances_path.open(encoding="utf-8")))
    return {
        "csv_total_instances": len(rows),
        "csv_real_instances": sum(row.get("kind") == "real" for row in rows),
        "csv_pilot_instances": sum(row.get("kind") == "pilot" for row in rows),
        "csv_real_true_fault_class_instances": sum(
            row.get("kind") == "real"
            and row.get("label_scope") == "true_fault_class"
            for row in rows
        ),
    }


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return False


def witness_row(sut_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    if sut_id == "cylinder_flow_meshgraphnet":
        honesty_boundary = (
            "External held-out-test MeshGraphNet cylinder-flow runtime witness "
            "from Minimum-MR-SubSet; it records true-fault-class ABD structure "
            "for the sibling repository and does not add a new primary SUT "
            "execution to this paper."
        )
        selected = data.get("selected_mrs", [])
        return {
            "sut_id": sut_id,
            "record_path": str(path),
            "status": data.get("status"),
            "label_scope": data.get("label_scope"),
            "kind": "real",
            "real_runtime_output": data.get("real_runtime_output"),
            "eval_split": data.get("eval_split"),
            "kstar": data.get("kstar"),
            "collapse": data.get("collapse"),
            "fault_classes_active": data.get("fault_classes_active"),
            "max_fault_class_signature_rank": data.get(
                "max_fault_class_signature_rank"
            ),
            "selected_mrs": selected,
            "honesty_boundary": honesty_boundary,
        }

    return {
        "sut_id": sut_id,
        "record_path": str(path),
        "status": data.get("status"),
        "label_scope": data.get("label_scope"),
        "kind": data.get("kind"),
        "submodule": data.get("submodule"),
        "submodule_commit": data.get("submodule_commit"),
        "checkpoint_sha256_prefix": data.get("checkpoint_sha256_prefix"),
        "kstar": data.get("kstar"),
        "collapse": as_bool(data.get("collapse")),
        "n_R": data.get("n_R"),
        "m_raw": data.get("m_raw"),
        "m_dedup": data.get("m_dedup"),
        "fault_classes_active": data.get("fault_classes_active"),
        "max_fault_class_signature_rank": data.get("max_fault_class_signature_rank"),
        "selected_mrs": data.get("selected_mrs", []),
        "honesty_boundary": data.get("honesty_boundary"),
    }


def build_audit(repo: Path) -> dict[str, Any]:
    if not repo.exists():
        raise FileNotFoundError(
            f"Minimum-MR-SubSet checkout not found at {repo}; clone {SOURCE_REPO} first"
        )

    report_path = repo / "runs/abd-analysis/REPORT.md"
    instances_path = repo / "runs/abd-analysis/instances.csv"
    if not report_path.exists() or not instances_path.exists():
        raise FileNotFoundError("ABD analysis report or instances.csv is missing")

    report_counts = parse_report_counts(report_path)
    csv_counts = parse_instances_csv(instances_path)

    witnesses: list[dict[str, Any]] = []
    for sut_id, rel_path in WITNESS_PATHS.items():
        data = read_json(repo / rel_path)
        row = witness_row(sut_id, rel_path, data)
        if row.get("status") != "PASS_WITNESS":
            raise ValueError(f"{sut_id} is not a PASS_WITNESS")
        if row.get("label_scope") != "true_fault_class":
            raise ValueError(f"{sut_id} is not true_fault_class scope")
        witnesses.append(row)

    return {
        "record_type": "minimum-mr-subset-external-scope-audit",
        "source_repo": SOURCE_REPO,
        "source_head": source_head(repo),
        "source_checkout": str(repo),
        "analysis_artifacts": {
            "report": "runs/abd-analysis/REPORT.md",
            "instances_csv": "runs/abd-analysis/instances.csv",
        },
        "external_real_rows": report_counts["report_real_instances"],
        "external_true_fault_class_rows": report_counts[
            "report_real_true_fault_class_instances"
        ],
        "csv_cross_check": csv_counts,
        "report_counts": report_counts,
        "primary_sci_ml_witnesses": witnesses,
        "manuscript_use": (
            "external witness evidence only; this audit does not add new primary "
            "SUT executions to this paper and must not be described as a "
            "cross-SUT pass-rate estimate"
        ),
        "honesty_boundary": (
            "The audit reads committed reports from the sibling Minimum-MR-SubSet "
            "repository. It widens empirical scope by showing comparable true-"
            "fault-class witness rows exist for a held-out cylinder-flow MGN "
            "runtime and two one-seed PINN PDE witnesses, but it is secondary "
            "provenance rather than a new experiment executed in this manuscript."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    audit = build_audit(args.repo)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
