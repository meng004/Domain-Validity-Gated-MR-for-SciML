# Domain-Validity-Gated Metamorphic Testing of Scientific ML Surrogates

## Structured Abstract

### Context

Scientific machine-learning (SciML) surrogates are increasingly used to approximate expensive physical simulations. Mesh-based neural simulators are attractive for fluid-flow problems because they operate on irregular meshes and predict spatiotemporal physical fields. Testing such systems is difficult because exact expected outputs are often unavailable for arbitrary inputs without running a trusted high-fidelity solver. Rollout accuracy and physics residuals provide useful evidence, but they do not by themselves specify which physical relations should hold under controlled transformations of inputs, meshes, boundary conditions, or parameters.

### Objective

This paper investigates how physically meaningful metamorphic relations (MRs) can be screened and operationalized as executable oracle-free test assets for scientific machine-learning systems. The goal is not to improve a predictive model, but to make the step from candidate relation to executable test asset more systematic, auditable, and explicit about the physical, numerical, and software conditions under which each relation is expected to hold. MeshGraphNets-family cylinder-flow surrogates are used as the concrete case study.

### Method

We propose a domain-validity rubric for screening candidate MRs, an MR-card and executable-asset format that records source cases, follow-up transformations, output mappings, metrics, tolerances, exclusion rules, and relation-level verdicts, and a case-study protocol for applying these assets to mesh-based neural cylinder-flow surrogates. Candidate sources may include physical equations, boundary conditions, representation contracts, expert reasoning, LLM-assisted candidate lists, and NOETHER-style pattern organization, but validity is decided by the rubric and evidence records rather than by candidate generation alone.

### Results

On cylinder flow, the rubric produces three distinct, artifact-backed outcomes on the same surrogate: node permutation is admitted and holds to machine precision; exact mirror-y is ruled out-of-domain and, downgraded to an OOD-stress probe, fails on every recorded eval frame; absolute conservation is deferred for want of a calibratable tolerance, while its reference-relative guard passes. These readings replicate across a K=6 checkpoint roster (six checkpoints), three held-out trajectories, and three further cylinder-flow architectures, including the NVIDIA PhysicsNeMo production implementation. On a genuinely second CFD task, compressible airfoil flow on a second official dataset, the same predicate yields a different but physically correct typed structure: node permutation stays admitted, while incompressible continuity is now rejected on physical-basis grounds rather than deferred, showing that the gate reasons about domain validity rather than running a fixed checklist. Two controls separate model-level violations from geometric artifacts, an O(h) operator sweep validates the measurement-floor gate, and cross-family PINN and FNO executions transfer the rubric beyond mesh surrogates. The evidence is bounded to the stated rosters and datasets.

### Conclusion

The evidence supports a validity-aware bridge from candidate MR ideas to auditable SciML test assets. The main empirical lesson is not that every physical intuition becomes a clean MR, or that every MR exposes a general fault. Rather, the scoped pilots show that a rubric-gated workflow can produce relation-level outcomes while preserving the evidence boundary for each claim. We frame this as a domain-admissibility-gated, relation-indexed approach to SciML OOD validation: a relation is admitted only when its tolerance dominates the relevant numerical error floor, and its verdict is read in a space that separates a model-level violation from an out-of-domain application.

## Keywords

Metamorphic testing; metamorphic relation identification; oracle problem; scientific machine learning; MeshGraphNets; cylinder flow; software verification and validation.

## 1. Introduction

Scientific computing increasingly uses learned surrogates such as MeshGraphNets to cut the cost of repeated numerical simulation. These models create a familiar software testing problem in a new setting: for most candidate inputs there is no cheap exact output to check against. The common response, held-out rollout error, is necessary but incomplete: a model can have low average error yet still violate relations that should hold under a physically meaningful transformation, and a high error does not say which physical, numerical, or representational condition was violated.

Metamorphic testing (MT) addresses this oracle problem by checking relations among multiple executions: if a source input is transformed in a specified way, the outputs should satisfy a necessary relation. Conservation laws, symmetries, nondimensional similarity, and boundary constraints all suggest such relations. The difficult part for SciML is deciding which candidate relations are actually valid and executable for a given program. A plausible-looking transformation may violate the governing assumptions, boundary conditions, discretization, or measurement tolerance of the system under test (SUT); treating it as an automatically valid MR makes a suite look rigorous while hiding the assumptions that decide whether a violation is meaningful. Physics-based MRs for learned field predictors are an active area, so the contribution here is validity-gated execution, not first use.

This paper treats MR identification for SciML as a validity-gated testing problem. Physical knowledge, expert reasoning, LLM-assisted lists, and NOETHER-style patterns can all suggest candidates, but a candidate becomes an executable MR only after its physical or software basis, transformation preconditions, tolerance rationale, and verdict interpretation are recorded (Section 3.4).

Two ideas organize this treatment. First, a candidate relation is *admissible* only when, in addition to a physical or software basis and satisfied transformation preconditions, it is numerically decidable: its verdict tolerance must dominate the intrinsic error floor of the operator that measures it, machine precision for an exact representation relation, the interpolation or mapping floor for an approximate geometric relation, or the discretization floor of a discrete operator for a continuity relation. Second, a relation-level verdict is read in two dimensions, how far the measured quantity violates the relation, and how far the transformed case lies outside the relation's validity domain, so that a model-level inconsistency is not confused with a relation applied outside its domain. We refer to this as a domain-admissibility-gated, relation-indexed approach to SciML out-of-distribution (OOD) validation, an organizing framework rather than a new algorithm.

The case study is scoped to cylinder-flow surrogates: one task examined deeply across four architectures including the PhysicsNeMo production implementation, with cross-family PINN and FNO executions testing whether the predicate transfers. This deliberately trades task breadth for architectural depth and auditability; the boundary of what this evidence supports is stated once, in Section 5.9.

### 1.1 Research Questions

The main research question is:

**RQ0. How can candidate metamorphic relations for scientific machine-learning systems be screened for domain validity and converted into executable oracle-free test assets without relying on exact per-sample expected outputs?**

We decompose this into four questions.

**RQ1 - Validity.** How can a domain-validity rubric distinguish physically meaningful candidate MRs from transformations that are executable but invalid, underspecified, or outside the relation's domain?

**RQ2 - Operationalization.** How can retained candidates be represented as MR cards and executable assets with source cases, follow-up transformations, metrics, thresholds, exclusions, and verdict rules?

**RQ3 - Verdict and interpretation.** How can relation-level verdicts distinguish pass, fail, skip, out-of-relation-domain, numerical tolerance issue, and inconclusive outcomes?

**RQ4 - Case-study evidence.** In a MeshGraphNets-family cylinder-flow case study, what evidence does the rubric-gated asset workflow add relative to rollout-accuracy diagnostics, secondary LLM/generic candidate baselines, and external witness evidence? The current evidence answers this through scoped comparators and a secondary external-scope audit rather than through cross-SUT pass-rate estimation.

### 1.2 Contributions

This paper makes three scoped contributions, each repositioned narrowly with respect to the closest prior we identify in Section 2, and evaluated through a single MeshGraphNets-family cylinder-flow case study. The positive claim is methodological: the paper contributes a measurement-floor admissibility gate, a typed domain-inadmissibility verdict, and a seeded-fault diagnostic stress test: the MR-class-to-fault-class diagnostic is used as stress-test evidence, not a validated localization model.

**Measurement-floor admissibility gate.** A domain-validity rubric and MR-card workflow screen candidate MRs and convert retained ones into auditable executable assets. The tolerance floor is grounded in the *intrinsic error floor of the discrete measurement operator*, whose truncation order is characterizable ($O(h)$ for a P1 discrete-divergence operator on a triangular mesh). Where Eniser et al.'s *relaxations* [eniser2022relaxations] derive a tolerance empirically from RL rollouts, ours is a property of the scoring operator's numerical analysis, so a relation can be refused before any model runs. For the concrete deployed-scale structured mesh this floor is closed-form: a leading-order predictor from the analytic Hessian matches the measured floor to within 0.5% and a rigorous a-priori bound dominates it (Section 5.5), so the gate's tolerance is set above a derived rather than merely estimated floor; a general bound for arbitrary unstructured meshes remains future work. To our knowledge, grounding an MR tolerance in the measurement operator's own error floor is new in the SciML setting.

**Typed domain-inadmissibility verdict.** Verdicts are read in two dimensions (relation-violation against domain-violation magnitude). Unlike the binary bug-vs-inapplicability separation of the Duque-Torres line [duqueTorres2023bugornot, duqueTorres2023completePipeline, duqueTorres2023metaTrimmer], the inadmissibility axis is *typed*, sub-dimensions drawn from PDE-domain preconditions, geometry, boundary conditions, and operator admissibility, and carries a continuous per-relation score from committed precondition measurements; cross-MR-class calibration is left to future work.

**Seeded-fault diagnostic stress test.** As an element none of the closest prior works addresses, the paper's own MRs are used as detectors against an independently re-implemented 10-mutant seeded-fault catalogue: the continuity MR responds to boundary-condition and normalization-scale faults, the symmetry MR to physical-channel and mesh-adjacency faults, node-permutation to none. This is suggestive evidence for a typed MR-class-to-fault-class diagnostic, not a validated localization model.

The three devices are the claims; Sections 5.3–5.6 carry their primary evidence and Section 5.8 shows the predicate transferring across model families. The design extends the active-transformation direction of Reichert et al. [reichert2024hess] from hydrology to mesh-based fluid surrogates; subjects, baselines, and controls are detailed in Section 4.

