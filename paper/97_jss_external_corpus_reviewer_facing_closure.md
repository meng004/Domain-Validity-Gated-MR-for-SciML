# JSS external-corpus reviewer-facing closure

Date: 2026-07-04

Purpose: close the reviewer-facing external-corpus packaging task and record
the final evidence, review, drift, and verification status.

## Completed phases

Phase A: pass.

- Evidence inventory and claim-boundary lock are recorded in
  `paper/95_jss_external_corpus_reviewer_facing_pack.md`.
- The evidence boundary is derived from
  `research_assets/runs/external-defect-corpus-scan/external_defect_corpus_summary.json`,
  `research_assets/runs/external-defect-corpus-scan/screened_candidates_initial.md`,
  claim C57, and `paper/93_external_defect_corpus_experiment_review.md`.

Phase B: pass.

- Screening protocol, inclusion criteria, exclusion criteria, defer/no-go
  categories, and purposeful-screen limitations are recorded in the reviewer
  pack and in the JSS supplement.

Phase C: pass.

- The semantic-component coverage map is recorded in the reviewer pack and in
  the JSS supplement.
- The five components remain: derivative periodicity, spectral metric
  decidability, Hermitian frequency-domain symmetry, coordinate/component
  axis-order gradients, and advection flux-boundary inference.

Phase D: pass.

- The evidence ladder is recorded in the reviewer pack and supplement.
- The current paper is bounded at Level 3, not Level 4.
- Regression tests protect the package from positive claims of representative
  sampling, production validation, trained-SUT correctness, or defect-rate
  evidence.

Phase E: pass.

- `submissions/JSS/supplementary/evidence_appendices.tex` now contains the
  screening protocol, semantic-component map, and evidence ladder.
- `submissions/JSS/cover_letter.md` frames the corpus as purposefully screened
  curated semantic evidence and explicitly says it is not statistically
  representative.
- `submissions/JSS/main.tex` was not expanded; the main-paper footprint remains
  unchanged for this task.

Phase F: pass.

- Academic-reviewer style re-review is recorded in
  `paper/96_jss_external_corpus_reviewer_facing_rereview.md`.
- Decision: appropriately bounded; evidence presentation improved, not a new
  acceptance guarantee.

Phase G: pass.

- Full regression: `471 passed in 1.89s`.
- `tools/validate_research_assets.py`: exit 0.
- `tools/validate_experiment_protocol.py`: exit 0.
- JSS PDF rebuilt with pdflatex/bibtex/pdflatex/pdflatex.
- Final log scan matched only `Output written on main.pdf (35 pages, 410238 bytes)`
  among the searched Overfull/undefined/citation/rerun/warning patterns.

## Theme-drift decision

No drift.

The new work remains about domain-validity-gated metamorphic testing evidence:
MR cards, external source/follow-up or before/after semantic witnesses,
metrics, typed verdicts, and claim boundaries. It does not reframe the paper as
a bug-mining benchmark, framework-quality survey, production CFD validation,
trained-SUT correctness study, or population defect-rate study.

## Data and conclusion honesty decision

Pass.

No unexecuted experiment result was added. The strongest licensed claim remains:

> The paper contains a curated external issue/PR/commit-linked semantic witness
> corpus with five units across four repositories or independent subsystems,
> transparent screening, and explicit Level-3 claim boundaries.

The following claims remain forbidden:

- statistically representative real-defect corpus,
- production validation,
- trained-SUT correctness or reliability,
- framework-wide correctness,
- defect rate, defect prevalence, or real-world defect-detection rate.

## Residual risk

Residual review risk is now mainly interpretation risk, not missing packaging
evidence. A reviewer may still request Level-4 production-scale or statistically
representative evidence. The honest response is that the current manuscript
does not claim Level 4; it provides Level-3 external semantic-witness evidence
for a JSS software V\&V method paper.
