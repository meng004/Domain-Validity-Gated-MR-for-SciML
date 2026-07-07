# 83 - Academic-reviewer JSS empirical-strength re-review

Date: 2026-07-03

Target: Journal of Systems and Software (JSS), regular paper.

Mode: academic-paper-reviewer re-review / verification review, focused on one
question: after the P0 independent periodic-advection workflow, does the paper
now reach the strong empirical persuasiveness normally needed for a stable JSS
regular-paper acceptance path?

This is a simulated academic review, not an external peer-review result or an
acceptance prediction guarantee.

## Evidence base verified

- Current P0 workflow report:
  `research_assets/runs/periodic-advection-primary-workflow/periodic_advection_primary_workflow_report.json`.
- Current JSS manuscript:
  `submissions/JSS/main.tex`.
- Current JSS package status:
  `submissions/JSS/main.log`, `submissions/JSS/README.md`.
- Previous gap review:
  `paper/81_academic_reviewer_jss_gap_review.md`.
- Current integrity checks executed in this review turn:
  - `pytest tests/test_p0_periodic_advection_primary_workflow.py tests/test_p0_submission_readiness.py -q`
    -> 8 passed, 5 subtests passed.
  - `python tools/validate_research_assets.py` -> exit 0.
  - `python tools/validate_experiment_protocol.py` -> exit 0.
  - `pytest tests -q` -> 449 passed, 334 subtests passed.
- Current JSS PDF status:
  `submissions/JSS/main.log` records `Output written on main.pdf (46 pages,
  483702 bytes)`, and `submissions/JSS/README.md` records 46 pages
  single-column, still above the JSS recommendation.

## Verification of the former P0 empirical-independence issue

Original major issue from review 81:

> Add one additional independent primary-scale SUT/task with the full
> rubric-to-verdict chain, preferably outside the current cylinder-flow family.

Verification:

- Status: **FULLY ADDRESSED for the narrow requested repair**.
- Evidence:
  - `periodic_advection_primary_workflow_report.json` records a new task:
    2D scalar periodic advection.
  - It records a new implementation family: NumPy periodic convolution
    surrogate, not MGN/PointMLP/PhysicsNeMo/PINN/FNO.
  - It records K=6 trained SUT checkpoints and n=10 held-out fields per SUT.
  - It records full workflow flags for trained checkpoints, rubric decisions,
    source/follow-up outputs, metric ledgers, and relation verdicts.
  - Results are 60/60 periodic-translation passes, 60/60 mass-conservation
    passes, and 6/6 fixed-velocity mirror rejections.

Quality assessment:

The repair is credible and traceable. It substantially improves the paper's
empirical independence relative to review 81. It is not a cosmetic addition.
However, the new evidence is synthetic and structurally favorable to the chosen
periodic-convolution SUT: translation equivariance and mass preservation are
expected from the architecture/operator pairing. Therefore it strengthens the
workflow-chain claim more than it strengthens real-world utility, production
generality, or defect-detection evidence.

## Reviewer panel synthesis

### EIC / JSS fit reviewer

Recommendation: **Major Revision, closer to Minor Revision than before P0**.

The paper is now clearly reviewable for JSS as a software V&V method paper. The
P0 addition reduces the largest empirical-independence objection. Still, a
stable accept/minor-revision trajectory is not yet secure because the manuscript
is 46 pages single-column, dense, and still presents many evidence units with
careful boundaries rather than a compact, reader-friendly empirical story.

Key concern: JSS reviewers may accept the bounded method framing, but the editor
may still see the length/density and the synthetic nature of the new task as
reasons for another major revision.

### Methodology reviewer

Recommendation: **Major Revision / high borderline**.

Strengths:

- Evidence discipline is strong: reports, ledgers, MR cards, tests, and
  fail-closed validators are present and passing.
- The P0 run supplies a genuine independent task and complete
  rubric-to-verdict chain.
- The manuscript correctly avoids population-rate and reliability claims.

Residual concerns:

- The periodic-advection task is independent, but it is synthetic and
  architecture-aligned. It does not test independent real defects,
  independently authored mutants, production code, or independently collected
  field data.
- Several evidence cells remain descriptive and non-independent; the paper
  handles this honestly, but the result is bounded validation rather than
  strong empirical generality.
- The subject inventory and evidence-role narrative have not fully absorbed the
  new periodic-advection task. `submissions/JSS/main.tex` includes it in
  `tab:effective-n` and `tab:mr-card-verdict`, but the surrounding subject
  inventory still emphasizes cylinder/airfoil/PINN/FNO/sibling evidence. This
  makes the P0 task look partly appended rather than designed into the study.

### Domain reviewer

Recommendation: **Minor-to-Major Revision**.

The core contribution is plausible: validity-gated MR assets with a
numerical-decidability gate. The P0 workflow helps show that the framework is
not only a cylinder-flow artifact. For a metamorphic-testing / SciML V&V
reviewer, this is now a more credible bounded method paper.

Residual concern: the paper still needs to keep the contribution contrast very
sharp. The novelty is not "we found more MRs" or "we show reliability"; it is
the auditable admit/reject/defer workflow, plus numerical-decidability
discipline. Any wording that sounds like broad empirical validation will be
vulnerable.

### Artifact / reproducibility reviewer

Recommendation: **Minor Revision on artifact integrity, Major Revision on
practitioner readiness**.

