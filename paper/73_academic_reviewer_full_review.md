# Academic Reviewer Full Review

Date: 2026-07-02

Manuscript reviewed: `manuscript/main.tex`

Title: "Numerical Decidability as a Soundness Criterion for Metamorphic Testing of Scientific ML Surrogates"

Target venue assumed for calibration: ACM TOSEM / top software-engineering journal.

Mode: `academic-paper-reviewer` full review. This is a read-only review; no manuscript edits were made.

## Phase 0: Field Analysis and Reviewer Configuration

Primary field: software engineering, software testing, metamorphic testing.

Secondary field: scientific machine learning, numerical methods, computational physics V&V.

Methodology type: mixed methodological + empirical software-engineering paper with theory component, executable artifacts, bounded case-study evidence, and seeded-fault stress tests.

Reviewer panel:

1. **EIC**: TOSEM handling editor for software testing and empirical software engineering. Focus: journal fit, contribution framing, novelty, maturity, and claim discipline.
2. **Reviewer 1, Methodology**: empirical SE / software-testing methodologist. Focus: experimental design, denominators, statistics, baselines, artifact-backed reproducibility.
3. **Reviewer 2, Domain**: SciML V&V / numerical-methods reviewer. Focus: physical validity, numerical floor, discretization assumptions, theory-to-implementation boundary.
4. **Reviewer 3, Perspective**: practitioner-facing testing and reliability reviewer. Focus: operational value, adoption cost, reproducibility, and whether the work will matter to SE readers.
5. **Devil's Advocate**: skeptical top-SE reviewer. Focus: strongest rejection argument, overgeneralization, hidden dependence on one core example, and whether the contribution is a re-labeling of careful engineering.

## Independent Review Reports

### EIC Review

Recommendation: **Major Revision**

Confidence: **4/5**

The paper now has a coherent TOSEM-facing identity: numerical decidability is positioned as a soundness precondition for metamorphic testing of SciML surrogates. This is clear in the title (line 65), abstract objective and method (lines 91-95), contribution framing (lines 127-139), and claim boundary section (lines 553-560). The manuscript is stronger than a workflow/tool paper because it links a methodological criterion to executable artifacts, typed verdicts, and a bounded operator-floor theorem.

Strengths:

- **Clearer central contribution**: Lines 127-133 define numerical decidability as the gate on admissibility, and the operator-floor contribution is now explicit rather than buried.
- **Good claim discipline**: Lines 139, 346, 367, 553, and 571 repeatedly prevent superiority, general reliability, and real-world fault-rate overclaims.
- **Reviewer-facing evidence map**: The design table at lines 351-373 and appendix claim map make the paper easier to audit than many artifact-heavy SE submissions.

Weaknesses:

- **Major: external validity still feels narrower than the title and keywords suggest.** The paper says the evidence is bounded (lines 302-304, 571-575), but the title and abstract still invite a broad "Scientific ML Surrogates" reading. A TOSEM reviewer may ask whether the claim should be scoped to mesh/PDE surrogates or relation-indexed SciML tests with numerical floors.
- **Major: the paper remains dense and long.** The introduction and evidence sections contain many safeguards, which are honest but make the main line hard to retain. The paper risks being read as "too many artifacts, one core theorem."
- **Minor: the preprint and AI-use disclosures are useful, but they also alert reviewers to provenance.** The manuscript should ensure the replication package and claim ledger are fully public and stable at submission.

EIC score: Originality 78, Methodological Rigor 72, Evidence Sufficiency 70, Argument Coherence 76, Writing Quality 74. Weighted average: **73.4**.

### Reviewer 1: Methodology Review

Recommendation: **Major Revision**

Confidence: **4/5**

The experimental design is unusually transparent. The subject inventory explicitly separates primary, supporting, secondary, and stress-test evidence (lines 302-331), and the analysis plan distinguishes descriptive cell summaries from inferential statistics (line 373). This is a major strength. However, the design still relies on convenience/role-based subjects rather than statistically representative sampling, and several denominators are not independent.

Strengths:

- **Denominator honesty**: Lines 302-304 state that the subjects are selected for evidence roles and are not sampling frames for general defect-detection rates.
- **Boundary-aware metrics**: Lines 333-346 frame the metrics as relation-cell outcomes and complementarity, not superiority.
- **Statistical caution**: Line 373 correctly labels repeated cells and restricts inferential claims.

Weaknesses:

- **Major: effective independent units need a single consolidated table.** The paper reports K=6 checkpoints, 3 trajectories, 240 airfoil cells, 30 trials per mutant, 60-entry catalogues, and external witness rows, but reviewers need a concise "nominal N vs effective N vs inference allowed" table.
- **Major: baseline comparisons remain contextual rather than decisive.** Lines 346 and 367 correctly avoid superiority, but then the paper should not rely on comparator language to motivate acceptance. The value should be stated as false-alarm prevention and typed triage, not performance competition.
- **Minor: inter-rater agreement appears in the metrics list (line 336), but the reviewer-facing evidence for it is not prominent in the main text.** Either foreground the result or remove/de-emphasize the metric.

