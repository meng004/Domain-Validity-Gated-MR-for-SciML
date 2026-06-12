# Experiment Evidence Package

## Scope

This package defines an evidence-gated empirical protocol for physically grounded
metamorphic-relation testing of MeshGraphNets-family cylinder-flow surrogates. It is a
protocol and asset-readiness package plus scoped real-SUT pilots, K=6 rosters, secondary
baseline contrasts, and a read-only external-scope audit; it is not a general reliability,
baseline-superiority, cross-SUT, or geometry-independent rate package. The rate-like
results admitted here are the bounded primary empirical scope upgrade grids over the K=6
MGN roster and three official held-out test trajectories, plus the trained FNO primary
workflow over generated Burgers/heat finite-difference data. The MGN grids are not a
single-source-trajectory estimate, but they remain one architecture family and one dataset.
The FNO workflow is a second trained primary execution, while staying outside cylinder-flow
and broad neural-operator claims.

## Evidence Inventory

| Artifact | Status | Evidence Limit |
|---|---|---|
| `research_assets/runs/node_permutation_fixture_verdict.json` | observed | Fixture-level asset plumbing only; SUT execution is `not-run`. |
| `research_assets/runs/real-sut-node-permutation-pilot/raw/metric_ledger.json` (+ raw `.npy` outputs, manifest) | observed | One-SUT/one-MR/one-case pilot: real MeshGraphNets cylinder-flow inference under node permutation; relative L2 = 0.0 (tol 1e-6), verdict pass. No rate or reliability claim. |
| `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json` (+ raw `.npy`, manifest; geometry in mirror-y-ood-stress-pilot) | observed | One-SUT/one-MR within-SUT frame rate: exact mirror-y is out-of-relation-domain on the real mesh; the approximate OOD-stress probe failed on 10/10 eval frames (0-9), median rel L2 0.737, ~3-5.5x the same-space mapping-error floor. Bounded within-SUT frame rate only; no reliability/accuracy/baseline/multi-SUT/geometry-independent claim. |
| `research_assets/runs/conservation-diagnostic-pilot/raw/{metric_ledger,conservation_report}.json` (+ raw `.npy`, manifest) | observed | One-SUT/one-MR/two-frame conservation diagnostic: absolute divergence-free relation stays deferred (reference divergence ~0.037 nondim, uncalibratable); reference-relative diagnostic passes (pred/reference divergence ratio 1.0025/1.0044). No absolute-conservation or rate claim. |
| `research_assets/runs/rollout-accuracy-baseline/raw/metric_ledger.json` (+ per-transition `v_pred` `.npy`, manifest) | observed | Same-SUT/same-trajectory one-step next-state accuracy diagnostic: median relative L2 0.0216 (min 0.0116, max 0.0788) over 9 transitions. The mirror-y OOD-stress violation (0.737) is ~34x this in-distribution accuracy. Accuracy diagnostic only; no reliability/baseline-superiority/multi-trajectory/cross-SUT claim. |
| `research_assets/runs/mirror-y-symmetric-mesh/raw/metric_ledger.json` (+ raw `.npy`, manifest) | observed | Exact mirror-y equivariance on a synthetic mesh that is provably symmetric about y=0 (bijection true, node-type match 1.0, reflection offset <1e-12, edge-set invariant): the exact relation is admissible (not downgraded) and the surrogate fails it, relative L2 1.10. Oracle-free equivariance test; synthetic no-obstacle OOD geometry; no accuracy/reliability/cross-SUT claim. |
| `research_assets/runs/primary-scope-upgrade/primary_scope_report.json` (+ source cases, per-trajectory/checkpoint manifests, and raw ledgers) | observed | Primary empirical scope upgrade: K=6 x 3 trajectories x 10 mirror-y OOD-stress grid fails 180/180, K=6 x 3 trajectories x 9 conservation-transition grid passes the reference-relative diagnostic 162/162 while absolute conservation remains deferred, and K=6 x 3 exact-symmetric-mesh input grid fails 18/18. Not a single-source-trajectory estimate; still not cross-SUT, cross-dataset, reliability, accuracy, or broad-generalization evidence. |
| `research_assets/runs/primary-volume-upgrade/primary_volume_report.json` (+ K=6 per-checkpoint manifests and raw ledgers) | observed-superseded | Phase-11 denominator-only run: K=6 x 10 mirror-y OOD-stress grid fails 60/60, K=6 x 9 conservation-transition grid passes 54/54, and K=6 x 3 exact-symmetric-mesh input grid fails 18/18. Superseded in the main text by the multi-trajectory primary-scope upgrade. |
| `research_assets/runs/seeded-fault-detection/raw/metric_ledger.json` (+ manifest, runner) | observed | Seeded-fault detection: the paper's MRs as detectors against a 10-mutant/5-class injected-fault catalogue (re-implemented from the read-only witness taxonomy). Conservation MR detects boundary/scale faults (3/10), mirror-y detects physical-channel/adjacency faults (2/10), node-permutation detects none (exact-by-design); union 5/10. Localizes by MR class. Not a real-world fault-detection rate, reliability, or cross-SUT claim. |
| `research_assets/runs/fno-k6-roster/fno_k6_aggregate.json` (+ per-SUT manifests, reports, checkpoints) | observed-supporting | Third architecture-family training roster: six torch FNO-2D checkpoints on closed-form synthetic Burgers/heat data. Superseded in the main text by the full FNO primary workflow package below. |
| `research_assets/runs/fno-primary-workflow/fno_primary_workflow_report.json` (+ per-SUT ledgers and raw `.npz` source/follow-up outputs) | observed | FNO primary workflow upgrade: six trained FNO-2D checkpoints over Burgers/heat. Periodic translation is admitted and passes 24/24 case cells; the periodic discrete-conservation MR is admitted-with-reference-floor and fails 24/24 case cells; the Dirichlet-boundary translation candidate is rejected 6/6. Full rubric-to-verdict evidence with raw source/follow-up outputs; outside cylinder-flow, performance, reliability, and broad neural-operator claims. |
| `research_assets/runs/phase3-unified-fault-catalog/phase3_unified_fault_catalog.json` | observed | Phase-3 v2 catalogue: 60 entries (10 executed canonical MGN mutants + 2 executed adversarial MGN mutants + 24 closed-form PINN probes + 24 closed-form FNO probes), with precision/recall and effect-size statistics. Catalogue-only inference; closed-form probes are not retrained mutant checkpoints. |
| `research_assets/runs/minimum-mr-subset-external-scope-audit/minimum_mr_subset_scope_audit.json` | observed-secondary-audit | Read-only Minimum-MR-SubSet external-scope audit at commit `9ef862ec37335b4834d0a1fb38b4b613af702f34`: 70 real ABD rows, 20 real true-fault-class rows, and three relevant SciML/PDE `PASS_WITNESS` rows. External witness evidence only; does not add new primary SUT executions to this paper. |
| `research_assets/runs/minimum-mr-subset-primary-rerun/cylinder-flow-mgn-runtime/abd_witness_report.json` (+ kill matrix, MR/mutant catalogues, residuals, provenance) | observed | Minimum-MR-SubSet primary rerun: real held-out DeepMind cylinder-flow MeshGraphNet runtime witness, `PASS_WITNESS`, kstar = 6, four active true fault classes, max signature rank 2, collapse false. It is reproducibility-backed runtime evidence, not a second architecture or dataset. |
| `research_assets/runs/minimum-mr-subset-primary-rerun/burgers2d-pinn-witness/abd_witness_report.json` and `.../diffusion2d-pinn-witness/abd_witness_report.json` (+ kill matrices, MR/mutant catalogues, provenance) | observed | Minimum-MR-SubSet PINN primary reruns: trained Burgers2D and Diffusion2D PINN witnesses, both `PASS_WITNESS`, kstar = 1, five active true fault classes, max signature rank 2. This is second trained-SUT/PDE witness evidence, not a cross-SUT pass-rate estimate. |
| `research_assets/experiments/experiment-ledger.yml` (`precondition_check`) | observed | 2026-06-05 environmental check: required `METBENCH_MGN_*` vars unset; the three METBENCH-planned SUTs stay blocked. |
| `research_assets/rubric/domain_validity_rubric.json` | qualified | Design-time rubric coverage; not a proof and not runtime evidence. |
| Real Echowve SUT run | blocked | Missing dataset root, model repository, checkpoint, command, and outputs. |
| Real PhysicsNeMo SUT run | blocked | Missing dataset root, model repository, checkpoint, command, and outputs. |
| Third implementation SUT run | blocked | Missing dataset root, model repository, checkpoint, command, and outputs. |
| Baseline comparison | observed-secondary | LLM-simulated expert, one-shot LLM, and generic-MR scope contrasts are executed; use only as admissibility-gap contrasts, not superiority comparisons. |

