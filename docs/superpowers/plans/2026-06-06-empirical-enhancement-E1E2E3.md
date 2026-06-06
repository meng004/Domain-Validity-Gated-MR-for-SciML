# Plan: Empirical Enhancement E1 + E2 + E3 (design for confirmation)

Date: 2026-06-06
Branch: claude/trusting-curie-i2VHM
Status: DESIGN — awaiting user confirmation before executing trainings.
Constraint: Minimum-MR-SubSet is READ-ONLY. Training reads its data/code but writes ALL
artifacts into this repo via --outdir / a local wrapper. Verified: timing probes wrote
nothing into the read-only repo.

Feasibility (measured): warm training is ~11 s / 100 steps, so a 1500-step checkpoint is
~2.5-4 min on CPU. K=6 SUTs => ~15-25 min total training. Time is not a constraint.

## Step 1 — SUT roster (determined)

All SUTs are MeshGraphNets cylinder-flow surrogates trained on the same single train
trajectory (1804 nodes, 150 frames) via the read-only train_stage_a.py protocol
(train_steps_max auto-caps at 149 pairs, lr 1e-3, 1500 steps). Honest scope: this is ONE
architecture family and ONE dataset; the roster varies training seed and model capacity,
not architecture family or data. It is cross-checkpoint / cross-configuration robustness,
NOT cross-SUT generality (echowve / PhysicsNeMo remain blocked: no artifacts).

| SUT | seed | hidden | layers | steps | how | role |
|-----|------|--------|--------|-------|-----|------|
| S0  | 0    | 64     | 4      | 1500  | existing vendored ckpt (sha256 cf281f85...) | anchor / published result |
| S1  | 1    | 64     | 4      | 1500  | CLI --seed 1 | seed replica |
| S2  | 2    | 64     | 4      | 1500  | CLI --seed 2 | seed replica |
| S3  | 3    | 64     | 4      | 1500  | CLI --seed 3 | seed replica |
| S4  | 0    | 128    | 4      | 1500  | local wrapper train(hidden=128) | capacity variant (wider) |
| S5  | 0    | 64     | 6      | 1500  | local wrapper train(num_layers=6) | depth variant (deeper) |

S0-S3 = 4 same-config models differing only by seed => isolates training-seed variance
(supports CIs). S0/S4/S5 = three capacities => cross-configuration robustness (descriptive,
n=3). Each new SUT records: config, seed, exact train command, checkpoint sha256, manifest.
Execution safety: train one at a time, commit+push each checkpoint immediately (~735 KB) to
survive periodic working-tree resets.

## Step 2 — Empirical design (E1, E2, E3)

### Research questions (new, additive to RQ0-RQ4)
- RQ-E1 (replication): Do the relation-level findings replicate across the 6 SUTs?
  Specifically (a) node-perm pass, (b) mirror-y violate, (c) conservation defer,
  (d) in-distribution accuracy << relation-violation, (e) seeded-fault detection profile.
- RQ-E2 (floor): Does the discrete-divergence operator's intrinsic error floor scale ~O(h)
  with mesh resolution, making the admissibility deferral operator-determined and a-priori
  characterizable (substantiating Contribution 1)?
- RQ-E3 (fault sensitivity): How stable is per-mutant detection across SUTs x input seeds,
  and how does detection vary with fault severity?

### E1 — multi-checkpoint replication
- IV: SUT (6 levels). For each SUT, run the SIX existing runners unchanged on the SAME
  inputs (eval trajectory + 10 frames; synthetic symmetric mesh; 10-mutant catalogue):
  run_real_sut_mr (node-perm), run_mirror_y_ood_stress, run_mirror_y_symmetric_mesh,
  run_conservation_diagnostic, run_rollout_accuracy, run_seeded_fault_detection.
- DVs per SUT: node-perm rel L2; mirror-y median rel L2 + median V/floor (10 frames);
  symmetric-mesh exact rel L2; conservation ratio + admissibility decision; rollout
  median + mean rel L2; seeded-fault union + per-MR detection set.
- Stats: across the 4 seed-replicas (S0-S3) report mean +/- 95% CI (bootstrap) per scalar;
  report the accuracy-vs-violation ratio distribution. Config variants (S0/S4/S5) reported
  descriptively (n=3). Non-replication, if any, reported verbatim (no seed cherry-picking).
- Headline target: "in-distribution accuracy << mirror-y relation-violation on all 6 SUTs"
  generalizes the core thesis from one checkpoint to a family.

### E2 — operator error-floor resolution sweep
- Build an analytic divergence-free reference field (stream-function u = (psi_y, -psi_x)) on
  symmetric structured meshes at resolutions h in {h0, h0/2, h0/4, h0/8}.
- Measure discrete-divergence RMS of the analytic solenoidal field => pure operator
  truncation error (true divergence is 0). Fit log-log slope; expect ~1 (O(h)); report
  slope + R^2.
- Show the admissibility decidability (tolerance vs floor) as a function of h.
- Claim: the floor is operator-determined and ~O(h) -> turns Contribution 1's
  "theoretically characterizable" from assertion into demonstration. Honest boundary: this
  validates the OPERATOR floor on a synthetic field; the real DeepMind-mesh 0.037 is a
  fixed-mesh measurement (that mesh cannot be refined), so the real-data decomposition
  stays a stated caveat. No training needed; reuse mesh builder + conservation_rubric.

### E3 — seeded-fault robustness + severity
- Across SUTs S0-S5 x input seeds {1..5}: per-(mutant, detector) detection indicator.
  Report per-mutant detection frequency + Wilson 95% CI; union rate + CI.
- Severity sweep on a gradeable fault: NS_scale in {1.1,1.25,1.5,2,4}x and partial vy-zero
  fraction in {0.25,0.5,0.75,1.0}; plot detection vs severity per detector.
- Claim: gross-fault detection stable; a measured sensitivity threshold bounds what these
  MRs catch (honest answer to the favorable-catalogue critique).

## Step 3 — Registration, threats, acceptance

Claim-ledger (authoritative) additions:
- C11-multicheckpoint-replication; C12-operator-floor-resolution; C13-fault-detection-robustness.
  Each with scope, wording_allowed/forbidden, evidence paths. Scope capped at "one
  architecture family, one dataset; cross-checkpoint/cross-configuration, not cross-SUT".

Threats to validity (pre-stated): one architecture family; one dataset/train trajectory
(seed-replicas are NOT independent of the data distribution); config variants n=3; E2
synthetic-field floor != real-data floor decomposition; one eval trajectory (10 frames),
temporally correlated.

Acceptance: every checkpoint reproducible (seed + sha256 + train command logged); every run
recorded in a metric ledger; validators exit 0; full unit-test suite green (with new marker
guards); PDF rebuilt clean; manuscript + main.tex updated with E1/E2/E3 results and the
external-validity scope correctly widened (one model -> K checkpoints, one family) and not
overclaimed.

## Honest expected outcome (for the submission decision)
Moves external validity one notch: single checkpoint -> 6 checkpoints of one family/dataset,
with CIs + a demonstrated O(h) floor + fault-detection CIs/severity curve. Expected IST
effect: Major(single-SUT) -> Major-toward-Minor. Does NOT reach true cross-SUT generality.
