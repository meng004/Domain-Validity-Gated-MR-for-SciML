# Academic Paper Phase 0 Configuration

> Status: authoritative IST/v2.2 stance-gated planning configuration.
> Scope: planning-stage paper contract only; Results remain blocked until real experiment outputs exist.

## 1. Paper Type

Research article / software engineering method paper with an empirical scientific-computing case study.

Primary positioning: domain-validity-gated metamorphic relation (MR) identification and executable MR asset construction for scientific machine-learning software, not a CFD solver paper, not a new GNN architecture paper, and not the main NOETHER or minimal-complete-MR theory paper.

## 2. Discipline and Audience

- Primary discipline: Software Engineering / Software Testing / Verification and Validation.
- Secondary domain: Scientific Machine Learning / Computational Fluid Dynamics.
- Target readers: metamorphic testing, AI/scientific software testing, simulation V&V, and scientific ML reliability researchers.

## 3. Journal Decision

Primary target: **Information and Software Technology (IST), regular research-paper track**.

Journal hierarchy:

1. **IST regular track**: current target; requires a structured abstract and has a 15,000-word research-paper limit.
2. **TOSEM**: aspirational only after stronger empirical evidence, broader SUT coverage, and a more mature theory/evidence package.
3. **Journal of Systems and Software (JSS)**: fallback if IST framing or review fit is weak.
4. **Software Testing, Verification and Reliability (STVR)**: fallback, not the current primary target.

## 4. Formatting Contract

- Manuscript language: English.
- Working format: Markdown scaffold in `manuscript/manuscript.md`.
- Citation workflow: BibTeX keys in Markdown during drafting; final style deferred to the selected journal template.
- Abstract format: IST structured abstract with **Context / Objective / Method / Results / Conclusion** headings.
- Word limit: keep the full research paper below IST's 15,000-word limit.

## 5. Working Title

Primary title:

**Domain-Validity-Gated Metamorphic Testing of Scientific ML Surrogates**

Candidate alternatives:

1. From Candidate Relations to Executable MR Assets for Scientific Machine Learning
2. Auditable Metamorphic-Relation Assets for Testing Scientific Machine-Learning Surrogates
3. Domain-Validity-Gated Oracle-Free Testing of Mesh-Based Neural Cylinder-Flow Surrogates

## 6. Main Research Question

**How can candidate metamorphic relations for scientific machine-learning systems be screened for domain validity and converted into executable oracle-free test assets without relying on exact per-sample test oracles?**

## 7. Research Questions

- **RQ1 - Validity:** How can a rubric distinguish physically meaningful MRs from executable but invalid transformations for cylinder-flow neural simulation?
- **RQ2 - Operationalization:** How can retained candidates be represented as MR cards and executable assets with source cases, follow-up transformations, metrics, thresholds, exclusions, and verdict rules?
- **RQ3 - Verdict and interpretation:** How can relation-level verdicts distinguish pass, fail, skip, out-of-relation-domain, numerical-tolerance issue, and inconclusive outcomes?
- **RQ4 - Case-study evidence:** In a MeshGraphNets-family cylinder-flow case study, what evidence does the rubric-gated asset workflow add relative to expert MR design, LLM-assisted candidate generation, generic MR-generation scope contrasts, and rollout-accuracy diagnostics?

## 8. Contribution Order

- **C1. Validity rubric for physically meaningful MRs.** A rubric for screening candidate MRs by physical basis, semantic preservation, measurable output relation, threshold interpretability, and failure diagnosability.
- **C2. MR-card and executable-asset workflow.** A workflow that translates rubric-accepted relations into case schemas, transformations, metrics, thresholds, assertions, exclusion rules, and reproducible execution assets.
- **C3. Relation-level verdict and ledger scheme.** A verdict structure that separates pass, fail, skip, out-of-relation-domain, numerical-tolerance issue, and inconclusive outcomes without claiming validated failure localization before seeded-fault evidence exists.
- **C4. MeshGraphNets cylinder-flow case study and reproducible MetBench assets.** A planned case study over MeshGraphNets-family cylinder-flow implementations/configurations with artifact-backed cases, runners, metrics, logs, and reproduction notes.

