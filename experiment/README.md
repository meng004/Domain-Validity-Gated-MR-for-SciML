# Experiment

This directory is the navigation entry point for the replication and validation
side of the project.

The executable assets remain at their established repository paths so existing
validators, tests, and manuscript guards continue to work:

- `research_assets/` stores claim ledgers, MR cards, rubrics, fixtures, and
  committed run artifacts.
- `tools/` stores deterministic runners, validators, scoring scripts, and
  build helpers.
- `tests/` stores regression guards that bind prose claims to ledgers.
- `requirements.txt` and `requirements/` define the Python environments.
- `REPRODUCIBILITY.md` gives the smoke, cache-replay, and full rerun tiers.

For release archives, these paths are bundled under the Zenodo package root.