## 2. Background and Related Work

### 2.1 Mesh-Based Neural Simulation

Mesh-based neural simulators learn dynamics on graph or mesh representations of physical systems. For fluid-flow problems, a mesh representation is attractive because the geometry, boundary regions, and local connectivity can be represented without forcing the state onto a regular grid. MeshGraphNets is a representative architecture family in this area: it encodes mesh nodes and edges, propagates information by message passing, and predicts future physical fields through autoregressive rollout.

The cylinder-flow benchmark combines the features that matter for SciML validation, geometry, boundary conditions, velocity and pressure-like fields, temporal rollout, and flow-regime assumptions, and exposes the distinction between data-driven accuracy and physical relation preservation: a model may fit a trajectory distribution while failing under a controlled transformation of geometry, mesh, or flow parameters.

We treat MeshGraphNets-family systems as software under test, not as new modeling contributions, and ask how their outputs behave under controlled input transformations and whether necessary relations remain within explicit tolerances.

### 2.2 Metamorphic Testing and the Oracle Problem

Metamorphic testing was developed to address programs for which it is difficult or impossible to know the correct output for a single test input. Instead of checking one output against one expected value, MT checks a relation among the outputs of a source input and one or more follow-up inputs. This framing has been applied to scientific software, simulation models, and machine-learning systems, all of which can suffer from oracle problems.

For SciML surrogates, the oracle problem is especially visible in out-of-distribution (OOD) settings. A trusted solver may be too expensive to run for every transformed case, and even when a reference output is available, a single pointwise error does not necessarily indicate whether a physical relation has been preserved. MR-based testing offers a complementary perspective: it asks whether the SUT maintains a necessary relation under a controlled transformation.

However, SciML MRs cannot be treated as generic input perturbations. In image-based ML testing, transformations such as lighting or weather changes may preserve the semantic label. In scientific computing, the transformation must respect governing equations, physical regimes, boundary conditions, mesh representation, and numerical tolerance. The correctness of the MR itself becomes a central validity question.

### 2.3 MR Identification for Scientific and Simulation Software

Prior work on scientific software testing has shown that MRs can be elicited from monotonicity, conservation-like behavior, scaling relations, simulation assumptions, and domain-specific expectations. Work on simulation validation similarly treats multi-run relations as pseudo-oracles when direct validation data are limited or unavailable. These studies establish that MR thinking is practical for scientific and simulation software, not merely for toy functions.

Other work has explored automated or semi-automated MR identification. For example, research on ocean system models shows that data-driven search can discover candidate transformations in complex physical software. CPS testing work shows that design assumptions can be encoded as MRs and then used to generate new test traces. These show that MR sources can include system assumptions, model structure, and physical design knowledge.

The gap is that candidate identification is not enough for SciML. A candidate relation must also state when it is supposed to hold. Without a domain-of-validity record, a failed test may mean several different things: the relation was invalid under the chosen boundary conditions, the transformation left the physical regime, the tolerance was not numerically justified, or the SUT violated a relation it should have preserved. This paper makes that distinction explicit.

### 2.4 Physics-Based MT for Learned Scientific Simulators

Three contemporary works are the closest prior to ours and frame what is and is not new here. We engage each one explicitly.

**Reichert et al. (2024)** [reichert2024hess] applied physics-derived metamorphic relations to a trained LSTM hydrologic surrogate. They perturbed climate-forcing inputs (temperature, precipitation) in directions where the qualitative physical response is known a priori, stratified pass/fail outcomes by basin elevation to produce an implicit applicability map, and excluded basins where forcing uncertainty dominated the response signal, an informal admissibility filter. The present work formalises these practices as an explicit admissibility predicate, a two-dimensional verdict type, and a relation-indexed applicability map, and extends them from hydrology to mesh-based neural fluid surrogates whose outputs live on irregular meshes and whose MR validity depends on geometry and discrete operators rather than basin physiography.

**Eniser et al. (2022)** [eniser2022relaxations] introduced *relaxations*, numerical tolerances embedded inside MR oracles, for action-policy testing of stochastic reinforcement-learning systems, deriving them empirically from policy rollouts on Highway, LunarLander and BipedalWalker. We extend this calibrated-tolerance principle to deterministic numerical surrogates by grounding the tolerance floor in the intrinsic error floor of the discrete measurement operator, whose truncation order is theoretically characterizable (for a P1 discrete-divergence operator on a triangular mesh, $O(h)$ in the mesh spacing). The distinction from rollout-derived relaxations is that the floor is a property of the measurement operator rather than of model stochasticity; for the concrete deployed-scale mesh we give its magnitude in closed form, a leading-order predictor matching the measured floor to within 0.5% and a rigorous a-priori upper bound (Section 5.5), with a general bound for arbitrary unstructured meshes left to future work.

**The 2023 violation-attribution cluster**, Duque-Torres et al. (SANER 2023) [duqueTorres2023bugornot], *Towards a Complete Metamorphic Testing Pipeline* [duqueTorres2023completePipeline] and MetaTrimmer [duqueTorres2023metaTrimmer], identified the bug-vs-MR-inapplicability separation as a research problem and addressed it architecturally with explicit MR constraints used as a pipeline pre-filter, with MetaTrimmer automating the constraint derivation from random-input violation logs. Our two-dimensional verdict instantiates this architectural pattern for physics-governed SciML; what is new is a *typed classification of domain-inadmissibility sub-dimensions* drawn from PDE-domain preconditions, geometry compatibility, boundary-condition compatibility, and operator admissibility, rather than a binary skip/proceed gate or a data-derived constraint set.

None of Reichert, Eniser, or the 2023 cluster maps MR failures back to identifiable fault classes within the system under test; the seeded-fault MR-as-detector with its class-specific response pattern (Section 5.3) is the element that distinguishes this paper.

| Capability | Reichert et al. 2024 | Eniser et al. 2022 | Duque-Torres 2023 line | This paper |
|---|---|---|---|---|
| Admissibility screening | informal exclusion filter | — | binary skip/proceed pre-filter | four-condition predicate with measurement-floor gate |
| Tolerance grounding | a-priori qualitative direction | empirical rollout-derived relaxations | — | measurement operator's own characterizable error floor (O(h) validated) |
| Inadmissibility verdict | implicit (basin strata) | — | binary | typed sub-dimensions + continuous per-relation D score |
| Fault-class diagnosis | — | — | — | MR-class-to-fault-class stress test with per-detector precision/recall |
| Subjects | one LSTM surrogate | RL policies | tabular/numeric programs | 4 cylinder-flow architectures incl. a production framework + PINN/FNO transfer |

### 2.5 SciML V&V, Residuals, UQ, and Failure Modes

SciML reliability research has developed several important tools: physics residuals, uncertainty quantification, conformal prediction, certified error bounds, stress testing, equivariance error, and failure-mode analysis. These tools address real weaknesses of learned PDE solvers and neural surrogates. For example, calibrated physics-informed uncertainty quantification uses PDE residuals as nonconformity scores and provides statistical coverage guarantees. Work on PINN failure modes shows that physical constraints in a training loss do not guarantee reliable behavior in more difficult regimes.

These methods are complementary to MT. A residual, conservation error, or equivariance error can be a useful diagnostic, but it is not automatically an MR. It becomes part of an executable relation only when there is a source case, a follow-up transformation, an expected output relation, a tolerance rule, and a verdict interpretation. We use SciML diagnostics as possible relation measurements, while MT supplies the multi-execution oracle-free structure.

### 2.6 Hybrid ML-Solver Trust Regions

Hybrid ML-solver frameworks use residual thresholds or error estimates to decide when a learned component should be trusted and when a numerical solver takes over, operationalizing a runtime trust region through residual-based switching rather than offline relation-based testing.

The distinction is deliberate. Uncertainty quantification, conformal prediction, and residual-threshold trust regions locate unreliable behavior passively in feature, residual, or error space. The present method acts offline and in relation space: it applies a controlled transformation and reports which necessary relation breaks under it, indexed by that transformation, and the two-dimensional verdict separates a model-level violation from an out-of-domain application, a separation a scalar accuracy or residual magnitude does not by itself provide (the §5.3 mirror-y result is one bounded within-SUT instance).

### 2.7 What Is New and What Is Not New

Metamorphic testing, MR identification, scientific-software MT, residual diagnostics, uncertainty quantification, LLM candidate generation, and NOETHER-style candidate organization are established or emerging sources of testing ideas. The paper's narrower claim is that SciML MR identification should be treated as a domain-validity problem: a candidate relation becomes useful only after its physical basis, transformation preconditions, output mapping, tolerance, exclusion rule, executable artifact, and relation-level verdict are recorded.

What is new is the evidence-gated conversion from candidate relation to executable SciML MR asset: to our knowledge the first validity-gated metamorphic-testing pipeline for physics-governed SciML in which candidate screening, verdict typing, and fault-class diagnosis are each operationalized and executed rather than proposed. Each closest prior work supplies one ingredient, Reichert et al. an informal admissibility filter, Eniser et al. a calibrated tolerance, the Duque-Torres line a binary applicability pre-filter, but none grounds the tolerance in the measurement operator's own characterizable error floor, types the inadmissibility verdict, or maps MR failures back to fault classes. The novelty is two organizing devices rather than a checklist of MR fields: an admissibility gate that ties a relation's tolerance to the numerical error floor of its own measurement, and a two-dimensional verdict that separates a model violation from an out-of-domain application. A third, empirically distinct element (Section 5.3) is the seeded-fault diagnostic stress test, where the paper's own MRs act as detectors with a by-class response pattern, continuity to boundary/scale faults, symmetry to physical-channel/adjacency faults, that none of the closest prior works reports.

