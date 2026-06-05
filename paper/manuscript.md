# Validity-Gated Metamorphic Testing of Mesh-Based Neural Surrogates: A Domain-Validity Rubric and Executable MR Assets for Scientific Machine Learning

> Manuscript draft for IST regular track.  
> Draft status: v0.5 evidence-gated draft with a realized single-SUT case study, 2026-06-05.  
> One MeshGraphNets surrogate is realized end-to-end (Section 5); cross-SUT rates and baseline comparisons remain future work.

## Target and Scope

- Primary target: *Information and Software Technology* regular research-paper track.
- Paper type: empirical software engineering / software testing and V&V method paper.
- Review framing: software testing contribution first; SciML and cylinder flow are the application context.
- Word limit target: keep the submitted paper below 15,000 words.
- Current draft policy: write Background, Motivation, Method, Empirical Design, and Threats; do not write empirical findings before artifacts exist.

## Structured Abstract

### Context

Scientific machine-learning (SciML) surrogates are increasingly used to approximate expensive physical simulations. Mesh-based neural simulators are attractive for fluid-flow problems because they operate on irregular meshes and predict spatiotemporal physical fields. Testing such systems is difficult because exact expected outputs are often unavailable for arbitrary inputs without running a trusted high-fidelity solver. Rollout accuracy and physics residuals provide useful evidence, but they do not by themselves specify which physical relations should hold under controlled transformations of inputs, meshes, boundary conditions, or parameters.

### Objective

This paper investigates how physically meaningful metamorphic relations (MRs) can be screened and operationalized as executable oracle-free test assets for scientific machine-learning systems. The goal is not to improve a predictive model, but to make the step from candidate relation to executable test asset more systematic, auditable, and explicit about the physical, numerical, and software conditions under which each relation is expected to hold. MeshGraphNets-family cylinder-flow surrogates are used as the concrete case study.

### Method

We propose a domain-validity rubric for screening candidate MRs, an MR-card and executable-asset format that records source cases, follow-up transformations, output mappings, metrics, tolerances, exclusion rules, and relation-level verdicts, and a case-study protocol for applying these assets to mesh-based neural cylinder-flow surrogates. Candidate sources may include physical equations, boundary conditions, representation contracts, expert reasoning, LLM-assisted candidate lists, and NOETHER-style pattern organization, but validity is decided by the rubric and evidence records rather than by candidate generation alone.

### Results

The workflow is realized end-to-end on one real trained MeshGraphNets cylinder-flow surrogate, where the rubric produces all four screening outcomes (retained, retained-as-OOD-stress, deferred, rejected) on four candidate relations and three relations are then executed with recorded relation-level verdicts. The substantive runtime finding is that the rubric flags exact mirror-y equivariance as out-of-relation-domain for this off-centre-cylinder mesh and downgrades it to an OOD-stress probe, which is violated on all ten consecutive frames of one eval trajectory; the other two executed relations (a representation-level permutation equivariance and a reference-relative divergence diagnostic) return the outcomes expected for a correct, in-distribution surrogate and serve mainly as sanity and calibration checks. Full results remain blocked pending cross-SUT artifacts; this draft makes no claims about cross-SUT or geometry-independent rates, fault-detection rates, comparative performance, localization accuracy, model accuracy, or SUT reliability.

### Conclusion

The contribution is a validity-aware bridge from candidate MR ideas to auditable SciML test assets, demonstrated end-to-end on one real trained MeshGraphNets cylinder-flow surrogate. On that single SUT the workflow produces all four rubric outcomes and three executed relation-level verdicts (a representation-MR pass, an out-of-relation-domain symmetry relation whose downgraded OOD-stress probe is violated on every recorded frame, and a deferred conservation relation with a passing reference-relative diagnostic). The paper positions MRs as a complement to rollout accuracy, residuals, uncertainty estimates, and equivariance errors: these diagnostics become executable oracle-free relations only when paired with valid transformations, explicit preconditions, exclusion rules, and auditable verdict records. Cross-SUT rates and baseline comparisons remain future work.

## Keywords

Metamorphic testing; test oracle problem; metamorphic relation identification; software verification and validation; domain-validity screening; scientific machine learning; mesh-based neural surrogates (MeshGraphNets); cylinder flow.

## 1. Introduction

Scientific computing increasingly uses learned surrogates to reduce the cost of repeated numerical simulation. In fluid dynamics, mesh-based neural simulators such as MeshGraphNets learn to predict physical fields on irregular meshes and can provide fast rollout predictions for benchmark problems such as flow around a cylinder. These models are useful because they can approximate high-cost solvers, but they also create a familiar software testing problem in a new setting: for many candidate inputs, there is no cheap and exact expected output against which the program can be checked.

The common response is to evaluate a surrogate on held-out trajectories and report rollout error. This is necessary, but it is not the whole validation problem. A model may have acceptable average error on a finite test set while still failing to preserve relations that should hold under a physically meaningful transformation. Conversely, a high error value does not always explain which physical, numerical, or representational condition has been violated. For a user who wants to deploy a SciML surrogate outside a narrow validation set, the practical question is not only "How accurate is the model on these samples?" but also "Under which transformations or regimes does this system stop respecting the relations it should respect?"

Metamorphic testing (MT) [2], [3] addresses the test-oracle problem by checking relations among multiple executions instead of requiring an exact output for each individual test case. The idea originates in test-case generation work by Chen et al. [4] and has since been surveyed and reviewed extensively [2], [3]. A metamorphic relation states that if a source input is transformed in a specified way, the corresponding outputs should satisfy a necessary relation. This is a natural idea for scientific computing: conservation laws, symmetry relations, nondimensional similarity, boundary constraints, continuity conditions, and numerical stability expectations all suggest possible relations among executions.

