# DeepXDE PeriodicBC issue-linked supplemental evidence completion report

Date: 2026-07-03

Target: one real-defect-linked supplemental empirical unit for JSS.

## Final status

Status: **completed as a single external issue/PR-linked semantic witness**.

The unit completes the chain:

candidate MR -> rubric decision -> MR card -> archived external issue/PR
source -> analytic source/follow-up endpoint check -> metric -> typed verdict
-> experiment ledger -> claim ledger -> supplementary integration.

The typed verdict is **pass** for reproducing the documented DeepXDE
PeriodicBC derivative-periodicity semantic contrast. This is not a trained
surrogate run and not a defect-rate study.

## Evidence artifacts

External source artifacts:

- `research_assets/runs/deepxde-periodicbc-real-defect-scan/raw/deepxde_issue_26.json`
- `research_assets/runs/deepxde-periodicbc-real-defect-scan/raw/deepxde_issue_26_comments.json`
- `research_assets/runs/deepxde-periodicbc-real-defect-scan/raw/deepxde_pr_27.json`
- `research_assets/runs/deepxde-periodicbc-real-defect-scan/raw/deepxde_pr_27.patch`
- `research_assets/runs/deepxde-periodicbc-real-defect-scan/raw/deepxde_periodicbc_commit_search.json`

MR card:

- `research_assets/mr_cards/deepxde_periodicbc_derivative_enforcement.json`

Runner and report:

- `tools/run_deepxde_periodicbc_real_defect_witness.py`
- `research_assets/runs/deepxde-periodicbc-real-defect-scan/deepxde_periodicbc_real_defect_witness_report.json`

Ledger entries:

- Experiment run: `deepxde-periodicbc-real-defect-witness-001`
- Claim: `C56-deepxde-periodicbc-real-defect-witness`

## Observed facts

Source facts:

- DeepXDE issue #26 is closed and titled "Periodic boundary condition issue".
- PR #27 is merged.
- PR #27 metadata records merge time `2020-04-07T20:40:13Z`.
- Merge commit: `c4b44313939aac1aa51430e9e2a1b6c2cbec0c10`.
- The PR patch adds `derivative_order` support to `PeriodicBC`.
- The commit-search artifact contains the message
  "PeriodicBC supports first order derivative (#27)".

Runtime semantic facts:

- Primary witness function: `u=x(1-x)`.
- Endpoint values: `u(0)=0`, `u(1)=0`.
- Endpoint derivatives: `du/dx(0)=1`, `du/dx(1)=-1`.
- Pre-PR value-only absolute residual: `0.0`.
- PR #27 `derivative_order=1` absolute residual: `2.0`.
- Smooth periodic control `u=sin(2*pi*x)` has value residual
  `2.4492935982947064e-16` and derivative residual `0.0`.
- Value-nonperiodic control `u=x` has value residual `1.0`.
- Typed verdict: `pass`.

## Allowed claim

The paper may say that one external DeepXDE issue/PR-linked boundary-condition
semantic witness was brought through the same fail-closed evidence chain. The
witness shows that a documented PeriodicBC derivative-periodicity blind spot can
be represented as a source/follow-up residual check and linked to a merged
external fix.

## Forbidden claims

Do not claim:

- a real-world defect-detection rate;
- trained PINN or surrogate accuracy;
- DeepXDE-wide correctness;
- production CFD validation;
- broad real-defect effectiveness;
- deployment readiness.

## Review interpretation

This evidence addresses a narrower but important reviewer concern than the
RealPDEBench preflight. RealPDEBench adds production-adjacent public data but no
pass/fail floor. The DeepXDE witness adds a real external defect/fix link and a
complete pass verdict, but at boundary-condition component level rather than
trained-SUT level. Together they strengthen external validity without changing
the paper into a production-CFD or real-defect-rate study.
