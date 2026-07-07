# 75 · Deep-research RQ and venue recommendation record

Date: 2026-07-03

Purpose: persist the deep-research assessment requested by the user: research-question
refinement, objective contribution evaluation, target-journal recommendation, and the
evidence basis for the recommendation. This record is descriptive only; it does not
modify the manuscript, claim ledger, experiments, or tests.

## 2026-07-03 reviewer recalibration addendum

This record was subsequently recalibrated by `paper/76_academic_reviewer_venue_recalibration.md`
using an academic-paper-reviewer style panel. The research-question extraction and
contribution assessment below remain valid, but the target-journal strategy is revised:

- **Operational target for the next realistic submission:** Journal of Systems and
  Software (JSS), regular paper, after focused tightening.
- **Aspirational ceiling target:** ACM TOSEM only after R1-R5 revision, ACM package
  migration, green venue-specific gates, clearer C53 centrality, and a stronger
  reviewer-simulation result.
- **Do not submit the current manuscript to TOSEM in its present state.**

The reason for the change is not a loss of scientific contribution. It is the gap
between the current manuscript/package state and a stable top-SE submission: broad
first-page framing, theorem visibility, denominator/effective-N trust, practitioner
workflow clarity, and venue-package readiness remain open issues.

## Evidence basis

Internal project evidence read before this record:

- `manuscript/main.tex`: active manuscript after numerical-decidability reframing.
- `research_assets/experiments/claim-ledger.yml`: claim ledger, including
  `C53-shape-regular-p1-operator-floor-soundness`.
- `paper/67_deepresearch_verdict_and_ABC_program.md`: prior deep-research venue
  ceiling assessment and A+B+C route.
- `paper/73_academic_reviewer_full_review.md`: TOSEM-calibrated simulated review,
  verdict `Major Revision with strong resubmission prospects`.
- `paper/74_tosem_stable_acceptance_gap_and_phase_loop_plan.md`: latest gap and
  phase-loop repair plan.
- `paper/76_academic_reviewer_venue_recalibration.md`: subsequent reviewer-panel
  recalibration that revises the operational target from TOSEM to JSS.

Verification status from `paper/74`:

- `rtk python3 tools/validate_research_assets.py`: exit 0.
- `rtk python3 tools/validate_experiment_protocol.py`: exit 0.
- `rtk python3 tools/ist_wordcount.py`: 14611 / 15000 words under IST counting,
  headroom 389.
- `rtk .venv/bin/python -m pytest tests -q`: 433 passed, 18 failed.
- `manuscript/main.tex` builds to a 51-page PDF with no undefined references or
  citations, no LaTeX Error, no Missing character, no Overfull hbox, and no rerun
  warning after the final scan; Underfull hbox warnings remain.

External source checks:

- ACM journal submissions require the ACM authoring template; LaTeX review
  submissions should use `\documentclass[manuscript]{acmart}` single-column format.
  Source: ACM Submissions page,
  `https://www.acm.org/publications/authors/submissions`.
- JSS states that papers should support claims through empirical studies,
  simulation, formal proofs, or other validation, and lists verification,
  validation, testing, AI in SE, and SE for AI systems as relevant topics. Source:
  `https://www.sciencedirect.com/journal/journal-of-systems-and-software/about/aims-and-scope`.
- EMSE describes itself as a forum for applied software-engineering research with a
  strong empirical component, with preference for studies that can be replicated or
  expanded. Source:
  `https://link.springer.com/journal/10664/aims-and-scope`.

TOSEM-specific page content was not reliably extractable in this environment, so the
TOSEM discussion below is based on the project-internal deep-research record, the
manuscript's field fit, and ACM publication-format requirements, not on an
unverified direct quote from the TOSEM website.

## Refined research question

Main research question:

> For scientific machine-learning surrogates, when can a physics-derived
> metamorphic relation be treated as a numerically decidable and physically
> admissible oracle-free software test?

Recommended sub-questions:

1. **RQ1: admissibility.** How should MR admissibility be formalized for SciML
   surrogate software, considering physical basis, domain preconditions,
   representation mapping, and numerical decidability?
