# JSS template instructions

Verified: 2026-07-04.

Use this template for Journal of Systems and Software regular-paper submissions.
The template follows the JSS Guide for Authors and Elsevier LaTeX instructions.

## Required files

- `main.tex`: editable Elsevier LaTeX manuscript source.
- `references.bib`: bibliography database.
- `elsarticle.cls`: Elsevier article class.
- `elsarticle-num.bst`: numbered BibTeX style.
- `highlights.txt`: 3 to 5 highlights, each at most 85 characters.
- `cover_letter.md`: submission cover letter.
- `declarations.md`: CRediT, competing interests, funding, data availability,
  and generative-AI declaration text.
- `author_biographies.md`: separate editable biographies, each at most 100 words.
- `precheck_jss.py`: hard pre-submission checks.

## Editorial Manager LaTeX rule

Elsevier's LaTeX instructions state that Editorial Manager cannot process LaTeX
submissions with subfolders. For the final source zip, place `main.tex`,
`references.bib`, `main.bbl` if used, `elsarticle.cls`, `elsarticle-num.bst`,
and all figure files in the same folder. Remove paths such as `figures/` from
`\includegraphics{...}`.

## Hard checks before submission

- Abstract: 250 words or less, factual, standalone.
- Keywords: 1 to 7 English keywords.
- Highlights: 3 to 5 bullets; each 85 characters or less including spaces.
- Page count: target under 36 pages single-column or 18 pages double-column. If
  longer, add a factual length-justification paragraph to the cover letter.
- Evidence: each claim maps to empirical study, simulation, formal proof, or
  other validation.
- Data/software: deposit and cite/link data and software where possible; otherwise
  state why sharing is not possible.
- Author biographies: separate editable file, not in the manuscript body.

## Local build

```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
python3 precheck_jss.py main.tex
```

Final log scan should show only the `Output written` line:

```bash
rg -n "Output written|Overfull|undefined|Undefined|Citation|Rerun|Warning|LaTeX Warning|Package natbib Warning" main.log
```

