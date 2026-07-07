# JSS external-corpus reviewer-facing evidence pack

Date: 2026-07-04

Purpose: turn the five-unit external defect-witness corpus into
quasi-representative reviewer-facing evidence while preserving the actual
evidence boundary. This note does not add a new experiment. It organizes the
already executed corpus so that a JSS reviewer can inspect the selection logic,
semantic-component breadth, claim permissions, and forbidden claims.

Authoritative sources:

- Screening ledger:
  `research_assets/runs/external-defect-corpus-scan/screened_candidates_initial.md`
- Corpus summary:
  `research_assets/runs/external-defect-corpus-scan/external_defect_corpus_summary.json`
- Experiment review:
  `paper/93_external_defect_corpus_experiment_review.md`
- Claim ledger: `research_assets/experiments/claim-ledger.yml`, claim C57
- Experiment ledger: `research_assets/experiments/experiment-ledger.yml`,
  run `external-defect-corpus-summary-001`
- JSS supplement:
  `submissions/JSS/supplementary/evidence_appendices.tex`

## Boundary decision

The package may be described as quasi-representative reviewer-facing evidence:
it shows breadth across multiple external SciML semantic components and public
issue/PR/commit sources. It must also say that the corpus is curated, bounded,
and not statistically representative.

Current paper reaches the external-witness tier, not the stronger future
production-scale / representative-defect-corpus tier in the evidence ladder
below.

Allowed wording:

- External issue/PR/commit-linked witness corpus.
- Five external units across four repositories or independent subsystems.
- 5/5 typed pass verdicts for the counted external witnesses.
- Evidence that addresses the "only self-made task" objection.
- Curated external evidence with transparent screening.

Forbidden wording:

- Representative sampling of SciML defects.
- Production validation or production SciML/CFD validation.
- Trained-SUT correctness or trained-SUT reliability evidence.
- Framework-wide correctness for DeepXDE, NeuralOperator, PhiFlow/PhiML, or
  JAX-CFD.
- Real-world defect rate, defect prevalence, or defect-detection rate.

## Counted units

| Unit | Source basis | Semantic component | Metric/verdict source | Boundary |
|---|---|---|---|---|
| EDC-01 | DeepXDE issue #26 and PR #27 | periodic boundary-condition derivative semantics | value-only residual 0.0 vs `derivative_order=1` residual 2.0; typed pass | Component witness, not trained PINN accuracy. |
| EDC-02 | NeuralOperator issue #532 and PR #661 | spectral metric numerical-decidability semantics | L1 radial collision, L2 gap 0.5857864376269049, old power 0.0 vs corrected 2.0; typed pass | Utility witness, not trained FNO reliability. |
| EDC-03 | NeuralOperator PR #702 | Hermitian frequency-domain symmetry semantics | boundary imaginary max 0.5 to 0.0 after enforcement; typed pass | PR-linked enforcement semantics only; no local GPU artifact reproduction claim. |
| EDC-04 | PhiFlow issue #199 and PhiML commit `96ef3e4...` | coordinate/component axis-order gradient semantics | old native shape [2,3] vs corrected [3,2]; typed pass | Axis-order witness, not full PhiFlow simulation validation. |
| EDC-05 | JAX-CFD PR #167 | advection flux boundary-condition inference semantics | old Neumann flux vs corrected Dirichlet flux at no-penetration wall; typed pass | Boundary-inference witness, not solver correctness. |

These five units are counted because each has public external source evidence,
an MR/gate family, an executable witness report, a metric, a typed
verdict, and a claim boundary. The corpus summary records five typed pass
verdicts and four repository or subsystem roots: DeepXDE, NeuralOperator,
PhiFlow/PhiML, and JAX-CFD.

## Screening protocol

Inclusion criteria:

- Public external issue, PR, commit, or maintainer-linked source artifact.
- SciML or scientific-software relevance.
- A clear semantic relation that can be represented as an MR card or gate.
- A source/follow-up, before/after, or equivalent semantic contrast.
- A local CPU-feasible witness with a concrete metric and typed verdict.
- Full rubric-to-verdict traceability into the claim and experiment ledgers.

