# Academic reviewer final assessment for JSS regular-paper stability

Date: 2026-07-04

Mode: academic-paper-reviewer final re-review.

Target: Journal of Systems and Software (JSS), regular paper.

Question: Does the manuscript meet the conditions needed for a stable JSS
regular-paper acceptance posture?

## Materials reviewed

- `submissions/JSS/main.tex`
- `submissions/JSS/main.pdf`
- `submissions/JSS/supplementary/evidence_appendices.tex`
- `submissions/JSS/cover_letter.md`
- `paper/94_academic_reviewer_jss_minor_readiness_after_external_corpus.md`
- `paper/96_jss_external_corpus_reviewer_facing_rereview.md`
- `paper/97_jss_external_corpus_reviewer_facing_closure.md`
- `paper/98_jss_external_corpus_humanizer_final_pass.md`
- `research_assets/runs/external-defect-corpus-scan/external_defect_corpus_summary.json`
- `research_assets/experiments/claim-ledger.yml`, claim C57
- `research_assets/experiments/experiment-ledger.yml`,
  run `external-defect-corpus-summary-001`
- `tests/test_external_defect_corpus_witnesses.py`

External venue check:

- ScienceDirect JSS page, checked 2026-07-04, states that JSS publishes across
  software engineering and that articles should provide evidence for their
  claims through empirical studies, simulation, formal proofs, or other
  validation. The scope includes verification, validation, testing, and
  software engineering for AI systems.

Fresh verification:

- `python -m pytest tests -q`: 471 passed.
- `python tools/validate_research_assets.py`: exit 0.
- `python tools/validate_experiment_protocol.py`: exit 0.
- JSS build log already records `Output written on main.pdf (35 pages, 410238 bytes)`.
- Latest log scan matches only the PDF output line among the searched
  Overfull/undefined/citation/rerun/warning patterns.

## Decision

**Decision: JSS regular-paper submission-ready; credible Minor Revision path;
not an unconditional stable-acceptance guarantee.**

The manuscript now meets the core conditions for a stable JSS regular-paper
submission posture:

- It is in JSS scope as a software V\&V/testing method for SciML surrogate and
  scientific-software evidence workflows.
- Its central claims are evidence-backed and ledger-bounded.
- The external-validity concern has been materially addressed by a five-unit
  external issue/PR/commit-linked semantic witness corpus across four
  repositories or independent subsystems.
- It no longer depends only on author-designed cylinder-flow evidence.
- The supplement and cover letter now make the corpus selection logic, semantic
  coverage, evidence ladder, and forbidden claims inspectable.
- Reproducibility and claim discipline are test-protected by ledgers, validators,
  and regression tests.
- The package is 35 pages in the current JSS PDF build, with no matched
  Overfull, undefined-reference, citation, rerun, or warning pattern in the
  final log scan.

However, "stable acceptance" cannot be stated as a fact. It remains a review
outcome, not a property that can be proven locally. The defensible judgement is
that the paper has moved from a borderline Minor/Major posture to a strong
submit-ready / likely Minor Revision posture.

## Acceptance-condition matrix

