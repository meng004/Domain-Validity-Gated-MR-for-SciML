# Minimal MR Assets and Related Work Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the minimum auditable research-asset package that supports manuscript tasks 1-3: executable MR asset schema, reference ledger, and evidence-bounded related-work/contribution updates.

**Architecture:** Use TDD around a small Python validator. The tests define the required fields for MR cards, candidate ledgers, verdict ledgers, and reference ledgers before any asset is created. The assets are evidence records, not empirical results; they must not claim SUT execution, pass rates, violation rates, or comparative superiority.

**Tech Stack:** Python standard library, JSON assets, Markdown paper notes, LaTeX manuscript text.

---

## Boundaries

### In scope

- Create structural validation tests for research assets.
- Create a minimal MR card for node permutation equivariance.
- Create a minimal candidate ledger.
- Create a minimal verdict ledger schema and empty/example ledger.
- Create a reference ledger for closest and uncertain works already cited or discussed.
- Update related-work/contribution text only where the supporting ledger evidence is explicit.

### Out of scope

- Do not run SUTs.
- Do not report empirical pass/fail rates.
- Do not report MR violation rates.
- Do not claim a SUT is reliable or unreliable.
- Do not insert figures.
- Do not commit, push, or open PR unless explicitly requested later.

### Evidence rule

Every conclusion must be traceable to one of:

- a local file path and line/field;
- a command output from the validation run;
- a reference-ledger entry with a source/DOI/URL/status;
- an explicit "unverified" or "blocked" marker.

## File Structure

- Create: `tests/test_research_assets.py`
  - Tests required fields and consistency rules.
- Create: `tools/validate_research_assets.py`
  - Reads JSON assets and returns structured validation errors.
- Create: `research_assets/mr_cards/node_permutation_equivariance.json`
  - One complete MR card, marked as design-time and not empirical.
- Create: `research_assets/ledgers/candidate_ledger.json`
  - Candidate MR decision ledger with node permutation as retained representation MR.
- Create: `research_assets/ledgers/verdict_ledger.schema.json`
  - Verdict ledger schema, with allowed verdict classes.
- Create: `research_assets/ledgers/verdict_ledger.example.json`
  - Empty/no-result example ledger showing schema shape without empirical claims.
- Create: `paper/reference_ledger.md`
  - Closest-work and citation-integrity ledger.
- Modify: `paper/ist-submission/main.tex`
  - Only after ledger evidence exists; update related work and contributions without stronger claims.
- Modify: `paper/manuscript.md`
  - Keep synchronized with the relevant textual changes in `main.tex` if it remains the plain-text mirror.

## Task 1: Research Asset Validator

**Files:**
- Create: `tests/test_research_assets.py`
- Create: `tools/validate_research_assets.py`

- [x] **Step 1: Write failing tests**

Create `tests/test_research_assets.py` with tests that require:

```python
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_research_assets.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_research_assets", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mr_card_contains_required_executable_fields():
    validator = load_validator()
    errors = validator.validate_repo(ROOT)
    assert not [e for e in errors if e["asset"] == "mr_card"], errors


def test_candidate_ledger_has_evidence_bounded_decisions():
    validator = load_validator()
    errors = validator.validate_repo(ROOT)
    assert not [e for e in errors if e["asset"] == "candidate_ledger"], errors


def test_verdict_ledger_schema_disallows_empirical_claims_without_runs():
    validator = load_validator()
    errors = validator.validate_repo(ROOT)
    assert not [e for e in errors if e["asset"] == "verdict_ledger"], errors


def test_reference_ledger_marks_unverified_sources_explicitly():
    validator = load_validator()
    errors = validator.validate_repo(ROOT)
    assert not [e for e in errors if e["asset"] == "reference_ledger"], errors
```

- [x] **Step 2: Run tests and verify RED**

Run:

```sh
rtk python3 -m unittest tests/test_research_assets.py
```

Expected: FAIL because `tools/validate_research_assets.py` and required assets do not exist.

- [x] **Step 3: Write minimal validator**

