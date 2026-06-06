# PR4 Evidence Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Converge the local manuscript, claim ledger, experiment ledger, evidence package, and integrity checks with the merged PR4 mirror-y 10-frame bounded within-SUT OOD-stress evidence.

**Architecture:** Treat PR4 as the evidence source and encode the paper boundary as executable consistency tests. The manuscript may report only claim-ledger wording strength, and validators must accept observed scoped pilots while keeping baseline, reliability, cross-SUT, exact mirror-y, and absolute conservation claims blocked.

**Tech Stack:** Markdown manuscript, YAML ledgers, Python `unittest`, existing repository validators, GitHub PR4 text snapshots in `/private/tmp/pr4-*`.

---

## Preconditions

- Current repo: `/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/MR识别/圆柱绕流`.
- All shell commands must use the `rtk` prefix.
- PR4 source evidence snapshots:
  - `/private/tmp/pr4-claim-ledger.yml`
  - `/private/tmp/pr4-experiment-ledger.yml`
  - `/private/tmp/pr4-evidence-package.md`
  - `/private/tmp/pr4-manuscript.md`
  - `/private/tmp/pr4-metric-ledger.json`
  - `/private/tmp/pr4-provenance.md`
- Required PR4 facts:
  - PR4 is merged in `meng004/Domain-Validity-Gated-MR-for-SciML`, head `42119239060b6bcc54590e7f72ddfbbe4664068e`.
  - Mirror-y exact relation remains `out-of-relation-domain`.
  - Approximate mirror-y OOD-stress probe failed on 10 of 10 recorded eval frames, frames 0-9.
  - Median relative L2 is `0.737` in manuscript wording, with ledger value `0.7368`.
  - Median `V/floor` is `3.96`, with range `3.02-5.55`.
  - No pass, skipped, out-of-relation-domain-at-probe, or inconclusive frame is silently dropped.
  - Claim boundary: one SUT, one checkpoint, one MR, one eval trajectory; not reliability, accuracy, baseline, multi-SUT, exact-symmetry, geometry-independent, or cross-SUT.

## Files

- Create: `tests/test_pr4_evidence_convergence.py`
- Modify: `tools/validate_experiment_protocol.py`
- Modify: `research_assets/experiments/claim-ledger.yml`
- Modify: `research_assets/experiments/experiment-ledger.yml`
- Modify: `research_assets/experiments/evidence-package.md`
- Modify: `paper/manuscript.md`
- Modify: `docs/superpowers/plans/2026-06-06-pr4-evidence-convergence.md`

## Task 1: RED Test For PR4 Evidence Convergence

**Files:**
- Create: `tests/test_pr4_evidence_convergence.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_pr4_evidence_convergence.py` with tests that read the local manuscript and ledgers. The tests must require:

```python
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper" / "manuscript.md"
CLAIM_LEDGER = ROOT / "research_assets" / "experiments" / "claim-ledger.yml"
EXPERIMENT_LEDGER = ROOT / "research_assets" / "experiments" / "experiment-ledger.yml"
EVIDENCE_PACKAGE = ROOT / "research_assets" / "experiments" / "evidence-package.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_claim_ledger_records_pr4_mirror_y_bounded_rate() -> None:
    text = read(CLAIM_LEDGER)
    required = [
        'claim_id: "C6-mirror-y-ood-stress"',
        'status: "observed"',
        "bounded within-SUT frame-level approximate OOD-stress rate",
        "failed on 10 of 10 recorded eval frames",
        "median relative L2",
        "0.737",
        "median ratio 3.96",
        "not a reliability, accuracy, baseline, multi-SUT",
        "Mirror-y is a valid exact relation for this mesh.",
    ]
    for marker in required:
        assert marker in text


def test_experiment_ledger_records_pr4_run_and_keeps_boundaries() -> None:
    text = read(EXPERIMENT_LEDGER)
    required = [
        'run_id: "real-sut-mirror-y-rate-upgrade-001"',
        'status: "observed"',
        'evidence_level: "real-sut-single-mr-ood-stress-frame-rate"',
        'recorded_frames: "0,1,2,3,4,5,6,7,8,9"',
        "ood_stress_frame_fail_count: 10",
        "ood_stress_frame_denominator: 10",
        "median_violation_rel_l2: 0.7368",
        "median_violation_over_floor: 3.96",
        "It is not a reliability, accuracy, baseline,",
    ]
    for marker in required:
        assert marker in text


def test_evidence_package_summarizes_pr4_without_overclaim() -> None:
    text = read(EVIDENCE_PACKAGE)
    required = [
        "Mirror-y OOD-stress within-SUT frame rate",
        "failed on **10 of 10 recorded eval frames**",
        "median relative L2 `0.737`",
        "bounded within-SUT frame rate",
        "not a geometry-independent or cross-SUT rate",
    ]
    for marker in required:
        assert marker in text


def test_manuscript_results_discussion_and_conclusion_are_pr4_aligned() -> None:
    text = read(MANUSCRIPT)
    required = [
        "failed on 10 of 10 recorded eval frames",
        "median relative L2 0.737",
        "median V/floor 3.96",
        "out-of-relation-domain",
        "one SUT, one checkpoint, one MR, one eval trajectory",
        "not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim",
        "bounded within-SUT frame-level OOD-stress result",
    ]
    for marker in required:
        assert marker in text

    stale_two_frame_rate_wording = re.compile(
        r"V = 0\.6914 and 0\.7494; about 3\.6--3\.8 times the mapping-error floor"
    )
    assert stale_two_frame_rate_wording.search(text) is None
```

- [ ] **Step 2: Run the new test and verify RED**

Run:

```bash
rtk python3 -m unittest tests.test_pr4_evidence_convergence
```

Expected: FAIL because the current local claim ledger lacks `C6-mirror-y-ood-stress`, the current experiment ledger lacks `real-sut-mirror-y-rate-upgrade-001`, and the current manuscript still contains two-frame mirror-y wording.

## Task 2: Update Ledgers And Evidence Package

**Files:**
- Modify: `research_assets/experiments/claim-ledger.yml`
- Modify: `research_assets/experiments/experiment-ledger.yml`
- Modify: `research_assets/experiments/evidence-package.md`
- Modify: `tools/validate_experiment_protocol.py`

- [ ] **Step 1: Update claim ledger**

Bring `claim-ledger.yml` into line with PR4:
- `C2-real-sut-verdicts` must be `observed` for the one-case node-permutation pilot.
- `C6-mirror-y-ood-stress` must be `observed` with the 10-frame bounded within-SUT wording.
- `C7-conservation-diagnostic` must be `observed` with absolute conservation deferred and reference-relative diagnostic pass.
- `C3-baseline-comparison` must remain `blocked`.
- Forbidden wording must explicitly bar reliability, accuracy, baseline, cross-SUT, geometry-independent, exact mirror-y, and absolute conservation overclaims.

- [ ] **Step 2: Update experiment ledger**

Bring `experiment-ledger.yml` into line with PR4:
- Keep `fixture-node-permutation-run-001`.
- Add observed real-SUT node-permutation pilot.
- Add observed mirror-y two-frame pilot as provenance context.
- Add observed `real-sut-mirror-y-rate-upgrade-001`.
- Add observed conservation diagnostic pilot.
- Keep METBENCH planned SUTs blocked.
- Preserve the distinction between blocked METBENCH env-gated SUTs and observed artifact-gated pilots.

- [ ] **Step 3: Update evidence package**

Bring `evidence-package.md` into line with PR4:
- Include evidence inventory for node permutation, mirror-y 10-frame rate upgrade, conservation diagnostic, blocked METBENCH planned SUTs, and blocked baseline comparison.
- Include claim gate table for C1-C7.
- State unsupported claims plainly.

- [ ] **Step 4: Update validator**

Modify `tools/validate_experiment_protocol.py` so it no longer requires every `real-sut-*` run to remain blocked. It must instead:
- Require PR4 markers for observed pilots.
- Still require `real-sut-echowve-blocked`, `real-sut-physicsnemo-blocked`, and `real-sut-third-implementation-blocked` to stay blocked.
- Require C6/C7 markers in the claim ledger.
- Require evidence-package PR4 markers.
- Continue rejecting forbidden empirical fields such as `baseline_superiority:`.

