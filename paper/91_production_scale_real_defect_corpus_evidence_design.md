# Production-scale / real-defect-corpus evidence design for stronger external validity

Date: 2026-07-03

Target venue: Journal of Systems and Software (JSS), regular paper.

Purpose: assess whether stronger external-validity evidence is necessary for
stable JSS acceptance, and define what would count as production-scale or
real-defect-corpus evidence without fabricating results.

## Current state

Current external-validity evidence is deliberately bounded:

- Primary trained-SUT evidence: MeshGraphNets-family cylinder-flow workflow and
  same-task variants.
- Independent full-chain task: six periodic-convolution SUTs on synthetic
  periodic advection, with full rubric-to-verdict evidence.
- Production-adjacent public-data witness: RealPDEBench foil preflight, typed
  verdict inconclusive because no independent PIV measurement-floor bound is
  available.
- Real-defect-linked witness: DeepXDE PeriodicBC issue #26 / PR #27 semantic
  boundary-condition witness, typed verdict pass for reproducing the
  derivative-periodicity semantic contrast.
- External sibling evidence: read-only Minimum-MR-SubSet audit/reruns and CPU
  replays.

Current conclusion: enough for a credible JSS method-paper submission, not
enough for a low-risk "stable accept" claim if reviewers expect production-scale
or real-defect-corpus evidence.

## Necessity assessment

### Is stronger evidence required before submission?

No, not strictly required for a JSS regular-method submission.

Reason:

- The paper's positive claim is methodological: validity-gated, numerically
  decidable SciML metamorphic testing with auditable assets.
- The manuscript explicitly blocks reliability, production CFD, and
  real-world-defect-rate claims.
- The current evidence now includes one independent full-chain task, one
  production-adjacent public-data preflight, and one external issue/PR-linked
  semantic witness.
- Additional production-scale or real-defect-corpus evidence would likely exceed
  the current submission schedule and risk turning the paper into a broader
  benchmark/corpus paper.

### Would stronger evidence materially reduce review risk?

Yes, if and only if it is genuinely production-scale or corpus-level.

It would reduce the main remaining Major Revision risk:

- "The external-validity story is a bounded mosaic rather than a clean
  production or real-defect evaluation."

It would not materially help if it is merely:

- another synthetic PDE;
- another same-family MGN/airfoil run;
- another inconclusive public-data preflight;
- another author-designed mutant catalogue;
- a GitHub issue with no executable semantic reproducer.

## Stronger-evidence target

The strongest feasible external-validity upgrade is:

> A small but real external SciML defect corpus with executable
> rubric-to-verdict reproductions.

Minimum acceptance criteria:

1. At least 5 external defect/fix units from public SciML or scientific-ML
   repositories.
2. At least 3 repositories or independent subsystems.
3. Each unit has an issue, PR, commit, or release note that documents the defect
   or behavioral fix.
4. Each unit maps to a predeclared MR family or validity-gate class:
   boundary-condition periodicity, conservation/floor, geometry mapping,
   coordinate/component transformation, normalization/units, or permutation/
   representation invariance.
5. Each unit has a minimal executable witness:
   candidate MR -> rubric decision -> MR card -> source/follow-up or before/
   after check -> metric -> typed verdict -> claim ledger.
6. Failed and inconclusive units remain in the corpus.
7. The manuscript may report only corpus construction and bounded detection /
   triage behavior, not population-wide defect prevalence or general reliability.

## Candidate corpus sources

Priority repositories:

1. DeepXDE
   - Fit: PINN boundary conditions, operator constraints, geometry conditions.
   - Existing seed: issue #26 / PR #27 PeriodicBC derivative-order support.
   - Risk: many issues are usage questions rather than defects.

2. NeuralOperator / neuraloperator
   - Fit: FNO / operator-learning code paths, padding, coordinate grids,
     resolution handling.
   - Risk: few issues may be directly MR-relevant or easy to replay.

3. NVIDIA PhysicsNeMo / Modulus
   - Fit: production-adjacent SciML framework, MeshGraphNet, GraphCast,
     CFD/weather examples.
   - Risk: heavy dependencies and GPU requirements; many issues are
     installation, documentation, or performance issues.

4. RealPDEBench / PDEBench ecosystems
   - Fit: public benchmark data and metadata, physical fields, data loaders.
   - Risk: defects may concern datasets or documentation rather than SUT
     behavior.

