# Academic Pipeline Quality Check

> Date: 2026-06-05  
> Source checked: `paper/ist-submission/main.tex`  
> Mode: academic-pipeline mid-stage quality check, with reviewer-style diagnosis  
> Figure policy for this check: **generated figures are held out and should not be inserted for now** because their design quality is not yet acceptable.

## 1. Overall Quality Verdict

Current manuscript quality: **promising but not review-ready**.

The paper has a defensible research position: it frames SciML MR identification as a validity-gated oracle-free testing problem rather than as a CFD, GNN, or generic MT paper. This is the right direction for IST. The draft also shows good claim discipline: empirical results are blocked, NOETHER is not overclaimed as a proof mechanism, and LLM use is limited to candidate generation and organization.

The main quality problem is that the paper is still closer to a **well-framed research plan** than a **complete method paper**. The manuscript states the right workflow, rubric, artifact format, and evaluation design, but it does not yet show enough concrete operational detail to convince an IST reviewer that the method is executable, reproducible, and non-trivial.

## 2. Pipeline Position

| Pipeline stage | Quality status | Comment |
|---|---|---|
| Stage 1 RESEARCH | Adequate for current writing | The positioning is coherent: oracle problem + physically grounded MR identification + MeshGraphNets cylinder-flow case. |
| Stage 2 WRITE | In progress | Draft structure exists, but method concreteness and evidence artifacts are insufficient. |
| Stage 2.5 INTEGRITY | Not ready | Citations and data cannot pass integrity checks yet. |
| Stage 3 REVIEW | Too early | A full review now would mainly repeat known blockers: no results, insufficient MR-card specificity, unverified references. |

Recommended pipeline action: **continue Stage 2 WRITE with targeted strengthening**, not peer review and not final integrity.

## 3. Quality Scores

| Dimension | Score | Diagnosis |
|---|---:|---|
| IST fit | 4 / 5 | Strong if kept as software testing / V&V method paper. Weakens if it drifts into CFD or general SciML claims. |
| Research question clarity | 4 / 5 | RQ0--RQ4 are coherent, but RQ4 may be too broad before evidence exists. |
| Novelty positioning | 3 / 5 | Good "not first physics MT" humility. Needs sharper contrast with closest Qi/Yu-style work and simulation V&V. |
| Method specificity | 2.5 / 5 | Rubric and MR asset format are named, but examples are still skeletal. Needs concrete MR cards. |
| Empirical design | 3 / 5 | SUTs, baselines, parameters, and stats are listed. Feasibility and data schema are not yet demonstrated. |
| Evidence strength | 1.5 / 5 | Results are correctly blocked, but this means the manuscript cannot yet support empirical claims. |
| Related work | 2.5 / 5 | The structure is good, but several newer citations remain unverified. |
| Writing quality | 3.5 / 5 | Generally clear and controlled. Some sections still sound like proposal language. |
| Figure readiness | 1.5 / 5 | Generated figures should be treated as exploratory drafts only; do not insert yet. |
| Submission readiness | 2 / 5 | Template compiles, but scholarly and empirical gates are not ready. |

## 4. Major Quality Issues

### Issue 1: The paper still reads like a protocol rather than a completed method paper

The draft repeatedly says what the method will do: planned SUTs, planned baselines, planned metrics, planned results, planned reproducibility. This is honest, but it also means the current manuscript cannot yet function as a complete IST empirical paper.

Minimum fix:

- Add a concrete method walkthrough using 2--3 MR examples.
- Show how one candidate relation moves through: source -> NOETHER-informed organization -> rubric decision -> MR card -> executable asset -> verdict logic.
- Keep Results blocked, but make Method executable enough that it does not feel aspirational.

### Issue 2: The rubric is plausible but under-operationalized

The domain-validity rubric is the headline contribution, but the current table is still a checklist of questions. IST reviewers will ask whether the rubric changes decisions or merely names what experts already do.

Minimum fix:

- Add accepted, rejected, deferred, and OOD-stress examples.
- For each example, show which rubric criterion determines the decision.
- Include at least one non-trivial rejection, such as time reversal for viscous cylinder flow, and one qualified relation, such as Reynolds--Strouhal similarity.

### Issue 3: MR cards are too skeletal

Table 2 says what evidence is needed, but it does not yet show a full MR card. The claimed contribution is "executable MR assets"; therefore one full card must appear in the paper.

Minimum fix:

- Add 3 full MR cards in the main text or appendix-like subsection:
  - node permutation equivariance;
  - mirror-y equivariance under boundary-compatible conditions;
  - discrete divergence boundedness as a continuity constraint.
