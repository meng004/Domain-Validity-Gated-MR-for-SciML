# Research Position, Necessity, Current State, and Argument Plan

> Date: 2026-06-05  
> Modes used: deep-research synthesis + research-evidence-gate + academic-paper plan  
> Scope: positioning and argument design only. This file does not modify `main.tex`, does not add results, and does not upgrade unverified references.

## 1. Bottom-Line Decision

The paper should be locked as an **Information and Software Technology (IST) software-testing / V&V method paper with a SciML case study**.

It should not be framed as:

- a CFD paper;
- a new MeshGraphNets or GNN architecture paper;
- a general SciML reliability paper;
- a paper proving that MRs are better than rollout accuracy;
- a paper claiming first physics-based MT for learned physical-field or fluid-velocity predictors;
- a completed empirical-results paper before SUT logs, MR executions, and verdict ledgers exist.

The safest fixed title-level positioning is:

> Domain-validity-gated MR identification and executable test assets for scientific machine learning.

The fixed research object is:

> Candidate MRs for SciML systems, with MeshGraphNets-family cylinder-flow surrogates treated as the concrete case-study SUTs.

The fixed research problem is:

> How can physically plausible candidate relations be screened for domain validity and converted into executable, auditable metamorphic-relation assets for oracle-free testing of SciML surrogates?

## 1.1 Route-Map Role

This paper should be positioned after three upstream works:

1. the published scientific-computing MR hierarchical classification/topology model;
2. the submitted NOETHER meta-pattern and semantic-variant work;
3. the ongoing hierarchy-relative minimal-complete MR selection theory.

Its role is not to repeat those contributions. Its role is the **execution and evidence layer**:

> candidate MR -> domain-validity rubric -> MR card -> executable asset -> relation-level verdict ledger.

The MeshGraphNets cylinder-flow material is therefore a case study for the asset workflow, not the paper's main conceptual novelty.

## 2. Evidence Basis

### 2.1 External evidence

The external evidence supports the broad need but narrows the novelty claim.

| Evidence | What it supports | What it does not support |
|---|---|---|
| MeshGraphNets paper: mesh-based neural simulators target expensive scientific simulations and promise substantial speedups. | Learned mesh simulators are a real SciML surrogate class worth testing. | It does not validate this paper's MRs or SUTs. |
| Test-oracle and MT literature. | Oracle-free testing is a recognized software-testing problem and MT is a standard relation-based response. | It does not show that any particular SciML MR is physically valid. |
| Hiremath et al. ocean-model MR identification. | MR identification for scientific/simulation software is an established problem, and automated candidate discovery has precedent. | It is not a neural PDE surrogate or cylinder-flow study. |
| Mandrioli et al. CPS design-assumption MRs. | Domain assumptions can be turned into MRs, and MR falsification can add information beyond ordinary tracking/error evidence. | It is CPS/control testing, not SciML fluid-surrogate testing. |
| NOETHER arXiv preprint. | A current framework exists for organizing metamorphic pattern discovery. | It is preprint-level and cannot certify physical validity of this paper's cylinder-flow MRs. |
| Gopakumar et al. calibrated physics-informed UQ. | Physics residuals and UQ are important SciML reliability tools. | They are not source/follow-up MR tests unless paired with explicit transformations and verdict rules. |
| Yu/Qi leads. | There are at least candidate/partial signs of physics-based MT for learned physical-field or fluid-velocity predictors. | They block any first/only novelty claim; Qi is currently unverified and Yu is partial. |

### 2.2 Local evidence

The local evidence supports method readiness, not empirical results.

| Local artifact | Current status | Claim allowed |
|---|---|---|
| `paper/ist-submission/main.tex` | IST draft exists with method, worked examples, and blocked Results. | The paper has a coherent draft and cautious claim discipline. |
| `research_assets/mr_cards/node_permutation_equivariance.json` | One design-time MR card exists. | A minimal MR asset format has been instantiated for node permutation. |
| `research_assets/ledgers/candidate_ledger.json` | One design-time candidate decision exists. | Node permutation has been retained as a design-time representation MR, not as an empirical pass/fail result. |
| `research_assets/ledgers/verdict_ledger.schema.json` and `.example.json` | Strict schema and no-run example exist. | Verdict classes and ledger shape are ready for future runs. |
| `tests/test_research_assets.py` and `tools/validate_research_assets.py` | 7 tests pass; validator exits 0. | Asset structure and local evidence references are auditable. |
| `paper/reference_ledger.md` | Literature ledger exists; most closest entries are PARTIAL or UNVERIFIED. | The related-work contrast must remain cautious. |

