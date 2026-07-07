# 76 · Academic-reviewer venue recalibration

Date: 2026-07-03

Purpose: use an academic-paper-reviewer style panel to review the current manuscript
objectively and recalibrate the target journal. This is a read-only review of the
paper; no manuscript, ledger, experiment, or test file is modified here.

## Materials reviewed

- `manuscript/main.tex`: active manuscript after numerical-decidability reframing.
- `research_assets/experiments/claim-ledger.yml`: claim boundaries, especially
  `C53-shape-regular-p1-operator-floor-soundness`.
- `paper/73_academic_reviewer_full_review.md`: prior TOSEM-calibrated full review.
- `paper/74_tosem_stable_acceptance_gap_and_phase_loop_plan.md`: latest gap plan and
  verification status.
- `paper/75_deep_research_rq_venue_recommendation.md`: prior deep-research venue
  recommendation.

External source checks used for venue fit:

- ACM author instructions: ACM journal submissions use the ACM authoring template;
  LaTeX review submissions should use `\documentclass[manuscript]{acmart}`.
  Source: `https://www.acm.org/publications/authors/submissions`.
- JSS scope: Journal of Systems and Software publishes software-engineering work and
  requires evidence through empirical studies, simulation, formal proofs, or other
  validation; topics include V&V, testing, AI in SE, and SE for AI systems.
  Source: `https://www.sciencedirect.com/journal/journal-of-systems-and-software/about/aims-and-scope`.
- EMSE scope: Empirical Software Engineering emphasizes applied software-engineering
  research with a strong empirical component and preference for replicable or
  expandable studies. Source:
  `https://link.springer.com/journal/10664/aims-and-scope`.

TOSEM-specific page text was not reliably extractable in the current environment.
TOSEM conclusions below therefore rely on the manuscript's SE-methodology fit, ACM
format requirements, and internal review records, not an unverified quotation from
the TOSEM site.

## Reviewer configuration

Primary field: software engineering, software testing, metamorphic testing.

Secondary field: scientific machine learning, numerical methods, computational
physics V&V.

Paper type: mixed methodological/theoretical paper with bounded empirical case
studies, executable artifacts, proof-supported claim boundaries, and seeded-fault
stress tests.

Panel:

1. **EIC / SE journal-fit reviewer**: evaluates target-journal fit, originality,
   field contribution, and desk-reject risk.
2. **Methodology reviewer**: evaluates denominators, independence, empirical design,
   statistics, and reproducibility.
3. **Domain/numerical reviewer**: evaluates C53, operator-floor assumptions, and
   physical/numerical validity.
4. **Practitioner/impact reviewer**: evaluates usability, operational workflow,
   cost, and relevance to software-testing readers.
5. **Devil's Advocate**: constructs the strongest rejection argument and checks
   whether venue ambition outruns evidence.

## Independent reviews

### 1. EIC / journal-fit review

Recommendation for current manuscript: **Major Revision for TOSEM; suitable for JSS
after focused tightening.**

Strengths:

- The manuscript has a recognizable SE-methodology core: numerical decidability as
  a soundness/admissibility condition for oracle-free metamorphic testing.
- The claim ledger and blocked-claim discipline are unusually strong and reduce the
  risk of overclaiming.
- C53 gives a real theoretical anchor; the paper is no longer merely a collection of
  MR-card artifacts.

Weaknesses:

- The first-page framing still risks a broad "SciML surrogates" reading, while the
  actual theory is P1 divergence on shape-regular triangular meshes and the evidence
  is bounded.
- TOSEM submission engineering is not ready: `paper/74` records an Elsevier/IST-style
  active package and 18 failing tests.
- The paper is dense and may be read as "one good theorem surrounded by too many
  supporting artifacts" unless the theorem and scope are made visually dominant.

Venue implication:

- TOSEM remains plausible only as an aspirational target after R1-R5 revision.
- JSS is the better operational target if the author wants a submission path closer
  to the current manuscript form.

### 2. Methodology review

