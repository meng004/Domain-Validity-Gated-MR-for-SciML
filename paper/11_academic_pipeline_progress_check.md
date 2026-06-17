# Academic Pipeline Progress Check

> Date: 2026-06-05  
> Target venue: Information and Software Technology  
> Checked source: `paper/ist-submission/main.tex`  
> Pipeline lens: research -> write -> integrity -> review -> revise -> final integrity -> finalize

## 1. Current Pipeline Stage

Current status: **Stage 2 WRITE is substantially underway, but not complete enough to enter Stage 2.5 INTEGRITY as a pass/fail gate.**

The paper has a coherent IST-format draft, a method-centered framing, a bibliography file, and three generated method figures. However, the empirical evidence package is not yet available. The Results section is correctly blocked. The paper should not proceed to external review simulation or final integrity verification until the evidence gates listed below are satisfied.

## 2. Stage Dashboard

| Pipeline stage | Status | Evidence |
|---|---|---|
| Stage 1 RESEARCH | Mostly complete for current draft | Research positioning, journal fit, Undermind related-work preparation, contribution framing, and DA-style necessity checks exist. |
| Stage 2 WRITE | In progress | IST LaTeX draft exists; structured abstract, introduction, related work, method, empirical design, threats, and conclusion scaffold exist. |
| Stage 2.5 INTEGRITY | Not ready | Some citations are explicitly marked for metadata verification; no empirical data ledger exists; Results are blocked. |
| Stage 3 REVIEW | Not ready | Reviewer simulation would be premature because empirical claims and evidence artifacts are absent. |
| Stage 4 REVISE | Not applicable yet | No completed review package. |
| Stage 4.5 FINAL INTEGRITY | Not ready | Requires verified references, verified data, reproducible artifacts, and final figures. |
| Stage 5 FINALIZE | Not ready | Submission package is a working draft, not an upload-ready package. |

## 3. Current Draft Metrics

| Item | Current status |
|---|---|
| LaTeX template | Elsevier `elsarticle` IST-format draft in place. |
| Current PDF | Builds successfully as `paper/ist-submission/main.pdf`. |
| PDF length | 21 pages. |
| Approximate word count | 4206 words from stripped LaTeX source. |
| References | 22 BibTeX entries. |
| Figures | 3 method figures generated as PDF + 300dpi PNG; not yet inserted into `main.tex`. |
| Result claims | Correctly blocked. |
| Compile errors | No fatal LaTeX errors, no LaTeX Error, no undefined citation warnings found in the latest log scan. |
| Formatting warnings | Overfull/underfull boxes remain, mainly from dense tables and long technical terms. |

## 4. Generated Figure Status

| Figure | Source | PDF | PNG | Status |
|---|---|---|---|---|
| Fig 1. Validity-gated MR testing workflow | `fig_1_validity_gated_workflow.mmd` | generated | 2352 x 2454, 300dpi | Ready for insertion after caption check. |
| Fig 2. Executable MR asset and verdict data flow | `fig_2_mr_asset_dataflow.mmd` | generated | 2352 x 2943, 300dpi | Ready for insertion after caption check. |
| Fig 3. MR hierarchy and interpretation protocol | `fig_3_mr_hierarchy.mmd` | generated, later dropped | 1758 x 3597, 300dpi | Not adopted; manuscript Fig 3 = fig_3_verdict_2d; source files removed 2026-06-17. |

Recommended insertion policy:

- Insert Fig 1 in `Method / Overview`.
- Insert Fig 2 in `MR card and executable asset format`.
- Insert Fig 3 in `Hierarchical interpretation protocol`, or move it to appendix if page pressure increases.
- Do not generate or insert result figures until real verdict ledgers and accuracy/MR joined data exist.

## 5. Integrity Gate Findings

### 5.1 Claims

Allowed claims:

- The paper proposes a domain-validity-gated MR workflow.
- NOETHER is used for candidate organization, not proof of validity.
- MR evidence complements rollout accuracy by asking a relation-level validation question.
- The empirical evaluation is planned over MeshGraphNets-family cylinder-flow SUTs.

Blocked claims:

- Any pass/fail rate.
- Any violation rate.
- Any fault-detection rate.
- Any superiority over baselines.
- Any localization accuracy.
- Any statement that one SUT is more reliable than another.

Current verdict: **claim discipline is good.**

### 5.2 Citations

The bibliography compiles, but it is not integrity-ready. Several entries still carry explicit metadata-verification notes, especially newer 2025/2026 papers. Before Stage 2.5 can pass, each such entry must be checked against publisher, DOI, proceedings, arXiv, or official metadata.

Current verdict: **citation integrity not yet passable.**

### 5.3 Data and Results

No executable MR ledger, SUT run log, verdict table, mutation/fault ledger, or accuracy/MR joined table is present in the manuscript package. This is acceptable for a writing-stage draft, but it blocks integrity and review stages.

Current verdict: **empirical evidence not yet available.**

### 5.4 Reproducibility

The manuscript states the right reproducibility requirements, but the runnable package is not yet complete. Required assets still include SUT commits, checkpoints, dataset provenance, adapter configs, seeds, MR cards, transformation code, runner logs, verdict ledgers, statistical scripts, and exclusion logs.

Current verdict: **reproducibility plan exists; reproducibility evidence is pending.**

## 6. Main Risks

1. **The method may still look too abstract** unless Fig 1--3 are inserted and 5--8 concrete MR cards are added.
2. **The Results section is appropriately blocked**, but the paper cannot be reviewed as a full empirical paper until real run artifacts exist.
3. **Citation metadata for recent work is the nearest scholarly integrity risk.**
4. **The generated figures are ready, but not yet integrated into LaTeX.**
5. **The current git working tree contains many untracked draft artifacts**, so a clean commit plan is needed before push/PR.

## 7. Recommended Next Stage

Recommended next action: **continue Stage 2 WRITE, not Stage 2.5 INTEGRITY.**

Concrete next steps:

1. Insert Fig 1--3 into `main.tex` with concise captions and `\label{fig:...}` references.
2. Add 5--8 concrete MR card examples, preferably in a table or appendix-like subsection.
3. Verify the 2025/2026 bibliography metadata and remove draft verification notes.
4. Create empty-but-typed CSV schemas for future result figures without dummy data.
5. Start or connect the executable MR asset work: SUT configs, transformations, runner logs, and verdict ledger.
6. Recompile and resolve the worst table-related overfull boxes.

Checkpoint decision:

- Proceeding to peer review now would be premature.
- Proceeding to citation/data integrity now would produce a fail report, which is useful only if the goal is to enumerate blockers.
- The best pipeline move is to finish the method manuscript assets and evidence schemas, then run integrity pre-review.
