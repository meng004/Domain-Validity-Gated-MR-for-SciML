# Reusable pre-submission checklist

Date extracted: 2026-07-07.

Purpose: reusable detection items, rules, and repair strategies for avoiding
editorial screening failures before journal submission.

Primary screening reference: Staron, Travassos, Russo, and Ghosh, "How not to
get your paper rejected -- From the editors' notebook", Information and
Software Technology 197 (2026) 108197, DOI 10.1016/j.infsof.2026.108197.
The local PDF used for this extraction is
`/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/venues/templates/IST/1-s2.0-S0950584926001862-main.pdf`.

Project-specific source rule: the authoritative manuscript source remains
`manuscript/`, especially `manuscript/main.tex`,
`manuscript/supplementary.tex`, and `manuscript/references.bib`.
Generated venue/upload packages under `submission/` are disposable
derivatives.

## 1. Editor-screening risk model

The IST editorial identifies recurring desk-rejection patterns. For this
checklist, the risks are operationalized as four pre-submission gates:

1. Low novelty or unclear contribution.
2. Unclear or misaligned scope.
3. Manuscript expression quality insufficient for reviewer assignment.
4. Premature or insufficient validation.

These are editor-screening gates, not ordinary reviewer preferences. A paper
can have technically correct details and still fail here if the abstract,
introduction, evidence design, and package do not let an editor quickly see
scope, novelty, readability, and validation maturity.

## 2. Gate A: low novelty or unclear contribution

### Detection items

- Abstract or introduction describes the tool/method itself but not the
  contribution to software engineering.
- Contribution is only a narrow extension, dataset-specific tweak, or
  implementation demonstration.
- Closest-prior comparison is delayed to the supplement or left implicit.
- Related work is a list of areas rather than a contrast against specific
  closest works.
- Novelty is expressed as "we apply X to Y" without explaining what advances
  software-engineering knowledge or practice.
- The paper claims a workflow, but the text does not identify the new decision
  rule, evidence boundary, or reviewer-relevant difference from prior work.

### Rules

- The main text must state what is new before the method details become dense.
- A paper about a method or tool must show how the method affects software
  engineering practice, evidence interpretation, testing decisions, or
  validation workflow.
- Closest-prior work must be cited and differentiated near where the novelty is
  claimed.
- The novelty sentence should be strong enough for an editor to reuse when
  selecting reviewers.

### Strategies

- Add or replace one hard positioning sentence in Section 2 or early Section 3.
  For this manuscript:
  "Existing work may constrain when an MR applies or relax an oracle tolerance;
  this work adds a prior admissibility requirement that the tolerance dominate
  the measuring operator's intrinsic numerical floor before any SUT-failure
  verdict is licensed."
- Use a closest-prior capability matrix in the supplement, but keep a compact
  main-text summary.
- Avoid presenting ledgers, scripts, or records as the novelty. They are
  implementation and audit mechanisms unless the argument shows why they change
  testing decisions.
- Prefer "what decision becomes possible" over "what artifact we built".

### Verification commands

```bash
rtk rg -n "closest prior|prior admissibility requirement|what none|gap addressed|contribution|adds" manuscript/main.tex manuscript/supplementary.tex
rtk rg -n "Reichert|Eniser|Duque-Torres|MetaTrimmer|NOETHER|MetaPattern|relaxation|operator-floor" manuscript/main.tex
```

## 3. Gate B: unclear or misaligned scope

### Detection items

- The abstract reads as applied science, domain modeling, or pure SciML rather
  than software-engineering testing/validation.
- The intended reader is not obvious: software engineers, AI engineers,
  testing researchers, or domain scientists.
- The manuscript applies software/AI to another domain without contributing to
  software-engineering technology, methods, or evidence practice.
- The target venue scope is only addressed in the cover letter, not visible in
  the abstract/introduction.
- The reviewer expertise needed is hard to infer from title, abstract, and
  first pages.

### Rules

- The paper must be framed as a software-engineering contribution in the
  abstract and first two pages.
- The problem statement must answer: why does this matter to software
  engineers or AI-system verification engineers?
- Domain examples may motivate the work, but the contribution must remain a
  method, evidence discipline, testing workflow, or validation technique for
  software systems.
