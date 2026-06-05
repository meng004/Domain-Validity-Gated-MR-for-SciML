# Experiment Empirical Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an evidence-gated experimental and empirical protocol for the MeshGraphNets cylinder-flow MR paper without inventing SUT results.

**Architecture:** Create a small Research Evidence Gate package: score task, experiment ledger, claim ledger, evidence package, and a manuscript-facing protocol note. A Python standard-library validator and tests enforce that real SUT claims remain blocked unless dataset, model repository, checkpoint, command, and output artifacts are recorded.

**Tech Stack:** Python standard library, `unittest`, YAML-like text ledgers, Markdown protocol notes, existing JSON MR assets.

---

## Evidence Boundaries

- The current package may use the existing fixture-level node-permutation verdict as asset-plumbing evidence.
- The current package must not claim real MeshGraphNets SUT inference, empirical pass/fail rates, violation rates, model reliability, seeded-fault detection, or baseline superiority.
- Real SUT experiments are allowed to move from `blocked` to `planned` only after concrete dataset, repository, checkpoint, and command paths are recorded.
- Baselines are protocol commitments until matching run artifacts exist.

## File Structure

- Create: `tests/test_experiment_protocol.py`
  - Tests required evidence-gate files, blocked SUT claims, baseline coverage, and protocol wording.
- Create: `tools/validate_experiment_protocol.py`
  - Validates the experiment package with standard-library text checks.
- Create: `research_assets/experiments/score-task.yml`
  - Defines RQ, subject systems, interventions, metrics, baselines, inputs, outputs, stopping rule, and claim limits.
- Create: `research_assets/experiments/experiment-ledger.yml`
  - Records current fixture run as observed asset plumbing and real SUT runs as blocked until artifacts exist.
- Create: `research_assets/experiments/claim-ledger.yml`
  - Classifies claims as supported, qualified, blocked, or speculative.
- Create: `research_assets/experiments/evidence-package.md`
  - Human-readable handoff for manuscript writing.
- Create: `paper/20_experiment_empirical_protocol.md`
  - Paper-facing experimental and empirical design note.

## Task 1: Experiment Protocol Validator

**Files:**
- Create: `tests/test_experiment_protocol.py`
- Create: `tools/validate_experiment_protocol.py`

- [x] **Step 1: Write failing tests**

Create `tests/test_experiment_protocol.py`:

```python
from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_experiment_protocol.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_experiment_protocol", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExperimentProtocolTests(unittest.TestCase):
    def test_experiment_protocol_files_exist_and_have_required_sections(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "experiment_protocol_files"], errors)

    def test_score_task_defines_subject_metrics_baselines_and_stopping_rule(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "score_task"], errors)

    def test_experiment_ledger_keeps_real_sut_runs_blocked_without_artifacts(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "experiment_ledger"], errors)

    def test_claim_ledger_blocks_empirical_result_claims(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "claim_ledger"], errors)

    def test_protocol_note_preserves_supported_and_blocked_boundaries(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "protocol_note"], errors)


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run RED**

Run:

```sh
rtk python3 -B -m unittest tests/test_experiment_protocol.py
```

Expected: FAIL because `tools/validate_experiment_protocol.py` and experiment package files do not exist.

Observed:

```text
rtk python3 -B -m unittest tests/test_experiment_protocol.py
FAILED (errors=5)
FileNotFoundError: tools/validate_experiment_protocol.py
```

After code-quality review, additional RED checks were added for fail-closed
empirical-result detection and operational run-manifest/baseline contracts:

```text
rtk python3 -B -m unittest tests/test_experiment_protocol.py
FAILED
test_experiment_ledger_rejects_empirical_result_fields_before_real_runs
test_claim_ledger_rejects_baseline_superiority_before_matched_runs
test_score_task_contains_run_manifest_and_baseline_scoring_contracts
```

- [x] **Step 3: Implement minimal validator**

Create `tools/validate_experiment_protocol.py`:

```python
from __future__ import annotations

