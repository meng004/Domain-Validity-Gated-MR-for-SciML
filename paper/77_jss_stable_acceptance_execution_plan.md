# 77 · JSS stable-acceptance execution plan

Date: 2026-07-03

Purpose: freeze the revised target as Journal of Systems and Software (JSS),
regular paper, and define a phase-by-phase Loop-engineering execution plan for
moving the manuscript toward a realistic, evidence-faithful, stable JSS submission.

This record does not claim acceptance is guaranteed. "Stable acceptance" here means
the manuscript should be revised until the most likely editorial outcome is a
reviewable paper with major-revision-or-better prospects, not a desk-reject caused
by venue mismatch, scope drift, unsupported claims, or package defects.

## Source hierarchy

Hard sources for this plan:

1. User decision on 2026-07-03: **主投 JSS，按 JSS regular paper 修**.
2. `paper/75_deep_research_rq_venue_recommendation.md`: deep-research RQ and
   venue recommendation, recalibrated to JSS.
3. `paper/76_academic_reviewer_venue_recalibration.md`: academic-reviewer panel;
   JSS is the operational target, TOSEM is aspirational only.
4. `research_assets/experiments/claim-ledger.yml`: prose may not exceed the claim
   ledger.
5. JSS official pages, verified 2026-07-03:
   - Guide for Authors:
     `https://www.sciencedirect.com/journal/journal-of-systems-and-software/publish/guide-for-authors`
   - Aims and scope:
     `https://www.sciencedirect.com/journal/journal-of-systems-and-software/about/aims-and-scope`
   - Journal Insights:
     `https://www.sciencedirect.com/journal/journal-of-systems-and-software/about/insights`

## JSS contract snapshot

The following items are copied into the project contract because they affect
revision and submission readiness:

- JSS publishes software-engineering papers and requires evidence for claims.
  Acceptable evidence forms include empirical studies, simulation, formal proofs,
  or other validation.
- Relevant topics include verification and validation, testing, AI/data analytics
  applied in software engineering, Software Engineering for AI systems, and methods
  and tools for empirical software engineering research.
- JSS uses **single anonymized review**. Author names and affiliations remain in the
  manuscript.
- JSS abstract requirement: concise factual abstract, **maximum 250 words**.
- JSS keywords: **1 to 7** English keywords.
- JSS highlights: required at submission, **3 to 5 bullets**, each **maximum 85
  characters including spaces**, submitted as a separate editable file.
- JSS accepts LaTeX submissions and requests editable source files. Elsevier LaTeX
  templates are recommended.
- JSS Insights on 2026-07-03: Impact Factor 4.1, CiteScore 9.4, APC USD 3,670 for
  open access, subscription route with no publication fee, acceptance rate 15%,
  submission-to-acceptance 203 days.
- No JSS-specific regular-paper word limit was found in the official guide page
  during this check. Therefore any word target used here is a readability and
  reviewer-risk target, not an official cap.
- Phase A correction from a renewed guide read on 2026-07-03: JSS encourages
  full-length papers to be under 36 pages single-column or 18 pages
  double-column. If the manuscript is longer, the submission should explain why
  the length is justified.

## Revised target statement

Current operational target:

> Journal of Systems and Software (JSS), regular paper.

Positioning:

> A software V&V method paper about when a physics-derived metamorphic relation
> is numerically decidable and physically admissible as an oracle-free test for
> SciML surrogate software.

Not the target:

- not a general SciML reliability benchmark;
- not a baseline-superiority paper;
- not a real-world defect-rate paper;
- not an arbitrary-mesh soundness paper;
- not a reliability-engineering paper for RESS;
- not a current TOSEM submission.

## Acceptance-impact priority order

1. Freeze the JSS contract and remove stale IST/TOSEM target drift.
2. Re-run evidence and test gates; classify failures before changing tests.
3. Rewrite title, abstract, and introduction for JSS scope and 250-word abstract.
4. Make C53 visibly load-bearing without expanding beyond its assumptions.
5. Add nominal-N / effective-N / inference-allowed table.
6. Add practitioner checklist and adoption-cost boundary.
7. Reduce density and demote non-load-bearing breadth evidence.
8. Build a JSS submission package.
9. Run academic-pipeline integrity, academic-reviewer re-review, and humanizer pass.

