# Targeted supplemental empirical scan plan for JSS stability

Date: 2026-07-03

Target: one optional supplemental empirical unit for the JSS regular-paper
package.

Decision posture: do not add another ordinary synthetic or same-family SUT.
Only proceed if the candidate is genuinely independent and improves the
remaining acceptance risk identified in `paper/85_jss_p0_p1_repair_report.md`:
production-adjacent or real-defect-linked evidence, with a full
rubric-to-verdict chain and minimal main-text footprint.

## Evidence gate

The candidate must satisfy all hard gates:

1. Not a repeat of the current synthetic periodic-advection evidence.
2. Independent SUT, independent data, or independent defect source.
3. A scarce algebraic or physical structure exists before seeing outcomes.
4. Full chain is executable:
   candidate MR -> rubric decision -> MR card -> source/follow-up run ->
   metric -> verdict -> claim-ledger entry.
5. Main-paper footprint is limited to one table row and one short paragraph;
   detailed evidence goes to supplementary material.
6. Failed, rejected, or inconclusive runs remain valid outputs and must be
   ledgered.

Hard No-Go conditions:

- no machine-readable metadata for the required physical precondition;
- no downloadable source/follow-up field data or checkpoint within a reasonable
  time budget;
- relation requires undocumented assumptions about geometry, coordinate axes,
  velocity components, or boundary labels;
- result would only support another "synthetic/generated PDE" claim;
- main text would need a new subsection or substantial theory expansion.

## Primary recommendation

### Candidate A: RealPDEBench Foil mirror-symmetry gate

Provisional rank: 1.

Source basis:

- RealPDEBench describes paired real-world measurements and matched numerical
  simulations for five physical systems, including `foil`.
- The project page reports real experiments, CFD simulations, 700+ trajectories,
  ten baseline models, and physics-oriented metrics.
- The GitHub README identifies the five scenarios as `cylinder`, `fsi`,
  `controlled_cylinder`, `foil`, and `combustion`; the foil scenario has
  98 real trajectories and 99 numerical trajectories; real fields include
  `u`, `v`, while numerical fields include `u`, `v`, `p`.
- The website describes the foil dataset as NACA0025 airfoil data with angle of
  attack from 0 to 20 degrees and Reynolds number from 2968 to 17031.

Why this is the best fit:

- It is production-adjacent relative to the current manuscript because it uses
  real measured flow data plus paired CFD, not a self-generated PDE toy.
- It matches a scarce algebraic structure already central to the paper:
  geometric mirror symmetry is physically admissible only under symmetry
  preconditions. For a symmetric NACA0025 foil, zero angle of attack is the
  plausible admissible case; non-zero angle of attack is the natural rejection
  case.
- It can strengthen the paper without changing the thesis: the expected claim
  is not "the model is reliable", but "the same validity gate can be applied to
  public real-world paired SciML flow data and can reject non-admissible
  mirror candidates when physical preconditions fail."

Planned MR family:

- Candidate relation: mirror-y equivariance for a symmetric foil at zero angle
  of attack.
- Source transformation: reflect the spatial coordinate about the centerline.
- Output mapping: `u(x,y) -> u(x,-y)`, `v(x,y) -> -v(x,-y)`.
- Rejection condition: non-zero angle of attack, asymmetric geometry/mesh,
  missing centerline alignment, missing component orientation, or measurement
  floor dominating the tolerance.
- Metric: relative L2 of transformed field difference, reported with an
  interpolation / measurement / simulation-pair floor.
- Verdict types: `PASS`, `FAIL`, `REJECTED_PHYSICAL_PRECONDITION`,
  `DEFERRED_NUMERICAL_FLOOR`, or `INCONCLUSIVE_MEASUREMENT_FLOOR`.

First-screen commands if execution is approved:

- Download metadata only for `foil`.
- Confirm whether metadata contains angle of attack and a zero-degree or
  near-zero-degree subset.
- Inspect `channels.json` and coordinate metadata.
- Download the smallest admissible real and numerical split needed for one
  source/follow-up check.
- Run a no-training verdict pass first, using released fields/checkpoints only.

Go decision:

- Go if metadata exposes AoA, field orientation, and a zero-AoA or explicitly
  symmetric subset; and if at least one real or numerical foil case can be
  transformed and scored without retraining.
- No-Go if zero-AoA is absent or undocumented, axes are ambiguous, or the
  measurement/interpolation floor dominates all useful tolerances.

Expected manuscript footprint if successful:

- Add one row to the existing MR-card verdict map:
  "RealPDEBench foil mirror gate".
