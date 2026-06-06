# Domain-Validity-Gated Metamorphic Relation Identification and Executable Test Assets for Scientific Machine Learning

> Manuscript draft for IST regular track.  
> Draft status: v0.4 PR4 evidence-gated results revision, 2026-06-05.  
> Full cross-SUT results remain blocked; only strictly scoped within-SUT pilot evidence on one MeshGraphNets checkpoint is reported (Section 5.1).

## Target and Scope

- Primary target: *Information and Software Technology* regular research-paper track.
- Paper type: empirical software engineering / software testing and V&V method paper.
- Review framing: software testing contribution first; SciML and cylinder flow are the application context.
- Word limit target: keep the submitted paper below 15,000 words.
- Current draft policy: empirical findings may be written only when traceable to merged artifacts, run manifests, raw outputs, metric ledgers, and claim-ledger boundaries.

## Structured Abstract

### Context

Scientific machine-learning (SciML) surrogates are increasingly used to approximate expensive physical simulations. Mesh-based neural simulators are attractive for fluid-flow problems because they operate on irregular meshes and predict spatiotemporal physical fields. Testing such systems is difficult because exact expected outputs are often unavailable for arbitrary inputs without running a trusted high-fidelity solver. Rollout accuracy and physics residuals provide useful evidence, but they do not by themselves specify which physical relations should hold under controlled transformations of inputs, meshes, boundary conditions, or parameters.

### Objective

This paper investigates how physically meaningful metamorphic relations (MRs) can be screened and operationalized as executable oracle-free test assets for scientific machine-learning systems. The goal is not to improve a predictive model, but to make the step from candidate relation to executable test asset more systematic, auditable, and explicit about the physical, numerical, and software conditions under which each relation is expected to hold. MeshGraphNets-family cylinder-flow surrogates are used as the concrete case study.

### Method

We propose a domain-validity rubric for screening candidate MRs, an MR-card and executable-asset format that records source cases, follow-up transformations, output mappings, metrics, tolerances, exclusion rules, and relation-level verdicts, and a case-study protocol for applying these assets to mesh-based neural cylinder-flow surrogates. Candidate sources may include physical equations, boundary conditions, representation contracts, expert reasoning, LLM-assisted candidate lists, and NOETHER-style pattern organization, but validity is decided by the rubric and evidence records rather than by candidate generation alone.

### Results

Full cross-SUT results remain blocked pending cross-SUT artifacts. Only strictly scoped, within-SUT pilot evidence on a single MeshGraphNets checkpoint is reported (Section 5.1): node-permutation equivariance holds to machine precision; an approximate mirror-y OOD-stress probe — the exact relation being out-of-relation-domain for this asymmetric mesh — failed on 10 of 10 recorded eval frames (median relative L2 0.737, median V/floor 3.96); and an absolute mass-conservation relation stays deferred while a reference-relative divergence diagnostic passes. Two further within-SUT runs sharpen the interpretation: a same-trajectory one-step rollout-accuracy diagnostic gives median relative L2 0.0216, so the mirror-y violation is about 34 times the surrogate's in-distribution accuracy; and on a synthetic mesh that is provably symmetric about the centerline — where the rubric admits the exact mirror-y relation rather than downgrading it — the surrogate still violates exact mirror-y equivariance (relative L2 1.10), which removes the out-of-relation-domain objection to the mirror-y finding. Used as detectors against a 10-mutant injected-fault catalogue, the MRs catch 5 of 10 faults and, in a suggestive, single-SUT test, localize them by MR class (continuity to boundary/scale faults, symmetry to physical-channel/adjacency faults). This draft makes no claims about cross-SUT pass rates, general or real-world fault-detection rates, comparative baseline superiority, validated localization accuracy, model accuracy, or SUT reliability.

### Conclusion

The evidence supports a validity-aware bridge from candidate MR ideas to auditable SciML test assets. The main empirical lesson is not that every physical intuition becomes a clean MR, or that every MR exposes a general fault. Rather, the scoped pilots show that a rubric-gated workflow can produce relation-level outcomes while preserving the evidence boundary for each claim. We frame this as a domain-admissibility-gated, relation-indexed approach to SciML OOD validation: a relation is admitted only when its tolerance dominates the relevant numerical error floor, and its verdict is read in a space that separates a model-level violation from an out-of-domain application.

## Keywords

Metamorphic testing; metamorphic relation identification; oracle problem; scientific machine learning; MeshGraphNets; cylinder flow; software verification and validation.

## 1. Introduction

Scientific computing increasingly uses learned surrogates to reduce the cost of repeated numerical simulation. In fluid dynamics, mesh-based neural simulators such as MeshGraphNets learn to predict physical fields on irregular meshes and can provide fast rollout predictions for benchmark problems such as flow around a cylinder. These models are useful because they can approximate high-cost solvers, but they also create a familiar software testing problem in a new setting: for many candidate inputs, there is no cheap and exact expected output against which the program can be checked.

The common response is to evaluate a surrogate on held-out trajectories and report rollout error. This is necessary, but it is not the whole validation problem. A model may have acceptable average error on a finite test set while still failing to preserve relations that should hold under a physically meaningful transformation. Conversely, a high error value does not always explain which physical, numerical, or representational condition has been violated. For a user who wants to deploy a SciML surrogate outside a narrow validation set, the practical question is not only "How accurate is the model on these samples?" but also "Under which transformations or regimes does this system stop respecting the relations it should respect?"

Metamorphic testing (MT) addresses the test-oracle problem by checking relations among multiple executions instead of requiring an exact output for each individual test case. A metamorphic relation states that if a source input is transformed in a specified way, the corresponding outputs should satisfy a necessary relation. This is a natural idea for scientific computing: conservation laws, symmetry relations, nondimensional similarity, boundary constraints, continuity conditions, and numerical stability expectations all suggest possible relations among executions.

The difficult part is deciding which candidate relations are valid and executable for a particular SciML program. A transformation that looks plausible at a high level may violate the governing assumptions, boundary conditions, discretization choices, or measurement tolerance of the actual system under test (SUT). For cylinder flow, mirror symmetry depends on geometry and boundary labels; translation invariance depends on how coordinates and domain boundaries are represented; Reynolds-Strouhal similarity depends on nondimensionalization and flow regime; a divergence check depends on a discrete divergence operator, mesh weights, and boundary treatment. Treating such transformations as automatically valid MRs would make the test suite look rigorous while hiding the very assumptions that determine whether a violation is meaningful.