## Phase 0 · JSS target-contract freeze

Preconditions:

- User has authorized JSS as the primary target.
- JSS official pages have been checked on 2026-07-03.
- `paper/75` and `paper/76` already support JSS as the operational target.

Core steps:

1. Update live project status so current target is JSS, not IST or TOSEM.
2. Preserve older IST/TOSEM records as history, but mark them as superseded by the
   JSS decision.
3. Record JSS official requirements and the evidence source for each requirement.
4. Define phase gates and drift checks before any manuscript rewrite.

Exit conditions:

- `NEXT_STEPS.md` points to JSS as the current execution target.
- Agent guidance files no longer say the active target is IST.
- This plan exists and can be used as the execution record.

Review acceptance:

- No manuscript claim is changed in Phase 0.
- No historical record is deleted or rewritten as if it never happened.
- The current target is unambiguous: JSS regular paper.

Theme-drift check:

- TOSEM appears only as aspirational ceiling or history.
- IST appears only as history or legacy package material.
- STVR remains excluded.
- RESS is not reintroduced as a target.

## Phase 1 · Evidence and gate baseline

Preconditions:

- Phase 0 exit conditions are met.
- No Phase 2 prose edits have been made yet.

Core steps:

1. Run:
   - `rtk python3 tools/validate_research_assets.py`
   - `rtk python3 tools/validate_experiment_protocol.py`
   - `rtk python3 tools/ist_wordcount.py`
   - `rtk .venv/bin/python -m pytest tests -q`
2. Record exact outputs in this file or a follow-on Phase 1 audit file.
3. Classify failing tests:
   - evidence/claim guard still relevant to JSS;
   - stale IST formatting guard;
   - stale TOSEM target guard;
   - real manuscript defect;
   - environment/package issue.
4. Do not weaken any evidence guard without root-cause analysis.

Exit conditions:

- Each failing gate has a root-cause category and planned fix.
- Evidence validators either pass or their failures are traced to concrete files.
- The next phase knows which tests must remain red until prose is revised.

Review acceptance:

- Failure classification is evidence-based, not convenient.
- Any proposed test change states why it remains faithful to the claim ledger.

Theme-drift check:

- Passing tests is not allowed to become more important than preserving evidence
  boundaries.
- The old IST 15,000-word counter may remain as a conservative local diagnostic,
  but it is not treated as a JSS official cap.

Phase 1 execution status: completed on 2026-07-03.

Observed baseline:

- `rtk python3 tools/validate_research_assets.py`: exit 0.
- `rtk python3 tools/validate_experiment_protocol.py`: exit 0.
- `rtk python3 tools/ist_wordcount.py`: initial Phase 1 value 14611 / 15000
  legacy IST-counted words; after Phase 2 first-page compression, 14567 / 15000.
- `rtk .venv/bin/python -m pytest tests -q`: initial Phase 1 value
  434 passed, 17 failed, 313 subtests passed.

Root-cause classification of the initial failures:

| Failure group | Root cause | JSS action |
|---|---|---|
| Long title and 317-word structured abstract | Real JSS first-page defect; JSS requires <=250-word abstract | Fixed in Phase 2 |
| Abstract/highlight ledger marker | Real auditability issue | Fixed in Phase 2 highlights |
| R4 adversarial-mutant markers missing in LaTeX | Main LaTeX package lagged behind Markdown source | Fixed by syncing R4 wording |
| FNO primary workflow marker missing in LaTeX | Main LaTeX package lagged behind Markdown source | Fixed by syncing FNO boundary wording |
| Phase 4 13050-word clarity buffer | Historical IST buffer, no longer JSS official; still useful as density signal | Replaced by 14600 local JSS-readability diagnostic pending Phase 6 compression |
| Structured-abstract / 300-word guard | IST-specific target guard | Replaced by JSS <=250-word abstract guard |
| Stale framework wording and table markers | Historical wording drift after numerical-decidability reframing | Updated guards to current JSS wording without weakening claim boundaries |

Post-fix Phase 1 verification:

- `rtk .venv/bin/python -m pytest tests -q`: 444 passed, 319 subtests passed.
- `rtk python3 tools/validate_research_assets.py`: exit 0.
- `rtk python3 tools/validate_experiment_protocol.py`: exit 0.
- LaTeX full chain in `manuscript/`: `pdflatex`, `bibtex`, `pdflatex`,
  `pdflatex` all exit 0; PDF remains 51 pages.
