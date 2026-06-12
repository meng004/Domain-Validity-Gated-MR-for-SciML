# abd-witness-burgers2d-pinn (run dir: burgers2d-pinn-witness)

status: PASS_WITNESS
label_scope: true_fault_class
sut: burgers2d_pinn

## Result

- Active true fault classes: 5 of 6.
- Max fault-class signature rank: 2.
- Exact kstar: 1.
- Collapse: True.
- Selected MRs: ['PINN_MR_INITIAL_REFERENCE'].
- Admitted (killed-by-something) mutants: 9 of 12.

## Submodule provenance

external/dvgmr @ 6ea488a (claude/trusting-curie-i2VHM, meng004/Domain-Validity-Gated-MR-for-SciML)
Checkpoint sha256 prefix: ff3eae5b40eb

## Honesty boundary

One PINN, one PDE (2D viscous Burgers, nu=0.05), one seed (20260607), one set of hyperparameters. Not a generalization across PINN architectures or PDEs.