The difficult part is deciding which candidate relations are valid and executable for a particular SciML program. A transformation that looks plausible at a high level may violate the governing assumptions, boundary conditions, discretization choices, or measurement tolerance of the actual system under test (SUT). For cylinder flow, mirror symmetry depends on geometry and boundary labels; translation invariance depends on how coordinates and domain boundaries are represented; Reynolds-Strouhal similarity depends on nondimensionalization and flow regime; a divergence check depends on a discrete divergence operator, mesh weights, and boundary treatment. Treating such transformations as automatically valid MRs would make the test suite look rigorous while hiding the very assumptions that determine whether a violation is meaningful.

Prior work on scientific-software MT, simulation testing, design-assumption MRs, and SciML reliability shows that relation-based and residual-based evidence is useful when direct oracles are limited. Recent candidate leads also suggest that physics-based MRs are being explored for learned physical-field or fluid-velocity predictors, but the currently verified record is not strong enough to support a first-or-only novelty claim. The remaining problem addressed here is therefore narrower: how candidate MRs are screened for domain validity, turned into executable test assets, and reported through relation-level verdicts that distinguish SUT inconsistency from out-of-relation-domain cases and numerical tolerance effects.

This paper treats MR identification for SciML as a validity-gated testing problem. Physical knowledge, expert reasoning, LLM-assisted candidate lists, and NOETHER-style pattern organization can all suggest candidate relations, but a candidate relation is not yet an executable MR. It must first state the physical or software basis of the relation, the transformation preconditions, boundary-condition compatibility, output mapping, metric, tolerance rationale, exclusion rule, and verdict interpretation. Only retained relations are converted into executable MR assets.

The case study is scoped to MeshGraphNets-family cylinder-flow surrogates. This is an intentionally narrow empirical setting rather than the paper's main conceptual contribution. It allows us to examine transformations over meshes, geometry, velocity fields, nondimensional quantities, and rollout behavior while keeping the SUT family concrete enough for reproducible testing. The evaluation is planned across three implementations or configurations, but we do not claim external validity across all neural fluid surrogates.

### 1.1 Research Questions

The main research question is:

**RQ0. How can candidate metamorphic relations for scientific machine-learning systems be screened for domain validity and converted into executable oracle-free test assets without relying on exact per-sample expected outputs?**

We decompose this into four questions.

**RQ1 - Validity.** How can a domain-validity rubric distinguish physically meaningful candidate MRs from transformations that are executable but invalid, underspecified, or outside the relation's domain?

**RQ2 - Operationalization.** How can retained candidates be represented as MR cards and executable assets with source cases, follow-up transformations, metrics, thresholds, exclusions, and verdict rules?

**RQ3 - Verdict and interpretation.** How can relation-level verdicts distinguish pass, fail, skip, out-of-relation-domain, numerical tolerance issue, and inconclusive outcomes?

**RQ4 - Comparative case-study evidence (future work).** In a MeshGraphNets-family cylinder-flow case study, what evidence does the rubric-gated asset workflow add relative to expert MR design, LLM-assisted candidate generation, generic MR-generation scope contrasts, and rollout-accuracy diagnostics? This paper addresses RQ1–RQ3 with a realized single-SUT case study and treats RQ4 as a planned comparison; the baseline runs and cross-SUT data required to answer it are not yet available, and we do not report comparative results.

### 1.2 Contributions

This paper is planned around four contributions.

First, we propose a domain-validity rubric for screening candidate MRs in SciML testing. The rubric checks whether a candidate relation has a clear physical basis, compatible boundary conditions, a semantics-preserving transformation, a measurable output relation, an interpretable tolerance, and a diagnosable failure mode.

Second, we define an MR-card and executable-asset workflow that converts retained candidates into auditable test assets. NOETHER-style pattern organization may be used as one candidate source, but it is not the contribution being evaluated here and it does not decide MR validity.

Third, we define a relation-level verdict and ledger scheme. Each retained MR records a source-case schema, follow-up transformation, output mapping, metric, tolerance rule, exclusion rule, and verdict interpretation. This converts physical diagnostics such as residuals, conservation errors, and equivariance errors into auditable oracle-free tests only when their transformation and validity conditions are explicit.

Fourth, we exercise the workflow in a MeshGraphNets-family cylinder-flow case study. We realize it end-to-end on one real trained surrogate, where the rubric produces all four screening outcomes and three relations are executed with recorded relation-level verdicts and committed artifacts (Section 5). The planned comparison of retained MRs with expert MR design, generic MR-generation scope contrasts, LLM-assisted candidate generation, and rollout-accuracy baselines, and the extension to additional surrogates, remain future work; we do not state cross-SUT or comparative results.

## 2. Background and Related Work

### 2.1 Mesh-Based Neural Simulation

Mesh-based neural simulators learn dynamics on graph or mesh representations of physical systems [5], [6]. For fluid-flow problems, a mesh representation is attractive because the geometry, boundary regions, and local connectivity can be represented without forcing the state onto a regular grid. MeshGraphNets [5] is a representative architecture family in this area: it encodes mesh nodes and edges, propagates information by message passing, and predicts future physical fields through autoregressive rollout. It builds on graph-network simulators for particle and mesh systems [6], and the cylinder-flow benchmark used in our case study is distributed with it [5].

The cylinder-flow benchmark is useful for testing because it combines several features that matter for SciML validation. It involves geometry, boundary conditions, velocity fields, pressure-like quantities or derived quantities, temporal rollout, and flow-regime assumptions. It also exposes the distinction between data-driven accuracy and physical relation preservation. A model may fit a trajectory distribution while failing under a controlled transformation of geometry, mesh representation, or flow parameters.

In this paper, MeshGraphNets-family systems are treated as software systems under test. We do not evaluate them as new modeling contributions. Instead, we ask how their outputs behave under controlled input transformations and whether necessary relations remain within explicit tolerances.

### 2.2 Metamorphic Testing and the Oracle Problem

Metamorphic testing was developed to address programs for which it is difficult or impossible to know the correct output for a single test input [4]. Instead of checking one output against one expected value, MT checks a relation among the outputs of a source input and one or more follow-up inputs. This framing has been applied to scientific software, simulation models, and machine-learning systems, all of which can suffer from oracle problems; for machine-learning classifiers in particular, metamorphic relations have been used as a validation technique in the absence of exact oracles [7].