Prior studies show that relation-based and residual-based evidence is useful when direct oracles are limited in scientific software, simulation testing, design-assumption MRs, and SciML reliability. Recent candidate leads also suggest that physics-based MRs are being explored for learned physical-field or fluid-velocity predictors, but the currently verified record is not strong enough to support a first-or-only novelty claim. The remaining problem addressed here is therefore narrower: how candidate MRs are screened for domain validity, turned into executable test assets, and reported through relation-level verdicts that distinguish SUT inconsistency from out-of-relation-domain cases and numerical tolerance effects.

This paper treats MR identification for SciML as a validity-gated testing problem. Physical knowledge, expert reasoning, LLM-assisted candidate lists, and NOETHER-style pattern organization can all suggest candidate relations, but a candidate relation is not yet an executable MR. It must first state the physical or software basis of the relation, the transformation preconditions, boundary-condition compatibility, output mapping, metric, tolerance rationale, exclusion rule, and verdict interpretation. Only retained relations are converted into executable MR assets.

Two ideas organize this treatment. First, a candidate relation is *admissible* only when, in addition to a physical or software basis and satisfied transformation preconditions, it is numerically decidable: its verdict tolerance must dominate the intrinsic error floor of the operator that measures it — machine precision for an exact representation relation, the interpolation or mapping floor for an approximate geometric relation, or the discretization floor of a discrete operator for a continuity relation. Second, a relation-level verdict is read in two dimensions — how far the measured quantity violates the relation, and how far the transformed case lies outside the relation's validity domain — so that a model-level inconsistency is not confused with a relation applied outside its domain. We refer to this as a domain-admissibility-gated, relation-indexed approach to SciML OOD validation. It is an organizing framework, not a new model and not a claim of superiority over uncertainty quantification.

The case study is scoped to MeshGraphNets-family cylinder-flow surrogates. This is an intentionally narrow empirical setting rather than the paper's main conceptual contribution. It allows us to examine transformations over meshes, geometry, velocity fields, nondimensional quantities, and rollout behavior while keeping the SUT family concrete enough for reproducible testing. Full cross-SUT evaluation remains blocked. The current case study reports only one trained SUT and checkpoint, so we do not claim external validity across all neural fluid surrogates.

### 1.1 Research Questions

The main research question is:

**RQ0. How can candidate metamorphic relations for scientific machine-learning systems be screened for domain validity and converted into executable oracle-free test assets without relying on exact per-sample expected outputs?**

We decompose this into four questions.

**RQ1 - Validity.** How can a domain-validity rubric distinguish physically meaningful candidate MRs from transformations that are executable but invalid, underspecified, or outside the relation's domain?

**RQ2 - Operationalization.** How can retained candidates be represented as MR cards and executable assets with source cases, follow-up transformations, metrics, thresholds, exclusions, and verdict rules?

**RQ3 - Verdict and interpretation.** How can relation-level verdicts distinguish pass, fail, skip, out-of-relation-domain, numerical tolerance issue, and inconclusive outcomes?

**RQ4 - Case-study evidence.** In a MeshGraphNets-family cylinder-flow case study, what evidence does the rubric-gated asset workflow add relative to expert MR design, LLM-assisted candidate generation, generic MR-generation scope contrasts, and rollout-accuracy diagnostics? In the current evidence only the rollout-accuracy comparator is answered; the expert-MR, LLM-candidate, and generic-MR comparators remain planned and are blocked pending their artifacts.

### 1.2 Contributions

This paper makes five scoped contributions, each repositioned narrowly with respect to the closest prior we identify in Section 2.

First, we propose a domain-validity rubric for screening candidate MRs in SciML testing. The rubric checks physical basis, transformation preconditions, boundary-condition compatibility, output mapping, metric and tolerance, and failure diagnosability. As a SciML-specific instantiation of the calibrated-tolerance principle introduced by Eniser et al. [eniser2022relaxations] as *relaxations* for stochastic RL policy testing, we ground the tolerance floor in the *intrinsic error floor of the discrete measurement operator*, whose truncation order is theoretically characterizable (for a P1 discrete-divergence operator on a triangular mesh, $O(h)$ in the mesh spacing); in this study the floor magnitude is estimated from the reference field on the deployed mesh rather than computed from a closed-form bound, which we leave to future work. To our knowledge, grounding an MR tolerance in the measurement operator's own error floor in this way is new in the SciML setting.

Second, we define an MR-card and executable-asset workflow that converts retained candidates into auditable test assets. NOETHER-style pattern organization may be used as one candidate source, but it is not the contribution being evaluated here and it does not decide MR validity.

Third, we define a relation-level verdict and ledger scheme that reads verdicts in two dimensions (relation-violation against domain-violation magnitude). This instantiates, for physics-governed SciML, the constraint-architecture pattern introduced by Duque-Torres et al. [duqueTorres2023bugornot], formalised by *Towards a Complete Metamorphic Testing Pipeline* [duqueTorres2023completePipeline], and automated data-drivenly by MetaTrimmer [duqueTorres2023metaTrimmer]; what is new here is a *typed classification* of domain-inadmissibility sub-dimensions drawn from PDE-domain preconditions, geometry, boundary conditions, and operator admissibility. The relation-violation axis is quantified; the domain-violation axis is at present only qualitatively operationalized, and a calibrated continuous score is left to future work.

Fourth, we provide a MeshGraphNets-family cylinder-flow case study on one trained SUT and checkpoint, extending the active-transformation testing direction of Reichert et al. [reichert2024hess] — who applied physics-derived MRs to a trained LSTM hydrologic surrogate and produced a basin-stratified applicability map — from hydrology to mesh-based neural fluid surrogates. The current evidence contains three scoped pilots, a same-SUT rollout-accuracy comparator, and an exact mirror-y test on a provably symmetric admissible synthetic mesh. Expert MR design, generic MR-generation scope contrasts, LLM-assisted candidate generation, and cross-SUT comparisons remain protocol commitments until matched artifacts exist.

Fifth, as an element that none of the closest prior works addresses, we use the paper's own MRs as fault detectors against an independently re-implemented 10-mutant seeded-fault catalogue, and report a by-class localization: the continuity MR localizes to boundary-condition and gross normalization-scale faults; the symmetry MR localizes to physical-channel and mesh-adjacency faults; node-permutation equivariance, by-design exact under these faults, localizes to none. This is suggestive evidence for a typed mapping from MR class to fault class, not a validated localization model.

## 2. Background and Related Work

### 2.1 Mesh-Based Neural Simulation

Mesh-based neural simulators learn dynamics on graph or mesh representations of physical systems. For fluid-flow problems, a mesh representation is attractive because the geometry, boundary regions, and local connectivity can be represented without forcing the state onto a regular grid. MeshGraphNets is a representative architecture family in this area: it encodes mesh nodes and edges, propagates information by message passing, and predicts future physical fields through autoregressive rollout.