## 3. Method

### 3.1 Overview

The proposed method is a five-stage workflow:

1. identify candidate relation sources;
2. organize candidate relations using declared candidate-source categories;
3. screen candidates with a domain-validity rubric;
4. convert retained relations into executable MR assets;
5. execute the assets and record relation-level verdicts.

The method deliberately separates candidate generation from validity judgment: the algebraic properties of the governing and discrete operators (and NOETHER-style pattern organization) generate candidates, but none of them certifies that a relation is physically valid for a particular SUT, dataset, mesh, boundary condition, or numerical tolerance. Validity is determined by the rubric and by executable evidence.

### 3.2 Candidate Relation Sources

Candidate MRs are read off the algebraic properties of the governing and discrete operators, and each candidate is located in one of the three classification levels of §3.6. For cylinder-flow surrogates the recurring meta-patterns are:

**Equivariance** (commutation with a group action). The equations commute with reflections, rigid motions, and frame changes, physical-model symmetry MRs, admissible only under compatible geometry and boundary labels; the representation commutes with node permutation, face ordering, and edge encoding, code-model representation MRs, which are training-independent software contracts.

**Conservation.** Continuity and balance laws yield discrete-divergence and boundary-flux relations (physical-model); their decidability is set at the computational-model level by the measuring operator's error floor (§3.3, §5.5).

**Homogeneity and scaling.** Reynolds- and Strouhal-number similarity yields nondimensional follow-up transformations, valid only within regimes where the relation is meaningful.

**Composition.** Autoregressive rollouts yield determinism, prefix-consistency, and semigroup-like checks, implementation and numerical-consistency relations, not physical laws.

**Cross-implementation comparison.** Outputs from different implementations support method-comparison checks only when units, state variables, meshes, rollout horizons, boundary conditions, and checkpoints are comparable; otherwise they are triangulation evidence rather than retained MRs.

Linearity (superposition) and order/monotonicity are further meta-patterns available for linear operators and positivity-preserving schemes; they are not exercised by the deterministic relations studied here. The same algebraic property can hold at the physical-model level yet fail at the computational or code level, an asymmetric mesh breaks reflection-equivariance, an uncalibratable operator floor blocks conservation decidability, so the admissibility gate (§3.3) locates where each property survives, and the typed verdict (§3.5) records that location.

### 3.3 Domain-Validity Rubric

We treat screening as deciding a single admissibility predicate. A candidate relation is an *admissible MR* when four conditions hold together: (i) it has a physical or software basis; (ii) its transformation preconditions are satisfied; (iii) its boundary conditions and output mapping remain compatible after the transformation; and (iv) it is numerically decidable, meaning the verdict tolerance dominates the intrinsic error floor of the operator that measures the relation. Conditions (i)-(iii) establish that the relation is meaningful for the transformed case; condition (iv) establishes that a violation can be told apart from numerical noise. All four conditions are gates that can reject or defer a candidate; provenance recording makes each gate auditable. The six rubric criteria below are the recorded, auditable form of these four conditions.

Each candidate MR is screened using a rubric with six criteria.

**Physical basis.** The relation must cite its source: governing equation, boundary condition, nondimensional law, representation property, numerical assumption, or implementation contract.

**Transformation preconditions.** The source-to-follow-up transformation must state what is changed and what is preserved. For example, a mirror relation must specify how coordinates, vector components, node types, and boundary labels transform.

**Boundary-condition compatibility.** The relation must hold under the boundary conditions of the transformed case. If the transformation changes the physical meaning of a boundary, the candidate is rejected or marked as an OOD stress test rather than a physics-preserving MR.

**Output mapping.** The expected relation among outputs must be measurable. A relation that cannot be mapped to available output fields is not executable.

**Metric and tolerance.** The verdict rule must define a metric and a tolerance. The tolerance may come from numerical precision, solver reference behavior, calibration data, repeated-run variability, or expert thresholding, but the source must be recorded. This criterion carries condition (iv): the tolerance must be shown to dominate the intrinsic error floor of the measuring operator. When that floor is itself uncalibratable, as for an absolute discrete-divergence relation whose reference field already carries non-negligible divergence, the relation is deferred rather than executed, because a violation could not be separated from the operator's own discretization error.

**Failure diagnosability.** The relation should indicate what kind of failure or boundary condition it can help interpret. If every possible violation has the same ambiguous meaning, the relation is weak evidence and should be treated cautiously.

The rubric outputs one of four screening decisions:

- retained as executable MR;
- retained as OOD stress relation, not physics-preserving MR;
- rejected as invalid or underspecified;
- deferred pending missing evidence, such as a discrete operator or threshold.

### 3.4 MR Card and Executable Asset Format

A retained MR is represented as an MR card. The card records:

- MR identifier and name;
- source category;
- physical or software basis;
- source-case schema;
- follow-up transformation;
- transformation preconditions;
- boundary-condition compatibility;
- output mapping;
- metric;
- tolerance and provenance;
- expected verdict classes;
- exclusion rules;
- artifact schema;
- expected fault or boundary interpretation.

Executable assets are generated from MR cards. Each asset includes transformation code, runner configuration, metric computation, verdict logic, and artifact recording. The asset format is intended to make MR execution auditable: another researcher should be able to inspect why a relation was retained, how the follow-up case was generated, how the comparison was made, and what a violation means.

### 3.5 Relation-Level Verdicts

An MR execution can produce several verdicts:

- **pass:** the relation holds within the stated tolerance;
- **fail:** the relation is violated within its valid domain;
- **skip:** the case cannot be run because a declared precondition is missing;
- **out-of-relation-domain:** the transformation produced a case outside the relation's validity domain;
- **numerical-tolerance issue:** the evidence is dominated by threshold or numerical-resolution uncertainty;
- **inconclusive:** the artifact is insufficient to decide.

This scheme prevents a common overclaim: not every relation violation is a program fault. A violation may reveal a model inconsistency, but it may also reveal that the MR was applied outside its domain, that the threshold was too tight, that the mesh operator was unsuitable, or that the case is not comparable.

It is useful to read these verdicts as regions of a two-dimensional space rather than as a flat list. One axis is the relation-violation magnitude, how far the measured quantity exceeds the tolerance, for example the violation-to-tolerance ratio or the violation-to-floor ratio V/floor. The other axis is the domain-violation magnitude, how far the transformed case lies outside the relation's validity domain, signalled by precondition violation, geometry mismatch, boundary-condition mismatch, or operator inadmissibility. Low domain-violation with low relation-violation is pass; low domain-violation with high relation-violation is the only region that may be read as SUT inconsistency; high domain-violation is out-of-relation-domain or, near the boundary, OOD-stress; a relation-violation that sits within the error floor is a numerical-tolerance issue. This decomposition is what keeps a model-level violation from being confused with a relation applied outside its domain, and it makes condition (iv) of the admissibility predicate explicit at verdict time.

In the present study the relation-violation axis is quantitative, mirror-y reports V/floor, and for the mirror-y relation the domain-violation axis is now operationalized as a continuous geometric score D = m/(m+1), where m is the worst reflected-node placement error in median-edge-length units (committed; see §5.1). The synthetic symmetric mesh scores D ≈ 0 (a reflected node lands on an existing node, so the exact relation is admissible) and the real asymmetric eval mesh scores D = 0.51 (a reflected node lands about one edge length off, so the exact relation is out-of-relation-domain and is downgraded to an approximate OOD-stress probe). The same construction now covers every executed MR class from committed measurements: the permutation-class relations and the PINN closed-form mirror relations are exact-by-construction (D = 0), the conservation relations score the committed open-boundary flux imbalance (MGN D = 0.036; Burgers D = 0.042; heat D = 0), and one roster-level entry is explicitly marked not operationalizable from committed data. These are per-relation operationalizations: the m measures differ in units across classes, so D is a per-relation normalized coordinate, not a cross-relation calibrated metric, and D values cannot be averaged or ranked across MR classes. They should be read per relation, not as a calibrated boundary measurement. Cross-relation calibration is left to future work.

### 3.6 Hierarchical Interpretation Protocol

We organize retained MRs using the three-level classification of metamorphic relations for scientific-computing programs of Yang et al. [yang2020hierarchical]: physical-model, computational-model, and code-model relations. For learned mesh surrogates, the computational-model level includes graph representation and message-passing discretization assumptions.

We use this hierarchy as a predeclared interpretation protocol that maps representation-level MRs to possible graph encoding or adapter problems, physical-model MRs to possible continuity, symmetry, or similarity violations, and code-model MRs to possible determinism, rollout, or implementation issues. At this stage, this is a localization protocol, not a validated localization model. It becomes validated only if seeded faults or mutants with known layers are used to evaluate the inference rule. Section 5.3 reports a first bounded test of this protocol: against an injected-fault catalogue the continuity MR responded to boundary and normalization-scale faults while the symmetry MR responded to physical-channel and mesh-adjacency faults, which is suggestive evidence for the protocol's direction but not, on one SUT and one catalogue, a validated localization model.

## 4. Empirical Design

### 4.1 Subject Systems

The study evaluates the workflow on three groups of subject systems, all with
recorded checkpoints, datasets, seeds, and environments in the experiment ledger.

