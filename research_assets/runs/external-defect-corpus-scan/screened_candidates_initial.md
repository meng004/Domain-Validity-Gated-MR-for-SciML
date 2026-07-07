# Initial screened candidates for external defect-witness corpus

Date: 2026-07-03

Purpose: record the first R1 screening pass for the one-week JSS
Minor-Revision risk-reduction sprint. This file is a screening ledger, not a
claim ledger. No manuscript claim may cite a candidate here until its executable
witness, MR card, run report, experiment-ledger entry, and claim-ledger entry
exist.

Raw GitHub search and source artifacts are archived under:

- `research_assets/runs/external-defect-corpus-scan/raw/`

## Current go / near-go candidates

| ID | External source | Raw artifacts | MR / gate family | Screening status | Rationale | Main risk |
|---|---|---|---|---|---|---|
| EDC-01 | DeepXDE issue #26 / PR #27, PeriodicBC derivative-order support | `deepxde_issue_26.json`, `deepxde_pr_27.json`, `deepxde_pr_27_files.json` | Boundary-condition periodicity | go, already executed as seed | Public issue and merged PR; existing project witness already runs source/follow-up residuals and typed verdict. | Counts as one unit only; component-level, not trained-SUT defect corpus by itself. |
| EDC-02 | NeuralOperator issue #532 / PR #661, `spectrum_2d` L2 norm and power calculation | `neuraloperator_issue_532.json`, `neuraloperator_issue_532_comments.json`, `neuraloperator_pr_661.json`, `neuraloperator_pr_661_files.json` | Conservation/floor or spectral-metric numerical decidability | go | External issue comment confirms a bug; merged PR states the corrected L2-norm binning and squared-magnitude-before-sum behavior. A small tensor witness should be CPU-only. | Need avoid overclaiming: this is a diagnostic utility, not trained FNO reliability. |
| EDC-03 | NeuralOperator PR #702, Hermitian symmetry before IFFT in SpectralConv | `neuraloperator_pr_702.json`, `neuraloperator_pr_702_files.json`, `neuraloperator_pr_702_commits.json` | Frequency-domain symmetry / real-valued transform consistency | go | Merged PR explicitly enforces Hermitian symmetry to fix line artifacts. This matches a rare algebraic-structure witness. | Need verify whether a deterministic CPU witness can expose the pre/post semantic difference without GPU-specific cuFFT artifacts. |
| EDC-04 | PhiFlow issue #199 / PhiML commit `96ef3e4...`, custom-gradient transpose fix | `phiflow_issue_199.json`, `phiflow_issue_199_comments.json`, `phiml_commit_96ef3e4d8376502a1b75dcdd799d9ada1cb39f72.json` | Coordinate/component transform or differential-operator consistency | go if dependency-light witness works | Public issue reports flow-past-obstacle gradient failure; maintainer comment links fix to PhiML commit "Fix incorrectly transposed custom gradients." | May require installing PhiFlow/PhiML versions; if heavy or brittle, downgrade to defer. |
| EDC-05 | JAX-CFD PR #167, flux-boundary implementation fix | `jaxcfd_pr_167.json`, `jaxcfd_pr_167_files.json` | Boundary-condition consistency | go if JAX dependency path is tractable | Merged PR says advection flux boundary condition is now correctly inferred from velocity boundary conditions. This is SciML infrastructure and directly MR-relevant. | JAX version constraints may be brittle; witness should prefer small local semantic reconstruction if full package replay is blocked. |

## Defer candidates

| ID | External source | Raw artifacts | Reason for deferral |
|---|---|---|---|
| EDC-D1 | PyG issue #8131 / PR #8143, eigenvector permutation-invariance test fails on AMD CPU | `pyg_issue_8131.json`, `pyg_issue_8131_comments.json`, `pyg_pr_8143.json`, `pyg_pr_8143_files.json` | The phrase matches permutation invariance, but the issue appears to be hardware/tolerance-related test instability rather than a clear SciML metamorphic semantic defect. Use only if the main five fail and the fix reveals a clean semantic witness. |
| EDC-D2 | NeuralOperator issue #599, BatchNormalization for FNOBlocks | `neuraloperator_issue_599.json` | Clear bug, but mostly ordinary API/runtime failure. It is weaker for this paper than spectrum, Hermitian symmetry, boundary, or gradient-transform witnesses. |

## No-go / low-priority sources from this pass

- PhysicsNeMo boundary search mainly returned XAeroNet preprocessing/download
  issues (`github_search_physicsnemo_boundary_bug_closed.json`). These do not
  currently support a validity-gated MR witness.
- Narrow NeuralOperator padding/grid-transform searches returned no hits.
- JAX-CFD generic bug search did not add stronger candidates than PR #167.
- Many DeepXDE PeriodicBC hits are user questions, not external defect/fix
  units.

## Initial R1 judgement

The one-week sprint is feasible enough to proceed to R2.

Current strongest route:

1. Count EDC-01 as the already-completed seed unit.
2. Build CPU-only semantic witnesses for EDC-02, EDC-03, EDC-04, and EDC-05.
3. If EDC-03 or EDC-04 proves GPU/dependency-specific, replace it only with a
   candidate that has the same level of external source traceability.

Minimum paper-integration gate remains unchanged:

- At least 5 external defect/fix units.
- At least 3 repositories or independent subsystems.
- Every counted unit has candidate MR -> rubric -> MR card -> source/follow-up
  or before/after witness -> metric -> typed verdict -> claim ledger.