The cylinder-flow benchmark is useful for testing because it combines several features that matter for SciML validation. It involves geometry, boundary conditions, velocity fields, pressure-like quantities or derived quantities, temporal rollout, and flow-regime assumptions. It also exposes the distinction between data-driven accuracy and physical relation preservation. A model may fit a trajectory distribution while failing under a controlled transformation of geometry, mesh representation, or flow parameters.

In this paper, MeshGraphNets-family systems are treated as software systems under test. We do not evaluate them as new modeling contributions. Instead, we ask how their outputs behave under controlled input transformations and whether necessary relations remain within explicit tolerances.

### 2.2 Metamorphic Testing and the Oracle Problem

Metamorphic testing was developed to address programs for which it is difficult or impossible to know the correct output for a single test input. Instead of checking one output against one expected value, MT checks a relation among the outputs of a source input and one or more follow-up inputs. This framing has been applied to scientific software, simulation models, and machine-learning systems, all of which can suffer from oracle problems.

For SciML surrogates, the oracle problem is especially visible in out-of-distribution (OOD) settings. A trusted solver may be too expensive to run for every transformed case, and even when a reference output is available, a single pointwise error does not necessarily indicate whether a physical relation has been preserved. MR-based testing offers a complementary perspective: it asks whether the SUT maintains a necessary relation under a controlled transformation.

However, SciML MRs cannot be treated as generic input perturbations. In image-based ML testing, transformations such as lighting or weather changes may preserve the semantic label. In scientific computing, the transformation must respect governing equations, physical regimes, boundary conditions, mesh representation, and numerical tolerance. The correctness of the MR itself becomes a central validity question.

### 2.3 MR Identification for Scientific and Simulation Software

Prior work on scientific software testing has shown that MRs can be elicited from monotonicity, conservation-like behavior, scaling relations, simulation assumptions, and domain-specific expectations. Work on simulation validation similarly treats multi-run relations as pseudo-oracles when direct validation data are limited or unavailable. These studies establish that MR thinking is practical for scientific and simulation software, not merely for toy functions.

Other work has explored automated or semi-automated MR identification. For example, research on ocean system models shows that data-driven search can discover candidate transformations in complex physical software. CPS testing work shows that design assumptions can be encoded as MRs and then used to generate new test traces. These ideas are important for the present paper because they show that MR sources can include system assumptions, model structure, and physical design knowledge.

The gap is that candidate identification is not enough for SciML. A candidate relation must also state when it is supposed to hold. Without a domain-of-validity record, a failed test may mean several different things: the relation was invalid under the chosen boundary conditions, the transformation left the physical regime, the tolerance was not numerically justified, or the SUT violated a relation it should have preserved. This paper makes that distinction explicit.

### 2.4 Physics-Based MT for Learned Scientific Simulators

Three contemporary works are the closest prior to ours and frame what is and is not new here. We engage each one explicitly.

**Reichert et al. (2024)** [reichert2024hess] applied physics-derived metamorphic relations to a trained LSTM hydrologic surrogate. They perturbed climate-forcing inputs (temperature, precipitation) in directions where the qualitative physical response is known a priori, stratified pass/fail outcomes by basin elevation to produce an implicit applicability map, and excluded basins where forcing uncertainty dominated the response signal — an informal admissibility filter. The present work formalises these practices as an explicit admissibility predicate, a two-dimensional verdict type, and a relation-indexed applicability map, and extends them from hydrology to mesh-based neural fluid surrogates whose outputs live on irregular meshes and whose MR validity depends on geometry and discrete operators rather than basin physiography. We do not claim to be the first to use physics-derived MRs on a trained neural surrogate.

**Eniser et al. (2022)** [eniser2022relaxations] introduced *relaxations* — numerical tolerances embedded inside MR oracles — for action-policy testing of stochastic reinforcement-learning systems, deriving them empirically from policy rollouts on Highway, LunarLander and BipedalWalker. We extend this calibrated-tolerance principle to deterministic numerical surrogates by grounding the tolerance floor in the intrinsic error floor of the discrete measurement operator, whose truncation order is theoretically characterizable (for a P1 discrete-divergence operator on a triangular mesh, $O(h)$ in the mesh spacing). The distinction from rollout-derived relaxations is that the floor is a property of the measurement operator rather than of model stochasticity; in the present study we estimate its magnitude empirically from the reference field on the deployed mesh, and a closed-form a-priori bound is left to future work. We do not claim that calibrated MR tolerance is itself new.

**The 2023 violation-attribution cluster** — Duque-Torres et al. (SANER 2023) [duqueTorres2023bugornot], *Towards a Complete Metamorphic Testing Pipeline* [duqueTorres2023completePipeline] and MetaTrimmer [duqueTorres2023metaTrimmer] — identified the bug-vs-MR-inapplicability separation as a research problem and addressed it architecturally with explicit MR constraints used as a pipeline pre-filter, with MetaTrimmer automating the constraint derivation from random-input violation logs. Our two-dimensional verdict instantiates this architectural pattern for physics-governed SciML; what is new is a *typed classification of domain-inadmissibility sub-dimensions* drawn from PDE-domain preconditions, geometry compatibility, boundary-condition compatibility, and operator admissibility, rather than a binary skip/proceed gate or a data-derived constraint set. We do not claim that the bug-vs-inapplicability separation is itself new.

Across all three closest works, the element our debates could not pre-empt is the seeded-fault MR-as-detector with by-class fault localization reported in Section 5.3. None of Reichert, Eniser, or the 2023 cluster attempts to map MR failures back to identifiable fault classes within the system under test.

### 2.5 SciML V&V, Residuals, UQ, and Failure Modes

SciML reliability research has developed several important tools: physics residuals, uncertainty quantification, conformal prediction, certified error bounds, stress testing, equivariance error, and failure-mode analysis. These tools address real weaknesses of learned PDE solvers and neural surrogates. For example, calibrated physics-informed uncertainty quantification uses PDE residuals as nonconformity scores and provides statistical coverage guarantees. Work on PINN failure modes shows that physical constraints in a training loss do not guarantee reliable behavior in more difficult regimes.

These methods are complementary to MT. A residual, conservation error, or equivariance error can be a useful diagnostic, but it is not automatically an MR. It becomes part of an executable relation only when there is a source case, a follow-up transformation, an expected output relation, a tolerance rule, and a verdict interpretation. This distinction is central to our paper. We use SciML diagnostics as possible relation measurements, while MT supplies the multi-execution oracle-free structure.