Create `tools/validate_research_assets.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path


MR_CARD_REQUIRED = {
    "mr_id",
    "title",
    "status",
    "evidence_level",
    "source_case_schema",
    "follow_up_transformation",
    "transformation_preconditions",
    "boundary_condition_compatibility",
    "output_mapping",
    "metric",
    "tolerance",
    "exclusion_rules",
    "allowed_verdicts",
    "verdict_interpretation",
    "claim_limitations",
}

ALLOWED_VERDICTS = {
    "pass",
    "fail",
    "skip",
    "out-of-relation-domain",
    "numerical-tolerance-issue",
    "inconclusive",
}


def read_json(path: Path, asset: str) -> tuple[object | None, list[dict[str, str]]]:
    if not path.exists():
        return None, [{"asset": asset, "path": str(path), "message": "missing file"}]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [{"asset": asset, "path": str(path), "message": f"invalid JSON: {exc}"}]


def require_keys(data: dict, required: set[str], asset: str, path: Path) -> list[dict[str, str]]:
    missing = sorted(required - set(data))
    return [{"asset": asset, "path": str(path), "message": f"missing key: {key}"} for key in missing]


def validate_mr_card(root: Path) -> list[dict[str, str]]:
    path = root / "research_assets" / "mr_cards" / "node_permutation_equivariance.json"
    data, errors = read_json(path, "mr_card")
    if errors or not isinstance(data, dict):
        return errors or [{"asset": "mr_card", "path": str(path), "message": "top-level value must be object"}]
    errors.extend(require_keys(data, MR_CARD_REQUIRED, "mr_card", path))
    verdicts = set(data.get("allowed_verdicts", []))
    if not verdicts or not verdicts.issubset(ALLOWED_VERDICTS):
        errors.append({"asset": "mr_card", "path": str(path), "message": "allowed_verdicts must be known verdict classes"})
    if data.get("evidence_level") != "design-time-asset":
        errors.append({"asset": "mr_card", "path": str(path), "message": "evidence_level must be design-time-asset"})
    return errors


def validate_candidate_ledger(root: Path) -> list[dict[str, str]]:
    path = root / "research_assets" / "ledgers" / "candidate_ledger.json"
    data, errors = read_json(path, "candidate_ledger")
    if errors or not isinstance(data, dict):
        return errors or [{"asset": "candidate_ledger", "path": str(path), "message": "top-level value must be object"}]
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append({"asset": "candidate_ledger", "path": str(path), "message": "entries must be a non-empty list"})
        return errors
    required = {"candidate_id", "mr_id", "decision", "decision_basis", "evidence_reference", "claim_limitations"}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append({"asset": "candidate_ledger", "path": str(path), "message": f"entry {index} must be object"})
            continue
        errors.extend(require_keys(entry, required, "candidate_ledger", path))
    return errors


def validate_verdict_ledger(root: Path) -> list[dict[str, str]]:
    schema_path = root / "research_assets" / "ledgers" / "verdict_ledger.schema.json"
    example_path = root / "research_assets" / "ledgers" / "verdict_ledger.example.json"
    schema, errors = read_json(schema_path, "verdict_ledger")
    example, example_errors = read_json(example_path, "verdict_ledger")
    errors.extend(example_errors)
    if errors:
        return errors
    if not isinstance(schema, dict) or not isinstance(example, dict):
        return [{"asset": "verdict_ledger", "path": str(schema_path), "message": "schema and example must be objects"}]
    if example.get("evidence_level") != "schema-example-no-runs":
        errors.append({"asset": "verdict_ledger", "path": str(example_path), "message": "example must declare schema-example-no-runs"})
    if example.get("entries") != []:
        errors.append({"asset": "verdict_ledger", "path": str(example_path), "message": "example entries must be empty until runs exist"})
    return errors


def validate_reference_ledger(root: Path) -> list[dict[str, str]]:
    path = root / "paper" / "reference_ledger.md"
    if not path.exists():
        return [{"asset": "reference_ledger", "path": str(path), "message": "missing file"}]
    text = path.read_text(encoding="utf-8")
    required_markers = ["| Key |", "| Verification status |", "UNVERIFIED", "VERIFIED"]
    return [
        {"asset": "reference_ledger", "path": str(path), "message": f"missing marker: {marker}"}
        for marker in required_markers
        if marker not in text
    ]


def validate_repo(root: Path) -> list[dict[str, str]]:
    root = Path(root)
    errors: list[dict[str, str]] = []
    errors.extend(validate_mr_card(root))
    errors.extend(validate_candidate_ledger(root))
    errors.extend(validate_verdict_ledger(root))
    errors.extend(validate_reference_ledger(root))
    return errors


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    failures = validate_repo(repo_root)
    for failure in failures:
        print(f"{failure['asset']}: {failure['path']}: {failure['message']}")
    raise SystemExit(1 if failures else 0)
```

