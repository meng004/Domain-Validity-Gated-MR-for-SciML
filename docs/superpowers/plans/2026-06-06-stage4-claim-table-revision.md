# Stage 4 Claim Table Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reviewer-facing evidence tables and related-work positioning, then rebuild the IST package without stale claims or wide-table layout failures.

**Architecture:** The Markdown manuscript and IST LaTeX package are both updated, but claim strength remains governed by `paper/22_stage2p5_integrity_audit.md`, `paper/citation_audit.md`, and experiment ledgers. Tests enforce that the new tables, related-work positioning, Stage 4 review record, and LaTeX build artifacts exist and retain the bounded PR4 claim wording.

**Tech Stack:** Markdown manuscript, Elsevier `elsarticle` LaTeX package, Python `unittest`, BibTeX, pdfTeX.

---

### Task 1: Add Stage 4 Readiness Tests

**Files:**
- Create: `tests/test_stage4_revision_readiness.py`
- Modify: none

- [ ] **Step 1: Write the failing test**

Create a Python unittest that checks:

```python
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper" / "manuscript.md"
IST_MAIN = ROOT / "paper" / "ist-submission" / "main.tex"
STAGE4_REVIEW = ROOT / "paper" / "24_stage4_revision_re_review.md"
LATEX_LOG = ROOT / "paper" / "ist-submission" / "main.log"
BIB = ROOT / "paper" / "ist-submission" / "main.bbl"
PDF = ROOT / "paper" / "ist-submission" / "main.pdf"

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

class Stage4RevisionReadinessTest(unittest.TestCase):
    def test_manuscript_has_reviewer_facing_tables_and_related_work_positioning(self):
        text = read(MANUSCRIPT)
        for marker in [
            "### 5.1 Claim-to-Evidence Map",
            "### 5.2 MR-Card-to-Verdict Map",
            "### 2.7 What Is New and What Is Not New",
            "C6-mirror-y-ood-stress",
            "failed on 10 of 10 recorded eval frames",
            "not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim",
            "absolute conservation remains deferred",
        ]:
            self.assertIn(marker, text)

    def test_ist_latex_has_compact_tables_and_new_not_new_section(self):
        text = read(IST_MAIN)
        for marker in [
            "\\subsection{Claim-to-evidence map}",
            "\\subsection{MR-card-to-verdict map}",
            "\\subsection{What is new and what is not new}",
            "\\small",
            "\\setlength{\\tabcolsep}{3pt}",
            "C6-mirror-y-ood-stress",
            "failed on 10 of 10 recorded eval frames",
            "absolute conservation remains deferred",
        ]:
            self.assertIn(marker, text)

    def test_stage4_re_review_record_exists_and_is_evidence_limited(self):
        text = read(STAGE4_REVIEW)
        for marker in [
            "Stage 4 revision and Stage 3' re-review record",
            "Revision decision: proceed to focused re-review",
            "claim-to-evidence table",
            "MR-card-to-verdict table",
            "what is new and what is not new",
            "Remaining risk: table layout polish and external reviewer judgment",
        ]:
            self.assertIn(marker, text)

    def test_final_latex_artifacts_exist_without_unresolved_references_or_overfull_boxes(self):
        self.assertTrue(PDF.exists() and PDF.stat().st_size > 100_000)
        self.assertTrue(BIB.exists() and BIB.stat().st_size > 5_000)
        log = read(LATEX_LOG)
        self.assertNotIn("Citation(s) may have changed", log)
        self.assertNotIn("Label(s) may have changed", log)
        self.assertNotIn("undefined", log.lower())
        self.assertNotRegex(log, re.compile(r"Overfull \\\\hbox"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `rtk python3 -m unittest tests.test_stage4_revision_readiness`

Expected: FAIL because the new manuscript sections, Stage 4 review record, and final LaTeX log are missing.

### Task 2: Add Reviewer-Facing Tables and Related-Work Positioning

**Files:**
- Modify: `manuscript/manuscript.md`
- Modify: `submissions/IST/main.tex`

- [ ] **Step 1: Add Related Work positioning**

Add a section near the end of Related Work:

- What is not new: MT, MR identification, scientific-software MT, residual/UQ diagnostics, LLM candidate generation, NOETHER-style candidate organization.
- What is new in this paper: domain-validity-gated conversion from candidate relation to executable SciML MR asset, with preconditions, metrics, tolerance, exclusion rules, artifacts, and relation-level verdicts.

- [ ] **Step 2: Add Claim-to-Evidence Map**

Add a compact table before detailed Results. Required rows:

- C1 domain-validity rubric
- C2 MR-card executable assets
- C3 baseline comparison blocked
- C4 node permutation sanity
- C5 conservation diagnostic deferred
- C6 mirror-y OOD-stress
- C7 LLM candidate support only

- [ ] **Step 3: Add MR-Card-to-Verdict Map**

Add a compact table covering:

- node permutation: pass sanity, relative L2 = 0.0
- mirror-y: exact relation out-of-relation-domain, approximate OOD-stress fail on 10 of 10 frames
- conservation: absolute conservation deferred, reference-relative divergence diagnostic pass

### Task 3: Fix LaTeX Table Layout and Rebuild

**Files:**
- Modify: `submissions/IST/main.tex`
- Generated: `submissions/IST/main.bbl`
- Generated: `submissions/IST/main.log`
- Generated: `submissions/IST/main.pdf`

- [ ] **Step 1: Reduce wide table pressure**

For wide `tabularx` tables, use `\small` or `\scriptsize`, `\setlength{\tabcolsep}{3pt}`, and replace fixed `p{...}` columns with `X` or narrower ragged-right columns where appropriate.

- [ ] **Step 2: Rebuild bibliography and PDF**

Run:

```bash
rtk bibtex main
rtk env TEXMFVAR=/private/tmp/codex-texmf-var pdflatex -interaction=nonstopmode -halt-on-error main.tex
rtk env TEXMFVAR=/private/tmp/codex-texmf-var pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Expected: PDF builds, `main.bbl` exists, `main.log` contains no unresolved references and no `Overfull \hbox`.

