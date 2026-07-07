# JSS Concept Density Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce conceptual density for broad JSS reviewers by introducing a minimal concept set, formalizing the core workflow once, and demoting secondary terms to derived or supplemental roles without weakening any evidence claim.

**Architecture:** Treat the manuscript as a layered explanation. The main text should first define five primitives in plain language and formal notation, then express MR cards, operator floors, semantic witnesses, and claim ledgers as derived implementation details. The supplement can retain detailed evidence tables; the main paper should repeat the same simple chain: candidate relation -> validity gate -> executable check -> typed verdict -> bounded claim.

**Tech Stack:** JSS LaTeX package (`submissions/JSS/main.tex` and supplementary appendix), regression tests in `tests/`, research ledgers in `research_assets/experiments/`, PDF build and LaTeX log checks.

---

## Evidence Baseline And Constraints

Authoritative constraints:

- JSS requires evidence-backed claims, not production validation for every method paper.
- Current review state: `paper/99_academic_reviewer_jss_stable_acceptance_final_review.md` judges the manuscript submission-ready with a credible Minor Revision path, while naming conceptual density as the main residual risk.
- Current PDF: `submissions/JSS/main.log` records 35 pages.
- Current evidence gates: full tests and both validators pass.

Non-negotiable claim boundaries:

- Do not claim stable acceptance as fact.
- Do not claim representative defect sampling, production validation, trained-SUT correctness, defect rate, or broad framework correctness.
- Do not add new experimental results.
- Do not expand main text enough to lose the 35-page risk posture.

## Minimal Concept Set

Use exactly five primary concepts in the main explanatory spine:

1. **Candidate relation.** A proposed metamorphic relation, from physics, representation, expert knowledge, or software semantics. Plain language: "a property we think the SUT should preserve under a controlled change."
2. **Validity gate.** A pre-execution check that asks whether the candidate relation is meaningful for this SUT and this transformed case. Formal role: `G(r, s, x) -> {admit, reject, stress, defer}`.
3. **Numerical decidability.** The measurement condition inside the gate: the metric and tolerance must be meaningful relative to the numerical floor. Operator floor is a derived term here, not a separate headline concept.
4. **Executable check.** The admitted relation becomes a structured MR card plus runner. MR card is the serialization of the candidate relation, not a new concept in the reader's first pass.
5. **Typed verdict.** The execution result is one of pass, fail, skip, out-of-domain, numerical-tolerance issue, or inconclusive, and only some verdicts license fault-like claims. Claim ledger is the audit record for this verdict-to-claim step, not a new core concept.

Derived terms and their placement:

- **MR card:** derived from executable check; define after concept 4.
- **Operator floor:** derived from numerical decidability; define once in the method.
- **Claim ledger / evidence ledger:** derived from typed verdict; keep as audit mechanism.
- **Semantic witness / external witness:** derived from executable check plus typed verdict; define in Results or supplement only.
- **Level 3 / Level 4 evidence:** reviewer-facing boundary language; keep mostly in supplement and cover letter.
- **MetaPattern / MR family:** specialist interpretation layer; keep after the five primitives or move detail to supplement.

## Phase A: Concept Inventory And Density Audit

**Priority:** P0.

**Preconditions:**

- Current `submissions/JSS/main.tex` builds.
- No manuscript claim is changed in this phase.

**Core steps:**

- [x] Count first-page and first-section occurrences of dense terms: `numerical decidability`, `admissibility`, `typed verdict`, `MR card`, `operator floor`, `claim ledger`, `semantic witness`, `Level 3`, `MetaPattern`.
- [x] Mark whether each term appears before it is defined.
- [x] Identify paragraphs with more than three new concepts in the same paragraph.
- [x] Record findings in `paper/100_jss_concept_density_audit.md`.

**Exit conditions:**

- Audit names the exact sections and terms creating density.
- Audit separates true conceptual overload from necessary technical vocabulary.

**Review and acceptance:**

- Every density finding must cite a file path and line or section anchor.
- No proposed removal may weaken a ledger-backed claim.

**Theme-drift check:**

- Pass if the audit remains about readability and reviewer comprehension.
- Fail if it becomes a new experimental or theoretical contribution.

## Phase B: Add A Five-Concept Reader Map

**Priority:** P0.

**Preconditions:**

- Phase A audit exists.
- Page budget allows either a short paragraph plus compact table, or replacement of existing dense contribution prose.

**Core steps:**

- [x] Add a compact "Reader map" near the end of Introduction or start of Method.
- [x] Include the five concepts with one plain-language definition each.
- [x] Add one sentence: "All other terms in the paper are implementation details or evidence records built from these five concepts."
- [x] Avoid adding a new floating table if page count risk increases; prefer replacing dense prose.

**Exit conditions:**

- A non-SciML reviewer can state the workflow in one sentence:
  "The paper screens a proposed relation, executes it only when valid and measurable, records a typed verdict, and restricts claims to that verdict."
- The first occurrence of each core term is either in the reader map or after it.

**Review and acceptance:**

- Check the reader map against the minimal concept set.
- Confirm no new claim appears in the abstract or contribution list.

**Theme-drift check:**

- Pass if the reader map explains the existing method.
- Fail if it reframes the paper as a general theory of all MRs or all SciML validation.

## Phase C: Formalize The Core Workflow Once

**Priority:** P0.

**Preconditions:**

- Five-concept reader map exists.
- Current notation in Method can be reused.

**Core steps:**