**Cylinder-flow surrogates (primary).** (i) A trained MeshGraphNets cylinder-flow
surrogate and its K=6 checkpoint roster (four seed replicas plus one wider and one
deeper configuration), all trained from the same trainer and DeepMind cylinder-flow
data; (ii) a same-domain S4/S5 wider/deeper MeshGraphNet variant package; (iii) a
newly trained non-message-passing PointMLP coordinate network on the same source
cases; and (iv) the NVIDIA PhysicsNeMo `MeshGraphNet` production implementation
evaluated on official DeepMind cylinder_flow TFRecords, an independent
production-framework implementation of the same task.

**Second CFD task (primary).** The NVIDIA PhysicsNeMo `MeshGraphNet`, trained and
evaluated on the official DeepMind **airfoil** dataset (SU2-simulated compressible
transonic flow over an aerofoil), a different physical regime (compressible) and a
second official dataset, used to test whether the admissibility predicate produces
the physically correct typed verdict structure when the governing physics changes.

**Cross-family replication subjects (supporting).** A K=15 PINN roster (fifteen 2D
Burgers and fifteen heat-equation seeds) and six trained FNO-2D checkpoints over the
same two PDE families, used to test whether the admissibility predicate and MR
rewrites transfer outside mesh-based surrogates.

**External witness runtime (secondary).** The read-only Minimum-MR-SubSet
repository supplies a held-out cylinder-flow MGN runtime witness and two trained
PINN PDE witnesses that are rerun locally for provenance.

Because the primary subjects share one task and dataset, the cylinder-flow
results are framed as same-task multi-architecture evidence, not as evidence for
all neural fluid surrogates.

### 4.2 Planned MR Classes

The initial MR set will be grouped into six classes:

**Representation MRs:** node permutation, face-order invariance, and encoding consistency.

**Geometric and symmetry MRs:** mirror-y equivariance and rigid transformation candidates, retained only under boundary-compatible conditions.

**Continuity and constraint MRs:** discrete divergence or mass-continuity checks with explicit mesh weighting and boundary treatment.

**Nondimensional similarity MRs:** Reynolds-Strouhal or scaling candidates, retained only under nondimensional and regime-compatibility checks.

**Numerical stability MRs:** small perturbation stability, mesh perturbation, or refinement consistency candidates.

**Temporal and implementation MRs:** rollout prefix consistency, deterministic execution, and conditional cross-implementation comparison.

Time reversal is excluded as a retained MR for viscous cylinder flow. Divergence is treated as an incompressible continuity or mass-conservation constraint, not as a Noether-derived conservation law.

### 4.3 Baselines and Comparators

The study uses four comparator families, all secondary to the main MR-asset workflow.

**LLM-simulated expert MR design.** Expert-LLMs propose MRs without the rubric. This baseline estimates what the proposed rubric adds beyond unguided elicitation; it is a secondary scope contrast rather than a human-expert benchmark.

**Generic MR-generation scope contrast.** Generic MR identification or generation methods are applied as far as their assumptions allow. This comparator shows where domain-validity information is needed for SciML.

**LLM-assisted candidate generation.** An LLM generates candidate MRs from prompts containing equations, SUT descriptions, and candidate relation categories. The LLM is treated only as a candidate-generation and material-organization tool. It does not judge MR validity. Prompt logs, model/version, temperature, candidate lists, and rubric decisions will be recorded.

**Rollout-accuracy baseline.** Standard rollout error is reported to compare pointwise predictive evidence with relation-level evidence. The goal is not to prove that MRs are better than accuracy, but to identify whether they answer a different validation question.

Where feasible, residual-based or UQ metrics will be reported as diagnostic comparators. They will not be treated as MRs unless paired with a source/follow-up transformation and explicit verdict rule.

### 4.4 Efficacy Parameters and Metrics

The primary efficacy parameters are:

- candidate retention rate: the proportion of candidate MRs retained by the rubric;
- executable MR rate: the proportion of retained MRs that can be executed on each SUT;
- MR violation rate: the proportion of valid-domain executions that fail the relation;
- violation magnitude: the metric distance from the stated tolerance;
- fault-detection rate: the proportion of seeded faults or mutants detected by at least one retained MR;
- boundary characterization: the transformation regions or parameter bins associated with elevated violation rates;
- interpretation yield: the proportion of failed executions assigned a non-ambiguous verdict category.

Secondary parameters include:

- MR construction cost;
- inter-rater agreement for rubric decisions;
- flakiness rate across repeated executions;
- localization agreement with seeded-fault layers;
- complementarity with rollout accuracy, measured by cases where accuracy and MR verdicts provide different boundary information.

### 4.5 Statistical Reporting

The study reports inferential statistics wherever the sampling structure
supports them, and clearly labels descriptive counts where it does not. Binary
detector outcomes over the unified fault catalogue carry Wilson score intervals
per detector; continuous violation magnitudes are compared with Wilcoxon
signed-rank tests and Cliff's delta effect sizes; rollout-accuracy and roster
medians carry bootstrap confidence intervals; and the operator-floor sweep
reports a log-log slope with a 95% confidence interval. Where repeated cells are
not independent samples, consecutive frames of one trajectory, or
checkpoint-by-trajectory grids within one architecture family, the paper
reports the counts as descriptive cell summaries and says so, rather than
presenting them as independent-trial inference. Small-sample results emphasize
effect sizes and intervals over significance claims.

### 4.6 Ethics, Integrity, and Reproducibility

The current study does not involve human subjects, personal data, or private sensitive information. The main ethical and integrity issues are research transparency, AI use, and reproducibility.

All SUT versions, datasets, checkpoints, scripts, and run logs should be recorded when licensing permits. Failed, skipped, and inconclusive cases must remain in the experiment ledger. LLM use is restricted to candidate generation and evidence organization; it is not used as a final judge of MR validity. No candidate MR should be described as valid unless it passes the rubric and has a corresponding MR card. No OOD violation should be described as a program fault without the verdict evidence needed to support that interpretation.

Third-party code, datasets, and model checkpoints will be used according to their licenses. If any artifact cannot be redistributed, the paper will provide access instructions and record the limitation.

## 5. Results

The *primary* evidence is the cylinder-flow case study (§5.3–§5.6), including
the same-task multi-architecture executions and the PhysicsNeMo
production-framework workflow; the cross-family PINN/FNO transfer (§5.8) is
*supporting*, and the baseline comparators and external witness audits (§5.7)
are *secondary* context. Section 5.9 states the boundary of the evidence.

### 5.1 Claim-to-Evidence Map

The contribution claims and the controls that calibrate them are below. The
architecture-replication, cross-family, baseline, and external-witness rows, 
with their committed evidence paths, are in Appendix A; the authoritative
runtime mapping is `claim-ledger.yml`.

| Claim | Status | Boundary |
|---|---|---|
| Domain-validity rubric | Supported method claim | Establishes an auditable screening rule; physical validity still depends on each relation's stated preconditions. |
| MR-card executable assets | Supported asset/workflow claim | Some cards remain protocol assets pending matched SUT evidence. |
| Node-permutation sanity check | Observed pilot | One representation-contract path on one pilot case. |
| Conservation diagnostic | Observed; absolute deferred | Reference-relative guard only; absolute conservation remains deferred. |
| Mirror-y OOD stress (PC6-mirror-y-ood-stress) | Observed bounded pilot | Failed on 10 of 10 recorded eval frames; not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim. |
| Exact mirror-y symmetric mesh | Observed control | Exact relation admissible and fails (rel L2 1.10) on a synthetic OOD symmetric mesh; binary equivariance evidence. |
| Rollout-accuracy diagnostic | Observed control | Same-SUT one-step median relative L2 0.0216; mirror-y is ~34x larger. |
| Operator-floor resolution | Observed | Log-log slope 0.984, 95% CI [0.975, 0.992], R² = 0.9999 over nine resolutions; closed-form floor for the deployed mesh (predictor within 0.5% plus a-priori bound, §5.5). |
| PC10-seeded-fault-detection | Observed | Detector stress test: MRs catch 5/10 injected mutants with class-specific response patterns. |

### 5.2 MR-Card-to-Verdict Map