- Fixed-string log scan found no `undefined`, `Undefined`, `LaTeX Error`,
  `Missing character`, `Overfull \hbox`, citation-rerun, label-rerun, or `Rerun`
  markers. Underfull hbox warnings remain and are not submission blockers.

## Phase 2 · JSS first-page rewrite

Preconditions:

- Phase 1 has classified current gate failures.
- The active claim boundaries are known.

Core steps:

1. Rewrite title direction for JSS:
   - prefer "Numerical Decidability for Sound Metamorphic Testing of SciML
     Surrogates" or a similarly bounded variant.
2. Rewrite abstract to <=250 words and make it factual, standalone, and
   reference-free.
3. Rewrite the first two introduction pages to lead with:
   - oracle-free testing problem;
   - numerical decidability and physical admissibility;
   - typed verdicts;
   - bounded proof-plus-validation evidence.
4. Remove or demote language that suggests broad reliability, superiority, or
   arbitrary-mesh guarantees.

Exit conditions:

- Abstract <=250 words.
- Title and abstract do not outrun `claim-ledger.yml`.
- A JSS editor can see the software-engineering method contribution on page 1.

Review acceptance:

- Run a quick EIC/JSS-fit review and a Devil's Advocate pass.
- Search for high-risk words: superiority, general, reliability guarantee,
  arbitrary mesh, defect rate, representative.

Theme-drift check:

- The first page must not become a TOSEM-style top-SE ambition pitch.
- The first page must not become a CFD/SciML performance paper.

Phase 2 execution status: completed on 2026-07-03.

Completed actions:

- Shortened title to `Numerical Decidability for Sound SciML Metamorphic Testing`.
- Replaced the old IST structured abstract with a JSS-compatible factual abstract
  under 250 words.
- Updated highlights to include the claim/evidence ledger and keep five short
  bullets.
- Synchronized the Markdown source title/abstract with the LaTeX front matter.
- Added missing first-page boundary wording in LaTeX: no completed applicability
  map; one bounded within-SUT contribution plus bounded witnesses; broader
  calibrated maps remain future work.
- Synced R4 adversarial-mutant and FNO primary-workflow wording into LaTeX so the
  main package carries the same evidence boundaries as the Markdown source.

Review acceptance:

- P0/P1 targeted tests: 13 passed, 5 subtests passed.
- Full test suite after Phase 2: 444 passed, 319 subtests passed.
- Theme drift check: the abstract now states auditable admissibility workflow and
  explicitly excludes general SciML reliability, baseline superiority,
  arbitrary-mesh soundness, and real-world defect-detection rates.

## Phase 3 · C53 theorem/proposition visibility

Preconditions:

- Phase 2 first-page scope is bounded.
- Claim C53 is present and supported in `claim-ledger.yml`.

Core steps:

1. Add a theorem/proposition box for C53 in the main text.
2. Include assumptions:
   - P1 constant-per-cell divergence diagnostic;
   - shape-regular triangular meshes;
   - C2 divergence-free reference fields with bounded Hessian.
3. State the bound and the admissible conclusion.
4. State forbidden extrapolations near the theorem.
5. Connect the theorem directly to typed defer/valid verdict semantics.

Exit conditions:

- C53 is visually and logically central.
- The theorem does not imply non-P1, learned-output, degenerate-mesh, or
  arbitrary-mesh guarantees.

Review acceptance:

- Domain/numerical reviewer can identify all assumptions without searching the
  appendix.
- Methodology reviewer agrees the experiments do not overgeneralize the theorem.

Theme-drift check:

- "Observed stable on unstructured examples" must not become "proved for arbitrary
  unstructured meshes."

Phase 3 execution status: completed on 2026-07-03.

Completed actions:

- Added `Proposition (C53: P1 operator-floor soundness)` to
  `manuscript/main.tex` and `manuscript/manuscript.md`.
- The proposition states only the ledger-supported boundary: P1
  constant-per-cell divergence, shape-regular triangular meshes, C2
  divergence-free fields, bounded Hessian, and a local floor bounded by
  `C_shape M h`.
