# 80 - JSS official guide, recent-reference benchmark, and repair plan

Date: 2026-07-03

Scope: read the current JSS official author guidance, extract a reproducible
recent high-citation benchmark from JSS articles, update reusable JSS venue and
template guidance, and define a repair plan for the current paper. The repair
plan is not executed until author confirmation.

## Source hierarchy

Primary venue sources:

- JSS Guide for Authors, ScienceDirect, accessed 2026-07-03:
  `https://www.sciencedirect.com/journal/journal-of-systems-and-software/publish/guide-for-authors`
- JSS Aims and scope, ScienceDirect, accessed 2026-07-03:
  `https://www.sciencedirect.com/journal/journal-of-systems-and-software/about/aims-and-scope`
- JSS Journal Insights, ScienceDirect, accessed 2026-07-03:
  `https://www.sciencedirect.com/journal/journal-of-systems-and-software/about/insights`

Bibliometric benchmark source:

- OpenAlex query, accessed 2026-07-03:
  `https://api.openalex.org/works?filter=primary_location.source.issn:0164-1212,from_publication_date:2024-01-01,to_publication_date:2026-07-03,type:article&sort=cited_by_count:desc&per-page=20`
- Crossref DOI metadata checks for selected benchmark papers, accessed
  2026-07-03.

Local manuscript evidence:

- Current JSS package: `submissions/JSS/`.
- Current final JSS package log: `submissions/JSS/main.log`.
- Current manuscript source: `manuscript/main.tex`,
  `manuscript/manuscript.md`.

## JSS regular-paper requirements that affect this manuscript

Official requirements and constraints:

1. Scope and evidence:
   - JSS covers all aspects of software engineering.
   - All articles should provide evidence for claims, including empirical
     studies, simulation, formal proofs, or other validation.
   - In-scope topics include verification and validation, testing, AI/data
     analytics applied in software engineering, Software Engineering for AI
     systems, and empirical software-engineering methods/tools.
2. Review model:
   - JSS uses single-anonymized review.
3. Abstract:
   - Concise and factual.
   - Maximum 250 words.
   - Standalone, normally without references.
4. Keywords:
   - 1 to 7 English keywords.
5. Highlights:
   - Required at submission.
   - Separate editable file.
   - 3 to 5 bullets.
   - Each bullet maximum 85 characters including spaces.
6. Length:
   - JSS encourages full-length papers under 36 pages single-column or 18 pages
     double-column.
   - If longer, the submission should include an explanation justifying the
     length.
   - This is a page-count recommendation, not a word-count cap found in the
     guide.
7. Tables and figures:
   - Tables must be editable text.
   - All tables and figures must be cited.
   - Tables should be used sparingly and should not duplicate prose.
   - Figures must be supplied as separate files; vector drawings should be EPS
     or PDF.
8. Research data:
   - JSS uses research-data Option C: deposit research data in a relevant
     repository and cite/link it, or explain why data cannot be shared.
   - Data availability is required at submission.
9. Software citation:
   - Software, scripts, models, notebooks, and libraries should be cited with
     creator, title, repository/archive, date/version, and identifier.
10. Mandatory submission declarations:
   - Competing interests declaration.
   - Funding source disclosure.
   - Generative-AI use declaration if AI tools were used in manuscript
     preparation.
   - CRediT author-contribution statement.
   - Short biographies, maximum 100 words per author.

## Recent high-citation JSS reference set

Definition used here:

- Journal: Journal of Systems and Software.
- ISSN filter: 0164-1212.
- Publication date: 2024-01-01 to 2026-07-03.
- Type: article.
- Ranking: OpenAlex `cited_by_count` descending.
- Result set size: 750 articles.

Top OpenAlex-ranked papers from this query:

| Rank | OpenAlex cited_by_count | Date | Ref. count | Paper |
|---|---:|---|---:|---|
| 1 | 130 | 2024-03-21 | 83 | GRACE: Empowering LLM-based software vulnerability detection with graph structure and in-context learning |
| 2 | 68 | 2024-02-22 | 247 | A/B testing: A systematic literature review |
| 3 | 62 | 2025-01-31 | 78 | UVL: Feature modelling with the Universal Variability Language |
| 4 | 44 | 2024-02-02 | 35 | Sustainability competencies and skills in software engineering: An industry perspective |
| 5 | 37 | 2024-04-16 | 50 | GPTSniffer: A CodeBERT-based classifier to detect source code written by ChatGPT |
| 6 | 37 | 2024-02-15 | 68 | Emerging technologies in higher education assessment and feedback practices: A systematic literature review |
| 7 | 36 | 2024-05-22 | 127 | Microservice API Evolution in Practice: A Study on Strategies and Challenges |
| 8 | 33 | 2024-07-20 | 54 | Hybrid quantum architecture for smart city security |
| 9 | 31 | 2024-11-15 | 72 | Agent design pattern catalogue: A collection of architectural patterns for foundation model based agents |
| 10 | 31 | 2024-10-18 | 73 | DLAP: A Deep Learning Augmented Large Language Model Prompting framework for software vulnerability detection |

Crossref check examples:

| Paper | Crossref is-referenced-by-count | Crossref reference-count | DOI |
|---|---:|---:|---|
| GRACE | 137 | 76 | `10.1016/j.jss.2024.112031` |
| A/B testing SLR | 66 | 191 | `10.1016/j.jss.2024.112011` |
| GPTSniffer | 37 | 56 | `10.1016/j.jss.2024.112059` |
| Automating correctness assessment of AI-generated code | 28 | 84 | `10.1016/j.jss.2024.112113` |
| UVL | 34 | 92 | `10.1016/j.jss.2024.112326` |

OpenAlex and Crossref counts differ, as expected, because the services use
different coverage and update pipelines. The ranking above therefore records the
data source and date, not a timeless citation fact.

## Benchmark implications for evidence scale and depth

What high-impact recent JSS papers show:

1. Evaluation breadth is explicit:
   - GRACE reports evaluation on three real-world vulnerability datasets and
     six state-of-the-art baselines.
   - GPTSniffer compares against two baselines and studies training/context
     factors.
   - Microservice API Evolution uses 17 semi-structured interviews across 11
     companies and open coding.
   - A/B testing SLR consolidates 143 studies.
   - ACCA compares four state-of-the-art generators, multiple baseline
     assessment methods, and human evaluation.
2. Reproducibility is visible:
   - Several reference papers expose code/data/material or replication packages.
   - JSS Open Science validation appears in at least one recent article page.
3. Independent evidence is not one fixed number:
   - For tools or detection methods, recent JSS examples typically use several
     independent datasets, baselines, or models.
   - For qualitative SE practice studies, independent evidence may be companies,
     interview participants, or coded artifacts.
   - For language/tool papers, adoption, parser/tool integration, and open
     repositories can function as independent evidence.
4. For this paper's method type, the closest rule is not "more cells" but
   "independent evidence units with distinct failure modes":
   - different SUT/task families;
   - different MR/operator families;
   - independent baselines or reference procedures;
   - reproducible artifacts and explicit threat-to-validity boundaries.

Practical target for the current paper:

- Minimum defendable JSS regular-paper target:
  3 or more clearly independent evidence units, each with a distinct role, plus
  reproducible ledgers and a compact main-text explanation.
- Stronger target:
  at least one additional independent primary-scale SUT or an explicit
  reviewer-facing justification that the current paper is a method/proof-plus-
  bounded-validation paper rather than a benchmark paper.

## Current paper gap analysis

Current verified state:

- JSS package builds successfully.
- Current `submissions/JSS/main.pdf`: 45 pages after Phase B supplementary
  extraction.
- Current abstract: 209 words.
- Current keywords: 7.
- Current highlights: 5 bullets, all under 85 characters.
- Existing evidence gates and regression tests passed in Phase 8.

Problems by acceptance impact:

### P0 - Page-length and package-rule mismatch

Issue:

- JSS encourages full-length papers under 36 pages single-column or 18 pages
  double-column. The current JSS package PDF is 45 pages single-column after
  moving detailed appendices to supplementary material.

