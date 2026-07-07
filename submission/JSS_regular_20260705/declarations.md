# Submission declarations

## CRediT author statement

Meng Li: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing - original draft, Writing - review and editing, Visualization.

Xiaohua Yang: Supervision, Conceptualization, Methodology, Writing - review and editing.

Jie Liu: Methodology, Validation, Writing - review and editing.

Shiyu Yan: Methodology, Software, Validation, Writing - review and editing.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Generative-AI usage declaration

During preparation of this work, the authors used AI-assisted tools for language editing, consistency checks, and manuscript-organization support. The authors reviewed and edited all AI-assisted output and take full responsibility for the content of the published article.

## Data and code availability

The replication package is archived on Zenodo at https://doi.org/10.5281/zenodo.20702952 and the source repository is https://github.com/meng004/Domain-Validity-Gated-MR-for-SciML. The package includes MR cards, execution manifests, verdict ledgers, validation scripts, regression tests, manuscript source, and committed derived evidence under `research_assets/runs/`. The evidence boundary is enforced by `research_assets/experiments/claim-ledger.yml` and fail-closed validators.

External inputs that are not redistributed are identified by source and provenance rather than implied to be bundled: the DeepMind cylinder-flow and airfoil TFRecords are public benchmark inputs staged by the workflow runners, and the read-only Minimum-MR-SubSet evidence is referenced by repository commit `9ef862ec37335b4834d0a1fb38b4b613af702f34`. GPU-dependent or credential-dependent reruns are documented in `REPRODUCIBILITY.md`; absence of those credentials causes the precondition gates to fail closed. The paper does not claim results beyond the committed evidence licensed by those artifacts.

## Evidence boundary

The paper claims an auditable admissibility and numerical-decidability workflow for SciML metamorphic testing. It does not claim general SciML reliability, baseline superiority, arbitrary-mesh soundness, real-world defect-detection rates, or broad neural-operator generalization.