Exclusion criteria:

- Ordinary API/runtime failures without a clear metamorphic or semantic
  relation.
- Hardware/tolerance-only instability without a deterministic semantic
  contrast.
- User questions or support issues without fix evidence.
- Dependency-heavy cases that could not be replayed within the one-week JSS
  risk-reduction scope.
- Non-SciML download, preprocessing, or packaging issues that do not test the
  method's relation-level evidence chain.

Candidate-pool transparency:

- Go candidates: EDC-01 through EDC-05.
- Defer candidates: PyG issue #8131 / PR #8143 and NeuralOperator issue #599.
- No-go or low-priority sources: PhysicsNeMo boundary-search preprocessing or
  download issues, narrow NeuralOperator padding/grid-transform searches with
  no hits, generic JAX-CFD bug-search results weaker than PR #167, and DeepXDE
  PeriodicBC user questions without external defect/fix units.

This is a purposeful screen for high-value external witnesses, not random
sampling from a complete population of SciML software defects. The defer and
no-go categories are retained to make the selection boundary visible, but they do not
license a defect-prevalence estimate.

## Evidence ladder

| Tier | Evidence type | What it licenses | What it does not license |
|---|---|---|---|
| Author-designed tier | Author-designed or synthetic task evidence | Internal method execution and debugging of the workflow. | External validity claims. |
| Independent-task tier | Independent SUT/task full-chain evidence | Evidence that the rubric-to-verdict chain works beyond the first task. | Production validation or defect prevalence. |
| External-witness tier | External issue/PR/commit-linked witness corpus | External witness evidence across multiple repositories or subsystems; evidence against the concern that the method only works on self-made tasks. | Production validation, trained-SUT correctness, defect rate, defect prevalence, or representative sampling. |
| Stronger future tier | Production-scale or statistically representative real-defect corpus | If actually executed, population-level or deployment-facing claims under a defined sampling frame. | Not reached by the current paper. |

Current paper reaches the external-witness tier, not the stronger future tier.

## Phase reviews

Phase A review: pass.

- Evidence inventory is based on the corpus summary, screening ledger, C57,
  and the prior experiment review.
- No new result is introduced.
- The permitted claim is external witness evidence; the corpus remains
  curated and bounded.

Phase A theme-drift check: pass.

- The work remains within MR-card/source-follow-up/metric/typed-verdict
  evidence.
- It does not become a bug-mining study, framework-quality survey,
  defect-prevalence estimate, or production reliability claim.

Phase B review: pass.

- Inclusion and exclusion criteria are explicitly stated.
- Deferred and no-go categories are retained from the screening ledger.
- The screen is described as purposeful, not random sampling.

Phase B theme-drift check: pass.

- Screening is used to contextualize evidence strength.
- It is not presented as a systematic review or population-level defect survey.

Phase C review: pass.

- The five counted units map to distinct SciML semantic components:
  boundary-condition derivative semantics, spectral metric decidability,
  Hermitian frequency-domain symmetry, coordinate/component axis-order
  gradients, and flux-boundary inference.
- This breadth addresses the "only self-made task" objection, but it does not
  prove statistical representativeness.

Phase C theme-drift check: pass.

- The coverage map supports method externality.
- It does not rank frameworks or judge product quality.

Phase D review: pass.

- The evidence ladder distinguishes the external-witness tier from the stronger
  future production-scale / representative-defect-corpus tier.
- The current paper is explicitly marked as external-witness-tier evidence only.
- Forbidden claims include production validation, trained-SUT correctness,
  defect rate, defect prevalence, and representative sampling.

Phase D theme-drift check: pass.

- The ladder is a claim-boundary tool.
- It is not used to imply that the stronger future tier has been achieved.

## Final integrity note

The reviewer-facing pack supports clearer external-validity communication, not
broader empirical generalization than the executed corpus provides. The honest
submission-facing claim is:

> The paper includes a curated, external issue/PR/commit-linked witness
> corpus across five units and four repositories/subsystems. It addresses the
> concern that the method is only a self-made task demonstration, while remaining
> not statistically representative and not a production, trained-SUT, or
> defect-rate validation.
