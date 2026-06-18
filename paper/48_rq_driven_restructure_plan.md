# 48 — RQ-Driven Manuscript Restructuring Plan for IST

> Date: 2026-06-18  
> Target manuscript: `paper/ist-submission/main.tex`  
> Target venue: Elsevier *Information and Software Technology* (IST), regular research paper  
> Purpose: record the revised research questions and use them to guide a chapter-by-chapter restructuring of the manuscript.  
> Scope: planning document only. It does not edit the submitted LaTeX manuscript and does not generate new figures.

## 1. Restructuring Rationale

The current manuscript has strong evidence assets: a domain-validity rubric, MR cards, executable runners, relation-level ledgers, an operator-floor argument, typed verdicts, bounded SciML case-study evidence, and fault-coverage stress tests. However, the current research question still reads as a candidate-screening and conversion question:

> How can candidate metamorphic relations for scientific-machine-learning systems be screened for domain validity and converted into executable oracle-free test assets without relying on exact per-sample expected outputs?

That question is valid, but for IST it underplays the strongest software-engineering contribution. IST reviewers need to see reusable software V&V knowledge: how a testing method turns implicit domain assumptions into auditable executable artifacts, and how its verdicts remain interpretable when a relation is invalid, outside its domain, or numerically undecidable.

The restructured paper should therefore move the center of gravity from:

> screening candidate MRs

to:

> constructing auditable, executable, and interpretable oracle-free V&V assets for SciML surrogate software.

The validity--coverage duality should remain in the paper, but as a derived implication and bounded stress-test result rather than the sole central claim. This reduces the risk that reviewers read it as tautological while preserving the paper's strongest insight: admissibility constrains both valid verdicts and detectable fault classes.

## 2. Final Research Questions

### Main Research Question

**RQ0. How can physics-derived metamorphic relations for scientific-machine-learning surrogate software be transformed into auditable, executable, and interpretable oracle-free V&V assets, while distinguishing genuine SUT inconsistency from relation invalidity and numerical measurement limits?**

### 中文解释

如何将面向 scientific-machine-learning surrogate software 的物理启发式 metamorphic relations，转化为可审计、可执行、可解释的 oracle-free V&V 测试资产，并在测试结果中区分真实 SUT inconsistency、关系本身不适用以及数值测量下限造成的不可判定性？

### Sub-Questions

**RQ1 — Admissibility.** What validity conditions determine whether a physics-derived candidate MR is admissible as an oracle-free test for a specific SciML surrogate SUT?

**RQ2 — Asset Construction.** How can admissible MRs be represented as reusable MR cards and executable test assets with explicit transformations, mappings, metrics, tolerances, exclusions, and evidence records?

**RQ3 — Verdict Interpretation.** How can relation-level verdicts separate SUT inconsistency from out-of-relation-domain application, numerical tolerance limits, and inconclusive evidence?

**RQ4 — Empirical Utility.** In bounded SciML surrogate case studies, what evidence does the validity-gated workflow provide beyond rollout accuracy, generic MR generation, and LLM-assisted candidate elicitation?

### Discussion Implication, Not a Formal RQ

**Coverage implication.** The admissible MR set can be used to interpret the test suite's fault-coverage boundaries and blind spots in the studied settings.

This is deliberately **not** a formal research question. It should appear in Results Analysis and Discussion as a bounded implication of RQ1--RQ4, not as a central thesis. This decision reduces the risk that reviewers read the validity--coverage argument as over-framed or tautological.

## 3. Why These Questions Fit IST