- The proposition explicitly excludes arbitrary/degenerate meshes, non-P1
  operators, learned-output, boundary-mismatch, reliability, and
  fault-detection guarantees.
- Added a regression marker to `tests/test_stage4_revision_readiness.py` so the
  C53 proposition cannot silently disappear.

Review acceptance:

- `rtk .venv/bin/python -m pytest tests -q`: 444 passed, 320 subtests passed.
- `rtk python3 tools/validate_research_assets.py`: exit 0.
- `rtk python3 tools/validate_experiment_protocol.py`: exit 0.
- `rtk python3 tools/ist_wordcount.py`: 14600 legacy-counted words, used only as
  a conservative local density diagnostic; JSS official guide check found no
  regular-paper word cap. Phase A later corrected the contract with JSS's
  page-count recommendation: under 36 single-column pages or 18 double-column
  pages, or explain the excess length.
- LaTeX `pdflatex` reruns completed with no fixed-string blockers in
  `manuscript/main.log`; Underfull hbox warnings remain.

Theme-drift result:

- C53 remains a numerical-decidability soundness claim for one operator class, not
  a general SciML reliability or arbitrary-mesh theorem.

## Phase 4 · Denominator and effective-N repair

Preconditions:

- Phase 3 sets the theoretical boundary.
- The evidence inventory from Phase 1 is available.

Core steps:

1. Add a consolidated nominal-N / effective-N / inference-allowed table.
2. Cover MGN checkpoints, airfoil cells, mutant trials, sibling/cross-program
   witnesses, and PINN/FNO rosters.
3. Mark descriptive evidence, bounded stress tests, witnesses, and non-independent
   repeated cells explicitly.
4. Align all Results and Discussion wording to the table.

Exit conditions:

- A reviewer cannot reasonably mistake non-independent cells for independent
  population evidence.
- All population-level or rate-level claims remain blocked unless ledger-supported.

Review acceptance:

- Methodology reviewer approves denominators and inference permissions.
- Claim-ledger audit finds no strengthened empirical claim.

Theme-drift check:

- Breadth evidence is not used as statistical representativeness.
- Mutant results are not used as real-world defect-rate evidence.

Phase 4 execution status: completed on 2026-07-03.

Completed actions:

- Added Table `tab:effective-n`, "Nominal-N, effective-N, and inference
  permissions", to `manuscript/main.tex`.
- Added the corresponding Markdown table to `manuscript/manuscript.md`.
- Covered the MGN cylinder roster, airfoil gate-discrimination cells, PointMLP
  and same-task variants, PINN/FNO cross-family executions, and fault/external
  witnesses.
- For each evidence block, separated nominal cell counts from effective evidence
  units and stated which inferences are allowed or forbidden.
- Added regression markers to `tests/test_stage4_revision_readiness.py` so this
  denominator repair cannot silently disappear.
- Compressed one introductory sentence after the new table pushed the legacy
  density diagnostic to 15002 words; no claim, result, or evidence boundary was
  changed by that compression.

Review acceptance:

- `rtk python3 tools/ist_wordcount.py`: 15000 legacy-counted words; this is a
  conservative local density diagnostic, not a JSS official cap.
- `rtk .venv/bin/python -m pytest tests/test_stage4_revision_readiness.py
  tests/test_phase4_clarity_surgery.py -q`: 8 passed, 26 subtests passed.
- `rtk .venv/bin/python -m pytest tests -q`: 444 passed, 322 subtests passed.
- `rtk python3 tools/validate_research_assets.py`: exit 0.
- `rtk python3 tools/validate_experiment_protocol.py`: exit 0.
- `rtk pdflatex -interaction=nonstopmode main.tex` rerun in `manuscript/`: exit
  0 after cross-reference stabilization; fixed-string log scan found no
  `undefined`, `Undefined`, `LaTeX Error`, `Missing character`, `Overfull`, or
  cross-reference rerun markers. Underfull hbox warnings remain.

Theme-drift result:

- The added table blocks population-rate, cross-SUT-rate, geometry-independent,
  neural-operator-generalization, real-world-defect-rate, superiority, and
  validated-localization readings unless later evidence explicitly supports them.
- The paper is still a JSS software V&V method paper, not a benchmark,
  reliability, or defect-rate paper.

## Phase 5 · Practitioner workflow and cost boundary