### Task 4: Add Stage 4 Revision and Re-Review Record

**Files:**
- Create: `paper/24_stage4_revision_re_review.md`

- [ ] **Step 1: Record revision actions**

Create a concise record listing:

- Added claim-to-evidence table.
- Added MR-card-to-verdict table.
- Added what-is-new / what-is-not-new related-work paragraph.
- Rebuilt IST package.

- [ ] **Step 2: Record focused re-review verdict**

Decision must be evidence-limited: proceed to focused re-review, not accept.
Residual risks must include table layout polish and external reviewer judgment.

### Task 5: Verify and Review

**Files:**
- Test: `tests/test_stage4_revision_readiness.py`
- Test: existing test suite

- [ ] **Step 1: Run focused tests**

Run: `rtk python3 -m unittest tests.test_stage4_revision_readiness`

Expected: PASS.

- [ ] **Step 2: Run full tests and validators**

Run:

```bash
rtk python3 -m unittest discover -s tests
rtk python3 -B tools/validate_experiment_protocol.py
rtk python3 -B tools/validate_research_assets.py
```

Expected: all pass.

- [ ] **Step 3: Request subagent review**

Ask a read-only subagent to check:

- no overclaim was introduced;
- both new tables are present in Markdown and LaTeX;
- related-work positioning is accurate;
- LaTeX log has no unresolved references or overfull boxes.

---

## Acceptance Criteria

- `tests/test_stage4_revision_readiness.py` fails before implementation and passes after.
- `manuscript/manuscript.md` and `submissions/IST/main.tex` contain both new compact tables.
- Related Work contains "What is new and what is not new".
- `paper/24_stage4_revision_re_review.md` records Stage 4 revision and focused re-review status.
- `submissions/IST/main.bbl`, `main.log`, and `main.pdf` are regenerated.
- The final LaTeX log has no unresolved references and no `Overfull \hbox`.
- Existing tests and validators pass.