## 3. Is the Gap Real?

Yes, but it is narrower than the early draft sometimes implied.

The gap is **not**:

> Nobody has used physics-based MRs for learned fluid or physical-field predictors.

That claim is unsafe. The current ledger marks `yu2025fluidvelocity` as `PARTIAL` and `qi2025physicalfield` as `UNVERIFIED`, but both are close enough to block first/only language.

The gap is:

> Existing work shows that physical knowledge can inspire MRs or reliability diagnostics, but this paper targets the validity and execution layer: how to decide whether a candidate relation is valid for a concrete SciML SUT, record its preconditions and exclusions, convert it into an executable MR asset, and report relation-level verdicts without confusing SUT inconsistency, out-of-relation-domain cases, and numerical-tolerance effects.

This gap is worth filling because it is a software-testing problem:

1. SciML surrogates create oracle uncertainty for transformed or OOD cases.
2. Accuracy-only evaluation remains useful but does not answer relation-level validity questions.
3. Physical residuals and UQ are useful diagnostics but do not by themselves define source/follow-up MR tests.
4. Expert reasoning about physical validity is often implicit; making it explicit through MR cards and ledgers improves reproducibility and reviewability.
5. For IST, the value is not a new flow solver. The value is a test method and auditable research asset structure.

## 4. Fixed Research Questions

The current RQ structure should be fixed as follows.

### RQ0

How can physically valid metamorphic relations be identified, operationalized, and used as oracle-free tests for MeshGraphNets-family cylinder-flow surrogates without relying on exact per-sample expected outputs?

### RQ1: Validity

How can a domain-validity rubric distinguish physically meaningful candidate MRs from transformations that are executable but invalid, underspecified, or outside the relation's domain?

### RQ2: Operationalization

How can a candidate-organization workflow be combined with the rubric to produce executable MR assets with source cases, follow-up transformations, output mappings, metrics, tolerances, exclusions, and verdict rules?

### RQ3: Verdict and interpretation

How can relation-level verdicts distinguish pass, fail, skip, out-of-relation-domain, numerical-tolerance issue, and inconclusive outcomes?

### RQ4: Empirical feasibility and comparison

Across MeshGraphNets-family cylinder-flow implementations or configurations, what evidence does the rubric-gated workflow add relative to expert MR design, LLM-assisted candidate generation, generic MR-generation scope contrasts, and rollout-accuracy diagnostics?

Important correction:

> Do not fix RQ3 as "validated failure localization" unless seeded faults or mutants exist. At the current evidence level, localization should be phrased as an interpretation protocol or future validation target.

## 5. Fixed Contribution Order

### C1: Domain-validity rubric

Claim strength: qualified but central.

Allowed wording:

> We propose a domain-validity rubric for screening candidate MRs in SciML testing.

Evidence needed before submission:

- retained, rejected, deferred, and OOD-stress examples;
- at least three complete MR cards;
- reviewer-readable criteria for physical basis, transformation preconditions, boundary compatibility, metric, tolerance, exclusion, and interpretation.

### C2: Executable MR asset workflow

Claim strength: partially supported locally.

Allowed wording:

> We define an executable MR asset format and instantiate it for design-time MR construction.

Current local support:

- one node-permutation MR card;
- one candidate ledger;
- one verdict-ledger schema;
- passing validator.

Evidence needed before Results:

- transformation code;
- runner config;
- metric computation;
- recorded source/follow-up cases;
- SUT logs.

### C3: Relation-level verdict scheme

Claim strength: partially supported as schema, not as empirical verdict evidence.

Allowed wording:

> We define relation-level verdict classes that separate pass, fail, skip, out-of-domain, numerical-tolerance, and inconclusive outcomes.

Do not write:

> We localize failures.

Safe alternative:

> We provide an interpretation protocol whose localization value can be evaluated once seeded faults or known failure layers are available.

### C4: Empirical evaluation

Claim strength: planned only.

Allowed wording:

> We design an empirical evaluation over MeshGraphNets-family cylinder-flow systems.

Blocked wording:

- "The method detects more faults";
- "The method outperforms accuracy-only evaluation";
- "The method identifies unreliable SUTs";
- "MR violations show the true operating boundary";
- any pass/fail, violation-rate, or comparative-performance claim.

## 6. Argument Scheme for the Paper

The paper should use a **five-link argument chain**.

### Link 1: Why this matters

Claim:

> Learned mesh simulators are attractive because they can reduce simulation cost, but their validation remains difficult under transformed or OOD cases.

Evidence:

- MeshGraphNets source for mesh-based learned simulation and computational motivation.
- Oracle-problem source for exact expected-output difficulty.

Manuscript role:

- Introduction paragraphs 1-2.

### Link 2: Why existing evaluation is insufficient

Claim:

> Rollout error, residuals, UQ, and equivariance diagnostics are useful, but they answer different questions from MR-based source/follow-up relation testing.

Evidence:

- SciML UQ source shows residual-based uncertainty is active and important.
- The paper's method distinguishes diagnostics from executable MRs.

Manuscript role:

- Introduction paragraph 2.
- Related work: SciML V&V, residuals, UQ.

### Link 3: Why MT is relevant but not plug-and-play

Claim:

> MT addresses oracle problems through relations among executions, but SciML relations require domain-validity screening.

Evidence:

- MT survey / scientific software MT.
- Local worked examples: node permutation, mirror-y, divergence.

Manuscript role:

- Introduction paragraphs 3-4.
- Method section: rubric.

### Link 4: What gap this paper fills

Claim:

> The gap is validity-gated operationalization: candidate relation -> validity decision -> executable MR card -> relation-level verdict.

Evidence:

- Mandrioli supports assumption-based MR design in CPS.
- Hiremath supports MR identification challenge for scientific simulation.
- Yu/Qi leads block first-claim but motivate careful differentiation.
- Local MR asset package shows the proposed asset format is concrete.

Manuscript role:

- End of Introduction.
- Related Work contrast paragraphs.

### Link 5: How the paper will prove value

Claim:

> The paper's value will be shown through artifact completeness, executable MR rate, verdict distributions, and comparison with expert/generic/LLM/accuracy baselines.

Evidence:

- Currently planned only.
- Needs experiment ledgers.

Manuscript role:

- Empirical Design.
- Results remains blocked until artifacts exist.

## 7. Safe Thesis Paragraph

This paragraph is safe for the Introduction after references are cleaned:

> This paper treats MR identification for SciML as a validity-gated testing problem. Physical knowledge can suggest candidate relations, but a candidate relation is not yet an executable MR. It must first state the physical or software basis of the relation, the transformation preconditions, boundary-condition compatibility, output mapping, metric, tolerance rationale, exclusion rule, and verdict interpretation. We therefore shift the contribution from generating plausible MR candidates to making MR validity and execution auditable for a concrete class of mesh-based neural cylinder-flow surrogates.

## 8. Safe Related-Work Contrast

Current safe contrast:

> Existing work on scientific-software MT, simulation testing, CPS design-assumption MRs, and physics-informed UQ shows that relation-based and residual-based evidence is useful when direct oracles are limited. Recent candidate leads also suggest that physics-based MRs are being explored for learned physical-field or fluid-velocity predictors. The remaining problem addressed here is not the mere inspiration of MRs from physics; it is the explicit screening, executable encoding, and relation-level reporting of MRs for SciML SUTs under stated validity conditions.

Do not name Qi as verified closest prior work until a trusted record exists. Do not use Yu as a strong closest-paper anchor until publisher/Crossref/IEEE evidence and paper text are inspected.

## 9. Claim Ledger for Writing

