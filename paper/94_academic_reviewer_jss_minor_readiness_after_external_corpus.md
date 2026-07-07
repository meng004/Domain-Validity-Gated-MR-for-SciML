# Academic reviewer re-review after external defect-witness corpus

Date: 2026-07-04

Mode: academic-paper-reviewer re-review style assessment.

Target: Journal of Systems and Software (JSS), regular paper.

Purpose: verify whether the one-week external defect-witness corpus and
subsequent prose compression move the manuscript closer to a Minor Revision
outcome, and whether any remaining issue still justifies another experiment.

Reviewed materials:

- `submissions/JSS/main.tex`
- `submissions/JSS/main.pdf`
- `submissions/JSS/supplementary/evidence_appendices.tex`
- `submissions/JSS/README.md`
- `submissions/JSS/cover_letter.md`
- `research_assets/experiments/claim-ledger.yml`
- `research_assets/experiments/experiment-ledger.yml`
- `research_assets/runs/external-defect-corpus-scan/external_defect_corpus_summary.json`
- `paper/92_external_defect_corpus_minor_revision_sprint.md`
- `paper/93_external_defect_corpus_experiment_review.md`
- `tests/test_external_defect_corpus_witnesses.py`

Verification evidence:

- External corpus summary: typed verdict `pass`, 5 units, 4 repositories or
  independent subsystems, verdict counts `{"pass": 5}`.
- Full regression: `468 passed, 334 subtests passed`.
- Evidence gates: `tools/validate_research_assets.py` and
  `tools/validate_experiment_protocol.py` exit 0.
- PDF/log check: `Output written on main.pdf (35 pages, 410238 bytes)`;
  no matched `Overfull`, undefined-reference, citation, rerun, or warning line
  in the final log scan.

## Decision

**Decision: Minor Revision / strong submit-ready.**

This is an improvement over the previous borderline Minor/Major assessment.
The previous strongest objection was that external validity was a bounded mosaic
with only one external issue-linked semantic witness. That objection is now
weaker: the manuscript has a five-unit external issue/PR/commit-linked semantic
witness corpus across DeepXDE, NeuralOperator, PhiFlow/PhiML, and JAX-CFD, and
the paper keeps the claim boundary explicit.

This is still not a guaranteed accept condition. The correct statement is:

> The manuscript is now in a credible JSS Minor Revision posture, with the
> remaining risks centered on readability and claim-boundary interpretation
> rather than missing external evidence.

## Revision response checklist

| Previous issue | Status | Verification | Quality assessment |
|---|---|---|---|
| External validity was bounded by one DeepXDE component witness plus synthetic/public-data witnesses. | Fully addressed for a method-paper submission; not converted into production validation. | C57 and `external_defect_corpus_summary.json` record 5 external semantic witnesses across 4 repos/subsystems. | Stronger and appropriately bounded. It answers "only self-made tasks?" better than another synthetic PDE would. |
| Page length sat at the JSS recommendation edge. | Fully addressed. | Final PDF is 35 pages, down from 36. | Editor friction from length is reduced. |
| Conceptual density could trigger Major Revision from non-SciML JSS reviewers. | Partially addressed. | Main prose was compressed; external corpus moved mainly to supplement. | Residual Minor-level clarity risk remains, but no longer justifies new experiments. |
| Risk of overclaiming real-defect or production evidence. | Fully addressed. | Main, supplement, claim ledger, experiment ledger, and tests forbid production validation, trained-SUT correctness, representative sampling, and defect-rate claims. | Claim discipline is strong and test-protected. |

## Reviewer panel synthesis

### EIC / journal-fit reviewer

Recommendation: **Minor Revision / submit-ready**.

The package is within the JSS regular-paper scope as a software V&V/testing
method for SciML surrogate software. The final 35-page PDF sits within the
single-column recommendation rather than at its edge. The additional external
corpus is useful because it gives the editor a simple response to the likely
screening concern that all evidence is self-authored or same-domain.

### Methodology reviewer

Recommendation: **Minor Revision**.

The evidence chain is now unusually auditable: MR cards, source artifacts,
runner scripts, typed JSON reports, claim ledger, experiment ledger, and tests
exist for the new corpus. The corpus is not representative sampling, but it does
not claim to be. For a method paper, five external issue/PR/commit-linked
semantic witnesses are enough to reduce the previous Major risk from external
validity.