- Non-claims must be clear enough to prevent wrong reviewer assignment.

### Strategies

- Use the title, abstract, introduction, and cover letter to repeat the same
  scope frame in different forms.
- In this manuscript, maintain the frame:
  "software V&V method for oracle-free testing of SciML surrogate software".
- Avoid recasting the paper as production CFD validation, general SciML
  reliability, model-performance benchmarking, or MR discovery.
- Put target-reader cues in the first paragraph:
  software testing, oracle problem, verification and validation, AI-enabled
  software, relation-level verdicts.

### Verification commands

```bash
rtk sed -n '80,160p' manuscript/main.tex
rtk rg -n "software|testing|verification|validation|oracle-free|V\\\\&V|software engineers|AI engineers|SciML surrogate" manuscript/main.tex venues/<venue>/cover_letter.md
rtk rg -n "production CFD|model-performance|reliability benchmark|defect-rate|MR-discovery|state-of-the-art accuracy" manuscript/main.tex venues/<venue>/cover_letter.md
```

## 4. Gate C: manuscript expression quality

### Detection items

- Abstract and introduction introduce too many specialist terms before the
  reader knows the problem.
- First pages contain sudden definitions, acronym clusters, or symbol-heavy
  claims.
- Abbreviations or symbols are used before they are expanded or defined.
- A table, figure, or proposition appears before the surrounding text explains
  why it is needed.
- Related terms are scattered across sections instead of being introduced as a
  group.
- Formatting defects distract from the argument: orphaned table captions,
  duplicated figure titles, large unexplained blank regions, unresolved
  citations, or overfull boxes.

### Rules

- Every abbreviation, symbol, table, figure, and specialized term follows the
  first-definition rule.
- Concept definitions belong in the method section unless they are essential
  to the abstract.
- A logically linked group of terms or symbols should be declared in one local
  section.
- Use one term for one concept. Do not preserve legacy terms merely because
  they existed in earlier drafts.
- Visual layout must be checked in the rendered PDF, not only in source text.

### Strategies

- Keep only necessary high-level terms in abstract/introduction.
- Define the five core concepts in Method:
  candidate relation, admissibility gate, numerical decidability, executable
  check, typed verdict.
- Remove or demote residual terms such as "MR card", visible evidence IDs, and
  internal migration labels.
- Render pages around problematic tables and figures before finalizing.
- Prefer replacing text over adding text when the main paper is close to a page
  limit.

### Verification commands

```bash
rtk rg -n "\\b(SUT|SciML|MR|MT|OOD|UQ|PINN|FNO|CFD|PDE|CPU|GPU|CI|P1|S4/S5|K)\\b" manuscript/main.tex manuscript/supplementary.tex
rtk rg -n "MR card|moved from the main text|placeholder|Reviewer-facing|Component coverage|Claim-to-evidence|Cross-program breadth|Secondary baselines|evidence appendices" manuscript/main.tex manuscript/supplementary.tex
rtk rg -n "\\bC[0-9]{1,3}\\b|\\bPC[0-9]{1,3}\\b|claim~C|evidence ID|claim ID" manuscript/main.tex manuscript/supplementary.tex
rtk rg -n "Overfull|undefined|Citation.*undefined|Rerun|There were undefined" submission/<venue_package_YYYYMMDD>/review/final_main.log
```

## 5. Gate D: premature or insufficient validation

### Detection items

- A method is evaluated on one or two convenient cases without explaining why
  that evidence is enough for the stated claim.
- The paper tests only against weak or outdated baselines.
- The validation does not include analytical, empirical, simulation, formal, or
  other evidence appropriate to the claim.
- Results are descriptive, but the conclusion sounds general or population
  level.
- The paper lacks threats to validity, inference permissions, reproducibility
  materials, or claim boundaries.
- Toy examples are presented as if they were production evidence.

### Rules

- Every claim must have an evidence type and a boundary.
- Bounded evidence is acceptable only when the claim is also bounded.
- Validation must be mature enough for a journal article: not merely a proof of
  concept unless the venue and article type support that framing.
- Statistical or empirical claims must match the sampling unit and independence
  structure.
- Replicability and transparency are part of validation maturity.

### Strategies