### 2.6 Hybrid ML-Solver Trust Regions

Hybrid ML-solver frameworks provide another relevant line of work. Some systems use residual thresholds or error estimates to decide when a learned component should be trusted and when a numerical solver should take over. Such systems operationalize a form of trust region, although often at runtime and through residual-based switching rather than offline relation-based testing.

Our study pursues a complementary direction. Before deployment, physically derived transformations are used to estimate where relation violations occur and what regimes, boundary conditions, or numerical assumptions are associated with them. The result is not a runtime switching policy by itself, but an evidence structure that can support later decisions about when a learned surrogate should be trusted.

The distinction from residual- and uncertainty-based trust estimation is deliberate. Uncertainty quantification, conformal prediction, and residual-threshold trust regions locate unreliable behavior in feature, residual, or error-estimate space, and they do so passively from observed inputs. The present method instead acts in relation space: it applies a physically derived, controlled transformation and reports which necessary relation breaks under it, indexed by that transformation. The intended product is therefore the evidence structure needed for a relation-indexed applicability map — a statement of the form "under this controlled transformation, this relation no longer holds" — rather than a scalar field of high residual, and the two-dimensional verdict separates a model-level violation from an out-of-domain application, a separation that, as the present case illustrates, a scalar accuracy or residual magnitude does not by itself provide. Section 5.3 gives that concrete within-SUT instance: a surrogate that is accurate in-distribution (median one-step relative L2 0.0216) still violates mirror-y equivariance by roughly an order of magnitude more, so the accuracy number does not bound the relation violation. We do not claim a completed applicability map in this paper; the mirror-y result reported below is one bounded within-SUT example of the evidence such a map would aggregate.

### 2.7 What Is New and What Is Not New

The paper does not claim that metamorphic testing, MR identification, scientific-software MT, residual diagnostics, uncertainty quantification, LLM candidate generation, or NOETHER-style candidate organization is new. These are established or emerging sources of testing ideas. The paper's narrower claim is that SciML MR identification should be treated as a domain-validity problem: a candidate relation becomes useful only after its physical basis, transformation preconditions, output mapping, tolerance, exclusion rule, executable artifact, and relation-level verdict are recorded.

What is new here is the evidence-gated conversion from candidate relation to executable SciML MR asset. The contribution is not a stronger neural simulator and not an automatic MR generator. It is a workflow that makes the validity boundary inspectable, so that a candidate can be retained, rejected, downgraded to OOD-stress, or deferred instead of being silently treated as a valid oracle. Structurally, the novelty is two organizing devices rather than a checklist of MR fields: an admissibility gate that ties a relation's tolerance to the numerical error floor of its own measurement, and a two-dimensional relation-level verdict that separates a model violation from an out-of-domain application. The admissibility gate is fully operational (it decides retain, downgrade, or defer on stated grounds in the case study); the verdict's domain-violation axis is, so far, only qualitatively operationalized, so the two-dimensional verdict is at this stage an interpretive structure pending a calibrated domain-violation score rather than a fully measured device. Both are means to make the validity boundary inspectable, not claims of empirical superiority over existing diagnostics. A third, empirically distinct element, examined in Section 5.3, is the seeded-fault by-class localization: used as detectors against an independently re-implemented injected-fault catalogue, the MRs map by class to fault class (continuity to boundary/scale faults, symmetry to physical-channel/adjacency faults), an element none of the three closest prior works addresses.

## 3. Method

### 3.1 Overview

The proposed method is a five-stage workflow:

1. identify candidate relation sources;
2. organize candidate relations using declared candidate-source categories;
3. screen candidates with a domain-validity rubric;
4. convert retained relations into executable MR assets;
5. execute the assets and record relation-level verdicts.

The method deliberately separates candidate generation from validity judgment. NOETHER-style patterns may help organize or generate candidate relation structures, but they do not certify that a relation is physically valid for a particular SUT, dataset, mesh, boundary condition, or numerical tolerance. Validity is determined by the rubric and by executable evidence.

### 3.2 Candidate Relation Sources

For cylinder-flow surrogates, candidate MRs may come from six sources.

**Physical equations and constraints.** Incompressible continuity, boundary behavior, and conservation-like expectations can suggest relation measurements such as discrete divergence or boundary-condition consistency.

**Geometric and symmetry assumptions.** Mirroring, rigid transformations, and coordinate-frame changes may suggest equivariance or invariance checks, but only under compatible geometry and boundary labels.

**Nondimensional similarity.** Reynolds-number and Strouhal-number relations may suggest follow-up transformations over flow parameters or extracted wake behavior, but only within regimes where the empirical or theoretical relation is meaningful.

**Mesh and graph representation.** Node permutations, face ordering, edge encoding, and mesh refinement may suggest representation-level MRs.

**Temporal rollout behavior.** Autoregressive rollouts may suggest determinism, prefix consistency, or semigroup-like sanity checks. These are useful implementation or numerical-consistency checks, but should not be overstated as physical laws.

**Cross-implementation comparison.** Outputs from different implementations may support method-comparison checks only if units, state variables, meshes, rollout horizons, boundary conditions, and checkpoints are comparable. Otherwise they are triangulation evidence rather than retained MRs.

### 3.3 Domain-Validity Rubric

We treat screening as deciding a single admissibility predicate. A candidate relation is an *admissible MR* when four conditions hold together: (i) it has a physical or software basis; (ii) its transformation preconditions are satisfied; (iii) its boundary conditions and output mapping remain compatible after the transformation; and (iv) it is numerically decidable, meaning the verdict tolerance dominates the intrinsic error floor of the operator that measures the relation. Conditions (i)-(iii) establish that the relation is meaningful for the transformed case; condition (iv) establishes that a violation can be told apart from numerical noise. None of the four is optional and none is merely documentary: each is a gate that can reject or defer a candidate, and provenance recording is the mechanism that makes each gate auditable, not a substitute for it. The six rubric criteria below are the recorded, auditable form of these four conditions.

Each candidate MR is screened using a rubric with six criteria.

**Physical basis.** The relation must cite its source: governing equation, boundary condition, nondimensional law, representation property, numerical assumption, or implementation contract.

**Transformation preconditions.** The source-to-follow-up transformation must state what is changed and what is preserved. For example, a mirror relation must specify how coordinates, vector components, node types, and boundary labels transform.

**Boundary-condition compatibility.** The relation must hold under the boundary conditions of the transformed case. If the transformation changes the physical meaning of a boundary, the candidate is rejected or marked as an OOD stress test rather than a physics-preserving MR.

**Output mapping.** The expected relation among outputs must be measurable. A relation that cannot be mapped to available output fields is not executable.

