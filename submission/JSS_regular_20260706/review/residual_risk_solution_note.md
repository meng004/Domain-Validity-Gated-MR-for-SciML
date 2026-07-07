# Residual Risk Solution Note

Date: 2026-07-04

Purpose: identify low-risk ways to reduce the two remaining scholarly risks without widening the manuscript beyond its evidence boundary.

## Risk 1: Bounded External Validity

Current state: the manuscript has bounded but non-trivial breadth: cylinder flow, airfoil, PINN/FNO, periodic advection, RealPDEBench, a five-unit external issue/PR/commit-linked witness corpus, and cross-program checks. It does not claim representative defect sampling, production validation, trained-SUT correctness, or real-world defect-detection rates.

Best solution:

1. Keep the main-text claim boundary exactly as it is.
2. Make the supplement and cover-letter framing reviewer-facing: describe the evidence as an evidence ladder rather than a representative corpus.
3. Preserve the inclusion/exclusion logic for the five external witnesses.
4. State explicitly that the external witness set weakens the self-made-task objection but does not estimate population defect rates.

Do not do:

- Do not rename the witness set as `representative` unless a sampling frame, inclusion rate, exclusion rate, and population definition are actually built.
- Do not add a new last-minute experiment unless it is a full rubric-to-verdict chain with independent SUT/data/defect source.

Decision: the current low-risk path is disclosure plus evidence-ladder presentation, not a new claim.

## Risk 2: Concept Density and Reviewer Usability

Current state: the five-concept reader map, formal spine, and concept-density regression tests are already in place. The latest tests pass, including the guard that prevents dense implementation terms from appearing before the reader map.

Best solution:

1. Keep the five-concept reader map near the start of the Introduction.
2. Keep the formal spine in Method: `r=(b,T,M,m,\tau,P)`, `G -> E -> V -> claim`.
3. Keep MetaPattern and related algebraic vocabulary as an optional candidate source scaffold, not as the main contribution.
4. Avoid adding new named concepts during final upload edits.
5. Keep the contribution sentence focused on the SciML-specific numerical-decidability gate.

Do not do:

- Do not add a new terminology table to the main text unless page pressure is re-opened; the existing reader map is lighter.
- Do not add non-SciML examples to defend generality; that would reopen the `only an application` risk.

Decision: the concept-density risk is already materially reduced. The remaining risk is ordinary reviewer usability, not a desk-rejection blocker.
