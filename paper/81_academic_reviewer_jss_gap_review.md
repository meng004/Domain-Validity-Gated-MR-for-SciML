# 81 - Academic-reviewer JSS gap review

Date: 2026-07-03

Target: Journal of Systems and Software (JSS), regular paper.

Mode: academic-paper-reviewer full-style synthesis, calibrated to JSS regular
paper and focused on empirical sufficiency for stable acceptance. This is a
local reviewer simulation, not external peer review and not an acceptance
prediction guarantee.

## Evidence base used

- JSS requirements and recent-reference benchmark:
  `paper/80_jss_official_guide_benchmark_gap_plan.md`.
- Current JSS package:
  `submissions/JSS/main.tex`, `submissions/JSS/main.pdf`,
  `submissions/JSS/README.md`, `submissions/JSS/cover_letter.md`,
  `submissions/JSS/declarations.md`, and
  `submissions/JSS/open_science_checklist.md`.
- Current live status:
  `NEXT_STEPS.md`.
- Latest local verification recorded in Phase E:
  JSS PDF 45 pages, 480870 bytes; full tests 447 passed and 334 subtests passed;
  evidence validators exit 0; legacy density diagnostic 14702/15000.

## Reviewer configuration

1. EIC / JSS fit reviewer: software engineering editor, focused on JSS scope,
   regular-paper maturity, desk-reject risk, and reviewability.
2. Methodology reviewer: empirical software engineering and software testing
   methods, focused on evidence design, independence, statistics, and
   reproducibility.
3. Domain reviewer: metamorphic testing / scientific software V&V reviewer,
   focused on novelty relative to MR identification, oracle-free testing, and
   SciML diagnostics.
4. Practice and artifacts reviewer: software-engineering artifact and Open
   Science reviewer, focused on usability, data/code availability, and
   reproducibility.
5. Devil's Advocate: skeptical reviewer testing the strongest rejection
   arguments.

## Editorial synthesis

Recommended simulated decision: **Major Revision**.

Desk-reject risk is now lower than before Phase A-E because the manuscript is
clearly framed as a JSS software V&V method paper, has a valid JSS package,
contains data/software availability information, and keeps claims bounded. The
remaining gap to "stable acceptance" is still material. A JSS reviewer can
reasonably accept the paper for review, but a stable accept/minor-revision
trajectory is not yet likely because empirical generality remains bounded and
the paper is still longer/dense relative to JSS guidance.

The empirical evidence is **not failing** in the sense of being unsupported or
fabricated; it is artifact-backed and explicitly bounded. It is, however,
weaker than what recent high-impact JSS method/tool papers often show when they
claim broad tool/method utility. The current paper is defensible as a
method/proof-plus-bounded-validation paper, not as a broad empirical benchmark
or general SciML testing tool evaluation.

## Panel findings

### EIC / JSS fit reviewer

Strengths:

- The topic is in JSS scope: software V&V/testing for AI/SciML software, with
  evidence required for claims. The local JSS contract records this scope and
  evidence requirement.
- The abstract and introduction state a bounded method contribution rather than
  an inflated reliability or baseline-superiority claim.
- The package now compiles and passes local gates.

Major concerns:

- The final package is 45 pages single-column. JSS encourages fewer than 36
  single-column pages or fewer than 18 double-column pages; this is not a hard
  cap, but it remains editor-friction risk even with the cover-letter
  explanation.
- The paper is still dense and table-heavy. Even after moving detailed
  appendices to supplementary material, the main text still reads partly like
  an evidence audit.

EIC recommendation: Major Revision, not desk reject, if length explanation is
accepted; stronger if further compressed.

### Methodology reviewer

Strengths:

- The paper now has a reviewer-facing independent-evidence-unit table with
  SUT/task, MR/operator, independence source, evidence role, allowed inference,
  and forbidden inference.
- It correctly blocks population-level inference from repeated cells and says
  many results are descriptive, not independent-trial inference.
- Evidence validators and regression tests pass; this reduces integrity risk.

Major concerns:

