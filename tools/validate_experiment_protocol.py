from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path


REAL_SUT_REQUIRED_ENV = [
    "METBENCH_MGN_DATA_ROOT",
    "METBENCH_MGN_REPO",
    "METBENCH_MGN_CHECKPOINT",
]


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


REQUIRED_FILES = {
    "score_task": "research_assets/experiments/score-task.yml",
    "experiment_ledger": "research_assets/experiments/experiment-ledger.yml",
    "claim_ledger": "research_assets/experiments/claim-ledger.yml",
    "evidence_package": "research_assets/experiments/evidence-package.md",
    "protocol_note": "paper/20_experiment_empirical_protocol.md",
}


def error(asset: str, path: Path, message: str) -> dict[str, str]:
    return {"asset": asset, "path": str(path), "message": message}


def read_text(path: Path, asset: str) -> tuple[str, list[dict[str, str]]]:
    if not path.exists():
        return "", [error(asset, path, "missing file")]
    return path.read_text(encoding="utf-8"), []


def require_markers(text: str, markers: list[str], asset: str, path: Path) -> list[dict[str, str]]:
    return [
        error(asset, path, f"missing marker: {marker}")
        for marker in markers
        if marker not in text
    ]


FORBIDDEN_EMPIRICAL_PATTERNS = [
    re.compile(r"^\s*status:\s*['\"]?(passed|failed)['\"]?\s*$", re.IGNORECASE),
    re.compile(r"^\s*outcome:\s*['\"]?(passed|failed)['\"]?\s*$", re.IGNORECASE),
    re.compile(r"^\s*(violation_rate|accuracy_improvement|baseline_superiority)\s*:", re.IGNORECASE),
]


def reject_forbidden_empirical_markers(
    text: str, asset: str, path: Path
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern in FORBIDDEN_EMPIRICAL_PATTERNS:
            if pattern.search(line):
                errors.append(
                    error(
                        asset,
                        path,
                        f"forbidden empirical marker on line {line_number}: {line.strip()}",
                    )
                )
    return errors


def split_yaml_list_items(text: str) -> list[list[str]]:
    items: list[list[str]] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        if re.match(r"^\s*-\s+", raw_line):
            if current:
                items.append(current)
            current = [raw_line]
        elif current:
            current.append(raw_line)
    if current:
        items.append(current)
    return items


def split_run_items(text: str) -> list[list[str]]:
    items: list[list[str]] = []
    current: list[str] = []
    for raw_line in text.splitlines():
        if re.match(r"^\s*-\s+run_id:", raw_line):
            if current:
                items.append(current)
            current = [raw_line]
        elif current:
            current.append(raw_line)
    if current:
        items.append(current)
    return items


def yaml_scalar(item: list[str], key: str) -> str | None:
    pattern = re.compile(rf"^\s*(?:-\s*)?{re.escape(key)}:\s*(.+?)\s*$")
    for line in item:
        match = pattern.match(line)
        if match:
            return match.group(1).strip().strip('"').strip("'")
    return None


def parse_flat_manifest(text: str) -> dict[str, str]:
    """Parse a flat ``key: value`` manifest into a dict.

    Comments and blank lines are ignored. Values are stripped of surrounding
    quotes. Nested structures are not supported on purpose: the run manifest is
    deliberately flat so it is trivially auditable.
    """
    fields: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0] if raw_line.lstrip().startswith("#") else raw_line
        match = re.match(r"^([A-Za-z0-9_]+):\s*(.*?)\s*$", line)
        if match:
            key, value = match.group(1), match.group(2).strip().strip('"').strip("'")
            fields[key] = value
    return fields


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_run_manifest(path: Path) -> list[dict[str, str]]:
    """Field-presence contract for a run manifest.

    Every required field must be present and non-empty. Placeholder values are
    accepted here (the example template uses them); artifact verification is a
    separate, stronger gate applied only to runs referenced by the ledger.
    """
    text, errors = read_text(Path(path), "run_manifest")
    if errors:
        return errors
    fields = parse_flat_manifest(text)
    for required in MANIFEST_REQUIRED_FIELDS:
        value = fields.get(required, "")
        if not value:
            errors.append(
                error("run_manifest", Path(path), f"missing manifest field: {required}")
            )
    return errors


