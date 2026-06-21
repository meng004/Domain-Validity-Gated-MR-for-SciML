# PROVENANCE — ext3-cross-sut-three-arm (claim C51)

## What this is
A **consolidation** of the per-SUT three-arm complementarity + validity-coverage
duality across the converged SUTs into one cross-SUT view (EXT-3, local part). It
runs **no new model** and introduces **no new numbers**: it reads committed
artifacts and tabulates them.

## How to reproduce
```bash
python tools/run_ext3_cross_sut_three_arm.py
# writes research_assets/runs/ext3-cross-sut-three-arm/raw/cross_sut_three_arm_report.json
```
CPU only, seconds, no GPU, no credentials. Deterministic (reads JSON + Wilson CIs).

## Inputs (committed artifacts, read-only)
| Source claim | File |
|---|---|
| C38 cylinder MeshGraphNets (MR vs accuracy) | `research_assets/runs/detection-vs-accuracy/raw/metric_ledger.json` |
| C42/C43 PointMLP (full three-arm) | `research_assets/runs/pointmlp-three-arm-complementarity/raw/metric_ledger.json` |
| C35/C36 converged airfoil (MR arm + duality) | `research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-seeded-fault-detection/raw/metric_ledger.json` |
| C47 cross-architecture duality (prior synthesis) | `research_assets/runs/cross-architecture-duality/cross_architecture_duality_report.json` |

## Output
`raw/cross_sut_three_arm_report.json` — per-SUT arm coverage, arm1/arm2/arm3
values where run, admissible MR set per SUT, the cross-SUT duality confirmations
(falsifiable), and the GPU-pending marker for the airfoil accuracy/generic arms.

## Boundary (C51)
- Consolidation over committed artifacts; **not** a new run.
- The airfoil **accuracy-monitor (arm2)** and **ungated-generic (arm3)** arms are
  **GPU-pending** (need the live PhysicsNeMo airfoil model); they are explicitly
  marked not-yet-run, never reported as complete.
- No superiority; the duality is a falsifiable cross-SUT prediction, not a law.
- GPU completion of the airfoil arms: see
  `docs/cloud_runbook/ext3_airfoil_three_arm_kickoff.md`.
