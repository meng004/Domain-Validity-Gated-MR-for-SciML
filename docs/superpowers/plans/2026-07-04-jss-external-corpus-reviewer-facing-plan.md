# JSS External Corpus Reviewer-Facing Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Turn the current five-unit external defect-witness corpus into reviewer-facing quasi-representative evidence with transparent screening, bounded claims, and explicit drift controls, without claiming statistical representativeness.

**Architecture:** The plan adds a compact evidence-ladder and claim-boundary package around existing artifacts. The main paper should remain short; detailed screening logic, inclusion/exclusion rules, semantic-component coverage, and forbidden claims should live in the supplement and supporting review notes. Every wording change must trace to the corpus summary, screening ledger, claim ledger, experiment ledger, or executable witness reports.

**Tech Stack:** LaTeX JSS submission package, YAML/JSON research ledgers, pytest regression guards, existing validation scripts.

---

## Evidence Baseline

Authoritative current artifacts:

- `research_assets/runs/external-defect-corpus-scan/screened_candidates_initial.md`
- `research_assets/runs/external-defect-corpus-scan/external_defect_corpus_summary.json`
- `paper/92_external_defect_corpus_minor_revision_sprint.md`
- `paper/93_external_defect_corpus_experiment_review.md`
- `paper/94_academic_reviewer_jss_minor_readiness_after_external_corpus.md`
- `research_assets/experiments/claim-ledger.yml`, especially C57
- `research_assets/experiments/experiment-ledger.yml`, run `external-defect-corpus-summary-001`
- `submissions/JSS/main.tex`
- `submissions/JSS/supplementary/evidence_appendices.tex`
- `submissions/JSS/cover_letter.md`
- `tests/test_external_defect_corpus_witnesses.py`

Current permitted evidence statement:

- Five external issue/PR/commit-linked semantic witnesses.
- Four repositories or independent subsystems: DeepXDE, NeuralOperator, PhiFlow/PhiML, JAX-CFD.
- Five typed pass verdicts.
- Coverage of boundary-condition periodicity, spectral metric decidability, Hermitian frequency symmetry, coordinate/component axis ordering, and flux-boundary consistency.

Current forbidden evidence statement:

- Representative sample of SciML software defects.
- Production CFD or production SciML validation.
- Trained-SUT correctness or reliability.
- Broad framework correctness.
- Real-world defect-detection rate or defect prevalence.

## Phase A: Evidence Inventory And Boundary Lock

**Priority:** P0.

**Preconditions:**

- The five EDC units and corpus summary exist.
- No new experimental result is introduced in this phase.
- The working rule is "quasi-representative reviewer-facing evidence", not statistical representativeness.

**Core steps:**

- [x] Re-read `external_defect_corpus_summary.json` and list each unit's source, metric, MR family, typed verdict, and forbidden claims.
- [x] Re-read `screened_candidates_initial.md` and extract the actual candidate-pool facts: go, defer, no-go/low-priority sources, and the stated minimum gate.
- [x] Re-read C57 in `claim-ledger.yml` and confirm that the allowed wording does not exceed "external semantic witness corpus".
- [x] Re-read `paper/93_external_defect_corpus_experiment_review.md` and carry over the accepted/forbidden conclusion boundary.
- [x] Produce a short internal memo, preferably `paper/95_jss_external_corpus_reviewer_facing_pack.md`, with a "permitted vs forbidden" claim table.

**Exit conditions:**

- The memo names every counted EDC unit and every deferred/no-go category that supports the screening transparency.
- No sentence uses "representative" without a qualifier such as "not statistically representative" or "quasi-representative, reviewer-facing".
- The memo explicitly says the corpus is curated and bounded.

**Review and acceptance:**

- Check that every evidence sentence has a file path source.
- Check that all numerical claims match existing JSON/YAML artifacts.
- Check that no new claim requires a new experiment.

**Theme-drift check:**

- Pass if the corpus is framed as MR-card/source-follow-up/metric/typed-verdict evidence.
- Fail if the plan turns into a bug-mining study, framework-quality survey, defect-prevalence estimate, or production reliability claim.

## Phase B: Screening Protocol And Candidate-Pool Transparency

**Priority:** P0.

**Preconditions:**

- Phase A memo exists and passes boundary review.
- Raw GitHub search/source artifacts remain archived under `research_assets/runs/external-defect-corpus-scan/raw/`.

**Core steps:**