def validate_run_manifest_contract(root: Path) -> list[dict[str, str]]:
    manifest_dir = root / "research_assets" / "experiments" / "manifests"
    example = manifest_dir / "node_permutation_real_sut.example.yml"
    if not example.exists():
        return [error("run_manifest", example, "missing example run manifest")]
    errors: list[dict[str, str]] = []
    for manifest_path in sorted(manifest_dir.glob("*.yml")):
        errors.extend(validate_run_manifest(manifest_path))
    return errors


def verify_manifest_artifacts(root: Path, manifest_path: Path) -> list[dict[str, str]]:
    """Artifact gate: a run manifest is only trustworthy when its recorded
    artifacts actually exist on disk and the checkpoint hashes to the recorded
    ``checkpoint_sha256``.

    This replaces the earlier prose-only precondition with an on-disk check.
    """
    errors = validate_run_manifest(manifest_path)
    if errors:
        return errors
    fields = parse_flat_manifest(manifest_path.read_text(encoding="utf-8"))

    checkpoint = root / fields["checkpoint_path"]
    if not checkpoint.exists():
        errors.append(
            error("real_sut_preconditions", manifest_path,
                  f"checkpoint_path does not exist: {fields['checkpoint_path']}")
        )
    else:
        actual = sha256_file(checkpoint)
        if actual != fields["checkpoint_sha256"]:
            errors.append(
                error("real_sut_preconditions", manifest_path,
                      f"checkpoint_sha256 mismatch: manifest={fields['checkpoint_sha256']} "
                      f"actual={actual}")
            )

    for field in ("source_case_path", "raw_output_dir"):
        target = root / fields[field]
        if not target.exists():
            errors.append(
                error("real_sut_preconditions", manifest_path,
                      f"{field} does not exist: {fields[field]}")
            )

    metric_ledger = root / fields["raw_output_dir"] / "metric_ledger.json"
    if not metric_ledger.exists():
        # Allow the ledger to sit beside the manifest as well.
        alt = manifest_path.parent / "metric_ledger.json"
        if not alt.exists():
            errors.append(
                error("real_sut_preconditions", manifest_path,
                      "metric ledger missing: expected metric_ledger.json next to raw outputs")
            )
    return errors


def validate_protocol_files(root: Path) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for relative_path in REQUIRED_FILES.values():
        path = root / relative_path
        if not path.exists():
            errors.append(error("experiment_protocol_files", path, "missing file"))
    return errors


def validate_score_task(root: Path) -> list[dict[str, str]]:
    path = root / REQUIRED_FILES["score_task"]
    text, errors = read_text(path, "score_task")
    if errors:
        return errors
    markers = [
        "research_question:",
        "study_type: \"software-testing\"",
        "MeshGraphNets-family cylinder-flow",
        "primary: \"relation-level verdict coverage and evidence completeness\"",
        "Manual expert MR design",
        "Generic automatic MR generation scope contrast",
        "LLM-generated candidate MRs",
        "Pure rollout accuracy",
        "forbidden_generalizations:",
        "No baseline superiority claim before matched run artifacts exist",
        "stop_condition:",
        "run_manifest_contract:",
        "required_env:",
        "command_template:",
        "source_case_path:",
        "follow_up_case_path:",
        "metric_ledger_fields:",
        "claim_upgrade_rule:",
        "baseline_scoring_contract:",
        "candidate_mr_count",
        "validity_rubric_decision",
        "executable_verdict_coverage",
        "evidence_completeness",
        "review_effort",
    ]
    errors = require_markers(text, markers, "score_task", path)
    for line in text.splitlines():
        match = re.match(r"^\s*command_template:\s*(.+?)\s*$", line)
        if match:
            value = match.group(1).strip().strip('"').strip("'")
            if value.startswith("rtk "):
                errors.append(
                    error(
                        "score_task",
                        path,
                        "command_template must not use the cloud-shell-invalid 'rtk' "
                        f"prefix so the recorded command is runnable: {value}",
                    )
                )
    return errors