| MR card | Rubric decision | Runtime verdict | What the verdict can and cannot mean |
|---|---|---|---|
| Node permutation equivariance | Retained as representation MR | pass sanity; relative L2 = 0.0 | Supports the executable path and representation contract for one case; does not establish model reliability. |
| Mirror-y equivariance (asymmetric eval mesh) | Exact relation out-of-relation-domain; downgraded to approximate OOD-stress | S0 pilot: fail on 10 of 10 recorded eval frames; primary upgrade: 180/180 fail across K=6 x 3 trajectories x 10 | Shows bounded within-family OOD-stress violation across three held-out trajectories; not by itself exact symmetry, cross-SUT, or geometry-independent evidence. |
| Mirror-y equivariance (synthetic symmetric mesh) | Exact relation admissible (bijection verified, offset < 1e-12, type-match 1.0) | S0 pilot: fail, relative L2 1.10; primary upgrade: 18/18 fail across K=6 x 3 input seeds | Shows exact-symmetry failure where the relation is admissible; synthetic no-obstacle OOD meshes, not accuracy or cross-SUT evidence. |
| Discrete divergence / conservation | Absolute mass-conservation MR deferred; reference-relative diagnostic retained | S0 pilot inconclusive: reference-relative non-regression guard; primary upgrade: 162/162 pass across K=6 x 3 trajectories x 9 | Reference-relative diagnostic only; the absolute conservation relation remains deferred. |
| MGN S4/S5 variant workflow | Node permutation admitted; mirror OOD/conservation diagnostic/exact-symmetry decisions recorded | 2/2 node-permutation passes; 60/60 mirror OOD failures; 54/54 conservation-diagnostic passes; 6/6 exact-symmetry failures | Same-domain MGN variant evidence, not an external SUT family. |
| PointMLP cylinder workflow | Node permutation admitted; mirror OOD/conservation diagnostic/exact-symmetry decisions recorded | 9/9 node-permutation passes; 10/10 mirror OOD failures; 9/9 conservation-diagnostic passes; 3/3 exact-symmetry failures | Different non-MGN cylinder SUT; not PhysicsNeMo/EchoWave or production CFD evidence. |
| PhysicsNeMo MGN scaled workflow | Node permutation admitted; mirror OOD/conservation diagnostic decisions recorded | Node permutation exact on 40/40 trajectories (relative L2 0.0); mirror-y OOD-stress fail on 40/40; rollout and conservation diagnostic ledgers recorded per trajectory | Official production architecture on 25+40 official trajectories at CPU scale; no full-scale production pass/fail rate, no official-checkpoint claim, and not external-aerodynamics evidence. |
| FNO periodic translation and conservation | Translation admitted; periodic discrete-conservation MR admitted-with-reference-floor; Dirichlet translation rejected | FNO primary workflow upgrade: 24/24 translation passes, 24/24 conservation failures, and 6/6 rejected Dirichlet exact-MR executions | Full rubric-to-verdict FNO evidence with raw source/follow-up outputs and per-case ledgers; outside cylinder-flow and broad neural-operator claims. |

### 5.3 Within-SUT pilot evidence (single SUT, single checkpoint)

All pilots run on one real trained MeshGraphNets cylinder-flow surrogate
(read-only `Minimum-MR-SubSet`, checkpoint sha256 `cf281f85…`). They exercise
three different rubric outcomes and are scoped accordingly; raw outputs, manifests,
and metric ledgers are committed (see §5.1).

- **Representation MR (correctness sanity check).** Node-permutation equivariance
  holds to machine precision (relative L2 = 0.0 at tolerance 1e-6). This is a
  structural property of message-passing and is reported only as a pipeline
  sanity check, not as model capability.
- **Geometric MR (out-of-relation-domain, approximate OOD-stress frame rate).**
  The rubric classifies exact mirror-y equivariance as out-of-relation-domain for
  this mesh, the reflection is non-bijective, the worst reflected-node mismatch is
  about one edge length, and the cylinder is off-centre by 7.2 mm, and downgrades
  it to an approximate nearest-neighbour OOD-stress probe scored against a
  same-space mapping-error floor. The probe failed on 10 of 10 recorded eval frames
  (median relative L2 0.737, median V/floor 3.96, floor range 3.02-5.55x),
  with no frame skipped or inconclusive. This is a bounded within-SUT frame-level OOD-stress result:
  one SUT, one checkpoint, one MR, one eval trajectory. The frames are consecutive
  rather than independent, so the 10/10 binomial interval is wide ([0.69, 1.00]); and because the
  mapping-error floor derives from the same geometric mismatch that triggered the
  downgrade, V/floor alone cannot separate a model-level violation from a geometric
  artifact, the symmetric-mesh run below resolves that ambiguity.
- **Continuity MR (deferred absolute relation, reference-relative diagnostic).** A
  P1 discrete-divergence operator yields non-negligible divergence even for the
  ground-truth field on this coarse mesh (dimensionless reference divergence ≈
  0.037), so an absolute divergence-free tolerance is not calibratable and the
  absolute mass-conservation relation stays deferred. As a reference-relative
  diagnostic, the surrogate's predicted next-state divergence stays within ~0.4–0.8%
  of the reference (the interior-only ratio confirms interior behaviour, not boundary imposition). Because the reference divergence is not yet decomposed into operator
  error, solver artefact, or non-solenoidal data, the ratio is a non-regression guard, not a conservation measurement: with a 50% threshold on two frames, a "pass"
  means "does not regress conservation by more than 50% on those frames," not
  "conserves mass."

- **Rollout-accuracy diagnostic (accuracy comparator on the same SUT).** On the same
  eval trajectory, the surrogate's one-step prediction error has median relative L2
  0.0216 (mean 0.044) over the nine recorded transitions. The surrogate is accurate
  in-distribution to a few percent per step, yet the mirror-y OOD-stress violation
  (median 0.737) is about 34 times the median accuracy. The two quantities are
  relative L2 of different objects, so this is an order-of-magnitude gap rather than a precise
  factor, within-SUT evidence that the relation diagnostic and rollout accuracy answer
  different questions; it is one-step, not a free-running rollout-stability result.
- **Exact mirror-y on a symmetric mesh (admissible relation, out-of-sample test).** To
  test whether the finding survives once the exact relation is admissible, we built a
  synthetic channel mesh provably symmetric about the centerline (verified bijection:
  node-type match 1.0, reflection offset < 1e-12, edge set invariant), so the predicate
  retains the exact relation. On one constructed input the surrogate violated exact
  mirror-y equivariance with relative L2 1.10 (fail). Equivariance is oracle-free and
  structural, a mirror-equivariant model would satisfy it to machine precision
  regardless of accuracy, so the nonzero result is not a geometric artifact, and it is
  an out-of-sample check the predicate did not fit to the original pilots. A normalizer
  control isolates the cause: zeroing the normalizer's transverse-velocity mean changes
  the violation only from 1.1032 to 1.1014, so it is dominated by the learned
  message-passing weights, which carry no equivariance constraint. The no-obstacle
  channel is itself deeply OOD, so the 1.10 confirms the surrogate carries no exact
  mirror-y constraint; it is a binary equivariance failure, not a
  calibrated in-distribution magnitude comparable to the asymmetric-mesh 0.737. It is one input on one mesh.
- **Seeded-fault detection (do the MRs catch known faults?).** We re-implemented,
  from the read-only Minimum-MR-SubSet witness taxonomy, an injected-fault catalogue of
  10 pipeline faults across five fault classes (boundary-condition, mesh-adjacency,
  normalization-scale, temporal-rollout, physical-channel), and used the paper's own
  MRs as detectors on the model's predicted update. The continuity MR detected the two
  boundary-condition faults and the gross normalization fault (divergence ratio
  3.8–10.6 vs the 1.5 threshold); the symmetry MR detected a physical-channel and a
  mesh-adjacency fault (violation rising 69–142% above baseline); node-permutation
  equivariance detected none, because these faults preserve node-relabeling invariance.
  5 of 10 mutants were detected by at least one MR, and the detections separate by MR
  class, continuity to boundary/scale faults, symmetry to physical-channel/adjacency
  faults, a first bounded test of the §3.6 interpretation protocol, suggestive rather
  than a validation. Three boundaries: the detected faults are gross corruptions that
  any divergence- or symmetry-sensitive detector would catch; the edge-drop fault is a
  near-miss (32% mirror-y change vs the 50% threshold) and the boundary faults are
  invisible to mirror-y by construction; and the remaining undetected faults shift the
  absolute output without crossing the scored-quantity thresholds, delimiting where
  these MRs are structurally insensitive. It is one SUT, one checkpoint, one
  injected-fault catalogue.

### 5.4 Multi-checkpoint, multi-trajectory, and multi-architecture replication

To address the single-checkpoint and thin-denominator objections without converting the study into a cross-SUT claim, the five within-SUT measurements are replayed on the K=6 MeshGraphNets roster (§4.1) over the first three official DeepMind held-out test trajectories. Per-trajectory/checkpoint manifests record source-case hashes, checkpoint hashes, and runner outputs (see §5.1).

The compact reading is: node-permutation equivariance is exact on all six checkpoints; the primary empirical scope upgrade gives a K=6 x 3 trajectories x 10 mirror-y OOD-stress grid with 180/180 failures (median relative L2 0.828, median V/floor 5.28); the K=6 x 3 trajectories x 9 conservation-transition grid passes the reference-relative diagnostic on 162/162 cells (max ratio 1.287, max interior ratio 1.049), while absolute conservation remains deferred; and the K=6 x 3 exact-symmetric-mesh input grid fails on 18/18 cells (median relative L2 1.097). Rollout relative L2 stays near 0.022 (CI [0.0217, 0.0224]), so the mirror-y violation remains much larger than the in-distribution one-step error across the roster. The trajectory-dependent cells are clustered by checkpoint, held-out test trajectory, and frame; the upgrade removes the single-source-trajectory denominator while remaining within one architecture family and one dataset, so the report's Wilson bounds are descriptive cell-count summaries, not independent-trial inference.

**Same-task multi-architecture replication.** Three further cylinder-flow executions test whether the verdict pattern is an artifact of one implementation. A same-domain S4/S5 wider/deeper MeshGraphNet variant package reproduces the pattern (2/2 node-permutation passes, 60/60 mirror OOD failures, 54/54 conservation-diagnostic passes, 6/6 exact-symmetry failures). A newly trained PointMLP coordinate network, a different architecture class with no message passing, reproduces it as well (9/9 node-permutation passes, 10/10 mirror OOD failures, 9/9 conservation-diagnostic passes, 3/3 exact-symmetry failures, median rollout relative L2 0.0298). Third, the NVIDIA PhysicsNeMo `MeshGraphNet` production implementation, in its official architecture (processor size 15, hidden 128, 2.33M parameters), is trained on the first 25 official DeepMind cylinder_flow train trajectories and evaluated per-trajectory on the first 40 official test trajectories: node-permutation equivariance is exact on 40/40 trajectories and mirror-y fails as OOD stress on 40/40, reproducing the pattern within a production framework rather than a research codebase. (This is a CPU-scale evaluation, not the official 10M-step schedule, not an official NVIDIA checkpoint, and not the full benchmark; the elevated one-step rollout error reflects the bounded training budget and is no closed-loop accuracy claim.) The same admissibility predicate, applied unchanged, produced the same typed decisions on all three, replicating the verdict pattern across architectures on one task and dataset.

