# JSS submission package

Target venue: Journal of Systems and Software, regular paper.

This venue directory contains JSS-only submission materials. The editable
manuscript authority is the repository-level `manuscript/` directory:

- `../../manuscript/main.tex`: manuscript source, with author information retained for single-anonymized review.
- `../../manuscript/supplementary.tex`: supplementary evidence source.
- `../../manuscript/references.bib`: bibliography database.
- `../../manuscript/figures/`: manuscript figures used by `main.tex`.
- `template/`: local Elsevier class/style files used when generating the upload package.
- `highlights.txt`: five editable highlights, each no longer than 85 characters.
- `cover_letter.md`: draft cover letter for Editorial Manager.
- `author_biographies.md`: separate editable author-biography/vitae file;
  each biography is sourced from the author-supplied biography file and no
  longer than 100 words.
- `declarations.md`: submission-system text for CRediT, competing interests, generative-AI use, data availability, and evidence boundary.
- `open_science_checklist.md`: data/software availability and JSS Open Science
  status audit.

Build check:

```bash
python venues/jss/build.py
```

Evidence boundary:

The paper claims an auditable admissibility and numerical-decidability workflow for SciML metamorphic testing, with a bounded five-unit external issue/PR/commit-linked witness corpus. It does not claim general SciML reliability, baseline superiority, arbitrary-mesh soundness, representative defect sampling, real-world defect-detection rates, production validation, or broad framework correctness.

Package status:

- JSS journal metadata is adapted in the generated package copy from `../../manuscript/main.tex`.
- The abstract is unstructured and within the JSS 250-word limit used by the project plan.
- Keywords are within the 1-7 keyword range used by the project plan.
- Declarations are present in the manuscript source and mirrored in `declarations.md` for submission-system entry.
- Data/software availability points to the Zenodo archive DOI and source
  repository; unavailable external inputs are identified by source and
  provenance rather than implied to be bundled.
- No graphical abstract is included.
- Length status after regenerating from `manuscript/main.tex` on 2026-07-06:
  the compiled main manuscript is 36 pages single-column after moving detailed
  evidence appendices to the separate supplementary file. This meets the
  project target of no more than 36 pages and sits at the upper edge of the
  JSS single-column length guidance; the cover letter states the page count
  and identifies the supplementary material as separate evidence support.
