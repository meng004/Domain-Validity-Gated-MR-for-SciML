# 79 · Phase 8 JSS pipeline, reviewer, and humanizer report

Date: 2026-07-03

Target: Journal of Systems and Software (JSS), regular paper.

Scope: final Phase 8 check after executing Phase 6 structure compression and
Phase 7 JSS package preparation. This report records only checks actually
performed in the local repository. It does not claim external peer review or
acceptance.

## Inputs checked

- Manuscript source: `manuscript/main.tex`, `manuscript/manuscript.md`.
- JSS package: `submissions/JSS/main.tex`, `submissions/JSS/main.pdf`,
  `submissions/JSS/highlights.txt`, `submissions/JSS/cover_letter.md`,
  `submissions/JSS/declarations.md`, `submissions/JSS/README.md`.
- Evidence gates: `tools/validate_research_assets.py`,
  `tools/validate_experiment_protocol.py`, regression tests under `tests/`.
- Claim boundary source: `research_assets/experiments/claim-ledger.yml`.

## Reproducible checks

| Check | Result |
|---|---|
| Evidence asset validator | exit 0 |
| Experiment protocol validator | exit 0 |
| Full regression suite | 445 passed, 328 subtests passed |
| Conservative legacy word-count diagnostic | 14668 total; headroom 332 under the old IST counter |
| Manuscript LaTeX build | exit 0; PDF 49 pages, 501873 bytes |
| JSS page-count recommendation | Post-Phase-8 correction required: 49 pages single-column exceeds the JSS recommendation of fewer than 36 pages single-column or 18 pages double-column |
| JSS package build chain | `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`, all exit 0 |
| JSS package final log scan | no undefined references/citations, LaTeX errors, missing characters, overfull boxes, or rerun markers |
| JSS abstract count | 209 words |
| JSS keywords | 7 |
| JSS highlights | 5 bullets; 62, 70, 67, 67, and 58 characters |
| Em dash scan | no matches after replacing Markdown table placeholders with `none` |
| AI-inflation pattern scan | no matches for the configured high-risk terms |

## Academic-pipeline integrity result

The final text remains claim-ledger-faithful in the checked areas. The manuscript
states a bounded numerical-decidability and admissibility workflow for SciML
metamorphic testing. It does not assert general SciML reliability, baseline
superiority, arbitrary-mesh soundness, real-world defect-detection rates, or
broad neural-operator generalization.

The high-risk claim scan found the risky terms only in boundary or blocked-claim
contexts. This is acceptable because the paper uses those terms to define what
the evidence does not support.

## JSS-calibrated reviewer re-review

Editorial fit:

- Fit is now plausible for JSS because the paper is framed as a software V&V
  method for testing SciML surrogate software.
- The first-page framing, practitioner checklist, typed verdicts, claim ledger,
  and JSS package all point to software-engineering evidence rather than a CFD or
  SciML performance benchmark.
- No current desk-reject-level venue mismatch was found in this re-review.

Methodology:

- The denominator/effective-N table and the centralized boundary wording reduce
  the risk that repeated cells are read as independent population evidence.
- The C53 proposition is visible and bounded to P1 constant-per-cell divergence
  on shape-regular triangular meshes with C2 divergence-free reference fields.
- The remaining methodological risk is external validity: the primary evidence
  still rests on bounded case studies and supporting falsification checks, not a
  broad population sample.

Software-engineering contribution:

- The strongest contribution is the auditable chain from MR cards to executable
  runners, typed verdicts, evidence ledgers, and manuscript claims.
- The paper now better explains adoption cost: relation-specific physics review,
  mapping code, operator-floor evidence, and bookkeeping.
- The main residual risk is reviewer appetite for more independent SUT evidence
  before accepting a regular paper.

Devil's Advocate:

- A skeptical reviewer may still ask whether the appendix is too dense for a
  regular JSS paper.
- A skeptical reviewer may also ask whether the method is sufficiently general
  beyond the primary cylinder-flow setting. The current text blocks overclaiming
  rather than pretending this risk is solved.
- No evidence was found that would justify strengthening claims beyond the
  current wording.

## Humanizer result

The humanizer pass was intentionally conservative. The final scan found no em
dash characters in the manuscript/JSS package sources checked here and no matches
for the configured inflated-writing terms. Four Markdown table placeholders were
changed from em dash characters to `none`. No claim, result, number, citation,
or venue fact was changed.

## Final Phase 8 decision

Phase 8 is accepted as complete for claim-faithfulness, metadata, compilation,
and humanizer checks. A renewed JSS guide read after Phase 8 corrected the length
contract: the current 49-page single-column package exceeds the JSS recommended
length. Therefore the package should not be treated as final-upload-ready until
it is compressed, converted and checked in double-column form, or accompanied by
a factual length justification. The remaining risks are bounded external
validity, reviewer preference for additional independent systems, density in the
supporting appendices, and the page-count risk.