The artifact story is strong: current tests pass, validators pass, P0 raw
outputs/checkpoints/ledgers exist, and the JSS package builds. This is above the
minimum artifact credibility threshold for JSS.

The practical adoption story is still weak: no measured MR-card authoring time,
no independent user study, no inter-author/domain-expert agreement, and no
maintenance-cost evidence. For JSS, this may not be fatal if the paper is framed
as a method plus evidence package, but it prevents a stable acceptance judgment
for "strong empirical utility."

### Devil's Advocate

Strongest rejection argument:

The authors added an independent SUT/task, but chose a synthetic periodic
advection task where the admitted relations are almost built into the surrogate
class. The new run proves the pipeline can execute cleanly on a second toy-like
operator setting, not that the method works on independently messy software
systems or real defects. The paper still relies heavily on curated evidence,
author-designed mutants/probes, and carefully bounded interpretations. A JSS
reviewer could reasonably say: "This is a high-integrity method artifact, but
not yet a strong empirical evaluation of general utility."

Severity: **Major**, not critical. It does not force rejection if the paper is
framed as bounded method validation, but it prevents an Accept/Minor confidence
level.

## Scores after P0

Scores are ordinal reviewer judgments, not calibrated acceptance probabilities.

| Dimension | Previous review 81 | Current score | Change | Rationale |
|---|---:|---:|---:|---|
| Originality | 78 | 78 | 0 | P0 adds evidence, not a new conceptual contribution. |
| Methodological rigor | 72 | 76 | +4 | Complete additional workflow, passing validators/tests, stronger independence. |
| Evidence sufficiency | 66 | 72 | +6 | Independent task materially improves sufficiency, but synthetic/architecture-aligned and no real-defect corpus. |
| Argument coherence | 72 | 71 | -1 | New evidence is useful but not fully integrated into subject-scope narrative; density increased. |
| Writing quality | 70 | 69 | -1 | 46 pages and table-heavy structure remain reviewer-load risks. |
| Literature integration | 73 | 73 | 0 | Unchanged by P0. |
| Significance and impact | 74 | 75 | +1 | Practical artifact value improves, adoption-cost evidence still absent. |

Weighted overall judgment: approximately **74/100**. This is above the prior
~71/100 and now near the upper Major Revision / lower Minor Revision boundary,
but still below a conservative "stable accept" level for a JSS regular paper.

## Editorial decision

Simulated decision: **Major Revision**, with a realistic path to Minor Revision
after one focused tightening pass.

The paper now has **stronger bounded empirical persuasiveness** and should no
longer be judged as lacking an independent full-chain SUT/task. It still does
not reach **stable JSS regular-paper acceptance** if that phrase means likely
Minor Revision or Accept after review. It is more accurate to say:

> The manuscript is now empirically defensible for JSS as a bounded,
> artifact-backed software V&V method paper, but it is not yet a stable-accept
> empirical tool/method paper.

## Residual priority issues

### P0 - Integrate P0 evidence into the experimental design narrative

Impact: high. Effort: low to medium.

The new periodic-advection evidence is in the effective-N table and MR verdict
map, but it should also appear in the subject inventory and evidence-role
description. Otherwise reviewers may see it as appended after the fact.

Concrete fix:

- Update the aggregate subject inventory paragraph in `submissions/JSS/main.tex`
  to mention the periodic-advection primary workflow.
- Add a row to `tab:subject-scope`, or explicitly explain why it is represented
  only in `tab:effective-n`.
- Clarify whether it is "primary" or "independent primary-scale synthetic
  workflow evidence"; avoid mixing it with production CFD primary evidence.

### P1 - Reduce JSS length/density risk

Impact: high. Effort: medium to high.

The package is 46 pages single-column against the JSS recommendation of fewer
than 36 pages single-column or 18 pages double-column. This is not a hard cap,
but it remains an editor-friction risk. The P0 evidence raised page count from
45 to 46 pages.

Concrete fix:

- Compress main-text evidence tables.
- Move more claim-map detail to supplementary material.
- Keep the main narrative focused on 3-5 evidence roles, not every ledger row.

### P1 - Add practitioner/adoption-cost evidence or explicitly demote it

Impact: medium-high. Effort: medium.

JSS readers may ask whether MR-card construction is usable beyond the authors.
The current manuscript says the workflow decomposes roles but does not measure
person-hours, agreement, or maintenance cost.

Concrete fix:

- Add a small, bounded adoption-cost table from existing project records if
  real traceable data exist.
- If no traceable data exist, state clearly that authoring effort and user study
  are future work and remove any wording that implies adoption readiness.

### P2 - Strengthen defect-evidence positioning

Impact: medium. Effort: high if new data are required.

The current evidence is enough for coverage-geometry claims but not for
real-world defect effectiveness. If stable acceptance is the target, an
independent real-defect or independently authored mutant corpus would still be
the strongest next empirical upgrade. If infeasible, keep this as a limitation,
not a hidden claim.

## Bottom line

Answer to the user's question:

**No, not yet at a conservative "stable JSS regular-paper acceptance" level for
strong empirical persuasiveness.**

**Yes, it is now much closer and empirically defensible for review as a bounded
JSS method paper.** The largest previous P0 empirical-independence gap has been
substantially addressed, but the remaining risks are length/density, synthetic
new-task evidence, incomplete integration of that evidence into the study
design narrative, and missing adoption/real-defect evidence.