### 5.4.1 Second task: compressible airfoil flow (the typed verdict changes with the physics)

The strongest test of a domain-validity gate is not whether it repeats a verdict on the same physics, but whether it produces the *correct, different* verdict when the physics changes. We therefore apply the identical four-condition admissibility predicate to a genuinely second CFD task on a second official dataset: the DeepMind **airfoil** benchmark, SU2-simulated compressible transonic flow over an aerofoil (5,233-node meshes, density, pressure, and velocity fields), distinct from the incompressible cylinder-flow task in both physics and data source. The same official PhysicsNeMo `MeshGraphNet` (2.33M-parameter official configuration: hidden width 128, 15 processor steps) is trained for 40 epochs on 100 official airfoil train trajectories (GPU-trained to a converged final loss near 0.14) across a K=6 checkpoint roster and evaluated per-trajectory on 40 official test trajectories, yielding 240 (checkpoint, trajectory) pairs.

The predicate produces a **different typed inadmissibility structure**, and the difference is the result:

- **Node-permutation equivariance is admitted and exact** (240/240 cells, relative L2 0.0). This relation is a representation contract and is training-independent, so it transfers to the new task unchanged.
- **Incompressible divergence-free continuity is *rejected* at the physical-basis gate (condition i).** On the airfoil flow the density varies by a median factor of 2.13x across the field (n=40 trajectories across the K=6 roster, 240/240 node-permutation exact), so the incompressible assumption $\nabla\cdot u = 0$ is physically false for this SUT, and the measured reference $\nabla\cdot u$ is correspondingly far from zero. This is the same relation that, on cylinder flow, passes conditions (i)-(iii) and is only *deferred* at the numerical-decidability gate (condition iv). The gate thus assigns the relation a categorically different verdict *type* on the two tasks, deferred-uncalibratable versus rejected-domain-invalid, for the physically correct reason in each case.
- **Compressible unsteady mass conservation** $\partial_t\rho + \nabla\cdot(\rho u)=0$ is the physically-correct replacement; its absolute discrete form is deferred (the P1 operator floor on a coarse transonic mesh is uncalibratable, exactly as for cylinder continuity), and a reference-relative diagnostic is recorded (median surrogate/reference residual ratio 1.01).
- **Mirror-y chord symmetry is rejected at the boundary-precondition gate (condition iii):** the SU2 trajectories carry a non-zero angle of attack, so reflection about the chord violates the boundary-value problem's symmetry preconditions.

The one-step rollout error remains moderate at this training budget (median relative L2 0.92) and is reported only as a training-state diagnostic; crucially, none of the four typed verdicts above depends on rollout quality, the admission rests on a representation contract and the rejections/deferral on physical and numerical reasoning about the relation, not on the surrogate's accuracy. This is precisely why the typed verdict structure transfers and discriminates across tasks. It is a primary-scale second-task roster (official MeshGraphNet architecture, 240 checkpoint-by-trajectory cells), not a SOTA-accuracy or official-checkpoint airfoil result.

### 5.5 Operator-floor resolution sweep (calibration of numerical decidability)

The numerical-decidability gate is checked by a symmetric-mesh P1 discrete-divergence sweep. Over nine resolutions (245,120 cells at the finest), the measured log--log slope is 0.984 with 95% CI [0.975, 0.992] and R² = 0.9999, matching the expected O(h) trend and supporting the use of the operator's intrinsic error floor in the continuity-MR verdict.

Beyond the slope, the *absolute* floor is closed-form for the concrete deployed-scale mesh. Because the P1 operator is exact on affine fields and the analytic reference field is divergence-free, the measured floor equals the geometry-weighted sum of the operator's second-order Lagrange remainders exactly; a leading-order predictor built from the analytic Hessian at each cell centroid matches the area-weighted RMS measured floor to within 0.5% at the deployed scale (measured 1.337 vs predicted 1.343, ratio 0.996) and converges to it as the mesh refines (0.999 at h0/2, 1.000 at h0/4), while a rigorous a-priori upper bound from the analytic Hessian's global spectral norm dominates the measured floor in RMS and pointwise at every resolution. The numerical-decidability gate therefore rests on a derived floor, not an empirical estimate, for this mesh; the same floor reproduces on a second, unstructured Delaunay topology (a jittered-grid triangulation, worst triangle angle about 14 degrees, over the same domain and reference field) with log--log slope 0.983 (95% CI [0.953, 1.014], R² = 0.999) and a matched-resolution unstructured-over-structured floor ratio of 1.06 median and 1.33 maximum, so the verdict is empirically topology-stable across these two mesh families, while a general bound for arbitrary unstructured meshes remains future work. The manuscript treats absolute conservation on the deployed mesh as deferred and reports only the reference-relative non-regression guard as executable evidence.

### 5.6 Fault-detection robustness across the multi-checkpoint roster

The seeded-fault experiment is a detector stress test rather than a real-world defect-rate estimate. Against the 10-mutant injected-fault catalogue (PC10-seeded-fault-detection), the MR set catches 5 of 10 mutants and repeats the by-class pattern across the K=6 roster: continuity catches boundary/scale faults, symmetry catches physical-channel/adjacency faults, and node permutation catches representation-ordering faults. The refined R3 sweep shows the blind region is a knife-edge / measure-zero blind subspace: the node-permutation detector catches the injected edge-ordering fault at fractions through 0.99, while the full replacement remains invisible to the intended detector.

**Adversarial mutants (R4).** Two additional mutants probe whether the blind spot is a subspace, not a point. A1 is detected by mirror-y through magnitude shift, with node-permutation 0/6 and conservation 0/6, so it is not evidence that the node-permutation or conservation detectors cover the blind subspace. A2 escapes every detector, confirming the subspace boundary that the catalogue must disclose. The pattern reflects the detectors' coverage geometry: each MR scores a single invariant (relabeling equivariance, the divergence ratio, or y-symmetry), so a fault is caught only when it perturbs a measured invariant and is structurally invisible when it preserves all of them, closing the blind region therefore calls for additional MRs that probe the uncovered directions, not for more mutants of the same kind.

**Unified catalogue and statistics.** Phase 3 merges 10 executed canonical MGN mutants, 2 executed adversarial MGN mutants, 24 closed-form output-level PINN probes, and 24 closed-form output-level FNO probes into a 60-entry unified fault catalogue (see §5.1). The artifact reports precision/recall with Wilson intervals: node-permutation 1.00/1.00, conservation 1.00/0.81, and mirror-y 0.94/0.55; it also reports Wilcoxon and Cliff's δ effect-size summaries, including PINN MR-B diffusion-vs-Burgers δ = 0.78 (large) with paired Wilcoxon p = 0.5 at n = 3. The PINN and FNO entries are closed-form probes with no retraining, not retrained mutant checkpoints. Re-run with realistic mechanism-level surrogate bugs that are not tailored to the relations (boundary mis-scaling, renormalization, channel swap, region dropout, fixed Gaussian noise, spatial shift, sharpening, mode truncation; per-fault output perturbation recorded), the by-class structure emerges rather than being constructed: on both a spectral FNO and a pointwise Burgers PINN, detection partitions by whether a fault changes the conserved channel integral and whether it breaks the symmetry or translation relation. The single-relation cells are near-definitional, since the conservation relation is itself the test of whether the integral changed, so the load-bearing and falsifiable content is coverage completeness: a fault preserving every measured invariant is predicted in advance, from the fault operator alone, to be invisible to the whole relation suite, and on both architectures every such fault is detected by no relation, with no falsifying case. This blindness is independent of how badly the fault degrades the output --- a transport fault corrupts the PINN field by 0.63 relative L2 yet stays invisible to every relation, while on the smoother FNO fields no invariant-preserving fault reaches a comparable magnitude, so the practical reach of the blind region is itself field-structure dependent. The trained-mutant MeshGraphNets and PointMLP evidence and the realistic-fault FNO/PINN evidence are not interchangeable; this is bounded cross-architecture evidence for a falsifiable coverage geometry, not generalized to all relations or architectures.

### 5.7 LLM and generic-MR baselines: Secondary baseline and external-scope audit

LLM baselines are secondary exploratory scope contrasts. Three expert-LLMs proposed 25 candidate MRs (24 unique) without access to the rubric. Three independent rater models then applied the four-condition predicate by majority vote: 4 candidates were retained, 2 downgraded to OOD-stress, 13 rejected, and 6 deferred. The 76% rejection/deferral rate and the absence of any novel retained candidate show an admissibility gap between unguided elicitation and validity-gated MR construction; this is an automated LLM-simulated expert baseline rather than a human-expert benchmark.

**Generic-MR generation.** A domain-blind generic-MR catalogue contributes the complementary scope contrast: only 3/13 templates are admitted, and all three coincide with this paper's MR families or software-contract variants. The dominant rejection reasons are missing physical/software basis and boundary/output incompatibility.