| IST expectation | RQ-driven response | Manuscript implication |
|---|---|---|
| Software testing / V&V contribution | RQ0 frames the contribution as oracle-free V&V asset construction, not CFD modeling. | Introduction and Method must foreground software testing artifacts and verdict interpretability. |
| Reusable engineering knowledge | RQ1--RQ3 define reusable gates, MR cards, and verdict classes. | Method section must read as a transferable workflow, not a one-off case-study recipe. |
| Empirical validation | RQ4 asks what bounded case-study evidence the workflow adds beyond alternatives. | Empirical Design and Results must keep denominator boundaries explicit. |
| Theory without overclaiming | Coverage is downgraded from formal RQ to discussion implication. | Discussion should present validity--coverage as a scoped implication with refutation conditions, not as a primary claim. |
| Practical relevance | RQ2 and RQ3 produce artifacts practitioners can inspect and rerun. | Figures and tables should make the asset workflow and verdict logic visible at a glance. |

## 4. Contribution Reframing

The revised contribution hierarchy should be:

1. **Primary contribution: validity-gated V&V asset construction.** The paper shows how physics-derived MRs become auditable, executable, oracle-free testing assets.
2. **Second contribution: measurement-floor admissibility.** A relation is only admitted when its verdict tolerance dominates the measurement operator's intrinsic numerical floor.
3. **Third contribution: typed relation-level verdicts.** The verdict separates SUT inconsistency, relation invalidity, out-of-domain application, numerical-floor deferral, and inconclusive evidence.
4. **Fourth contribution: bounded empirical utility.** The case studies show what evidence this workflow adds beyond rollout accuracy, generic MR generation, and LLM-assisted MR elicitation.
5. **Derived implication, not formal RQ: admissibility shapes coverage.** The admissible MR set helps explain fault-coverage boundaries and blind spots in the studied settings.

This hierarchy is safer than making validity--coverage duality the main novelty. It gives IST reviewers a concrete software-engineering method first, then a bounded theoretical implication.

## 5. RQ-to-Section Traceability

| RQ | Primary section | Supporting section | Evidence artifacts | Must not claim |
|---|---|---|---|---|
| RQ0 | Introduction, Method | Discussion | Full workflow, MR cards, ledgers | General SciML reliability |
| RQ1 | Method | Related Work, Results | `domain_validity_rubric.json`, operator-floor sweep | Physical validity proof for all MRs |
| RQ2 | Method | Empirical Design | MR cards, runners, manifests, metric ledgers | Complete automation of MR discovery |
| RQ3 | Method, Results | Discussion | two-dimensional verdict plot, verdict tables | Cross-relation calibrated domain score |
| RQ4 | Empirical Design, Results | Discussion | rollout baseline, LLM/generic baselines, MGN/FNO/PINN evidence | Baseline superiority |
| Coverage implication | Results Analysis and Discussion | Threats to Validity, Future Work | seeded-fault catalogues, airfoil transfer, cross-program checks | Real-world defect detection rate |

## 6. Proposed Manuscript Structure

Use a conventional IST-friendly structure:

1. Introduction
2. Related Work
3. Method
4. Experimental Design
5. Results Analysis and Discussion
6. Threats to Validity
7. Future Work
8. Conclusion

This structure separates method, experiment, interpretation, threats to validity, and future work. It also reduces the current risk that Results and Discussion blend too much, and that boundary statements interrupt the main argument. The title **Threats to Validity** is preferred because it matches empirical software-engineering convention for IST-style papers. Method and artifact limitations should be included inside the relevant validity categories rather than promoted to a separate title.

## 7. Chapter-by-Chapter Restructuring Plan

### 7.1 Introduction

**Goal.** Establish the software testing problem, state the revised RQ set, and explain why IST readers should care.

**Reader takeaway.** SciML surrogate software faces an oracle problem, but the harder testing issue is not just missing expected outputs. Physics-derived MRs must themselves be validated, made executable, and interpreted under numerical limits.

**Required content.**

- Start from software V&V, not CFD or neural architectures.
- Introduce the ambiguity of MR verdicts: SUT failure vs invalid relation vs numerical-floor issue.
- Present RQ0 and RQ1--RQ4.
- Reframe contributions around auditable executable V&V assets.
- State the evidence boundary early: bounded case studies, not general reliability or baseline superiority.