2. **RQ2: soundness.** For P1 discrete-divergence diagnostics, can an
   operator-floor bound determine when an absolute relation-level verdict is
   admissible and when it must be deferred?
3. **RQ3: verdict semantics.** Can typed verdicts distinguish SUT inconsistency
   from out-of-relation-domain application, mapping artifacts, and numerical-floor
   artifacts?
4. **RQ4: bounded utility.** Under bounded SUT, mutant, and witness evidence, does
   the gate provide complementarity, false-alarm removal, and coverage-boundary
   explanation without claiming baseline superiority or general reliability?

Short thesis statement:

> Numerical decidability is a soundness precondition for relation-indexed
> metamorphic testing of SciML surrogates: a relation-level verdict should be
> issued only when the relation is physically applicable and its tolerance dominates
> the intrinsic floor of the measurement operator.

## Objective contribution assessment

### Supported contributions

1. **Real methodological core.** The manuscript is no longer merely an MR workflow
   or artifact paper. Its core is a software-testing criterion: numerical
   decidability as a precondition for admissible oracle-free MR verdicts on SciML
   surrogates.

2. **Bounded theory contribution.** Claim C53 supports a local operator-floor bound
   for the P1 constant-per-cell divergence operator on shape-regular triangular
   meshes with C2 divergence-free reference fields and bounded Hessian. This is a
   legitimate soundness artifact, but only for the stated operator and mesh class.

3. **Executable and auditable mechanism.** MR cards, executable runners, typed
   verdicts, and the fail-closed claim ledger make the paper stronger than a prose
   method proposal. The audit trail is a major strength.

4. **Bounded empirical breadth.** The manuscript reports bounded evidence across
   MeshGraphNets cylinder flow, airfoil, PointMLP, PINN/FNO executions, and
   cross-program sibling witnesses. This supports gate behavior, complementarity,
   and coverage-boundary interpretation within stated limits.

5. **Strong claim discipline.** The manuscript and ledger repeatedly block general
   reliability, baseline superiority, arbitrary-mesh soundness, and real-world
   defect-detection-rate claims.

### Unsupported or still weak claims

The current evidence does **not** support:

- general SciML surrogate reliability;
- real-world defect-detection rates;
- baseline superiority over rollout accuracy, residual/UQ diagnostics, expert MR
  design, generic MR generators, or LLM-assisted MR candidate generation;
- arbitrary unstructured-mesh soundness;
- guarantees for degenerate/sliver meshes, non-P1 operators, discontinuous fields,
  learned-output-specific floors, or boundary-condition mismatch;
- statistically representative external-validity conclusions.

### Current maturity judgment

Scientific maturity:

- **TOSEM-potential Major Revision**, not Minor Revision and not ready-to-submit.
- The central contribution is credible and reviewable.
- The main remaining scientific risks are scope overbreadth, theorem visibility,
  denominator/effective-N trust, and practitioner workflow clarity.

Submission-engineering maturity:

- Not ready. The current active package is still Elsevier/IST-style. `paper/76`
  revises the operational target to JSS and keeps TOSEM only as an aspirational
  ceiling after package migration and green venue-specific gates. The full test
  suite currently has 18 failures according to `paper/74`.

## Target journal recommendation

### Revised operational recommendation: Journal of Systems and Software

Recommendation:

> Target Journal of Systems and Software (JSS), regular paper, for the next
> realistic submission after focused tightening.

Reasons:

1. **Best current operational fit.** The paper is fundamentally about software
   testing, metamorphic testing, oracle-free V&V, admissibility, and evidence
   discipline for AI/SciML software components. JSS explicitly covers software
   engineering methods and V&V/testing work, including AI in SE and SE for AI
   systems.

2. **Validation form matches the paper.** The manuscript's strongest asset is a
   proof-supported method plus bounded empirical validation and reproducible
   artifacts. JSS explicitly accepts multiple validation forms, including empirical
   studies, simulation, formal proofs, and other validation.