Preconditions:

- Phase 4 prevents denominator misreading.

Core steps:

1. Add a practitioner checklist:
   - define the relation;
   - check physical admissibility;
   - compute or estimate numerical floor;
   - compare tolerance to floor;
   - issue typed verdict;
   - record claim boundary.
2. Add cost/adoption limits:
   - domain expertise required;
   - operator-specific floor required;
   - not a replacement for expert MR design.
3. Reframe breadth evidence as falsification roles.

Exit conditions:

- JSS readers can see how the method is applied.
- Practical value is clear without claiming automation or general reliability.

Review acceptance:

- Practitioner reviewer can summarize the workflow in six steps.
- Devil's Advocate does not find hidden "low-cost automation" claims.

Theme-drift check:

- The paper must not imply domain experts are replaceable.

Phase 5 execution status: completed on 2026-07-03.

Completed actions:

- Added `Practitioner checklist and adoption boundary` to `manuscript/main.tex`.
- Added the corresponding checklist/boundary paragraph to
  `manuscript/manuscript.md`.
- The checklist states six application steps: state the relation/source, record
  source/follow-up preconditions, check boundary labels and output mapping, bound
  or calibrate the operator floor, compare verdict tolerance with the floor, and
  issue a typed verdict with ledgered evidence.
- The adoption boundary states that the method does not remove domain expertise
  or automate MR discovery; adoption costs are relation-specific physics review,
  mapping code, floor evidence, and bookkeeping.
- Added a regression guard in `tests/test_stage4_revision_readiness.py` requiring
  the practitioner checklist and the domain-expertise/fault-claim boundary to
  remain visible.
- Debugged the Phase 8 style guard after the new boundary text increased repeated
  `not a` phrasing. Rewrote the new boundary and one nearby method sentence into
  positive wording without changing the evidence boundary.

Review acceptance:

- `rtk python3 tools/ist_wordcount.py`: 14996 legacy-counted words.
- `rtk .venv/bin/python -m pytest tests/test_stage4_revision_readiness.py
  tests/test_phase4_clarity_surgery.py tests/test_phase8_novelty_clarity_revision.py
  -q`: 13 passed, 32 subtests passed.
- `rtk .venv/bin/python -m pytest tests -q`: 445 passed, 328 subtests passed.
- `rtk python3 tools/validate_research_assets.py`: exit 0.
- `rtk python3 tools/validate_experiment_protocol.py`: exit 0.
- `rtk pdflatex -interaction=nonstopmode main.tex` rerun in `manuscript/`: exit
  0 after cross-reference stabilization; fixed-string log scan found no
  `undefined`, `Undefined`, `LaTeX Error`, `Missing character`, `Overfull`,
  citation rerun, or cross-reference rerun markers. Underfull hbox warnings
  remain.

Theme-drift result:

- The practitioner paragraph adds usability without claiming automation, replacing
  experts, low-cost adoption, baseline superiority, reliability guarantees, or
  real-world fault attribution.

Phase 0-5 re-review note on 2026-07-03:

- Phase 0-4 are accepted as complete for the JSS checkpoint.
- Phase 5 is accepted only as **basically qualified / sufficient to enter Phase
  6**, not as a final practitioner-value completion. The checklist and adoption
  boundary are now visible, but the manuscript still needs Phase 6 structure work
  to make breadth evidence read as falsification/supporting evidence rather than
  as an artifact catalogue.
- To make Phase 5 fully qualified, Phase 6 must:
  1. place the six-step practitioner workflow in the paper's main logic rather
     than as an isolated paragraph;
  2. map each supporting evidence family to one falsification role;
  3. demote LLM/generic/sibling/breadth evidence to supporting evidence in both
     Results and Discussion;
  4. remove repeated caveat phrasing by centralizing evidence boundaries;
  5. keep the domain-expertise and operator-floor cost boundary visible after
     compression.
- The live task tracker was repaired after this review: the old TOSEM/IST/RESS
  history was archived to `paper/78_superseded_next_steps_history_20260703.md`,
  and `NEXT_STEPS.md` now points to JSS Phase 6 as the sole next action.

## Phase 6 · Structure compression

Preconditions:

- Phases 2-5 have stable text and no high-risk claim drift.

Core steps:

1. Reorder the paper around one contribution:
   numerical-decidability-gated metamorphic testing.
2. Demote LLM candidate generation, generic baselines, sibling evidence, and
   breadth demonstrations to supporting roles.
3. Reduce dense caveat repetition by centralizing evidence boundaries.
4. Keep JSS reviewer readability as the controlling factor.

Exit conditions:

- The paper reads as a regular JSS method paper, not an internal audit report.
- Each table and figure has a load-bearing role.

Review acceptance:

- Full academic-reviewer panel returns no desk-reject-level concern.
- Clarity issues are minor or bounded.

Theme-drift check:

- The manuscript must not become an artifact catalog.

Phase 6 execution status: completed on 2026-07-03.

Completed actions:

- Rewrote the Results opening in `manuscript/main.tex` and
  `manuscript/manuscript.md` so evidence roles are explicit:
  cylinder-flow is primary evidence; airfoil/PINN/FNO executions are supporting
  falsification checks; LLM/generic baselines and sibling reruns are secondary
  scope contrasts; seeded faults are detector blind-spot stress tests.
- Made the load-bearing roles of the main result tables explicit:
  `tab:rqmap`, `tab:mr-card-verdict`, `tab:primary-result-summary`, and
  `tab:effective-n`.
- Compressed the cross-program and secondary-baseline appendices while preserving
  all guard markers required by tests and all reported numerical facts.
- Replaced repeated caveat phrasing with centralized evidence-boundary wording
  without weakening the claim ledger.
- Preserved the Phase 5 practitioner/adoption boundary after compression.

Review acceptance:

- `rtk .venv/bin/python -m pytest tests -q`: 445 passed, 328 subtests passed.
- `rtk python3 tools/validate_research_assets.py`: exit 0.
- `rtk python3 tools/validate_experiment_protocol.py`: exit 0.
- `rtk python3 tools/ist_wordcount.py`: 14668 legacy-counted words, used only as
  a conservative density diagnostic; headroom 332 under the old IST counter.
- `rtk pdflatex -interaction=nonstopmode main.tex` in `manuscript/`: final PDF
  49 pages, 501873 bytes.
- Fixed-string log scan in `manuscript/main.log` found no undefined references
  or citations, LaTeX errors, missing characters, overfull boxes, or rerun
  markers. Underfull hbox warnings remain and are not treated as blockers.

Theme-drift result:

- Phase 6 makes Phase 5 fully qualified: the practitioner workflow is no longer
  an isolated value paragraph because the Results structure now shows how each
  evidence family supports, falsifies, or bounds the method.
- Breadth evidence remains supporting/falsification evidence, not statistical
  representativeness, baseline superiority, or general SciML reliability.

## Phase 7 · JSS package

Preconditions:

- The revised manuscript passes Phase 6 review.

Core steps:

1. Create `submissions/JSS/`.
2. Prepare manuscript source, PDF, highlights, cover letter, declarations, CRediT,
   data/code availability, and submission README.
3. Use Elsevier LaTeX-compatible editable source.
4. Compile and scan for LaTeX, reference, figure, and package defects.

Exit conditions:

- JSS package is upload-ready.
- Source and PDF are consistent.
- Highlights satisfy 3-5 bullets, <=85 characters each.

Review acceptance:

- Format/compliance review passes.
- Citation/reference audit passes.

Theme-drift check:

- Do not rename the IST package as JSS without JSS-specific review.

Phase 7 execution status: completed on 2026-07-03.

Completed actions:

- Created `submissions/JSS/` with editable Elsevier LaTeX source, bibliography,
  local `elsarticle` files, figure PDFs, compiled PDF, highlights, cover letter,
  declarations, and package README.
- Updated the JSS package metadata:
  `\journal{Journal of Systems and Software}` and JSS-specific top comment in
  `submissions/JSS/main.tex`.
- Added `submissions/JSS/highlights.txt` with five highlights; measured lengths
  are 62, 70, 67, 67, and 58 characters.
- Added `submissions/JSS/cover_letter.md` and `submissions/JSS/declarations.md`
  with bounded claims and no acceptance or superiority overclaim.

Review acceptance:

- JSS package build chain in `submissions/JSS/`: `pdflatex`, `bibtex`,
  `pdflatex`, `pdflatex`, all exit 0.