For SciML surrogates, the oracle problem is especially visible in out-of-distribution (OOD) settings. A trusted solver may be too expensive to run for every transformed case, and even when a reference output is available, a single pointwise error does not necessarily indicate whether a physical relation has been preserved. MR-based testing offers a complementary perspective: it asks whether the SUT maintains a necessary relation under a controlled transformation.

However, SciML MRs cannot be treated as generic input perturbations. In image-based ML testing, transformations such as lighting or weather changes may preserve the semantic label. In scientific computing, the transformation must respect governing equations, physical regimes, boundary conditions, mesh representation, and numerical tolerance. The correctness of the MR itself becomes a central validity question.

### 2.3 MR Identification for Scientific and Simulation Software

Prior work on scientific software testing has shown that MRs can be elicited from monotonicity, conservation-like behavior, scaling relations, simulation assumptions, and domain-specific expectations. Work on simulation validation similarly treats multi-run relations as pseudo-oracles when direct validation data are limited or unavailable. These studies establish that MR thinking is practical for scientific and simulation software, not merely for toy functions.

Other work has explored automated or semi-automated MR identification. For example, Hiremath et al. [10] pursue automated metamorphic test identification for ocean system models, using known physical symmetries to discover candidate transformations in complex simulation software where oracles rarely exist. Mandrioli et al. [1] show, for cyber-physical systems, that design assumptions can be encoded as metamorphic relations and combined with genetic programming to generate new test traces. These ideas are important for the present paper because they show that MR sources can include system assumptions, model structure, and physical design knowledge. Our setting differs in that the validity of a candidate relation for a mesh-based neural PDE surrogate depends on geometry, boundary labels, discretization, and numerical tolerance, which is exactly what the domain-validity rubric is designed to screen.

The gap is that candidate identification is not enough for SciML. A candidate relation must also state when it is supposed to hold. Without a domain-of-validity record, a failed test may mean several different things: the relation was invalid under the chosen boundary conditions, the transformation left the physical regime, the tolerance was not numerically justified, or the SUT violated a relation it should have preserved. This paper makes that distinction explicit.

### 2.4 Physics-Based MT for Learned Scientific Simulators

The most directly related work applies physics-based metamorphic and mutation testing to learned fluid-velocity predictors. Yu et al. [11] study mutation-testing strategies for intelligent models that predict fluid-velocity fields, which is the closest reported use of physics-motivated metamorphic ideas for learned fluid predictors (we cite it as a closest-work lead established from its publisher record; we did not inspect its full text and make no claim about its specific method). We therefore explicitly do not claim to be the first to apply physics-based MT to learned fluid or field predictors. (A further physical-field-prediction lead exists but could not be confirmed against a trusted record and is not relied upon here.)

Our contribution is narrower and methodological, and we state the differentiator positively. Relative to scenario-level physical consistency checks and to prior physics-motivated MT for learned predictors, the unit of contribution here is the *validity gate and its auditable record*, not the idea that physical relations can be tested. Concretely, the workflow (i) screens each candidate with a domain-validity rubric that emits one of four explicit decisions — retained, retained-as-OOD-stress, deferred, rejected — rather than treating every physically motivated transformation as a usable MR; (ii) represents each retained relation as an executable MR card with declared preconditions, boundary-condition compatibility, output mapping, metric, tolerance provenance, exclusion rules, and a verdict taxonomy that includes an out-of-relation-domain category; and (iii) records every decision and every executed verdict, with raw outputs and provenance, in a fail-closed ledger so the screening and the result are both auditable. The practical payoff is that a test report can distinguish a model inconsistency from a relation applied outside its valid domain, and can show *why* a candidate was downgraded, deferred, or rejected — distinctions that an undifferentiated physics-MT suite does not record.

### 2.5 SciML V&V, Residuals, UQ, and Failure Modes

SciML reliability research has developed several important tools: physics residuals, uncertainty quantification, conformal prediction, certified error bounds, stress testing, equivariance error [9], and failure-mode analysis [8]. These tools address real weaknesses of learned PDE solvers and neural surrogates. For example, calibrated physics-informed uncertainty quantification uses PDE residuals as nonconformity scores and provides statistical coverage guarantees. Work on physics-informed neural network failure modes [8] shows that physical constraints in a training loss do not guarantee reliable behavior in more difficult regimes. Equivariance, in turn, is a structural property that can be built into a network's architecture [9]; our representation-level relation (Section 5) checks an equivariance that the message-passing architecture is expected to satisfy by construction, which is exactly why we treat its result as a sanity check rather than as model-capability evidence.

These methods are complementary to MT. A residual, conservation error, or equivariance error can be a useful diagnostic, but it is not automatically an MR. It becomes part of an executable relation only when there is a source case, a follow-up transformation, an expected output relation, a tolerance rule, and a verdict interpretation. This distinction is central to our paper. We use SciML diagnostics as possible relation measurements, while MT supplies the multi-execution oracle-free structure.

### 2.6 Hybrid ML-Solver Trust Regions

Hybrid ML-solver frameworks provide another relevant line of work. Some systems use residual thresholds or error estimates to decide when a learned component should be trusted and when a numerical solver should take over. Such systems operationalize a form of trust region, although often at runtime and through residual-based switching rather than offline relation-based testing.

Our study pursues a complementary direction. Before deployment, physically derived transformations are used to estimate where relation violations occur and what regimes, boundary conditions, or numerical assumptions are associated with them. The result is not a runtime switching policy by itself, but an evidence structure that can support later decisions about when a learned surrogate should be trusted.

## 3. Method

### 3.1 Overview

The proposed method is a five-stage workflow:

1. identify candidate relation sources;
2. organize candidate relations using declared candidate-source categories;
3. screen candidates with a domain-validity rubric;
4. convert retained relations into executable MR assets;
5. execute the assets and record relation-level verdicts.

The method deliberately separates candidate generation from validity judgment. NOETHER-style patterns may help organize or generate candidate relation structures, but they do not certify that a relation is physically valid for a particular SUT, dataset, mesh, boundary condition, or numerical tolerance. Validity is determined by the rubric and by executable evidence.