**Metric and tolerance.** The verdict rule must define a metric and a tolerance. The tolerance may come from numerical precision, solver reference behavior, calibration data, repeated-run variability, or expert thresholding, but the source must be recorded. This criterion carries condition (iv): the tolerance must be shown to dominate the intrinsic error floor of the measuring operator. When that floor is itself uncalibratable — as for an absolute discrete-divergence relation whose reference field already carries non-negligible divergence — the relation is deferred rather than executed, because a violation could not be separated from the operator's own discretization error.

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

It is useful to read these verdicts as regions of a two-dimensional space rather than as a flat list. One axis is the relation-violation magnitude — how far the measured quantity exceeds the tolerance, for example the violation-to-tolerance ratio or the violation-to-floor ratio V/floor. The other axis is the domain-violation magnitude — how far the transformed case lies outside the relation's validity domain, signalled by precondition violation, geometry mismatch, boundary-condition mismatch, or operator inadmissibility. Low domain-violation with low relation-violation is pass; low domain-violation with high relation-violation is the only region that may be read as SUT inconsistency; high domain-violation is out-of-relation-domain or, near the boundary, OOD-stress; a relation-violation that sits within the error floor is a numerical-tolerance issue. This decomposition is what keeps a model-level violation from being confused with a relation applied outside its domain, and it makes condition (iv) of the admissibility predicate explicit at verdict time.

In the present study the relation-violation axis is quantitative — mirror-y reports V/floor — but the domain-violation axis is so far only partially operationalized. The mirror-y case is placed near the validity boundary *qualitatively*: the reflection is non-bijective and the worst reflected-node mismatch is about one mesh edge length, so the exact relation is out-of-relation-domain and is downgraded to an approximate OOD-stress probe. We do not claim a fully calibrated, continuous domain-violation score; defining such a score across MR classes is left to future work. The two-dimensional reading is used here as an interpretive structure, not as a calibrated boundary measurement.

### 3.6 Hierarchical Interpretation Protocol

We organize retained MRs into a three-level hierarchy inspired by MR classification for scientific computing: physical-model relations, computational-model relations, and code-model relations. For learned mesh surrogates, the computational-model level includes graph representation and message-passing discretization assumptions.

We use this hierarchy as a predeclared interpretation protocol that maps representation-level MRs to possible graph encoding or adapter problems, physical-model MRs to possible continuity, symmetry, or similarity violations, and code-model MRs to possible determinism, rollout, or implementation issues. At this stage, this is a localization protocol, not a validated localization model. It becomes validated only if seeded faults or mutants with known layers are used to evaluate the inference rule. Section 5.3 reports a first bounded test of this protocol: against an injected-fault catalogue the continuity MR localized to boundary and normalization-scale faults while the symmetry MR localized to physical-channel and mesh-adjacency faults, which is suggestive evidence for the protocol's direction but not, on one SUT and one catalogue, a validated localization model.

## 4. Empirical Design

### 4.1 Subject Systems

The current evidence uses one trained MeshGraphNets-family implementation and
checkpoint. The broader protocol names three intended implementation families,
but they remain blocked until matched artifacts exist:

1. an echowve MeshGraphNets PyTorch/PyG implementation;
2. NVIDIA PhysicsNeMo `vortex_shedding_mgn`;
3. DeepMind TF1 MeshGraphNets, or a third same-family configuration if runtime feasibility requires substitution.

For any future SUT admitted into the study, the experiment ledger must record
repository URL, commit, checkpoint, dataset, mesh format, input fields, output
fields, rollout horizon, random seeds, environment, and known runtime
limitations before the manuscript can use it as evidence. Because these SUTs
share a task and architecture family, even a completed cross-SUT package would
be framed as a same-family stress test, not as evidence for all neural fluid
surrogates.

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

The study uses four comparator families.

**Expert MR design.** Domain experts manually propose MRs. This baseline estimates what the proposed rubric adds beyond conventional expert elicitation.

**Generic MR-generation scope contrast.** Generic MR identification or generation methods are applied as far as their assumptions allow. This comparator is not used to claim that generic methods are weak; it is used to show where domain-validity information is needed for SciML.

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

### 4.5 Statistical Plan

The current paper reports only one bounded within-SUT frame-level OOD-stress
rate for mirror-y. Broader violation-rate estimates, confidence intervals, and
paired comparisons remain blocked until the same source cases and
transformations are run across eligible SUTs or baselines. If those artifacts are
later produced, binary verdict comparisons should use McNemar or Fisher-style
tests only when assumptions are appropriate, and continuous violation magnitudes
should use paired bootstrap intervals. When many MRs or transformation bins are
compared, multiple-comparison correction or false-discovery-rate control must be
reported.

If the number of executable cases remains small, the study must emphasize effect
sizes, confidence intervals, and qualitative failure interpretation rather than
strong significance claims.

### 4.6 Ethics, Integrity, and Reproducibility

The current study does not involve human subjects, personal data, or private sensitive information. The main ethical and integrity issues are research transparency, AI use, and reproducibility.

All SUT versions, datasets, checkpoints, scripts, and run logs should be recorded when licensing permits. Failed, skipped, and inconclusive cases must remain in the experiment ledger. LLM use is restricted to candidate generation and evidence organization; it is not used as a final judge of MR validity. No candidate MR should be described as valid unless it passes the rubric and has a corresponding MR card. No OOD violation should be described as a program fault without the verdict evidence needed to support that interpretation.

Third-party code, datasets, and model checkpoints will be used according to their licenses. If any artifact cannot be redistributed, the paper will provide access instructions and record the limitation.

## 5. Results

Full cross-SUT, comparative, and fault-detection results remain **blocked** (see
5.4). This section reports only strictly scoped, within-SUT pilot evidence whose
artifacts are committed and validated.

### 5.1 Claim-to-Evidence Map

