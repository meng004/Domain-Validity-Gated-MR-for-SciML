# JSS P0-P1 repair report

Date: 2026-07-03

Target: Journal of Systems and Software regular paper.

Scope: repair the P0-P1 items identified in
`paper/84_academic_reviewer_jss_stable_acceptance_review.md`.

## Inputs

- JSS package: `submissions/JSS/`.
- Previous review: `paper/84_academic_reviewer_jss_stable_acceptance_review.md`.
- Author-biography source supplied by the author:
  `/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/MR识别/最小完备MR子集/manuscript/author_bios.tex`.
- JSS venue record: `../../venues/jss.md`, verified 2026-07-03.

## P0 repairs

### Author biographies / Vitae

Status: repaired.

Action:

- Replaced the pending TODO biographies in `submissions/JSS/author_biographies.md`
  with biography text derived only from the supplied source file.
- Kept the biographies outside `main.tex`, as required by the JSS Vitae rule.
- Kept every biography under the JSS 100-word limit:
  Meng Li 26 words; Xiaohua Yang 25 words; Jie Liu 25 words; Shiyu Yan
  25 words.

Evidence:

- `submissions/JSS/author_biographies.md`.
- No `TODO`, `pending author`, or obsolete 37-page wording remains in
  `submissions/JSS/README.md`, `submissions/JSS/cover_letter.md`,
  `submissions/JSS/author_biographies.md`, or `submissions/JSS/main.tex`.

### Page-count risk

Status: materially repaired, with residual "upper edge" risk.

Action:

- Performed another prose-level compression pass in `submissions/JSS/main.tex`,
  mainly in Results/Discussion, Threats, Future Work, and Conclusion.
- Added compact natbib reference spacing with `\setlength{\bibsep}{0pt plus 0.2ex}`.
- Updated `submissions/JSS/README.md` and `submissions/JSS/cover_letter.md`
  from the obsolete 37-page status to the current 36-page status.

Evidence:

- Final build log: `Output written on main.pdf (36 pages, 412508 bytes)`.
- No `Overfull`, undefined-reference, changed-label, or citation warnings were
  found by the final log scan.

Interpretation:

- The package is no longer in the previous 37-page state.
- Because `../../venues/jss.md` records the JSS recommendation as "under 36
  pages single-column or 18 pages double-column", 36 pages should still be
  described conservatively as the upper edge of the recommendation rather than
  as a zero-risk length condition.

## P1 repairs

Status: repaired enough for submission-package readiness, not enough to claim
guaranteed acceptance.

Action:

- Preserved the main P0 evidence markers during compression:
  periodic-advection primary workflow; 60/60 translation passes; 60/60
  mass-conservation passes; fixed-velocity mirror candidate rejection; not
  production CFD or real-defect evidence; inconclusive reference-relative
  non-regression guard; normalizer-control change from 1.1032 to 1.1014; and
  the calibrated in-distribution magnitude boundary.
- Retained the explicit evidence boundary against baseline superiority,
  general SciML reliability, production CFD evidence, real-defect rates, and
  calibrated coverage claims.
- Updated the cover letter to frame the contribution as a bounded V&V workflow
  with auditable evidence rather than a general reliability claim.

## Verification commands and results

- `pdflatex -interaction=nonstopmode main.tex`: passed; 36-page PDF.
- `bibtex main`: passed.
- Final `pdflatex -interaction=nonstopmode main.tex`: passed; 36-page PDF.
- Final log scan: only `Output written on main.pdf (36 pages, 412508 bytes)`;
  no overfull, undefined-reference, changed-label, or citation warnings matched.

## Remaining risk

The P0 administrative blockers identified in the prior review are repaired.
The largest remaining acceptance risks are now scientific/editorial rather than
package-completion blockers:

- 36 pages is still at the upper edge of the JSS length recommendation.
- The empirical evidence remains deliberately bounded: no production CFD,
  no real-defect corpus, no broad neural-operator reliability claim.
- Conceptual density remains a review risk, although the main evidence pathway
  is now shorter and the claim boundary is still explicit.

Conclusion: the manuscript is closer to a JSS-ready regular-paper package than
in the prior review. It is fair to say that P0 is repaired and P1 is materially
reduced. It is not fair to claim stable acceptance or guaranteed acceptance.