Figure 1 summarizes the workflow. Candidate relations from several sources flow
into the domain-validity rubric, which emits one of four screening decisions.
Retained and retained-as-OOD-stress relations become MR cards and executable assets;
executing an asset against a system under test produces a relation-level verdict that
is recorded, with its raw outputs and provenance, in an auditable ledger. Deferred and
rejected candidates are also recorded, with the rubric reason, so the screening itself
is auditable.

**Figure 1. Validity-gated MR workflow (textual schematic).**

```
 candidate sources                    domain-validity rubric            assets & evidence
 ------------------                   ----------------------            -----------------
 physical equations    \                                       retain ----> MR card --> executable asset
 symmetry assumptions   \   organize    +-------------------+   OOD-stress -> MR card --> executable asset
 nondimensional laws     >----------->  | 6/7 rubric        |---------------------------------+
 mesh/representation    /   (NOETHER,   | criteria,         |   defer -----> recorded reason  |
 temporal rollout      /     expert,    | 4 decisions       |   reject ----> recorded reason  |
 cross-implementation        LLM)       +-------------------+                                  |
                                                                                               v
                                          SUT execution  -->  relation-level verdict  -->  ledger (raw
                                          (manifest, runner)   (pass/fail/skip/OoRD/        outputs, metric,
                                                               num-tol/inconclusive)        rubric decision)
```

### 3.2 Candidate Relation Sources

For cylinder-flow surrogates, candidate MRs may come from six sources.

**Physical equations and constraints.** Incompressible continuity, boundary behavior, and conservation-like expectations can suggest relation measurements such as discrete divergence or boundary-condition consistency.

**Geometric and symmetry assumptions.** Mirroring, rigid transformations, and coordinate-frame changes may suggest equivariance or invariance checks, but only under compatible geometry and boundary labels.

**Nondimensional similarity.** Reynolds-number and Strouhal-number relations may suggest follow-up transformations over flow parameters or extracted wake behavior, but only within regimes where the empirical or theoretical relation is meaningful.

**Mesh and graph representation.** Node permutations, face ordering, edge encoding, and mesh refinement may suggest representation-level MRs.

**Temporal rollout behavior.** Autoregressive rollouts may suggest determinism, prefix consistency, or semigroup-like sanity checks. These are useful implementation or numerical-consistency checks, but should not be overstated as physical laws.

**Cross-implementation comparison.** Outputs from different implementations may support method-comparison checks only if units, state variables, meshes, rollout horizons, boundary conditions, and checkpoints are comparable. Otherwise they are triangulation evidence rather than retained MRs.

### 3.3 Domain-Validity Rubric

Each candidate MR is screened using a rubric with seven criteria: six design criteria that judge whether the relation is physically and operationally well-posed, and a seventh executability gate. The seven correspond one-to-one to the dimensions in the released rubric artifact.

**Physical basis.** The relation must cite its source: governing equation, boundary condition, nondimensional law, representation property, numerical assumption, or implementation contract.

**Transformation preconditions.** The source-to-follow-up transformation must state what is changed and what is preserved. For example, a mirror relation must specify how coordinates, vector components, node types, and boundary labels transform.

**Boundary-condition compatibility.** The relation must hold under the boundary conditions of the transformed case. If the transformation changes the physical meaning of a boundary, the candidate is rejected or marked as an OOD stress test rather than a physics-preserving MR.

**Output mapping.** The expected relation among outputs must be measurable. A relation that cannot be mapped to available output fields is not executable.

**Metric and tolerance.** The verdict rule must define a metric and a tolerance. The tolerance may come from numerical precision, solver reference behavior, calibration data, repeated-run variability, or expert thresholding, but the source must be recorded.

**Failure diagnosability.** The relation should indicate what kind of failure or boundary condition it can help interpret. If every possible violation has the same ambiguous meaning, the relation is weak evidence and should be treated cautiously.

**SUT runtime requirements (executability gate).** The relation must be executable against the SUT with the available dataset, checkpoint, mesh format, and runtime. A relation that is otherwise well-posed but cannot yet be run on any accessible system under test is deferred rather than retained, and the missing runtime prerequisites are recorded. In our case study this gate, together with the metric-and-tolerance criterion, is what keeps the divergence relation deferred until a calibrated operator and an executable configuration exist (Table 1).

The rubric outputs one of four screening decisions:

- retained as executable MR;
- retained as OOD stress relation, not physics-preserving MR;
- rejected as invalid or underspecified;
- deferred pending missing evidence, such as a discrete operator or threshold.

Table 1 shows the four screening decisions instantiated on the four cylinder-flow
candidates used in this study. The same candidate set later supplies the executed
relations in Section 5, so the rubric outcome and the runtime evidence can be read
together.

**Table 1. Rubric screening decisions for four cylinder-flow MR candidates.**

| Candidate | Source category | Decisive rubric criterion | Decision |
|---|---|---|---|
| Node-permutation equivariance | Mesh/graph representation | Reindexing preserves geometry and boundary labels; transformation and inverse mapping fully specified | retained (executable MR) |
| Mirror-y equivariance | Geometric/symmetry | Boundary-condition compatibility fails on the measured mesh (off-centre cylinder, non-mirror-symmetric geometry) | retained as OOD stress relation, not physics-preserving |
| Discrete divergence boundedness | Physical equation (continuity) | Metric/tolerance not calibratable: reference field already has non-negligible discrete divergence on a coarse mesh | deferred pending a calibrated operator/tolerance |
| Viscous time reversal | Physical equation (temporal) | Physical basis fails: viscous cylinder flow is dissipative and not time-reversal invariant | rejected as invalid |

The decisions are not symmetric in cost. Rejection and deferral remove candidates
that would otherwise inflate an apparently rigorous suite, and the OOD-stress
downgrade keeps a useful stress probe while preventing it from being reported as a
physics-preserving equivalence. Each decision is recorded with its evidence
references in a candidate ledger so that another reviewer can audit why a relation
was retained, downgraded, deferred, or rejected.

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

