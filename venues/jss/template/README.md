# JSS template instructions

Verified: 2026-07-04 against the local ScienceDirect Guide for Authors PDF and the bundled Elsevier template zips.

Use this directory for Journal of Systems and Software submissions. The local authoritative guide is:

`Guide for authors - Journal of Systems and Software - ISSN 0164-1212 | ScienceDirect.com by Elsevier.pdf`

## Template choice

This directory keeps both official Elsevier template families:

- `elsarticle.zip` and extracted `elsarticle-*` files.
- `els-cas-templates.zip` and extracted selected CAS files under `cas/`.

For this project, the default template is `elsarticle` with author-year references:

```tex
\documentclass[preprint,12pt,authoryear]{elsarticle}
\journal{Journal of Systems and Software}
\bibliographystyle{elsarticle-harv}
```

CAS (`cas-sc` or `cas-dc`) is available as an optional Elsevier workflow template, not the default for this package.

## Required/expected files

- `main.tex`: editable Elsevier LaTeX manuscript source.
- `references.bib`: bibliography database.
- `elsarticle.cls`: Elsevier article class.
- `elsarticle-harv.bst`: author-year BibTeX style for JSS.
- `highlights.txt`: 3 to 5 highlights, each at most 85 characters including spaces.
- `cover_letter.md`: submission cover letter.
- `declarations.md`: CRediT, competing interests, funding, data availability, and generative-AI declaration text.
- `author_biographies.md`: separate editable biographies, each at most 100 words.
- `precheck_jss.py`: hard pre-submission checks.

## Hard checks before submission

- Abstract: 250 words or less, factual, standalone, normally no references.
- Keywords: 1 to 7 English keywords.
- Highlights: 3 to 5 bullets, each 85 characters or less including spaces.
- Review process: single anonymized, so do not anonymize author names or affiliations.
- Page count: target under 36 pages single-column or 18 pages double-column; explain if longer.
- References: author-year style preferred for JSS; reference list complete and consistent.
- Evidence: every claim maps to empirical study, simulation, formal proof, or other validation.
- Data/software: deposit and cite/link data and software where possible; otherwise state why sharing is not possible.
- Author biographies: separate editable file, not in the manuscript body.

## Local build

```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
python3 precheck_jss.py main.tex
```

Final log should have no unresolved citations/references or rerun warnings.
