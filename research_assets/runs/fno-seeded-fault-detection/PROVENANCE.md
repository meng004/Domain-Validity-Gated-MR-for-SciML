# Provenance: FNO end-to-end seeded-fault detection (claim C45, EXT path-B)

Scope: **upgrade the converged K=6 FNO-2D roster from a clean-model MR-compliance check into a
fault DETECTION experiment, reproducing the MeshGraphNets by-class structure on a third
architecture family (spectral FNO) and different physics (Burgers/heat).** K=6 trained
checkpoints, one author-designed output-level fault catalogue. **Not** a real-world
fault-detection rate, reliability, baseline-superiority, or cross-architecture generalization
claim.

## System under test and inputs (all committed; CPU-only, no credentials)

| Input | Path (committed in this repo) |
|---|---|
| FNO-2D K=6 roster (Burgers/heat x seeds 0,1,2) | `research_assets/runs/fno-k6-roster/{burgers,heat}_s{0,1,2}/sut/checkpoint.pt` |
| FD dataset generator + model loader + metric helper | `tools/gen_fd_dataset_2d.py`, `tools/run_fno_k6_roster.py`, `tools/train_fno_2d.py` |

The FNO checkpoints are the already-committed roster; the read-only Minimum-MR-SubSet sibling
is **not** needed. Detectors are the FNO's two admitted MRs (periodic translation; periodic
channel-sum/mass).

## Environment configuration

CPU-only. Beyond the repo's verifiable tier (`numpy`):

```bash
pip install "numpy==1.26.4" torch        # CPU torch is sufficient (no CUDA/MPS)
```

Determinism: the eval cases are generated with fixed seeds, and all faults are deterministic
output transforms (scale, offset, fixed masks, periodic roll), so reruns are byte-identical
modulo the report timestamp. Runtime under a minute.

## Operation steps

```bash
python tools/run_seeded_fault_detection_fno.py \
    --outdir research_assets/runs/fno-seeded-fault-detection
python tools/validate_research_assets.py
python -m pytest tests/test_fno_seeded_fault_detection.py -q
```

## Pinned results (verification, 24 cells per fault = 6 SUTs x 4 cases)

- `global_scale`, `constant_offset` -> **conservation** only (24/24; translation 0/24).
- `asymmetric_zero_sum_bias` -> **translation** only (24/24; conservation 0/24).
- `asymmetric_nonzero_bias` -> **both** (24/24).
- `transport_shift_blind` -> **neither** (0/24, Wilson 95% CI **[0.00, 0.14]**); a
  translation-equivariant, channel-sum-preserving transport/phase fault that degrades the
  field up to ~0.27 relative L2 yet evades both MRs at every swept severity — a genuine blind
  subspace. Union: 4/5 faults detected by ≥1 MR.

Full claim wording is in `research_assets/experiments/claim-ledger.yml`
(`C45-fno-seeded-fault-detection`). Generated 2026-06-20.