We further distinguish **MR-level** verdicts from **probe-level** verdicts, because the two answer different questions. An MR-level pass or fail is a verdict on a relation that the rubric retained as a physics-preserving MR within its valid domain: a fail is evidence about the SUT. A probe-level verdict arises when the rubric has already classified the exact relation as out-of-relation-domain and retained only an approximate stress probe; the probe's pass or fail then describes the behavior of that approximate construction, not a clean verdict on the exact relation. A probe-level fail therefore says "the SUT does not satisfy the (approximate) stress relation," and attributing that failure to a specific cause — geometry, the approximate transformation, or the model — requires the additional analysis recorded with the run, not the verdict label alone. Tables 1 and 2 annotate which verdicts are MR-level and which are probe-level.

### 3.6 Hierarchical Interpretation Protocol (design sketch)

We organize retained MRs into a hierarchy inspired by scientific-computing MR classification: physical-model relations, computational-model relations, and code-model relations. For learned mesh surrogates, the computational-model level includes graph representation and message-passing discretization assumptions. The intent is a predeclared protocol in which representation-level MRs point to graph-encoding issues, physical-model MRs to continuity, symmetry, or similarity violations, and code-model MRs to determinism or rollout issues. We present this only as a design sketch: it is a localization *protocol*, not a validated localization model, and it can be validated only with seeded faults or mutants of known layer, which are out of scope for the present single-SUT study and are left to future work.

## 4. Empirical Design

Sections 4.1–4.5 describe the full planned study; the realized evidence is the
single-SUT case study reported in Section 5. We keep the planned design here because
it fixes the subject systems, MR classes, comparators, metrics, and analysis against
which the realized pilot — and the still-blocked cross-SUT work — should be read; the
future-tense passages below are commitments, not reported results.

### 4.1 Subject Systems

The planned study uses three MeshGraphNets-family implementations or configurations:

1. an echowve MeshGraphNets PyTorch/PyG implementation;
2. NVIDIA PhysicsNeMo `vortex_shedding_mgn`;
3. DeepMind TF1 MeshGraphNets, or an equivalent third MeshGraphNets-family implementation or configuration if runtime feasibility requires substitution.

For each SUT, the experiment ledger will record repository URL, commit, checkpoint, dataset, mesh format, input fields, output fields, rollout horizon, random seeds, environment, and known runtime limitations. Because these SUTs share a task and architecture family, the study will be framed as a same-family stress test, not as evidence for all neural fluid surrogates.

At the time of writing, one configuration in this family has been realized
end-to-end and supplies the executed verdicts in Section 5: a pure-PyTorch
MeshGraphNet (encode–process–decode, 176k parameters) trained on the official
DeepMind `cylinder_flow` benchmark and evaluated on a held-out test trajectory.
Its repository commit, checkpoint sha256, dataset slice hashes, exact commands, and
raw outputs are recorded so that every reported number is auditable. The echowve and
PhysicsNeMo implementations remain blocked pending their dataset, checkpoint,
command, and output artifacts; we therefore report single-SUT evidence and treat
cross-implementation results as future work rather than as current findings.

### 4.2 Planned MR Classes

The initial MR set will be grouped into six classes:

**Representation MRs:** node permutation, face-order invariance, and encoding consistency.

**Geometric and symmetry MRs:** mirror-y equivariance and rigid transformation candidates, retained only under boundary-compatible conditions.

**Continuity and constraint MRs:** discrete divergence or mass-continuity checks with explicit mesh weighting and boundary treatment.

**Nondimensional similarity MRs:** Reynolds-Strouhal or scaling candidates, retained only under nondimensional and regime-compatibility checks.

**Numerical stability MRs:** small perturbation stability, mesh perturbation, or refinement consistency candidates.

**Temporal and implementation MRs:** rollout prefix consistency, deterministic execution, and conditional cross-implementation comparison.

Time reversal is excluded as a retained MR for viscous cylinder flow, because the viscous Navier–Stokes dynamics are dissipative and not time-reversal invariant. Divergence is treated as the kinematic incompressibility (continuity) constraint of the incompressible Navier–Stokes equations — enforced in the solver as a Lagrange-multiplier (pressure) condition — and not as a Noether-derived conservation law; in the viscous, dissipative setting Noether's theorem does not supply this constraint, and the incompressible particle-relabelling symmetry yields Kelvin's circulation theorem rather than pointwise mass conservation.

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
- MR violation rate: the proportion of valid-domain executions that fail the relation (computed only over relations retained as physics-preserving MRs; probe-level executions of out-of-relation-domain relations are reported separately and are not counted in this denominator);
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

### 4.5 Statistical Plan (for the planned multi-SUT study)

The following plan applies to the full multi-SUT study, which is not yet executed;
the realized single-SUT case study in Section 5 is below the sample size at which
this machinery is meaningful, and we deliberately report it qualitatively rather than
with inferential statistics (Section 5.1). When the cross-SUT data exist, violation
rates will be reported with confidence intervals, treating the trajectory (not the
individual autocorrelated frame) as the unit of analysis. Paired comparisons will be
used where the same source cases and transformations are run across SUTs or baselines.
For binary verdict comparisons, McNemar or Fisher-style tests may be used when
assumptions are appropriate. For continuous violation magnitudes, paired bootstrap
intervals are preferred. When many MRs or transformation bins are compared,
multiple-comparison correction or false-discovery-rate control will be reported. If the
number of executable cases is small, the study will emphasize effect sizes, confidence
intervals, and qualitative failure interpretation rather than strong significance claims.

### 4.6 Ethics, Integrity, and Reproducibility

The planned study does not involve human subjects, personal data, or private sensitive information. The main ethical and integrity issues are research transparency, AI use, and reproducibility.

All SUT versions, datasets, checkpoints, scripts, and run logs should be recorded when licensing permits. Failed, skipped, and inconclusive cases must remain in the experiment ledger. LLM use is restricted to candidate generation and evidence organization; it is not used as a final judge of MR validity. No candidate MR should be described as valid unless it passes the rubric and has a corresponding MR card. No OOD violation should be described as a program fault without the verdict evidence needed to support that interpretation.

