# STVR 论文结构与证据地图

> Academic Paper Phase 2 / Structure Architecture  
> Status: outline approved for drafting only where evidence exists.

## 1. Target Article Shape

STVR-facing article type:

**Method paper with a reproducible case study.**

The manuscript should not be framed as:

- a new GNN architecture paper;
- a CFD benchmark paper;
- a MetBench integration note only;
- a pure survey of metamorphic testing.

It should be framed as:

**a physically grounded MR identification and operationalization method for oracle-free testing of mesh-based neural surrogate models, evaluated on cylinder-flow MeshGraphNets.**

## 2. Proposed Section Structure

### 1. Introduction

Purpose:

- Establish scientific ML surrogate testing as a real software testing problem.
- Introduce the oracle problem.
- Argue that MT is promising but MR identification is the bottleneck.
- State why physical neural simulation requires domain-grounded MR identification.
- Introduce cylinder flow MeshGraphNets as a case study.

Evidence needed:

- MeshGraphNets efficiency and scientific simulation context.
- Oracle problem and MT foundation.
- MR identification difficulty from METRIC/SimiMR/GenMorph literature.

### 2. Background and Related Work

Subsections:

1. Test oracle problem and metamorphic testing.
2. MR identification and generation.
3. MT for ML and scientific software.
4. Simulation V&V and scientific ML testing.
5. Mesh-based neural simulation and cylinder flow.

Evidence needed:

- At least 20-30 verified references.
- Explicit competing-work paragraph for METRIC, SimiMR, GenMorph, and LLM-based MR workflows.

### 3. Physically Grounded MR Identification

Subsections:

1. Framework overview.
2. Invariant source taxonomy.
3. Candidate MR formulation.
4. Validity rubric.
5. Operationalization into executable assertions.

Evidence needed:

- MR cards for every MR.
- Clear boundary: method is systematic and framework-based, not fully automatic.

### 4. Case Study Design

Subsections:

1. Subject under test: MeshGraphNets cylinder-flow implementation.
2. Dataset and runtime assets.
3. MR set.
4. Metrics and thresholds.
5. Execution protocol.
6. Reproducibility package.

Evidence needed:

- Baseline rollout smoke test.
- Runtime asset manifest.
- Case schema, runner/parser contracts.
- Deterministic device/profile rules.

### 5. Results

Subsections:

1. Overall MR execution results.
2. Representation-level MRs.
3. Physics-level MRs.
4. Re-St frequency-domain MR.
5. Failure signature analysis.

Evidence needed:

- Tables of MR pass/fail and metric values.
- At least one example failure trace or diagnostic.
- FFT/probe evidence if Re-St is retained.

Blocking condition:

- Do not draft this section as if results exist before running experiments.

### 6. Discussion

Subsections:

1. What graph-structural MRs reveal.
2. What physics-level MRs reveal.
3. Why physical validity matters in MR identification.
4. Practical implications for testing scientific ML software.
5. Limitations of single-SUT evidence.

Evidence needed:

- Results section.
- Threats-to-validity framing.

### 7. Threats to Validity

Categories:

- Construct validity: Are MR metrics actually measuring the intended physical relation?
- Internal validity: Are failures caused by model behavior, runner/parser defects, or invalid transformations?
- External validity: Single MeshGraphNets implementation and single flow domain.
- Conclusion validity: Threshold interpretation and statistical/empirical support.
- Reproducibility: Dependencies, checkpoint, fixture, deterministic settings, open artifacts.

### 8. Conclusion

Purpose:

- Restate that physics-grounded MR identification can make oracle-free testing practical for scientific ML surrogate models.
- Avoid overstating automation or generalization.

## 3. Contribution-to-Evidence Map

| Contribution | Evidence required | Current status |
|---|---|---|
| C1. MR taxonomy | MR source classification and MR cards | Partly available in `theory/` |
| C2. Validity rubric | Criteria + examples of valid/invalid MR candidates | Needs drafting |
| C3. Operationalization workflow | case schema, runner/parser contract, metric/threshold/assertion mapping | Partly available in MetBench asset doc |
| C4. MeshGraphNets case study | baseline, MR execution results, failure signatures | Not yet available |

## 4. Initial MR Set for Paper

### Batch 1: Representation and Basic Equivariance

| MR | Role | Expected paper use |
|---|---|---|
| identity determinism | sanity check | Baseline reliability gate |
| node permutation equivariance | graph-structural MR | Shows GNN representation-level correctness |
| face order invariance | graph construction MR | Detects preprocessing/order bugs |
| mirror-y equivariance | geometry/physics bridge MR | First physics-aware relation |

### Batch 2: Robustness and Conservation

| MR | Role | Expected paper use |
|---|---|---|
| velocity perturbation stability | robustness MR | Tests local smoothness |
| divergence / mass conservation | physics-level MR | Tests incompressible-flow consistency |
| rigid translation invariance | geometric MR | Tests coordinate encoding assumptions |
| rollout prefix consistency | temporal MR | Tests deterministic autoregressive behavior |

### Batch 3: Similarity and Long-Horizon Dynamics

| MR | Role | Expected paper use |
|---|---|---|
| scale similarity | physical similarity MR | Links geometry/velocity scaling |
| Re-St invariance | frequency-domain physics MR | High-value STVR differentiator if evidence is strong |

## 5. Argument Blueprint

Main claim:

> A metamorphic relation for scientific ML surrogate testing is publishable only when it is not merely executable, but also physically valid, measurable, threshold-interpretable, and diagnosable.

Supporting claims:

1. Exact test oracles are expensive for mesh-based neural simulation.
2. MT supplies relational oracles, but MR identification remains a bottleneck.
3. Generic MR identification/generation methods do not fully resolve physical semantic validity.
4. Cylinder flow provides a compact domain where graph, geometry, physics, and temporal invariants can be operationalized.
5. The resulting MR set reveals different failure classes than aggregate prediction error alone.

Counter-arguments to address:

1. "This is only a case study."  
   Response: Yes; frame generality at the method and taxonomy level, not at empirical universality.

2. "MRs are manually designed."  
   Response: The contribution is systematic, physically grounded identification and operationalization, not full automation.

3. "Thresholds are arbitrary."  
   Response: Separate numerical precision thresholds, deterministic equivalence thresholds, robustness tolerances, and physical-frequency thresholds.

4. "Failure may indicate OOD transformations, not model defects."  
   Response: Include validity boundaries and classify invalid/OOD transformations separately.

## 6. Immediate Next Tasks

1. Convert each MR into a one-page card.
2. Expand and verify the literature matrix.
3. Decide whether first manuscript targets Batch 1+2 only or includes Batch 3 Re-St evidence.
4. Start writing Introduction and Method sections only; defer Results until experiment outputs exist.