- [x] Define inclusion criteria: public external source, issue/PR/commit linkage, SciML or scientific-software relevance, clear semantic relation, CPU/local witness feasibility, full rubric-to-verdict chain.
- [x] Define exclusion criteria: ordinary API/runtime failures without MR semantics, hardware/tolerance-only instability, user questions without fix evidence, dependency-heavy cases that cannot be replayed in the one-week scope, non-SciML preprocessing/download issues.
- [x] Convert the existing go/defer/no-go screening ledger into a concise supplement subsection or table.
- [x] State the candidate-pool limitation honestly: this is a purposeful screen for high-value semantic witnesses, not random sampling from a complete defect population.
- [x] Keep any main-text addition to one sentence or footnote-sized wording if possible.

**Exit conditions:**

- A reviewer can see how the five units were selected.
- Defer/no-go cases are visible enough to avoid cherry-picking concerns.
- The text does not imply an unseen complete universe of SciML defects.

**Review and acceptance:**

- Verify all screening categories come from `screened_candidates_initial.md`.
- Verify that exclusion criteria do not retroactively hide failed experiments.
- Verify that "purposeful", "curated", or "bounded" language remains present.

**Theme-drift check:**

- Pass if screening is used only to contextualize evidence strength.
- Fail if screening is presented as a systematic literature review, benchmark construction study, or population-level defect survey.

## Phase C: Semantic-Component Coverage Map

**Priority:** P0.

**Preconditions:**

- Phase B screening protocol is drafted.
- The five EDC reports and MR cards remain the only counted evidence units.

**Core steps:**

- [x] Create a compact coverage map with columns: unit, external source, repository/subsystem, semantic component, MR family, metric, verdict, allowed claim boundary.
- [x] Map the five units to distinct SciML semantic components:
  - DeepXDE: periodic boundary-condition derivative semantics.
  - NeuralOperator spectrum_2d: spectral metric/numerical-decidability semantics.
  - NeuralOperator SpectralConv: Hermitian frequency-domain symmetry semantics.
  - PhiFlow/PhiML: coordinate/component axis-order gradient semantics.
  - JAX-CFD: advection flux boundary-condition inference semantics.
- [x] Add one sentence explaining why this breadth reduces the "only self-made tasks" objection.
- [x] Add one sentence explaining why this breadth still does not prove statistical representativeness.

**Exit conditions:**

- The coverage map fits in supplement without increasing main-paper density.
- The main paper uses only a compact pointer or a single row in the subject-scope/evidence table.
- No framework-wide correctness claim appears.

**Review and acceptance:**

- Confirm every metric value matches `external_defect_corpus_summary.json`.
- Confirm the DeepXDE, NeuralOperator, PhiFlow/PhiML, and JAX-CFD labels match existing artifacts.
- Confirm the map distinguishes repository breadth from defect-population representativeness.

**Theme-drift check:**

- Pass if semantic-component diversity supports method externality.
- Fail if the text starts ranking frameworks, judging maintainers, or implying product quality.

## Phase D: Claim Ladder And Forbidden-Claim Guard

**Priority:** P0.

**Preconditions:**

- Phase C coverage map exists.
- Claim-ledger wording for C57 is available.

**Core steps:**

- [x] Add an evidence ladder with at least four levels:
  - Level 1: author-designed or synthetic task evidence.
  - Level 2: independent SUT/task full-chain evidence.
  - Level 3: external issue/PR/commit-linked semantic witness corpus.
  - Level 4: production-scale or statistically representative real-defect corpus.
- [x] Mark the current paper as reaching Level 3, not Level 4.
- [x] Define what Level 3 allows: external semantic-witness evidence across multiple repositories/subsystems.
- [x] Define what Level 3 forbids: production validation, trained-SUT correctness, defect rate, defect prevalence, representative sampling.
- [x] Add or update regression tests so prohibited phrases cannot enter JSS main/supplement/cover letter as positive claims.

**Exit conditions:**

- The manuscript package gives reviewers an explicit reason why the corpus is useful and bounded.
- The evidence ladder prevents the paper from sounding evasive or inflated.
- Tests fail if the manuscript claims representative sampling, production validation, or defect-rate evidence.

**Review and acceptance:**

- Run the targeted external-corpus tests.
- Run `tools/validate_research_assets.py`.
- Run `tools/validate_experiment_protocol.py`.
- Inspect failures before any wording is strengthened.

**Theme-drift check:**

- Pass if Level 3 is used as a claim boundary.
- Fail if the ladder is used to imply that Level 4 has been achieved.

## Phase E: JSS Manuscript And Supplement Integration

**Priority:** P1.

**Preconditions:**