- Final `submissions/JSS/main.pdf` after Phase B supplementary extraction:
  45 pages, 477814 bytes.
- Phase A page-count correction remains active: this 45-page single-column
  package exceeds the JSS recommended length and must be further compressed or
  justified before final submission.
- Final log scan found no undefined references or citations, LaTeX errors,
  missing characters, overfull boxes, citation rerun, label rerun, or
  cross-reference rerun markers. Underfull hbox warnings remain.
- Abstract count from `submissions/JSS/main.tex`: 209 words.
- Keyword count: 7.
- Metadata scan found the active package target only as Journal of Systems and
  Software; occurrences of Information and Software Technology remain only as
  cited journal titles in `references.bib`, not as target metadata.

Theme-drift result:

- The JSS package was built from the revised source and checked as a JSS package;
  it is not a renamed IST package.

## Phase 8 · Academic pipeline, reviewer, humanizer

Preconditions:

- JSS package exists and compiles.

Core steps:

1. Run academic-pipeline-style integrity checks:
   claim-faithfulness, citation/data consistency, abstract/conclusion consistency.
2. Run academic-reviewer re-review calibrated to JSS.
3. Apply humanizer_academic to reduce AI-like writing patterns while preserving
   claim strength and technical precision.
4. Recompile and re-run final gates.

Exit conditions:

- No unsupported claim remains.
- No verified source is missing for factual venue or result claims.
- Reviewer residual issues are minor or explicitly acknowledged.

Review acceptance:

- Final integrity check passes.
- JSS reviewer panel no longer predicts desk reject.

Theme-drift check:

- Humanization must not strengthen cautious claims.
- Polished prose must remain ledger-faithful.

Phase 8 execution status: completed on 2026-07-03.

Completed actions:

- Ran academic-pipeline-style integrity checks using local, reproducible gates:
  evidence validators, full regression tests, conservative word-count diagnostic,
  final LaTeX log scan, abstract/keyword/highlight checks, metadata scan, and
  high-risk claim wording scan.
- Performed a JSS-calibrated reviewer re-review and recorded the result in
  `paper/79_phase8_jss_pipeline_reviewer_humanizer_report.md`.
- Applied `humanizer_academic` constraints conservatively: scanned for em dash
  characters and AI-typical inflated wording, then replaced four Markdown table
  em dash placeholders with `none`. No result, claim, number, or citation was
  changed.
- Re-ran the full test suite after the humanizer edit.

Review acceptance:

- `rtk .venv/bin/python -m pytest tests -q`: 445 passed, 328 subtests passed
  after the final humanizer edit.
- Em dash scan over manuscript and JSS package sources: no matches.
- AI-inflation pattern scan over manuscript and JSS package sources: no matches
  for the configured high-risk terms.
- High-risk claim scan found terms such as reliability, superiority,
  arbitrary-mesh, real-world defect, and guarantee only in explicit boundary or
  blocked-claim contexts, not as positive claims.
- Reviewer re-review finds no current desk-reject-level venue mismatch after
  Phase 6-7, but retains residual risks: bounded external validity, dense
  appendices, likely reviewer interest in more independent SUT evidence, and the
  Phase A/B page-count risk created by the current 45-page single-column package.

Theme-drift result:

- Humanization did not strengthen the paper's claims. The paper remains a bounded
  JSS software V&V method paper, not a reliability benchmark, baseline contest,
  arbitrary-mesh theorem, or real-world defect-rate study.

## Phase 0 status

Status: completed on 2026-07-03.

Completed actions:

- Added this JSS execution plan.
- Updated `NEXT_STEPS.md` so the current execution target is JSS regular paper.
- Updated `AGENTS.md` and `CLAUDE.md` so future agents do not resume the stale
  IST/TOSEM target.
- Verified by text scan that current-target wording points to JSS, while TOSEM
  remains only as history or aspirational ceiling.

Overall execution status after Phase 8:

- Phase 0-8 are complete under the JSS stable-acceptance plan.
- The current package is ready for author-side inspection in
  `submissions/JSS/`, not a guarantee of acceptance.

Immediate next action after this record:

Author-side review of `submissions/JSS/main.pdf`, `cover_letter.md`,
`declarations.md`, and `highlights.txt`; then decide whether to submit, request
another reviewer pass, or commit/archive the package state.