Third-party code, datasets, and model checkpoints will be used according to their licenses. If any artifact cannot be redistributed, the paper will provide access instructions and record the limitation.

## 5. Results

Full cross-SUT, comparative, and fault-detection results remain **blocked** (see
5.2). This section reports only strictly scoped, within-SUT pilot evidence whose
artifacts are committed and validated.

### 5.1 Within-SUT pilot evidence (single SUT, single checkpoint)

All pilots run on one real trained MeshGraphNets cylinder-flow surrogate
(read-only `Minimum-MR-SubSet`, checkpoint sha256 `cf281f85…`). They exercise
three different rubric outcomes and are scoped accordingly; raw outputs, manifests,
and metric ledgers are committed under `research_assets/runs/`.

- **Representation MR (correctness sanity check; MR-level pass).** Node-permutation
  equivariance holds to machine precision (relative L2 = 0.0 at tolerance 1e-6). This
  is a structural property of message passing and is reported only as a pipeline
  sanity check, not as model capability. The result is exactly 0.0 rather than ~1e-7
  because the run executes on CPU in float32, where the scatter aggregation is
  order-deterministic and therefore invariant to node reindexing; on a GPU or in mixed
  precision the value would be small but nonzero, which is what the 1e-6 tolerance
  guards against.
- **Geometric MR (out-of-relation-domain; probe-level fail).** The rubric classifies
  exact mirror-y equivariance as out-of-relation-domain for this mesh: the reflection
  about the channel centerline is non-bijective, the worst reflected-node mismatch is
  about one mesh edge length, and the cylinder center sits ≈7.2 mm below the
  centerline. (This off-centring is a deliberate design choice
  of the DFG laminar cylinder-flow benchmark [12] that breaks geometric symmetry and
  triggers the Kármán vortex street at Re ≈ 100; the standard DFG geometry places the
  cylinder ≈5 mm from the channel centerline, and the measured 7.2 mm indicates the
  released mesh differs slightly from the nominal geometry.) The single-step mirror relation is, in
  principle, valid even on an instantaneous (asymmetric) shedding frame: because the
  Navier–Stokes equations are y-reflection symmetric under symmetric boundary
  conditions, a perfectly equivariant predictor should map a mirrored input state to
  the mirror of the original predicted output. The failure therefore reflects the
  geometric precondition failure, not the temporal asymmetry of shedding. The rubric
  consequently downgrades the relation to an approximate nearest-neighbour OOD-stress
  probe scored by the predeclared MR-card metric against a same-space mapping-error
  floor. Under that probe the surrogate fails on all ten consecutive frames of one
  eval trajectory (median relative L2 0.737; per-frame ratio to the floor in the range
  3.0–5.5×; every recorded frame kept in the denominator, none skipped or
  inconclusive). Because these are consecutive frames of a single rollout they are not
  independent observations, so we treat the trajectory as the unit of analysis and
  report the outcome qualitatively rather than as a calibrated rate. The mapping-error
  floor (≈13–25% of the field norm) estimates what the approximate reflection alone
  could contribute, but it is a heuristic, not a clean additive decomposition: the same
  approximate correspondence also distorts the fields being compared, so the per-frame
  ratio of 3.0–5.5× should be read as an upper bound on the model's own non-equivariance
  contribution rather than a lower bound — the residual cannot be cleanly partitioned
  among the geometric precondition failure, the approximate map, and the model. This is
  a probe-level outcome, not an MR-level verdict on the SUT's correctness; the
  defensible statement is that mirror-y equivariance does not hold for this SUT on this
  mesh under the predeclared probe — not a reliability, accuracy, baseline, multi-SUT,
  exact-symmetry, or geometry-independent claim.
- **Continuity MR (deferred absolute relation; reference-relative diagnostic).** A P1
  (piecewise-constant-gradient) discrete-divergence operator yields a non-negligible
  divergence even for the ground-truth field. This is expected and is not a solver
  error: the training data is produced by a solver that enforces incompressibility in
  its own discrete norm (e.g., an inf-sup-stable finite-element pair or a finite-volume
  flux balance), which does not coincide with the node-collocated P1 divergence applied
  here, so extracting node velocities and applying a P1 divergence is nonzero by
  construction of the space mismatch. The mesh-normalised reference divergence
  (scaled by the median edge length) is ≈0.037; the dimensional RMS is ≈2.0–2.1 s⁻¹
  across frames, and a cylinder-diameter normalisation would give ≈0.2 — all far above
  any near-machine
  absolute tolerance — so an absolute divergence-free relation is not calibratable and
  stays deferred. As a reference-relative diagnostic, the surrogate's predicted
  next-state divergence stays within ≈0.2–2.5% of the reference field's across all nine
  evaluable frames of the trajectory (frames 0–8; all-cell ratio range 1.0025–1.0248,
  median 1.011; interior-only range 1.0042–1.0418, median 1.019), passing the
  conservative regression threshold of 1.5 on every frame. We emphasize that this
  "pass" is consistent with the surrogate simply being accurate on in-distribution
  frames — the ratio is bounded near 1.0 whenever the prediction is close to the
  reference — and therefore is not independent evidence of conservation beyond what
  rollout accuracy already captures. Its role is to calibrate the deferred absolute
  relation, and the threshold of 1.5 is a deliberately conservative, uncalibrated choice
  that should be tightened against the across-frame variability of the reference
  divergence before it carries weight.

Table 2 summarizes the three executed relations. All numbers are computed from
committed raw outputs and metric ledgers (Section 5.3) and were recomputed from those
committed outputs; the specific artifact for the ten-frame mirror-y figure is
`research_assets/runs/mirror-y-rate-upgrade/raw/metric_ledger.json`.

**Table 2. Executed relation-level verdicts on one MeshGraphNets cylinder-flow surrogate (one checkpoint, one eval trajectory).**

