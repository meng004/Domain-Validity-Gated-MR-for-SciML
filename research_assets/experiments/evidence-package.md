# Experiment Evidence Package

## Scope

This package defines an evidence-gated empirical protocol for physically grounded
metamorphic-relation testing of MeshGraphNets-family cylinder-flow surrogates. It is a
protocol and asset-readiness package plus three strictly-scoped real-SUT pilots (node
permutation, mirror-y OOD-stress, divergence/conservation diagnostic); it is not a full
Results package and reports no general reliability, accuracy, baseline, cross-SUT, or
geometry-independent rate outcome. The only rate-like result admitted here is the bounded
within-SUT mirror-y OOD-stress frame rate recorded by PR4.

## Evidence Inventory

| Artifact | Status | Evidence Limit |
|---|---|---|
| `research_assets/runs/node_permutation_fixture_verdict.json` | observed | Fixture-level asset plumbing only; SUT execution is `not-run`. |
| `research_assets/runs/real-sut-node-permutation-pilot/raw/metric_ledger.json` (+ raw `.npy` outputs, manifest) | observed | One-SUT/one-MR/one-case pilot: real MeshGraphNets cylinder-flow inference under node permutation; relative L2 = 0.0 (tol 1e-6), verdict pass. No rate or reliability claim. |
| `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json` (+ raw `.npy`, manifest; geometry in mirror-y-ood-stress-pilot) | observed | One-SUT/one-MR within-SUT frame rate: exact mirror-y is out-of-relation-domain on the real mesh; the approximate OOD-stress probe failed on 10/10 eval frames (0-9), median rel L2 0.737, ~3-5.5x the same-space mapping-error floor. Bounded within-SUT frame rate only; no reliability/accuracy/baseline/multi-SUT/geometry-independent claim. |
| `research_assets/runs/conservation-diagnostic-pilot/raw/{metric_ledger,conservation_report}.json` (+ raw `.npy`, manifest) | observed | One-SUT/one-MR/two-frame conservation diagnostic: absolute divergence-free relation stays deferred (reference divergence ~0.037 nondim, uncalibratable); reference-relative diagnostic passes (pred/reference divergence ratio 1.0025/1.0044). No absolute-conservation or rate claim. |
| `research_assets/experiments/experiment-ledger.yml` (`precondition_check`) | observed | 2026-06-05 environmental check: required `METBENCH_MGN_*` vars unset; the three METBENCH-planned SUTs stay blocked. |
| `research_assets/rubric/domain_validity_rubric.json` | qualified | Design-time rubric coverage; not a proof and not runtime evidence. |
| Real Echowve SUT run | blocked | Missing dataset root, model repository, checkpoint, command, and outputs. |
| Real PhysicsNeMo SUT run | blocked | Missing dataset root, model repository, checkpoint, command, and outputs. |
| Third implementation SUT run | blocked | Missing dataset root, model repository, checkpoint, command, and outputs. |
| Baseline comparison | blocked | Missing matched run artifacts and scoring ledgers. |

## Claim Gate Table

| Claim | Status | Manuscript Use | Results Use |
|---|---|---|---|
| `C1-fixture-asset-path` | observed | May describe executable fixture-level asset path. | Cannot describe real SUT behavior. |
| `C2-real-sut-verdicts` | observed (pilot) | May describe the single-SUT/single-MR/single-case node-permutation pilot pass. | May appear in Results only as an explicitly scoped pilot; not as a rate, reliability, or general claim. |
| `C3-baseline-comparison` | blocked | May describe baseline protocol commitments. | Cannot be written as Results. |
| `C4-rubric-decision-coverage` | qualified | May describe design-time decision coverage with limitations. | Cannot substitute for runtime evidence. |
| `C5-precondition-check` | observed | May describe the 2026-06-05 fail-closed precondition gate. | Cannot describe any SUT verdict or unblocked run. |
| `C6-mirror-y-ood-stress` | observed | May describe the out-of-relation-domain decision and the bounded within-SUT frame-level OOD-stress rate (10/10 eval frames). | May appear in Results only as a scoped within-SUT, approximate-reflection frame rate; not as a geometry-independent/cross-SUT rate, reliability, or general failure claim. |
| `C7-conservation-diagnostic` | observed (pilot) | May describe the deferred absolute relation and the reference-relative conservation diagnostic pass. | May appear in Results only as a scoped reference-relative diagnostic; not as absolute conservation, a rate, or a reliability claim. |
| Seeded-fault effectiveness | speculative | Future-work only. | Cannot be written as Results. |

## Methods-Ready Statements

- The study evaluates relation-level verdict coverage and evidence completeness.
- The current protocol records baselines as commitments rather than outcomes.
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

## Statements Not Supported

- Any pass/fail or violation rate beyond the bounded within-SUT mirror-y OOD-stress frame
  rate; no model-reliability conclusion is supported.
- Absolute mass conservation (the divergence-free relation is deferred; only a reference-relative diagnostic was run).
- More than one SUT has been evaluated; mirror-y is asserted only as an approximate OOD-stress probe, not an exact relation for this mesh.
- The protocol improves accuracy or is superior to any baseline.
- Seeded-fault detection effectiveness has been measured.

## Next Experiments

1. Extend beyond a single eval trajectory: a mirror-symmetric mesh (to test the exact mirror-y relation), additional trajectories/SUTs, and CIs before any cross-SUT or geometry-independent rate.
2. Record `METBENCH_MGN_DATA_ROOT`, `METBENCH_MGN_REPO`, and `METBENCH_MGN_CHECKPOINT` for the other planned SUTs.
3. Add the exact command, environment, and seed manifest before any run (now enforced by the manifest contract).
4. Preserve raw source and follow-up SUT outputs and a relation-level metric ledger (now enforced by the runner).
5. Update the claim ledger only after the corresponding artifacts exist and the artifact gate verifies them.
6. Repeat the same evidence bundle for each baseline before making any comparison.