Recommendation for current manuscript: **Major Revision; target should not be a
primarily empirical journal unless denominator presentation is repaired.**

Strengths:

- The manuscript explicitly states that subjects are selected for evidence roles, not
  statistical representativeness.
- It distinguishes descriptive cell summaries from inference where the sampling
  structure does not support population claims.
- The validators and artifact ledger create a good reproducibility posture.

Weaknesses:

- Reviewers still need one consolidated nominal-N / effective-N / inference-allowed
  table. Without it, the 240 airfoil cells, K=6 rosters, 30-trial mutant sweeps,
  sibling witness rows, and cross-program executions can be misread as independent
  evidence.
- Baseline language must stay framed as complementarity and false-alarm prevention,
  not competition.
- The full test suite currently fails 18 tests, which is a serious submission-readiness
  defect even if some failures are stale IST guards.

Venue implication:

- EMSE is not the best fit because it is likely to foreground empirical
  representativeness and statistical generalization.
- JSS is more forgiving of mixed evidence forms, provided the proof and validation
  logic are clear.

### 3. Domain / numerical V&V review

Recommendation for current manuscript: **Scientifically credible, but theorem boundary
must be made explicit before a top-SE submission.**

Strengths:

- C53 is a meaningful improvement: it supports a local P1 divergence floor bound
  under shape-regular triangular meshes and C2 divergence-free reference fields.
- The manuscript correctly blocks arbitrary-mesh, learned-output, non-P1, reliability,
  and fault-detection-rate extrapolations.
- The airfoil example is valuable because it shows the same gate producing a
  different typed verdict for a physically valid reason.

Weaknesses:

- The theorem is still too easy to skim past. A reviewer may confuse "unstructured
  Delaunay topology observed stable" with "general unstructured-mesh theorem".
- Boundary treatment, flux-form operators, discontinuous fields, and learned-output
  floors are central to deployment but remain future work.
- The paper should say more plainly when a user should replace the P1 diagnostic with
  a flux-form finite-volume operator.

Venue implication:

- This is the strongest argument for TOSEM, but only if C53 becomes the visible
  load-bearing contribution.
- If the manuscript keeps the current breadth-heavy structure, JSS is safer.

### 4. Practitioner / impact review

Recommendation for current manuscript: **Major Revision; practical value is present
but hard to extract.**

Strengths:

- The paper's practical contribution is clear once understood: invalid MR verdicts
  should not be treated as model faults.
- MR cards, runners, typed verdicts, and claim ledgers are operationally meaningful.
- The paper is honest about authoring effort and does not claim zero-cost automation.

Weaknesses:

- A practitioner cannot yet extract a concise "Monday morning" workflow from the main
  text.
- Cost-benefit evidence is absent. The paper can still be publishable, but it must
  avoid implying easy adoption.
- Cross-program and sibling evidence may look defensive unless each block states
  exactly what alternative explanation it falsifies.

Venue implication:

- JSS is a good target because it values validated software-engineering methods and
  practical relevance.
- TOSEM requires the same checklist and falsification map, but with sharper theoretical
  positioning.

### 5. Devil's Advocate review

Recommendation for current manuscript: **Do not submit to TOSEM now. Submit to JSS
after tightening, or keep TOSEM only after a focused revision cycle.**

Strongest rejection argument:

The manuscript may still be over-positioned. Its defensible core is narrow but real:
for one important class of measurement operator, numerical floors can make an
absolute MR verdict inadmissible unless the tolerance dominates the floor. The paper
then surrounds this core with many assets, baselines, LLM candidate sources, sibling
evidence, and seeded mutants. A strict TOSEM reviewer may conclude that the paper is
trying to convert excellent evidence discipline into broader generality than the
evidence warrants. If C53 is not accepted as a field-level contribution, the rest of
the manuscript becomes a careful but incremental testing workflow.

Critical issues:

- The title and abstract still invite broader SciML surrogate expectations than the
  evidence can support.
- The current package/test state is not submission-ready.
- General reliability and defect-rate claims are blocked, which is correct, but this
  also limits the paper's impact pitch for the very top venues.

