# Provenance: three-arm complementarity + gate value + knife-edge (claims C42, C43; MVP-B/C)

Scope: **three detector arms on the converged PointMLP cylinder SUT over a 20-fault catalogue
(four predeclared classes), quantifying complementarity (NOT superiority) and making the
admissibility gate's value measurable.** One converged SUT, one checkpoint, one eval
trajectory; the MGN cross-SUT reading is read from committed artifacts (C38, C13), not re-run.
**No** real-world rate, reliability, or any baseline-superiority claim.

## System under test and inputs (all committed; CPU-only, no credentials)

| Input | Path (committed in this repo) |
|---|---|
| PointMLP checkpoint (converged; rollout median rel-L2 0.0298) | `research_assets/runs/pointmlp-cylinder-primary-workflow/sut/checkpoint.pt` |
| Eval trajectory (DeepMind cylinder_flow test traj 2, 10 frames) | `research_assets/runs/primary-scope-upgrade/source_cases/test_traj002_frames000_009.npz` |
| MGN MR-vs-accuracy reference (committed C38) | `research_assets/runs/detection-vs-accuracy/raw/metric_ledger.json` |
| Generic-template admissibility decisions (committed) | `research_assets/runs/generic-mr-baseline/generic_mr_report.json` |

The read-only Minimum-MR-SubSet sibling is **not** needed for this experiment.

## Environment configuration

CPU-only. Beyond the verifiable tier (`numpy`, `PyYAML`):

```bash
pip install "numpy==1.26.4" "scipy>=1.11" torch    # CPU torch is sufficient (no CUDA/MPS)
```

Determinism: fixed seeds for the node permutation (`default_rng(20260620)`) and the
PC_zero_vy node-index selection (`default_rng(99)`); the checkpoint is loaded read-only.
Reruns are byte-identical (modulo the ledger timestamp).

## Operation steps

```bash
python tools/run_three_arm_complementarity_pointmlp.py \
    --out research_assets/runs/pointmlp-three-arm-complementarity
python tools/validate_research_assets.py
python -m pytest tests/test_three_arm_complementarity.py -q
```

## The three arms (and why the third is a baseline-false-positive measurement)

- **Arm 1 validity-gated MR** (node-perm 1e-5, conservation ratio 1.5, mirror-y rel-change
  0.5) and **Arm 2 accuracy-monitor** (rollout L2 >= 2x the fault-free baseline) form the 2x2
  complementarity table.
- **Arm 3 ungated-generic** is measured by **baseline false-positive rate**, not a detection
  rate: the committed generic and expert MR baselines both admit *no* MR beyond the paper's
  three (`novel_retained = []`), so a "third detection arm" would either duplicate Arm 1
  (gated) or, if ungated, fire on the fault-free SUT. Each generic template is therefore
  treated as a claimed exact invariant, and the metric is whether it flags the correct,
  fault-free SUT. This makes the gate's value measurable: the gate admits only the
  real-invariant detector and rejects the false-alarming ones.

## Pinned results (verification)

- Catalogue **20 faults**, **4 predeclared classes** (boundary / normalization / temporal /
  physical-channel).
- Arm 1 (validity-gated MR) **13/20** (Wilson 95% CI [0.43, 0.82]); Arm 2 (accuracy) **6/20**.
- **2x2 (MR x accuracy):** both 4, MR-only 9, accuracy-only 2, neither 5 — nine MR-only faults
  are relation violations the accuracy monitor leaves within its 2x band (complementarity).
- **Gate value (Arm 3):** the one gate-admitted generic detector has a **0% baseline
  false-positive** rate; all **6 gate-rejected** templates fire on the fault-free SUT (**100%**)
  — the gate removes exactly the false-alarming detectors.
- **Knife-edge (PC_zero_vy node-index-selected partial zeroing):** detected at every fraction
  0.1–0.99, escapes only the uniform 1.0 (which becomes permutation-invariant) — a fault
  becomes invisible to a geometric detector exactly when it enters the detector's invariance;
  reproduces the MGN C13 knife-edge on a second (row-wise) architecture.
- ARS self-check: fault classes predeclared; descriptive detection rates with Wilson CIs (no
  hypothesis test), so no multiple-comparison correction is applied.

Full claim wording is in `research_assets/experiments/claim-ledger.yml`
(`C42-three-arm-complementarity`, `C43-knife-edge-blind-region`). Generated 2026-06-20.
