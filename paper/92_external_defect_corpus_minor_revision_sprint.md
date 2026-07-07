# One-week external defect-witness corpus sprint for JSS Minor-Revision risk reduction

Date: 2026-07-03

Target: Journal of Systems and Software (JSS), regular paper.

Goal: reduce the residual Major-Revision risk identified in
`paper/90_academic_reviewer_jss_stable_acceptance_rereview.md`, especially the
objection that the external-validity evidence remains bounded and mosaic-like.

Non-goal: do not claim production CFD validation, ecosystem-wide defect
prevalence, trained-SUT reliability, or superiority over uncertainty
quantification. The sprint is allowed to improve external-validity evidence only
if the evidence is external, issue/PR/commit-linked, executable, and traceable.

## Decision

Given a one-week empirical budget, the highest-ROI action is a small external
SciML defect-witness corpus, not another synthetic PDE or same-family SUT run.

Rationale:

- The current paper is already JSS-submission-ready but borderline
  Minor/Major because external validity is bounded.
- Another author-designed task would add length without answering the strongest
  reviewer objection: "does this work outside self-made examples?"
- A small public issue/PR-linked corpus can answer that objection more directly
  while staying within a method-paper scope.
- Full training on production-scale SciML models is not the best one-week
  option because dependency, GPU, and data risks are high, and failures would be
  hard to interpret.

## Minimum success standard

The sprint counts as stronger external-validity evidence only if all conditions
hold:

1. At least 5 external defect/fix units.
2. At least 3 repositories or clearly independent subsystems.
3. Every unit has a public issue, PR, commit, or release note documenting the
   defect, behavior change, or fix.
4. Every unit maps to a predeclared MR family or validity-gate class.
5. Every counted unit has a complete chain:
   candidate MR -> rubric decision -> MR card -> source/follow-up or
   before/after witness -> metric -> typed verdict -> claim ledger.
6. Failed and inconclusive units remain recorded.
7. The main manuscript receives at most one short paragraph and one table row;
   detailed evidence goes to supplement.

If the sprint produces only 3-4 units, or only 1-2 repositories/subsystems, it
may be used as supplementary evidence but must not be described as a stronger
external-validity corpus.

## Candidate repositories

Priority sources, screened in this order:

1. DeepXDE
   - Existing seed: issue #26 / PR #27 PeriodicBC derivative-order support.
   - Search focus: boundary conditions, periodic constraints, derivatives,
     geometry, transforms.
2. NeuralOperator / neuraloperator
   - Search focus: FNO padding, coordinate grids, normalization, transforms,
     resolution handling.
3. NVIDIA Modulus / PhysicsNeMo
   - Search focus: boundary constraints, graph/weather/CFD data pipelines,
     normalization, coordinate handling.
4. RealPDEBench / PDEBench ecosystems
   - Search focus: data fields, metadata, component signs, boundary labels,
     loader semantics.
5. JAX-CFD / PhiFlow / related differentiable solver utilities
   - Search focus: periodic grids, boundary conditions, conservation,
     coordinate/component transforms.

## Phase R0: corpus protocol lock

Preconditions:

- Current JSS manuscript and ledgers remain the authority for existing claims.
- No new external-validity wording enters the paper before executable evidence
  exists.
- Existing DeepXDE PeriodicBC witness may be counted only as one seed unit.

Core steps:

1. Freeze inclusion and exclusion rules.
2. Freeze MR-family taxonomy:
   boundary-condition periodicity, conservation/floor, coordinate/component
   transform, geometry mapping, normalization/units, permutation/
   representation invariance, resolution/padding consistency.
3. Freeze typed verdicts: pass, fail, inconclusive, blocked-by-environment,
   no-go-not-semantic.
4. Create a screened-candidate ledger with raw source artifact paths.

Exit condition:

- A candidate can be classified without subjective post-hoc wording.

Review and acceptance:

- The evidence gate rejects any candidate without an external issue, PR,
  commit, or release note.
