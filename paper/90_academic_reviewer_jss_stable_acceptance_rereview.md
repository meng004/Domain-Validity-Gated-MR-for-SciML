# Academic reviewer re-review for JSS regular-paper stable acceptance

Date: 2026-07-03

Mode: academic-paper-reviewer full/re-review style assessment.

Target: Journal of Systems and Software (JSS), regular paper.

Reviewed materials:

- `submissions/JSS/main.tex`
- `submissions/JSS/main.pdf`
- `submissions/JSS/README.md`
- `submissions/JSS/highlights.txt`
- `submissions/JSS/declarations.md`
- `submissions/JSS/author_biographies.md`
- `submissions/JSS/open_science_checklist.md`
- `submissions/JSS/supplementary/evidence_appendices.tex`
- `research_assets/experiments/claim-ledger.yml`
- `research_assets/experiments/experiment-ledger.yml`
- `paper/89_deepxde_periodicbc_real_defect_witness_completion.md`

JSS source checked:

- ScienceDirect Guide for Authors, Journal of Systems and Software, accessed
  2026-07-03.

Verification evidence:

- JSS scope: software engineering, verification/validation/testing, AI for
  software engineering, and evidence-supported claims are within scope.
- Peer review: single anonymized.
- Abstract limit: <=250 words; current abstract is 210 words by local count.
- Highlights: five highlights; character counts 62, 70, 67, 67, and 58.
- Vitae: separate editable author biographies exist; each biography is below
  100 words.
- Length: JSS encourages fewer than 36 pages single-column or 18 pages
  double-column; current build is exactly 36 pages.
- PDF build/log scan: `Output written on main.pdf (36 pages, 413925 bytes)`;
  no Overfull, undefined-reference, citation, or warning line matched the final
  scan.
- Full regression: `460 passed, 334 subtests passed`.
- Evidence gates: `tools/validate_research_assets.py` and
  `tools/validate_experiment_protocol.py` exit 0.

## Editorial decision

**Decision: borderline Minor Revision / strong submit-ready, but not a
guaranteed stable-accept condition.**

The previous P0 administrative blockers have been repaired. The package now has
complete author biographies, a 36-page compiled JSS manuscript, compliant
highlights, a 210-word abstract, declarations, data availability, and passing
evidence gates. The empirical case is also stronger than in the previous
review: the independent periodic-advection workflow remains a full
rubric-to-verdict synthetic primary workflow, and the new DeepXDE PeriodicBC
issue-linked witness adds one external real-defect-linked semantic chain.

However, "stable acceptance" is stronger than "reasonable to submit." On that
stricter standard, the paper still has residual review risk from conceptual
density, upper-edge length, and bounded external validity. The correct claim is:

> The manuscript now meets the main conditions for a credible JSS regular-paper
> submission and has a plausible Minor Revision path, but acceptance is not
> stable enough to call low-risk or guaranteed.

## Reviewer panel synthesis

### EIC / journal-fit reviewer

Recommendation: **Minor Revision / submit-ready**.

The paper is in JSS scope as a software V&V/testing paper for SciML surrogate
software. The manuscript follows the JSS package requirements that matter for
initial review: title page, abstract, keywords, highlights, CRediT, competing
interest declaration, generative-AI declaration, data availability, and separate
Vitae. The 36-page length is not above the stated recommendation, but it sits
at the upper edge and may still create editor friction.

### Methodology reviewer

Recommendation: **Minor-to-Major Revision**.

The evidence discipline is unusually strong: MR cards, ledgers, raw run
artifacts, source/follow-up outputs, validators, full tests, and supplementary
claim maps exist. The new DeepXDE witness is valuable because it links one
external issue/PR to a typed semantic verdict rather than relying only on
author-designed synthetic faults. Still, the evidence is deliberately bounded:
no production CFD defect corpus, no broad neural-operator reliability claim, and
no population-level real-defect rate. This is acceptable for a method paper if
the claim boundary stays visible.

### Software-testing / JSS domain reviewer

Recommendation: **Minor Revision**.

