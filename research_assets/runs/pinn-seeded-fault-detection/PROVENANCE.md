# Provenance: PINN end-to-end seeded-fault detection (claim C46, EXT path-B)

Scope: **reproduce the MeshGraphNets by-class seeded-fault structure on a fourth, pointwise
architecture family (physics-informed MLP) using the converged K=6 Burgers PINN roster and
the shared committed FD reference grid.** K=6 trained checkpoints, one shared reference, one
author-designed output-level fault catalogue. **Not** a real-world fault-detection rate,
reliability, baseline-superiority, or cross-architecture generalization claim.

## System under test and inputs (all committed; CPU-only, no credentials)

| Input | Path (committed in this repo) |
|---|---|
| Burgers PINN K=6 roster (seeds 0–5) | `research_assets/runs/pinn-k6-roster/burgers_s{0..5}/sut/checkpoint.pt` |
| Shared FD reference grid (MR-C conservation Q) | `research_assets/runs/pinn-cross-family/reference_solution.npz` |
| PINN model class | `tools/train_pinn_burgers2d.py` (`PINN`) |

The PINN checkpoints are the already-committed roster; the read-only Minimum-MR-SubSet sibling
is **not** needed. Detectors are the PINN's two non-trivial admitted MRs (MR-B mirror-y
equivariance; MR-C mass conservation). MR-A permutation equivariance is vacuous for a pointwise
MLP and is not used as a detector.

## Environment configuration

CPU-only. Beyond the repo's verifiable tier (`numpy`):

```bash
pip install "numpy==1.26.4" torch        # CPU torch is sufficient (no CUDA/MPS)
```

Determinism: the random eval set uses a fixed seed (`EVAL_SEED = 20260620`); all faults are
deterministic output transforms of the predicted `(u_x, u_y)` field, so reruns are
byte-identical modulo the report timestamp. Runtime under a minute.

## Operation steps

```bash
python tools/run_seeded_fault_detection_pinn.py \
    --outdir research_assets/runs/pinn-seeded-fault-detection
python tools/validate_research_assets.py
python -m pytest tests/test_pinn_seeded_fault_detection.py -q
```

## Pinned results (verification, 6 SUTs)

- `scale_ux` -> **conservation** only (6/6; mirror ratio 0.99, Q change 15%).
- `asym_y_ux` (odd-in-y, zero integral) -> **mirror** only (6/6; mirror violation ratio
  about 9.6x, Q change 0.00%).
- `upper_half_offset` -> **both** (6/6).
- `cos_x_blind` (y-independent, x-zero-integral) -> **neither** (0/6, Wilson 95% CI
  **[0.00, 0.39]**); preserves u_x evenness and the conserved integral yet degrades the field
  up to ~0.70 relative L2 — a genuine blind subspace. Union: 3/4 faults detected by ≥1 MR.

Full claim wording is in `research_assets/experiments/claim-ledger.yml`
(`C46-pinn-seeded-fault-detection`). Generated 2026-06-20.
