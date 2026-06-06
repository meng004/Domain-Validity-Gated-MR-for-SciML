# Stage 2.5 Claim-Evidence Integrity Audit

Date: 2026-06-06

Scope: Integrity audit for the current manuscript and IST submission package
after PR4. The audit is deliberately conservative: a claim is allowed only if it
can be traced to a ledger, artifact, or cited source. Anything else is marked
blocked, deferred, or protocol-only.

## Evidence Sources Checked

- `research_assets/experiments/claim-ledger.yml`
- `research_assets/experiments/experiment-ledger.yml`
- `research_assets/experiments/evidence-package.md`
- `research_assets/runs/real-sut-node-permutation-pilot/raw/metric_ledger.json`
- `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json`
- `research_assets/runs/conservation-diagnostic-pilot/raw/metric_ledger.json`
- `paper/citation_audit.md`
- `paper/ist-submission/main.tex`
- `paper/manuscript.md`

## Claim Matrix

| Claim ID | Current status | Allowed wording | Evidence path | Forbidden overclaim |
|---|---|---|---|---|
| C1-domain-validity-rubric | Supported as method/design claim | The paper proposes a domain-validity rubric that screens candidate MRs before execution. | `research_assets/rubric/domain_validity_rubric.json`; `paper/manuscript.md`; `paper/ist-submission/main.tex` | The rubric proves physical validity or replaces domain expertise. |
| C2-mr-card-executable-assets | Supported as asset/workflow claim | Retained candidates are represented as MR cards and executable assets with transformations, metrics, tolerances, exclusions, and verdicts. | `research_assets/mr_cards/`; `tools/validate_research_assets.py`; `paper/manuscript.md` | Every card has cross-SUT empirical evidence. |
| C3-baseline-comparison-blocked | Blocked | Baselines are protocol commitments only: expert MR design, generic MR-generation scope contrast, LLM candidates, and rollout accuracy diagnostics. | `research_assets/experiments/claim-ledger.yml`; `research_assets/experiments/experiment-ledger.yml` | Seeded-fault and baseline superiority claims remain blocked; no superiority, fault-detection, localization, or runtime claim is supported. |
| C4-node-permutation-sanity | Observed pilot | Node-permutation equivariance holds to machine precision for one real trained MeshGraphNets cylinder-flow surrogate and one pilot case; this is a structural sanity check. | `research_assets/runs/real-sut-node-permutation-pilot/raw/metric_ledger.json`; `claim-ledger.yml` | The SUT passes node permutation in general, or model reliability has been established. |
| C5-conservation-diagnostic-deferred | Observed diagnostic, absolute claim deferred | The absolute conservation relation remains deferred because the discrete divergence operator gives non-negligible reference divergence; a reference-relative diagnostic passes on recorded frames. | `research_assets/runs/conservation-diagnostic-pilot/raw/metric_ledger.json`; `research_assets/runs/conservation-diagnostic-pilot/raw/conservation_report.json`; `claim-ledger.yml` | Absolute conservation remains deferred; do not claim exact divergence-free behavior, conservation rate, or model reliability. |
| C6-mirror-y-ood-stress | Observed bounded pilot | Exact mirror-y is out-of-relation-domain for this mesh and is downgraded to an approximate OOD-stress probe; it failed on 10 of 10 recorded eval frames, with median relative L2 0.737 and median V/floor 3.96. | `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json`; `research_assets/runs/mirror-y-rate-upgrade/manifest.yml`; `claim-ledger.yml`; `experiment-ledger.yml` | This is not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim. |
| C7-llm-candidate-support-only | Supported as process boundary | LLM use is restricted to candidate generation and material organization; it does not judge MR validity. | `paper/manuscript.md`; `paper/ist-submission/main.tex`; method and ethics sections | LLMs automatically identify valid SciML MRs. |

## Numeric Claim Trace

| Number or phrase | Permitted location | Evidence |
|---|---|---|
| `relative L2 = 0.0` | Node-permutation pilot result | `research_assets/runs/real-sut-node-permutation-pilot/raw/metric_ledger.json` |
| `failed on 10 of 10 recorded eval frames` | Mirror-y bounded OOD-stress result | `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json` |
| `median relative L2 0.737` | Mirror-y bounded OOD-stress result | `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json` |
| `median V/floor 3.96` | Mirror-y bounded OOD-stress result | `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json` |
| `one SUT, one checkpoint, one MR, one eval trajectory` | Mirror-y claim boundary | `research_assets/experiments/claim-ledger.yml`; `experiment-ledger.yml` |
| `absolute conservation remains deferred` | Divergence/conservation diagnostic | `research_assets/runs/conservation-diagnostic-pilot/raw/conservation_report.json`; `claim-ledger.yml` |

## Integrity Verdict

The current manuscript can claim a method workflow plus three minimal within-SUT
pilot outcomes. It cannot claim cross-SUT generality, seeded-fault effectiveness,
baseline superiority, runtime advantage, localization accuracy, model reliability,
model accuracy, exact mirror-y symmetry, geometry-independent mirror-y rates, or
absolute mass conservation.

In short, seeded-fault and baseline superiority claims remain blocked.
