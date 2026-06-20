# Provenance: PointMLP cross-architecture seeded-fault detection (claim C41, MVP-A)

Scope: **the paper's three domain-validity MR detectors run, with their predeclared
thresholds, on a SECOND already-converged architecture family (row-wise PointMLP) to
exercise the seeded-fault-detection step the MeshGraphNets SUT already has (C10).** One
converged SUT, one checkpoint, one eval trajectory, the same injected-fault catalogue.
**Not** a real-world fault-detection rate, reliability, baseline-superiority, or proof that
the by-class pattern generalizes across architectures (at most a reproduction on two).

## System under test and inputs (all committed; CPU-only, no credentials)

| Input | Path (committed in this repo) |
|---|---|
| PointMLP checkpoint (converged; rollout median rel-L2 0.0298) | `research_assets/runs/pointmlp-cylinder-primary-workflow/sut/checkpoint.pt` (sha256 `76c0c6c7…`) |
| Eval trajectory (DeepMind cylinder_flow test traj 2, 10 frames) | `research_assets/runs/primary-scope-upgrade/source_cases/test_traj002_frames000_009.npz` |
| MGN reference (committed C10 result, for the by-class comparison) | `research_assets/runs/seeded-fault-detection/raw/metric_ledger.json` |

The PointMLP SUT was trained on committed DeepMind cylinder_flow source cases
(`tools/run_pointmlp_cylinder_primary_workflow.py`); it is row-wise (no message passing) and
uses no edge connectivity, so it is a genuinely different architecture family from the MGN.
The read-only Minimum-MR-SubSet sibling is **not** needed for this experiment.

## Environment configuration

CPU-only. Beyond the repo's verifiable tier (`numpy`, `PyYAML`):

```bash
pip install "numpy==1.26.4" "scipy>=1.11" torch    # CPU torch is sufficient (no CUDA/MPS)
```

`torch` is the only extra dependency (the row-wise MLP runs on CPU in well under a minute).
Determinism: the node permutation uses a fixed seed (`numpy.random.default_rng(20260620)`)
and the checkpoint is loaded read-only, so reruns are byte-identical (modulo the ledger
timestamp).

## Operation steps

```bash
python tools/run_seeded_fault_detection_pointmlp.py \
    --out research_assets/runs/pointmlp-cylinder-seeded-fault-detection
python tools/validate_research_assets.py
python -m pytest tests/test_seeded_fault_detection_pointmlp_cross_sut.py -q
```

The runner writes `raw/metric_ledger.json` here. The guard test reads that committed ledger;
it does not re-run the SUT.

## Pinned results (verification)

- Eight of the ten catalogue mutants apply; the two mesh-adjacency mutants
  (`MA_drop_edges`, `MA_permute_edges`) are **not-applicable** (no-ops on a row-wise network
  with no edge set), recorded as such rather than as detector misses.
- Union detection **4/8** applicable (Wilson 95% CI [0.22, 0.78]); node-perm 0/8,
  conservation 4/8, mirror-y 2/8.
- By-class **reproduces the MGN reading on the shared classes**: node-permutation localizes
  none on both; conservation localizes boundary-condition + normalization-scale on both;
  mirror-y localizes a physical-channel fault on both (MGN union 5/10).
- Architecture-specific (honest): mesh-adjacency is MGN-only; on PointMLP the channel-swap
  fault additionally trips conservation and mirror-y additionally flags skip-denorm; the
  partial-channel-zeroing fault stays below threshold.

Full claim wording is in `research_assets/experiments/claim-ledger.yml`
(`C41-pointmlp-seeded-fault`). Generated 2026-06-20.
