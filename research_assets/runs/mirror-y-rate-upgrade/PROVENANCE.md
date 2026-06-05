# Provenance: mirror-y OOD-stress within-SUT frame-level rate

Scope: **same SUT, same checkpoint, same MR (mirror-y), multiple eval frames.**
This upgrades the two-frame mirror-y pilot to a bounded within-SUT frame-level
OOD-stress rate. It is **not** a reliability, accuracy, baseline, multi-SUT, or
exact-physical-symmetry claim, and the mirror-y mapping is deterministic (no seed
dimension is fabricated).

## System under test (read-only source)

- Same real trained MeshGraphNet cylinder-flow surrogate as the other pilots:
  `meng004/Minimum-MR-SubSet` (merged PR #103), commit `8c0b7ef`, checkpoint
  sha256 `cf281f85…b04a9` (shared by sha256 with the node-permutation pilot).

## Command

```bash
python3 -B tools/run_mirror_y_ood_stress.py \
  --manifest research_assets/runs/mirror-y-rate-upgrade/manifest.yml \
  --frames 0,1,2,3,4,5,6,7,8,9
```
Exit code `0`. Deterministic mapping (mirror axis y=0.205); `seed` recorded in the
manifest only for environment provenance, not as a sampling dimension.

## Why this is an approximate OOD-stress rate, not an exact MR rate

As in the two-frame pilot, the exact mirror-y relation is **out-of-relation-domain**
for this mesh (reflection about the channel centerline is non-bijective, worst
reflected-node mismatch ≈ one mesh edge length, cylinder off-centre by −7.2 mm).
The rubric downgrades it to an approximate nearest-neighbour OOD-stress probe, and
each frame is scored by the MR card formula against the same-space mapping-error
floor. The reported rate is therefore a within-SUT *frame-level* OOD-stress rate.

## Result

Recorded eval frames: `0,1,2,3,4,5,6,7,8,9` (the eval trajectory has 10 frames).

| frame | V | mapping-error floor | V/floor | verdict |
|---|---|---|---|---|
| 0 | 0.6914 | 0.1943 | 3.56 | fail |
| 1 | 0.6863 | 0.2081 | 3.30 | fail |
| 2 | 0.7364 | 0.2194 | 3.36 | fail |
| 3 | 0.7493 | 0.2479 | 3.02 | fail |
| 4 | 0.7494 | 0.1952 | 3.84 | fail |
| 5 | 0.7335 | 0.1727 | 4.25 | fail |
| 6 | 0.7255 | 0.1308 | 5.55 | fail |
| 7 | 0.7371 | 0.1502 | 4.91 | fail |
| 8 | 0.7596 | 0.1865 | 4.07 | fail |
| 9 | 0.7835 | 0.1883 | 4.16 | fail |

Aggregate (denominator = all 10 recorded frames; no frame was skipped, out-of-
relation-domain at the probe level, or inconclusive):

- **fail: 10 / 10** (frame-level OOD-stress rate = 1.0)
- pass: 0, inconclusive: 0
- median V = 0.7368, median V/floor = 3.96

## Honest statement (allowed wording)

Within the same SUT and checkpoint, the approximate mirror-y OOD-stress probe
failed on **10 of 10 recorded eval frames** under the predeclared MR-card metric,
each violation standing ~3–5.5× above its mapping-error floor.

## Honesty boundary

- The exact mirror-y relation remains out-of-relation-domain for this mesh.
- This is **not** a reliability claim, **not** an accuracy claim, **not** a
  baseline result, **not** a multi-SUT rate, and **not** a geometry-independent
  violation rate. It is one SUT, one checkpoint, one MR, one eval trajectory's
  frames, under an approximate reflection.
