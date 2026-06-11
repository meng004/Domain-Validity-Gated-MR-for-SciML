# CLAUDE.md — repository conventions for Claude Code sessions

This repository develops the manuscript "Domain-Validity-Gated Metamorphic
Relation Identification and Executable Test Assets for Scientific Machine
Learning" for submission to **Elsevier Information and Software Technology
(IST), regular track**. The notes below are the working contract every Claude
Code session should respect.

## Hard user constraints (standing)

- Reply in Chinese, in plain technical style; avoid AI-stylistic filler.
- Cloud shell commands take no `rtk` prefix.
- The sibling repository at `/home/user/Minimum-MR-SubSet/` is **READ-ONLY**.
  Never modify it. This repo may import from `Minimum-MR-SubSet/scripts/` and
  read its committed `data/` fixtures; all writes land here.
- "实事求是" — every conclusion must be backed by real, recomputable evidence
  (a claim-ledger ID, a file path, a verifiable source). Ask when blocked
  rather than guessing.
- STVR is not a candidate venue.

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
page limit; the word count is the binding constraint.

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

## Repository invariants

- Working branch: `claude/trusting-curie-i2VHM`. `main` is for merged PRs.
- Every commit must be backed by real data; never fabricate experiment
  outputs or claim that a never-run experiment succeeded. The PR description
  must point to ledgers and raw artifacts under `research_assets/runs/`.
- `research_assets/experiments/claim-ledger.yml` is the single source of
  truth for what the manuscript may say. Add a new claim ID before writing
  prose that depends on it; never widen the wording beyond `wording_allowed`.
- `tests/test_stage4_revision_readiness.py` and friends are the manuscript
  regression guards. Run `python -m pytest tests -q` before pushing.

## Verifying a prior session's state

Past sessions have left compaction summaries that did not match reality.
Before trusting any claim about commits, branches, or artifacts:

```bash
git fetch origin claude/trusting-curie-i2VHM main
git rev-parse HEAD origin/claude/trusting-curie-i2VHM origin/main
git log --oneline HEAD..origin/claude/trusting-curie-i2VHM
```

If the local working tree is behind the remote, the remote is authoritative
for the prior session's work; align with `git reset --hard origin/...` only
after confirming no uncommitted local changes worth keeping.
