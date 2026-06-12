# abd-witness-diffusion2d-pinn (run dir: diffusion2d-pinn-witness)

status: PASS_WITNESS
label_scope: true_fault_class
sut: diffusion2d_pinn

## Result

- Active true fault classes: 5 of 6.
- Max fault-class signature rank: 2.
- Exact kstar: 1.
- Collapse: True.
- Selected MRs: ['DIFFUSION_PINN_MR_SNAPSHOT_REFERENCE'].
- Admitted (killed-by-something) mutants: 10 of 12.

## Submodule provenance

external/dvgmr @ 0912fef (claude/trusting-curie-i2VHM, meng004/Domain-Validity-Gated-MR-for-SciML)
Checkpoint sha256 prefix: b54a6b529aa0

## Honesty boundary

One PINN, one PDE (2D heat, alpha=0.1, Neumann zero-flux), one seed (20260607), one set of hyperparameters. Not a generalization across PINN architectures or PDEs.
