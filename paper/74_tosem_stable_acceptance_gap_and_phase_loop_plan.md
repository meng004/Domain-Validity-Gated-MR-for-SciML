# 74 · TOSEM stable-acceptance gap and phase-loop repair plan

Date: 2026-07-03.

Purpose: read the latest execution plan and project state, assess the gap to a stable
mid-level acceptance posture for the current target journal, and define a sequential
phase-loop repair plan. This plan does not fabricate missing evidence. Every status
statement below is tied to a file, command, or source read during this audit.

## Evidence read in this audit

Project evidence:

- `NEXT_STEPS.md`: latest project route is A+B+C, theory-first, toward TOSEM stable submission; it records Phase 0/C/B/A-L/S-Q as closed on 2026-07-02.
- `paper/67_deepresearch_verdict_and_ABC_program.md`: current line judged IST/STVR level before the A+B+C program; TOSEM stability requires theory closure, breadth support, and clean ledger discipline.
- `paper/68_phaseC_refocus_skeleton.md`: Phase C reframes the paper around numerical-decidability admissibility.
- `paper/69_phase0_tosem_evidence_gate.md`: before Phase B, arbitrary unstructured-mesh soundness was blocked.
- `paper/70_phaseB_operator_floor_soundness.md`: Phase B partially closes the theory gate with a shape-regular triangular P1 divergence theorem; it explicitly does not cover degenerate meshes, arbitrary operators, discontinuous fields, boundary mismatch, non-P1 estimators, learned-output floors, reliability, or fault-detection claims.
- `paper/71_phaseA_L_measured_advantage_ledger_audit.md`: measured-advantage evidence supports complementarity and gate value, not superiority.
- `paper/72_phaseS_Q_pipeline_reviewer_humanizer_report.md`: prior final QA reported a medium remaining gap, with the main residual risk being external validity and denominator trust.
- `paper/73_academic_reviewer_full_review.md`: simulated TOSEM-calibrated panel recommends Major Revision; consensus issues are broad framing vs bounded evidence, theorem visibility, denominator/effective-N trust, practitioner workflow, and breadth organization.
- `manuscript/main.tex`: current active LaTeX manuscript after TOSEM reframing.
- `research_assets/experiments/claim-ledger.yml`: C53 exists and is `supported-theory`.

Commands executed in the project path:

- `rtk git status --short --branch`: worktree is dirty; `manuscript`/`submissions`/release-package files include modified and untracked artifacts. No reset or cleanup was performed.
- `rtk python3 tools/validate_research_assets.py`: exit 0.
- `rtk python3 tools/validate_experiment_protocol.py`: exit 0.
- `rtk python3 tools/ist_wordcount.py`: IST-counted total 14611, hard cap 15000, headroom 389.
- `rtk .venv/bin/python -m pytest tests -q`: 433 passed, 18 failed.
- `rtk pdflatex -interaction=nonstopmode main.tex`, `rtk bibtex main`, then another `pdflatex` in `manuscript/`: PDF builds to 51 pages; final fixed-string log scan found no undefined references/citations, undefined control sequence, LaTeX Error, Missing character, Overfull hbox, or rerun warning. Underfull hbox warnings remain.

External formatting source checked because the target has changed from IST to ACM TOSEM:

- ACM author instructions say ACM journal submissions must use the ACM authoring template; LaTeX review submissions should use the latest Primary Article Template with `\documentclass[manuscript]{acmart}` single-column format; ACM journals use ScholarOne Manuscript Central except listed exceptions. Source: ACM "Submitting Articles to ACM Journals", lines 377-394 and 498-501, page last revised 2025-12-18.

## Current status

Scientific status: the paper now has a real TOSEM-facing core, not just a workflow story. The core is numerical decidability as a soundness precondition for relation-indexed SciML metamorphic testing. C53 gives a bounded theory artifact for shape-regular triangular P1 divergence, and the manuscript/ledger correctly block superiority, reliability, arbitrary-mesh, and real-world defect-rate claims.

