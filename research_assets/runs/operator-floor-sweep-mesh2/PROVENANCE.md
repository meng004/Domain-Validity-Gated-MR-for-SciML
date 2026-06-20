# Provenance: operator-floor cross-topology sweep (claim C44, EXT-2)

Scope: **re-measure the P1 discrete-divergence operator floor on a SECOND, unstructured
mesh topology (Delaunay triangulation of a jittered grid) over the same domain and the same
analytically divergence-free reference field, and compare to the structured sweep (C12).**
Two specific mesh topologies, one smooth analytic field, one domain. **Not** a generalization
across arbitrary mesh families and **not** a closed-form bound for unstructured meshes (that
remains future work; cf. C32).

## Inputs (all committed; CPU-only, no credentials, no SUT)

| Input | Path (committed in this repo) |
|---|---|
| Structured sweep (for the matched-resolution floor-ratio comparison) | `research_assets/runs/operator-floor-sweep-extended/operator_floor_extended_report.json` |
| Operator + analytic field + char-length/fit helpers | `tools/conservation_rubric.py`, `tools/run_operator_floor_sweep.py`, `tools/run_operator_floor_sweep_extended.py` |

The unstructured mesh is generated in-process (no external input): a jittered structured grid
is Delaunay-triangulated over `[0, Lx] x [-Ly, Ly]`. No trained SUT, dataset, or sibling repo
is involved; the operator and analytic field are mesh-agnostic.

## Environment configuration

CPU-only. Beyond the repo's verifiable tier (`numpy`):

```bash
pip install "numpy==1.26.4" "scipy>=1.11"        # scipy supplies scipy.spatial.Delaunay
```

Determinism: the interior-node jitter uses a fixed seed (`SEED = 20260620`,
`numpy.random.default_rng`); the Delaunay triangulation is deterministic for a fixed point
set, so reruns are byte-identical modulo the report timestamp. Runtime well under a minute.

## Operation steps

```bash
python tools/run_operator_floor_sweep_mesh2.py \
    --outdir research_assets/runs/operator-floor-sweep-mesh2
python tools/validate_research_assets.py
python -m pytest tests/test_ext2_operator_floor_cross_topology.py -q
```

## Pinned results (verification)

- Unstructured (Delaunay) log--log slope **0.983**, Student-t 95% CI **[0.953, 1.014]**,
  R² = **0.999** over eight resolutions (920 to 137,760 cells), matching the structured slope
  **0.984**.
- Matched-resolution unstructured-over-structured floor-magnitude ratio: **1.06 median**,
  **1.33 maximum** (worst triangle angle about 14 degrees, so no degenerate-sliver artifact).
- Verdict `operator-floor-topology-stable`: the O(h) numerical-decidability decision does not
  flip between the two topologies.

Full claim wording is in `research_assets/experiments/claim-ledger.yml`
(`C44-operator-floor-cross-topology`). Generated 2026-06-20.