- Use an evidence-tier structure:
  primary, supporting, secondary, and stress-test evidence.
- Separate nominal counts from effective evidence units.
- Label descriptive counts as descriptive when cells are not independent.
- Keep baseline comparisons as "scope contrasts" unless a superiority study is
  actually present.
- Include claim-boundary tables in the supplement.
- Keep a blocked-claim list active:
  no production validation, no representative defect rate, no broad reliability
  rate, no baseline superiority, no arbitrary-mesh theorem, unless new evidence
  is added.

### Verification commands

```bash
rtk rg -n "primary|supporting|secondary|stress-test|bounded|claim boundary|inference permission|descriptive|Wilson|bootstrap|Wilcoxon|threats to validity" manuscript/main.tex manuscript/supplementary.tex
rtk rg -n "production validation|representative defect|real-world defect-detection rate|baseline superiority|broad reliability|arbitrary-mesh|state-of-the-art" manuscript/main.tex manuscript/supplementary.tex
rtk rg -n "claim-ledger.yml|manifest|metric ledger|run logs|replication package|data availability|code availability" manuscript/main.tex manuscript/supplementary.tex venues/<venue>/cover_letter.md
```

## 6. Reporting-guideline and transparency gate

### Detection items

- Missing data/code availability, competing-interest declaration, CRediT
  statement, AI-use declaration, funding statement, or reproducibility pointer.
- Methodology lacks enough detail for reviewers to judge design quality.
- Empirical sections omit demographics, experimental plan, threats to validity,
  datasets, scripts, metrics, or statistical methods where relevant.
- Supplement exists but is not referenced where evidence is needed.

### Rules

- The main paper must make the evidence logic reviewable.
- The supplement may carry detailed evidence, but the main paper must announce
  what is in it and why it matters.
- Reporting materials should be separate submission files when the venue asks
  for them.

### Strategies

- Maintain an open-science or reproducibility checklist in the package.
- Keep relation records, runners, metric ledgers, manifests, and claim ledgers
  visible as replication artifacts.
- Do not hide unsupported claims behind supplementary length.

### Verification commands

```bash
rtk ls -la submission/<venue_package_YYYYMMDD>
rtk rg -n "Data availability|Code availability|CRediT|Competing|Generative|AI|Funding|reproducibility|replication" manuscript/main.tex venues/<venue>/declarations.md venues/<venue>/cover_letter.md submission/<venue_package_YYYYMMDD>
```

## 7. Source-of-truth and package discipline

### Detection items

- Edits were made in generated `submission/` packages rather than
  `manuscript/`.
- `source/`, venue-specific copies, or old generated packages are accidentally
  treated as authoritative.
- `main.tex`, `supplementary.tex`, `references.bib`, or figures are copied
  inconsistently into the package.

### Rules

- `manuscript/` is the only paper source of truth.
- Generated venue packages are disposable derivatives.
- Package files should be regenerated after every source edit.

### Strategies

- Edit `manuscript/main.tex`, `manuscript/supplementary.tex`, or venue-template
  files as appropriate.
- Rebuild the target package.
- Verify that generated files contain the new text.

### Verification commands

```bash
rtk python venues/<venue>/build.py
rtk rg -n "target phrase" manuscript/main.tex submission/<venue_package_YYYYMMDD>/source/main.tex
rtk rg -n "target phrase" venues/<venue>/cover_letter.md submission/<venue_package_YYYYMMDD>/cover_letter.md
```

## 8. Citation and first-use discipline

### Detection items

- First use of a literature-derived idea, framework, model, conclusion, or
  claim without an immediate citation.
- Closest-prior comparison paragraphs rely only on citations in a previous
  paragraph.
- Abbreviations, symbols, tables, or figures are used before they are declared.

### Rules

- A cited work's idea must be cited where the idea is first used.
- Each named closest prior should carry a nearby citation in the comparison
  paragraph.
- First occurrence: full term plus abbreviation. Later occurrences may use the
  abbreviation.
- Tables should be announced in text before the table appears.

### Strategies

- Add citations by replacing existing wording when the paper is page-limited.
- Keep full comparison matrices in the supplement, with a main-text pointer.
- Define technical symbols locally before use; avoid abstract-level symbol
  detail unless essential.

### Verification commands