**Three-arm complementarity and a measured gate value.** On the converged PointMLP SUT, over a 20-fault catalogue spanning four predeclared fault classes, three arms are contrasted: the validity-gated MR suite, a rollout-accuracy monitor (rollout L2 ≥ 2× baseline), and ungated generic templates. The MR suite and the accuracy monitor are complementary: the suite detects 13/20 faults (Wilson 95% CI [0.43, 0.82]) and the monitor 6/20, with a 2×2 split of MR-only 9, accuracy-only 2, both 4, neither 5, so nine faults are relation violations the monitor leaves inside its 2× baseline band and two degrade rollout without crossing a relation threshold. The third arm makes the gate's value measurable rather than asserted: the single gate-admitted generic template raises no baseline false positive on the fault-free correct SUT (0%), whereas all six gate-rejected templates fire on it (100% baseline false positive), so the admissibility gate is exactly what removes the false-alarming detectors. The same knife-edge symmetry blind spot (§5.6) recurs on this row-wise architecture. This is complementarity and a measured gate value, reported with descriptive Wilson CIs and never a superiority ranking.

**LLM-generated MRs.** The one-shot LLM baseline generated K=8 candidates; vendor-disjoint raters (`glm-5.1`, `kimi-k2.6`, `deepseek-v4-flash`) scored them. 7/8 reached panel-majority valid, six overlap this paper's MR families, and the most informative disagreement is the centerline-reflection case where a rater objected to non-bijectivity on the asymmetric mesh. Fleiss kappa is 0.077, a small-sample paradox paired with PRA 0.79 / item-unanimous 0.75.

**Minimum-MR-SubSet audit and primary reruns.** The sibling repository audit at commit `9ef862ec37335b4834d0a1fb38b4b613af702f34` records 70 real ABD instances, including 20 true-fault-class rows. We locally reran three SciML/PDE witnesses: held-out cylinder-flow MGN (`PASS_WITNESS`, kstar = 6, four active true fault classes, collapse false) and trained Burgers2D/Diffusion2D PINNs (`PASS_WITNESS`, kstar = 1 each, five active classes each; Diffusion includes Neumann mass conservation). The PINN reruns add second trained-SUT/PDE primary witness evidence, while remaining one-seed witnesses rather than cross-SUT rates.

### 5.8 Cross-family transfer: PINN and FNO subjects (supporting)

The cross-family executions are not decoration: they test the two claims that the cylinder-flow case study cannot test by itself. First, that the admissibility predicate is *family-agnostic*, the same four conditions, applied unchanged, produce typed decisions on pointwise PINNs and spectral FNOs (admitting periodic translation, rejecting Dirichlet translation as boundary-incompatible, ruling MR-A vacuous for pointwise MLPs). Second, that the conservation MR class produces *full executable verdicts wherever its floor is calibratable*: the FNO periodic discrete-conservation MR executes end-to-end against a case-level reference floor and fails 24/24, and the PINN reference-relative conservation passes 30/30, while the MGN open-boundary absolute variant is the one member of the class the gate correctly refuses to execute. The deferral on cylinder flow is therefore the fail-closed gate discriminating rather than a missing verdict.

#### 5.8.1 Cross-family PINN extension (K=6 roster)

The PINN extension checks whether the predicate and MR rewrites can be carried outside MeshGraphNets. The K=15 PINN roster contains fifteen Burgers and fifteen heat-equation seeds. MR-A remains vacuous by construction for pointwise MLP PINNs; the two non-trivial MR checks are mirror-y and reference-relative conservation. MR-B passes on 13/15 Burgers seeds (mean 0.712, CI [0.583, 0.875]; Wilson pass-rate CI [0.62, 0.96]) but is mixed on heat with 7/15 passing (mean 1.495, CI [1.142, 1.897]; Wilson pass-rate CI [0.25, 0.70]). MR-C passes on all 15/15 of both PDEs (Wilson CI [0.80, 1.00]): Burgers mean 1.007 (CI [0.997, 1.017]) and heat mean 1.006 (CI [0.988, 1.022]). This is a two-PDE seed roster rather than a PINN-vs-MGN benchmark.


#### 5.8.2 FNO primary workflow upgrade (K=6)

The **FNO primary workflow upgrade** converts the earlier FNO roster into a second trained primary execution. Six torch FNO-2D checkpoints cover Burgers and heat. For each checkpoint and four held-out generated periodic finite-difference cases, the workflow records rubric decisions, source and follow-up tensors, mapped outputs, metric ledgers, and relation verdicts. Periodic integer translation is admitted and yields **24/24 translation passes** (maximum relative-L2 violation below 1e-5). The **periodic discrete-conservation MR** is admitted-with-reference-floor because the finite-difference target supplies a case-level channel-sum drift floor; the trained FNO outputs exceed that calibrated floor on **24/24 conservation failures**. The Dirichlet translation candidate is rejected for 6/6 SUTs because it changes the boundary-value problem and is not executed as an exact MR. This is **not only admissibility evidence**: it is a full rubric-to-verdict FNO execution with raw source/follow-up outputs and per-case ledgers, outside cylinder-flow and broad neural-operator claims.

### 5.9 Boundary of the evidence

The canonical block list is narrowed but still active: the evidence reported
above does not support external-dataset or geometry-independent pass/fail
rates, comparative superiority over baselines, general or real-world
fault-detection rates, validated localization, runtime, reliability, or model
accuracy claims. The executed comparators are scoped diagnostics, the
external-scope audit is secondary provenance, and the same-task
multi-architecture and cross-family executions widen the evidence within their
stated rosters without lifting these boundaries.

## 6. Discussion

### 6.1 Interpretation of the Scoped Evidence

The value of the current study is not that every MR finds a new fault beyond rollout accuracy. Rather, the value is that retained MRs provide relation-level evidence under explicit transformations. When a violation or deferral is observed, the MR card and verdict rule help distinguish model inconsistency, relation-domain boundary, numerical tolerance problem, and inconclusive evidence.

A natural objection is that the predicate merely re-describes the three outcomes it was introduced with and is therefore fitted rather than tested. Three runs answer this out-of-sample. The symmetric-mesh run tests an admitted relation the predicate newly classifies as exact, finding a genuine equivariance violation rather than a pre-arranged result. The rollout-accuracy run shows the mirror-y violation is about 34 times the in-distribution one-step error, so the relation evidence does not merely restate accuracy. The K=6 roster, three held-out trajectories, and the second airfoil task then check that these readings survive larger denominators and a change of physics. None of this removes the bounded-execution limitation, but together they make the scope interpretable.

A second objection reads the deferred absolute-conservation relation as a pipeline gap. The conservation class does produce full executable verdicts wherever its floor is calibratable (FNO periodic conservation fails 24/24; PINN reference-relative conservation passes 30/30), and the gate refuses execution only on the MGN open-boundary variant whose verdict could not be separated from the operator's discretization error, a pipeline that executed it anyway would have produced the false conservation pass below.

The rubric averted two concrete misreadings. Without the numerical-decidability gate, the absolute discrete-divergence relation would have been executed and, because the surrogate's divergence is close to the reference, recorded as a conservation *pass*, a false assurance, since the reference field itself carries non-negligible divergence; the rubric deferred it instead. Without the boundary and bijectivity checks, the asymmetric-mesh mirror-y failure would have read as a model symmetry fault; the rubric downgraded it to OOD-stress and flagged the geometry. Both are overclaims the candidate relation alone would have produced.

### 6.2 Boundary of Claims

The workflow is not claimed to beat rollout accuracy, to have NOETHER certify the physical validity of cylinder-flow MRs, to let LLMs identify valid MRs automatically, or to generalize from the studied MeshGraphNets-family configurations to all SciML surrogates. The supported claim is narrower: a domain-validity-aware workflow makes MR identification and execution more auditable for a concrete class of SciML SUTs.

### 6.3 Implications for SciML Testing

The scoped evidence shows how SciML testing can move from implicit expert checks to explicit MR assets. Such assets can complement residuals, uncertainty estimates, and accuracy metrics by making transformation assumptions and verdict rules inspectable. This is especially important for OOD validation, where the boundary of the relation is often as important as the violation itself.

In that sense the workflow is aimed at producing, over many controlled transformations, a relation-indexed applicability map: a record of where a surrogate stops respecting the relations it should respect, expressed in relation space rather than in residual space. We do not claim a completed applicability map in this paper; the present evidence is one bounded within-SUT point on such a map, and assembling a calibrated map would require the cross-SUT, multi-trajectory, and cross-relation score-calibration work that remains future work.

## 7. Threats to Validity

**Construct validity.** MR validity depends on the rubric, physical assumptions, boundary-condition compatibility, and tolerance rules. Incorrect discrete operators or thresholds may create false violations or false passes.

**Internal validity.** SUT setup, checkpoint differences, random seeds, mesh preprocessing, and runtime nondeterminism may affect verdicts. The experiment ledger must record these details.

**External validity.** The empirical evidence covers two CFD tasks on two official datasets, incompressible DeepMind cylinder flow (across four architectures: the MeshGraphNets K=6 roster, S4/S5 variants, PointMLP, and the PhysicsNeMo production implementation) and compressible DeepMind airfoil flow, plus bounded cross-family PINN and FNO executions over 2D Burgers and heat data. The second-task airfoil result demonstrates that the predicate produces a physically correct, task-specific typed verdict structure rather than a fixed checklist, but it is a primary-scale K=6 roster (official architecture, 240 cells) with moderate surrogate accuracy at the local training budget; the Minimum-MR-SubSet reruns add reproduced held-out cylinder-flow MGN evidence and two trained PINN PDE witnesses as applicability checks, not general cross-SUT pass-rate estimates. Generalization to all neural operators, PINNs, or fluid surrogates without further evidence is not supported.