## Claim Gate Table

| Claim | Status | Manuscript Use | Results Use |
|---|---|---|---|
| `C1-fixture-asset-path` | observed | May describe executable fixture-level asset path. | Cannot describe real SUT behavior. |
| `C2-real-sut-verdicts` | observed (pilot) | May describe the single-SUT/single-MR/single-case node-permutation pilot pass. | May appear in Results only as an explicitly scoped pilot; not as a rate, reliability, or general claim. |
| `C3-baseline-comparison` | observed-secondary | May describe the LLM-simulated expert, one-shot LLM, and generic-MR admissibility-gap contrasts. | May appear only as secondary scope contrasts, not as defeated competitors. |
| `C4-rubric-decision-coverage` | qualified | May describe design-time decision coverage with limitations. | Cannot substitute for runtime evidence. |
| `C5-precondition-check` | observed | May describe the 2026-06-05 fail-closed precondition gate. | Cannot describe any SUT verdict or unblocked run. |
| `C6-mirror-y-ood-stress` | observed | May describe the out-of-relation-domain decision and the bounded within-SUT frame-level OOD-stress rate (10/10 eval frames). | May appear in Results only as a scoped within-SUT, approximate-reflection frame rate; not as a geometry-independent/cross-SUT rate, reliability, or general failure claim. |
| `C7-conservation-diagnostic` | observed (pilot) | May describe the deferred absolute relation and the reference-relative conservation diagnostic pass. | May appear in Results only as a scoped reference-relative diagnostic; not as absolute conservation, a rate, or a reliability claim. |
| `C8-rollout-accuracy-baseline` | observed | May describe the same-SUT one-step rollout accuracy (median rel L2 0.0216) and that mirror-y is ~34x larger. | May appear in Results only as a same-SUT accuracy diagnostic; not as reliability, baseline superiority, multi-trajectory, or cross-SUT. |
| `C9-mirror-y-exact-symmetric-mesh` | observed | May describe the exact mirror-y fail (rel L2 1.10) on a provably symmetric, admissible mesh. | May appear in Results only as a one-input exact-equivariance test on a synthetic OOD mesh; not as accuracy, reliability, or cross-SUT. |
| `C10-seeded-fault-detection` | observed | May describe MR-as-detector results on the 10-mutant catalogue (union 5/10) and the by-class localization. | May appear in Results only as a bounded fault-detection result on one SUT/one catalogue; not a general or real-world fault-detection rate. |
| `C22-primary-empirical-scope-upgrade` | observed | May describe the K=6 x 3 trajectories x 10 mirror-y OOD-stress grid, K=6 x 3 trajectories x 9 conservation-transition grid, and K=6 x 3 exact-symmetric-mesh input grid. | May appear as the main primary MGN scope upgrade; not a cross-SUT, cross-dataset, reliability, accuracy, or broad-generalization claim. |
| `C21-primary-empirical-volume-upgrade` | observed | May describe the K=6 x 10 mirror-y OOD-stress grid, K=6 x 9 conservation-transition grid, and K=6 x 3 exact-symmetric-mesh input grid. | May appear only as a clustered primary MGN volume upgrade; not independent multi-trajectory estimates, cross-SUT rates, reliability claims, or absolute-conservation evidence. |
| `C16-unified-fault-catalog-statistics` | observed | May describe the 60-entry unified catalogue and its precision/recall/effect-size summaries. | May appear only as catalogue/statistical reporting; not as a real-world defect rate or validated localization model. |
| `C19-third-family-fno-roster` | observed-supporting | May describe the K=6 FNO training roster and its original admit/reject translation-boundary decision. | Use as supporting provenance for C23, not as the main FNO results row. |
| `C23-fno-primary-workflow-upgrade` | observed | May describe the full FNO primary workflow upgrade: 24/24 translation passes, 24/24 conservation failures under a periodic discrete-conservation MR, and 6/6 Dirichlet translation rejections. | May appear as trained FNO rubric-to-verdict evidence with raw source/follow-up outputs; not as cylinder-flow evidence, performance benchmarking, reliability, or broad neural-operator generalization. |
| `C20-minimum-mr-subset-external-scope-audit` | observed-secondary-audit | May cite the 70 real rows, 20 true-fault-class rows, and three relevant SciML/PDE `PASS_WITNESS` rows from the sibling repository. | External witness evidence only; does not add new primary SUT executions to this paper or support cross-SUT pass-rate claims. |
| `C24-minimum-mr-subset-primary-rerun` | observed | May describe the local rerun of the held-out cylinder-flow MGN witness: `PASS_WITNESS`, kstar = 6, four active true fault classes, max signature rank 2, collapse false. | Real runtime rerun evidence; not a second architecture or dataset, and not a cross-SUT or cross-dataset rate. |
| `C25-minimum-mr-subset-pinn-primary-reruns` | observed | May describe local reruns of the trained Burgers2D and Diffusion2D PINN witnesses: `PASS_WITNESS`, kstar = 1 each, five active true fault classes each, max signature rank 2. | Second trained-SUT/PDE witness evidence only; not a general PINN/PDE claim or cross-SUT pass-rate estimate. |
| General seeded-fault effectiveness | partially-observed | Bounded result in C10; general effectiveness is future-work. | Cannot be written as a general Results claim. |