def validate_experiment_ledger(root: Path) -> list[dict[str, str]]:
    path = root / REQUIRED_FILES["experiment_ledger"]
    text, errors = read_text(path, "experiment_ledger")
    if errors:
        return errors
    markers = [
        "run_id: \"fixture-node-permutation-run-001\"",
        "status: \"observed-fixture-only\"",
        "sut_execution: \"not-run\"",
        "run_id: \"real-sut-echowve-blocked\"",
        "run_id: \"real-sut-physicsnemo-blocked\"",
        "run_id: \"real-sut-third-implementation-blocked\"",
        "status: \"blocked\"",
        "METBENCH_MGN_DATA_ROOT",
        "METBENCH_MGN_REPO",
        "METBENCH_MGN_CHECKPOINT",
        "primary: null",
        "keep_failed_runs: true",
    ]
    errors.extend(require_markers(text, markers, "experiment_ledger", path))
    errors.extend(reject_forbidden_empirical_markers(text, "experiment_ledger", path))
    for item_index, item in enumerate(split_run_items(text)):
        run_id = yaml_scalar(item, "run_id")
        if not (run_id and run_id.startswith("real-sut-")):
            continue
        status = yaml_scalar(item, "status")
        if status == "blocked":
            # A blocked real run must record not-run and keep its missing
            # prerequisite markers so the gap stays explicit.
            if yaml_scalar(item, "sut_execution") != "not-run":
                errors.append(
                    error(
                        "experiment_ledger",
                        path,
                        f"real SUT run {item_index} sut_execution must remain not-run",
                    )
                )
            joined = "\n".join(item)
            for marker in [
                "METBENCH_MGN_DATA_ROOT",
                "METBENCH_MGN_REPO",
                "METBENCH_MGN_CHECKPOINT",
                "exact command",
                "raw output artifact path",
                "primary: null",
            ]:
                if marker not in joined:
                    errors.append(
                        error(
                            "experiment_ledger",
                            path,
                            f"real SUT run {item_index} missing blocked prerequisite marker: {marker}",
                        )
                    )
        else:
            # A non-blocked (observed) real run must point at a run manifest;
            # the manifest's artifacts are verified by the artifact gate. Without
            # a manifest the run has no evidence and must remain blocked.
            if not yaml_scalar(item, "manifest"):
                errors.append(
                    error(
                        "experiment_ledger",
                        path,
                        f"real SUT run {item_index} status must remain blocked "
                        "until it references a verified run manifest",
                    )
                )
            if yaml_scalar(item, "sut_execution") != "run":
                errors.append(
                    error(
                        "experiment_ledger",
                        path,
                        f"real SUT run {item_index} observed run must record "
                        "sut_execution: run",
                    )
                )
    return errors


def validate_claim_ledger(root: Path) -> list[dict[str, str]]:
    path = root / REQUIRED_FILES["claim_ledger"]
    text, errors = read_text(path, "claim_ledger")
    if errors:
        return errors
    markers = [
        "claim_id: \"C1-fixture-asset-path\"",
        "status: \"observed\"",
        "research_assets/runs/node_permutation_fixture_verdict.json",
        "claim_id: \"C2-real-sut-verdicts\"",
        "status: \"blocked\"",
        "claim_id: \"C3-baseline-comparison\"",
        "status: \"blocked\"",
        "claim_id: \"C4-rubric-decision-coverage\"",
        "status: \"qualified\"",
        "blocked_reason:",
        "wording_allowed:",
    ]
    errors.extend(require_markers(text, markers, "claim_ledger", path))
    errors.extend(reject_forbidden_empirical_markers(text, "claim_ledger", path))
    return errors