The software-engineering contribution is now clearer: numerical decidability is
used as an admissibility condition for metamorphic testing, and the artifact
workflow prevents invalid transformations from being reported as SUT faults.
The DeepXDE issue-linked witness improves JSS-facing credibility by showing the
same source/follow-up residual style can connect to an external software
defect/fix. The remaining weakness is readability for non-SciML JSS reviewers.

### SciML / numerical-validity reviewer

Recommendation: **Minor-to-Major Revision**.

The operator-floor argument is credible within its stated scope. The paper
correctly limits P1 divergence conclusions to shape-regular triangular meshes
and refuses arbitrary-mesh or reliability claims. The airfoil, PINN/FNO,
periodic-advection, RealPDEBench preflight, and DeepXDE witness now give a
reasonable breadth story. The RealPDEBench evidence is still inconclusive and
should remain supplementary; the DeepXDE witness is real-defect-linked but
component-level, not trained-SUT-level.

### Devil's Advocate

Strongest remaining objection:

The paper is rigorous but dense. A skeptical reviewer may argue that the
external-validity story is a mosaic of bounded witnesses rather than a clean
production-scale evaluation: periodic-advection is synthetic, RealPDEBench is
inconclusive, and DeepXDE is a boundary-condition component witness rather than
a trained SciML surrogate experiment. This objection does not invalidate the
methodological contribution, but it can still trigger Major Revision if the
reviewer expects a production or real-defect corpus.

Severity: **major review risk, not fatal flaw**.

## Scores

Scores are ordinal reviewer judgments, not acceptance probabilities.

| Dimension | Score | Rationale |
|---|---:|---|
| Originality | 80 | Numerical-decidability gating for SciML MR verdicts is a clear method contribution. |
| Methodological rigor | 82 | Strong artifact discipline, ledgers, validators, tests, and fail-closed wording. |
| Evidence sufficiency | 78 | Strong bounded evidence plus one real-defect-linked witness; still no production defect corpus. |
| Argument coherence | 76 | Core path is visible, but density remains high. |
| Writing quality | 74 | Readable but compressed and conceptually heavy. |
| Literature integration | 76 | Adequate positioning against MT, SciML, tolerance, and violation-attribution work. |
| Significance / impact | 78 | Useful for SciML V&V practice if readers accept bounded method framing. |

Weighted judgment: approximately **78/100**, near the upper Major Revision /
lower Minor Revision boundary under the reviewer rubric. With JSS-specific fit
and package completeness included, the practical decision is **borderline Minor
Revision**.

## Conditions checklist

| Condition | Status | Evidence |
|---|---|---|
| JSS scope fit | Pass | JSS scope includes V&V/testing and software engineering for AI systems. |
| Evidence-backed claims | Pass | Claim ledger, experiment ledger, tests, validators, and run artifacts pass. |
| Abstract <=250 words | Pass | Local count: 210 words. |
| Highlights | Pass | Five highlights, all <=85 characters. |
| Vitae | Pass | Separate editable biographies, each <100 words. |
| Declarations | Pass | CRediT, competing interest, generative AI, data availability present. |
| PDF build | Pass | 36-page PDF, no matched Overfull/undefined/citation warnings. |
| Page recommendation | Borderline pass | Exactly 36 pages; upper edge of recommendation. |
| Empirical persuasiveness | Mostly pass | Multiple full-chain workflows; one external issue-linked witness; no broad rate claim. |
| Broad-reader readability | Partial | Dense method/evidence narrative remains the main review risk. |

## Final judgement

The manuscript now satisfies the main submission-readiness conditions for a JSS
regular paper. It is no longer blocked by P0 administrative issues, and the
empirical story is materially stronger after the independent periodic-advection
workflow and DeepXDE issue-linked witness.

It is still not honest to say "stable accept" in the sense of high-confidence
acceptance. The strongest defensible statement is:

> **JSS regular-paper submission-ready; plausible Minor Revision path; residual
> Major Revision risk from density and bounded external validity.**

No further experiment is required before submission unless the authors want to
lower risk beyond the current practical threshold. Additional experiments would
have diminishing returns unless they are production-scale or real-defect-corpus
level, which would likely exceed the current submission schedule.
