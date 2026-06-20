# Provenance: cross-architecture validity-coverage duality synthesis (claim C47, EXT-3)

Scope: **a synthesis over the four committed end-to-end seeded-fault reports (MeshGraphNets,
PointMLP, FNO, PINN) that checks whether the validity-coverage duality's two qualitative,
falsifiable predictions reproduce on every architecture family.** No new model runs; reads
already-committed reports only. This strengthens the duality (C37) from two CFD SUTs to four
architecture families but remains a **qualitative, falsifiable organizing principle — not** a
validated or quantitative predictive coverage model, **not** proven for all MRs/architectures,
and asserts no fault-detection rate or baseline superiority.

## Inputs (all committed; CPU-only, no credentials, no SUT, no torch)

| Input | Path (committed in this repo) |
|---|---|
| MeshGraphNets seeded-fault (C10) | `research_assets/runs/seeded-fault-detection/raw/metric_ledger.json` |
| PointMLP seeded-fault (C41) | `research_assets/runs/pointmlp-cylinder-seeded-fault-detection/raw/metric_ledger.json` |
| FNO seeded-fault (C45) | `research_assets/runs/fno-seeded-fault-detection/fno_seeded_fault_report.json` |
| PINN seeded-fault (C46) | `research_assets/runs/pinn-seeded-fault-detection/pinn_seeded_fault_report.json` |

## Environment configuration

CPU-only, **pure Python standard library** (no numpy/scipy/torch). The runner only reads JSON
and computes per-architecture coverage-geometry signatures:

```bash
# no extra dependency beyond Python 3.12
```

Determinism: the synthesis is a deterministic function of the four committed reports, so
reruns are byte-identical modulo the report timestamp. Runtime under a second.

## Operation steps

```bash
python tools/run_cross_architecture_duality.py \
    --outdir research_assets/runs/cross-architecture-duality
python tools/validate_research_assets.py
python -m pytest tests/test_cross_architecture_duality.py -q
```

## Pinned results (verification)

The duality's two predictions hold on **4/4** architecture families:
- **P1** (coverage partitioned by admitted MR): each family covers via two admitted-MR
  invariants — a conservation/mass invariant plus a symmetry-or-translation invariant
  (MGN/PointMLP: conservation + mirror-y; FNO: conservation + periodic translation; PINN:
  conservation + mirror-y).
- **P2** (structural blind region): every family has ≥1 fault preserving all measured
  invariants and detected by no MR — MeshGraphNets 5 (incl. the `PC_zero_vy` knife-edge),
  PointMLP 4, the FNO `transport_shift_blind`, the PINN `cos_x_blind`.

`duality_reproduces_on_all_families = true`. Full claim wording is in
`research_assets/experiments/claim-ledger.yml` (`C47-cross-architecture-coverage-duality`).
Generated 2026-06-20.