Methodology score: Originality 74, Methodological Rigor 70, Evidence Sufficiency 68, Argument Coherence 74, Writing Quality 72. Weighted average: **71.0**.

### Reviewer 2: Domain / Numerical V&V Review

Recommendation: **Major Revision**

Confidence: **4/5**

The numerical-decidability argument is the strongest part of the revised manuscript. The abstract states the tolerance-vs-operator-floor requirement (lines 91-95), the contribution section defines the P1 shape-regular boundary (line 133), and the results section reports the slope, confidence interval, closed-form predictor, and Delaunay topology check (line 477). This gives the work a defensible soundness core.

Strengths:

- **C53 substantially improves theoretical support**: Line 477 gives the local reason for the operator floor and states the theorem boundary.
- **Correct deferral behavior**: Lines 452 and 477 make the important point that absolute conservation remains deferred when the floor is not decidable.
- **Task-discriminating physics**: Line 472 is convincing: incompressible divergence-free continuity is rejected on compressible airfoil for the right physical reason.

Weaknesses:

- **Critical/Major: the theory boundary must be even more visually explicit.** The result is for P1 constant-per-cell divergence on shape-regular triangular meshes and C2 divergence-free reference fields. Reviewers may still skim "unstructured Delaunay" as "general unstructured mesh." Add a theorem box or main-text proposition with assumptions and non-claims.
- **Major: boundary and learned-output effects are future work, but they are central to SciML deployment.** Lines 567 and 579-581 acknowledge this. A reviewer may require a clearer explanation of when a user should choose a flux-form finite-volume operator instead of the P1 diagnostic.
- **Minor: the relation between reference-relative diagnostic and absolute conservation should be diagrammed.** Lines 452 and 477 are precise but easy to miss.

Domain score: Originality 82, Methodological Rigor 76, Evidence Sufficiency 72, Argument Coherence 78, Writing Quality 74. Weighted average: **76.0**.

### Reviewer 3: Perspective / Practical Impact Review

Recommendation: **Major Revision leaning Minor after focused tightening**

Confidence: **3/5**

The paper's practical value is that it prevents invalid metamorphic verdicts from being treated as model faults. The mirror-y and conservation examples make this concrete: asymmetric mirror-y becomes OOD stress rather than a defect oracle (lines 438-450), while absolute conservation is deferred and only a reference-relative guard is reported (lines 440, 452). This is useful for practitioners who build tests around physics relations.

Strengths:

- **Operational assets are well motivated**: MR cards, runners, ledgers, and typed verdicts are not just documentation; they prevent overclaiming.
- **Adoption cost is honestly stated**: Lines 558-560 say the gate requires domain knowledge, numerical analysis, and testing expertise, and does not measure person-hours.
- **Reproducibility posture is strong**: Lines 577 and the Phase S/Q report show successful temporary-mirror validators and compiled output, while recording the OneDrive permission caveat.

Weaknesses:

- **Major: the practitioner workflow is hard to extract.** A TOSEM reader should be able to answer "What do I do on Monday?" Add a one-page checklist: relation candidate -> four gate checks -> floor decision -> verdict type -> allowed claim.
- **Major: cost-benefit evidence is absent.** Line 560 admits person-hours and maintenance cost are not measured. This is acceptable, but the paper should not imply easy adoption.
- **Minor: the paper's appendix breadth may distract from the main value.** The cross-program sections are useful, but they may read as defensive accumulation unless the main text states exactly what each breadth block falsifies.

Impact score: Originality 76, Methodological Rigor 70, Evidence Sufficiency 70, Argument Coherence 72, Writing Quality 72. Weighted average: **72.0**.

### Devil's Advocate Review

Recommendation: **Major Revision; reject if the claim is not narrowed**

Confidence: **4/5**

Strongest counter-argument:

The paper may still be over-positioned. Its central example is a particular numerical issue in using P1 divergence as a conservation diagnostic on mesh-based SciML surrogates. The authors then surround this with MR cards, typed verdicts, claim ledgers, multiple SUT rosters, LLM candidate sources, generic baselines, external sibling artifacts, and seeded mutants. A skeptical reviewer could argue that the core accepted contribution is narrower than the manuscript's framing: "if your measurement operator has a numerical floor, do not issue a pass/fail oracle below that floor." That is valuable, but not obviously a broad framework for SciML V&V. The evidence blocks show diligence, not necessarily generality. The strongest fix is not more breadth prose; it is a sharper theorem/criterion presentation and a more modest title/abstract claim that makes the paper about admissibility soundness for relation-indexed SciML tests.

