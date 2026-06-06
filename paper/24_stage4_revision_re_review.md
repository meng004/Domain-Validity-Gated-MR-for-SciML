# Stage 4 revision and Stage 3' re-review record

Date: 2026-06-06

Scope: focused revision after the Stage 3 internal reviewer simulation. This
record is evidence-limited and does not claim external peer-review acceptance.

## Revision actions

- Added a claim-to-evidence table to the manuscript and IST LaTeX package.
- Added an MR-card-to-verdict table covering node permutation, mirror-y, and
  conservation.
- Added a Related Work subsection explaining what is new and what is not new.
- Tightened the mirror-y wording around the bounded within-SUT frame-level
  OOD-stress claim.
- Rebuilt the IST package after regenerating the bibliography.

## Focused re-review

Revision decision: proceed to focused re-review.

The revision addresses the Stage 3 concern that the method contribution and
evidence boundary were too diffuse. The two compact tables now show, in one
place, which claims are supported, which are blocked, and which artifacts support
each verdict. The related-work paragraph also prevents the paper from implying
that MT, scientific-software MT, LLM candidate generation, or NOETHER-style
candidate organization is new.

## Residual risk

Remaining risk: table layout polish and external reviewer judgment.

The manuscript still has minimal empirical evidence: one SUT, one checkpoint,
one mirror-y OOD-stress MR, one eval trajectory, plus node-permutation and
conservation pilots. It remains unsuitable for reliability, accuracy, baseline,
multi-SUT, exact-symmetry, geometry-independent, seeded-fault, or localization
claims.
