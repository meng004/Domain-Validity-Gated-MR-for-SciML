# IST submission template — provenance

The IST Guide for Authors (ScienceDirect) directs LaTeX submissions to the
official Elsevier `elsarticle` bundle. CTAN is its canonical distribution.

- Source: https://mirrors.ctan.org/macros/latex/contrib/elsarticle.zip
- Version: `elsarticle.cls` v3.5 / `elsarticle-num.bst` v2.1
- Release date: 2026-01-09; Copyright 2007-2026 Elsevier Ltd
- Maintainer: C. V. Radhakrishnan
- Downloaded: 2026-06-24

`elsarticle.cls` is generated from the official `elsarticle.dtx`/`elsarticle.ins`
(`latex elsarticle.ins`). The vendored copies in `submissions/IST/`
(`elsarticle.cls`, `elsarticle-num.bst`) are this exact v3.5 build.

v3.5 vs prior v3.4: removes the "Preprint submitted to Elsevier" first-page
footer (per Elsevier instruction 2024-10), restores default bibliography
font/spacing, namespaces an internal counter. The manuscript compiles cleanly
under v3.5: 50 pages, 0 warnings, 0 overfull, 0 undefined.
