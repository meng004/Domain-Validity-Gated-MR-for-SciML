# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This repository develops the manuscript "Domain-Validity-Gated Metamorphic
Testing of Scientific ML Surrogates" for submission to **Elsevier Information
and Software Technology (IST), regular track**.

## Hard user constraints (standing)

- Reply in Chinese, in plain technical style; avoid AI-stylistic filler.
- "实事求是" — every conclusion must be backed by real, recomputable evidence
  (a claim-ledger ID, a file path, a verifiable source). Ask when blocked
  rather than guessing.
- The sibling Minimum-MR-SubSet repository is **READ-ONLY**: locally at
  `../最小完备MR子集/`, in cloud sessions at `/home/user/Minimum-MR-SubSet/`.
  Never modify it. This repo may import from its `scripts/` and read its
  committed `data/` fixtures; all writes land here.
- STVR is not a candidate venue.
- In cloud sessions, shell commands take no `rtk` prefix.

## Common commands

```bash
# Full test suite (manuscript regression guards; ~238 tests)
python -m pytest tests -q

# Single test file
python -m pytest tests/test_stage4_revision_readiness.py -q

# Fail-closed evidence gates (run before trusting/committing data changes)
python tools/validate_experiment_protocol.py
python tools/validate_research_assets.py

# IST word count (single source of truth; conservative over-estimate,
# counts refs + appendices + 200 words per float per IST rules)
python tools/ist_wordcount.py

# Build the submission PDF (from submissions/IST/)
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

CI (`.github/workflows/validate.yml`) runs the unittest suites plus
`validate_research_assets.py` on every push; it needs only Python + numpy
(torch-dependent real-SUT runs are exercised offline against committed
artifacts).

Real-SUT pilots require `METBENCH_MGN_*` environment variables; absent
those, the precondition gate fails closed and SUT runs stay blocked by
design — this is intended behavior, not an error to fix.

## Architecture: the evidence pipeline

The repo's core invariant is that **prose may only claim what the ledgers
license**, enforced by tests. The flow is:

1. **Raw evidence** — `research_assets/runs/` holds committed raw outputs,
   manifests, and metric ledgers for every executed run (40+ run dirs).
   Never fabricate outputs or claim a never-run experiment succeeded.
2. **Claim ledger** — `research_assets/experiments/claim-ledger.yml` is the
   single source of truth for what the manuscript may say. Runtime claims
   are `C1`–`C10`; paper-level claims `PC1`–`PC10` map onto them in a
   distinct namespace. Add a claim ID *before* writing prose that depends on
   it; never widen wording beyond `wording_allowed`.
3. **Manuscript** — `manuscript/manuscript.md` is the prose source of truth;
   `submissions/IST/main.tex` + `references.bib` is the Elsevier
   `elsarticle` submission package (class files are vendored in that folder).
4. **Regression guards** — `tests/test_*` pin manuscript text, claim
   wording, asset schemas, and phase outcomes to the ledgers. They are
   numbered by pipeline stage/phase (e.g. `test_stage4_revision_readiness.py`,
   `test_phase6_submission_maturity_hard_gates.py`). A prose edit that
   breaks a guard means the prose outran the evidence — fix the prose or
   add evidence, never weaken the guard silently.

Supporting assets:

- `research_assets/mr_cards/` — executable MR cards (JSON): mirror-y
  equivariance, node-permutation equivariance, discrete divergence
  boundedness. `research_assets/rubric/domain_validity_rubric.json` is the
  admissibility rubric.
- `research_assets/ledgers/` — candidate/verdict ledger schemas.
- `tools/` — runners (`run_*.py`), trainers (`train_*.py`), scorers, and the
  two fail-closed validators. `tools/run_academic_review_panel.py` drives
  the simulated review panels whose outputs land in `docs/superpowers/`.
- `paper/00–36_*.md` — numbered planning/audit/review records in
  chronological order; the highest numbers reflect current state (see also
  `NEXT_STEPS.md` for the live task list).
- `theory/` — background notes on MeshGraphNets cylinder-flow and MR theory
  (mostly Chinese-language).

## Branches and verifying prior session state

- Local default branch: `main`. As of 2026-06-17 the submission work and all
  prior session / `codex/*` branches were merged into `main` and the repo was
  consolidated to a single `main` line (local and remote, in sync); work
  continues directly on `main`.
- Past sessions have left compaction summaries that did not match reality.
  Before trusting any claim about commits, branches, or artifacts:

```bash
git fetch origin
git rev-parse HEAD origin/main
git log --oneline HEAD..origin/main
```

If the local tree is behind the remote, the remote is authoritative for
prior session work; `git reset --hard origin/...` only after confirming no
uncommitted local changes worth keeping.

## Target venue: IST regular track — submission requirements

Sources: ScienceDirect "Guide for Authors — Information and Software
Technology"; Elsevier latex-instructions; Elsevier highlights / CRediT pages.
Verified 2026-06-07.

### Length limits (hard)

| Article type           | Word limit |
|------------------------|------------|
| Regular Paper          | **≤ 15,000 words** |
| SLR / Mapping Study    | ≤ 20,000 words |
| Short Communication    | ≤ 2,500 words (refs ≤ 10) |

**Counting rule (IST-specific):** references AND appendices count toward the
total, and **each figure or table is counted as 200 words**. There is no
page limit; the word count is the binding constraint. Check with
`python tools/ist_wordcount.py`.

### Abstract

- **Structured abstract is mandatory** ("Papers will not be handled without a
  structured abstract").
- Five required headings: **Context, Objective(s), Method(s), Results,
  Conclusion**.
- Hard limit: **≤ 300 words**.

### Highlights

- 3 to 5 bullets, **each ≤ 85 characters including spaces**.
- Submit as a separate file at submission time.

### Keywords

- 1 to 7 keywords; prefer single terms over phrases where possible.

### Manuscript format

- LaTeX template: **Elsevier `elsarticle.cls`** with `elsarticle-num`
  (numbered Vancouver-style references). Word template also accepted.
- IST is **NOT** in the "Your Paper Your Way" list — initial submission must
  follow the formal format (no double-spaced single-column free-form draft).
- **Peer review model: single-anonymized** (reviewers see the authors; authors
  do not see reviewers). The submission therefore **keeps** author names,
  affiliations, CRediT, and funding — do NOT anonymize `main.tex`. (Verified
  2026-06-07 against indexed Guide-for-Authors text; IST and Information
  Systems are single-anonymized, unlike Information Processing & Management.)

### Mandatory at submission

- Structured abstract (above).
- Highlights file.
- **CRediT author statement** (contributor roles).
- **Declaration of Competing Interest** (via Elsevier's tool; required even
  when there is none).
- **Generative-AI usage declaration**.
- Submission system: **Editorial Manager** at
  `https://www.editorialmanager.com/infsof/`.

### Optional

- Graphical abstract (TIFF/EPS/PDF; AI-generated images forbidden).

## Scope framing (do not drift)

The paper is a software V&V method paper: a domain-validity-aware workflow
for identifying and executing MRs in SciML OOD validation. It is **not**
framed as outperforming accuracy-based validation, and **not** as a claim of
superiority over uncertainty quantification. The evidence boundary in
`README.md` ("Evidence boundary" section) lists exactly what is and is not
claimed — read it before citing any number in prose.
