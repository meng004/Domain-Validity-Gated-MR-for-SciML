# JSS Concept Density Audit

Date: 2026-07-04.

Scope: `submissions/JSS/main.tex` only. The audit checks readability and reviewer comprehension for the JSS regular-paper draft. No new experiment is introduced, no result is changed, and no claim boundary is widened.

## Evidence Sources

- `submissions/JSS/main.tex`, lines 88--109: abstract method/results paragraph.
- `submissions/JSS/main.tex`, lines 135--149: introduction central-idea, contribution, and paper-organization paragraphs.
- `submissions/JSS/main.tex`, lines 214--270: method overview, candidate-source, and admissibility sections.
- `submissions/JSS/main.tex`, lines 296--312: research-question setup.
- `paper/99_academic_reviewer_jss_stable_acceptance_final_review.md`: final reviewer-facing risk note that concept density remains the main residual readability risk.

## Findings

1. The abstract introduces too many specialist terms in one pass: numerical decidability, admissibility predicate, MR card, typed verdict, claim ledger, and operator floor all appear before the reader has a minimal workflow model. These terms are valid and evidence-backed, but the density raises comprehension risk for non-SciML JSS reviewers.

2. The introduction at lines 135--149 places implementation records and interpretation mechanisms beside the core idea. The cluster "MR card", "typed verdict", "claim ledger", "operator floor", and MetaPattern makes the method look broader and more abstract than the actual contribution. The evidence supports a bounded validity-gated workflow, not a new general theory of SciML reliability.

3. The method overview currently moves from "admissibility, asset construction, and verdict interpretation" directly to specialized names. It lacks one compact formal spine that lets later terms be read as derived details.

4. The research questions are technically aligned but their labels are jargon-heavy: "Admissibility", "Asset construction", "Verdict interpretation", and "Empirical utility" are accurate but do not tell a broad JSS reviewer what action is being evaluated.

5. The dense terms are not false. The repair should keep them, but delay and subordinate them:
   - MR card = record for an executable check.
   - operator floor = measurement limit used by numerical decidability.
   - claim ledger = audit record for verdict-to-claim discipline.
   - semantic witness = external instance of the same check-to-verdict chain.
   - MetaPattern = optional candidate-source scaffold, not the paper's central contribution.

## Phase A Review

Phase A review: pass.

The audit identifies concrete density locations and separates readability overload from necessary technical vocabulary. No proposed edit removes a ledger-backed claim.

Theme-drift check: pass.

The repair target remains JSS reviewer comprehension of the existing software V&V method. It does not add experiments, does not claim representative defect sampling, does not claim production validation, and does not reframe the paper as broad SciML reliability evidence.