Venue implication:

- For immediate or near-term submission, JSS is the fairer target.
- TOSEM should be reserved for a version where the theorem box, denominator table,
  practitioner checklist, and breadth-falsification map are already repaired.

## Editorial synthesis

Decision for current manuscript if submitted to TOSEM now:

> **Reject / Resubmit Encouraged or Major Revision at best**, depending on editor
> appetite. The paper has a publishable core, but current scope framing, theorem
> visibility, denominator trust, and package readiness are not yet strong enough for
> a stable TOSEM submission.

Decision for current manuscript if submitted to JSS after focused tightening:

> **Major Revision with realistic prospects.** The paper fits JSS better because JSS
> explicitly accepts software-engineering papers supported by empirical studies,
> simulation, formal proofs, or other validation, and the manuscript's mixed proof +
> bounded-validation structure is natural there.

Consensus findings:

- **5/5 reviewers** agree the paper has a real contribution.
- **5/5 reviewers** agree current evidence does not support general SciML reliability,
  baseline superiority, arbitrary-mesh guarantees, or real-world defect rates.
- **5/5 reviewers** agree the current manuscript is not ready for immediate TOSEM
  submission.
- **4/5 reviewers** favor JSS as the current operational target.
- **4/5 reviewers** keep TOSEM as an aspirational target after focused revision.

## Revised target-journal recommendation

### Revised operational target: JSS

The target journal should be revised from "primary TOSEM now" to:

> **Journal of Systems and Software (JSS), regular paper**, if the goal is the most
> realistic next submission after a focused but not radical revision.

Rationale:

- JSS scope directly covers software-engineering methods and tools for V&V and
  testing, AI in SE, and SE for AI systems.
- JSS accepts multiple validation forms, including empirical studies, simulation,
  formal proofs, and other validation, which matches this paper's proof + bounded
  empirical evidence pattern.
- The paper's practical artifact discipline, reproducibility, and claim-ledger
  posture are likely to be valued there.
- The external-validity limitations are still serious, but less likely to be a
  desk-level mismatch than at TOSEM.

Required before JSS submission:

- Narrow title and abstract so they advertise bounded relation-indexed SciML V&V,
  not general SciML surrogate reliability.
- Add the C53 theorem/proposition box.
- Add a nominal-N / effective-N / inference-allowed table.
- Add a practitioner checklist and cost boundary.
- Reduce density and move non-load-bearing breadth evidence out of the main path.
- Keep all claim-ledger boundaries intact.

### Aspirational target: TOSEM

TOSEM remains appropriate only as:

> **Aspirational top-SE target after R1-R5 focused revision and ACM package migration.**

Conditions for returning TOSEM to primary target:

- The manuscript is converted to ACM `acmart` review format.
- Full tests or venue-specific tests are green.
- C53 is visually and logically central.
- Broad title/abstract wording no longer outruns evidence.
- Denominator/effective-N and practical workflow concerns are fixed.
- The final reviewer simulation moves from "Major Revision" toward "Minor Revision"
  or "Major Revision leaning Minor".

### Not recommended as primary

- **TSE**: too high-risk with current evidence; likely to demand stronger real-defect
  or independent multi-system evidence.
- **EMSE**: likely to overemphasize sampling, independence, and empirical
  generalization relative to the paper's theory/method core.
- **IST**: prior desk rejection and current C53 reframing make this a fallback only
  after deliberate down-scoping.
- **RESS**: scope bridge remains structurally weaker unless the paper is rebuilt
  around reliability consequences; not the best target for the current SE-methodology
  framing.
- **STVR**: excluded by standing project instruction.

## Bottom line

The corrected venue strategy is:

1. **JSS as the operational target for the next realistic submission.**
2. **TOSEM as the stretch target only after the focused revision loop closes.**
3. **Do not submit the current manuscript to TOSEM in its present state.**

This changes the practical recommendation in `paper/75`: TOSEM remains the ceiling,
but JSS is the better current target after objective academic review.