```bash
rtk rg -n "closest prior|Reichert|Eniser|Duque-Torres|MetaTrimmer|NOETHER|MetaPattern|prior admissibility requirement" manuscript/main.tex
rtk rg -n "Table~\\\\ref|Figure~\\\\ref|\\\\caption\\{|\\\\label\\{tab:|\\\\label\\{fig:" manuscript/main.tex manuscript/supplementary.tex
```

## 9. Terminology control and legacy-term removal

### Detection items

- Multiple names for one concept.
- Internal workflow traces remain in reader-facing text.
- Visible evidence IDs or claim IDs appear in the manuscript narrative.

### Rules

- Define only necessary concepts.
- Other labels should be implementation details, evidence records, relation
  records, or supplementary evidence.
- Claim/evidence IDs belong in internal ledgers and audit artifacts.

### Strategies

- Replace residual internal terms with reader-facing wording:
  "relation record", "supplementary evidence appendix", "evaluation design",
  "claim boundary", or "evidence table".
- Remove visible IDs if meaning, artifact type, claim boundary, and evidence
  status remain clear.

### Verification commands

```bash
rtk rg -n "MR card|moved from the main text|placeholder|Reviewer-facing|Component coverage|Claim-to-evidence|Cross-program breadth|Secondary baselines|evidence appendices" manuscript/main.tex manuscript/supplementary.tex
rtk rg -n "\\bC[0-9]{1,3}\\b|\\bPC[0-9]{1,3}\\b|claim~C|evidence ID|claim ID" manuscript/main.tex manuscript/supplementary.tex
```

## 10. Main/supplement division

### Detection items

- Appendix-like first-level sections remain in the main paper.
- Detailed evidence tables expand the main paper past the page target.
- Supplement sections have only one sentence because a table floated away.
- Supplement tables appear before they are introduced.

### Rules

- Main text carries the argument, compact result index, and key evidence
  boundaries.
- Supplement carries detailed evidence maps, closest-prior matrices,
  inference-permission tables, and extended evidence.
- Every supplement table should be introduced before it appears.

### Strategies

- Keep main evidence in compact tables and short interpretive paragraphs.
- Move full closest-prior and evaluation-design matrices to the supplement.
- Use one main-text pointer rather than appendix-like sections in the main
  paper.

### Verification commands

```bash
rtk rg -n "^\\\\section|^\\\\subsection|Table~A|Closest-prior|Evaluation design|moved from" manuscript/supplementary.tex
rtk rg -n "^\\\\section|Claim-to-evidence map|Cross-program breadth|Secondary baselines" manuscript/main.tex
```

## 11. Layout and visual PDF checks

### Detection items

- Table caption or header stranded at the bottom of a page.
- Large blank regions caused by floats.
- Figure title duplicated above a figure when caption already supplies it.
- Text, table, or figure overlap.

### Rules

- Layout defects must be verified visually.
- Page-count fixes should not create worse layout or push the paper over the
  target page count.

### Strategies

- Render relevant PDF pages to PNG.
- Inspect the affected page and adjacent page.
- Use local layout controls only when needed, such as `\newpage` before a table
  that otherwise splits badly.

### Verification commands

```bash
rtk mkdir -p tmp/pdfs
rtk pdftoppm -png -f 18 -l 19 -r 150 submission/<venue_package_YYYYMMDD>/main.pdf tmp/pdfs/main_table_check
rtk pdfinfo submission/<venue_package_YYYYMMDD>/main.pdf
```

## 12. Reviewer-style acceptance-risk audit

### Detection items

- Desk-reject risks: scope unclear, novelty hidden, validation insufficient,
  reporting incomplete.
- Major-revision risks: representative defect sampling demanded, production
  validation demanded, adoption cost questioned, conceptual density.
- Minor-revision risks: local definitions, citations, terminology, table layout,
  and supplement navigation.

### Rules

- Use `academic-paper-reviewer` as a review-only mode.
- Evaluate the gap to stable acceptance, not only whether the manuscript can be
  submitted.
- Separate "paper cannot claim this" from "paper should add this".

### Strategies

- Review from five roles:
  EIC/venue fit, methodology, software testing, domain/numerical, devil's
  advocate.
