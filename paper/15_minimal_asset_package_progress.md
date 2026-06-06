# Minimal Asset Package Progress

Date: 2026-06-05

## Scope

Implemented Task 1, Task 2, and the local-validation part of Task 3 from
`docs/superpowers/plans/2026-06-05-minimal-mr-assets-and-related-work.md`.

This note covers the structural validator, the minimum design-time
node-permutation MR asset package, and the reference ledger's local structural
validation. It does not cover related-work edits, manuscript edits, figures,
commits, pushes, or PRs.

## Files Created

- `tests/test_research_assets.py`
- `tools/validate_research_assets.py`
- `research_assets/mr_cards/node_permutation_equivariance.json`
- `research_assets/ledgers/candidate_ledger.json`
- `research_assets/ledgers/verdict_ledger.schema.json`
- `research_assets/ledgers/verdict_ledger.example.json`
- `paper/reference_ledger.md`
- `paper/15_minimal_asset_package_progress.md`

## TDD Record

### RED

Command:

```sh
rtk python3 -m unittest tests/test_research_assets.py
```

Observed failure after converting the tests to `unittest.TestCase`:

- 3 tests were collected.
- All 3 errored because `tools/validate_research_assets.py` did not exist.
- Failure class: `FileNotFoundError`.

After adding the validator but before adding JSON assets, the same command
failed with 3 assertion failures because the required MR card, candidate
ledger, verdict ledger schema, and verdict ledger example were missing.

### GREEN

Commands:

```sh
rtk python3 -m unittest tests/test_research_assets.py
rtk python3 tools/validate_research_assets.py
```

Observed result before integration hardening:

- `rtk python3 -m unittest tests/test_research_assets.py`: ran 3 tests, `OK`.
- `rtk python3 tools/validate_research_assets.py`: exited 0 with no validation
  failures printed.

### INTEGRATION RED

After `paper/reference_ledger.md` existed, an integration test was added to make
the reference ledger part of the same validation gate.

Command:

```sh
rtk python3 -m unittest tests/test_research_assets.py
```

Observed failure:

- 4 tests were collected.
- The new reference-ledger test failed because `validate_reference_ledger` did
  not exist.

Additional hardening tests were then added for candidate evidence references,
verdict schema contracts, and reference-ledger rows.

Command:

```sh
rtk python3 -m unittest tests/test_research_assets.py
```

Observed failure:

- 7 tests were collected.
- 3 tests failed because `validate_candidate_evidence_references`,
  `validate_verdict_schema_contract`, and `validate_reference_ledger_rows` did
  not exist.

After adding those functions, validation exposed one real evidence issue:

- `candidate_ledger.json` cited a local marker,
  `permutation must synchronize x, pos, y, and face`, that was not present in
  `theory/MeshGraphNets圆柱绕流MetBench_MR资产编制与验证说明.md`.

The ledger was corrected to cite only local markers present in that theory
file: `mgn-node-permutation-equivariance`, `node_permutation`,
`permutation_relative_l2_error`, and `<= 1e-6`.

### INTEGRATION GREEN

Commands:

```sh
rtk python3 -m unittest tests/test_research_assets.py
rtk python3 tools/validate_research_assets.py
```

Observed result:

- `rtk python3 -m unittest tests/test_research_assets.py`: ran 7 tests, `OK`.
- `rtk python3 tools/validate_research_assets.py`: exited 0 with no validation
  failures printed.

## What This Package Supports

- The MR card is structurally complete for the design-time
  `mgn-node-permutation-equivariance` relation.
- The candidate ledger records node permutation equivariance as a
  design-time-retained representation MR.
- The verdict ledger schema and example define the allowed verdict shape while
  keeping the example entries empty until actual runs exist.
- The validator checks required structural fields, design-time evidence levels,
  allowed verdict classes, and the empty no-run verdict example.
- The validator now also checks candidate evidence references against local
  files, checks the strict verdict-ledger schema contract, and checks that the
  reference ledger has per-key status, observed facts, evidence sources, and
  claim-support limits.

## What This Package Does Not Support

- No real SUT was run.
- No empirical pass/fail verdict was produced.
- No MR violation rate or pass rate was produced.
- No model reliability or unreliability conclusion was produced.
- The reference ledger is structurally validated, but most closest-work entries
  remain `PARTIAL` or `UNVERIFIED`; this does not support strong related-work
  or novelty claims.
- No manuscript, related-work, or contribution text was edited.
- No commit, push, or PR was performed.

## Local Evidence Links

- Node-permutation MR design anchor:
  `theory/MeshGraphNets圆柱绕流MetBench_MR资产编制与验证说明.md` lists
  `mgn-node-permutation-equivariance`, the `node_permutation` transform,
  `permutation_relative_l2_error`, and threshold `<= 1e-6`.
- Implementation asset:
  `research_assets/mr_cards/node_permutation_equivariance.json` encodes the
  relation, metric, tolerance, allowed verdicts, and claim limitations.
- Decision ledger:
  `research_assets/ledgers/candidate_ledger.json` records the design-time
  retained decision and states that it is not a SUT pass/fail claim.
- No-run verdict example:
  `research_assets/ledgers/verdict_ledger.example.json` keeps `entries` empty
  and declares `evidence_level` as `schema-example-no-runs`.
- Reference ledger:
  `paper/reference_ledger.md` records `qi2025physicalfield` as `UNVERIFIED`,
  `yu2025fluidvelocity` as `PARTIAL`, and guardrails that prevent strong
  closest-work or first/only novelty claims from these entries.