5. JAX-CFD / PhiFlow / torch-cfd-like scientific ML utilities
   - Fit: boundary conditions, periodic grids, conservation, differentiable
     solvers.
   - Risk: may be outside "learned surrogate SUT" framing unless scoped as
     scientific-ML infrastructure.

## Phase-loop execution design

### Phase R0: corpus protocol lock

Preconditions:

- Current JSS submission package remains unchanged except for optional
  supplement references.
- No claim of production validation or defect-rate improvement is allowed before
  evidence exists.

Core steps:

1. Freeze inclusion/exclusion rules.
2. Freeze MR-family taxonomy and typed verdict labels.
3. Define per-unit evidence schema.
4. Define No-Go rules.

Exit condition:

- A corpus protocol file exists and validators can check unit completeness.

Review and drift check:

- Reject any unit that is only a documentation typo, installation dependency,
  or unsupported user code.

### Phase R1: issue/PR mining

Preconditions:

- R0 protocol complete.

Core steps:

1. Search public issues/PRs using targeted terms:
   `periodic`, `boundary`, `conservation`, `normalization`, `coordinate`,
   `permutation`, `grid`, `padding`, `symmetry`, `units`, `component`.
2. Save raw issue/PR/commit JSON or patch files.
3. Screen each candidate into `go`, `defer`, or `no-go`.

Exit condition:

- At least 20 candidates screened, or fewer if search saturation is documented.

Review and drift check:

- A candidate cannot be counted as real-defect-linked unless an external issue,
  PR, commit, or release note documents the defect/fix.

### Phase R2: semantic witness construction

Preconditions:

- At least 5 `go` candidates.

Core steps:

1. Write one MR card per candidate.
2. Build a minimal reproducer that does not require full training unless the
   defect requires it.
3. Prefer analytic, CPU-only, or fixture-level reproductions when they directly
   represent the defect semantics.
4. Record source/follow-up metrics and typed verdict.

Exit condition:

- At least 5 units have typed verdicts, including pass/fail/inconclusive as
  observed.

Review and drift check:

- Do not treat a dependency or environment failure as a semantic SUT defect.

### Phase R3: corpus ledger and statistics

Preconditions:

- R2 produced typed reports.

Core steps:

1. Add experiment-ledger entries.
2. Add claim-ledger entries with bounded wording.
3. Report corpus counts:
   screened, accepted, executed, pass/fail/inconclusive, no-go reasons.
4. If the denominator supports it, report descriptive percentages with Wilson
   intervals; otherwise report counts only.

Exit condition:

- Evidence validators and corpus tests pass.

Review and drift check:

- Do not report prevalence, ecosystem-wide defect rate, or method superiority.

### Phase R4: paper integration

Preconditions:

- R3 passes.

Core steps:

1. Put detailed corpus table in supplement.
2. Add one main-text row and one short paragraph only if page budget allows.
3. Update cover letter to describe the corpus as external real-defect-linked
   evidence.

Exit condition:

- JSS package remains at or below current page-risk threshold; all tests pass.

Review and drift check:

- If the corpus requires a new theory section, move it to a follow-up paper
  rather than overloading the JSS submission.

## Go / no-go decision for current submission

Recommendation: **do not run the full corpus before this JSS submission**.

Reason:

- The current package is submission-ready and already at the 36-page upper edge.
- A real-defect corpus is a separate empirical contribution with substantial
  screening, execution, and reporting cost.
- A rushed corpus would be worse than no corpus: weak issue selection or
  incomplete reproducers would create integrity risk.

Recommended current action:

- Keep the current JSS submission bounded and clear.
- Prepare the real-defect corpus as a post-submission or revision-round
  reserve.
- If reviewers explicitly request stronger external validity, execute R0-R4 as
  the response plan.

## Claim boundary

Allowed future wording after successful corpus execution:

- "We constructed and executed a small external issue/PR-linked SciML
  defect-witness corpus."
- "The corpus shows that the admissibility gate can be applied to several
  independently sourced defect/fix units."
- "The result is a bounded external-witness study."

Forbidden wording even after execution:

- "The method detects real-world defects in general."
- "The corpus estimates real defect prevalence."
- "The method is production validated."
- "The method is superior to existing testing or monitoring methods."