Submission-engineering status: not stable. The current active manuscript is still in an Elsevier/IST-style `elsarticle` package, while the latest project route targets ACM TOSEM. The regression suite also still contains IST-era guards. The full test run fails 18 tests, including title length, abstract length, highlight ledger mention, stale R4/adversarial-mutant markers, FNO positioning, Phase-4 clarity, Stage-2.5 boundary markers, and compact-table section markers.

Acceptance posture: medium-to-large gap overall. If judged only on scientific core, the remaining gap is medium and fixable through focused revision. If judged as a complete target-journal submission package, the gap is larger because the target contract, source of truth, and regression guards are not aligned.

Do not claim: stable accept, minor revision, TOSEM-ready package, general unstructured-mesh theorem, baseline superiority, general SciML reliability, or real-world defect-detection rates.

## Priority by expected acceptance impact

P0. Target contract and green-gate mismatch. Impact: highest. Evidence: `NEXT_STEPS.md` says TOSEM target, ACM instructions require `acmart` manuscript submission, but active package is `elsarticle`; pytest has 18 failures. Without resolving this, any "ready" claim is false.

P1. Broad first-page framing versus bounded evidence. Impact: highest. Evidence: `paper/73` R1 and Devil's Advocate both flag the title/abstract/keywords as inviting a broad SciML-surrogate reading. Current title is 99 characters and still broad.

P2. C53 theorem visibility and assumption control. Impact: highest. Evidence: `paper/73` R2 and DA require a theorem/proposition box. C53 is real but easy to miss; `paper/70` says it is only shape-regular triangular P1.

P3. Denominator and independence trust. Impact: high. Evidence: current text says cells are not independent, but `paper/73` asks for a single nominal-N / effective-N / inference-allowed table.

P4. Practitioner workflow and cost boundary. Impact: medium-high. Evidence: `paper/73` R3 asks for a one-page checklist and clearer adoption cost. Current text has cost caveats but no reviewer-facing workflow checklist.

P5. Breadth evidence organization. Impact: medium-high. Evidence: `paper/73` asks each breadth block to state what it falsifies: checklist-only reading, single-architecture artifact, or single-task artifact.

P6. External-validity evidence. Impact: high for "stable non-edge" acceptance, but not always mandatory for a bounded Major Revision repair. Evidence: `paper/71` and `paper/72` identify external validity and denominator trust as the largest residual scientific risk.

P7. Final polish and AI-style cleanup. Impact: medium. Evidence: `paper/72` already ran one humanizer-style pass, but future rewrites may reintroduce inflated language, connective damage, or overbroad claims.

## Loop protocol used by every phase

Each phase follows the same loop:

1. Entry check: confirm prerequisites and cite the current source files.
2. Repair: make the smallest change set that closes the phase goal.
3. Evidence sync: update claim-ledger, tests, manuscript, and package only where the new evidence licenses it.
4. Verification: run the phase-specific commands and record exact outcomes.
5. Review: perform an adversarial reviewer check focused on the phase risk.
6. Theme-drift check: verify the paper still answers "when is an MR verdict numerically decidable and admissible as SciML V&V evidence?"
7. Checkpoint: do not proceed if the exit condition is not met.

## Phase 0: venue contract and source-of-truth freeze

Prerequisites:

- Dirty worktree acknowledged with `rtk git status --short --branch`.
- User confirms the active target remains TOSEM rather than returning to IST/RESS.

Main steps:

- Create or update `venues/TOSEM.md` from official ACM instructions and any TOSEM-specific page that can be verified.
- Declare the active manuscript source: either convert `manuscript/main.tex` to ACM `acmart` format, or create a separate `submissions/TOSEM/` package and treat `manuscript/main.tex` as source content.
- Decide how IST-era tests should behave: preserve them for an IST package, or split venue-specific gates so TOSEM work is not judged by stale IST title/abstract/highlight constraints.
- Record all untracked or generated files that must not be silently mixed into the submission package.

Exit conditions:

- One target package path exists and is named in the plan.
- Venue-specific tests are explicit; no ambiguous "IST file means TOSEM paper" state remains.
- No manuscript claim is widened during packaging.

Review:

- Check official formatting requirements against current package.
- Confirm the test suite fails or passes for meaningful reasons, not stale venue assumptions.

Theme-drift check:

- Packaging changes must not turn the paper back into a broad reliability or workflow paper.

