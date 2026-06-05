# IST/v2.2 论文结构与证据地图

> Target: Information and Software Technology (IST), regular research paper track.
> IST MT special issue is closed; cite it only as community-fit evidence, not as an available submission channel.
> Evidence gate: Results, detection rates, significance claims, failure signatures, and comparative superiority remain BLOCKED until actual experiment artifacts exist.

## 1. Target Article Shape

IST-facing article type:

**Software testing / V&V method paper with empirical validation and open reproducibility assets.**

Frame the paper as:

**a validity-rubric-first, NOETHER-informed, executable oracle-free MR testing framework for mesh-based neural cylinder-flow surrogates, evaluated across three MeshGraphNets-family implementations/configurations with baselines, seeded faults/mutations, statistical tests, and MetBench assets.**

Do not frame it as:

- a CFD solver paper;
- a new GNN architecture paper;
- a pure NOETHER theory paper;
- a MetBench engineering report;
- a submission to the closed IST MT special issue;
- a results paper before experiments exist.

Structured abstract must use IST-friendly fields:

| Field | Content boundary |
|---|---|
| Context | Oracle problem in testing scientific ML / mesh-based neural surrogates |
| Objective | Identify and operationalize physically valid MRs as executable oracle-free tests |
| Method | Validity rubric, NOETHER-informed candidate generation, hierarchical localization protocol, three-implementation empirical protocol |
| Results | BLOCKED until actual run tables, mutation evidence, and statistics exist |
| Conclusions | Only evidence-bounded claims; no generalization beyond observed artifacts |

## 2. Accepted Contribution Order

Main claim:

> A physical MR for scientific ML testing is publishable only when it is physically valid, executable, threshold-interpretable, diagnosable, and reproducible; NOETHER can guide candidate generation, but IST value comes from the software testing framework, empirical validation, and open assets.

| Contribution | Paper role | Evidence required |
|---|---|---|
| C1. Validity rubric | Headline contribution; separates valid MRs from executable but invalid/OOD transformations | Criteria, reject examples, MR cards, threshold semantics |
| C2. NOETHER-informed executable oracle-free MR framework | Uses NOETHER to organize candidate relation structures, then maps rubric-accepted relations into executable MR verdicts | A_cyl definition, block assignment table, curation preconditions, Translate-to-MetBench mapping, verdict schema |
| C3. Hierarchical failure localization protocol | Organizes MRs into a tree that can map violations to representation, physical-model, temporal, cross-SUT, or implementation layers once seeded-fault evidence exists | MR tree, layer-to-fault-class mapping, localization protocol, top-k/layer agreement metric |
| C4. Three-implementation empirical evaluation and reproducible MetBench assets | IST empirical validation within the MeshGraphNets-family cylinder-flow scope and open-science package | SUT adapters, comparability protocol, baselines, seeded faults/mutations, stats scripts, run artifacts, Zenodo/GitHub package |

## 3. v2.1 Theory Guardrails

| Topic | Accepted v2.1 stance | Paper action |
|---|---|---|
| Divergence | Divergence-free behavior is an incompressible-flow continuity / mass constraint, not a Noether conservation law | Never write "Noether-derived mass conservation"; use divergence MR as a continuity-constraint MR and possible constraint-block witness |
| Time reversal | Viscous N-S dynamics are not time-reversal valid for this domain | Exclude time-reversal MR explicitly; use the exclusion as a validity-rubric example |
| Rollout MRs | Prefix consistency and determinism belong to qualitative-dynamics / semigroup behavior | Do not attach rollout MRs to time-reversal block |
| N-S symmetries | Classical Lie point symmetries are prior domain knowledge | State that NOETHER consumes classical N-S symmetries as symmetry-block inputs; do not claim it discovers them |
| Symmetry block | Symmetry MRs must be boundary-condition compatible | Include BC-compatible subgroup selection for mirror, translation, scaling, and similarity candidates |
| NOETHER dependency | Downstream construction is conditional on upstream domain curation | Do not imply NOETHER proves physical validity; make operator-algebra curation and rubric filtering explicit |
| Method comparison | Cross-SUT agreement is conditional, not automatically an MR | Require matched cases, units, fields, rollout horizons, boundary conditions, and tolerances before retaining it as an MR |
| Baselines | Generic/LLM baselines can become strawmen | Treat generic tools as scope-contrast baselines; preserve prompts, versions, candidates, and rubric decisions |
| Non-symmetry blocks | IST contribution must not collapse into symmetry-only testing | Emphasize order, limit, qualitative-dynamics, method-comparison, relational-equivalence, and constraint-style candidates |
| Executability | Candidate patterns are not enough | Every retained MR needs transform, metric, threshold, verdict, failure signature, and reproducibility record |

