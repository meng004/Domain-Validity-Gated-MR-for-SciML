# RealPDEBench foil supplemental evidence completion report

Date: 2026-07-03

Target: optional production-adjacent supplemental empirical unit for JSS.

Plan source: `paper/86_targeted_supplemental_empirical_scan_plan.md`.

## Final status

Status: **completed as an inconclusive production-adjacent preflight witness**.

The supplemental unit does not produce a pass/fail SUT verdict. It does complete
a fail-closed evidence chain:

candidate MR -> metadata/rubric precondition screen -> MR card -> public
zero-AoA real-flow source field -> mirror source/follow-up metric -> typed
verdict -> experiment ledger -> claim ledger -> supplementary integration.

The final typed verdict is **inconclusive**, because the coordinate mirror map
is exact on the stored grid but no independent PIV measurement-floor bound is
available for interpreting the observed real-field mirror residual as a pass or
fail.

## Evidence artifacts

Metadata screen:

- `research_assets/runs/realpdebench-foil-metadata-screen/metadata_screen_summary.json`
- `paper/87_realpdebench_foil_phase_s1_s2_screen_report.md`

MR card:

- `research_assets/mr_cards/realpdebench_foil_mirror_y_gate.json`

Preflight runner and report:

- `tools/run_realpdebench_foil_mirror_preflight.py`
- `research_assets/runs/realpdebench-foil-preflight/foil_mirror_preflight_report.json`

Source artifact:

- `research_assets/runs/realpdebench-foil-preflight/raw/real-data-00000-of-00098.arrow`
- SHA-256:
  `294bea9abde2ef140fa83ca0580c5a1d37940642c4232f8f58b506cc5da994a9`
- Remote source:
  `https://huggingface.co/datasets/AI4Science-WestlakeU/RealPDEBench/resolve/main/foil/hf_dataset/real/data-00000-of-00098.arrow`

Ledger entries:

- Experiment run: `realpdebench-foil-mirror-preflight-001`
- Claim: `C55-realpdebench-foil-mirror-preflight`

Tests:

- `tests/test_realpdebench_foil_metadata_screen.py`

JSS integration:

- `submissions/JSS/supplementary/evidence_appendices.tex`
- `submissions/JSS/main.tex` only names the supplement-level preflight witness.

## Observed facts

Metadata facts:

- RealPDEBench foil metadata has machine-readable angle of attack and Reynolds
  number.
- Real fields include `u`, `v`, `x`, `y`, and `t`.
- Numerical fields include `u`, `v`, `p`, `x`, `y`, and `t`.
- Real test index includes 1088 zero-AoA rows and 19 zero-AoA unique
  simulations.
- Numerical test index includes 102 zero-AoA rows and 10 zero-AoA unique
  simulations.

Preflight run facts:

- Source field: `10000_0.0.h5`.
- Reynolds number: 10000.
- Angle of attack: 0.0 degrees.
- Field shape: 3990 x 128 x 256.
- Coordinate mirror axis: 0.
- x-invariance floor: 0.0.
- y-reflection floor: 0.0.
- Coordinate floor max norm: 0.0.
- u mirror relative L2: 0.0600196123.
- sign-reversed-v mirror relative L2: 1.3753287792.
- combined uv relative L2: 0.2292153537.
- Typed verdict: `inconclusive`.

## Allowed claim

The paper may say that a production-adjacent public RealPDEBench foil real-flow
case was screened and brought through metadata validation, coordinate mirror
mapping, and source/follow-up metric generation under the same fail-closed
admissibility style used in the paper. The coordinate reflection floor is zero
for the downloaded zero-AoA field, but the observed real-field mirror residual
cannot be interpreted as pass/fail without an independent PIV measurement-floor
bound.

## Forbidden claims

Do not claim:

- RealPDEBench validates the method on production CFD.
- The method detects real defects on RealPDEBench.
- The foil result is a trained-SUT pass/fail result.
- The method generalizes to aerodynamic data or real-flow benchmarks.
- The observed mirror residual is a SUT fault.
- The preflight proves model reliability, physical correctness, or deployment
  readiness.

## Review interpretation

This evidence has useful but bounded JSS value. It addresses the reviewer
concern that the paper only uses self-made synthetic tasks by adding a public
real-flow benchmark artifact and a real measured field. It does not close the
real-defect or production-deployment gap, and it should not be promoted to a
primary empirical result. Its best role is supplementary: it shows that the
same admissibility discipline can fail closed on production-adjacent public
data when the measurement floor is not yet known.

## Next action

No additional RealPDEBench data download is recommended for the JSS submission
unless the authors obtain or derive a defensible PIV measurement-floor bound.
Without that bound, more RealPDEBench field residuals would add volume but not
license stronger claims.
