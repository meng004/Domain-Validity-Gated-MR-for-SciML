# Reproducibility

This package separates **what can be reproduced with no special hardware or
credentials** (the evidence the manuscript actually rests on, all bound to
committed artifacts) from **what requires a GPU and external data** (the
from-scratch SUT training/inference). Every paper claim is bound to a tracked
artifact under `research_assets/runs/` via
`research_assets/experiments/claim-ledger.yml`.

## System requirements

| Tier | Hardware | Credentials | Time |
|------|----------|-------------|------|
| 1 Smoke | CPU, Python 3.12 | none | ≤ 5 min |
| 2 Cache replay | CPU, Python 3.12 (+ a TeX dist for the PDF) | none | ≤ 30 min |
| 2c C40 cross-program | CPU + scipy (+ a source-built OpenMC for E5) | none | ≤ 30 min |
| 2d MVP cross-arch | CPU + CPU `torch` | none | ≤ 5 min |
| 2e EXT cross-arch + duality | CPU + CPU `torch` + scipy | none | ≤ 5 min |
| 3 Full re-run | CUDA GPU | `METBENCH_MGN_*`; gateway key for the review panel | hours |

## Environment setup

```bash
python -m venv .venv && source .venv/bin/activate   # Python 3.12 (tested on 3.12.7)
pip install -r requirements.txt                     # verifiable tier: numpy + PyYAML only
```

## Tier 1 — Smoke (≤ 5 min, no credentials): toolchain integrity

```bash
# Fail-closed asset validators + the compile-independent test subset CI runs:
python tools/validate_research_assets.py; echo $?      # expect: 0
python tools/validate_experiment_protocol.py; echo $?  # expect: 0
python -m unittest tests/test_research_assets.py tests/test_executable_mr_assets.py \
  tests/test_experiment_protocol.py tests/test_mirror_y_rubric.py \
  tests/test_conservation_rubric.py                    # expect: OK
```

The validators are fail-closed: they refuse to pass if any claim in the
manuscript is not backed by a committed artifact ledger.

The **full** regression suite (`python -m pytest tests -q`, 313 tests) additionally
includes one compile-gate check (`test_stage4_revision_readiness`) that reads the
gitignored `main.bbl`/`main.log`. On a fresh clone run the Tier-2 LaTeX compile
first to generate them; without it, that single test fails and the other 312 pass.
CI runs only the compile-independent subset above and is unaffected.

## Tier 2 — Cache replay (≤ 30 min, no credentials): paper numbers + PDF

```bash
# IST word count (single source of truth; counts refs + appendices + 200 w/float)
python tools/ist_wordcount.py

# A representative deterministic ledger regeneration (no GPU, no data download):
python tools/run_classical_operator_conservation.py
#   expect: baseline |dM|max ~2.2e-16 PASS; 3/3 operator-code faults detected

# Build the submission PDF (needs a TeX distribution, e.g. TeX Live / MacTeX):
cd paper/ist-submission
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
#   expect: 0 undefined references, 0 "Missing character", 0 "Overfull \hbox"
```

Every other number in the paper is read from a committed ledger under
`research_assets/runs/`; the regression suite in Tier 1 pins the prose to those
ledgers, so a green Tier 1 already certifies that the paper does not claim more
than the artifacts license.

## Tier 2c — C40 end-to-end cross-program pipeline (CPU; OpenMC E5 needs a source build)

This paper's validity-gated pipeline is executed end-to-end on five read-only
Minimum-MR-SubSet SUTs (claim C40). The four classical solvers are pure CPU (numpy + scipy);
the fifth (E5) runs the **real OpenMC Monte-Carlo k-eigenvalue solver** in multi-group mode.
Full provenance, including the nuclear-data choice, is in
`research_assets/runs/endtoend-pseries/PROVENANCE.md`.

```bash
MMRS=/home/user/Minimum-MR-SubSet                      # read-only sibling (clone if absent)

# Classical SUTs E1-E4 (parabolic / hyperbolic / stiff-ODE / conservation), no build:
pip install "scipy>=1.11"                              # numpy already in requirements.txt
PYTHONPATH="$MMRS/scripts:$MMRS" python3 tools/run_endtoend_pipeline_pseries.py \
    --suts p1_heat,p2_wave,p5_pke,p7_burgers

# E5 OpenMC (Monte-Carlo): build OpenMC from source first (no wheel/conda/Docker here).
# Multi-group mode -> NO continuous-energy nuclear-data download (~GB ENDF/B not needed):
bash tools/build_openmc_e5.sh                          # builds + installs + smoke-verifies
PYTHONPATH="$MMRS/scripts:$MMRS" LD_LIBRARY_PATH=/usr/local/lib \
    python3 tools/run_endtoend_pipeline_pseries.py     # default --suts includes p9_openmc
#   expect: 5 SUTs / 5 program types; gate 38 admit / 7 reject / 0 defer; E5 k_eff == k_inf
```

If `openmc` is not importable the runner records E5 as `not-executed-openmc-not-importable`
and the four classical SUTs still run; the committed five-SUT artifact was produced with a
from-source OpenMC 0.15.2. The guard `tests/test_endtoend_pipeline_pseries.py` pins the
committed result (it reads the ledgers, it does not re-run OpenMC).