- Add one sentence to experimental subjects:
  "A production-adjacent public real-flow benchmark was screened for a
  mirror-symmetry gate; the detailed evidence is supplementary."
- Add one short supplementary subsection with MR card, metadata provenance,
  floor estimate, verdict table, and blocked claims.

Allowed claim wording:

- "We screened a public paired real/simulation flow benchmark for the same
  mirror-symmetry admissibility gate."
- "The gate is applied to production-adjacent real measurement data when
  metadata and measurement floors permit."
- "The result is a public-data validity-gate witness, not a real-defect rate,
  production deployment study, or model-reliability claim."

Blocked claim wording:

- "The method is validated on production CFD."
- "The method detects real defects."
- "The method generalizes to all real aerodynamic data."
- "RealPDEBench proves broad SciML reliability."

## Backup candidates

### Candidate B: RealPDEBench Cylinder or Controlled Cylinder

Provisional rank: 2.

Value: public real-world measured flow data with paired simulations and released
models. It could support time-shift, periodic-statistic, or control-parameter
relations.

Risk: the algebraic relation is less clean than the foil zero-AoA mirror gate.
Periodic wake dynamics and forced control may support statistical or
phase-conditioned relations, not exact MR verdicts. This risks adding theory
and length.

Go only if metadata exposes forcing frequency/phase or a documented symmetry
precondition that yields a clear admissible/rejected pair.

### Candidate C: PDEBench public benchmark with a conservation or scaling MR

Provisional rank: 3.

Value: independent benchmark, broad PDE coverage, published datasets,
pretrained models, and baseline scripts. PDEBench includes data generation,
download, and baseline model code for tasks such as advection, Burgers,
reaction-diffusion, Darcy flow, shallow water, and compressible Navier-Stokes.

Risk: still simulated/generated PDE evidence. This is useful as a benchmark
replication but does not directly answer the strongest JSS concern about
real-world or production-adjacent evidence.

Go only if RealPDEBench is blocked and the selected task provides a rare
algebraic contrast absent from the current paper.

### Candidate D: GitHub real-defect mining in DeepXDE / NeuralOperator /
PhysicsNeMo

Provisional rank: exploratory only.

Value: could become real-defect-linked if a closed issue/PR documents a
reproducible boundary-condition, coordinate, normalization, conservation, or
equivariance bug that can be checked before/after the fix.

Risk: high screening cost and high failure rate. Most issues are installation,
API, dependency, or performance problems rather than MR-relevant physical
defects. A library-level issue may also drift away from the paper's SciML
surrogate-SUT framing.

Go only if the issue has:

- a specific commit or PR fixing behavior;
- a minimal reproducer;
- physical or algebraic semantics;
- before/after executable versions;
- a relation-level verdict that can be stated without inventing a defect.

### Candidate E: Local P3 SemanticMutation repository

Provisional rank: not suitable as the main JSS supplemental SUT.

Value: strong source of semantic-fault classes and mutation-testing
infrastructure; useful for designing a real-defect/mining query or seeded
operator taxonomy.

Risk: it concerns single-output scientific-computing kernels and semantic
mutation adequacy, not an independent SciML surrogate SUT with public
real-world field data. Using it as the new primary evidence would not answer
"is this only self-made SciML evidence?"

Use only as an auxiliary taxonomy for screening GitHub issues or defining
fault classes.

## Targeted scanning protocol

### Phase S0: lock the added-evidence question

Preconditions:

- JSS package remains 36 pages.
- Current P0/P1 repairs are not reopened.
- The candidate is allowed to fail closed.

Core steps:

1. State the exact review risk being addressed:
   "lack of public production-adjacent or real-world data witness."
2. Freeze allowed claims and blocked claims before inspecting outcomes.
3. Decide that no new main-text theory section is allowed.

Exit condition:

- A one-paragraph evidence question and blocked-claim list exist.

Review / drift check:

- Reject any candidate that mainly increases SUT count but does not address
  public real-world / production-adjacent evidence.

### Phase S1: metadata-only candidate screen

Preconditions:

- Public source URL and license/access terms are recorded.

Core steps:

1. For RealPDEBench `foil`, download metadata only.
2. Inspect scenario metadata, channel names, coordinate axes, AoA/Re fields,
   split definitions, and trajectory IDs.
3. Record whether zero-AoA or explicitly symmetric cases exist.
4. Record whether non-zero AoA cases exist for rejected-candidate contrast.

Exit condition:

- Candidate A is marked `go`, `no-go`, or `defer` with file paths and metadata
  evidence.

Review / drift check:

- If AoA or axes are inferred rather than documented, mark `no-go`; do not
  guess.