| Claim | Status | Allowed use |
|---|---|---|
| MeshGraphNets are a relevant learned mesh-simulation family. | supported | Introduction and SUT scope. |
| SciML transformed/OOD cases create oracle difficulty. | qualified | Motivation; do not imply no solver can ever be run. |
| MT is suitable for oracle-free relation checking. | supported | Background. |
| Candidate SciML MRs require validity screening. | supported by reasoning + examples | Core gap and method. |
| NOETHER can organize candidate relation sources. | qualified | Mention as preprint-level organizing aid, not proof. |
| This paper is first physics-based MT for learned fluid predictors. | blocked | Do not write. |
| The method detects faults better than accuracy-only evaluation. | blocked | Requires experiment/fault evidence. |
| Node permutation MR asset exists. | supported locally | Method artifact status. |
| The paper currently has empirical findings. | blocked | Results remain blocked. |
| Relation-level verdicts can support boundary characterization. | speculative/qualified | Use as planned evaluation aim until run data exists. |

## 10. Current State

Current stage:

> Stage 2 writing with strengthened method artifacts; not ready for Stage 2.5 integrity, peer review, or submission.

What is stronger now:

- The research position is clear and IST-compatible.
- Results are blocked honestly.
- A minimal node-permutation MR asset exists.
- A validator and tests create a local evidence gate.
- A reference ledger prevents unsafe novelty claims.

What remains weak:

- Closest-work verification is incomplete.
- `references.bib` contains metadata that the ledger says must be corrected.
- Only one design-time MR card exists.
- No SUT has been run.
- No verdict ledger contains run entries.
- No baseline comparison evidence exists.
- Localization is not validated.

## 11. Recommended Next Writing and Research Actions

### Immediate action 1: Fix reference integrity

Before changing related work or contribution language in `main.tex`, update the bibliography and ledger:

- remove or clearly quarantine `qi2025physicalfield` unless a trusted source is found;
- verify `yu2025fluidvelocity` via IEEE/Crossref or downgrade it;
- correct NOETHER authors/title from arXiv;
- correct Mandrioli authors/pages;
- correct Baral/Wang metadata or remove from submission bibliography.

### Immediate action 2: Expand MR cards

Add two more design-time MR cards:

- mirror-y equivariance;
- discrete divergence boundedness.

These should pass the same validator or an extended validator.

### Immediate action 3: Create first executable runner path

For node permutation only:

- define sample input fixture;
- implement transformation code;
- implement metric code;
- produce one dry-run or blocked-run ledger entry.

### Immediate action 4: Revise configuration alignment

Update `paper/02_paper_configuration.md` so C3/RQ3 no longer promises validated failure localization. Use "relation-level verdict and interpretation protocol" unless seeded-fault evidence is added.

## 12. Decision

The study is necessary and worth pursuing, but its value rests on **validity-gated executable MR assets**, not on broad novelty claims.

The paper should now proceed under this fixed stance:

> A software-testing method paper for IST that makes candidate MR identification in SciML auditable through domain-validity rubrics, executable MR cards, and relation-level verdict ledgers, demonstrated through a MeshGraphNets-family cylinder-flow case study.

Results, reliability conclusions, fault detection, boundary maps, and baseline superiority remain blocked until direct execution evidence exists.

## 13. Sources Checked

- MeshGraphNets arXiv page: https://arxiv.org/abs/2010.03409
- NOETHER arXiv page: https://arxiv.org/abs/2605.17390
- Hiremath et al. ocean-model MR identification arXiv page: https://arxiv.org/abs/2103.09782
- Mandrioli et al. CPS MR paper record: https://orbilu.uni.lu/handle/10993/64828
- Gopakumar et al. calibrated physics-informed UQ PMLR page: https://proceedings.mlr.press/v267/gopakumar25a.html
- IST ScienceDirect journal page: https://www.sciencedirect.com/journal/information-and-software-technology
- Local evidence: `paper/reference_ledger.md`, `paper/15_minimal_asset_package_progress.md`, `research_assets/`, `tests/test_research_assets.py`, `tools/validate_research_assets.py`.
