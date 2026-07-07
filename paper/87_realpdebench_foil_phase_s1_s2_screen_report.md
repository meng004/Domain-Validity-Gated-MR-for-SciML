# RealPDEBench foil Phase S1-S2 screen report

Date: 2026-07-03

Purpose: execute the first two phases of
`paper/86_targeted_supplemental_empirical_scan_plan.md` for the candidate
supplemental empirical unit:

`RealPDEBench Foil mirror-y admissibility gate`.

## Phase S1: metadata-only screen

Status: **Go to S2; not yet Go to verdict execution.**

No large Arrow data, model checkpoint, or training artifact was downloaded.
Only public metadata and small JSON files were saved under:

`research_assets/runs/realpdebench-foil-metadata-screen/`

### Source evidence

Primary public sources:

- RealPDEBench website: `https://realpdebench.github.io/`
- RealPDEBench GitHub README:
  `https://github.com/AI4Science-WestlakeU/RealPDEBench`
- Hugging Face dataset tree and small metadata JSONs:
  `https://huggingface.co/datasets/AI4Science-WestlakeU/RealPDEBench`

Downloaded metadata artifacts:

- `hf_foil_tree.json`
- `channels.json`
- `in_dist_test_params_real.json`
- `out_dist_test_params_real.json`
- `remain_params_real.json`
- `remain_params_numerical.json`
- `test_index_real.json`
- `test_index_numerical.json`
- `dataset_info_real.json`
- `dataset_info_numerical.json`
- `state_real.json`
- `metadata_screen_summary.json`
- `github_readme.md`
- `website_home.html`

### Metadata facts observed

From `channels.json`:

- Scenario: `foil`.
- Real fields: `u`, `v`.
- Numerical fields: `u`, `v`, `p`.
- The file states that geometric parameters, including angle of attack and
  Reynolds number, are stored in the `*_params_*.json` index files.

From `dataset_info_real.json` and `dataset_info_numerical.json`:

- Real features include `sim_id`, `u`, `v`, `x`, `y`, `t`, and shape fields.
- Numerical features include `sim_id`, `u`, `v`, `p`, `x`, `y`, `t`, and shape
  fields.

From `metadata_screen_summary.json`:

- Real split parameter counts:
  - `in_dist`: 10
  - `out_dist`: 10
  - `remain`: 78
- Real AoA distribution:
  - `in_dist`: 10 cases at 10.0 degrees.
  - `out_dist`: 6 cases at 0.0 degrees, 1 at 15.0 degrees, 3 at 20.0 degrees.
  - `remain`: 13 cases at 0.0 degrees, 19 at 5.0 degrees, 10 at 10.0 degrees,
    19 at 15.0 degrees, 17 at 20.0 degrees.
- Real test index:
  - 5140 rows.
  - 98 unique simulations.
  - 1088 zero-AoA rows.
  - 19 zero-AoA unique simulations.
- Numerical metadata:
  - 99 `remain` parameter cases.
  - 20 zero-AoA numerical cases.
  - Numerical test index has 442 rows, 48 unique simulations, and 102 zero-AoA
    rows.

Interpretation:

- The RealPDEBench foil candidate passes the metadata-only availability screen:
  AoA is machine-readable; zero-AoA and non-zero-AoA cases exist; real and
  numerical field metadata expose velocity components and coordinates.
- This does **not** yet prove mirror-y admissibility. The actual coordinate
  arrays still need to be inspected to verify reflection centerline, exact or
  interpolated mapping, component orientation, and mapping/measurement floor.

### Phase S1 decision

Decision: **Go to Phase S2**.

Reason:

- The candidate is not blocked by missing AoA metadata.
- The candidate is not blocked by missing velocity/channel metadata.
- The candidate is still blocked from verdict execution until coordinate
  symmetry and floor dominance are checked.

## Phase S2: algebraic MR-card precommitment

Status: **completed as design-time candidate, not executable result.**

Created:

- `research_assets/mr_cards/realpdebench_foil_mirror_y_gate.json`

Key precommitted rule:

- Exact mirror-y is only a candidate for `AoA = 0.0` degree cases.
- Non-zero AoA cases must be rejected as out-of-relation-domain for exact
  mirror-y.
- Coordinate centerline, velocity component convention, and mapping /
  measurement floor must be verified before any pass/fail verdict is allowed.
- The card carries no numeric tolerance and no pass/fail verdict classes.

Allowed current candidate verdicts:

- `skip`
- `out-of-relation-domain`
- `numerical-tolerance-issue`
- `inconclusive`

Blocked claims:

- No real-defect detection claim.
- No production CFD validation claim.
- No broad aerodynamic generalization claim.
- No model reliability claim.
- No pass/fail claim for RealPDEBench foil yet.

## Tests added

Created:

- `tests/test_realpdebench_foil_metadata_screen.py`

The tests assert:

- Zero-AoA real and numerical cases exist in the metadata screen.
- Real and numerical metadata expose velocity and coordinate fields.
- The new MR card remains a fail-closed `design-time-candidate`, with no
  calibrated threshold and no pass/fail verdicts.

Verification result:

- `tests/test_realpdebench_foil_metadata_screen.py`: 3 passed.
- `tools/validate_research_assets.py`: passed.
- `tools/validate_experiment_protocol.py`: passed.
- Full test suite: 452 passed, 334 subtests passed.

## Next phase

Recommended next step: Phase S3-preflight, still without training:

1. Download or access the smallest possible zero-AoA real and numerical field
   shard needed to inspect coordinates and one time slice.
2. Verify whether `(x, y)` supports a deterministic reflection map.
3. Estimate the coordinate-reflection / interpolation floor.
4. If the floor is not bounded, stop with `DEFERRED_NUMERICAL_FLOOR`.
5. Only if floor dominance can be established, generate a typed verdict ledger.

Do not integrate anything into the JSS main paper at this stage.