## 9. v2.1 Physics Corrections

- No claim may state that Noether's theorem derives the divergence-free condition.
- Divergence is treated as an incompressible continuity / mass-conservation constraint.
- Time reversal is explicitly excluded for viscous cylinder flow because the dynamics are dissipative and not time-reversal invariant in the intended test sense.
- The symmetry block consumes known classical Navier-Stokes Lie symmetries as prior physical knowledge; it does not claim to discover those symmetries.
- NOETHER is one possible guidance and organization source for relation candidates, not a theorem prover, not a claim that every MR is derived from Noether's theorem, and not the contribution being evaluated in this paper.
- NOETHER's downstream construction guarantees apply only after the cylinder-flow operator algebra and block assignment have been curated; upstream curation remains an empirical/domain-validity hypothesis.
- Method-comparison/cross-SUT agreement is a conditional MR only after a comparability protocol establishes matched cases, units, fields, rollout horizons, boundary conditions, and tolerances.

## 10. SUT Plan

Planned subject systems, all within the MeshGraphNets-family cylinder-flow scope:

1. **echowve MeshGraphNets PyG** cylinder-flow implementation.
2. **NVIDIA PhysicsNeMo `vortex_shedding_mgn`** implementation.
3. **DeepMind TF1 MeshGraphNets**, or an equivalent third MeshGraphNets-family SUT/configuration if the TF1 runtime/assets prove impractical.

Third-SUT selection remains pending until runtime feasibility and reproducible assets are confirmed. This design supports cross-implementation pressure testing, not broad generalization to all neural fluid surrogates.

## 11. Baseline Plan

The empirical comparison should include four baselines:

1. Manual expert MR design.
2. Generic automatic MR identification/generation as a scope-contrast baseline, not as a strawman performance baseline.
3. LLM-generated MR design with fixed prompts, model/version, temperature, prompt logs, and rubric decisions.
4. Pure rollout accuracy without relational testing.

Baseline claims are planning targets only until executable protocols and result artifacts exist.
No baseline may be described as weaker, stronger, or outperformed until the same SUT/fault evidence exists.

## 12. Evidence Gate

Results drafting is blocked until experiments produce auditable artifacts. Required evidence before writing Results:

- SUT-specific setup and reproducibility notes.
- Baseline rollout evidence for each available SUT.
- Executable MR cases with logged inputs, transformations, outputs, metrics, thresholds, and assertions.
- MR cards with physical basis, boundary-condition compatibility, output mapping, discrete operator if applicable, threshold provenance, and OOD/exclusion rules.
- Baseline comparison artifacts for the four baseline families.
- Relation-level verdict records, with failure-localization claims allowed only if seeded faults, mutants, or known failure-layer evidence are added.
- Threats-to-validity notes grounded in observed limitations rather than anticipated outcomes.

Until those artifacts exist, the paper may describe motivation, method, protocol, and planned evaluation only. It must not report invented effect sizes, pass/fail rates, performance improvements, or comparative findings.

## 13. Stop / Go Gate

Accepted IST/v2.1 Phase 0 state:

- [x] Primary target is IST regular track.
- [x] TOSEM is aspirational only after stronger evidence; JSS and STVR are fallback options.
- [x] Structured IST abstract and 15,000-word limit are part of the writing contract.
- [x] Contribution order is C1 validity rubric, C2 MR-card/executable-asset workflow, C3 relation-level verdict ledger, C4 MeshGraphNets cylinder-flow case study and MetBench assets.
- [x] v2.1 physics corrections are binding.
- [x] v2.2 stance gate is binding: no broad neural-fluid generalization, no first-symmetry-test claim, no validated localization claim, and no baseline superiority claim before artifacts.
- [x] Three MeshGraphNets-family SUT/configuration and four-baseline plans are planning commitments, not completed results.
- [x] Full Results drafting remains blocked until experiment outputs exist.