| Claim | Current status | Evidence | Boundary |
|---|---|---|---|
| PC1-domain-validity-rubric | Supported method claim | `research_assets/rubric/domain_validity_rubric.json` | Does not prove physical validity by itself. |
| PC2-mr-card-executable-assets | Supported asset/workflow claim | `research_assets/mr_cards/`; validators | Not every card has cross-SUT evidence. |
| PC3-baseline-comparison-blocked | Blocked | `claim-ledger.yml`; `experiment-ledger.yml` | No baseline superiority, seeded-fault, localization, or runtime claim. |
| PC4-node-permutation-sanity | Observed pilot | `real-sut-node-permutation-pilot/raw/metric_ledger.json` | One SUT and one pilot case only. |
| PC5-conservation-diagnostic-deferred | Observed diagnostic; absolute claim deferred | `conservation-diagnostic-pilot/raw/metric_ledger.json`; `conservation_report.json` | absolute conservation remains deferred. |
| PC6-mirror-y-ood-stress | Observed bounded pilot | `mirror-y-rate-upgrade/raw/metric_ledger.json`; `claim-ledger.yml` | failed on 10 of 10 recorded eval frames; not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim. |
| PC7-llm-candidate-support-only | Supported process boundary | Method and ethics sections | LLMs organize candidates; they do not judge MR validity. |
| PC8-rollout-accuracy-diagnostic | Observed | `rollout-accuracy-baseline/raw/metric_ledger.json` | Same-SUT one-step accuracy (median rel L2 0.0216); mirror-y is ~34x larger; not a baseline-superiority or multi-trajectory claim. |
| PC9-exact-mirror-y-symmetric-mesh | Observed | `mirror-y-symmetric-mesh/raw/metric_ledger.json` | Exact relation admissible and fails (rel L2 1.10) on a synthetic OOD symmetric mesh; not an accuracy, reliability, or cross-SUT claim. |
| PC10-seeded-fault-detection | Observed | `seeded-fault-detection/raw/metric_ledger.json` | MRs as detectors catch 5/10 injected mutants, localizing by MR class; not a general or real-world fault-detection rate. |

The PC# identifiers above are paper-level claims. The single source of truth for runtime-evidence claims is the runtime claim ledger (`research_assets/experiments/claim-ledger.yml`, claims C1–C9); each paper claim maps to it as: PC1→C4-rubric-decision-coverage; PC2→C1-fixture-asset-path and C4-rubric-decision-coverage; PC3→C3-baseline-comparison; PC4→C2-real-sut-verdicts; PC5→C7-conservation-diagnostic; PC6→C6-mirror-y-ood-stress; PC7→ no runtime-evidence claim (a method/ethics process boundary); PC8→C8-rollout-accuracy-baseline; PC9→C9-mirror-y-exact-symmetric-mesh; PC10→C10-seeded-fault-detection. The ledger's C5-precondition-check underlies the precondition gate described in the method section.

### 5.2 MR-Card-to-Verdict Map

| MR card | Rubric decision | Runtime verdict | What the verdict can and cannot mean |
|---|---|---|---|
| Node permutation equivariance | Retained as representation MR | pass sanity; relative L2 = 0.0 | Supports the executable path and representation contract for one case; does not establish model reliability. |
| Mirror-y equivariance (asymmetric eval mesh) | Exact relation out-of-relation-domain; downgraded to approximate OOD-stress | fail on 10 of 10 recorded eval frames; median relative L2 0.737; median V/floor 3.96 | Shows bounded within-SUT OOD-stress violation for one trajectory; does not by itself show exact symmetry failure, cross-SUT rate, or geometry-independent behavior. |
| Mirror-y equivariance (synthetic symmetric mesh) | Exact relation admissible (bijection verified, offset < 1e-12, type-match 1.0) | fail; relative L2 1.10 on one input state | Shows an exact-symmetry violation where the relation is admissible, removing the out-of-relation-domain objection; synthetic no-obstacle OOD mesh, one input; not an accuracy or cross-SUT claim. |
| Discrete divergence / conservation | Absolute mass-conservation MR deferred; reference-relative diagnostic retained | inconclusive: reference-relative non-regression guard on 2 frames (not scored as a conservation pass) | At 2 frames with a 50% slack threshold and an undecomposed reference divergence, this guards against regression but does not establish conservation. |

### 5.3 Within-SUT pilot evidence (single SUT, single checkpoint)

All pilots run on one real trained MeshGraphNets cylinder-flow surrogate
(read-only `Minimum-MR-SubSet`, checkpoint sha256 `cf281f85…`). They exercise
three different rubric outcomes and are scoped accordingly; raw outputs, manifests,
and metric ledgers are committed under `research_assets/runs/`.

- **Representation MR (correctness sanity check).** Node-permutation equivariance
  holds to machine precision (relative L2 = 0.0 at tolerance 1e-6). This is a
  structural property of message-passing and is reported only as a pipeline
  sanity check, not as model capability.
- **Geometric MR (out-of-relation-domain, approximate OOD-stress frame rate).**
  The rubric classifies exact mirror-y equivariance as out-of-relation-domain for
  this mesh (the reflection is non-bijective, the worst reflected-node mismatch is
  about one mesh edge length, and the cylinder is off-centre by 7.2 mm), and
  downgrades it to an approximate nearest-neighbour OOD-stress probe scored by the
  predeclared MR-card metric against a same-space mapping-error floor. Within the
  same SUT and checkpoint, the approximate mirror-y OOD-stress probe failed on 10
  of 10 recorded eval frames (median relative L2 0.737, median V/floor 3.96,
  3.02-5.55x mapping-error floor range); every recorded frame is kept in the
  denominator and none was skipped or inconclusive. This is a bounded within-SUT
  frame-level OOD-stress result under an approximate reflection: one SUT, one
  checkpoint, one MR, one eval trajectory. It is not an exact mirror-symmetry result
  and not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or
  geometry-independent claim. The 10 frames are consecutive states of one trajectory
  and are therefore not independent samples; the 10/10 count is evidence about one
  trajectory segment, and an exact binomial 95% interval for 10 successes in 10 trials
  is wide ([0.69, 1.00]). The V/floor ratio is normalized by a mapping-error floor that
  is itself a function of the same geometric mismatch that triggered the downgrade, so
  on this asymmetric mesh V/floor cannot fully separate a model-level violation from an
  amplified geometric artifact; the exact-symmetry run on a symmetric mesh below is what
  resolves that ambiguity.
- **Continuity MR (deferred absolute relation, reference-relative diagnostic).** A
  P1 discrete-divergence operator yields a non-negligible divergence even for the
  ground-truth field on this coarse mesh (dimensionless reference divergence ≈
  0.037), so an absolute divergence-free tolerance is not calibratable and the
  absolute mass-conservation relation stays deferred. As a reference-relative
  diagnostic, the surrogate's predicted next-state divergence stays within ~0.4–0.8%
  of the reference on the recorded eval frames (interior-only ratio confirms this is
  not a boundary-imposition artefact). This asserts no absolute conservation. Two
  caveats bound this diagnostic. First, the reference divergence ≈ 0.037 is not yet
  decomposed into discrete-operator error, solver projection artefact, or genuinely
  non-solenoidal training data; if the reference field is itself materially
  non-solenoidal, the reference-relative ratio compares two imperfect fields and is a
  non-regression guard rather than a conservation measurement. Second, the diagnostic
  uses a 50% regression threshold (ratio > 1.5) on two eval frames only, so "passes"
  means "does not regress conservation by more than 50% on those frames," not
  "conserves mass."