3. **Risk is lower than immediate TOSEM.** `paper/76` finds that the current paper
   has a real contribution but is not ready for immediate TOSEM submission because
   broad framing, theorem visibility, denominator/effective-N trust, practitioner
   workflow clarity, and package readiness remain unresolved.

4. **Contribution remains credible.** The reviewer panel agrees that C53, executable
   MR assets, typed verdicts, and claim-ledger discipline make a publishable SE
   method paper, provided the claims remain bounded.

Required before submission:

- narrow title/abstract/keywords so broad "SciML surrogates" wording does not
  outrun the evidence;
- add a theorem/proposition box for C53 with assumptions, bound, allowed claims,
  and forbidden claims;
- add a nominal-N / effective-N / inference-allowed table;
- add a practitioner checklist for applying the gate;
- reorganize breadth evidence as falsification roles, not generality accumulation;
- repair venue-specific tests and prepare a JSS-compatible submission package.

### Aspirational ceiling: ACM TOSEM

Recommendation:

> Keep ACM TOSEM as an aspirational top-SE target only after the focused revision
> loop closes and the package is migrated to ACM `acmart` review format.

Reasons:

- TOSEM remains the strongest prestige ceiling if the paper is framed as a
  soundness/admissibility criterion rather than a broad SciML reliability paper.
- C53 gives a defensible theoretical spine, but it must become visually and
  logically central.
- The current active package/test state is not TOSEM-ready according to `paper/74`
  and `paper/76`.

Conditions for returning TOSEM to primary target:

- ACM `acmart` review package completed.
- Full tests or venue-specific gates green.
- Title and abstract no longer outrun evidence.
- Nominal-N / effective-N / inference-allowed table added.
- Practitioner checklist and cost boundary added.
- Final reviewer simulation improves from "Major Revision" toward "Minor Revision"
  or "Major Revision leaning Minor".

### Not primary: EMSE

Reason:

- EMSE prioritizes applied software-engineering research with a strong empirical
  component. The current paper has empirical evidence, but its main contribution is
  a soundness criterion plus numerical theory. EMSE reviewers are likely to press
  harder on independence, sampling, replication, and statistical generalization.

### Not recommended now: IST

Reason:

- The manuscript already received an IST desk rejection in the project record.
  Returning to IST would discard much of the value of the current TOSEM-oriented
  C53/theory reframing unless the paper is deliberately downgraded and re-scoped.

### Excluded by user constraint: STVR

Reason:

- STVR may be technically plausible for metamorphic testing, but the project
  instructions explicitly state that STVR is not a candidate venue.

### High-risk stretch: IEEE TSE

Reason:

- TSE is an upper-bound stretch only after further independent subjects or stronger
  real-defect evidence. With the current evidence, the paper is too bounded and too
  method/theory-centered to be a realistic first target for TSE.

## Recommended positioning for the next revision

Recommended title direction:

> Numerical Decidability for Sound Metamorphic Testing of SciML Surrogates

or a narrower variant:

> Operator-Floor Admissibility for Metamorphic Testing of SciML Surrogates

Recommended framing:

- Lead with the soundness/admissibility criterion.
- Make C53 visually unavoidable.
- Treat MR cards, typed verdicts, LLM candidate generation, generic baselines, and
  sibling evidence as support mechanisms, not separate headline contributions.
- Replace any broad "SciML reliability" reading with bounded "relation-indexed
  SciML V&V evidence".

## Bottom-line judgment

The paper's research problem is real, timely, and defensible:

> oracle-free metamorphic testing of SciML surrogates needs a criterion for when a
> relation-level verdict is numerically decidable and physically admissible.

The academic contribution is strongest when framed as:

> a soundness/admissibility criterion, supported by a bounded P1 operator-floor
> theorem, executable artifacts, typed verdicts, and bounded empirical demonstrations.

The best current operational target is:

> **Journal of Systems and Software (JSS)**, after focused tightening.

The aspirational ceiling is:

> **ACM TOSEM**, only after the focused revision loop and ACM package migration.