from pathlib import Path


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
        "LLM-generated candidate MRs",
        "Pure rollout accuracy",
        "forbidden_generalizations:",
        "No baseline superiority claim before matched run artifacts exist",
        "stop_condition:",
    ]
    return require_markers(text, markers, "score_task", path)


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
        "status: \"blocked\"",
        "METBENCH_MGN_DATA_ROOT",
        "METBENCH_MGN_REPO",
        "METBENCH_MGN_CHECKPOINT",
        "primary: null",
        "keep_failed_runs: true",
    ]
    errors.extend(require_markers(text, markers, "experiment_ledger", path))
    forbidden = [
        "status: \"passed\"",
        "status: \"failed\"",
        "violation_rate:",
        "accuracy_improvement:",
        "baseline_superiority:",
    ]
    for marker in forbidden:
        if marker in text:
            errors.append(error("experiment_ledger", path, f"forbidden marker before real runs: {marker}"))
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
    return require_markers(text, markers, "claim_ledger", path)


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
        "## 7. 当前 blocked 项",
        "不能写成 Results",
        "真实 MeshGraphNets SUT execution remains blocked",
    ]
    return require_markers(text, markers, "protocol_note", path)


def validate_repo(root: Path) -> list[dict[str, str]]:
    root = Path(root)
    errors: list[dict[str, str]] = []
    errors.extend(validate_protocol_files(root))
    errors.extend(validate_score_task(root))
    errors.extend(validate_experiment_ledger(root))
    errors.extend(validate_claim_ledger(root))
    errors.extend(validate_protocol_note(root))
    return errors


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    failures = validate_repo(repo_root)
    for failure in failures:
        print(f"{failure['asset']}: {failure['path']}: {failure['message']}")
    raise SystemExit(1 if failures else 0)
```

- [x] **Step 4: Run expected partial GREEN**

Run:

```sh
rtk python3 -B -m unittest tests/test_experiment_protocol.py
```

Expected: still FAIL because experiment files are missing, but the validator imports correctly.

Observed:

```text
rtk python3 -B -m unittest tests/test_experiment_protocol.py
FAILED (failures=5)
Validator imported; score-task.yml, experiment-ledger.yml, claim-ledger.yml,
evidence-package.md, and paper/20_experiment_empirical_protocol.md were missing.
```

## Task 2: Evidence Gate Artifacts

**Files:**
- Create: `research_assets/experiments/score-task.yml`
- Create: `research_assets/experiments/experiment-ledger.yml`
- Create: `research_assets/experiments/claim-ledger.yml`
- Create: `research_assets/experiments/evidence-package.md`

- [x] **Step 1: Create score task**

Create `research_assets/experiments/score-task.yml` with the research question, SUT scope, MR set, baselines, primary/secondary metrics, reproducibility controls, outputs, stopping rule, and forbidden generalizations. Required baselines are:

```text
Manual expert MR design
Generic automatic MR generation scope contrast
LLM-generated candidate MRs
Pure rollout accuracy
```

Primary metric must be:

```text
relation-level verdict coverage and evidence completeness
```

- [x] **Step 2: Create experiment ledger**

Create `research_assets/experiments/experiment-ledger.yml` with one observed fixture-only run and blocked real-SUT runs:

```text
run_id: "fixture-node-permutation-run-001"
status: "observed-fixture-only"
sut_execution: "not-run"
```

Blocked runs must include:

```text
real-sut-echowve-blocked
real-sut-physicsnemo-blocked
real-sut-third-implementation-blocked
```

Each blocked run must name missing prerequisites: `METBENCH_MGN_DATA_ROOT`, `METBENCH_MGN_REPO`, and `METBENCH_MGN_CHECKPOINT`.

- [x] **Step 3: Create claim ledger**

Create `research_assets/experiments/claim-ledger.yml` with at least four claims:

- `C1-fixture-asset-path`: `observed`
- `C2-real-sut-verdicts`: `blocked`
- `C3-baseline-comparison`: `blocked`
- `C4-rubric-decision-coverage`: `qualified`

No claim may say real SUT inference has been run.

- [x] **Step 4: Create evidence package**

Create `research_assets/experiments/evidence-package.md` with sections from the Research Evidence Gate template. It must include a claim gate table and a next-experiments list.

- [x] **Step 5: Run GREEN for evidence files**

Run:

```sh
rtk python3 -B -m unittest tests/test_experiment_protocol.py
rtk python3 -B tools/validate_experiment_protocol.py
```

Expected: tests may still fail only because `paper/20_experiment_empirical_protocol.md` is missing.

Observed:

```text
rtk python3 -B -m unittest tests/test_experiment_protocol.py
3/5 tests passed; remaining failures were protocol_note missing.

