# Provenance: FNO realistic-fault emergence test (claim C48)

Scope: **the same two admitted FNO MRs and the same predeclared thresholds as the constructed
C45 experiment, re-run against eight REALISTIC mechanism-level surrogate bugs that are NOT
tailored to the invariants, to test whether the by-class detection structure is emergent or
merely constructed.** K=6 trained FNO-2D checkpoints (Burgers/heat x seeds 0,1,2), 4 eval
cases each (24 cells per fault; 12 for the Burgers-only channel swap). **Not** a real-world
fault-detection rate, reliability, baseline-superiority, a clean 1:1 by-class diagonal, or a
proof that the blind region is exhaustive or generalizes.

## Why this experiment

An adversarial review found that the constructed FNO catalogue (C45) had its by-class
separation *designed in*: each fault was an analytic transform built to live in (or out of) a
specific MR's null space, so "which MR catches which fault" was fixed by the fault's analytic
symmetry, not discovered. This runner re-does it with real bugs whose MR response is
**measured**, with the detector thresholds and the fault amplitudes both fixed in advance.

## System under test and inputs (all committed; CPU-only, no credentials)

| Input | Path (committed in this repo) |
|---|---|
| FNO K=6 roster checkpoints (converged) | `research_assets/runs/fno-k6-roster/{burgers,heat}_s{0,1,2}/sut/checkpoint.pt` |
| -- Burgers seed 0 checkpoint | sha256 `3221c8cc5618…` |
| -- heat seed 0 checkpoint | sha256 `9a9ebfaeb249…` |
| Constructed C45 report (for the emergent-vs-constructed comparison) | `research_assets/runs/fno-seeded-fault-detection/fno_seeded_fault_report.json` |

Eval inputs are regenerated deterministically by `gen_fd_dataset_2d.make_dataset` (periodic FD
Burgers/heat, seed `1000 + roster_seed`), matching the C45 protocol. The read-only
Minimum-MR-SubSet sibling is **not** needed.

## Detectors and predeclared thresholds (reused verbatim from C45, none tuned)

- Periodic integer-translation MR: clean model passes (`TRANSLATION_TOL = 1e-5`); a fault is
  detected when the translation-mapped follow-up crosses that tolerance while the clean model
  does not.
- Periodic channel-sum (mass) MR: a fault is detected when it changes the per-channel spatial
  sum by more than `CONSERVATION_BREAK_TOL = 0.05` (5%) of the clean output.

Both constants are imported directly from `tools/run_seeded_fault_detection_fno.py`; the
realistic runner cannot change them.

## Fault catalogue (8 realistic bugs, NOT tailored to the MRs; amplitudes fixed in the runner)

| key | mechanism | output-level implementation |
|---|---|---|
| `boundary_band_corrupt` | boundary-handling error | outer 1-cell band x 0.4 |
| `global_renorm` | de-normalization / calibration error | whole field x 1.2 |
| `channel_swap` | channel-index error (Burgers only) | swap u_x <-> u_y |
| `region_dropout` | masked / failed sub-region | zero a `H//4 x W//4` corner patch |
| `gaussian_noise` | numerical instability | + 0.20 * RMS fixed zero-mean noise (seed 20260620) |
| `mode_truncation` | spectral over-smoothing | FFT, zero the upper half of modes, inverse |
| `spatial_shift` | transport / phase error | spatial roll by `W//6` |
| `sharpen` | over-regularization / high-pass | field + 8.0 * (field - box-blur(field)) |

Each fault's measured `output_perturbation_rel_l2` is recorded per case; amplitudes were set
to a realistic damage level (target rel-L2 0.10-0.30 where the field permits) and were **not**
tuned to graze any detector threshold.

## Environment configuration

CPU-only. Beyond the repo's verifiable tier (`numpy`, `PyYAML`):

```bash
pip install torch        # CPU torch is sufficient (no CUDA/MPS); committed run used torch 2.12.0+cpu
```

Determinism: the noise field uses a fixed seed (`numpy.random.default_rng(20260620)`), datasets
are regenerated from fixed seeds, and the checkpoints are loaded read-only, so reruns are
byte-identical modulo the report timestamp.

## Operation steps

```bash
python tools/run_realistic_fault_fno.py \
    --outdir research_assets/runs/fno-realistic-fault
python tools/validate_research_assets.py
python -m pytest tests/test_fno_realistic_fault.py -q
```

The runner writes `fno_realistic_fault_report.json` here. The guard test reads that committed
report; it does not re-run the SUT.

## Pinned results (verification) — generated 2026-06-20

Per-fault measured perturbation and emergent by-class localization:

| fault | median rel-L2 | detection | by-class |
|---|---|---|---|
| `boundary_band_corrupt` | 0.299 | 24/24 | both |
| `region_dropout` | 0.249 | 24/24 | both |
| `gaussian_noise` | 0.201 | 24/24 | translation only |
| `global_renorm` | 0.200 | 24/24 | conservation only |
| `channel_swap` (Burgers) | 1.125 | 8/12 | conservation only |
| `spatial_shift` | 0.005 (max 0.194) | 0/24 | none (structural blind) |
| `sharpen` | 0.006 (max 0.204) | 0/24 | none (structural blind) |
| `mode_truncation` | 0.000 (max 0.001) | 0/24 | none (sub-band) |

The in-band faults are detected 24/24 (Wilson 95% CI [0.86, 1.00]).

### §6 emergence questions (answered honestly)

1. **Does by-class emerge?** Yes, but as a **2x2 partition**, not a clean 1:1 diagonal. The
   five detected faults localize by the two binary properties the MRs actually probe -- (changes
   the channel integral?) x (breaks translation equivariance?): conservation-only =
   `{global_renorm, channel_swap}`, translation-only = `{gaussian_noise}`, both =
   `{boundary_band_corrupt, region_dropout}`. The partition is read off the measurements, with
   faults that are not designed around the MR null spaces.
2. **Are the old "blind" faults really blind at realistic magnitude?** Yes where reachable.
   `spatial_shift`, `sharpen`, `mode_truncation` are each fixed spatial operators that commute
   with the translation MR and preserve the channel integral, so they are structurally invisible
   to both MRs (0/24). On `heat` seed 0 (the one roster member whose output retains spatial
   structure) `spatial_shift` reaches rel-L2 up to 0.194 and `sharpen` up to 0.204 -- solidly in
   the realistic band -- and they **still** escape both MRs (0/4 in-band). `mode_truncation`
   stays below the realistic band (max 0.001) on these smooth low-resolution spectral outputs,
   so output-space MR testing cannot reach it here. The blind region is **real, not a
   construction artifact**.
3. **Honest verdict:** comparable-but-richer-and-messier than the constructed version. The
   by-class structure emerges (2x2 partition) and the transport/high-frequency blind region is
   confirmed real rather than designed; this is stronger evidence than the constructed C45
   (because it is measured, not built in) but messier (because it is not a clean diagonal).

Full claim wording is in `research_assets/experiments/claim-ledger.yml`
(`C48-fno-realistic-fault-emergence`).
