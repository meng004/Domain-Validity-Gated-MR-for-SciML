# Provenance: PINN realistic-fault emergence test (claim C49)

Scope: **the companion of the FNO realistic-fault test (C48) on the pointwise PINN
architecture.** The same eight realistic mechanism-level faults (imported verbatim from the FNO
runner, not tailored per architecture) are measured against the PINN's two non-trivial admitted
MRs (MR-B mirror-y, MR-C conservation) at their predeclared C46 thresholds, on the K=6 Burgers
PINN roster evaluated on the committed FD reference grid. **Not** a real-world fault-detection
rate, reliability, baseline-superiority, a clean 1:1 by-class diagonal, or a proof that the
blind region is exhaustive or generalizes.

## Why this experiment

The same adversarial-review critique that motivated C48 applies to the constructed PINN
catalogue (C46): its by-class separation was *designed in* (an odd-in-y bias built to integrate
to zero, a cos(pi x) perturbation built to keep u_x even and preserve the x-integral). This
runner re-does it with real bugs whose MR response is **measured**, sharing one fault catalogue
with the FNO run so the faults are demonstrably not architecture-tailored.

## System under test and inputs (all committed; CPU-only, no credentials)

| Input | Path (committed in this repo) |
|---|---|
| Burgers PINN K=6 roster (converged) | `research_assets/runs/pinn-k6-roster/burgers_s{0..5}/sut/checkpoint.pt` |
| -- burgers seed 0 checkpoint | sha256 `6f37097e5e44…` |
| Shared FD reference grid (129x129, symmetric in y, 6 snapshots) | `research_assets/runs/pinn-cross-family/reference_solution.npz` (sha256 `5da3a0358b20…`) |
| Constructed C46 report (emergent-vs-constructed comparison) | `research_assets/runs/pinn-seeded-fault-detection/pinn_seeded_fault_report.json` |
| Shared fault catalogue (single source of truth) | `tools/run_realistic_fault_fno.py` (`apply_fault`, `REALISTIC_FAULTS`) |

The mirror-y map is an exact grid flip because the reference grid is symmetric in y (verified at
runtime; the runner aborts otherwise). The conserved quantity is the grid sum of u_x.

## Detectors and predeclared thresholds (reused verbatim from C46, none tuned)

- MR-B mirror-y equivariance: u_x even, u_y odd in y. A fault is detected when the median
  faulted mirror-y violation exceeds `MR_B_FACTOR = 3.0` times the clean violation (ratio form,
  robust to the PINN's imperfect clean equivariance).
- MR-C mass conservation: Q(t) = integral of u_x. A fault is detected when the median relative
  change in Q across the reference snapshots exceeds `MR_C_TOL = 0.10`.
- MR-A permutation equivariance is vacuous for a pointwise MLP and is **not** used as a detector.

Both constants are imported directly from `tools/run_seeded_fault_detection_pinn.py`.

## Fault catalogue

Identical to C48 (see `research_assets/runs/fno-realistic-fault/PROVENANCE.md`): boundary-band
mis-scale, global renorm, channel swap, region dropout, fixed zero-mean Gaussian noise (seed
20260620), mode truncation, spatial shift, sharpen. Each fault's measured
`output_perturbation_rel_l2` (median over snapshots) is recorded per SUT; amplitudes are the
shared fixed values and were **not** tuned per architecture or to graze any threshold.

## Environment configuration

CPU-only. Beyond the repo's verifiable tier (`numpy`, `PyYAML`):

```bash
pip install torch        # CPU torch is sufficient (no CUDA/MPS); committed run used torch 2.12.0+cpu
```

Determinism: the noise field uses a fixed seed, the reference grid is fixed, and the checkpoints
are loaded read-only, so reruns are byte-identical modulo the report timestamp.

## Operation steps

```bash
python tools/run_realistic_fault_pinn.py \
    --outdir research_assets/runs/pinn-realistic-fault
python tools/validate_research_assets.py
python -m pytest tests/test_pinn_realistic_fault.py -q
```

The runner writes `pinn_realistic_fault_report.json` here. The guard test reads that committed
report; it does not re-run the SUT.

## Pinned results (verification) — generated 2026-06-20

Per-fault measured perturbation (median over snapshots) and emergent by-class localization
across the 6 SUTs:

| fault | median rel-L2 | detection | by-class |
|---|---|---|---|
| `channel_swap` | 1.413 | 6/6 | both |
| `gaussian_noise` | 0.201 | 6/6 | mirror only |
| `global_renorm` | 0.200 | 6/6 | conservation only |
| `spatial_shift` | 0.626 (max 0.631) | 0/6 | none (structural blind, above band) |
| `region_dropout` | 0.022 | 0/6 | below realistic magnitude (untestable) |
| `sharpen` | 0.022 | 0/6 | below realistic magnitude (untestable) |
| `boundary_band_corrupt` | 0.003 | 0/6 | below realistic magnitude (untestable) |
| `mode_truncation` | 0.002 | 0/6 | below realistic magnitude (untestable) |

The three detected faults are detected 6/6 (Wilson 95% CI [0.61, 1.00]).

### §6 emergence questions (answered honestly)

1. **Does by-class emerge?** Yes. Of the four faults that reach a testable output magnitude on
   this smooth 129x129 field, three are detected and localize as a **2x2 partition** by (changes
   the conserved x-integral) x (breaks mirror-y symmetry): conservation-only = `{global_renorm}`,
   mirror-only = `{gaussian_noise}`, both = `{channel_swap}`. This is the same emergent structure
   as the FNO run, with the symmetry MR being mirror-y instead of translation.
2. **Are the old "blind" faults really blind at realistic magnitude?** `spatial_shift` reaches a
   large transport-error magnitude (rel-L2 up to 0.63, above the nominal band) and is detected by
   neither MR -- a roll keeps u_x even / u_y odd and preserves the x-integral, so it is
   structurally invisible to both MRs. The blind region is **real, not a construction artifact**.
   `sharpen` (0.022) and `mode_truncation` (0.002) stay below the realistic band on this smooth
   field, so output-space MR testing cannot probe them here.
3. **Honest verdict:** comparable-but-richer-and-messier than the constructed C46. By-class
   emerges as a 2x2 partition (not a clean diagonal) and the transport blind region is confirmed
   real; four faults fall below realistic output magnitude on this fine-grid smooth field and are
   reported as untestable rather than as misses.

Full claim wording is in `research_assets/experiments/claim-ledger.yml`
(`C49-pinn-realistic-fault-emergence`).