## Tier 2d — MVP cross-architecture seeded-fault + three-arm (CPU + torch, no credentials)

The 1-region empirical-expansion MVP runs entirely on CPU on the committed, converged
PointMLP cylinder checkpoint (no GPU, no METBENCH, no sibling repo). The only dependency
beyond the verifiable tier is CPU `torch`. Per-run provenance (inputs, expected numbers) is
in each run directory's `PROVENANCE.md`.

```bash
pip install "scipy>=1.11" torch          # CPU torch; numpy already in requirements.txt

# MVP-A: cross-architecture seeded-fault detection (claim C41)
python tools/run_seeded_fault_detection_pointmlp.py \
    --out research_assets/runs/pointmlp-cylinder-seeded-fault-detection
#   expect: union 4/8 applicable; 2 mesh-adjacency mutants not-applicable (row-wise no-op)

# MVP-B/C: three-arm complementarity + gate value + knife-edge (claims C42, C43)
python tools/run_three_arm_complementarity_pointmlp.py \
    --out research_assets/runs/pointmlp-three-arm-complementarity
#   expect: MR 13/20, accuracy 6/20; 2x2 both=4/mr_only=9/acc_only=2/neither=5;
#           gate value: admitted-detector FP 0% vs 6/6 rejected templates 100%; knife-edge miss only at 1.0

python tools/validate_research_assets.py                                  # expect: 0
python -m pytest tests/test_seeded_fault_detection_pointmlp_cross_sut.py \
    tests/test_three_arm_complementarity.py -q                           # expect: OK
```

Both runners are deterministic (fixed seeds, read-only checkpoint); reruns are byte-identical
modulo the ledger timestamp. The committed ledgers were produced with CPU `torch 2.12.0+cpu`.

## Tier 2e — EXT operator-floor cross-topology, FNO/PINN seeded-fault, cross-arch duality (CPU, no credentials)

The local EXT layer runs entirely on CPU on committed, converged checkpoints and reports (no
GPU, no METBENCH, no sibling repo). Dependencies beyond the verifiable tier are CPU `torch`
(FNO/PINN) and `scipy` (EXT-2 Delaunay); EXT-3 is pure standard library. Per-run provenance
(inputs, expected numbers) is in each run directory's `PROVENANCE.md`.

```bash
pip install "scipy>=1.11" torch          # CPU torch; numpy already in requirements.txt

# EXT-2: operator-floor on a second unstructured Delaunay topology (claim C44)
python tools/run_operator_floor_sweep_mesh2.py \
    --outdir research_assets/runs/operator-floor-sweep-mesh2
#   expect: slope 0.983 (95% CI [0.953, 1.014]); floor ratio 1.06 median / 1.33 max; topology-stable

# B-FNO: FNO end-to-end seeded-fault, by-class + blind (claim C45)
python tools/run_seeded_fault_detection_fno.py \
    --outdir research_assets/runs/fno-seeded-fault-detection
#   expect: scale/offset -> conservation 24/24; asym -> translation; both; transport-shift blind 0/24

# B-PINN: PINN end-to-end seeded-fault, by-class + blind (claim C46)
python tools/run_seeded_fault_detection_pinn.py \
    --outdir research_assets/runs/pinn-seeded-fault-detection
#   expect: scale -> conservation 6/6; odd-y -> mirror 6/6; both; cos(pi x) blind 0/6

# EXT-3: cross-architecture duality synthesis over the four reports (claim C47)
python tools/run_cross_architecture_duality.py \
    --outdir research_assets/runs/cross-architecture-duality
#   expect: duality holds 4/4 (P1 coverage partitioned by admitted MR + P2 structural blind region)

python tools/validate_research_assets.py                                  # expect: 0
python -m pytest tests/test_ext2_operator_floor_cross_topology.py \
    tests/test_fno_seeded_fault_detection.py \
    tests/test_pinn_seeded_fault_detection.py \
    tests/test_cross_architecture_duality.py -q                          # expect: OK
```

All four runners are deterministic (fixed seeds / read-only inputs); reruns are byte-identical
modulo the report timestamp. EXT-3 needs no dependency beyond the Python standard library.

## Tier 3 — Full re-run (hours, GPU + credentials)

Real SUT runs require a CUDA GPU and the `METBENCH_MGN_*` environment variables;
absent those, the precondition gate fails closed **by design** (this is intended
behavior, not an error). Datasets (~1–2 GB DeepMind cylinder-flow / airfoil
TFRecords) are auto-staged by the workflow runners. The review panel
(`tools/run_academic_review_panel.py`) additionally needs `OPENAI_API_KEY` and
`OPENAI_BASE_URL` for an OpenAI-compatible gateway. Provide credentials via the
environment only; never commit them.

## Container (Tier 1, reproducible toolchain)

```bash
docker build -t dvg-mr-sciml .
docker run --rm dvg-mr-sciml      # runs the compile-independent CI checks (validators + unittest subset)
```

## Archival

On acceptance the full repository is deposited to Zenodo for a persistent DOI.
After the deposit, fill the `doi:` field in `CITATION.cff` and the placeholder in
the manuscript's Data-availability statement.
