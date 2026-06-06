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
| PC1-domain-validity-rubric | Supported as method/design claim | The paper proposes a domain-validity rubric that screens candidate MRs before execution. | `research_assets/rubric/domain_validity_rubric.json`; `paper/manuscript.md`; `paper/ist-submission/main.tex` | The rubric proves physical validity or replaces domain expertise. |
| PC2-mr-card-executable-assets | Supported as asset/workflow claim | Retained candidates are represented as MR cards and executable assets with transformations, metrics, tolerances, exclusions, and verdicts. | `research_assets/mr_cards/`; `tools/validate_research_assets.py`; `paper/manuscript.md` | Every card has cross-SUT empirical evidence. |
| PC3-baseline-comparison-blocked | Blocked | Baselines are protocol commitments only: expert MR design, generic MR-generation scope contrast, LLM candidates, and rollout accuracy diagnostics. | `research_assets/experiments/claim-ledger.yml`; `research_assets/experiments/experiment-ledger.yml` | Seeded-fault and baseline superiority claims remain blocked; no superiority, fault-detection, localization, or runtime claim is supported. |
| PC4-node-permutation-sanity | Observed pilot | Node-permutation equivariance holds to machine precision for one real trained MeshGraphNets cylinder-flow surrogate and one pilot case; this is a structural sanity check. | `research_assets/runs/real-sut-node-permutation-pilot/raw/metric_ledger.json`; `claim-ledger.yml` | The SUT passes node permutation in general, or model reliability has been established. |
| PC5-conservation-diagnostic-deferred | Observed diagnostic, absolute claim deferred | The absolute conservation relation remains deferred because the discrete divergence operator gives non-negligible reference divergence; a reference-relative diagnostic passes on recorded frames. | `research_assets/runs/conservation-diagnostic-pilot/raw/metric_ledger.json`; `research_assets/runs/conservation-diagnostic-pilot/raw/conservation_report.json`; `claim-ledger.yml` | Absolute conservation remains deferred; do not claim exact divergence-free behavior, conservation rate, or model reliability. |
| PC6-mirror-y-ood-stress | Observed bounded pilot | Exact mirror-y is out-of-relation-domain for this mesh and is downgraded to an approximate OOD-stress probe; it failed on 10 of 10 recorded eval frames, with median relative L2 0.737 and median V/floor 3.96. | `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json`; `research_assets/runs/mirror-y-rate-upgrade/manifest.yml`; `claim-ledger.yml`; `experiment-ledger.yml` | This is not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim. |
| PC7-llm-candidate-support-only | Supported as process boundary | LLM use is restricted to candidate generation and material organization; it does not judge MR validity. | `paper/manuscript.md`; `paper/ist-submission/main.tex`; method and ethics sections | LLMs automatically identify valid SciML MRs. |
| PC8-rollout-accuracy-diagnostic | Observed | On the same eval trajectory the surrogate's one-step accuracy is median relative L2 0.0216; the mirror-y violation (0.737) is ~34x larger. | `research_assets/runs/rollout-accuracy-baseline/raw/metric_ledger.json`; `claim-ledger.yml` (C8) | A baseline-superiority, multi-trajectory, cross-SUT, or reliability claim. |
| PC9-exact-mirror-y-symmetric-mesh | Observed | On a provably symmetric mesh the exact mirror-y relation is admissible and the surrogate fails it (relative L2 1.10), removing the out-of-relation-domain objection. | `research_assets/runs/mirror-y-symmetric-mesh/raw/metric_ledger.json`; `claim-ledger.yml` (C9) | An accuracy, reliability, cross-SUT, multi-input, or cylinder-flow-geometry claim (the mesh is synthetic, no-obstacle, OOD). |

The `PC#` identifiers are paper-level claims and are intentionally distinct from the authoritative runtime claim ledger so the two cannot be confused. The runtime claim ledger (`research_assets/experiments/claim-ledger.yml`, claims `C1-fixture-asset-path` … `C7-conservation-diagnostic`) is the single source of truth for runtime-evidence claims. Mapping: PC1→C4, PC2→C1/C4, PC3→C3, PC4→C2, PC5→C7, PC6→C6, PC7→none (method/ethics boundary); the ledger `C5-precondition-check` underlies the precondition gate.

## Numeric Claim Trace

| Number or phrase | Permitted location | Evidence |
|---|---|---|
| `relative L2 = 0.0` | Node-permutation pilot result | `research_assets/runs/real-sut-node-permutation-pilot/raw/metric_ledger.json` |
| `failed on 10 of 10 recorded eval frames` | Mirror-y bounded OOD-stress result | `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json` |
| `median relative L2 0.737` | Mirror-y bounded OOD-stress result | `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json` |
| `median V/floor 3.96` | Mirror-y bounded OOD-stress result | `research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json` |
| `one SUT, one checkpoint, one MR, one eval trajectory` | Mirror-y claim boundary | `research_assets/experiments/claim-ledger.yml`; `experiment-ledger.yml` |
| `absolute conservation remains deferred` | Divergence/conservation diagnostic | `research_assets/runs/conservation-diagnostic-pilot/raw/conservation_report.json`; `claim-ledger.yml` |
| `median relative L2 0.0216` (rollout accuracy; mirror-y ~34x) | Rollout-accuracy diagnostic | `research_assets/runs/rollout-accuracy-baseline/raw/metric_ledger.json` |
| `relative L2 1.10` (exact mirror-y fail, symmetric admissible mesh) | Exact mirror-y symmetric-mesh run | `research_assets/runs/mirror-y-symmetric-mesh/raw/metric_ledger.json` |

## Integrity Verdict

The current manuscript can claim a method workflow plus three minimal within-SUT
pilot outcomes. It cannot claim cross-SUT generality, seeded-fault effectiveness,
baseline superiority, runtime advantage, localization accuracy, model reliability,
model accuracy, exact mirror-y symmetry, geometry-independent mirror-y rates, or
absolute mass conservation.

In short, seeded-fault and baseline superiority claims remain blocked.