def validate_real_sut_preconditions(
    root: Path, env: dict[str, str] | None = None
) -> list[dict[str, str]]:
    """Fail-closed **artifact** gate for real-SUT runs.

    A ``real-sut-*`` run may only leave ``blocked``/``not-run`` when it carries a
    ``manifest:`` reference whose recorded artifacts actually exist on disk and
    whose checkpoint hashes to the recorded ``checkpoint_sha256``. This executes
    the "前置条件检查" as code: it checks path existence, the SUT commit record,
    and the checkpoint sha256, rather than merely checking that environment
    variables are present. A blocked run is always acceptable.

    ``env`` is retained for compatibility and lets callers reason about the
    originally-planned METBENCH_MGN_* subjects; the artifact gate is stronger
    than (and subsumes) an env-presence check.
    """
    env = os.environ if env is None else env
    path = root / REQUIRED_FILES["experiment_ledger"]
    text, errors = read_text(path, "real_sut_preconditions")
    if errors:
        return errors
    for item in split_run_items(text):
        run_id = yaml_scalar(item, "run_id")
        if not run_id or not run_id.startswith("real-sut-"):
            continue
        status = yaml_scalar(item, "status")
        sut_execution = yaml_scalar(item, "sut_execution")
        if status == "blocked":
            # Blocked is always allowed; ledger-marker checks live elsewhere.
            continue

        manifest_rel = yaml_scalar(item, "manifest")
        verified = False
        if manifest_rel:
            manifest_path = root / manifest_rel
            if not manifest_path.exists():
                errors.append(
                    error(
                        "real_sut_preconditions",
                        path,
                        f"manifest for {run_id} does not exist: {manifest_rel}",
                    )
                )
            else:
                artifact_errors = verify_manifest_artifacts(root, manifest_path)
                errors.extend(artifact_errors)
                verified = not artifact_errors

        if not verified:
            errors.append(
                error(
                    "real_sut_preconditions",
                    path,
                    f"real SUT run {run_id} must stay blocked until its run "
                    "manifest artifacts verify (checkpoint sha256, raw outputs, "
                    "metric ledger)",
                )
            )
            errors.append(
                error(
                    "real_sut_preconditions",
                    path,
                    f"real SUT run {run_id} must stay not-run until its run "
                    "manifest artifacts verify",
                )
            )
        elif sut_execution != "run":
            errors.append(
                error(
                    "real_sut_preconditions",
                    path,
                    f"real SUT run {run_id} has a verified manifest and must "
                    "record sut_execution: run",
                )
            )
    return errors


def validate_protocol_note(root: Path) -> list[dict[str, str]]:
    path = root / REQUIRED_FILES["protocol_note"]
    text, errors = read_text(path, "protocol_note")
    if errors:
        return errors
    markers = [
        "## 1. 实验目标",
        "## 2. 分层实验设计",
        "## 3. 实证矩阵",
        "## 4. 指标与判定",
        "## 5. Baseline",
        "## 6. 证据门槛",
        "## 7. 当前 pilot 结果与 blocked 项",
        "不能写成 Results",
        "三个 METBENCH 计划的真实 SUT execution 仍 blocked",
        "single-SUT / single-MR / single-case pilot",
    ]
    return require_markers(text, markers, "protocol_note", path)


def validate_repo(root: Path) -> list[dict[str, str]]:
    root = Path(root)
    errors: list[dict[str, str]] = []
    errors.extend(validate_protocol_files(root))
    errors.extend(validate_score_task(root))
    errors.extend(validate_run_manifest_contract(root))
    errors.extend(validate_experiment_ledger(root))
    errors.extend(validate_real_sut_preconditions(root))
    errors.extend(validate_claim_ledger(root))
    errors.extend(validate_protocol_note(root))
    return errors


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    failures = validate_repo(repo_root)
    for failure in failures:
        print(f"{failure['asset']}: {failure['path']}: {failure['message']}")
    raise SystemExit(1 if failures else 0)