| Condition for JSS regular-paper stability | Status | Evidence | Residual risk |
|---|---|---|---|
| JSS scope fit | Pass | JSS scope includes software engineering, V\&V/testing, and SE for AI systems; manuscript frames the contribution as a software V\&V method. | Low. |
| Evidence-backed claims | Pass | Claim ledger, experiment ledger, validators, and tests constrain all main empirical claims. | Low if wording remains bounded. |
| Primary empirical execution | Pass | Multiple full rubric-to-verdict workflows, including cylinder, PINN/FNO, periodic-advection, and related SUT/task executions. | Low-to-moderate because evidence is method-paper evidence, not population reliability. |
| External validity beyond self-made tasks | Pass for current claims | Five external issue/PR/commit-linked semantic witnesses, four repositories/subsystems, 5/5 typed pass, Level 3 evidence. | Moderate only if reviewers demand Level 4 representative or production-scale evidence. |
| Representative real-defect corpus | Not claimed / not required for current claims | Reviewer-facing pack and supplement state current paper reaches Level 3, not Level 4. | Managed by explicit boundary. |
| Production validation | Not claimed / not required for current claims | Cover letter, supplement, C57, and tests forbid production-validation wording. | Managed by explicit boundary. |
| Trained-SUT correctness | Not claimed / not required for external corpus | External corpus is component/utility semantic witness evidence. | Managed by explicit boundary. |
| Defect rate or prevalence | Not claimed / not required | Screening is purposeful, not random sampling; no denominator or sampling frame is claimed. | Managed by explicit boundary. |
| Reproducibility and traceability | Pass | MR cards, raw artifacts, reports, claim ledger, experiment ledger, validators, and regression tests. | Low. |
| Readability for broad JSS reviewers | Partial pass | Main text compressed; detailed corpus content moved to supplement; humanizer pass applied. | Main residual risk. |
| Page / format friction | Pass | Current JSS PDF is 35 pages. | Low, assuming no further main-text growth. |

## Reviewer-panel synthesis

### EIC / journal-fit reviewer

Recommendation: **Minor Revision / submit-ready.**

The paper is within JSS scope and has enough evidence to justify review as a
regular paper. The added external corpus and reviewer-facing evidence ladder
give the editor a clear answer to the self-made-task concern. The manuscript is
not positioned as an industry deployment report, a production CFD validation,
or a defect-rate benchmark, so absence of Level-4 evidence is not a fatal scope
gap.

### Methodology reviewer

Recommendation: **Minor Revision.**

The claim-evidence discipline is strong. C57 and
`external_defect_corpus_summary.json` bound the external corpus to five public
semantic witnesses across four repositories/subsystems. The validators and
tests pass. The screening protocol states inclusion/exclusion criteria and
discloses defer/no-go categories. Methodologically, this is sufficient for the
paper's Level-3 claim, but not for representative defect-sampling claims.

### Software-testing / JSS reviewer

Recommendation: **Minor Revision.**

The paper's contribution is a reusable V\&V workflow: MR cards, admissibility
rubric, typed verdicts, metrics, and ledgers. That is a JSS-appropriate
software-engineering contribution. The main risk is that the conceptual stack
is dense for readers who are not familiar with SciML, metamorphic testing, and
operator floors. This risk is now a clarity issue, not a missing-evidence issue.

### SciML / numerical-validity reviewer

Recommendation: **Minor Revision.**

The manuscript preserves the numerical-validity boundary. The external corpus
covers boundary conditions, spectral metrics, Hermitian frequency constraints,
axis-order gradients, and flux-boundary inference. The paper does not claim
trained-model reliability or broad solver correctness from those witnesses.
This makes the evidence credible.

### Devil's Advocate

Strongest remaining objection:

A skeptical reviewer can still ask for production-scale trained-SUT validation
or a statistically representative real-defect corpus. That objection is real,
but it targets a stronger Level-4 claim that the manuscript does not make. It
therefore remains a residual preference risk rather than a methodological
blocker.

Severity: **minor-to-moderate residual risk, not a current Major blocker.**

## Stable-acceptance judgement

The manuscript does **not** reach an "accept without revision is likely" state.
That would require unusually low conceptual friction and a reviewer panel that
fully accepts the Level-3 evidence boundary without asking for further
clarification.

The manuscript **does** reach a defensible "stable JSS regular-paper
submission" state:

- no known P0 evidence gap remains;
- no new experiment is recommended before submission;
- likely reviewer requests are expected to be wording, explanation, or boundary
  clarifications rather than a demand to rebuild the empirical core;
- if a reviewer demands Level-4 production/representative evidence, the correct
  response is a scope-boundary argument rather than a pre-submission experiment.

## Final judgement

Best current description:

> **JSS regular-paper submission-ready; credible Minor Revision path; residual
> risk mainly from conceptual density and possible reviewer appetite for
> Level-4 production or representative real-defect evidence.**

This is the strongest honest conclusion supported by the current evidence. It
is not a guarantee of stable acceptance.