- Primary evidence remains centered on cylinder-flow MeshGraphNets-family
  workflows. Same-task variants, PointMLP, and PhysicsNeMo reduce
  single-implementation risk but do not fully solve task/dataset independence.
- Airfoil is strong gate-discrimination evidence, but its model accuracy is
  explicitly high-error and its role is typed verdict discrimination, not a
  broad performance or reliability demonstration.
- PINN/FNO and sibling evidence broaden the method, but several components are
  output-level probes, read-only external artifacts, or supporting/falsification
  evidence rather than independent primary SUT validations.
- Fault evidence is useful for coverage geometry, but not a real-defect corpus
  or independently authored mutant study.

Methodology recommendation: Major Revision unless the paper either adds one
additional independent primary-scale SUT/defect study or makes the
method/proof-plus-bounded-validation positioning even more explicit and compact.

### Domain reviewer

Strengths:

- The numerical-decidability gate is a plausible contribution beyond ordinary
  MR identification.
- The P1 operator-floor argument is load-bearing and bounded; it is not
  overclaimed as arbitrary-mesh theory.
- Typed verdicts and MR-card assets are coherent software-testing artifacts.

Major concerns:

- The paper must continue distinguishing "MR identification" from "MR
  admissibility/decidability." Reviewers may otherwise see the contribution as
  incremental relative to existing scientific-software MT and MR-selection work.
- The strongest theoretical contribution is narrow: P1 constant-per-cell
  divergence on shape-regular triangular meshes. This is acceptable only if the
  paper keeps it positioned as an example of the gate, not as a general
  numerical theorem.

Domain recommendation: Major Revision to strengthen contribution clarity and
reduce density; empirical evidence is acceptable for bounded claims but not for
broad generalization.

### Practice and artifacts reviewer

Strengths:

- Data/software availability is now much stronger: Zenodo DOI, GitHub source
  repository, committed evidence directories, Minimum-MR-SubSet commit, public
  benchmark-input boundary, and fail-closed credential behavior are all stated.
- The package explicitly avoids claiming JSS Open Science validation before any
  JSS Open Science Board review.
- Reproducibility tiers are documented.

Major concerns:

- The paper still does not report user effort, authoring time, inter-author
  agreement, or maintenance burden for MR-card construction. For a JSS audience,
  this weakens practitioner-readiness.
- Some full reruns require GPU/public TFRecords/credentials; this is honestly
  disclosed, but reviewers may still prefer a clearer "what can be reproduced by
  reviewers in 30 minutes" box in the main text or supplement.

Practice recommendation: Minor-to-Major Revision. Artifact readiness is now
reasonable; adoption-cost evidence remains weak.

### Devil's Advocate

Strongest rejection argument:

The paper may be methodologically honest but still empirically underpowered for
a JSS regular paper if read as a tool/method evaluation. It has many cells, but
the truly independent primary-scale evidence is narrow: one main CFD task and
one changed-physics airfoil task, with other evidence serving supporting,
secondary, or stress-test roles. The evidence is carefully bounded, but careful
bounding does not by itself create generality. A skeptical reviewer could say:
"This is a promising audit framework demonstrated on a curated set of related
SciML examples, but it has not yet shown that independent practitioners or
independent defects benefit from it."

Critical issue:

- None that forces rejection if the paper is framed as a bounded method paper.

Major issues:

- Empirical independence is still the central acceptance risk.
- Page length and density can magnify reviewer skepticism.
- Adoption cost is asserted qualitatively rather than measured.

## Scores

Scores are ordinal reviewer judgments, not calibrated acceptance probabilities.

| Dimension | Score / 100 | Rationale |
|---|---:|---|
| Originality | 78 | Numerical-decidability gate and typed verdict framing are novel enough for JSS if differentiated from MR identification. |
| Methodological rigor | 72 | Strong artifact discipline and evidence gates; limited by bounded primary independence and descriptive/non-independent cells. |
| Evidence sufficiency | 66 | Sufficient for bounded method claims; below stable-acceptance level for broad empirical utility. |
| Argument coherence | 72 | Structure is much improved, but density and many boundaries still slow the reader. |
| Writing quality | 70 | Technically clear but compressed, table-heavy, and reviewer-load intensive. |
| Literature integration | 73 | Covers MT/SciML/testing context reasonably; contribution contrast must stay sharp. |
| Significance and impact | 74 | Important niche for SciML V&V, with practical artifact value, but adoption evidence is thin. |

