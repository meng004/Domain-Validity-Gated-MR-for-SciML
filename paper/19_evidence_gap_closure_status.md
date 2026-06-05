# Evidence Gap Closure Status

## What is now supported

The asset package now supports explicit design-time classification for four MR-candidate outcomes through `research_assets/rubric/domain_validity_rubric.json` and `research_assets/ledgers/candidate_ledger.json`.

- `mgn-node-permutation-equivariance` is retained as `retained-design-time` because its graph reindexing, inverse output mapping, metric, tolerance, and evidence limits are specified.
- `mgn-mirror-y-equivariance` is retained as `retained-ood-stress` because its y-reflection and velocity-component mapping are meaningful only under mirror-compatible geometry, boundary labels, and component conventions.
- `mgn-discrete-divergence-boundedness` is marked `deferred` because the discrete divergence operator, boundary treatment, and tolerance calibration are not yet fixed.
- `cand-viscous-time-reversal` is marked `rejected-design-time` because local physics notes exclude time reversal for viscous cylinder flow.

These are rubric-backed expert judgments with local evidence references. They are not automatic proofs and are not empirical SUT results.

## What remains blocked

Real MeshGraphNets SUT execution remains blocked unless dataset, model repository, and checkpoint paths are supplied, including `METBENCH_MGN_DATA_ROOT`, `METBENCH_MGN_REPO`, and `METBENCH_MGN_CHECKPOINT`.

The current package still does not support empirical pass/fail rates, violation rates, model-reliability conclusions, seeded-fault detection claims, or comparative SUT performance claims. Divergence/conservation also remains blocked as a retained MR until the operator, boundary treatment, and tolerance evidence are made explicit.

## How the rubric changed decisions

The rubric turns candidate handling into an auditable decision ledger rather than a flat list of plausible relations. It separates ordinary design-time retention, conditional OOD-stress retention, deferred candidates, diagnostic downgrades, and design-time rejection.

This changes the interpretation of the candidate set in three ways. First, node permutation can be kept as a representation-level asset without pretending it has real SUT evidence. Second, mirror-y can be preserved as a useful stress candidate while making its domain preconditions visible. Third, time reversal is no longer an ambiguous temporal relation: for viscous cylinder flow it is explicitly rejected at design time, with the rejection itself serving as evidence that the validity rubric filters physically invalid candidates.

## Manuscript claim boundary

The manuscript may claim that the work now has an explicit rubric and candidate ledger that record evidence-bounded MR decisions for the cylinder-flow MeshGraphNets case study. It may also claim that the current assets distinguish retained, OOD-stress, deferred, and rejected candidates before runtime execution.

The manuscript must not claim that MeshGraphNets inference has been run, that any SUT passed or failed these MRs, that divergence has a calibrated retained-MR threshold, or that time reversal failed empirically. The honest boundary is design-time evidence management plus fixture-level asset plumbing from earlier tasks, with real SUT results still blocked.