- Phases A-D pass review.
- The current JSS PDF length should not increase materially.

**Core steps:**

- [x] Update `submissions/JSS/supplementary/evidence_appendices.tex` with the screening protocol, coverage map, and evidence ladder.
- [x] Update `submissions/JSS/main.tex` only if needed, using one short pointer sentence or one compact table-row adjustment.
- [x] Update `submissions/JSS/cover_letter.md` with one bounded sentence: the package includes a curated external issue/PR/commit-linked semantic-witness corpus, not a production or representative defect-rate study.
- [x] Avoid moving dense corpus details back into Results/Discussion.
- [x] Rebuild the JSS PDF and scan the LaTeX log.

**Exit conditions:**

- Main paper remains within the current page/length risk envelope.
- Supplement carries the reviewer-facing detail.
- Cover letter frames the corpus without overclaiming.

**Review and acceptance:**

- Check PDF page count and LaTeX warnings.
- Check that main text remains readable for a JSS non-SciML reviewer.
- Check that supplement table density is acceptable.

**Theme-drift check:**

- Pass if integration supports the software V&V method contribution.
- Fail if the new material dominates the paper or turns it into a real-defect-corpus paper.

## Phase F: Academic Reviewer Re-Review And Evidence Gate

**Priority:** P1.

**Preconditions:**

- Phase E manuscript package builds.
- Targeted tests and validators have passed or their failures are documented.

**Core steps:**

- [x] Run an academic-paper-reviewer style re-review focused on JSS reviewer interpretation.
- [x] Ask specifically whether the corpus now reads as:
  - too weak,
  - appropriately bounded,
  - overclaimed as representative.
- [x] Re-check theme drift against the paper's central claim: domain-validity-gated metamorphic testing for SciML surrogate validation.
- [x] Re-check evidence honesty against all forbidden claims in `external_defect_corpus_summary.json`.
- [x] Record the review in a new numbered `paper/96_*.md` note.

**Exit conditions:**

- The review says the package is at least "appropriately bounded" on external evidence.
- Any remaining Major-risk issue is identified explicitly rather than hidden.
- If overclaiming is found, return to Phase D/E and weaken wording.

**Review and acceptance:**

- Verify that the new review cites the exact files it inspected.
- Verify that it does not assert acceptance probability or guaranteed stable accept.
- Verify that any "Minor Revision posture" conclusion is presented as reviewer-risk assessment, not fact.

**Theme-drift check:**

- Pass if review remains about JSS acceptance risk and evidence sufficiency.
- Fail if review shifts into improving scientific-model performance claims or production deployment claims.

## Phase G: Final Verification And Submission-Readiness Gate

**Priority:** P1.

**Preconditions:**

- Phase F passes without requiring another experiment.
- All manuscript and supplement changes are complete.

**Core steps:**

- [x] Run the full regression suite.
- [x] Run `tools/validate_research_assets.py`.
- [x] Run `tools/validate_experiment_protocol.py`.
- [x] Rebuild `submissions/JSS/main.pdf`.
- [x] Scan the LaTeX log for overfull boxes, undefined references, citation warnings, rerun warnings, and other warnings.
- [x] Confirm the final PDF page count.
- [x] Record final evidence status and residual risks in the plan or a `paper/97_*.md` closure note.

**Exit conditions:**

- Tests and validators pass, or any failure is documented with a decision not to submit until fixed.
- PDF builds with acceptable log status.
- The final claim boundary remains: curated external real-defect semantic-witness corpus, not representative sampling or production validation.

**Review and acceptance:**

- Use verification-before-completion before saying the package is ready.
- Compare final manuscript wording against forbidden claims.
- Confirm no claim outruns the ledgers.

**Theme-drift check:**

- Pass if the final package still reads as a JSS software-testing/method paper.
- Fail if the final package reads as a defect-mining benchmark, production CFD validation, or framework-quality evaluation.

## Stop Rules

- Stop and weaken wording if any artifact contradicts a claim.
- Stop and repair if tests or validators fail.
- Stop and move detail to supplement if main-paper length or density increases.
- Stop and explicitly label residual risk if a reviewer-facing claim cannot be traced to a source artifact.

## Expected Outcome

The intended outcome is not a claim of representative real-defect sampling. The intended outcome is a clearer, auditable evidence package that lets a JSS reviewer see:

- how the five external witnesses were found,
- why they cover multiple SciML semantic components,
- what claim strength they support,
- what stronger claims they do not support,
- why the corpus reduces Major Revision risk without changing the paper's scope.
