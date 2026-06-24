# IST Submission Draft

This folder contains the Information and Software Technology submission-format draft.

## Official template source

- Journal target: `Information and Software Technology`
- Publisher template family: Elsevier `elsarticle`
- Official LaTeX instructions checked: <https://www.elsevier.com/en-au/researcher/author/policies-and-guidelines/latex-instructions>
- Official template package downloaded on 2026-06-05:
  <https://assets.ctfassets.net/o78em1y1w4i4/4MpsJHO0MOJ2xZuwGTAbOZ/7bc64af36477c5d6cfce335a1f872363/elsarticle.zip>

The local TeX Live installation did not include `elsarticle.cls`, so `elsarticle.cls` was generated from the official `elsarticle.dtx` and `elsarticle.ins` files and copied into this folder.

## Files

- `main.tex`: current IST-format manuscript draft.
- `references.bib`: current bibliography file.
- `elsarticle.cls`, `elsarticle-harv.bst`, `elsarticle-num.bst`: local Elsevier template dependencies.
- `main.pdf`: compiled PDF draft.

## Build command

Use a writable TeX cache directory if the local TeX installation needs to generate fonts:

```sh
TEXMFVAR=/private/tmp/codex-texmf-var TEXMFCONFIG=/private/tmp/codex-texmf-config pdflatex -interaction=nonstopmode main.tex
bibtex main
TEXMFVAR=/private/tmp/codex-texmf-var TEXMFCONFIG=/private/tmp/codex-texmf-config pdflatex -interaction=nonstopmode main.tex
TEXMFVAR=/private/tmp/codex-texmf-var TEXMFCONFIG=/private/tmp/codex-texmf-config pdflatex -interaction=nonstopmode main.tex
```

Current verification status:

- PDF builds successfully.
- Output: `main.pdf`, 21 pages.
- Approximate manuscript word count from stripped LaTeX source: 4206 words.
- Remaining issues: several overfull/underfull box warnings, mostly from long terms and narrow tables; some new-paper bibliography entries still need metadata verification before submission.