## 4. IST Section Outline

### 1. Introduction

- Present oracle-free testing of scientific ML surrogates as a software engineering / V&V problem.
- Position MT as relational oracle construction, with MR validity as the bottleneck.
- State why mesh-based cylinder-flow surrogates need physically grounded yet executable MRs.
- Mention IST MT activity only as community-fit evidence; regular track is the target.
- Contributions appear in C1 -> C2 -> C3 -> C4 order.

### 2. Background and Related Work

- Test oracle problem and metamorphic testing.
- MR identification/generation: MRP/MROP, MR-Scout, GenMorph, LLM workflows, and recent MR generation roadmaps.
- Scientific software testing, simulation V&V, and scientific ML testing.
- MeshGraphNets and cylinder-flow surrogate modeling.
- Classical N-S Lie symmetries, continuity constraints, and why divergence is not a Noether conservation-law claim.
- NOETHER and hierarchical MR classification as theory inputs, written self-contained enough for IST review.

### 3. Validity Rubric for Physical MRs

Contribution C1 section.

Rubric dimensions:

- physical validity;
- semantic preservation under domain and boundary conditions;
- measurable output relation;
- threshold interpretability;
- executable oracle-free verdict;
- failure diagnosability;
- reproducibility and asset completeness.

Required examples:

- accepted: BC-compatible mirror equivariance, graph permutation equivariance, rollout prefix consistency;
- qualified: scaling / Re-St similarity only under nondimensional and data-regime compatibility;
- rejected: time-reversal MR for viscous cylinder flow;
- corrected: divergence as continuity constraint, not Noether law.

### 4. NOETHER-Informed Executable MR Framework

Contribution C2 section.

- Define the cylinder-flow program-induced operator algebra A_cyl.
- Assign operators to NOETHER blocks, recording unassigned or constraint-like candidates honestly.
- Explain how classical N-S Lie symmetries enter the symmetry block as curated inputs, and state that physical validity is decided by the rubric rather than by NOETHER alone.
- Emphasize non-symmetry blocks: qualitative dynamics, method comparison, order/limit relations, relational equivalence, and constraints.
- Translate MetaPatterns into MetBench-style assets: case JSON, source/follow-up transform, runner, parser, metric, threshold, verdict.

### 5. Hierarchical Failure Localization

Contribution C3 section.

- Build MR tree by layer: representation/preprocessing, physical model, temporal rollout, cross-SUT method comparison, implementation/runtime.
- Map each MR family to plausible fault classes and diagnosis evidence.
- Treat divergence MR as a continuity-constraint witness and possible feedback to NOETHER block coverage.
- Define what counts as localization evidence before Results are written.

### 6. Empirical Evaluation Design

Contribution C4 protocol section.

- RQs/hypotheses: validity coverage, fault/mutation detection, baseline comparison, localization utility, reproducibility.
- SUT matrix: three MeshGraphNets implementations.
- Baseline matrix: four baselines.
- Fault/mutation matrix: seeded faults by MR layer and SUT.
- Metrics: MR violation, mutant/fault detection, localization agreement, continuous metric deltas, runtime/reproducibility overhead.
- Statistics: paired tests, confidence intervals, effect sizes, and multiple-comparison correction.

### 7. Results

BLOCKED until experiment artifacts exist.

Allowed placeholders only:

- table shells for SUT smoke tests;
- MR execution table schema;
- mutation/fault detection table schema;
- baseline comparison table schema;
- statistical-test output schema;
- reproducibility package manifest.

Do not write:

- pass/fail counts;
- detection percentages;
- "outperforms" claims;
- significance claims;
- concrete failure signatures;
- runtime overhead values.

### 8. Discussion

Draft only after Results exist, except for planned discussion questions:

- When does the rubric reject executable but physically invalid MRs?
- Which MR layers are most useful for localization?
- What does a continuity-constraint MR imply for NOETHER block coverage?
- How do open assets change inspectability and replication?

### 9. Threats to Validity

IST expects a clear, classified section.

| Category | Required treatment |
|---|---|
| Construct validity | Whether MR metrics actually measure the intended physical/software relation |
| Internal validity | Runner/parser bugs, threshold errors, SUT adapter defects, invalid transformations |
| External validity | Three SUTs still limited to MeshGraphNets/cylinder-flow family |
| Conclusion validity | Mutation design, statistical power, multiple testing, flaky runs |
| Reproducibility | Checkpoints, datasets, seeds, environment locks, prompt logs, open assets |
| Theory validity | NOETHER dependency, self-contained restatement, divergence/time-reversal corrections |

### 10. Reproducibility and Data Availability

- Describe the MetBench package, SUT adapters, MR cards, case JSON, runner/parser, metric scripts, thresholds, fault seeds, mutation specs, prompt logs, stats scripts, and archived results.
- Target GitHub + Zenodo DOI when artifacts are stable.
- Include exact commit, environment, seeds, checkpoint provenance, and exclusion rules.

### 11. Conclusion

- Restate C1-C4 only at evidence-supported strength.
- Avoid claiming full automation, CFD novelty, universal generalization, or unrun empirical findings.

## 5. Evaluation and Evidence Map

### 5.1 Three MeshGraphNets-Family SUTs

| SUT | Planned source | Role | Evidence required before Results |
|---|---|---|---|
| SUT-1 echowve MGN | `github.com/echowve/meshGraphNets_pytorch` | Primary PyTorch/PyG cylinder-flow case | Commit, dataset/checkpoint, adapter, smoke run, MR run artifacts |
| SUT-2 NVIDIA PhysicsNeMo MGN | `github.com/NVIDIA/physicsnemo` / `vortex_shedding_mgn` | Cross-implementation and method-comparison block instance | Version, NGC checkpoint provenance, adapter, comparable MR subset, run artifacts |
| SUT-3 DeepMind MGN | `github.com/google-deepmind/deepmind-research/meshgraphnets` | Cross-framework TF1 and family-scope stress test | Environment feasibility, dataset/checkpoint, adapter, smoke run, documented exclusions |

Status: repositories are identified in the plan; empirical claims remain blocked until current run artifacts exist. If SUT-3 is replaced for environment reasons, record the replacement rule and preserve the three-implementation rationale. This evidence does not support broad generalization beyond MeshGraphNets-family cylinder-flow surrogates.

### 5.2 Four Baselines

| Baseline | Purpose | Evidence required |
|---|---|---|
| B1 expert/manual MR | Compare against domain-expert MR design | Expert protocol, MR list, validity screening, execution results |
| B2 generic automatic MR identification | Scope-contrast baseline for whether generic MR tools recover physical semantic MRs without domain curation | Tool/version or documented adaptation, generated candidates, validity outcomes |
| B3 LLM-generated MR | Compare against prompt-based MR suggestion | Fixed prompts, model/version, prompt logs, candidate list, validity outcomes |
| B4 accuracy-only evaluation | Show difference between prediction error and relational/physical verdicts | Rollout-error metric, same SUT/fault set, comparison table |

No baseline may be described as weaker or stronger until the same SUT/fault evidence exists.

### 5.3 MR Families to Carry Forward

