# Provenance: discrete divergence / mass-conservation diagnostic (evidence-gated)

Scope: **one SUT, one MR (discrete divergence boundedness), a few eval frames.**
Not a violation rate, not a reliability/accuracy claim, not a baseline comparison,
and **not** an absolute mass-conservation proof.

## System under test (read-only source)

- Same real trained MeshGraphNet cylinder-flow surrogate as the other pilots:
  `meng004/Minimum-MR-SubSet` (merged PR #103), commit `8c0b7ef`, checkpoint
  sha256 `cf281f85…b04a9` (shared by sha256 with the node-permutation pilot).

## Command

```bash
python3 -B tools/run_conservation_diagnostic.py \
  --manifest research_assets/runs/conservation-diagnostic-pilot/manifest.yml \
  --frames 0,4
```
Exit code `0`. Stdout/stderr in `raw/stdout.log`, `raw/stderr.log`.

## Why the absolute relation stays deferred (the rubric decision)

The discrete divergence operator is a P1 (linear, constant-per-cell) divergence on
the triangular mesh, summarised by an area-weighted RMS. On this coarse mesh the
**ground-truth** field's discrete divergence is itself non-negligible —
dimensionless reference divergence ≈ `0.037` (raw RMS ≈ `2.08`), far above any
absolute `div ≈ 0` tolerance (`1e-6`). An absolute divergence-free relation is
therefore **not calibratable** here, so it stays `deferred-uncalibrated-absolute-tolerance`
(matching the design-time candidate ledger's `deferred` decision). This pilot is
itself the evidence for keeping the absolute relation deferred.

## Reference-relative diagnostic

Instead of an absolute tolerance, the diagnostic compares the surrogate's
predicted next-state discrete divergence to the ground-truth next-state divergence
on the same mesh, flagging a conservation *regression* only when the ratio exceeds
`1.5`.

| frame | div_rms (pred) | div_rms (reference) | ratio pred/reference | verdict |
|---|---|---|---|---|
| 0 | 2.0901 | 2.0848 | 1.0025 | pass |
| 4 | 2.0521 | 2.0431 | 1.0044 | pass |

The surrogate's predicted field differs from the reference (max abs velocity diff
≈ 0.106, so the model genuinely predicts a different field), yet its discrete
divergence stays within ~0.4% of the reference level: the surrogate does **not**
degrade mass conservation relative to the data representation.

## Honesty boundary

Pilot evidence for one SUT, two eval frames. It asserts no absolute mass
conservation (the absolute relation is deferred), no violation/conservation rate,
no reliability, no accuracy, and no baseline result. It supports only the narrow,
reference-relative statement that the surrogate's discrete divergence matches the
ground-truth field's on these frames — and it demonstrates the rubric refusing an
uncalibratable absolute tolerance rather than fabricating one.