| Relation | Rubric outcome | Metric | Value | Verdict |
|---|---|---|---|---|
| Node-permutation equivariance | retained MR | relative L2 vs source (tol 1e-6) | 0.0 (1 case) | MR-level pass — sanity check, expected by construction |
| Mirror-y equivariance | retained OOD stress (exact relation out-of-relation-domain) | approximate-reflection relative L2 vs same-space mapping-error floor | median 0.737; per-frame 3.0–5.5× floor; 10/10 consecutive frames | probe-level fail (not independent observations) |
| Discrete divergence boundedness | deferred (absolute); reference-relative diagnostic | predicted/reference RMS divergence ratio (flag > 1.5) | all-cell 1.0025–1.0248 (median 1.011), interior-only 1.0042–1.0418; n=9 frames | diagnostic pass on all 9 (consistent with in-distribution accuracy); absolute relation deferred |

*Notes.* "MR-level" verdicts apply to relations retained as physics-preserving MRs; "probe-level" verdicts apply to an approximate stress probe that the rubric retained after classifying the exact relation as out-of-relation-domain (§3.5). For mirror-y, the same-space mapping-error floor against which the violation is compared is ≈13–25% of the field norm, and the 3.0–5.5× ratio is an upper bound on the model's own non-equivariance contribution (§5.1). The ten mirror-y frames are consecutive frames of one trajectory (not independent); the nine divergence frames likewise come from one trajectory.

These pilots illustrate the direction of the paper's argument — that an
evidence-gated rubric will refuse, downgrade, or defer a relation rather than
fabricate a verdict, and that the one substantive runtime finding (the mirror-y
probe-level failure) is surfaced only after the rubric has made the relation's
out-of-relation-domain status explicit. They are pilot-scale, restricted to one SUT,
one checkpoint, and one eval trajectory under approximate transformations, and do not
by themselves prove the general claim.

### 5.2 Still blocked

The following remain blocked and must not be written as results: cross-SUT or
geometry-independent pass/fail rates; comparative superiority over any baseline;
fault-detection rates; localization accuracy; runtime or performance claims; and
any claim that one SUT is more reliable than another. The three METBENCH-planned
SUTs and the baseline comparison stay blocked pending their artifacts.

### 5.3 Reproducibility package

Each executed relation ships as a self-contained, auditable bundle rather than as a
narrative number. For the realized SUT the package contains: the domain-validity
rubric and candidate ledger that record the four screening decisions; an MR card per
relation with its metric, tolerance, and exclusion rules; a flat run manifest that
records the SUT repository commit, the checkpoint sha256, the dataset slice, the
exact command, the random seed, and the device and framework versions; the runner
that executes the transformation and metric; the raw source, follow-up, and mapped
outputs (committed as arrays); a relation-level metric ledger with the per-frame
verdict, metric value, mapping-error floor, and rubric decision; and the run stdout
and exit code. A fail-closed validator refuses to admit a relation-level verdict
unless the manifest's checkpoint hash and every raw output it lists verify on disk,
and a continuous-integration job in the artifact repository re-runs the validators and
unit tests on every change. This is the concrete sense in which the workflow is
"auditable": each number in Tables 1 and 2 can be regenerated from the committed
artifacts and is checked by the same gate that produced it. One reproducibility
limitation is explicit: re-executing a runner (as opposed to re-checking the committed
outputs) additionally requires the system-under-test repository — the trained
MeshGraphNet implementation and its dataset loader — at the recorded commit, which is a
separate, read-only dependency referenced by the manifest rather than vendored in full.

## 6. Discussion

### 6.1 Expected Interpretation

The value of the study is not that every MR will find a new fault beyond rollout accuracy. Rather, it is that retained MRs provide relation-level evidence under explicit transformations, and that the rubric records why a candidate is retained, downgraded, deferred, or rejected. The single-SUT case study illustrates this concretely: the same surrogate yields a representation-level pass, a symmetry relation that the rubric refuses to treat as exact and whose downgraded probe is violated on every recorded frame, and a conservation relation the rubric defers because an absolute tolerance is not calibratable on the mesh. When a violation is observed, the MR card and verdict rule record which category applies and provide an auditable basis for further investigation; they do not, on their own, prove the attribution. In particular, when the rubric has already classified a relation as out-of-relation-domain before execution (as for mirror-y), the subsequent probe-level failure is expected and pre-explained, and separating a genuine model inconsistency from the relation-domain boundary depends on the quality of the rubric decision and the recorded analysis, not on the execution result alone.

### 6.2 Boundary of Claims

The paper must avoid four overclaims. It must not claim that MRs are always better than rollout accuracy. It must not claim that NOETHER proves the physical validity of cylinder-flow MRs. It must not claim that LLMs can automatically identify valid MRs. It must not generalize from three MeshGraphNets-family configurations to all SciML surrogates.

The safer claim is that a domain-validity-aware workflow can make MR identification and execution more auditable for a concrete class of SciML SUTs.

### 6.3 Implications for SciML Testing

If the empirical study succeeds, it will show how SciML testing can move from implicit expert checks to explicit MR assets. Such assets can complement residuals, uncertainty estimates, and accuracy metrics by making transformation assumptions and verdict rules inspectable. This is especially important for OOD validation, where the boundary of the relation is often as important as the violation itself.

## 7. Threats to Validity

**Construct validity.** MR validity depends on the rubric, physical assumptions, boundary-condition compatibility, and tolerance rules. Incorrect discrete operators or thresholds may create false violations or false passes.

**Internal validity.** SUT setup, checkpoint differences, random seeds, mesh preprocessing, and runtime nondeterminism may affect verdicts. The experiment ledger must record these details.

**External validity.** The study is limited to MeshGraphNets-family cylinder-flow implementations or configurations. It should not be generalized to all neural operators, PINNs, or fluid surrogates without further evidence.

**Baseline fairness.** Generic MR-generation and LLM baselines may not be designed for SciML. They should be interpreted as scope contrasts and candidate-generation comparators, not as defeated competitors.