Critical / major issues:

- **Critical: broad framing vs bounded evidence.** Lines 65, 91-101, and 127-139 frame "Scientific ML Surrogates"; lines 302-304 and 571-575 concede bounded case-study evidence. This tension must be resolved by title/abstract scoping or a stronger independence argument.
- **Major: evidence accumulation may mask the linchpin.** If C53 is not accepted by reviewers, much of the paper becomes an artifact discipline around an intuitive gate. Make C53 impossible to miss and easy to verify.
- **Major: sibling and generated artifacts may look like convenience evidence.** Lines 320, 329, 516, and 571 acknowledge sibling/read-only provenance. Keep these as breadth, not as central validation.

Observations:

- The paper is unusually honest. Its blocked-claim list at line 553 is a real strength.
- The current version is much more reviewable than a superiority-oriented version would be.

## Editorial Synthesis

Decision: **Major Revision**

Rationale:

All reviewers agree that the revised manuscript has a publishable core: numerical decidability as an admissibility/soundness criterion for SciML metamorphic testing. The strongest evidence is the operator-floor analysis (line 477) coupled with typed verdict changes across cylinder flow and airfoil (line 472). The paper is also unusually disciplined about claim boundaries (lines 302-304, 346, 367, 553, 571-575). However, all reviewers also converge on the same acceptance risk: the paper's broad SciML-surrogate framing still outruns the independent evidence base. The work should not be rejected as immature, because the central criterion, artifacts, and validation are real; but it is not yet a Minor Revision because reviewers will likely ask for a sharper scope statement, a clearer theorem box, and a denominator/effective-N table before they trust the claims.

Consensus:

- **CONSENSUS-5**: Central contribution is now clear and potentially TOSEM-relevant.
- **CONSENSUS-5**: General reliability, superiority, and real-world defect-rate claims are correctly blocked.
- **CONSENSUS-4**: External validity and denominator trust remain the main weakness.
- **CONSENSUS-4**: C53/the operator-floor theorem should be elevated visually and structurally.
- **CONSENSUS-3**: Practical adoption cost needs clearer treatment.

Disagreement:

- Reviewer 2 is more positive because the numerical V&V core is sound.
- Devil's Advocate is stricter because top-SE reviewers may judge contribution breadth, not only theorem correctness.
- Editor resolution: **Major Revision**, not Reject, because the weaknesses are fixable without redesigning the whole study.

## Required Revisions

| # | Revision item | Source | Severity | Estimated effort |
|---|---|---|---|---|
| R1 | Narrow the title/abstract/keywords or add a sharper scope sentence that prevents broad SciML-surrogate overreading | EIC, DA | Critical | 1-2 days |
| R2 | Add a theorem/proposition box for C53 with assumptions, bound, allowed claims, and forbidden claims | R2, DA | Critical | 2-4 days |
| R3 | Add a "nominal N / effective N / inference allowed" table for all evidence blocks | R1, EIC | Major | 2-3 days |
| R4 | Add a practitioner checklist showing how to apply the gate and what verdict/claim each branch licenses | R3 | Major | 1-2 days |
| R5 | Reorganize breadth evidence so each block states exactly what it falsifies: checklist-only reading, single-architecture artifact, or single-task artifact | EIC, R3, DA | Major | 2-4 days |

## Suggested Revisions

- Move the strongest blocked-claim list closer to the end of the introduction or keep a shorter version there.
- Add a small figure explaining absolute conservation deferral vs reference-relative diagnostic vs flux-form admissibility.
- De-emphasize LLM candidate generation unless it is necessary for the contribution; it can distract from the numerical-decidability core.
- Review all occurrences of broad phrases such as "SciML V&V" and ensure each is paired with the bounded-evidence scope.
- Keep the AI-use disclosure, but ensure the Zenodo package, claim ledger, scripts, and proof artifact are synchronized before submission.

## Revision Roadmap

Priority 1:

- R1: Decide whether to narrow the title or add a strong first-page scope boundary.
- R2: Insert C53 theorem box in the Method or Results section, with assumptions and non-claims.
- R3: Add effective-denominator table.

Priority 2:

- R4: Add practitioner gate checklist.
- R5: Tighten breadth evidence into a falsification map.

Priority 3:

- Reduce density in the introduction/results bridge.
- Fix remaining Underfull-heavy tables if visible in final PDF.
- Re-run LaTeX, validators, and claim-language scans after revision.

Overall verdict: **Major Revision with strong resubmission prospects**. The paper is no longer blocked by missing theory or confused positioning, but it still needs tighter scope control and reviewer-facing evidence organization before it can be considered a stable TOSEM submission.