## Phase 1: green-gate repair loop

Prerequisites:

- Phase 0 target contract is written.
- Active source path is fixed.

Main steps:

- Repair the 18 current test failures by either updating the manuscript to satisfy valid guards or replacing stale IST-only guards with TOSEM-specific guards. This must be done by changing tests only when the venue contract makes the old guard invalid.
- Preserve substantive guard intent: title must not overbroaden, abstract must stay concise, highlights must mention traceable artifacts/ledger, R4/adversarial-mutant evidence must not disappear, and old boundary statements must remain covered by new wording.
- Re-run validators, word count/page estimate, full pytest, and LaTeX build.

Exit conditions:

- `validate_research_assets.py` exit 0.
- `validate_experiment_protocol.py` exit 0.
- Full test suite passes or any remaining failures are documented as intentionally venue-specific and excluded by a named test target.
- PDF build has no undefined refs/citations, no LaTeX Error, no Missing character, no Overfull hbox, and no rerun warning.

Review:

- Review all test edits as if they were reviewer concerns: no weakening just to go green.

Theme-drift check:

- The repaired gates must still enforce prose <= ledger.

## Phase 2: first-page scope and title loop

Prerequisites:

- Phase 1 green-gate state or an accepted temporary exception for venue migration.
- C53 wording boundaries available from `claim-ledger.yml`.

Main steps:

- Narrow the title and keywords so "Scientific ML Surrogates" does not imply broad reliability or arbitrary surrogate coverage.
- Rewrite the abstract so the first page says: criterion, shape-regular P1 theory, bounded case studies, complementarity/gate value, and non-claims.
- If TOSEM format removes IST structured abstract requirements, keep the content discipline even without the five headings.
- Make the blocked-claim list visible early enough that reviewers do not discover it only in threats.

Exit conditions:

- Abstract/title no longer outrun C53/C38/C42/C51/C52.
- No sentence claims general reliability, superiority, arbitrary-mesh soundness, or real-world defect rates.
- Humanizer scan finds no inflated "pivotal/crucial/groundbreaking/underscores" style additions.

Review:

- Run an EIC/Devil's-Advocate check on only the first two pages.

Theme-drift check:

- The paper remains a soundness/admissibility criterion paper, not a general SciML testing benchmark.

## Phase 3: C53 theorem-box loop

Prerequisites:

- Phase 2 first-page scope is bounded.
- `paper/70` theorem and C53 ledger entry are the only theory sources used.

Main steps:

- Add a theorem/proposition box in Method or Results with assumptions, bound, operational decision rule, and non-claims.
- Include a small decision table: P1 diagnostic admissible, P1 absolute conservation deferred, reference-relative diagnostic, flux-form finite-volume alternative, outside-scope cases.
- Ensure Appendix claim map references C53 and the proof artifact.

Exit conditions:

- A reviewer can identify the theorem, assumptions, and forbidden generalizations in under one page.
- The text distinguishes proved shape-regular P1 theory from observed two-topology stability and concrete structured-mesh closed-form predictor.

Review:

- Domain/numerical reviewer check: look for any implicit arbitrary-mesh, learned-output, or boundary-condition claim.

Theme-drift check:

- The theorem supports admissibility soundness only; it must not become a model-correctness or reliability claim.

## Phase 4: denominator and inference table loop

Prerequisites:

- Active evidence blocks are fixed after Phases 2-3.
- Claim ledger remains parseable.

Main steps:

- Add a compact table with columns: evidence block, nominal N/cells, effective independent unit, inference allowed, claim forbidden.
- Cover at minimum: cylinder MGN K=6/trajectories, airfoil 240 cells, PointMLP 20-fault catalogue, PINN/FNO rosters, cross-program sibling evidence, operator-floor sweep, C53 theorem.
- Move repeated caveats out of prose where the table can carry them more clearly.

Exit conditions:

- Every major number on the first-page or Results path has a denominator source and an inference boundary.
- Reviewers cannot read descriptive cells as independent population trials.

Review:

- Methodology reviewer check: try to convert each number into an invalid population-rate claim; the table must block it.

Theme-drift check:

- Denominator clarity should support bounded evidence, not invite a performance-ranking paper.