Weighted overall judgment: **about 71/100**, corresponding to **Major Revision**
under the reviewer rubric, with potential to reach Minor Revision if the
empirical-independence and density risks are reduced.

## Gap to stable JSS acceptance

Stable acceptance here means a realistic path toward reviewable
major-revision-or-better and eventually minor/accept after revision, not a
guaranteed acceptance.

Current state:

- Reviewability: **moderate to good**.
- Desk-reject risk: **low to moderate**, mainly due to length/density rather
  than topic mismatch.
- Stable acceptance probability without further revision: **not yet high**.
- Main blocker: **empirical sufficiency for a regular JSS method paper**.

### Main empirical conclusion

The empirical evidence **meets the minimum credibility threshold** for a bounded
method/proof-plus-validation manuscript because:

- there are multiple evidence units with explicit roles;
- repeated cells are not misrepresented as independent samples;
- claims are tied to ledgers and validators;
- results include changed-physics, cross-family, and external-audit checks.

It **does not yet meet a stable-acceptance level** for a broad JSS empirical
tool/method paper because:

- independent primary-scale SUT evidence remains limited;
- no independent real-defect corpus or independently authored mutant set is
  used to test coverage claims;
- adoption cost/user effort is not measured;
- baseline comparisons are deliberately secondary and not a full competitive
  evaluation.

## Priority issues

P0. Empirical independence gap.

- Best fix: add one additional independent primary-scale SUT/task with the full
  rubric-to-verdict chain, preferably outside the current cylinder-flow family.
- Alternative if new execution is infeasible: explicitly recast the paper as a
  method/proof-plus-bounded-validation paper in title/abstract/introduction and
  reduce any wording that sounds like broad empirical validation.

P1. Page length and density.

- The 45-page single-column package remains above JSS's recommendation.
- Further compress main-text tables and move more audit detail to supplement,
  or prepare a verified double-column form if that is the intended submission
  format.

P1. Practitioner/adoption evidence.

- Add a compact adoption-cost subsection or table: MR-card authoring effort,
  role split, which steps are automated, which require domain/numerical
  expertise, and which steps reviewers can rerun quickly.
- Do not invent person-hours unless actually measured.

P2. Baseline and comparator clarity.

- Keep rollout accuracy, generic/LLM MR generation, and sibling reruns as scope
  contrasts unless stronger comparator experiments are actually run.
- Avoid implying baseline superiority.

P2. Open Science status.

- Current availability statements are adequate for submission, but the paper
  must not imply JSS Open Science validation before review.

## Recommended next repair plan

1. Decide whether one additional independent primary-scale SUT can be executed
   without compromising evidence integrity.
2. If yes, run it as a full rubric-to-verdict evidence unit and add a ledger ID
   before changing prose.
3. If no, make the bounded-validation positioning even more explicit and remove
   residual broad-tool-evaluation cues.
4. Compress another 5-8 pages from the JSS package by moving secondary evidence
   and table detail to supplementary material.
5. Add a no-fabrication adoption-cost table that distinguishes measured,
   unmeasured, automated, and expert-required steps.

## Final reviewer answer

The manuscript is now a plausible JSS submission candidate but not yet at
"stable acceptance" level. The evidence is credible and honestly bounded; the
remaining gap is that JSS regular-paper reviewers may expect stronger
independent empirical validation or a cleaner, shorter method-paper narrative.
The most important next decision is whether to add a genuinely independent
primary-scale evidence unit. If that is not feasible, the safest path is to
embrace the bounded method/proof-plus-validation identity and reduce density so
reviewers judge the paper by that standard rather than by broad empirical tool
benchmark standards.
