# 50 — EIC-facing novelty and evidence compression repair plan

> Date: 2026-06-18  
> Target manuscript: `submissions/IST/main.tex`  
> Goal: improve EIC and Reviewer-2 readability without adding experiments or expanding claims.

## Overall Goal

Shift the editorial reading from "another SciML MR case study with many results" to "an auditable V&V asset-construction workflow for SciML surrogate testing." The revision must sharpen novelty, reduce secondary-evidence crowding, and answer the shared concern about the uncalibrated domain-violation axis.

## Task 1 — Introduction exact novelty paragraph

**Goal.** Make the contribution boundary visible in the first two pages.

**Implementation.** Add or rewrite a concise exact-novelty paragraph that states:

1. The paper does not claim to invent metamorphic testing.
2. The paper does not replace residual, UQ, accuracy, or trust-region diagnostics.
3. The new contribution is measurement-floor admissibility + MR-card executable assets + typed verdict ledgers.
4. The evidence supports bounded SciML V&V utility, not general SciML reliability or real-world defect-detection rates.

**Acceptance criteria.**

- The novelty boundary appears before the RQs.
- RQ0--RQ4 remain unchanged.
- Coverage remains an implication, not a research question.
- No claim of general reliability, universal coverage, or baseline superiority is introduced.

## Task 2 — Results secondary-evidence compression

**Goal.** Reduce the "crowded manuscript" impression by making secondary evidence visibly secondary.

**Implementation.**

- Preserve primary evidence: cylinder-flow gate decisions, K=6/trajectory/architecture replication, airfoil gate discrimination, operator-floor sweep, and PINN/FNO transfer.
- Compress secondary evidence: LLM/generic baselines, Minimum-MR-SubSet audit/rerun, and cross-program breadth.
- State explicitly that secondary evidence is a scope contrast or audit trail, not core validation or superiority evidence.
- Prefer shorter prose over new tables or figures.

**Acceptance criteria.**

- Results still separates primary/supporting/secondary evidence.
- Secondary evidence does not read as generalization evidence.
- Main text remains 4 figures and 5 tables.
- Word count does not increase.

## Task 3 — D-axis calibration future protocol

**Goal.** Answer the MethodologyRigor/Perspective concern that the domain-violation axis is per-relation and not cross-MR calibrated.

**Implementation.** In Future Work or Threats to Validity, specify a concrete future protocol:

- normalize domain-distance measures within each relation family;
- define anchor cases for in-domain, near-boundary, and out-of-relation-domain settings;
- build relation-family calibration sets;
- use independent domain experts or raters to validate the D-axis categories;
- report agreement and residual cross-MR comparability limits.

**Acceptance criteria.**

- The manuscript does not claim current cross-MR calibration.
- The current D-axis remains explicitly per-relation.
- Future Work gives a concrete protocol, not a vague promise.

## Drift Checks

Run searches for:

- `RQ5`
- `validity--coverage duality`
- `central claim`
- `general reliability`
- `baseline superiority`
- `real-world defect`
- `universal`

Any hit must be inspected. The revision fails if it revives RQ5, makes coverage central, claims baseline superiority, or implies general SciML reliability.

## Verification

Run:

```bash
rtk .venv/bin/python tools/ist_wordcount.py
rtk .venv/bin/python -m pytest tests/test_p0_submission_readiness.py tests/test_stage2p5_submission_readiness.py
rtk zsh -lc 'cd submissions/IST && TEXMFVAR=/private/tmp/codex-texmf-var TEXMFCONFIG=/private/tmp/codex-texmf-config pdflatex -interaction=nonstopmode main.tex && bibtex main && TEXMFVAR=/private/tmp/codex-texmf-var TEXMFCONFIG=/private/tmp/codex-texmf-config pdflatex -interaction=nonstopmode main.tex && TEXMFVAR=/private/tmp/codex-texmf-var TEXMFCONFIG=/private/tmp/codex-texmf-config pdflatex -interaction=nonstopmode main.tex'
```