| MR family | Block / layer | Status rule |
|---|---|---|
| Identity determinism | Reliability gate / qualitative dynamics | Required smoke gate |
| Node permutation equivariance | Representation layer | Executable if graph relabeling preserves semantics |
| Face order invariance | Preprocessing / representation layer | Detects ordering and parser faults |
| Mirror-y equivariance | Symmetry block | Retain only with BC-compatible subgroup argument |
| Rigid translation | Symmetry block | Retain only if coordinates, domain, and BCs support it |
| Scaling / Re-St similarity | Similarity / limit-style physical relation | Qualified until nondimensional regime and frequency evidence exist |
| Rollout prefix consistency | Qualitative dynamics / semigroup | Valid temporal MR; not time reversal |
| Divergence boundedness | Continuity constraint | Not Noether conservation; possible constraint-block witness |
| Cross-SUT agreement | Conditional method-comparison block | Retain as an MR only after comparability protocol passes; otherwise report as cross-implementation analysis |

Excluded:

- time-reversal MR for viscous N-S cylinder flow.

### 5.4 Seeded Faults and Mutations

Minimum evidence table:

| Field | Requirement |
|---|---|
| Fault/mutant ID | Stable ID with SUT, file/operator, and seed |
| Fault class | Representation, BC/transform, physical metric, temporal rollout, adapter/parser, numerical threshold |
| Injection mechanism | Script, patch, config mutation, or seeded data perturbation |
| Expected affected MR layer | Predeclared before execution |
| Observed verdicts | MR pass/fail plus metric values from run artifacts |
| Baseline outcome | B1-B4 result on the same fault/mutant where applicable |
| Localization evidence | Whether the MR tree points to the intended layer |

Aggregate claims require per-mutant evidence, not only summary scores.

### 5.5 Statistical Tests

| Question | Planned analysis |
|---|---|
| MR framework vs baselines on paired fault detection | McNemar or Cochran Q where paired binary outcomes apply |
| Continuous metric differences across SUTs/MRs | Wilcoxon signed-rank, paired bootstrap, or permutation test |
| Detection/localization effect size | Odds ratio, Cliff's delta, or bootstrap confidence interval |
| Multiple MR/fault comparisons | Holm-Bonferroni or Benjamini-Hochberg, declared before reporting |
| Flakiness and determinism | Repeated seeds/runs with explicit instability reporting |

Statistics are blocked until scripts and raw outputs are present.

### 5.6 Open Reproducibility Package

Package contents required before submission:

- MR cards and validity-rubric decisions;
- SUT adapter source and version pins;
- MetBench case JSON, runner/parser contracts, metric scripts, thresholds, and verdict schema;
- seeded fault/mutation scripts and manifests;
- prompt logs for LLM baseline;
- raw run outputs, processed tables, and statistical scripts;
- environment locks, seeds, checkpoint/dataset provenance, exclusion rules;
- README with one-command or stepwise reproduction path;
- archive manifest and DOI once GitHub/Zenodo publication is ready.

## 6. Claim Ledger

Allowed before experiments:

- IST regular-track positioning;
- software testing/V&V motivation;
- C1 rubric design;
- C2 framework architecture;
- C3 localization protocol;
- planned C4 evaluation design;
- v2.1 theory corrections and MR validity boundaries.

Blocked before experiments:

- any empirical effectiveness claim;
- any claim that NOETHER-informed MRs outperform baselines;
- any claim that NOETHER mechanically proves the physical validity of cylinder-flow MRs;
- any "first neural-fluid-symmetry-test" or "first physical MR for ML surrogates" claim;
- any SUT pass/fail, mutation score, or detection rate;
- any statistical significance statement;
- any concrete failure signature;
- any claim that the framework generalizes beyond the evaluated SUTs.
- any claim that C3 is a validated localization model before seeded-fault layer evidence exists.

Immediate next writing work:

1. Draft Introduction, Background, C1, C2, C3, and Empirical Evaluation Design only.
2. Convert every retained MR into a card with rubric decision and executable verdict mapping.
3. Freeze SUT/baseline/fault/statistics protocols before running experiments.
4. Keep Results, Discussion claims, and Conclusion strength gated by real artifacts.