rtk python3 -B tools/validate_experiment_protocol.py
Only protocol_note missing was reported.
```

## Task 3: Paper-Facing Experimental And Empirical Plan

**Files:**
- Create: `paper/20_experiment_empirical_protocol.md`

- [x] **Step 1: Create protocol note**

Create `paper/20_experiment_empirical_protocol.md` with these exact sections:

```markdown
## 1. 实验目标
## 2. 分层实验设计
## 3. 实证矩阵
## 4. 指标与判定
## 5. Baseline
## 6. 证据门槛
## 7. 当前 blocked 项
```

It must say:

```text
真实 MeshGraphNets SUT execution remains blocked
```

It must also say that blocked claims `不能写成 Results`.

- [x] **Step 2: Run final GREEN**

Run:

```sh
rtk python3 -B -m unittest tests/test_experiment_protocol.py
rtk python3 -B tools/validate_experiment_protocol.py
```

Expected: PASS / exit 0.

Observed:

```text
rtk python3 -B -m unittest tests/test_experiment_protocol.py
Ran 8 tests
OK

rtk python3 -B tools/validate_experiment_protocol.py
exit 0, no failure output

rtk python3 -B -m unittest tests/test_research_assets.py tests/test_executable_mr_assets.py tests/test_experiment_protocol.py
Ran 25 tests
OK
```

## Final Verification

Run:

```sh
rtk python3 -B -m unittest tests/test_research_assets.py tests/test_executable_mr_assets.py tests/test_experiment_protocol.py
rtk python3 -B tools/validate_research_assets.py
rtk python3 -B tools/validate_experiment_protocol.py
rtk git status --short --untracked-files=all
```

Report honestly:

- which experiment claims are observed, qualified, blocked, or speculative;
- what can be written as protocol/method;
- what cannot be written as Results;
- what real artifacts are needed before running SUT experiments.

## Follow-up Increment (2026-06-05): Executable Precondition Gate

**Goal:** Turn the "前置条件检查" from prose into a fail-closed code gate and remove a
cloud-shell-invalid command prefix from the recorded run-manifest contract.

- [x] **Step 1: Write failing tests (RED)** in `tests/test_experiment_protocol.py`:
  - `test_real_sut_preconditions_block_runs_when_env_unset` — a `real-sut-*` run marked
    `observed`/`run` while env is unset must error.
  - `test_real_sut_preconditions_pass_for_current_blocked_ledger` — the shipped ledger
    must pass with env unset.
  - `test_real_sut_preconditions_run_inside_validate_repo` — the gate runs in `validate_repo`.
  - `test_score_task_command_template_has_no_cloud_shell_prefix` — `command_template`
    must not start with the `rtk ` prefix.

  Observed RED:

  ```text
  python3 -B -m unittest tests/test_experiment_protocol.py
  FAILED (failures=1, errors=2)
  AttributeError: ... no attribute 'validate_real_sut_preconditions'  (x2)
  AssertionError: 'rtk' not found in '...'
  ```

- [x] **Step 2: Implement (GREEN)**
  - Added `REAL_SUT_REQUIRED_ENV` and `validate_real_sut_preconditions(root, env)` to
    `tools/validate_experiment_protocol.py`; wired it into `validate_repo`.
  - Added a `command_template` `rtk `-prefix rejection inside `validate_score_task`.
  - Dropped the `rtk ` prefix in `research_assets/experiments/score-task.yml` and
    `paper/20_experiment_empirical_protocol.md`.
  - Recorded the 2026-06-05 environmental check (all `METBENCH_MGN_*` UNSET) in
    `experiment-ledger.yml:precondition_check`, claim `C5-precondition-check` (observed),
    and the evidence package.

  Observed GREEN:

  ```text
  python3 -B -m unittest tests/test_experiment_protocol.py
  Ran 12 tests
  OK
  python3 -B tools/validate_experiment_protocol.py
  exit 0
  ```

**Evidence boundary:** the precondition record is an environmental observation only; it
asserts no SUT verdict, rate, accuracy, or baseline result. Real SUT execution stays blocked.