## Task 3: Update Manuscript Sections

**Files:**
- Modify: `paper/manuscript.md`

- [ ] **Step 1: Replace Results mirror-y wording**

Update Results so Table 1 and Section 5.2 report PR4:
- `failed on 10 of 10 recorded eval frames`
- `median relative L2 0.737`
- `median V/floor 3.96`
- `3.02-5.55x mapping-error floor range`
- exact relation remains `out-of-relation-domain`
- bounded within-SUT frame-level OOD-stress only.

- [ ] **Step 2: Update Discussion**

Update Discussion to say the paper now has one bounded rate claim only under PR4 scope, and still has no reliability, accuracy, baseline, multi-SUT, exact-MR, or geometry-independent claim.

- [ ] **Step 3: Update Threats and Conclusion**

Update Threats and Conclusion so rate language is not stale:
- mirror-y has a bounded within-SUT frame-level OOD-stress rate;
- conservation and node permutation remain pilots;
- broader rates and external validity remain blocked.

## Task 4: GREEN Verification And Review

**Files:**
- Test: `tests/test_pr4_evidence_convergence.py`
- Test: existing `tests/test_experiment_protocol.py`
- Test: existing validators

- [ ] **Step 1: Run targeted PR4 consistency test**

Run:

```bash
rtk python3 -m unittest tests.test_pr4_evidence_convergence
```

Expected: PASS.

- [ ] **Step 2: Run experiment protocol validator**

Run:

```bash
rtk python3 -B tools/validate_experiment_protocol.py
```

Expected: exit 0.

- [ ] **Step 3: Run research asset validator**

Run:

```bash
rtk python3 -B tools/validate_research_assets.py
```

Expected: exit 0.

- [ ] **Step 4: Run full unittest suite**

Run:

```bash
rtk python3 -m unittest discover -s tests
```

Expected: all tests pass. Record the test count exactly from output.

- [ ] **Step 5: Text integrity scan**

Run:

```bash
rtk rg -n "0\\.6914 and 0\\.7494; about 3\\.6--3\\.8|violation rate has been measured|The SUT fails mirror-y in general|Mirror-y is a valid exact relation|model is unreliable|baseline superiority" paper/manuscript.md research_assets/experiments
```

Expected: no unsafe manuscript claim. Matches inside `wording_forbidden` are acceptable only if the line is clearly forbidden wording.

- [ ] **Step 6: Subagent review**

Dispatch a reviewer subagent with:
- the plan file path;
- the changed file list;
- the verification command outputs;
- instruction to identify unsupported claims, stale PR3/two-frame wording, and validator loopholes.

Acceptance: reviewer reports no critical or important issues, or all such issues are fixed and re-reviewed.

## Acceptance Criteria

- New RED test failed before edits for the expected PR4 inconsistency.
- After edits, targeted PR4 consistency test passes.
- Existing protocol and research-asset validators exit 0.
- Full unittest suite passes.
- `paper/manuscript.md` reports mirror-y as PR4 bounded within-SUT frame-level OOD-stress evidence, not two-frame pilot evidence.
- `claim-ledger.yml`, `experiment-ledger.yml`, and `evidence-package.md` include C6/PR4 and preserve forbidden overclaims.
- Baseline comparison, METBENCH planned SUTs, seeded fault, cross-SUT reliability, exact mirror-y, and absolute conservation claims remain blocked/forbidden.
- Reviewer subagent finds no unresolved critical or important issue.

## Review Checklist

- Every number in manuscript Results has a direct PR4 ledger/provenance source.
- Every rate-like phrase includes its denominator and scope.
- `10/10` is not generalized beyond one SUT, one checkpoint, one MR, one eval trajectory.
- `median relative L2 0.737` and `median V/floor 3.96` are consistent with PR4 metric/provenance.
- Exact mirror-y remains out-of-relation-domain.
- Divergence absolute relation remains deferred.
- No baseline or accuracy result is implied.
- Validator logic matches the new evidence state rather than the old all-real-SUT-blocked state.