**Acceptance criteria.**

- A software testing reviewer can identify the paper's SE contribution by the end of page 2.
- RQ0 includes auditable, executable, interpretable, oracle-free V&V assets.
- Validity--coverage duality appears only after the primary method contribution is clear.
- No sentence implies general SciML reliability or model superiority.

**Figures and tables.**

| Item | Type | Use | Action |
|---|---|---|---|
| Table I: RQs, contributions, evidence | Table | Maps each formal RQ to contribution and evidence section. | Add or adapt current `Research questions, efficacy parameters, baselines, and artifacts` table; keep coverage as a discussion implication row, not a formal RQ. |
| No figure required | -- | Introduction should stay lean. | Avoid adding a concept figure here unless the RQ map is hard to follow. |

### 7.2 Related Work

**Goal.** Position the paper against MT, MR identification, physics-based testing of surrogates, relaxed oracles, constraint-based inapplicability handling, residual/UQ monitoring, and executable research artifacts.

**Reader takeaway.** Existing work supplies pieces: MR identification, physics-derived MRs, relaxed thresholds, bug-vs-inapplicability constraints, residual/UQ diagnostics. None combines admissibility, measurement-floor tolerance, executable MR assets, typed verdicts, and artifact-backed SciML evidence.

**Required content.**

- Organize by problem relation, not by chronology.
- Closest-prior paragraph must explicitly answer: what is already known, what remains unsolved, what this paper adds.
- Residual/UQ/rollout accuracy should be framed as complementary diagnostics, not defeated baselines.
- LLM MR generation should be treated as a candidate source, not a validity authority.

**Acceptance criteria.**

- Each closest prior is connected to exactly one missing capability.
- The related-work table does not overstate first-use claims.
- The paper's gap is stated as executable, validity-gated V&V asset construction.

**Figures and tables.**

| Item | Type | Use | Action |
|---|---|---|---|
| Table II: Closest-prior capability matrix | Table | Shows admissibility filter, floor-grounded tolerance, executable assets, typed verdict, coverage implication. | Keep current closest-prior table, but add `Executable evidence assets` as a column if word budget allows. |
| No new figure | -- | Related work is better handled by a compact matrix. | Do not add decorative taxonomy figure. |

### 7.3 Method

**Goal.** Present the transferable method that answers RQ1--RQ3: admissibility gate, MR-card asset construction, execution pipeline, evidence ledger, and typed verdict interpretation.

**Reader takeaway.** The method is a reusable V&V workflow: a candidate MR becomes a test asset only after passing explicit admissibility conditions and being encoded into executable artifacts with traceable verdict evidence.

**Required content.**

- Define the four admissibility conditions: physical/software basis, preconditions, boundary/output mapping compatibility, numerical decidability.
- Explain measurement-floor admissibility as a method principle, not only a cylinder-flow fact.
- Define MR card fields and how they become executable assets.
- Define relation-level verdict classes and the two-axis interpretation.
- Explain the evidence ledger as part of the method, not only replication packaging.

**Acceptance criteria.**

- RQ1, RQ2, and RQ3 are fully answerable from this section without reading Results.
- Each method component has a corresponding artifact field or output.
- The reader can trace candidate -> admitted/deferred/rejected -> executable asset -> metric -> verdict -> ledger.
- The method does not imply automatic MR discovery or universal physical validity.

**Figures and tables.**

| Item | Type | Use | Action |
|---|---|---|---|
| Fig. 1: Validity-gated V&V workflow | Flowchart | Shows candidate -> admissibility gate -> MR card -> executable run -> verdict ledger. | Keep current workflow figure, retitle toward V&V assets. |
| Fig. 2: MR-card-to-executable data flow | Architecture/data-flow diagram | Shows source/follow-up execution, mapping, metric, exclusion, verdict ledger. | Keep current asset-flow figure. |
| Fig. 3: Verdict space | Conceptual/data plot | Shows SUT inconsistency vs out-of-domain vs numerical deferral. | Keep current two-dimensional verdict figure, but ensure caption is shorter and less overloaded. |
| Table III: Admissibility gate and verdict semantics | Table | Defines the gate criteria, MR-card essentials, and allowed verdict interpretations. | Merge the current admissibility rubric, MR-card schema, and verdict taxonomy into one compact method table. |

