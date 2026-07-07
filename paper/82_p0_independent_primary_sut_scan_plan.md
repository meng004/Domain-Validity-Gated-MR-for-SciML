# P0 Independent Primary-Scale SUT Scan and Execution Plan

Date: 2026-07-03
Target venue pressure: JSS regular paper; increase empirical persuasion without
overstating external validity.

## Objective

Add at least one genuinely independent primary-scale SciML SUT/task and run the
complete rubric-to-verdict chain:

1. candidate relation screening;
2. MR-card asset;
3. trained SUT/checkpoint evidence;
4. source/follow-up executions;
5. metric ledgers;
6. typed relation verdicts;
7. claim-ledger and manuscript binding.

The added evidence must be recomputable from committed code and artifacts. It
must not reuse the cylinder-flow, airfoil, PINN, or FNO evidence as the new
primary task.

## Screening Criteria

| Criterion | Requirement | Rationale for JSS acceptance risk |
|---|---|---|
| Independence | Different governing task/PDE and SUT implementation from existing MGN, PointMLP, PhysicsNeMo airfoil, PINN, and FNO runs | Reduces the central reviewer objection that the paper is a one-task evidence package |
| Full chain | Includes admitted and rejected/downgraded candidate decisions, executable source/follow-up outputs, metric ledgers, and verdicts | JSS reviewers will not treat admissibility-only evidence as sufficient empirical validation |
| Recomputability | CPU-only, no external downloads, deterministic seeds, committed outputs | Avoids another blocked production-SUT prerequisite |
| Primary-scale denominator | Multiple trained SUT seeds/checkpoints and multiple evaluation cases per SUT | Gives meaningful denominator depth while avoiding false population inference |
| Claim discipline | Explicitly states what the new run cannot show | Prevents broad reliability, SOTA accuracy, or real-defect claims |

## Candidate Scan

| Candidate | Independence | MR fit | Practicality | Decision |
|---|---:|---:|---:|---|
| Additional PhysicsNeMo airfoil variants | Medium: same second CFD task already present | Strong node-permutation and conservation gates | GPU/data heavy; mostly deepens an existing task | Reject for P0 because it is not a genuinely new task |
| New Burgers/heat FNO or PINN seeds | Low: same PDE families already present | Strong translation/conservation relations | Easy but risks repackaging supporting evidence | Reject for P0 independence |
| External production SUT download | Potentially high | Unknown until installed | Network/GPU/license risk; cannot guarantee completion | Defer; not suitable for immediate P0 |
| 2D periodic scalar advection surrogate | High: new PDE/task, new lightweight SUT | Exact periodic translation and mass conservation; mirror candidate can be rejected under fixed velocity | CPU-only, deterministic, full raw-output chain feasible | Select |

## Selected P0 Task

Task: 2D scalar periodic advection on a 32 x 32 grid.

SUT family: deterministic NumPy-trained periodic convolution surrogate. Each
seed trains a local convolution kernel by ridge least squares to approximate one
periodic advection step, then saves a checkpoint.

Scale:

- K = 6 trained SUT seeds/checkpoints.
- n = 10 held-out evaluation fields per SUT.
- 60 source/follow-up relation cells per admitted MR.

Candidate relations:

1. Periodic integer-translation equivariance.
   - Gate decision: admitted.
   - Physical/software basis: the periodic advection operator and periodic
     convolution surrogate commute with integer grid translations.
   - Verdict metric: relative L2 between the source output and inverse-mapped
     follow-up output.
2. Global mass/mean conservation.
   - Gate decision: admitted with a measured numerical tolerance.
   - Physical basis: periodic advection preserves the spatial integral of a
     scalar field.
   - Verdict metric: absolute mean drift normalized by input RMS.
3. Mirror reflection under fixed advection velocity.
   - Gate decision: rejected as an exact MR.
   - Reason: reflecting the scalar field without transforming the velocity
     vector changes the boundary-value/transport problem.
   - Execution rule: not executed as an exact MR.

## Phase Loop

### Phase P0-A: Evidence Design

Prerequisites: current ledgers and manuscript scope read; no claim added before
an executable artifact exists.

Core steps: create scan plan; add MR cards for admitted relations; write runner
and tests that require full workflow flags and manuscript binding.

End condition: plan, cards, runner, and test exist; no empirical claim yet.

Review acceptance: every new relation has a gate decision and claim boundary.

Theme-drift check: keep the task as SciML surrogate V&V evidence, not a new
accuracy benchmark.

### Phase P0-B: Execution

Prerequisites: runner can train/checkpoint K=6 SUTs without external data.

Core steps: run the workflow; save checkpoints, raw source/follow-up outputs,
per-SUT metric ledgers, smoke manifest, and aggregate verdict report.

End condition: aggregate report contains K=6, n=10, full workflow flags, and
verdict counts for admitted and rejected relations.

Review acceptance: failures or surprising outcomes remain in the report; no
threshold is tuned after looking at results.

Theme-drift check: do not convert the run into a model-performance claim.

### Phase P0-C: Evidence Binding

Prerequisites: report exists and is reproducible by the runner.

Core steps: add claim-ledger and experiment-ledger entries; bind the new result
to manuscript/JSS text with explicit boundaries.

End condition: tests can find the evidence markers and ledgers cite real files.

Review acceptance: wording allowed is no broader than the report.

Theme-drift check: classify the run as independent primary-scale synthetic PDE
evidence, not production CFD or real-defect evidence.

### Phase P0-D: Verification

Prerequisites: all artifacts and manuscript bindings are written.

Core steps: run the new test, research-asset validator, experiment-protocol
validator, and full test suite as feasible.

End condition: verification output is recorded in the final status.

Review acceptance: any failure is investigated and either fixed or reported as a
remaining blocker with file path and reason.

Theme-drift check: final status reports evidence actually generated, not planned.

