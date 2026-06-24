# Academic-Paper Plan -> Full Drafting Audit

> Date: 2026-06-05  
> Skill mode used: `academic-paper plan -> full`  
> Source edited: `submissions/IST/main.tex`  
> Figure policy: generated figures remain excluded; no figure was inserted into the manuscript.

## 1. Plan

The previous quality check identified one high-leverage writing task: make the method concrete enough that the manuscript reads as an executable method paper rather than a protocol. The plan for this pass was:

1. Add a worked-example subsection in the Method section.
2. Draft complete candidate-to-MR-card explanations for three relation types.
3. Narrow the empirical comparison promise in RQ4.
4. Recompile the IST LaTeX manuscript.
5. Track word count, terminology consistency, and argument-chain coherence.

## 2. Full Drafting Changes

### 2.1 Added worked examples

Added:

- `\subsection{Worked examples: from candidate relation to executable MR card}`
- `Table 3. Worked screening decisions for three candidate MRs`
- `MR-1: node permutation equivariance`
- `MR-2: mirror-y equivariance`
- `MR-3: discrete divergence boundedness`

The new section clarifies that the examples are design-time method examples, not empirical results. It shows how the rubric changes the status of candidate relations:

- node permutation is retained as an executable representation MR;
- mirror-y equivariance is retained only under boundary-compatible conditions;
- discrete divergence boundedness is treated as a qualified continuity-constraint MR whose verdict depends on operator and tolerance evidence.

### 2.2 Narrowed RQ4

RQ4 was revised to avoid overpromising. The current framing is:

- primary comparator: expert MR design;
- secondary contrasts: LLM candidates and generic MR-generation outputs;
- diagnostic evidence: rollout accuracy.

This keeps the comparison useful while reducing the risk of claiming that all comparator families are equally central or fully executable.

### 2.3 Updated baselines and RQ evidence map

The empirical design now states that expert MR design is the primary comparator. Generic MR-generation and LLM-assisted candidate generation are secondary candidate-source contrasts. Rollout accuracy is described as a diagnostic rather than as a competitor that MRs must defeat.

## 3. Word Count Tracking

| Checkpoint | Approximate stripped-source word count |
|---|---:|
| Before this drafting pass | 4206 |
| After this drafting pass | 5137 |
| Net change | +931 |

Interpretation:

- The added length is method-bearing rather than ornamental.
- The manuscript remains far below the usual IST upper bound for a regular paper.
- The next expansion should go to verified related-work contrast and empirical artifacts, not more abstract framing.

## 4. Compilation Status

Compilation command:

```sh
TEXMFVAR=/private/tmp/codex-texmf-var TEXMFCONFIG=/private/tmp/codex-texmf-config pdflatex -interaction=nonstopmode main.tex
```

Status:

- LaTeX compilation succeeded.
- Output PDF: `submissions/IST/main.pdf`
- Current PDF length: 24 pages.
- No figures are inserted in `main.tex`.

Remaining formatting warnings:

- Overfull/underfull boxes remain, mainly in dense tables and long technical terms.
- The new worked-decision table compiles, but it is typographically dense. It may need redesign after the text stabilizes.

## 5. Terminology Consistency

Preferred terms remain stable:

| Preferred term | Current status |
|---|---|
| `scientific machine learning (SciML)` | Stable. |
| `system under test (SUT)` | Stable. |
| `candidate MR` | Stable; used for unvalidated proposals. |
| `retained MR` | Stable; used only after rubric screening. |
| `domain-validity rubric` | Stable and central. |
| `NOETHER-informed` | Stable; NOETHER is not described as proof. |
| `executable MR asset` | Stable and strengthened by worked examples. |
| `relation-level verdict` | Stable. |
| `out-of-relation-domain` | Stable. |
| `rollout-accuracy diagnostic` | Updated from baseline language in the empirical design. |

Guardrail scan:

- No figure insertion commands were found in `main.tex`.
- NOETHER is still framed as candidate organization, not proof.
- LLM use remains candidate generation and material organization only.
- Divergence is framed as a continuity constraint, not as a Noether-derived conservation-law claim.
- The text still blocks empirical pass/fail and superiority claims.

## 6. Argument Chain Check

The current argument chain is more coherent than before:

1. SciML surrogates create an oracle problem for arbitrary transformed inputs.
2. Rollout accuracy is useful but does not specify relation-level physical consistency.
3. MT can supply oracle-free multi-execution checks.
4. In SciML, candidate MRs are unsafe unless their domain of validity is explicit.
5. The paper's contribution is the workflow from candidate relation to rubric decision to executable MR asset to relation-level verdict.
6. The worked examples now show that the rubric changes candidate status rather than merely listing questions.
7. The empirical design remains blocked until executable artifacts and run ledgers exist.

Coherence verdict: **improved and mostly coherent**.

Remaining weak links:

- The bibliography still contains several unverified 2025/2026 entries.
- The worked examples are prose-level executable descriptions; actual code/schema artifacts still need to exist.
- The Results section is still intentionally blocked.
- Tables need typographic cleanup before submission.

## 7. Next Writing Target

The next highest-value writing task is citation and related-work hardening:

1. Build a reference ledger for newer and closest papers.
2. Verify or downgrade uncertain entries.
3. Rewrite the closest-work contrast after metadata verification.
4. Then return to empirical artifact schemas and table cleanup.

Do not insert the current generated figures until they are redesigned from the strengthened method text.