### 7.4 Experimental Design

**Goal.** Explain how the method is evaluated against RQ4 under bounded, auditable conditions, while preparing the evidence needed for the later coverage implication.

**Reader takeaway.** The experiments are not a model benchmark. They test whether the validity-gated workflow produces interpretable verdicts and executable evidence across selected SciML surrogate settings; fault-coverage interpretation is a bounded discussion implication.

**Required content.**

- State evaluation objectives by RQ, not only by dataset/SUT.
- Separate primary evidence, transfer checks, stress tests, and secondary baselines.
- Define units of analysis and denominators: checkpoint, trajectory, frame, transition, mutant, MR.
- Explain why rollout accuracy, generic MR generation, and LLM MR generation are contextual baselines rather than competitors.
- State all claim boundaries before Results.

**Acceptance criteria.**

- Every experiment maps to at least one RQ.
- Every numeric denominator has a traceable artifact.
- The section makes clear which evidence is primary, supporting, secondary, or stress-test only.
- No baseline is framed as defeated unless the evidence supports direct comparison.

**Figures and tables.**

| Item | Type | Use | Action |
|---|---|---|---|
| Table IV: Evaluation design by research question | Table | Maps RQ, evaluation question, SUT/data, metric, artifact, and claim boundary. | Merge the RQ-to-experiment matrix with evidence tiers and claim boundaries. |
| Optional Fig. 4: Experiment portfolio map | Flow/graph | Shows primary cylinder-flow, second CFD task, FNO/PINN, baselines, cross-program checks. | Add only if Results feels hard to navigate; otherwise table is enough. |

### 7.5 Results Analysis and Discussion

**Goal.** Present results by RQ, interpret what they show, and connect findings back to IST-level contribution.

**Reader takeaway.** The workflow produces interpretable verdicts and auditable evidence beyond rollout accuracy, while its coverage boundaries follow from which MRs are admissible in the studied settings.

**Required content.**

- Organize results by RQ or by claims, not by historical experiment phase.
- For RQ1/RQ3: show different admissibility outcomes across node permutation, mirror-y, conservation, airfoil.
- For RQ2: show that MR cards and ledgers produce reproducible artifacts.
- For RQ4: compare evidence added beyond rollout accuracy and candidate baselines.
- Present coverage implication as bounded, qualitative, and stress-test supported, but not as a formal RQ result.
- Move broader interpretation into the same section only after results are shown.

**Acceptance criteria.**

- Each subsection starts with the RQ it answers.
- Each result states its evidence boundary in the same paragraph or table row.
- Coverage discussion never becomes a real-world defect-rate claim.
- Validity--coverage is described as an implication of admissibility, not as an independent universal theory.

**Figures and tables.**

| Item | Type | Use | Action |
|---|---|---|---|
| Table V: MR-to-verdict and evidence summary | Table | Main result table showing admitted/deferred/rejected, verdict meaning, and evidence source. | Keep current MR-card-to-verdict content but align rows to RQ1/RQ3 and compress artifact detail. |
| Fig. 4: Operator-floor calibration | Data plot | Shows O(h) floor and why absolute conservation is deferred. | Current figure count suggests this may already be present or should be restored if missing. |
| No main-text coverage table by default | -- | Coverage belongs in discussion prose or appendix after RQ5 is downgraded. | Move detailed fault-class coverage matrix to appendix if needed. |
| No main-text coverage figure by default | -- | Avoid adding Fig. 5 under the 4-figure hard constraint. | Use prose plus existing verdict/evidence tables. |

