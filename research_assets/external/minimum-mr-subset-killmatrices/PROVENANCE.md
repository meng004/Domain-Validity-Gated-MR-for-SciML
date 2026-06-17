# Provenance: Minimum-MR-SubSet kill matrices (read-only reuse, claim C39)

These seven `kill_matrix.csv` files are copied **verbatim** from the read-only sibling
repository Minimum-MR-SubSet (`../最小完备MR子集`). They are kept here as committed
fixtures so the cross-program coverage analysis (`tools/run_cross_program_coverage.py`,
claim C39) is reproducible in this repository without the sibling present. **The sibling
is never modified; this is read-only reuse.**

| Fixture | Sibling run dir (`runs/…`) | Family | Domain |
|---|---|---|---|
| `s1-cylinder-mgn` | `abd-witness-cylinder-flow-mgn-runtime-20260605T021457Z` | neural surrogate | CFD incompressible (MeshGraphNet) |
| `s2-burgers2d-pinn` | `abd-witness-burgers2d-pinn-20260607T161215Z` | neural surrogate | 2D conservation law (PINN) |
| `s3-diffusion2d-pinn` | `abd-witness-diffusion2d-pinn-20260608T032704Z` | neural surrogate | 2D parabolic (PINN) |
| `c1-p2-wave` | `pseries-faultclass-p2_wave-20260611T074853Z` | classical solver | hyperbolic PDE (FDM) |
| `c2-p5-pke` | `pseries-faultclass-p5_pke-20260612T154001Z` | classical solver | stiff ODE / reactor kinetics |
| `c3-p7-burgers` | `pseries-faultclass-p7_burgers-20260612T154001Z` | classical solver | conservation law (FVM) |
| `r1-openmc` | `abd-p9-openmc-20260604T030626Z` | production code | Monte-Carlo neutron transport |

**Schema:** `sut, mutant_id, fault_class, mr_id, mr_meta_pattern, trial_id, killed,
residual, tolerance, seed, status`.

**Kill conventions vary across the corpus** (`killed` is `1`/`0` or `true`/`false`;
`status` is `OK` for the PINN runs but `killed`/`survived` for the others); the analysis
normalizes both. These are the **sibling's own MR suites and mutant catalogues** (e.g. the
cylinder fixture uses the sibling's 8-MR suite, not the paper's 3-MR pilot), reused only to
test whether the coverage-geometry reading generalizes across program types. The paper's
validity-gated pipeline was NOT executed end-to-end on each program.

Copied 2026-06-17.
