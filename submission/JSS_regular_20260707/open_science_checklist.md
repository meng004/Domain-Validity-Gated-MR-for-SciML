# JSS open-science and availability checklist

Date: 2026-07-03

Purpose: record the submission-facing data and software availability status for
the JSS package without claiming any JSS Open Science validation that has not
occurred.

## Persistent identifiers and repositories

- Replication archive DOI: https://doi.org/10.5281/zenodo.20702952
- Source repository: https://github.com/meng004/Domain-Validity-Gated-MR-for-SciML
- Citation metadata: `CITATION.cff`
- Zenodo metadata: `.zenodo.json`

## Included in the replication package

- Manuscript source and Elsevier/JSS submission source.
- MR cards and admissibility rubric under `research_assets/mr_cards/` and
  `research_assets/rubric/`.
- Claim and experiment ledgers under `research_assets/experiments/`.
- Committed manifests, metric ledgers, reports, and derived outputs under
  `research_assets/runs/`.
- Validation scripts, runners, and fail-closed regression tests.
- Reproducibility instructions in `REPRODUCIBILITY.md`.

## External inputs not implied to be redistributed

- DeepMind cylinder-flow and airfoil TFRecords are public benchmark inputs
  staged by workflow runners; the manuscript package records provenance and
  derived ledgers rather than bundling the full TFRecords.
- Minimum-MR-SubSet evidence is read-only external/sibling evidence cited at
  commit `9ef862ec37335b4834d0a1fb38b4b613af702f34`.
- GPU-dependent and credential-dependent reruns are documented; missing
  credentials intentionally trigger fail-closed precondition checks.

## JSS Open Science status

The package is prepared for data/code availability review, but it has not been
validated by a JSS Open Science Board or awarded any JSS Open Science badge.