## Phase 5: practitioner checklist and breadth-falsification loop

Prerequisites:

- Phases 2-4 have fixed the main reviewer-facing scope.

Main steps:

- Add a one-page practitioner checklist: relation candidate -> physical basis -> domain preconditions -> representation mapping -> numerical floor -> verdict type -> allowed claim.
- Add a breadth-falsification map: each block states which alternative reading it falsifies and what it does not prove.
- Clarify when to use flux-form finite-volume operators instead of the P1 diagnostic.
- State adoption cost without implying zero-cost automation.

Exit conditions:

- A practitioner can answer "what do I do on Monday?" without reading the appendices first.
- Breadth evidence is not presented as accumulation for generality; each block has a specific falsification role.

Review:

- Practitioner reviewer check focused on operational value and cost.

Theme-drift check:

- Checklist must be an implementation of numerical-decidability gating, not a new claim of automated MR discovery.

## Phase 6: optional external-validity strengthening loop

Prerequisites:

- Phases 1-5 pass.
- User decides whether "stable non-edge TOSEM" requires new evidence rather than bounded resubmission.

Main steps:

- Choose one high-value external-validity repair only if it can be run and traced: independent SUT, independently authored mutant/defect source, or a stronger public benchmark witness.
- Add a new claim ID before writing any prose.
- Run the experiment or record the blocker; do not convert a failed or unavailable run into positive evidence.

Exit conditions:

- New evidence is committed under `research_assets/runs/`, guarded by tests, and licensed in `claim-ledger.yml`; or the plan records that no new external-validity evidence was added.
- If results contradict the current story, the manuscript is narrowed or the target is downgraded.

Review:

- External validity reviewer check: evaluate whether the new subject is genuinely independent or only another convenience artifact.

Theme-drift check:

- Additional breadth must not revive superiority, reliability, or real-world defect-rate claims.

## Phase 7: TOSEM submission-package loop

Prerequisites:

- Phase 0 target contract is TOSEM.
- Phases 1-5 are green; Phase 6 is either complete or explicitly skipped.

Main steps:

- Build `submissions/TOSEM/` using ACM `acmart` manuscript mode unless a verified TOSEM-specific instruction says otherwise.
- Add CCS concepts, ACM keywords, figure descriptions, artifact/readme material, CRediT/AI-use/funding statements as allowed by ACM workflow.
- Confirm ScholarOne/ACM metadata needs, author identity policy, artifact links, and Zenodo/package synchronization.

Exit conditions:

- TOSEM package compiles cleanly.
- Artifact links and claim ledger match the package.
- No stale IST-only package is presented as the TOSEM submission package.

Review:

- Formatting and submission checklist review against official ACM instructions.

Theme-drift check:

- Formatting conversion must not change scientific claims.

## Phase 8: academic-pipeline final QA and humanizer loop

Prerequisites:

- Submission package is complete.
- All claims are ledger-backed.

Main steps:

- Run academic-pipeline final integrity mode: citation/reference checks, data/claim verification, AI research failure-mode checklist, and final manuscript consistency.
- Run academic reviewer re-review focused on the five `paper/73` required revisions.
- Run humanizer pass only after content stabilizes: remove inflated AI-style language, redundant hedging, unsupported significance labels, and em dashes while preserving logical connectives and evidential qualifiers.
- Re-run validators, full tests, package build, claim scans, and log scans.

Exit conditions:

- Final integrity check has zero blocking issues or records explicit unresolved limitations.
- Humanizer pass changes style only; it does not change numbers, evidence boundaries, or claim strength.
- Final reviewer simulation is at least "Minor Revision leaning Accept" or the remaining Major Revision items are explicitly accepted by the user as submission risk.

Review:

- Mandatory academic-pipeline checkpoint. Do not auto-advance past integrity failures.

Theme-drift check:

- The final paper must still be about numerical-decidability admissibility for relation-indexed SciML MR testing.

## Immediate next action

Start Phase 0, not Phase 2. The current highest-risk problem is not the lack of a clever sentence; it is the mismatch among target journal, active source package, and regression gates. Once Phase 0 fixes the contract, Phase 1 can make the gate green without silently weakening evidence discipline.
