# Clarity / Density Revision Plan (v34-panel response)

> **Plan-first per user request.** Do NOT edit the manuscript until this plan is
> approved. Every prose edit is **dual-source**: it must land identically in
> BOTH `paper/manuscript.md` and `paper/ist-submission/main.tex`. After each
> phase: run the prose-guard tests + `tools/ist_wordcount.py` + a `pdflatex`
> clean-room compile.

**Goal:** Raise the simulated-panel *clarity* dimension (v33 6.8 / v34 6.6 —
lowest of seven, and the most-cited concern across both rounds) by reducing
self-referential jargon and nested-parenthetical density, **without** changing
any claim, removing any test-pinned token, or exceeding the Phase-4 clarity word
cap.

**Architecture:** Density *redistribution*, not addition. Three guard rails
bound every edit: (1) IST-counted body <= 11,800 words (current **11,520**, so
~**280** words of slack — `test_phase4_clarity_surgery`); (2) test-pinned tokens
kept verbatim; (3) both prose files stay in sync (several guards loop
`for text in (self.md, self.tex)`). Gloss-on-first-use spends a few words;
offset by trimming nested parentheticals so the **net delta stays <= 0**.

**Tech Stack:** Manual LaTeX/Markdown edits; `python3 tools/ist_wordcount.py`;
`python3 -m unittest` on the prose-guard modules; `pdflatex` x2 clean-room.

---

## Hard constraints (verified this session)

- **Word cap 11,800** (slack ~280). Whole-revision net delta must be <= +280;
  target <= 0 by leaning on parenthetical trims.
- **Pinned-verbatim tokens — do NOT rename/remove:**
  - `K=6` and `OOD-stress` (e.g. `test_phase12` asserts the literal string
    `"K=6 x 3 trajectories x 10 mirror-y OOD-stress grid"`).
  - Abstract Results/Conclusion must stay **digit-free** and keep the sentence
    `"Broader generalization is future work"` (`test_phase4`).
  - LLM-baseline counts (n=8 candidates, 7 panel-valid, Fleiss kappa 0.077,
    rater models glm-5.1/kimi-k2.6/deepseek-v4-flash) pinned by
    `test_p2_llm_baseline_report`.
  - Highlights: exactly 5 items, each <= 85 chars (`test_phase4`).
- **Dual-source sync:** `manuscript.md` + `main.tex`.
- **Guard tests to re-run after edits:** `test_phase4_clarity_surgery`,
  `test_phase8_novelty_clarity_revision`, `test_phase9_scope_and_framing_revision`,
  `test_phase12_primary_empirical_scope`, `test_p2_llm_baseline_report`,
  `test_phase6_submission_maturity_hard_gates`, then the full suite.

---

## Phase 1 — Safe glosses + parenthetical trims (no test edits) [recommended]

### Edit 1.1 — Spell out the OOD acronym at first use (abstract, ~L53)
- Before: `mirror-y is a bounded OOD-stress finding, not an admitted exact symmetry;`
- After:  `mirror-y is a bounded out-of-distribution (OOD) stress finding, not an admitted exact symmetry;`
- Pinned token `OOD-stress` preserved at all later uses; no digit added ->
  `test_phase4` abstract guard safe. **Delta ~ +3 words. Risk: low.**

### Edit 1.2 — Gloss K=6 at first body use (intro, ~L116)
- Before: `its K=6 roster over three official held-out trajectories`
- After:  `its K=6 checkpoint roster (six checkpoints) over three official held-out trajectories`
- Token `K=6` kept verbatim. **Delta ~ +2 words. Risk: low.**
- NOTE: confirm "six checkpoints" wording against the methods/ledger definition
  at edit time; do NOT invent how the six differ (seeds vs epochs).

### Edit 1.3 — Itemize the dense three-levels sentence (methods, ~L188)
- The single 6-parenthetical sentence
  (`Candidate MRs are read off ... three levels (physical-model,
  computational-model, code-model): equivariance (...); conservation (...);
  homogeneity/scaling (...); composition (...); and cross-implementation
  comparison (...)`) -> convert to a short `\begin{itemize}` (md: `-` bullets),
  one bullet per category, each parenthetical moved into its bullet.
- Rationale: poster child for the reviewers' "nested parenthetical scope
  boundaries obscure the core narrative." Roughly word-neutral; large
  readability gain. **Risk: MEDIUM** — preserve every factual clause and the
  `Sec.~\ref{subsec:operator-floor-sweep}` cross-ref; re-run `test_phase9` /
  `test_phase12` (may pin phrases in this region).

### Edit 1.4 — Split 2-3 more nested-parenthetical sentences (~L213, ~L269)
- Break each "...: clause; clause; (e.g. ...)" run-on into two plain sentences.
- Pure density reduction, **word-neutral to negative. Risk: low.**

**Phase 1 verification:** `ist_wordcount` total <= 11,800; the six guard modules
green; `pdflatex` 40 pp / 0 undefined; `git diff` shows only intended deltas in
both files.

---

## Phase 2 — Condense the LLM-baseline narrative (OPTIONAL, needs explicit OK)

- Targets ~L296 + ~L443 + ~L477: **keep the pinned numbers** (n=8, 7 valid,
  kappa 0.077, rater models, rejection/deferral counts) but cut framing
  verbosity into a tighter paragraph.
- Benefit: frees ~40-80 words (helps the cap) + cuts density + directly answers
  v34's "LLM baselines underdeveloped / distracting" concern (Perspective,
  DevilsAdvocate).
- **Risk: MEDIUM** — `test_p2_llm_baseline_report` reads the JSON artifact, not
  the prose, so trimming is safe *iff* the reported numbers stay identical;
  verify no other test greps the trimmed sentences before cutting.

---

## Out of scope (explicitly NOT doing)

- Renaming `K=6` / `OOD-stress` (test-pinned).
- Adding any new claim or evidence.
- Touching highlights (5 items, <= 85 chars, pinned).
- Em-dash (`---`) cleanup — separate humanizer task (CLAUDE.md S11.4.1).

---

## Phasing & checkpoints

1. **Phase 1** -> run guards -> show `git diff` of both files -> **checkpoint**
   (you approve before Phase 2).
2. **Phase 2** (only if approved) -> run guards.
3. Optional: re-run the gateway panel (v35) on the revised text to measure the
   clarity-dimension delta against v34's 6.6.

**Expected net effect:** clarity dimension up from ~6.6; word count flat or
down; zero claim/evidence change; all guard tests green.