Why it matters:

- This is a direct official-guide mismatch. It can trigger editor/reviewer
  friction even if not an absolute rejection rule.

Fix direction:

- Either reduce the main manuscript further, move additional audit detail to
  supplementary material, or switch to an Elsevier double-column submission form
  and verify the 18-page double-column target. The current cover letter includes
  a factual length justification, but this remains a review-risk item until the
  editor accepts the explanation or the manuscript is compressed further.

### P1 - Independent SUT evidence is still bounded

Issue:

- The paper has multiple evidence families, but primary evidence remains centered
  on the cylinder-flow workflow. Airfoil, PINN, FNO, sibling, and fault evidence
  are currently framed as supporting or falsification evidence.

Why it matters:

- Recent high-impact JSS method/tool papers often show evaluation over several
  independent datasets, systems, companies, models, or baselines. The current
  manuscript is defensible as a method/proof-plus-bounded-validation paper, but
  weaker as a broad empirical tool paper.

Fix direction:

- Make the independent-evidence-unit table more reviewer-facing and, if feasible,
  add one additional primary-scale independent SUT. If not feasible, explicitly
  justify the current evidence strategy as bounded validation, not a benchmark.

### P1 - Data/software citation and repository-readiness need a JSS-specific pass

Issue:

- The manuscript has repository artifacts, ledgers, scripts, and data statements,
  but JSS specifically asks for research data deposit/linking or an explanation
  when sharing is not possible, and asks software to be cited as software.

Why it matters:

- JSS emphasizes Open Science and reproducibility. Artifact availability can
  reduce reviewer doubt for a method paper with bounded empirical scope.

Fix direction:

- Add or verify data/software references for the repository release, datasets,
  scripts, and external software artifacts. Ensure the submission package has a
  clear data-availability statement with persistent identifiers if available.

### P2 - Main-text density and appendix load

Issue:

- The paper still reads partly like an evidence audit. It has many tables and
  appendices, while JSS says tables should be used sparingly and not duplicate
  text.

Why it matters:

- Recent JSS articles tend to present a clear evaluation narrative: RQs,
  independent evidence units, baselines/comparators, results, threats. Dense
  audit detail can obscure the contribution.

Fix direction:

- Collapse or move detailed ledgers to supplementary material; keep only the
  main RQ/evidence/claim boundary in the paper.

### P2 - Cover-letter length justification is missing

Issue:

- If the paper remains above the JSS recommended page count, the cover letter
  should explicitly justify length.

Why it matters:

- The official guide asks for an explanation when the manuscript is longer than
  the recommended page count.

Fix direction:

- Add a short, factual length-justification paragraph only if final page count
  remains above the JSS recommendation.

## Proposed repair plan, pending author confirmation

Execution authorized by the user on 2026-07-03. Execute phases in priority order.

### Phase A - JSS rule correction and package audit

Priority: P0.

Preconditions:

- Author confirms the updated JSS contract.
- No new scientific claim is added.

Steps:

1. Update `paper/77`, `paper/79`, and `submissions/JSS/README.md` to replace
   the incomplete "no word cap found" framing with the official page-count
   recommendation.
2. Add a JSS page-count check to the local submission-readiness tests.
3. Decide whether the target package should be single-column under 36 pages or
   double-column under 18 pages.

Exit conditions:

- Local docs and tests reflect the official page recommendation.
- Current package status explicitly says 45 pages single-column and therefore
  needs compression or justification.

Review and drift check:

- Do not invent a hard rejection rule. The rule is an encouragement plus
  justification requirement, not a proven absolute cap.

### Phase B - Length and density repair

Priority: P0.

Preconditions:

- Phase A is accepted.
- Current evidence boundaries are locked.

Steps:

1. Move detailed cross-program, LLM/generic baseline, and low-load-bearing
   appendix material to supplementary material.
2. Keep one compact main-text table for evidence units and inference permissions.
3. Merge repetitive boundary statements into one canonical evidence-boundary
   paragraph plus table notes.
