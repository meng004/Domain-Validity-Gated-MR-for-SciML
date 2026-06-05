"""Shared run-manifest contract.

Single source of truth for the run-manifest field set, the metric-ledger field
set, and the flat ``key: value`` parser. Both the validator
(``validate_experiment_protocol.py``) and the runner (``run_real_sut_mr.py``)
import from here so the contract cannot drift between them.
"""
from __future__ import annotations

import re


# Fields a run manifest must record before a real-SUT run can be trusted.
MANIFEST_REQUIRED_FIELDS = [
    "run_id",
    "sut_id",
    "sut_repo",
    "sut_commit",
    "checkpoint_path",
    "checkpoint_sha256",
    "dataset_root",
    "source_case_path",
    "mr_id",
    "command",
    "raw_output_dir",
    "seed",
    "device",
    "python_version",
    "framework_version",
]

# Fields every relation-level metric-ledger entry must carry.
METRIC_LEDGER_FIELDS = [
    "run_id",
    "sut_id",
    "mr_id",
    "source_case_id",
    "follow_up_case_id",
    "metric_name",
    "metric_value",
    "tolerance",
    "verdict",
    "evidence_artifact",
]

# Raw outputs a node-permutation run must persist before a verdict is trusted.
REQUIRED_RAW_OUTPUTS = [
    "source_output",
    "follow_up_output",
    "mapped_output",
]


def parse_flat_manifest(text: str) -> dict[str, str]:
    """Parse a flat ``key: value`` manifest into a dict.

    Comment lines and blank lines are ignored; values are stripped of
    surrounding quotes. Nested structures are unsupported on purpose: the run
    manifest is deliberately flat so it is trivially auditable.
    """
    fields: dict[str, str] = {}
    for raw_line in text.splitlines():
        if raw_line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_]+):\s*(.*?)\s*$", raw_line)
        if match:
            key, value = match.group(1), match.group(2).strip().strip('"').strip("'")
            fields[key] = value
    return fields


def missing_manifest_fields(fields: dict[str, str]) -> list[str]:
    return [name for name in MANIFEST_REQUIRED_FIELDS if not fields.get(name)]
