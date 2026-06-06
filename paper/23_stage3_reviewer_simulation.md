# Stage 3 Reviewer Simulation

Date: 2026-06-06

Mode: internal pre-submission reviewer simulation after Stage 2.5 integrity
audit. This is not an external peer review. It is a structured risk check based
only on the current manuscript, IST LaTeX package, citation audit, claim ledger,
and committed artifacts.

## Editorial decision

Editorial decision: Major revision before external submission.

Reason: the paper now has a credible minimal empirical core, but the empirical
package is still narrow. The manuscript is strongest as a method paper with
bounded pilot evidence. It is not yet strong enough for a broad empirical
software-engineering claim about SciML MR effectiveness, baseline superiority,
fault detection, reliability, or cross-SUT validity.

## Reviewer configuration

- Editor: IST software testing and empirical software engineering fit.
- Reviewer 1 - methodology and evidence: empirical design, claim strength,
  reproducibility, statistics.
- Reviewer 2 - software testing and MR contribution: novelty over MT/MR
  identification, oracle problem, MR-card contribution.
- Reviewer 3 - SciML and domain validity: physical assumptions, cylinder-flow
  validity, numerical tolerances.
- Devil's Advocate: strongest counter-argument and rejection-risk audit.

## Editor summary

The current manuscript is much more defensible than a plan-only methods paper.
It reports one bounded within-SUT frame-level OOD-stress result, plus
node-permutation and conservation diagnostics. It also now has an IST LaTeX
package, a citation audit, and a Stage 2.5 claim-evidence audit. The submission
should still be framed as an early method paper with pilot evidence.

Main editorial risk: a reviewer may ask whether the paper's contribution is a
new testing method or mainly a disciplined packaging of known MT ideas for one
SciML example. The answer must be made sharper: the contribution is not MT
itself, not LLM generation, and not NOETHER. It is the domain-validity-gated
conversion of candidate relations into executable, auditable SciML MR assets
with relation-level verdicts.

## Reviewer 1 - methodology and evidence

Strengths:

- The claim ledger and experiment ledger make the empirical boundary unusually
  explicit.
- PR4 evidence is not overstated: mirror-y is written as bounded within-SUT
  frame-level OOD-stress, one SUT, one checkpoint, one MR, one eval trajectory.
- The manuscript states that the mirror-y result is not a reliability,
  accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim.
- Exact guardrail phrase: not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim.

Major concerns:

- The empirical denominator is still small. A 10/10 mirror-y frame result is
  useful, but it is not enough for broad violation-rate or reliability claims.
- Baseline, seeded-fault, cross-SUT, and localization evidence remain blocked.
- The statistical plan is currently a protocol, not an executed analysis.

Required revision:

- Keep all rate language tied to the exact artifact boundary.
- Move any broader efficacy parameter discussion into "future evaluation" or
  "blocked protocol commitments" unless corresponding artifacts exist.
- Add a compact table in the manuscript that mirrors
  `paper/22_stage2p5_integrity_audit.md`.

## Reviewer 2 - software testing and MR contribution

Strengths:

- The paper has a clear oracle-problem motivation.
- The MR-card format and verdict ledger are concrete and inspectable.
- The distinction between candidate generation and validity judgment is useful
  for MT research.

Major concerns:

- The novelty over prior scientific-software MT must be stated carefully. The
  paper should not imply that physics-based or simulation-domain MT is new.
- Related work must keep `qi2025physicalfield` and the fluid-velocity lead as
  non-submission guardrails unless stronger source verification is obtained.
- A reviewer may ask why MR cards are not simply documentation templates. The
  answer must emphasize executable transformation, metric, tolerance,
  exclusion, artifact, and verdict coupling.

Required revision:

- Add a "What is new and what is not new" paragraph near the end of Related
  Work.
- Make the rubric-to-executable-asset transition the central technical object.

## Reviewer 3 - SciML and domain validity

Strengths:

- The paper treats mirror-y correctly as out-of-relation-domain for the exact
  relation on the observed mesh.
- The conservation diagnostic is appropriately deferred for absolute
  conservation because the reference field has non-negligible discrete
  divergence.
- LLM use is restricted to candidate generation and material organization.

Major concerns:

- The physical credibility of each MR depends on mesh geometry, boundary labels,
  vector mapping, and tolerance provenance. Reviewers will ask for those details
  in compact form.
- The current evidence does not show that the method works across flow regimes,
  meshes, or model families.
- The divergence result is easy to misread as conservation success. The
  manuscript must keep "absolute conservation remains deferred" visible.

Required revision:

- Add a short table for each retained or downgraded MR: physical basis,
  precondition, metric, verdict, and what the verdict cannot mean.
- Keep the exact phrase "absolute conservation remains deferred" near the
  conservation result.

## Devil's Advocate

Strongest counter-argument:

The paper may still look like a careful case-study report rather than a mature
method contribution. A skeptical reviewer could say: the method identifies
reasonable MR candidates, runs three pilots on one SUT, and mostly concludes
that some claims are blocked. That is honest, but is it enough for IST? The best
defense is to argue that the blocked/deferred outcomes are part of the method's
value: the rubric prevents invalid MRs from becoming false evidence, and the
ledger makes the boundary of SciML validity visible.

Critical risk:

- If any section implies reliability, accuracy, baseline, multi-SUT,
  exact-symmetry, or geometry-independent conclusions, the paper becomes
  overclaimed.

Major risk:

- If the manuscript does not show exactly how a candidate relation becomes an
  executable asset, the contribution may be judged as process documentation.

Minor risk:

- Several wide tables currently produce LaTeX overfull/underfull warnings. They
  are not correctness failures, but they may look unpolished in the PDF.

## Stage 3 revision roadmap

1. Add one compact claim-to-evidence table to the manuscript or appendix.
2. Add one compact MR-card-to-verdict table for node permutation, mirror-y, and
   conservation.
3. Tighten Related Work with a "new / not new" paragraph.
4. Keep the mirror-y claim wording unchanged: bounded within-SUT frame-level
   OOD-stress; one SUT, one checkpoint, one MR, one eval trajectory; not a
   reliability, accuracy, baseline, multi-SUT, exact-symmetry, or
   geometry-independent claim.
5. Fix LaTeX table layout warnings before submission.

## Bottom line

The paper is no longer merely a plan. It is an evidence-gated method paper with
minimal pilot evidence. The next highest-ROI revision is not adding many new
experiments immediately; it is making the current evidence impossible to
misread, then adding one or two compact tables that connect method, artifact,
verdict, and claim boundary.