**Baseline fairness.** Generic MR-generation and LLM baselines may not be designed for SciML. They should be interpreted as scope contrasts and candidate-generation comparators, not as defeated competitors.

**Conclusion validity.** Small sample sizes, multiple MRs, and many transformation bins can produce unstable conclusions. The primary MGN scope upgrade expands the weakest trajectory-dependent denominators to K=6 x 3 trajectories x 10 mirror-y frames and K=6 x 3 trajectories x 9 conservation transitions, plus K=6 x 3 exact-symmetry inputs, removing the single-source-trajectory denominator within the stated scope.

**Reproducibility.** Some SUTs may depend on old runtimes or non-redistributable checkpoints. The paper should disclose such barriers and provide the most complete runnable package possible. By re-run cost: the operator-floor sweep, MR-card validators, and typed-verdict logic replay on CPU in minutes from committed scripts alone; the cylinder-flow MGN pilot, K=6 roster, PointMLP, and FNO/PINN rosters replay on CPU from committed checkpoints and metric ledgers; PhysicsNeMo MGN and airfoil training require a GPU and the public DeepMind TFRecords; and the Minimum-MR-SubSet audit and rerun execute read-only from sibling fixtures at the cited commit.

## 8. Conclusion

This paper presents domain-validity-gated MR identification as an auditable oracle-free testing workflow for SciML surrogates. The evidence supports the scoped pilots of Section 5.3; expands them across K=6 MGN checkpoints and three held-out trajectories with 180 mirror-y, 162 conservation-transition, and 18 exact-symmetry cells; replicates the verdict pattern across same-task architectures, including wider/deeper MGN variants, a non-message-passing PointMLP network, and the NVIDIA PhysicsNeMo production implementation; calibrates the P1 operator floor (slope 0.984, 95% CI [0.975, 0.992]); and adds bounded PINN/FNO cross-family executions plus two primary trained-PINN witness reruns. The central claim remains methodological: physically meaningful SciML MRs require explicit validity conditions, executable assets, raw evidence records, and relation-level verdicts.

## Data Availability

All MR cards, executable assets, run manifests, raw outputs, metric ledgers,
and the claim ledger that backs every empirical statement in this paper are
maintained in a version-controlled replication package. The package, including
the trained checkpoints, the seeded-fault catalogue, and the per-trajectory
ledgers referenced by relative path throughout Section 5, will be archived
with a DOI on Zenodo upon acceptance; until then it is available to reviewers
on request through the editor.

## Appendix A. Full claim-to-evidence ledger

The complete per-claim ledger backing Section 5, including the
architecture-replication, cross-family, baseline, and external-witness rows
summarized compactly in §5.1. Each row gives the committed evidence path; the
authoritative runtime mapping is `claim-ledger.yml`.

| Claim | Current status | Evidence | Boundary |
|---|---|---|---|
| Domain-validity rubric | Supported method claim | `research_assets/rubric/domain_validity_rubric.json` | Establishes an auditable screening rule; physical validity still depends on each relation's stated preconditions. |
| MR-card executable assets | Supported asset/workflow claim | `research_assets/mr_cards/`; validators | Some cards remain protocol assets pending matched SUT evidence. |
| Baseline admissibility contrast | Observed | `expert-mr-baseline/`; `llm-mr-baseline/`; `generic-mr-baseline/`; `claim-ledger.yml` | Expert-LLM, LLM, and generic baselines executed as scoped admissibility-gap comparators without ranking methods as competitors. |
| Minimum-MR-SubSet external-scope audit | Observed secondary audit | `minimum-mr-subset-external-scope-audit/minimum_mr_subset_scope_audit.json` | external witness evidence from 70 real rows and three SciML/PDE true-fault-class PASS_WITNESS rows; does not add new primary SUT executions to this paper. |
| Minimum-MR-SubSet primary rerun | Observed external runtime rerun | `minimum-mr-subset-primary-rerun/cylinder-flow-mgn-runtime/abd_witness_report.json` | `PASS_WITNESS`, kstar = 6, four active true fault classes, max signature rank 2, collapse false; real held-out cylinder-flow MGN runtime, not a second architecture or dataset. |
| Minimum-MR-SubSet PINN primary reruns | Observed second-SUT/PDE reruns | `minimum-mr-subset-primary-rerun/burgers2d-pinn-witness/`; `minimum-mr-subset-primary-rerun/diffusion2d-pinn-witness/` | trained Burgers2D and Diffusion2D PINN witnesses, `PASS_WITNESS`, kstar = 1 each, five active true fault classes each; one-seed witnesses, no cross-SUT rate. |
| Primary empirical scope upgrade | Observed | `primary-scope-upgrade/primary_scope_report.json`; per-trajectory/checkpoint manifests | K=6 x 3 trajectories x 10 mirror-y OOD-stress grid fails 180/180; K=6 x 3 trajectories x 9 conservation-transition grid passes 162/162 as reference-relative diagnostic; K=6 x 3 exact-symmetric-mesh input grid fails 18/18; trajectory-dependent cells are clustered by checkpoint, held-out test trajectory, and frame; not a single-source-trajectory estimate, not a cross-SUT rate. |
| LLM role boundary | Supported process boundary | Method and ethics sections | LLMs organize candidates; the rubric decides validity. |
| Multicheckpoint replication | Observed | `multicheckpoint/e1_aggregate.json`; per-SUT manifests under `multicheckpoint/S0..S5/` | K=6 checkpoints of one MeshGraphNets architecture family on one dataset; within-family replication. |
| Fault-detection robustness | Observed | `fault-robustness-e3/fault_robustness_report.json`; `phase3-unified-fault-catalog/phase3_unified_fault_catalog.json` | 30-trial Wilson CIs per MGN mutant plus the Phase-3 60-entry unified fault catalogue (composition in §5.6), with by-detector precision/recall (Wilson CIs) and Wilcoxon/Cliff effect sizes. |
| S4/S5 variant primary workflow | Observed | `same-domain-variant-primary-workflow/same_domain_variant_primary_workflow_report.json`; raw ledgers | Same-domain wider/deeper MGN variants: 2/2 node-permutation passes, 60/60 mirror OOD failures, 54/54 conservation-diagnostic passes, 6/6 exact-symmetric failures; not PhysicsNeMo/EchoWave or cross-dataset reliability evidence. |
| PointMLP cylinder primary workflow | Observed | `pointmlp-cylinder-primary-workflow/pointmlp_cylinder_primary_workflow_report.json`; checkpoint and raw ledgers | Newly trained non-MGN row-wise coordinate network on cylinder-flow source cases: 9/9 node-permutation passes, 10/10 mirror OOD failures, 9/9 conservation-diagnostic passes, 3/3 exact-symmetric failures, median rollout rel L2 0.0298; not PhysicsNeMo/EchoWave or production CFD evidence. |
| PhysicsNeMo MGN scaled workflow | Observed multi-trajectory production-framework execution | `production-grade-sut-extension/physicsnemo-mgn-vortex-shedding-scaled/physicsnemo_mgn_scaled_workflow_report.json`; newly trained checkpoint, per-trajectory ledgers, raw outputs | NVIDIA PhysicsNeMo `MeshGraphNet` in its official architecture (2.33M params) trained on 25 and evaluated on 40 official DeepMind `cylinder_flow` trajectories: node permutation exact on 40/40 (relative L2 0.0), mirror-y fails as OOD stress on 40/40 (median 0.31), conservation reference-relative diagnostic only; CPU-scale, not the official 10M-step schedule, NVIDIA checkpoint, or production benchmark, and not AeroGraphNet/DoMINO evidence. |
| FNO primary workflow upgrade | Observed | `fno-primary-workflow/fno_primary_workflow_report.json`; per-SUT ledgers and raw `.npz` source/follow-up outputs | Six trained FNO-2D checkpoints over Burgers/heat: 24/24 translation passes, 24/24 conservation failures under a periodic discrete-conservation MR, and 6/6 Dirichlet-boundary translation rejections; full rubric-to-verdict evidence, outside cylinder-flow and broad neural-operator claims. |

## References

Submission citation status is tracked in `paper/citation_audit.md` and the IST
package bibliography at `paper/ist-submission/references.bib`. The current
submission draft cites only keys that are backed by BibTeX entries and an audit
row. The unverified `qi2025physicalfield` lead is excluded from the submission
bibliography; the partially verified fluid-velocity lead is retained only in the
non-submission reference ledger as a guardrail against first-or-only novelty
claims.

Core cited groups:

- Mesh-based neural simulation: `pfaff2021meshgraphnets`.
- Oracle problem and metamorphic testing: `barr2015oracle`,
  `chen1998metamorphic`, `segura2016survey`, `chen2011ml`.
- Scientific and simulation-software MT: `kanewala2019scientific`,
  `lin2020exploratory`, `olsen2019simulation`, `raunak2021continuum`,
  `hiremath2021ocean`, `mandrioli2025cps`.
- SciML V&V and learned PDE surrogates: `raissi2019pinn`,
  `karniadakis2021piml`, `li2021fno`, `krishnapriyan2021failure`,
  `gopakumar2025calibrated`.
- Hybrid ML-solver trust-region context: `baral2025xrepit`,
  `wang2025deeponetfe`.
- MR organization and pattern context: `yang2020hierarchical`,
  `zhao2026noether`.