### Phase S2: algebraic MR-card precommitment

Preconditions:

- Metadata supports at least one admissible or rejected foil-mirror case.

Core steps:

1. Draft an MR card for foil mirror-y.
2. Specify physical preconditions, representation mapping, metric, tolerance,
   and floor source.
3. Specify the rejection conditions for non-zero AoA.
4. Add a small test that verifies the MR card fails closed when metadata is
   missing or ambiguous.

Exit condition:

- MR card can be validated without looking at outcome values.

Review / drift check:

- The MR must be a gate witness, not a model-performance benchmark.

### Phase S3: minimal no-training verdict run

Preconditions:

- MR card passes schema validation.
- Minimal real/numerical data and, if needed, one released checkpoint are
  available.

Core steps:

1. Load one or a few admissible source cases.
2. Build the reflected follow-up field.
3. Estimate interpolation / measurement / paired-simulation floor.
4. Score source/follow-up fields.
5. Record every run in `research_assets/runs/realpdebench-foil-mirror-gate/`.

Exit condition:

- At least one typed verdict exists, including pass/fail/reject/defer/
  inconclusive; failure and inconclusive outcomes are acceptable.

Review / drift check:

- Do not claim model reliability or real-defect detection.

### Phase S4: evidence-ledger integration

Preconditions:

- S3 produced raw outputs and a typed verdict ledger.

Core steps:

1. Add an experiment-ledger entry.
2. Add a claim-ledger entry with conservative wording.
3. Add regression tests for the new claim boundary and key phrases.
4. Run evidence validators and full tests.

Exit condition:

- Validators and tests pass, or the candidate is rejected and documented.

Review / drift check:

- If wording exceeds the ledger, downgrade the wording rather than expanding
  the claim.

### Phase S5: supplement-first paper integration

Preconditions:

- S4 passes evidence gates.

Core steps:

1. Add detailed evidence to supplementary material.
2. Add one row to the main verdict map.
3. Add one short main-text sentence or paragraph.
4. Rebuild JSS PDF; if the PDF exceeds the length boundary, compress elsewhere
   or move the new text fully to supplement.

Exit condition:

- JSS PDF remains no worse than the current 36-page upper-edge state, and all
  tests pass.

Review / drift check:

- If the main text grows into a new section, stop and revert to supplement-only
  reporting.

## Subagent screening design

Use independent agents only for screening, not for fabricating claims.

1. Algebraic-structure scout:
   - Role: identify candidate MR families from metadata and equations.
   - Best-fit base model: strongest mathematical/physical reasoning model
     available.
   - Output: admissible/rejected preconditions, not result claims.

2. Repository/issue scout:
   - Role: scan GitHub issues/PRs for reproducible bug-linked candidates.
   - Best-fit base model: code-search-oriented model with strong repository
     navigation.
   - Output: candidate issue IDs, commits, reproducer paths, and No-Go reasons.

3. Reproducibility engineer:
   - Role: run metadata-only and minimal no-training checks.
   - Best-fit base model: code-execution-oriented model with conservative
     debugging behavior.
   - Output: commands, manifests, hashes, output paths.

4. Evidence auditor:
   - Role: enforce claim-ledger wording and blocked claims.
   - Best-fit base model: conservative reviewer model.
   - Output: supported / qualified / blocked claim table.

## Initial ranking

| Rank | Candidate | Expected ROI | Main risk | Decision |
|---|---|---|---|---|
| 1 | RealPDEBench Foil mirror-y gate | High if zero-AoA metadata exists | AoA/axis metadata may be insufficient; floor may dominate | First screen |
| 2 | RealPDEBench Cylinder / Controlled Cylinder | Medium | relation may be statistical, not exact MR | Backup |
| 3 | PDEBench conservation/scaling MR | Medium-low | simulated benchmark only | Backup if RealPDEBench blocked |
| 4 | DeepXDE / NeuralOperator / PhysicsNeMo real-defect mining | Potentially high, but uncertain | issue mining may not yield executable physical defect | Parallel exploratory scan only |
| 5 | Local P3 SemanticMutation | Low as SUT, useful as taxonomy | not independent SciML surrogate evidence | Auxiliary only |

## Recommendation

Run Phase S1 on RealPDEBench Foil first. Do not run any heavy training. The
first decision should be metadata-only: if zero-AoA / symmetry metadata and
axes are not explicitly documented, stop and record No-Go. If they are present,
proceed to an MR-card precommitment and a minimal no-training verdict run.

This is the only currently identified candidate that plausibly satisfies the
JSS-stability target without turning the paper into a broader benchmark study.