- Prefer response-strategy preparation over adding new experiments unless a
  real reviewer demands them.

### Evidence to inspect

- `manuscript/main.tex`
- `manuscript/supplementary.tex`
- venue cover letter and highlights
- generated `main.pdf` and `supplementary.pdf`
- `research_assets/experiments/claim-ledger.yml`
- generated package review logs

## 13. Generic verification bundle after any edit

```bash
rtk python venues/<venue>/build.py
rtk python tools/<venue>_precheck.py submission/<venue_package_YYYYMMDD>/source/main.tex
rtk python -m pytest tests/test_stage2p5_submission_readiness.py tests/test_stage4_revision_readiness.py tests/test_p0_submission_readiness.py -q
rtk pdfinfo submission/<venue_package_YYYYMMDD>/main.pdf
rtk pdfinfo submission/<venue_package_YYYYMMDD>/supplementary.pdf
rtk rg -n "Overfull|undefined|Citation.*undefined|Rerun|There were undefined" submission/<venue_package_YYYYMMDD>/review/final_main.log
```

## Appendix A. JSS-specific checks

JSS-specific material is kept here so that Sections 1-13 remain reusable for
other target journals.

### A1. JSS scope and evidence contract

- Current target: Journal of Systems and Software, regular paper.
- Frame as a software V&V/testing method paper for AI-enabled scientific
  software.
- Do not frame as a general SciML reliability benchmark.
- Keep author identities visible because the JSS package is single-anonymized.
- JSS-relevant contribution frame:
  "software V&V method", "oracle-free validation", "auditable relation
  records", "typed verdicts", "bounded executions", "claim boundaries".

### A2. JSS package compliance

#### Detection items

- Abstract over 250 words.
- Missing separate highlights file.
- Highlights not 3-5 bullets or over 85 characters each.
- Missing CRediT, competing-interest declaration, generative-AI declaration,
  data/code availability, author biographies, open-science checklist, or
  editable LaTeX source.
- `main.pdf` incorrectly includes supplementary or highlights.

#### Rules

- JSS main manuscript stays author-visible.
- Highlights are a separate editable file.
- Supplementary evidence is a separate file/PDF.
- Keep the main manuscript within JSS regular-paper page guidance when
  possible; current target is 36 single-column pages.

#### Verification commands

```bash
rtk python venues/jss/build.py
rtk python tools/precheck_jss.py submission/JSS_regular_YYYYMMDD/source/main.tex
rtk python -m pytest tests/test_stage2p5_submission_readiness.py tests/test_stage4_revision_readiness.py tests/test_jss_concept_density_repair.py tests/test_p0_submission_readiness.py -q
rtk pdfinfo submission/JSS_regular_YYYYMMDD/main.pdf
rtk pdfinfo submission/JSS_regular_YYYYMMDD/supplementary.pdf
rtk ls -la submission/JSS_regular_YYYYMMDD
```

### A3. JSS cover letter and highlights

#### Rules

- Cover letter should state:
  1. JSS software V&V/testing fit.
  2. Central contribution: admissibility-gated workflow.
  3. Analytical and empirical validation.
  4. Bounded evidence boundary.
  5. Package compliance and separate files.
- Highlights should be 3-5 concise bullets, each no more than 85 characters.

#### Strategies

- Explicitly rule out false readings:
  not MR discovery, not production CFD validation, not defect-rate study, not
  model-performance benchmarking, not baseline superiority.
- State that evidence supports bounded method utility and auditability, not
  production reliability or representative defect-detection rates.

#### Verification commands

```bash
rtk sed -n '1,160p' venues/jss/cover_letter.md
rtk sed -n '1,80p' venues/jss/highlights.txt
rtk rg -n "JSS software V&V method paper|production CFD validation|defect-rate|MR-discovery|bounded method utility" venues/jss/cover_letter.md submission/JSS_regular_YYYYMMDD/cover_letter.md
```

### A4. Current JSS posture after the 2026-07-07 edits

- Main manuscript: 36 pages.
- Supplementary evidence: 14 pages.
- JSS precheck: passes, with the expected warning that highlights are separate.
- Key targeted tests: pass.
- Final LaTeX log: no Overfull, unresolved citation, or undefined-reference
  warning.