- [x] **Step 4: Run tests and verify expected remaining failures**

Run:

```sh
rtk python3 -m unittest tests/test_research_assets.py
```

Expected: FAIL because the validator exists but the assets do not yet exist.

## Task 2: Minimal Node-Permutation MR Asset Package

**Files:**
- Create: `research_assets/mr_cards/node_permutation_equivariance.json`
- Create: `research_assets/ledgers/candidate_ledger.json`
- Create: `research_assets/ledgers/verdict_ledger.schema.json`
- Create: `research_assets/ledgers/verdict_ledger.example.json`

- [x] **Step 1: Create minimal MR card and ledgers**

Create a design-time MR card for node permutation equivariance. It must explicitly say it is not an empirical result and does not assert any SUT pass/fail.

- [x] **Step 2: Run tests and verify GREEN for asset structure**

Run:

```sh
rtk python3 -m unittest tests/test_research_assets.py
rtk python3 tools/validate_research_assets.py
```

Expected: PASS and validator exits 0.

- [x] **Step 3: Record evidence in an implementation note**

Create or update `paper/15_minimal_asset_package_progress.md` with:

- files created;
- tests run;
- exact pass/fail status;
- what the package does prove;
- what it does not prove.

## Task 3: Reference Ledger

**Files:**
- Create: `paper/reference_ledger.md`

- [x] **Step 1: Build ledger entries from local bibliography and explicitly classified verification leads**

Include entries for at least:

- `qi2025physicalfield`;
- `yu2025fluidvelocity`;
- `zhao2026noether`;
- `hiremath2021ocean`;
- `mandrioli2025cps`;
- `baral2025xrepit`;
- `wang2025deeponetfe`.

Each entry must have:

- BibTeX key;
- title;
- authors if available;
- source used for verification;
- DOI/URL if verified;
- verification status: `VERIFIED`, `PARTIAL`, or `UNVERIFIED`;
- how it may be used in the manuscript.

- [x] **Step 2: Run tests**

Run:

```sh
rtk python3 -m unittest tests/test_research_assets.py
rtk python3 tools/validate_research_assets.py
```

Expected: PASS if the ledger contains required markers and assets still validate.

## Task 4: Evidence-Bounded Related Work and Contribution Update

Status: blocked for strong manuscript updates as of 2026-06-05. The reference
ledger marks `qi2025physicalfield` as `UNVERIFIED` and most closest-work keys as
`PARTIAL`; therefore the manuscript must not strengthen closest-work,
first/only novelty, or submission-ready citation claims until those entries are
upgraded or removed.

**Files:**
- Modify: `paper/ist-submission/main.tex`
- Modify: `paper/manuscript.md`

- [ ] **Step 1: Revise only claims supported by `paper/reference_ledger.md`**

Rules:

- A `VERIFIED` source may support a direct closest-work statement.
- A `PARTIAL` source may support cautious wording.
- An `UNVERIFIED` source may not support a strong claim.
- Do not claim empirical results.
- Do not claim automatic MR validity identification.

- [ ] **Step 2: Run validation and LaTeX check**

Run:

```sh
rtk python3 -m unittest tests/test_research_assets.py
rtk python3 tools/validate_research_assets.py
rtk env TEXMFVAR=/private/tmp/codex-texmf-var TEXMFCONFIG=/private/tmp/codex-texmf-config pdflatex -interaction=nonstopmode main.tex
```

Expected:

- tests pass;
- validator exits 0;
- LaTeX creates `paper/ist-submission/main.pdf`;
- no fatal LaTeX error.

## Self-Review Checklist

- [ ] No empirical result was invented.
- [ ] Every MR asset states its evidence level.
- [ ] The verdict ledger example has no run entries.
- [ ] Related-work claims are no stronger than the reference ledger allows.
- [ ] Figures remain excluded.
- [ ] Git status is reported honestly.
