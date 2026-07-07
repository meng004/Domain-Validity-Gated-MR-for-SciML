# JSS Submission Package Review

## Build

- Main source build: pass
- JSS template precheck: pass
- Main PDF log: `Output written on main.pdf (36 pages, 436531 bytes).`
- Warning-pattern hits in final main.log: 0

## Editorial Manager structure

- Repository-level `manuscript/` is the authoritative paper source; this package's `source/` directory is a generated upload copy with shared class/style/bibliography/figure files.
- The manuscript uses Elsevier `elsarticle` with `authoryear` and `elsarticle-harv.bst`, matching the JSS Guide's author-year reference style.
- `jss_latex_source.zip` is flattened for Editorial Manager and contains both `main.tex` and `supplementary.tex` with their shared dependencies.
- Manuscript PDF excludes highlights and the supplementary appendix; highlights and supplementary evidence are separate files.
- Cover letter, declarations, author biographies, and open-science checklist are separate files.
- Supplementary evidence appendix is provided separately as PDF; its editable canonical LaTeX source is `manuscript/supplementary.tex`.

## Desk-rejection risk audit derived from the reference PDF

- Reference source: Staron, `How not to get your paper rejected -- From the editors' notebook`, Information and Software Technology 197 (2026) 108197.
- PDF-derived desk-rejection checks applied: journal scope, novelty/impact, empirical validation, reporting-guideline compliance, replicability/transparency, audience fit, and premature/small-evaluation risk.
- The package foregrounds the software-engineering V&V problem in the abstract and cover letter.
- The title, abstract, and introduction use bounded `admissibility` / `interpretable verdict` wording rather than broad soundness wording, reducing overclaim and audience-fit risk.
- The package avoids claiming production validation, representative defect sampling, trained-SUT correctness, or real-world defect rates.
- Residual risk remains bounded rather than eliminated: the evidence is a curated external issue/PR/commit-linked witness corpus and bounded executions, not a statistical defect corpus.

## LaTeX audit

- Final flat source zip contains no subdirectories and no `.aux`, `.log`, `.out`, `.blg`, `.spl`, or `.DS_Store` files.
- Six broken math/subscript pattern scans were run on the flat `main.tex`; no hits were found.
- Humanization scan found no em dash and no inflated-significance wording requiring automatic repair. Numeric-prefix hits are dates, ORCIDs, or factual catalogue labels rather than invented terms.

## Residual risks

- Editorial Manager item labels must still be selected manually during upload.
- If EM requires every source file as an individual upload rather than a source zip, use the files inside `source/`.