- [x] Define a candidate relation as a tuple `r = (b, T, M, m, tau, P)` where `b` is basis, `T` transformation, `M` output mapping, `m` metric, `tau` tolerance, and `P` preconditions.
- [x] Define gate output as `G(r, s, x) in {admit, reject, stress, defer}`.
- [x] Define execution output as `E(r, s, x) = (y, y', z)` where `z` is the measured relation evidence.
- [x] Define verdict mapping as `V(G, z) -> typed verdict`.
- [x] State the claim rule once: only an admitted relation with a fail verdict inside the relation domain can support a SUT-inconsistency claim.

**Exit conditions:**

- Existing rubric, MR-card, and verdict sections can point back to this formal spine.
- Terms like "operator floor" and "claim ledger" are no longer forced to carry the main argument.

**Review and acceptance:**

- Verify notation does not introduce unledgered claims.
- Verify mathematical notation is readable and minimal.

**Theme-drift check:**

- Pass if the formalism only clarifies the existing workflow.
- Fail if it implies a new proof of general MR soundness.

## Phase D: Demote Or Relocate Secondary Terms

**Priority:** P1.

**Preconditions:**

- Phases B-C complete.
- Regression tests protect forbidden claims.

**Core steps:**

- [x] Replace early uses of "MR card, typed verdict, and ledgers" clusters with "executable check and bounded claim record" where precision is not needed.
- [x] Define "operator floor" only under numerical decidability, not in the abstract or first contribution paragraph unless essential.
- [x] Move or shorten references to `MetaPattern`, `Level 3`, and external semantic witness terminology in main text if they compete with the core five concepts.
- [x] Keep detailed terminology in supplement with cross-reference rather than repeated definitions in main text.

**Exit conditions:**

- Introduction and Research Questions no longer introduce more than two unfamiliar concepts per paragraph.
- Detailed terms remain available for expert reviewers.

**Review and acceptance:**

- Run targeted tests that check required JSS and external-corpus boundary wording still exists.
- Check that no evidence table becomes ambiguous after term simplification.

**Theme-drift check:**

- Pass if simplification improves readability while preserving method precision.
- Fail if it removes claim boundaries or hides limitations.

## Phase E: Plain-Language Pass For Abstract, Contributions, And RQs

**Priority:** P1.

**Preconditions:**

- Phases B-D complete.
- No page-count regression is allowed.

**Core steps:**

- [x] Rewrite the abstract's method/result sentence around the five-step chain.
- [x] Rewrite contribution bullets so each bullet maps to one primitive or one evidence block.
- [x] Rewrite RQs using plain verbs: screen, build, interpret, evaluate.
- [x] Preserve all numerical results and claim boundaries.

**Exit conditions:**

- Abstract can be understood without knowing "operator floor" before reading the method.
- RQs align one-to-one with the five-concept workflow and existing evaluation design.

**Review and acceptance:**

- Run humanizer scan for inflated wording.
- Run claim-boundary tests.

**Theme-drift check:**

- Pass if the paper still reads as a JSS software-testing method paper.
- Fail if plain language oversimplifies into unsupported claims.

## Phase F: Reviewer-Facing Comprehension Gate

**Priority:** P1.

**Preconditions:**

- Phases B-E complete.
- Main PDF builds.

**Core steps:**

- [x] Create `paper/101_jss_concept_density_repair_review.md`.
- [x] Review the revised manuscript from three viewpoints:
  JSS software-testing reviewer, non-SciML software engineering reviewer, and SciML/numerical reviewer.
- [x] Ask whether each reviewer can identify: problem, five concepts, evidence chain, and forbidden claims.
- [x] Record any remaining concept-density risk as Minor/Major/Blocker.

**Exit conditions:**

- No reviewer viewpoint classifies concept density as a Major blocker.
- Any remaining issue is a local clarity edit, not a structural rewrite.

**Review and acceptance:**

- Fresh verification must include full tests, validators, PDF build, and log scan.

**Theme-drift check:**

- Pass if review remains about comprehension of the existing contribution.
- Fail if review asks for new experiments or new theory outside the current paper.

## Phase G: Final Verification

**Priority:** P1.

**Preconditions:**

- Phase F review is pass or minor-only.

**Core steps:**

- [x] Run `python -m pytest tests -q`.
- [x] Run `python tools/validate_research_assets.py`.
- [x] Run `python tools/validate_experiment_protocol.py`.
- [x] Rebuild JSS PDF with `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
- [x] Scan `submissions/JSS/main.log` for Overfull, undefined, citation, rerun, and warning patterns.
- [x] Confirm page count remains within the current 35-page posture or document any increase.

**Exit conditions:**

- Full tests pass.
- Evidence gates pass.
- PDF builds.
- Log scan has no submission-risk warning patterns.
- Page count is not worse, or any increase is explicitly justified.

**Review and acceptance:**

- Use verification-before-completion before claiming success.

**Theme-drift check:**

- Pass if final manuscript remains claim-bounded and JSS-scoped.
- Fail if readability edits introduce broader claims.

## Stop Rules

- Stop if a simplification removes a limitation.
- Stop if the page count increases above the current 35-page posture.
- Stop if any term replacement makes a test or claim ledger inconsistent.
- Stop if the manuscript starts implying Level 4 production or representative-defect evidence.

## Expected Outcome

After repair, the main paper should have one visible conceptual spine:

> A candidate relation is screened by a validity gate. If it is valid and numerically decidable, it becomes an executable check. The check produces a typed verdict. The verdict, not the author's intention, determines what claim the paper may make.

All other terms should be explainable as derived details:

- MR card = the structured form of an executable check.
- Operator floor = the measurement limit used by numerical decidability.
- Claim ledger = the audit record that prevents verdict-to-claim drift.
- External semantic witness = an externally sourced instance of the same executable-check and typed-verdict chain.