4. Rebuild PDF and measure page count.

Exit conditions:

- Preferred: under 36 pages single-column or under 18 pages double-column.
- Current Phase B result: detailed appendices moved to supplementary material;
  package rebuilt to 45 pages single-column; cover letter includes a factual
  length justification. This satisfies the fallback exit condition but not the
  preferred page-count target.

Review and drift check:

- Compression must not remove evidence IDs, result numbers, or claim boundaries
  needed by tests.

Phase B execution status: partial-complete on 2026-07-03.

Completed actions:

- Moved the detailed JSS package appendices from `submissions/JSS/main.tex` to
  `submissions/JSS/supplementary/evidence_appendices.tex`.
- Replaced main-text appendix references with supplementary-material wording so
  the compiled JSS package has no dangling labels.
- Added `submissions/JSS/supplementary/README.md`.
- Updated `submissions/JSS/README.md` and `submissions/JSS/cover_letter.md` with
  the measured length status and factual justification.

Review acceptance:

- JSS package build chain in `submissions/JSS/`: `pdflatex`, `bibtex`,
  `pdflatex`, `pdflatex`, all exit 0 after the extraction.
- Final `submissions/JSS/main.pdf`: 45 pages, 477814 bytes.
- Log scan found no undefined references or citations, LaTeX errors, missing
  characters, overfull boxes, citation rerun, label rerun, or cross-reference
  rerun markers.

Residual risk:

- The package is shorter than the Phase A 49-page build but remains above the
  JSS recommendation of fewer than 36 single-column pages. Further compression
  or editor acceptance of the length justification is still required before this
  can be called final-upload-ready.

### Phase C - Independent evidence-unit strengthening

Priority: P1.

Preconditions:

- Phase B creates enough space in the manuscript.
- Evidence ledger is the source of truth.

Steps:

1. Create a reviewer-facing evidence-unit table:
   unit, SUT/task, MR/operator, independence source, evidence role, allowed
   inference, forbidden inference.
2. Reclassify current units without inflating them:
   cylinder-flow primary, airfoil changed-physics falsification, PINN/FNO
   operator/family transfer, sibling programs external audit, faults detector
   blind-spot stress tests.
3. Decide whether a new independent primary-scale SUT is feasible. If not,
   write a bounded-validation justification.

Exit conditions:

- A JSS reviewer can see at least three independent evidence units and why each
  has a distinct failure mode.
- No evidence family is presented as population-level representativeness.

Review and drift check:

- Do not convert supporting evidence into primary evidence unless the raw
  execution and ledger support it.

Phase C execution status: completed on 2026-07-03.

Completed actions:

- Reworked the nominal/effective-N table in `manuscript/main.tex`,
  `manuscript/manuscript.md`, and `submissions/JSS/main.tex` into an
  independent-evidence-unit table.
- Added explicit columns for SUT/task and MR/operator, independence source,
  evidence role, allowed inference, and forbidden inference.
- Classified the current evidence without inflation:
  cylinder primary workflow, same-task architecture check, changed-physics
  airfoil task, PINN/FNO PDE families, and fault/external witnesses.
- Added regression guards requiring the independent-evidence-unit wording,
  independence source, and evidence role markers to remain present.

Review acceptance:

- `rtk .venv/bin/python -m pytest tests/test_stage4_revision_readiness.py -q`:
  5 passed, 35 subtests passed.
- `submissions/JSS/main.tex` recompiled after the table change: final PDF
  45 pages, 478520 bytes.
- JSS log scan found no undefined references or citations, LaTeX errors, missing
  characters, overfull boxes, citation rerun, label rerun, or cross-reference
  rerun markers.

Residual risk:

- Phase C improves reviewer-facing independence classification, but it does not
  create a new independent primary-scale SUT. The paper must continue to present
  airfoil, PINN/FNO, sibling, and fault evidence according to their stated roles
  rather than as population-level representativeness.

### Phase D - Open Science, data, and software citation repair

Priority: P1.

Preconditions:

- Repository/release status is known.

Steps:

1. Audit whether every dataset, script package, model, and external software
   dependency cited as evidence has a stable citation or repository URL.
2. Add software/data references where appropriate.
3. Update data availability to match JSS Option C: repository deposit/linking,
   or explicit non-sharing reason.
4. Check whether JSS Open Science Initiative participation is realistic.

Exit conditions:

- Data/software availability is directly submission-ready.
- No unpublished or unavailable artifact is implied to be public.

Review and drift check:

- Do not claim Open Science validation before JSS Open Science Board review.

Phase D execution status: completed on 2026-07-03.

Completed actions:

- Updated `.zenodo.json` to remove the stale Information and Software Technology
  submission description and align the archive description with the JSS
  regular-paper target.
- Updated JSS `declarations.md`, `main.tex`, and the manuscript sources so data
  availability points to the Zenodo DOI, source repository, committed evidence
  directories, Minimum-MR-SubSet commit, public benchmark inputs, and fail-closed
  credential boundaries.
- Updated `REPRODUCIBILITY.md` so archival status uses the existing DOI instead
  of an acceptance-time placeholder.
- Added `submissions/JSS/open_science_checklist.md` and linked it from the JSS
  package README.
- Added a P0 regression guard for JSS data/software availability metadata.

Review acceptance:

- `rtk .venv/bin/python -m pytest tests/test_p0_submission_readiness.py -q`:
  6 passed, 5 subtests passed.
- `rtk .venv/bin/python -m pytest tests/test_stage4_revision_readiness.py -q`:
  5 passed, 35 subtests passed.
- `submissions/JSS/main.tex` recompiled after the data-availability repair:
  final PDF 45 pages, 480870 bytes after the final Phase E wording adjustment.
- JSS log scan found no undefined references or citations, LaTeX errors, missing
  characters, overfull boxes, citation rerun, label rerun, or cross-reference
  rerun markers.

Residual risk:

- The package is prepared for data/software availability review, but it has not
  been validated by a JSS Open Science Board and must not claim any JSS Open
  Science badge.

### Phase E - Final JSS package rebuild

Priority: P2.

Preconditions:

- Phases A-D are complete or explicitly waived.

Steps:

1. Rebuild JSS package.
2. Run tests, validators, page-count check, abstract/highlight/keyword checks,
   LaTeX log scan, and high-risk-claim scan.
3. Update cover letter only with verified facts.

Exit conditions:

- Package compiles.
- Page-count status is acceptable or justified.
- Evidence boundaries remain ledger-faithful.

Review and drift check:

- Final package must remain a JSS software V&V method paper, not a broad SciML
  reliability benchmark or baseline-superiority paper.

Phase E execution status: completed on 2026-07-03.

Completed actions:

- Rebuilt the current JSS package through the full LaTeX/BibTeX chain:
  `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
- Re-ran the final JSS log scan, page-count parser, evidence validators, density
  diagnostic, P0/stage guards, and full regression suite.
- Fixed one post-verification prose issue caught by the full suite: the Phase C
  table wording used repetitive `not a` disclaimer phrasing, now replaced with a
  positive boundary statement.

Review acceptance:

- Final `submissions/JSS/main.pdf`: 45 pages, 480870 bytes.
- Final JSS log scan found no undefined references or citations, LaTeX errors,
  missing characters, overfull boxes, citation rerun, label rerun, or
  cross-reference rerun markers.
- `rtk python3 tools/validate_research_assets.py`: exit 0.
- `rtk python3 tools/validate_experiment_protocol.py`: exit 0.
- `rtk python3 tools/ist_wordcount.py`: 14702 legacy-counted words; headroom 298
  under the legacy 15000 diagnostic cap.
- `rtk .venv/bin/python -m pytest tests -q`: 447 passed, 334 subtests passed.

Residual risk:

- Phase E verifies package consistency but does not erase the JSS page-length
  risk. The current package remains 45 pages single-column, above the JSS
  recommendation of fewer than 36 single-column pages. The cover letter and
  README contain the factual length explanation; further compression remains the
  main pre-submission improvement if the author wants to reduce editor friction.
