# JSS reviewer-facing external-corpus re-review

Date: 2026-07-04

Mode: academic-paper-reviewer re-review, focused on whether the external
defect-witness corpus is now presented as appropriately bounded
reviewer-facing evidence for a JSS regular paper.

Reviewed materials:

- `paper/95_jss_external_corpus_reviewer_facing_pack.md`
- `submissions/JSS/supplementary/evidence_appendices.tex`
- `submissions/JSS/cover_letter.md`
- `tests/test_external_defect_corpus_witnesses.py`
- `research_assets/runs/external-defect-corpus-scan/external_defect_corpus_summary.json`
- `research_assets/runs/external-defect-corpus-scan/screened_candidates_initial.md`
- `research_assets/experiments/claim-ledger.yml`, claim C57
- `research_assets/experiments/experiment-ledger.yml`, run
  `external-defect-corpus-summary-001`

Fresh verification before this review:

- `python -m pytest tests/test_external_defect_corpus_witnesses.py -q`:
  11 passed.
- `python tools/validate_research_assets.py`: exit 0.
- `python tools/validate_experiment_protocol.py`: exit 0.

## Editorial decision

Decision: **appropriately bounded; evidence presentation improved, not a new
acceptance guarantee.**

The new reviewer-facing package improves how a JSS reviewer can interpret the
external corpus. It now explains selection logic, deferred/no-go categories,
semantic-component breadth, and a four-level evidence ladder. The text also
states that the paper reaches Level 3, not Level 4. This is the correct
position: the corpus goes beyond a single external witness, but it is not
a representative defect corpus, production validation, trained-SUT correctness
evidence, or a defect-rate study.

## Reviewer panel synthesis

### EIC / journal-fit reviewer

Assessment: pass.

The supplement now gives an editor a compact answer to the likely scope
question: "Why is this not only a self-made cylinder-flow demonstration?" The
answer is evidence-backed and bounded: five external issue/PR/commit-linked
semantic witnesses across four repositories or subsystems. This supports JSS
software-testing relevance without reframing the paper as a bug-mining or
defect-prevalence study.

Residual risk: a reviewer who demands production-scale validation can still ask
for more evidence, but that request would exceed the paper's declared claim
boundary.

### Methodology reviewer

Assessment: pass.

The inclusion and exclusion criteria are now explicit. Deferred/no-go sources
are disclosed, which makes the selection boundary inspectable. The candidate pool is
described as a purposeful screen, not random sampling. This is methodologically
honest because the raw corpus does not contain a sampling frame, a denominator,
or a population model for SciML defects.

Residual risk: the phrase "quasi-representative reviewer-facing evidence" must
remain in internal/reviewer-facing explanation only. In formal result wording,
"curated external semantic witness corpus" is safer.

### Software-testing / JSS reviewer

Assessment: pass.

The evidence ladder is useful because it states what Level 3 permits:
external semantic-witness evidence across multiple repositories/subsystems. It
also tells the reader what it forbids: production validation, trained-SUT
correctness, defect rate, defect prevalence, and representative sampling. This
keeps the corpus from reading as an inflated defect benchmark.

Residual risk: the supplement adds more prose, so final PDF/log checks remain
necessary.

### SciML / numerical-validity reviewer

Assessment: pass.

The semantic-component coverage map is faithful to the artifacts: derivative
periodicity, spectral metric decidability, Hermitian frequency-domain symmetry,
axis-order gradients, and flux-boundary inference. These are SciML-relevant
software semantics. The map does not imply trained surrogate correctness, solver
accuracy, or production CFD readiness.

Residual risk: NeuralOperator PR #702 remains a PR-linked enforcement-semantics
witness, not a local reproduction of GPU line artifacts. The boundary remains
visible in the prior experiment review and the corpus summary.

### Devil's Advocate

Strongest objection:

The corpus is still curated and small. A skeptical reviewer can argue that
Level 3 evidence does not establish production-scale behavior or representative
real-defect effectiveness. That objection is valid as a limitation, but not a
contradiction, because the manuscript and supplement explicitly forbid Level 4
claims.

Severity: minor-to-moderate residual review risk, not a new Major issue by
itself.

## Traceability matrix

| Requirement | Verified location | Verdict |
|---|---|---|
| Screening process visible | `paper/95_*`, supplement "Reviewer-facing screening protocol" | Pass |
| Candidate-pool limits visible | `paper/95_*`, `screened_candidates_initial.md` | Pass |
| Semantic-component coverage visible | `paper/95_*`, supplement "Semantic-component coverage map" | Pass |
| Evidence ladder visible | `paper/95_*`, supplement "Evidence ladder and claim boundary" | Pass |
| Current level bounded | Both reviewer pack and supplement say "Current paper reaches Level 3, not Level 4" | Pass |
| Forbidden claims guarded | `tests/test_external_defect_corpus_witnesses.py` and C57 wording | Pass |
| No statistical representativeness claim | Cover letter and supplement say not statistically representative | Pass |
| No production/trained-SUT/defect-rate claim | C57, corpus summary, cover letter, supplement | Pass |

## Theme-drift check

Result: pass.

The new material remains inside the paper's software V\&V method scope. It
explains how external semantic witnesses support an MR-card/source-follow-up/
metric/typed-verdict workflow. It does not turn the paper into a bug-mining
benchmark, framework-quality survey, production CFD validation, or population
defect-rate study.

## Data and conclusion honesty check

Result: pass.

The added claims are traceable to existing artifacts. No new experiment result
is introduced. The strongest licensed conclusion is:

> The paper now has a curated, external issue/PR/commit-linked semantic witness
> corpus with transparent screening and explicit Level-3 claim boundaries.

The following conclusions remain forbidden:

- Representative sample of SciML defects.
- Production validation.
- Trained-SUT correctness.
- Defect rate, defect prevalence, or real-world defect-detection rate.
- Broad correctness claims about any included framework.

## Final re-review judgement

The reviewer-facing corpus package is suitable for submission packaging. It
answers a likely external-validity misunderstanding while preserving a truthful
evidence boundary. The next required gate is mechanical:
run the full regression suite, evidence validators, and JSS PDF/log build before
claiming submission readiness.
