# Experiment Evidence Package

## Scope

This package defines an evidence-gated empirical protocol for physically grounded
metamorphic-relation testing of MeshGraphNets-family cylinder-flow surrogates.
It is a protocol and asset-readiness package, not a Results package.

## Evidence Inventory

| Artifact | Status | Evidence Limit |
|---|---|---|
| `research_assets/runs/node_permutation_fixture_verdict.json` | observed | Fixture-level asset plumbing only; SUT execution is `not-run`. |
| `research_assets/rubric/domain_validity_rubric.json` | qualified | Design-time rubric coverage; not a proof and not runtime evidence. |
| Real Echowve SUT run | blocked | Missing dataset root, model repository, checkpoint, command, and outputs. |
| Real PhysicsNeMo SUT run | blocked | Missing dataset root, model repository, checkpoint, command, and outputs. |
| Third implementation SUT run | blocked | Missing dataset root, model repository, checkpoint, command, and outputs. |
| Baseline comparison | blocked | Missing matched run artifacts and scoring ledgers. |

## Claim Gate Table

| Claim | Status | Manuscript Use | Results Use |
|---|---|---|---|
| `C1-fixture-asset-path` | observed | May describe executable fixture-level asset path. | Cannot describe real SUT behavior. |
| `C2-real-sut-verdicts` | blocked | May describe planned evidence gate. | Cannot be written as Results. |
| `C3-baseline-comparison` | blocked | May describe baseline protocol commitments. | Cannot be written as Results. |
| `C4-rubric-decision-coverage` | qualified | May describe design-time decision coverage with limitations. | Cannot substitute for runtime evidence. |
| Seeded-fault effectiveness | speculative | Future-work only. | Cannot be written as Results. |

## Methods-Ready Statements

- The study evaluates relation-level verdict coverage and evidence completeness.
- The current protocol records baselines as commitments rather than outcomes.
- Missing real-SUT prerequisites fail closed and keep empirical claims blocked.
- Fixture-level observations are limited to asset plumbing and transformation metrics.

## Statements Not Supported

- Real MeshGraphNets inference has been executed.
- The SUT satisfies, violates, or is reliable under any MR.
- The protocol improves accuracy or is superior to any baseline.
- Seeded-fault detection effectiveness has been measured.

## Next Experiments

1. Record `METBENCH_MGN_DATA_ROOT`, `METBENCH_MGN_REPO`, and `METBENCH_MGN_CHECKPOINT` for one real SUT.
2. Add the exact command, environment, and seed manifest before any run.
3. Preserve raw source and follow-up SUT outputs.
4. Generate a relation-level metric ledger from the raw outputs.
5. Update the claim ledger only after the corresponding artifacts exist.
6. Repeat the same evidence bundle for each baseline before making any comparison.
