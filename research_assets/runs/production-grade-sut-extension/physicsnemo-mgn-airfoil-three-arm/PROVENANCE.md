# PROVENANCE — physicsnemo-mgn-airfoil-three-arm (claim C52)

## What this is
The **airfoil row completion** of the EXT-3 cross-SUT three-arm table: the two arms
that need the **live converged PhysicsNeMo airfoil model** (GPU), added to the
already-committed MR arm (arm1, C36). A real model run, not a consolidation.

- **arm2 accuracy-monitor** — deployed one-step state rollout (predicted next
  velocity vs ground-truth next velocity); a fault is detected when its rollout
  reaches 2x the fault-free baseline (`ACCURACY_ROLLOUT_MULT=2.0`, same multiplier
  as the PointMLP three-arm, C42/C43).
- **arm3 ungated-generic gate value** — five generic MT templates treated as
  claimed exact invariants; the metric is each template's baseline false-positive
  rate on the fault-free SUT (does it flag the correct model?).
- arm1 (node-permutation + compressible conservation) is recomputed over the same
  frames so the 2x2 MR-vs-accuracy table is internally coherent (mirror-y is
  inadmissible on the airfoil — non-zero angle of attack — and is not run as a detector).

## How to reproduce
```bash
# WSL2 + CUDA, EXT-1 environment (~/ext1-venv); see docs/cloud_runbook/ext3_airfoil_three_arm_kickoff.md
source ~/ext1-venv/bin/activate
python tools/run_airfoil_three_arm.py
# writes research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-three-arm/raw/metric_ledger.json
```
Deterministic (fixed seeds for permutation / generic templates). ~5 min on an RTX 3090.

## Inputs (committed, read-only)
| What | File |
|---|---|
| converged airfoil checkpoint (C35 roster) | `research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster/checkpoint_k01_seed20260616.pt` |
| SUT infra (model build, graph, predict) | `tools/run_physicsnemo_mgn_airfoil_workflow.py` |
| fault catalogue + mutation ops (arm1 template) | `tools/run_seeded_fault_detection_physicsnemo_airfoil.py` |
| arm2/arm3 reference recipe | `tools/run_three_arm_complementarity_pointmlp.py` |

## Result (honest, as-run)
- **arm1 MR**: 1/10 — only `NS_skip_denorm` (reproduces C36's robust detection).
- **arm2 accuracy-monitor**: 2/10 — `BC_zero_outflow` and `BC_nonzero_wall`, the two
  boundary-condition faults that grossly corrupt the deployed state (~150-310x baseline).
- **2x2 complementarity**: both=0, mr_only=1, accuracy_only=2, neither=7 — MR and
  accuracy catch **disjoint** fault subsets.
- **arm3 gate value**: gate-admitted node-permutation false-positive **0**; all four
  gate-rejected templates (mirror-y, scaling, channel-swap, additive) false-positive
  **1.0**. mirror-y is the duality-critical rejected template the gate removes.

## Boundary (C52)
- The airfoil is a **deliberately low-fidelity** surrogate. arm2's deployed-state
  rollout baseline (~7e-4) is small because the compressible flow is near-stationary
  per step — this is a **different quantity** from C35's reported delta-prediction
  rollout of 0.92; no contradiction. The accuracy monitor therefore catches only
  gross deployed-state corruption.
- Detection counts are for this 10-mutant catalogue only — **not** a real-world
  rate, reliability, strong-detection, or any baseline-superiority claim.
- One checkpoint, 5 trajectories x 9 frames, two admissible detectors.
