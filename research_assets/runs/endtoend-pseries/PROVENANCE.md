# Provenance: end-to-end cross-program pipeline (claim C40)

Scope: **this paper's validity-gated pipeline (four-condition admissibility rubric -> typed
two-dimensional verdict -> per-SUT coverage map) executed end-to-end on five CPU-only SUTs
imported read-only from the Minimum-MR-SubSet sibling.** The MRs and seeded mutants are the
sibling's domain assets; only the gate + typed-verdict framework is newly executed. Detection
counts are for the sibling's committed mutant sets only. **Not** a per-program reliability or
real-world detection rate, **not** a baseline-superiority claim, and the MRs are **not** new
contributions of this paper. Unlike C39 (read-only kill-matrix reuse), C40 runs the pipeline.

## System under test (read-only source)

Sibling `meng004/Minimum-MR-SubSet`, commit `726c0314e014fb4286346cf500680fd57a0f2326`
(local read-only checkout `/home/user/Minimum-MR-SubSet`). The sibling is never modified;
the runner only adds it to `sys.path` for import. All writes land in this directory.

| Tag | SUT (sibling) | Program type | Numerical method | Interface |
|---|---|---|---|---|
| E1 | `experiments/puts/p1_heat` | parabolic PDE | classical FDM | `mcmr.pseries` observables |
| E2 | `experiments/puts/p2_wave` | hyperbolic PDE | classical FDM | `mcmr.pseries` observables |
| E3 | `experiments/puts/p5_pke` | stiff ODE | LSODA (scipy) | `mcmr.pseries` observables |
| E4 | `experiments/puts/p7_burgers` | nonlinear conservation law | classical FVM | `mcmr.pseries` observables |
| E5 | `scripts/mcmr/openmc_put` headline PUT | Monte-Carlo transport | **real OpenMC** k-eigenvalue (multi-group) | `run_kinf_openmc` k-oracle |

## Operation steps

E1–E4 are pure CPU (numpy + scipy), no special build:

```bash
MMRS=/home/user/Minimum-MR-SubSet
PYTHONPATH="$MMRS/scripts:$MMRS" python3 tools/run_endtoend_pipeline_pseries.py \
    --suts p1_heat,p2_wave,p5_pke,p7_burgers
```

E5 additionally needs a runnable OpenMC (see "OpenMC environment" below). Once built:

```bash
MMRS=/home/user/Minimum-MR-SubSet
PYTHONPATH="$MMRS/scripts:$MMRS" LD_LIBRARY_PATH=/usr/local/lib \
    python3 tools/run_endtoend_pipeline_pseries.py     # default --suts now includes p9_openmc
```

The runner writes `e1/`–`e5/metric_ledger.json` plus the aggregate `metric_ledger.json` here.
If `openmc` is not importable, E5 is skipped and recorded as `not-executed-openmc-not-importable`
(the four classical SUTs still run); the run does not fail.

## OpenMC environment configuration (E5)

`openmc` has **no pip wheel/sdist** on this environment's index, **no conda** is present, and
**no Docker daemon** is running, so OpenMC is **built from source**. The reproducible recipe is
`tools/build_openmc_e5.sh`; the steps it automates:

- **Version:** tag `v0.15.2` (the Python-3.11-compatible release; `main` requires `>=3.12`).
- **Build deps (apt):** `libhdf5-dev` (serial), `libpng-dev`, `cmake`, `g++`; the vendored
  `fmt` / `pugixml` / `xtensor` / `xtl` submodules are fetched with the clone.
- **C++ core:** `cmake -DCMAKE_BUILD_TYPE=Release -DHDF5_PREFER_PARALLEL=OFF`, `make`,
  `make install` to `/usr/local` (gives `/usr/local/bin/openmc` + `libopenmc.so`), `ldconfig`.
- **Python API:** `pip install <src>` with **build isolation** (the Debian system setuptools
  lacks the patched `install_layout`, so `--no-build-isolation` fails; the isolated build
  pulls a clean setuptools and succeeds). Installs `openmc 0.15.2`.
- **OpenMC run settings (per oracle call):** `particles=2000, batches=30, inactive=10,
  seed=1`; draws `sample_param_draws(3, 20260531)`. Deterministic: reruns are byte-identical
  (modulo the ledger timestamp).

## Nuclear data (E5): multi-group, no continuous-energy download

The sibling's MR-bearing OpenMC subject is the **1-group infinite-medium "headline" PUT**:
its MRs are cross-section-algebra relations on macroscopic multi-group cross-sections
(`sigma_f, nu, sigma_c, sigma_s`) and its mutants are MGXS-assembly bugs, so the subject is
**multi-group by construction**. The oracle (`mcmr.openmc_put.headline_openmc.run_kinf_openmc`)
builds a **self-generated 1-group MGXS library in code** and runs OpenMC in `energy_mode =
"multi-group"`. Therefore **no continuous-energy nuclear data (ENDF/B, ~GB) is downloaded or
required**, and `OPENMC_CROSS_SECTIONS` is unused.

This is still the **real OpenMC Monte-Carlo transport solver** (compiled C++ core, particle
tracking, k-eigenvalue power iteration); only the cross-section representation is multi-group.
The continuous-energy PWR pin-cell adapter (`experiments/puts/p9_openmc.py`) that *would* need
ENDF/B is a separate single-`k_eff` criticality calculation with **no MR/mutant infrastructure**,
so it cannot exercise this pipeline; it is deliberately not used here. **Verification:** the
1-group infinite medium has the closed-form `k_inf = nu*sigma_f/(sigma_c+sigma_f)`; OpenMC
reproduces it exactly at the reference point (`k_eff = 1.20000 = k_inf`), so this is a real
verification against ground truth, not merely "it ran".

## Pinned results (for verification; pinned by tests/test_endtoend_pipeline_pseries.py)

| Tag | Program type | gate admit/reject/defer | full-set mutation score | structural blind spots |
|---|---|---|---|---|
| E1 p1_heat | parabolic PDE | 9 / 0 / 0 | 0.75 | M3_no_bc, M7_dx_offbyone, M13_bc_left_only |
| E2 p2_wave | hyperbolic PDE | 7 / 2 / 0 | 0.20 | 14 escaped (energy/CFL/IC/stencil classes) |
| E3 p5_pke | stiff ODE | 7 / 3 / 0 | 0.20 | PK1_rho_sign, PK3_lambda_sign, PK4_swap |
| E4 p7_burgers | conservation law | 10 / 0 / 0 | 0.20 | BU1_flux_linear, BU2_roll_sign, BU4_cfl_x2 |
| E5 openmc_headline_mg | Monte-Carlo transport | 5 / 2 / 0 | 0.5556 | M01_abs_minus, M02_abs_drop_f, M09_fission_x2 |

Aggregate: 5 SUTs, 5 program types; the gate makes non-trivial program-specific decisions
(38 admitted / 7 rejected total; every rejection is a one-sided monotonicity MR that the
output-mapping / construct-validity probe does not falsify; 0 deferred); structural blind spots
in all 5 programs (declared equivalent mutants — e.g. `M07_scatter_x2` for OpenMC — set aside);
the operator-class-to-fault-coverage mapping is program-specific. The full claim wording is in
`research_assets/experiments/claim-ledger.yml` (`C40-endtoend-cross-program-pipeline`).

Generated on a from-source OpenMC 0.15.2 build, 2026-06-17.
