# Provenance: mirror-y OOD-stress MR probe (evidence-gated)

Scope: **one SUT, one MR (mirror-y), a few eval frames.** Not a violation rate,
not a reliability claim, not a baseline comparison.

## System under test (read-only source)

- Same real trained MeshGraphNet cylinder-flow surrogate as the node-permutation
  pilot: `meng004/Minimum-MR-SubSet` (merged PR #103), commit `8c0b7ef`.
- Checkpoint sha256 `cf281f85…b04a9` and the eval-split source case are shared
  by sha256 with `research_assets/runs/real-sut-node-permutation-pilot/`.

## Command

```bash
python3 -B tools/run_mirror_y_ood_stress.py \
  --manifest research_assets/runs/mirror-y-ood-stress-pilot/manifest.yml \
  --frames 0,4
```
Exit code `0`. Stdout/stderr in `raw/stdout.log`, `raw/stderr.log`.

## Why this is NOT a clean equivariance test (the rubric decision)

Mirror-y equivariance requires a mirror-symmetric domain. The measured geometry
of the real eval mesh (`raw/precondition_report.json`) does **not** satisfy this:

- reflection about the channel centerline `y = 0.205` is **not a bijection**;
- the worst reflected-node mismatch is `1.93e-2`, ≈ one median mesh edge length
  (`1.88e-2`) — i.e. `max_nn_over_edge ≈ 1.03`;
- node-type match under reflection is `0.977` (< 1);
- the cylinder is **off-centre by −7.2 mm** (center `y ≈ 0.198` vs centerline
  `0.205`) — the classic DFG asymmetry that drives vortex shedding.

So the rubric classifies the exact mirror relation as **out-of-relation-domain**
and downgrades it to a **conditional OOD-stress probe** (`retained-ood-stress`).
This is the evidence-gating point: the method refuses to treat mirror-y as a
clean MR on a geometry that does not support it.

## OOD-stress probe procedure

For each frame, following the MR card formula
`norm(unmirror_y(y_mirror) - y0) / norm(y0)`:

- `source_output` `y0 = f(s)`;
- build the mirrored input via the nearest-neighbour reflection correspondence
  `pi` (`v_y -> -v_y`, reflect node values), and predict
  `follow_up_output = f(mirror(s))` `= y_mirror`;
- `mapped_output = unmirror(y_mirror)` (apply the reflection to the follow-up);
- violation `V = norm(mapped_output - source_output) / norm(source_output)`.

The **mapping-error floor** is computed in the same (output) space: applying the
reflection twice to the source prediction would be the identity for a perfect
correspondence, so `norm(mirror(mirror(y0)) - y0) / norm(y0)` bounds the error
attributable to the imperfect `pi` rather than to the model.

## Result (approximate OOD-stress)

| frame | mirror_y_relative_l2_error (V) | mapping-error floor | V / floor | OOD-stress verdict |
|---|---|---|---|---|
| 0 | 0.6914 | 0.1943 | 3.56 | fail |
| 4 | 0.7494 | 0.1952 | 3.84 | fail |

The model's mirror-y equivariance residual (~0.69–0.75 relative L2) stands
~3.6–3.8× above the mapping-error floor, so the violation is the model's, not an
artefact of the approximate correspondence. Independent re-check confirmed
`mapped == unmirror(follow_up)` and `mapped != source` (max abs diff ≈ 4.0).

## Honesty boundary

Pilot evidence for one SUT, one MR, two eval frames, under an **approximate**
reflection (the exact relation being out-of-relation-domain). It does not assert
a violation rate, model reliability, baseline superiority, or seeded-fault
detection, and it does not measure the model's accuracy. It supports only the
qualitative point that a genuinely trained, converged surrogate (training loss
1.62 -> 0.022 per the SUT repo's checkpoint manifest) can still substantially
violate a physically-motivated reflection symmetry.