**Conclusion validity.** Small sample sizes, multiple MRs, and many transformation bins can produce unstable conclusions. The analysis should emphasize confidence intervals, effect sizes, and predeclared verdict categories. Three specific limitations of the present single-SUT case study follow. *Single-trajectory autocorrelation:* the ten mirror-y frames and the two divergence frames are consecutive frames of one eval trajectory and are not independent observations; the trajectory, not the individual frame, is the unit of analysis, and we therefore report the mirror-y outcome qualitatively rather than as a calibrated rate. *Approximate-mapping confound:* the mirror-y mapping-error floor is computed from the same approximate nearest-neighbour reflection used by the probe; if that floor underestimates the approximation error, the "above floor" framing overstates how much of the violation is attributable to the model rather than the transformation. *Single checkpoint:* all executed verdicts come from one trained checkpoint; a different training run or checkpoint could yield different verdicts.

**Reproducibility.** Some SUTs may depend on old runtimes or non-redistributable checkpoints. The paper should disclose such barriers and provide the most complete runnable package possible.

## 8. Conclusion

This paper's conclusion is methodological and is supported, at pilot scale, by a single-SUT case study: domain-validity-gated MR identification provides an auditable oracle-free testing workflow for MeshGraphNets-family cylinder-flow surrogates. On one real trained surrogate the rubric produced all four screening outcomes and three executed relation-level verdicts with committed, independently recomputable artifacts. The central claim is that physically meaningful SciML MRs require explicit validity conditions, executable assets, and relation-level verdicts; the evidence here demonstrates the workflow rather than establishing cross-SUT rates, baseline comparisons, or reliability conclusions, which remain future work.

## References

Cited references are restricted to items whose bibliographic identity is confirmed
against a publisher, proceedings, arXiv, or Crossref-grade record. A small number of
closest-work leads remain at partial or unverified status and are intentionally not
cited in the running text (see the note after the list); resolving them is a remaining
pre-submission step.

[1] C. Mandrioli, S. Y. Shin, D. Bianculli, and L. Briand, "Testing CPS With Design
Assumptions-Based Metamorphic Relations and Genetic Programming," *IEEE Transactions on
Software Engineering*, vol. 51, no. 6, pp. 1666–1684, 2025, doi: 10.1109/TSE.2025.3563121.

[2] S. Segura, G. Fraser, A. B. Sanchez, and A. Ruiz-Cortés, "A Survey on Metamorphic
Testing," *IEEE Transactions on Software Engineering*, vol. 42, no. 9, pp. 805–824, 2016,
doi: 10.1109/TSE.2016.2532875.

[3] T. Y. Chen, F.-C. Kuo, H. Liu, P.-L. Poon, D. Towey, T. H. Tse, and Z. Q. Zhou,
"Metamorphic Testing: A Review of Challenges and Opportunities," *ACM Computing Surveys*,
vol. 51, no. 1, art. 4, 2018, doi: 10.1145/3143561.

[4] T. Y. Chen, S. C. Cheung, and S. M. Yiu, "Metamorphic Testing: A New Approach for
Generating Next Test Cases," Dept. of Computer Science, Hong Kong Univ. of Science and
Technology, Tech. Rep. HKUST-CS98-01, 1998.

[5] T. Pfaff, M. Fortunato, A. Sanchez-Gonzalez, and P. W. Battaglia, "Learning
Mesh-Based Simulation with Graph Networks," in *Proc. Int. Conf. on Learning
Representations (ICLR)*, 2021. arXiv:2010.03409.

[6] A. Sanchez-Gonzalez, J. Godwin, T. Pfaff, R. Ying, J. Leskovec, and P. W.
Battaglia, "Learning to Simulate Complex Physics with Graph Networks," in *Proc. Int.
Conf. on Machine Learning (ICML)*, 2020. arXiv:2002.09405.

[7] X. Xie, J. W. K. Ho, C. Murphy, G. Kaiser, B. Xu, and T. Y. Chen, "Testing and
validating machine learning classifiers by metamorphic testing," *Journal of Systems and
Software*, vol. 84, no. 4, pp. 544–558, 2011, doi: 10.1016/j.jss.2010.11.920.

[8] A. S. Krishnapriyan, A. Gholami, S. Zhe, R. M. Kirby, and M. W. Mahoney,
"Characterizing possible failure modes in physics-informed neural networks," in *Advances
in Neural Information Processing Systems (NeurIPS)*, 2021. arXiv:2109.01050.

[9] T. S. Cohen and M. Welling, "Group Equivariant Convolutional Networks," in *Proc.
Int. Conf. on Machine Learning (ICML)*, 2016. arXiv:1602.07576.

[10] D. J. Hiremath, M. Claus, W. Hasselbring, and W. Rath, "Towards Automated
Metamorphic Test Identification for Ocean System Models," 2021. arXiv:2103.09782 (also
IEEE/ACM MET 2021).

[11] K. Yu et al., "Research on Mutation Testing Strategies for Intelligent Models
Predicting Fluid Velocity Fields," in *Proc. 2025 7th Int. Academic Exchange Conf. on
Science and Technology Innovation (IAECST)*, pp. 178–182, 2025, doi:
10.1109/IAECST68792.2025.11415187. (DOI verified to resolve to the publisher record;
full text not inspected, so we cite it only as a closest-work lead, not for method
detail.)

[12] M. Schäfer, S. Turek, F. Durst, E. Krause, and R. Rannacher, "Benchmark
Computations of Laminar Flow Around a Cylinder," in *Flow Simulation with
High-Performance Computers II*, Notes on Numerical Fluid Mechanics, vol. 52, pp.
547–566, Vieweg, 1996, doi: 10.1007/978-3-322-89849-4_39.

*Leads pending verification (not cited).* A few items remain at partial or unverified
status in the project reference ledger and are therefore not cited: a physical-field
prediction MT lead for which no trusted record was found; a NOETHER-style framework for
metamorphic pattern discovery from operator algebras (arXiv-only, metadata inconsistent);
and residual-guided hybrid ML–solver trust-region frameworks. Resolving or removing these
remaining leads is a small final bibliographic step before submission.
