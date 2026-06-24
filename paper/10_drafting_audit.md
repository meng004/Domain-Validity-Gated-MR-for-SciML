# Drafting Audit for `manuscript/manuscript.md`

> Date: 2026-06-05  
> Draft inspected: `manuscript/manuscript.md` v0.3  
> Purpose: word-count tracking, terminology consistency, and argument-chain audit for the academic-paper plan -> full drafting pass.

## 1. Current Word Count

Total word count: **4,693 words**.

| Section | Current words | Draft target | Status |
|---|---:|---:|---|
| Front matter | 39 | 0-100 | ok |
| Target and Scope | 69 | 50-100 | ok |
| Structured Abstract | 302 | 250-350 | ok |
| Keywords | 17 | 5-10 keywords | ok |
| 1. Introduction | 967 | 1,000-1,400 | near target |
| 2. Background and Related Work | 1,054 | 1,500-2,200 | needs citations and detail |
| 3. Method | 871 | 1,500-2,200 | needs MR-card detail |
| 4. Empirical Design | 794 | 1,200-1,800 | needs protocol tables |
| 5. Results | 59 | blocked | intentionally locked |
| 6. Discussion | 216 | 700-1,100 | wait for evidence |
| 7. Threats to Validity | 157 | 500-800 | needs expansion |
| 8. Conclusion | 57 | 150-250 | wait for evidence |
| References | 50 | final refs later | placeholder |

IST safety target: keep final manuscript under **15,000 words**. Current draft leaves enough space for references, MR tables, experiment protocol, and results.

## 2. Term Consistency

Use these terms consistently:

| Preferred term | Avoid / downgrade | Rationale |
|---|---|---|
| scientific machine learning (SciML) | scientific AI | aligns with field terminology |
| system under test (SUT) | model under test when software context matters | keeps software testing framing |
| metamorphic relation (MR) | metamorphic rule, metamorphic oracle | MR is standard term |
| candidate MR | generated MR | candidate status avoids overclaiming |
| retained MR | valid MR without evidence | retained means passed rubric |
| domain-validity rubric | validity rubric alone when ambiguous | foregrounds physical/numerical boundary |
| NOETHER-informed | NOETHER-guided, NOETHER-proved | avoids implying proof of physical validity |
| executable MR asset | MR idea, test idea | emphasizes auditable implementation |
| relation-level verdict | metric score only | separates test verdict from diagnostic value |
| out-of-relation-domain | invalid result | distinguishes MR misuse from SUT failure |
| rollout-accuracy baseline | accuracy-only superiority contrast | avoids saying MR is better than accuracy |
| MeshGraphNets-family implementations/configurations | three independent SciML systems | external validity is limited |

Current scan status:

- `NOETHER-informed` is used for candidate organization.
- `NOETHER-guided`, `NOETHER proves`, and baseline superiority claims were not used as positive claims.
- LLM role is limited to candidate generation and evidence organization.
- Results are explicitly blocked.

## 3. Argument Chain

Current chain:

1. SciML surrogates reduce simulation cost but create an oracle problem.
2. Rollout accuracy and residual diagnostics are useful but answer a limited question.
3. MT can test necessary relations across executions.
4. In SciML, candidate transformations are unsafe unless their physical and numerical validity conditions are explicit.
5. Existing work already uses physics-based MT for learned physical-field or fluid-velocity predictors, so novelty is not "first physics MR".
6. The remaining gap is the workflow from candidate MR to domain-validity screening to executable asset to relation-level verdict.
7. The proposed method fills that workflow gap for MeshGraphNets-family cylinder-flow surrogates.
8. The empirical study is designed as same-family stress testing, with scoped baselines and evidence-gated claims.

Coherence verdict: **mostly coherent**.

Main remaining weak links:

- Related Work still needs verified citations for Qi/Yu/Gopakumar/Mandrioli and foundational MT.
- Method needs concrete MR-card examples. Without 5-8 cards, the rubric may look abstract.
- Empirical Design needs a table mapping RQs to metrics, baselines, and artifacts.
- Threats to Validity need expansion around same-family SUTs, threshold provenance, and baseline fairness.

## 4. Evidence Gate

Claims allowed in the draft now:

- The paper proposes a domain-validity-aware workflow.
- NOETHER is used as candidate organization, not proof.
- MRs complement rollout accuracy by asking a different validation question.
- The empirical evaluation is planned over MeshGraphNets-family SUTs.
- LLMs are candidate-generation and organization tools only.

Claims still blocked:

- Any pass/fail rate.
- Any fault-detection rate.
- Any superiority over baselines.
- Any localization accuracy.
- Any claim that one SUT is more reliable than another.
- Any generalization to all neural fluid surrogates or all SciML systems.

## 5. Next Drafting Tasks

1. Add verified citations and citation keys.
2. Draft 5-8 MR cards in a table or appendix-style subsection.
3. Add an RQ-to-metric-to-artifact table.
4. Expand Threats to Validity.
5. Create a reference ledger before writing final Related Work paragraphs.

## 6. IST Template Migration Status

Updated on 2026-06-05.

- Official Elsevier `elsarticle` template package was downloaded from Elsevier and stored under `paper/ist-template/`.
- The working IST-format manuscript is now `submissions/IST/main.tex`.
- The compiled draft is `submissions/IST/main.pdf`.
- The draft uses `\documentclass[preprint,12pt,authoryear]{elsarticle}` and `\journal{Information and Software Technology}`.
- The local TeX installation did not include `elsarticle.cls`; it was generated from the official `elsarticle.dtx` and `elsarticle.ins` files.
- Full LaTeX/BibTeX compilation succeeded with writable TeX cache variables.
- Current PDF length: 21 pages.
- Approximate stripped-source word count: 4206 words.
- Remaining technical issues: overfull/underfull box warnings from long terms and dense tables.
- Remaining scholarly issues: several 2025/2026 bibliography entries still need final metadata verification before submission.

Evidence gate remains unchanged: no empirical result claims should be added until executable MR cards, SUT configurations, run logs, and experiment ledgers exist.
