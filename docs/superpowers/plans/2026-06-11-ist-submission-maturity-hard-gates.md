# IST Submission Maturity Hard Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the IST maturity assessment's immediate hard blockers into automated gates and clean the current LaTeX submission package enough to compile without unresolved merge artifacts.

**Architecture:** Add one focused unittest module for submission-package health, following the existing P0/P1/Phase4/Phase5 gate style. Fix only the LaTeX submission source issues that the new tests expose: conflict markers, duplicate labels, and stale unresolved references. Preserve the empirical claim boundaries; do not invent new SUT evidence.

**Tech Stack:** Python `unittest`, existing `tools/ist_wordcount.py`, LaTeX `pdflatex`/`bibtex` fallback because `latexmk` is unavailable.

---

### Task 1: Add Phase 6 Submission Hard-Gate Tests

**Files:**
- Create: `tests/test_phase6_submission_maturity_hard_gates.py`
- Read: `paper/ist-submission/main.tex`
- Read: `paper/ist-submission/main.log`
- Read: `paper/33_phase5_review_panel_triage.md`

- [ ] **Step 1: Write failing tests**

Add tests that assert:
- no unresolved conflict markers in `main.tex`;
- no duplicate `\label{...}` values;
- every `\ref{...}`/`\pageref{...}` target has a matching label;
- `fig:r3-pc-nonmonotone` is not referenced unless defined;
- Phase 5 remains explicitly `not-yet-submit`.

- [ ] **Step 2: Run tests to verify RED**

Run: `rtk python3 -m unittest tests.test_phase6_submission_maturity_hard_gates -v`

Expected initial failures: conflict markers, duplicate `subsec:pinn-extension`, and undefined `fig:r3-pc-nonmonotone`.

### Task 2: Resolve Current LaTeX Hard Blockers

**Files:**
- Modify: `paper/ist-submission/main.tex`

- [ ] **Step 1: Remove merge-conflict markers**

Keep the detailed `ours` fault-robustness section, because it preserves the strongest evidence and the referenced table. Remove the shorter duplicate `theirs` paragraph and all `<<<<<<<`, `=======`, `>>>>>>>` markers.

- [ ] **Step 2: Merge duplicate PINN and blocked-status sections**

Keep the concise PINN section only once with one `\label{subsec:pinn-extension}`. Keep one canonical blocked-status paragraph with no duplicate conflict text.

- [ ] **Step 3: Fix stale figure reference**

Either restore the `fig:r3-pc-nonmonotone` figure block if the file exists, or replace the reference with prose that does not cite the missing figure. Prefer the smallest edit that matches available artifacts.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `rtk python3 -m unittest tests.test_phase6_submission_maturity_hard_gates -v`

Expected: all tests pass.

### Task 3: Rebuild And Verify Submission Package

**Files:**
- Generated/updated: `paper/ist-submission/main.pdf`
- Generated/updated: `paper/ist-submission/main.log`

- [ ] **Step 1: Compile with available tools**

Run:
`rtk env TEXMFVAR=/private/tmp/codex-texmfvar pdflatex -interaction=nonstopmode main.tex`
`rtk bibtex main`
`rtk env TEXMFVAR=/private/tmp/codex-texmfvar pdflatex -interaction=nonstopmode main.tex`
`rtk env TEXMFVAR=/private/tmp/codex-texmfvar pdflatex -interaction=nonstopmode main.tex`

- [ ] **Step 2: Run targeted gate suite**

Run:
`rtk python3 -m unittest tests.test_p0_submission_readiness tests.test_phase4_clarity_surgery tests.test_phase5_review_panel tests.test_phase6_submission_maturity_hard_gates -v`

Expected: all targeted gates pass, while Phase 5 still records not-yet-submit status.

- [ ] **Step 3: Report remaining non-hard warnings**

Summarize any remaining `Overfull \hbox` or bibliography metadata warnings as residual polish, not completion blockers unless they create unresolved refs/labels.