- Each card should include transformation, preconditions, output mapping, metric, tolerance provenance, exclusion rule, and verdict interpretation.

### Issue 4: Related work is structurally good but not integrity-ready

The paper properly avoids claiming to be the first physics-based MT paper for learned physical predictors. However, the closest-paper comparison still depends on references that are not fully verified.

Current explicit citation risks:

- `hiremath2021ocean` has incomplete metadata.
- `mandrioli2025cps` is marked early-access metadata to verify.
- `qi2025physicalfield` is based on the Undermind report and needs venue verification.
- `baral2025xrepit` and `wang2025deeponetfe` are marked as preprint or metadata-to-verify.

Minimum fix:

- Create a reference ledger with DOI/source/status.
- Remove or downgrade any paper that cannot be verified.
- Rewrite the "closest studies" paragraph only after metadata is checked.

### Issue 5: RQ4 may overpromise

RQ4 asks how retained MRs compare with expert MRs, generic generation, LLM candidates, and rollout accuracy across three SUTs. That is a lot for one paper, especially when current experiments are not yet available.

Minimum fix:

- Split comparison claims into primary and secondary:
  - Primary: retained MR workflow vs expert/manual MR process.
  - Secondary: LLM/generic generation as candidate-source contrast.
  - Diagnostic: rollout accuracy as complementary evidence, not a competitor.
- Make fault-detection claims conditional on seeded faults actually being run.

### Issue 6: Figures are not ready

The generated figures are currently not good enough to insert. The problem is not only aesthetics; some layouts risk compressing the argument into boxes without clarifying the methodological novelty.

Decision:

- Do not insert Fig 1--3 now.
- Keep figure files as exploratory drafts.
- Redesign later from the strengthened method text, not from the current abstract workflow.

## 5. Strengths Worth Keeping

1. **Good claim discipline.** The draft clearly blocks empirical results and avoids fake pass/fail evidence.
2. **Good positioning.** The novelty is framed as validity-gated MR identification and executable MR assets, not "first physics MR".
3. **Good boundary control.** NOETHER, LLMs, rollout accuracy, and residuals are each given bounded roles.
4. **Good journal direction.** IST is plausible if the final paper has enough empirical validation and reproducibility evidence.
5. **Good ethics/reproducibility awareness.** The paper already states ledger, prompt, artifact, and licensing expectations.

## 6. Quality Upgrade Plan

### Pass 1: Make the method concrete

Target output:

- A new subsection: "Worked Example: From Candidate Relation to Executable MR Card".
- 3 complete MR cards.
- A short rejected/deferred candidate table.

Expected effect:

- Raises Method specificity from 2.5 to about 3.5/5.
- Makes the paper feel less like a protocol.

### Pass 2: Clean related work and citation integrity

Target output:

- Reference ledger.
- Verified closest-work table.
- Revised related-work paragraph comparing this paper with Qi/Yu/Gopakumar/Mandrioli only where metadata is confirmed.

Expected effect:

- Reduces integrity risk before Stage 2.5.

### Pass 3: Narrow the empirical promise

Target output:

- Recast RQ4 into a feasible primary/secondary comparison structure.
- Add typed schemas for future ledgers without dummy data.
- Keep seeded-fault claims explicitly conditional.

Expected effect:

- Reduces overpromise and review risk.

### Pass 4: Redesign figures after method strengthening

Target output:

- One high-quality method figure only after the worked example is written.
- Optional result figures only from real data.

Expected effect:

- Avoids inserting weak diagrams that dilute the argument.

## 7. Readiness Decision

Current decision: **Stage 2 continue / quality revision required.**

Do not proceed to:

- formal peer review simulation;
- final integrity verification;
- figure insertion;
- submission packaging.

Proceed to:

- method concretization;
- citation verification;
- MR-card examples;
- evidence schema preparation;
- later figure redesign.

## 8. Immediate Next Task

The highest-leverage next task is:

> Write a worked example that takes one non-trivial candidate MR through the rubric and produces a complete executable MR card.

Recommended first worked example:

> Mirror-y equivariance for cylinder flow, because it forces the paper to handle physical basis, boundary labels, vector-component mapping, mesh transformation, metric, tolerance, and exclusion rules.

Second example:

> Node permutation equivariance, because it is clearly executable and shows representation-level testing rather than physics-only reasoning.

Third example:

> Discrete divergence boundedness, explicitly framed as a continuity constraint rather than a Noether-derived conservation law.