- A unit is not counted if the only evidence is a documentation typo, install
  problem, performance-only complaint, or unsupported user code.

Theme drift check:

- The sprint remains about validity-gated metamorphic testing for SciML
  software. It must not drift into a broad bug-mining paper or a framework
  quality survey.

## Phase R1: targeted candidate mining

Preconditions:

- R0 rules are fixed.
- Raw GitHub/source artifacts are saved before screening conclusions are made.

Core steps:

1. Search the priority repositories with targeted terms:
   `periodic`, `boundary`, `conservation`, `normalization`, `coordinate`,
   `permutation`, `grid`, `padding`, `symmetry`, `units`, `component`,
   `derivative`, `transform`, `mesh`.
2. Save raw issue/PR/commit metadata for each promising candidate.
3. Screen at least 20 candidates, or document search saturation if fewer
   plausible candidates exist.
4. Classify candidates as `go`, `defer`, or `no-go`.

Exit condition:

- At least 5 `go` candidates exist, or the sprint explicitly downgrades to
  partial evidence.

Review and acceptance:

- Each `go` candidate must have a plausible CPU/fixture/analytic witness path.
- Full training is allowed only if dependencies and data are already tractable.

Theme drift check:

- Reject candidates that test ordinary API usage rather than metamorphic or
  domain-validity semantics.

## Phase R2: executable witness construction

Preconditions:

- At least 5 `go` candidates are available.
- Each candidate has archived raw source evidence.

Core steps:

1. Write one MR card per counted unit.
2. Build a minimal executable witness for each candidate.
3. Produce source/follow-up or before/after metrics.
4. Emit typed verdict reports under `research_assets/runs/`.
5. Keep failures and inconclusive outcomes in the run ledger.

Exit condition:

- At least 5 counted units have typed reports and artifact paths.

Review and acceptance:

- A reviewer can follow every counted claim from manuscript wording to claim
  ledger, experiment ledger, run report, raw source artifact, and script.

Theme drift check:

- Do not report environment failures as semantic defects. Do not turn witness
  behavior into population-level defect rates.

## Phase R3: ledger, tests, and claim boundary

Preconditions:

- R2 reports exist.

Core steps:

1. Add experiment-ledger entries.
2. Add claim-ledger entries with bounded allowed wording.
3. Add tests that enforce artifact existence and claim wording boundaries.
4. Run research-asset validators and full manuscript regression tests.

Exit condition:

- Validators and tests pass.

Review and acceptance:

- Unsupported wording remains blocked. Inconclusive units are described as
  inconclusive.

Theme drift check:

- The sprint supports external validity only. It must not become a new central
  contribution that requires reorganizing the whole paper.

## Phase R4: JSS integration

Preconditions:

- R3 passes.

Core steps:

1. Put the corpus details in the supplement.
2. Add one main-text row and one short Results/Discussion paragraph.
3. Update the cover letter and claim map.
4. Rebuild the JSS PDF and check page count/log warnings.

Exit condition:

- JSS package remains within page-risk bounds and all evidence gates pass.

Review and acceptance:

- Academic reviewer re-review should no longer identify "no real external
  defect corpus" as the strongest Major-Revision objection.

Theme drift check:

- If the integration requires more than one paragraph and one row, move details
  to supplement or defer the corpus to a response-to-review package.

## One-week schedule

Day 1: R0 and R1 initial mining.

Day 2: Finish R1 screening and select the first 5 `go` units.

Days 3-5: R2 executable witness construction.

Day 6: R3 ledger, claim boundary, and regression tests.

Day 7: R4 paper integration, PDF verification, and reviewer re-review.

## Go / no-go rules

Proceed to paper integration only if the minimum success standard is met.

Use as supplementary reserve evidence only if the sprint yields partial but
traceable evidence.

Abort or defer if candidate witnesses require heavy GPU training, private data,
unavailable dependencies, or subjective interpretation without executable
metrics.