- **Rollout-accuracy diagnostic (accuracy comparator on the same SUT).** On the same
  eval trajectory, the surrogate's one-step next-state prediction error
  (`v_pred = v_t + denormalized predicted delta`, the trainer's own convention) has
  median relative L2 0.0216 (mean 0.044; min 0.0116, max 0.0788) over the nine recorded
  transitions. The per-transition error is bimodal (alternating ~0.012 and ~0.075),
  consistent with the vortex-shedding cycle, so we quote both statistics. The surrogate
  is therefore accurate in-distribution to a few percent per step, yet the mirror-y
  OOD-stress violation (median 0.737) is larger by roughly an order of magnitude — about
  34x the median accuracy and 17x the mean. Both quantities are dimensionless relative
  L2, but of different objects (equivariance of the model output versus next-state
  velocity error against the ground truth), so the ratio is an order-of-magnitude gap
  rather than a precise factor, and we do not compare the symmetric-mesh 1.10 to this
  number directly because their reference distributions differ. This is the first
  within-SUT evidence that the relation-level diagnostic and ordinary rollout accuracy
  answer different validation questions on this surrogate; it remains a same-SUT accuracy
  diagnostic, not a baseline-superiority, multi-trajectory, or cross-SUT claim, and it is
  one-step, not a free-running rollout-stability result.
- **Exact mirror-y on a symmetric mesh (admissible relation, out-of-sample test).** To
  test whether the mirror-y finding survives once the exact relation is admissible, we
  built a synthetic structured channel mesh that is provably symmetric about the
  centerline: the reflection is a verified bijection (node-type match 1.0, reflection
  offset < 1e-12, edge set invariant), so the admissibility predicate retains the exact
  relation rather than downgrading it. On one constructed input state the surrogate
  violated exact mirror-y equivariance with relative L2 1.10 (verdict fail). Because
  equivariance is oracle-free and structural — a mirror-equivariant model would satisfy
  it to machine precision regardless of accuracy — the nonzero result is not a geometric
  artifact, and it is an out-of-sample check that the admissibility predicate did not fit
  to the original three pilots. We ran one control to separate the learned weights from
  the input normalizer, which is fit to the asymmetric training data and so is not exactly
  equivariant in the transverse velocity: zeroing the normalizer's transverse-velocity
  mean (which makes it exactly equivariant in that component) changes the violation only
  from 1.1032 to 1.1014, so the normalizer accounts for about 0.2% of it and the violation
  is dominated by the learned message-passing weights, which carry no equivariance
  constraint. Two boundaries remain. The mesh is synthetic, has no obstacle, and is
  out-of-distribution for the cylinder-trained surrogate, so the *magnitude* 1.10 may be
  amplified by normalization mismatch relative to in-distribution behaviour; the result
  should be read as confirming that the surrogate carries no exact mirror-y equivariance
  constraint, while not bounding the in-distribution equivariance violation, rather than as a
  calibrated in-distribution magnitude. And this is one input on one mesh; it is not an accuracy, reliability,
  cross-SUT, or geometry-independent claim. The 1.10 magnitude is also larger than the
  asymmetric-mesh OOD-stress 0.737, which would be paradoxical if the symmetric mesh were
  the cleaner setting; the more likely reading is that the synthetic no-obstacle channel
  is itself more aggressively out-of-distribution for the cylinder-trained surrogate
  (Poiseuille-like profile rather than vortex shedding, no obstacle wake), so the larger
  magnitude reflects deeper OOD rather than a cleaner equivariance measurement. The two
  runs therefore answer different questions — admissibility of the relation, and severity
  of the violation under OOD — and the symmetric-mesh number should be read as a binary
  equivariance failure on an admissible relation, not as a directly comparable magnitude.
- **Seeded-fault detection (do the MRs catch known faults?).** We re-implemented, in
  pure numpy/torch from the read-only Minimum-MR-SubSet witness taxonomy, a catalogue of
  10 injected pipeline faults across five fault classes (boundary-condition, mesh-adjacency,
  normalization-scale, temporal-rollout, physical-channel), and used the paper's own MRs as
  detectors on the model's predicted update. The conservation (continuity) MR detected the
  two boundary-condition faults and the gross normalization fault (divergence ratio 3.8–10.6
  vs the 1.5 threshold); the mirror-y (symmetry) MR detected a physical-channel and a
  mesh-adjacency fault (violation rising 69–142% above its 0.735 baseline); node-permutation
  equivariance detected none, because these faults preserve node-relabeling invariance and
  the MR stays exact by design. Five of ten mutants were detected by at least one MR (at least
  one mutant per detected fault class), and the detections localize by MR class — continuity to
  boundary/scale faults, symmetry to physical-channel/adjacency faults — which is a first
  bounded test of the §3.6 interpretation protocol, suggestive rather than a validation. Three honesty notes bound this. First, the detected faults are gross corruptions (zeroed inflow, non-zero wall, un-denormalized update, swapped velocity channels, permuted edges) that any divergence- or symmetry-sensitive detector would catch; the catalogue is an independent taxonomy, not adversarial to these MRs but not designed for them. Second, two undetected cases are near or by-construction: the edge-drop fault is a near-miss (32% mirror-y change vs the 50% threshold), and the boundary-condition faults are invisible to mirror-y by construction because boundary imposition happens downstream of the update the symmetry MR scores. Three
  honesty notes bound this. First, the detected faults are gross corruptions (zeroed inflow,
  non-zero wall, un-denormalized update, swapped velocity channels, permuted edges) that any
  divergence- or symmetry-sensitive detector would catch; the catalogue is an independent
  taxonomy, not adversarial to these MRs but not designed for them. Second, two undetected
  cases are near or by-construction: the edge-drop fault is a near-miss (32% mirror-y change vs
  the 50% threshold), and the boundary-condition faults are invisible to mirror-y by
  construction because boundary imposition happens downstream of the update the symmetry MR
  scores. Third, the remaining undetected faults (doubling a small update, sign-flipping the
  step, zeroing the transverse update) shift the absolute output without crossing the
  scored-quantity thresholds, delimiting where these MRs are structurally insensitive. It is
  one SUT, one checkpoint, one injected-fault catalogue; it is not a real-world or general
  fault-detection rate, a reliability claim, or a baseline-superiority claim.

These pilots illustrate the direction of the paper's argument — that in-distribution
accuracy alone does not bound whether a surrogate respects physical structure (the
mirror-y violation is about 34x the one-step accuracy on the same SUT), and that an
evidence-gated rubric will refuse, downgrade, or admit a relation on stated grounds
rather than fabricate a verdict. They are pilot-scale, within one SUT and checkpoint,
and do not by themselves prove the general claim.

### 5.4 Still blocked

The following remain blocked and must not be written as results: cross-SUT or
geometry-independent pass/fail rates; comparative superiority over any baseline;
general or real-world fault-detection rates; localization accuracy as a validated
model; runtime or performance claims; and any claim that one SUT is more reliable than
another. The three METBENCH-planned SUTs, and the expert-MR, generic-MR-generation, and
LLM-candidate baselines, stay blocked pending their artifacts. Two exceptions are now
executed on the existing SUT and reported as scoped diagnostics, not as defeated
competitors or general rates: the rollout-accuracy comparator (Section 5.3), and a
bounded seeded-fault detection result over one 10-mutant injected-fault catalogue
(Section 5.3), whose by-class localization is suggestive evidence for, not a validation
of, the interpretation protocol.

## 6. Discussion

### 6.1 Interpretation of the Scoped Evidence

The value of the current study is not that every MR finds a new fault beyond rollout accuracy. Rather, the value is that retained MRs provide relation-level evidence under explicit transformations. When a violation or deferral is observed, the MR card and verdict rule help distinguish model inconsistency, relation-domain boundary, numerical tolerance problem, and inconclusive evidence.

The PR4 mirror-y evidence adds one bounded rate claim only: the approximate OOD-stress probe failed on 10 of 10 recorded eval frames for one SUT, one checkpoint, one MR, one eval trajectory. It remains an out-of-relation-domain exact mirror-y case and a bounded within-SUT frame-level OOD-stress result, not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim.

A natural objection is that the admissibility predicate merely re-describes the three outcomes it was introduced with — node permutation passes, mirror-y is downgraded, conservation is deferred — and is therefore fitted rather than tested. The two added within-SUT runs are designed to answer this. The symmetric-mesh run is an out-of-sample use of the predicate: the predicate states that on a symmetric mesh the exact mirror-y relation becomes admissible, and the experiment then tests that admitted relation independently, finding a genuine equivariance violation (relative L2 1.10) rather than confirming a pre-arranged result. The rollout-accuracy run supplies the accuracy comparator the original three pilots lacked, and shows the mirror-y violation is about 34 times the surrogate's in-distribution one-step error, so the relation evidence is not a restatement of accuracy. Neither run removes the central limitation — this is still one SUT and one checkpoint — but together they convert the mirror-y finding from a self-downgraded probe into an admissible-relation violation with an accuracy baseline.

The comparative baselines (expert MR design, generic MR generation, LLM candidates) remain blocked, so we cannot yet quantify what the rubric adds over unguided MR identification. We can, however, make the counterfactual concrete on the present evidence: the rubric averted two specific misreadings that an unguided application would plausibly have made. Without the numerical-decidability gate, the absolute discrete-divergence relation would have been executed and, because the surrogate's predicted divergence is close to the reference, recorded as a conservation *pass* — a false assurance, since the reference field itself carries non-negligible divergence and no calibrated tolerance exists; the rubric instead deferred it. Without the boundary-compatibility and bijectivity checks, the exact mirror-y failure on the asymmetric eval mesh would have been read as a model symmetry fault, when the symmetric-mesh run shows the exact relation is admissible elsewhere and the asymmetric-mesh violation is partly a geometric artifact; the rubric instead downgraded it to an OOD-stress probe and flagged the geometry. These are two concrete cases where the rubric prevented an overclaim that the candidate relation alone would have produced — a counterfactual argument for the workflow's value, pending the blocked baseline measurements.

### 6.2 Boundary of Claims

The paper must avoid four overclaims. It must not claim that MRs are always better than rollout accuracy. It must not claim that NOETHER proves the physical validity of cylinder-flow MRs. It must not claim that LLMs can automatically identify valid MRs. It must not generalize from three MeshGraphNets-family configurations to all SciML surrogates.

The safer claim is that a domain-validity-aware workflow can make MR identification and execution more auditable for a concrete class of SciML SUTs.

### 6.3 Implications for SciML Testing

The scoped evidence shows how SciML testing can move from implicit expert checks to explicit MR assets. Such assets can complement residuals, uncertainty estimates, and accuracy metrics by making transformation assumptions and verdict rules inspectable. This is especially important for OOD validation, where the boundary of the relation is often as important as the violation itself.

In that sense the workflow is aimed at producing, over many controlled transformations, a relation-indexed applicability map: a record of where a surrogate stops respecting the relations it should respect, expressed in relation space rather than in residual space. The present evidence is one bounded within-SUT point on such a map, not the map itself; assembling a calibrated map would require the cross-SUT, multi-trajectory, and domain-violation-score work that remains future work.

## 7. Threats to Validity

**Construct validity.** MR validity depends on the rubric, physical assumptions, boundary-condition compatibility, and tolerance rules. Incorrect discrete operators or thresholds may create false violations or false passes.

**Internal validity.** SUT setup, checkpoint differences, random seeds, mesh preprocessing, and runtime nondeterminism may affect verdicts. The experiment ledger must record these details.

**External validity.** The study is limited to MeshGraphNets-family cylinder-flow implementations or configurations. It should not be generalized to all neural operators, PINNs, or fluid surrogates without further evidence.

**Baseline fairness.** Generic MR-generation and LLM baselines may not be designed for SciML. They should be interpreted as scope contrasts and candidate-generation comparators, not as defeated competitors.

**Conclusion validity.** Small sample sizes, multiple MRs, and many transformation bins can produce unstable conclusions. The mirror-y evidence has a bounded within-SUT frame-level OOD-stress rate, while conservation and node permutation remain pilots. Broader rates, external validity, seeded-fault effectiveness, reliability, accuracy, and baseline claims remain blocked.

**Reproducibility.** Some SUTs may depend on old runtimes or non-redistributable checkpoints. The paper should disclose such barriers and provide the most complete runnable package possible.

## 8. Conclusion

This paper presents domain-validity-gated MR identification as an auditable oracle-free testing workflow for MeshGraphNets-family cylinder-flow surrogates. The current evidence supports one bounded within-SUT frame-level OOD-stress result for mirror-y, plus scoped node-permutation and conservation pilots. It does not support broader rates, external-validity claims, seeded-fault claims, baseline comparisons, reliability conclusions, accuracy conclusions, exact mirror-y claims, or absolute conservation claims. The central claim remains methodological: physically meaningful SciML MRs require explicit validity conditions, executable assets, raw evidence records, and relation-level verdicts.

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
