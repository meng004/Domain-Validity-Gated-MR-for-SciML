# Provenance: real-sut node-permutation equivariance MR pilot

Scope: **one SUT, one MR, one source case.** Pilot evidence only — not a rate,
not a reliability claim, not a baseline comparison.

## System under test (read-only source)

- Repository: `meng004/Minimum-MR-SubSet` (cloned read-only at `/home/user/Minimum-MR-SubSet`).
- Commit: `8c0b7ef3605fd9452884d701e2a191a2b14a5a35`.
- Provenance: the trained MeshGraphNet cylinder-flow surrogate produced by that
  repository's merged PR #103 ("EXP: real cylinder-flow MGN runtime ABD-A witness").
- Model code consumed (read-only): `scripts/mcmr/cylinder_flow/{mgn.py,dm_dataset.py}`.

## Vendored artifacts (committed here, verified by sha256)

- `sut/checkpoint.pt` — sha256 `cf281f85941ff21ff86af0122924299d7b71a375f50f118e725eda1e859b04a9`
  (matches the SUT repo's `checkpoint_manifest.json`).
- `source_case.npz` — sha256 `f72a285d9c98ea0f132d22b08e6bbf0caa6a249c07d856195cec1f466467ac02`
  (the DeepMind cylinder_flow **test/eval** split slice; matches the SUT repo's
  `data_manifest.json:validation_npz_sha256`).

## Command

```bash
python3 -B tools/run_real_sut_mr.py \
  --manifest research_assets/runs/real-sut-node-permutation-pilot/manifest.yml \
  --frame 0
```

Exit code: `0`. Stdout/stderr captured in `raw/stdout.log`, `raw/stderr.log`.

## Procedure

1. Load the source case (eval-split frame 0; 1923 nodes, 11070 mesh edges).
2. Run the SUT → source output (per-node velocity-delta prediction).
3. Apply a node permutation (seed 20260605, a bijection over node indices) and
   relabel the mesh edge endpoints consistently.
4. Run the SUT on the permuted graph → follow-up output.
5. Inverse-map the follow-up output back to the source node order → mapped output.
6. Score relative L2 of (mapped − source) and compare to the MR card tolerance.

## Result

- `permutation_relative_l2_error` = `0.0` (tolerance `1e-6`, assertion `less_or_equal`).
- Verdict: `pass`.
- Independent check: the follow-up output differs from the source output in the
  permuted node order (max abs diff ≈ 11.0, so the SUT genuinely ran on the
  permuted graph), while the inverse-mapped output equals the source output
  bit-for-bit. The model is permutation-equivariant by construction; this run
  confirms that property holds for this real checkpoint on this real case.

## Honesty boundary

Pilot evidence for one SUT, one MR, one source case. It does not establish a
pass/fail rate, a violation rate, model reliability, baseline superiority, or
seeded-fault detection. Those remain blocked or speculative in the claim ledger.