### 7.6 Threats to Validity

**Goal.** Separate validity threats from discussion, using empirical software-engineering terminology while making the evidence boundary credible.

**Reader takeaway.** The authors understand which factors threaten construct, internal, external, and conclusion validity, including method and artifact limitations.

**Required content.**

- Construct validity: MR validity depends on physical assumptions, operators, and thresholds.
- Internal validity: SUT setup, checkpoints, seeds, preprocessing.
- External validity: two CFD tasks, bounded surrogate families, secondary cross-program checks.
- Conclusion validity: non-independent cells, small mutant catalogue, descriptive rates.
- Method and artifact threats: MR-card workflow is not automatic MR discovery; claim ledgers improve auditability but do not prove physical correctness.
- AI/tooling validity: LLM candidate generation and AI-assisted writing are not evidence authorities.

**Acceptance criteria.**

- Every limitation connects to a claim boundary.
- The limitation section does not introduce new results.
- The language distinguishes "not supported" from "false".
- Mutant catalogue is explicitly stress-test evidence, not real-world defect-rate evidence.

**Figures and tables.**

| Item | Type | Use | Action |
|---|---|---|---|
| No main-text table by default | -- | Threats should be concise prose organized by validity category. | Use a short boundary paragraph; keep the full claim-to-evidence map in the appendix. |
| No figure | -- | Threats and limitations should be direct prose. | Do not add a conceptual figure. |

### 7.7 Future Work

**Goal.** Turn limitations into a research agenda without weakening current claims.

**Reader takeaway.** Future work is not needed to make the current contribution valid, but is needed for broader applicability, calibrated scores, and real-world defect-rate evidence.

**Required content.**

- Cross-relation calibration of domain-violation scores.
- Broader SUT families, datasets, and converged production checkpoints.
- Independent real-world defect corpora or externally sourced mutants.
- Larger comparative studies against residual/UQ/accuracy monitors.
- Tooling for MR-card authoring and validation.

**Acceptance criteria.**

- Future work follows directly from limitations.
- No current conclusion depends on future work.
- The agenda is framed as extension, not repair.

**Figures and tables.**

| Item | Type | Use | Action |
|---|---|---|---|
| No main-text table by default | -- | Future work should be short and tied to validity threats. | Avoid a roadmap table unless reviewers explicitly ask for one. |

### 7.8 Conclusion

**Goal.** Close with the method contribution, bounded evidence, and practical implication.

**Reader takeaway.** The paper contributes a practical software V&V workflow for turning physics-derived MRs into auditable executable tests with interpretable verdicts; it does not claim broad reliability or superiority.

**Required content.**

- One paragraph answering RQ0.
- One paragraph summarizing evidence by RQ.
- One paragraph stating practical implication for SciML surrogate testing.
- One sentence preserving boundary.

**Acceptance criteria.**

- Conclusion does not introduce new numbers not already in Results.
- The last claim is methodological, not model-reliability.
- Validity--coverage is mentioned only as a bounded implication, if at all.

**Figures and tables.**

No figure or table. The conclusion should be clean and short.

## 8. Recommended Figure and Table Portfolio

The main text should not use every possible table listed during planning. The target portfolio is a hard constraint: **4 figures + 5 tables**. This is both a readability decision and a word-budget decision: IST counts every figure and table as 200 words, so reducing unnecessary floats directly protects the 15,000-word cap.

### Main-Text Figures