## Methods-Ready Statements

- The study evaluates relation-level verdict coverage and evidence completeness.
- The current protocol records baselines as secondary scope contrasts rather than superiority outcomes.
- Missing real-SUT prerequisites fail closed and keep empirical claims blocked.
- The fail-closed precondition and artifact gates are enforced in code (`tools/validate_experiment_protocol.py:validate_experiment_ledger` and `validate_real_sut_preconditions`), not only described in prose.
- Fixture-level observations are limited to asset plumbing and transformation metrics.

## Single Real-SUT Pilot (scoped)

- One real trained MeshGraphNets cylinder-flow surrogate (read-only `Minimum-MR-SubSet`,
  PR #103, checkpoint sha256 `cf281f85...b04a9`) was executed on one eval-split source
  case (frame 0; 1923 nodes, 11070 edges) under the node permutation equivariance MR.
- The inverse-mapped follow-up output equalled the source output: relative L2 = 0.0
  (tolerance 1e-6), verdict pass. Raw outputs, manifest, and metric ledger are committed
  under `research_assets/runs/real-sut-node-permutation-pilot/`.
- This is pilot evidence for one SUT, one MR, one source case only.

## Mirror-y OOD-stress within-SUT frame rate (scoped, evidence-gated)

- On the real eval mesh the rubric classified the **exact** mirror-y relation as
  `out-of-relation-domain` from measured geometry: reflection about the channel
  centerline is non-bijective, the worst reflected-node mismatch (`1.93e-2`) is about
  one median mesh edge length (`1.88e-2`), node-type match is `0.977`, and the cylinder
  is off-centre by `-7.2 mm`. The relation was therefore downgraded to an approximate
  OOD-stress probe (`retained-ood-stress`).
- Under that probe (scored by the MR card formula: un-mirror the follow-up, normalise by
  the source norm), within the same SUT and checkpoint, the approximate mirror-y OOD-stress
  probe failed on **10 of 10 recorded eval frames** (0-9): median relative L2 `0.737`, each
  violation about `3-5.5x` the same-space mapping-error floor; 0 pass, 0 inconclusive, with
  every recorded frame kept in the denominator. Frame-level rate run under
  `research_assets/runs/mirror-y-rate-upgrade/`; the two-frame pilot and the geometry
  precondition report remain under `research_assets/runs/mirror-y-ood-stress-pilot/`.
- Evidence-gating takeaway: the method refuses to treat mirror-y as a clean MR where the
  geometry does not support it, yet the downgraded probe surfaces a large symmetry violation
  on every recorded eval frame of a genuinely trained, converged surrogate. This is a bounded
  within-SUT frame rate, not a geometry-independent or cross-SUT rate. The bounded within-SUT frame rate is reported only for this one SUT, one checkpoint, one MR, and one eval trajectory.

## Conservation Diagnostic Pilot (scoped, evidence-gated)

- A P1 discrete divergence operator gives a non-negligible divergence even for the
  ground-truth field on this coarse mesh (dimensionless reference divergence ≈ `0.037`,
  raw RMS ≈ `2.08`), so an absolute `div ≈ 0` tolerance is not calibratable. The absolute
  mass-conservation relation therefore stays **deferred** — the pilot is itself the
  evidence for that deferral.
- As a reference-relative diagnostic (flag a regression only if the surrogate's divergence
  exceeds the reference field's by > 50%), the surrogate's predicted next-state divergence
  stayed within ~0.4-0.8% of the reference on two eval frames (all-cell ratio `1.0025` /
  `1.0044`; interior-only ratio over 3183/3612 cells `1.0042` / `1.0075`, which rules out a
  boundary-imposition artefact): **pass** on both. Artifacts under
  `research_assets/runs/conservation-diagnostic-pilot/`.
- Evidence-gating takeaway: the rubric refuses an uncalibratable absolute tolerance instead
  of fabricating one, and the calibrated diagnostic shows the surrogate does not degrade
  conservation relative to the data.

## Primary Empirical Scope Upgrade (scoped, evidence-gated)

- The primary empirical scope upgrade reruns the weakest MGN denominators on the
  Minimum-MR-SubSet-derived K=6 checkpoint roster and the first three official
  DeepMind held-out test trajectories at commit
  `9ef862ec37335b4834d0a1fb38b4b613af702f34`.
- The `K=6 x 3 trajectories x 10 mirror-y OOD-stress grid` fails on 180/180
  checkpoint-trajectory-frame cells (descriptive cell-level Wilson 95% bound
  `[0.98, 1.00]`, not independent-trial inference; median relative L2 `0.828`,
  median V/floor `5.28`).
- The `K=6 x 3 trajectories x 9 conservation-transition grid` passes on 162/162
  checkpoint-trajectory-transition cells as a reference-relative diagnostic
  (max ratio `1.287`, max interior ratio `1.049`);
  the absolute mass-conservation relation remains deferred.
- The `K=6 x 3 exact-symmetric-mesh input grid` fails on 18/18 checkpoint-input cells
  (median relative L2 `1.097`) on synthetic no-obstacle admissible meshes.
- The trajectory-dependent cells are clustered by checkpoint, held-out test trajectory,
  and frame. This is not a single-source-trajectory estimate, but it remains one
  architecture family and one dataset, not a cross-SUT or cross-dataset rate.

## Statements Not Supported

- Any pass/fail or violation rate beyond the bounded primary MGN scope-upgrade grids;
  no model-reliability conclusion is supported.
- Absolute mass conservation (the divergence-free relation is deferred; only a reference-relative diagnostic was run).
- More than one SUT has been evaluated; mirror-y is asserted only as an approximate OOD-stress probe, not an exact relation for this mesh.
- The protocol improves accuracy or is superior to any baseline.
- General real-world seeded-fault effectiveness beyond the committed catalogues.

## Next Experiments

1. Extend beyond a single eval trajectory: a mirror-symmetric mesh (to test the exact mirror-y relation), additional trajectories/SUTs, and CIs before any cross-SUT or geometry-independent rate.
2. Record `METBENCH_MGN_DATA_ROOT`, `METBENCH_MGN_REPO`, and `METBENCH_MGN_CHECKPOINT` for the other planned SUTs.
3. Add the exact command, environment, and seed manifest before any run (now enforced by the manifest contract).
4. Preserve raw source and follow-up SUT outputs and a relation-level metric ledger (now enforced by the runner).
5. Update the claim ledger only after the corresponding artifacts exist and the artifact gate verifies them.
6. Repeat the same evidence bundle for each baseline before making superiority comparisons.