### Software-testing / JSS domain reviewer

Recommendation: **Minor Revision**.

The software-engineering contribution is clearer after the corpus integration:
the artifact workflow is not only applied to author-designed physical examples
but also to public defect/fix records in scientific-software ecosystems. The
main remaining issue is readability: reviewers unfamiliar with SciML may need a
little help following the relation between numerical decidability, MR cards, and
typed verdicts. This is a prose clarification issue, not a new-experiment issue.

### SciML / numerical-validity reviewer

Recommendation: **Minor Revision**.

The operator-floor and admissibility claims remain carefully bounded. The
external corpus covers boundary conditions, spectral metrics, Hermitian
frequency constraints, axis-order gradients, and flux-boundary inference. These
are component/utility-level semantic witnesses, not trained surrogate
validation. The manuscript says that explicitly, which keeps the evidence
credible.

### Devil's Advocate

Strongest remaining objection:

The corpus improves external validity but remains semantic/component-level. A
skeptical reviewer can still say that the paper lacks production-scale trained
SciML defect detection. That objection is now a scope limitation rather than a
methodological blocker because the manuscript does not claim production-scale
defect detection.

Severity: **Minor-to-moderate review risk, not Major by itself.**

## Updated scores

Scores are ordinal review judgments, not acceptance probabilities.

| Dimension | Previous | Updated | Rationale |
|---|---:|---:|---|
| Originality | 80 | 81 | Core contribution unchanged; external corpus clarifies practical relevance. |
| Methodological rigor | 82 | 85 | Evidence discipline is stronger with five new audited external units. |
| Evidence sufficiency | 78 | 84 | Main improvement: external issue/PR/commit-linked corpus replaces single-witness limitation. |
| Argument coherence | 76 | 80 | Prose compression and one-row corpus integration reduce density. |
| Writing quality | 74 | 78 | Better length and tighter Results/Threats, but still conceptually dense. |
| Literature integration | 76 | 77 | Mostly unchanged. |
| Significance / impact | 78 | 81 | Stronger demonstration that the workflow applies beyond self-made tasks. |

Weighted judgement by the skill rubric: approximately **82/100**, mapping to
Minor Revision / strong submit-ready. This is not an "Accept without revision"
assessment because a JSS reviewer may still request clarity edits or sharper
scope wording.

## Does another experiment remain necessary?

No, not before submission.

Reason:

- The prior Major-risk evidence gap was not "more data of any kind"; it was
  "external issue/PR/commit-linked evidence." That gap has been materially
  reduced.
- Another one-week experiment would likely add marginal breadth while
  increasing manuscript/supplement complexity.
- The remaining risk is interpretability for a broad JSS audience, not lack of
  an additional SUT.

Only one future experiment would still be worth doing, but it should be saved
for reviewer response unless explicitly requested: a trained-SUT or
production-scale real-defect corpus with independent data and defect sources.
That is larger than the current scope and would risk changing the paper's
contribution.

## Topic drift and integrity check

Topic drift status: **No drift in the current manuscript.**

The external corpus remains tied to the paper's method because every unit is
reported as a validity-gated semantic witness with MR card, metric, typed
verdict, and claim boundary. The paper would drift if it described the corpus as
a general bug-mining study, framework quality survey, trained-SUT validation,
or defect-rate benchmark. Current tests and claim ledgers block those phrasings.

Data integrity status: **Pass.**

All corpus claims trace to run reports, raw external artifacts, MR cards,
claim-ledger wording, experiment-ledger records, and regression tests. No
unexecuted result is introduced in the manuscript.

## Final judgement

The manuscript is now best described as:

> **JSS regular-paper submission-ready; credible Minor Revision path; residual
> risk mainly from conceptual density and reviewer appetite for production-scale
> evidence, not from missing external semantic evidence.**

No further experiment is recommended before submission. The next highest-ROI
work is final reader-facing polish: preserve the 35-page PDF, keep the corpus
main-text footprint small, and ensure the cover letter frames the external
corpus as stronger semantic witness evidence rather than production validation.