| Figure | Title | Section | Necessity | Tool | Purpose |
|---|---|---|---|---|---|
| Fig. 1 | Validity-gated V&V workflow | Method | High | Mermaid/draw.io | Shows the full candidate-to-verdict pipeline. |
| Fig. 2 | MR-card-to-executable asset data flow | Method | High | Mermaid/draw.io | Shows how MR cards become runs, metrics, verdicts, and ledgers. |
| Fig. 3 | Two-dimensional verdict space | Method/Results | High | matplotlib | Makes verdict interpretation visible. |
| Fig. 4 | Operator-floor calibration | Results | High | matplotlib | Justifies numerical decidability and conservation deferral. |
| No Fig. 5 in main text | Coverage geometry matrix | Appendix/prose only | -- | -- | Coverage is now a discussion implication; do not add a fifth main-text figure. |

Required default: **4 main-text figures**. Any coverage geometry visualization should be appendix-only unless a later reviewer explicitly requests it.

### Main-Text Tables

| Table | Title | Section | Purpose |
|---|---|---|---|
| Table I | RQs, contributions, evidence | Introduction | Locks the paper's argument around RQ0--RQ4 and notes coverage as a discussion implication. |
| Table II | Closest-prior capability matrix | Related Work | Shows why the contribution is not merely prior-work repetition. |
| Table III | Admissibility gate and verdict semantics | Method | Merges the rubric, MR-card essentials, and verdict taxonomy for RQ1--RQ3. |
| Table IV | Evaluation design by research question | Experimental Design | Merges RQ-to-experiment mapping with evidence tiers and claim boundaries. |
| Table V | MR-to-verdict and evidence summary | Results | Main empirical verdict table for RQ1--RQ4. |
| Appendix Table A1 | Claim-to-evidence map | Appendix | Full artifact traceability. |

Required default: **5 main-text tables**. The full claim-to-evidence table and any detailed coverage/blind-spot matrix belong in the appendix, not the main text. Do not add a future-work table unless reviewers request it.

### Tables to Merge or Move

| Original planning item | Revised handling | Reason |
|---|---|---|
| Separate MR-card schema table | Merge into Table III | The schema is important, but a standalone table reads like documentation rather than an IST article. |
| Separate verdict taxonomy table | Merge into Table III | Verdict semantics belong next to the admissibility gate. |
| Separate evidence-tier table | Merge into Table IV or move to appendix | Evidence tiers prevent overclaiming but should not interrupt the experimental design. |
| Empirical utility beyond baselines table | Fold into Table IV or Table V | Baselines are scope contrasts, not a full competitive evaluation. |
| Future-work roadmap table | Remove from main text | Future work should be concise prose. |
| Coverage implication table | Move to appendix or prose | RQ5 is downgraded, so coverage no longer needs a main-text table. |

## 9. Proposed Section-Level Acceptance Checklist

Before rewriting the manuscript, each section should pass these checks:

1. **RQ visibility.** The section clearly answers at least one RQ.
2. **IST relevance.** The section speaks to software testing/V&V, not only SciML physics.
3. **Evidence traceability.** Every result claim maps to an artifact or ledger.
4. **Boundary discipline.** No reliability, superiority, or real-world defect-rate claim appears without support.
5. **Reader economy.** Defensive caveats are consolidated into tables or boundary paragraphs, not scattered through every sentence.
6. **Duality control.** Validity--coverage is a bounded implication, not the primary burden of novelty.

## 10. Implementation Order

1. **Rewrite Introduction around RQ0--RQ4.** This fixes the paper's contract with the reader.
2. **Revise Related Work to support the gap.** The closest-prior matrix should match the new RQ structure.
3. **Rebuild Method as the answer to RQ1--RQ3.** This should become the paper's core IST contribution.
4. **Rebuild Experimental Design around RQ4.** Use RQ-to-experiment mapping to prevent phase-history narration; keep coverage as a planned discussion implication.
5. **Reorganize Results by RQ.** Avoid chronological accumulation of experiments.
6. **Split Discussion, Threats to Validity, and Future Work.** Discussion interprets; threats bound; future work extends.
7. **Shorten Conclusion.** Answer RQ0 and preserve boundaries.

This order matters because changing Results before changing the RQs would preserve the current rhetorical imbalance. The paper needs a new argument spine first.
