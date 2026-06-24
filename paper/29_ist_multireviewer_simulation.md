# Stage 9 — IST Multi-Reviewer Simulation (Opus 4.7)

Date: 2026-06-07
Method: Four parallel Opus-4.7 subagents, each instructed to play one of the
four roles a real IST regular-track review cycle assembles. Each agent read the
manuscript, ledgers, and run artifacts **independently** (no cross-talk) and
returned a structured report. The four reports were then merged into the
meta-review below.

Inputs each reviewer saw:
- `submissions/IST/main.tex` (the submission as of commit `c92533d`)
- `CLAUDE.md` and `paper/28_ist_format_compliance_check.md` (IST hard
  requirements, word budget, etc.)
- `research_assets/experiments/claim-ledger.yml` (C1–C13)
- `research_assets/runs/` ledgers and raw outputs

---

## 1. Verdict at a glance

| Reviewer | Role | Recommendation |
|---|---|---|
| Action Editor | scope / format / IST hard compliance | **Send out, but pre-review revisions needed** |
| Reviewer #1 | Empirical SE methodology (Verdecchia / Wohlin standard) | **Major Revision (borderline)** |
| Reviewer #2 | Domain expert in MT and SciML V&V | **Major Revision** |
| Reviewer #3 | Replication & Open Science | **Minor Revision** (no integrity red lines) |

**Meta-decision (3 of 4 lean Major):** **Major Revision**. The replication
discipline is unusually strong (R3 calls the claim ledger an exemplar); the
methodological framing and external validity are the bottleneck.

---

## 2. Consensus hot spots (≥ 2 reviewers independently flagged)

These are the issues no single-reviewer round would let slide:

1. **External validity is the central weakness** — Action Editor flags it via
   the abstract Conclusion's four "not" claims (self-disclosure of narrow
   scope); Reviewer #1 calls it a "fatal threat" (M1: K=6 same architecture
   family, one dataset, S0–S3 sharing data and trainer); Reviewer #2 says
   §1 ("SciML surrogates") oversells what the case study supports (M5).
2. **The "domain-validity rubric" novelty is overstated** — Reviewer #2
   (M1) shows the six rubric items are largely covered by Kanewala 2019 /
   Lin 2020 / Olsen 2019; Action Editor (item 5) recommends rewriting the
   Conclusion away from over-claiming. The only **genuinely new** ingredient
   is the operator-floor-grounded tolerance gate.
3. **The real headline finding has the wrong framing** — Reviewer #2
   states explicitly that §5.5 (operator-floor O(h) calibration, slope
   0.988, R²=1.000) and §5.6/R3 (non-monotone detection of PC_zero_vy
   because uniform $v_y=0$ is itself mirror-y-symmetric) are the most
   transferable insights, not the rubric. Reviewer #1 (m3) and Action
   Editor (Highlights point) agree at least that the abstract/Highlights
   under-promote what the empirical work actually achieved.
4. **The claim-ledger system is a top-decile strength but invisible to
   readers** — Reviewer #1 (Section IV: "top 10% of IST submissions") and
   Reviewer #3 (top of Section II: "no other IST paper I've seen has this
   structured ledger") both say so. The Abstract and Highlights never
   mention it.
5. **Baselines are essentially absent** — Reviewer #1 (M2): three of four
   planned comparators are still `blocked`; Reviewer #2 (concept review:
   the rubric vs. expert-MR-baseline contrast is unobserved). Reviewer #1
   recommends at least a minimal LLM-candidate baseline before submission.

---

## 3. Hard issues, ranked by priority

### P0 — Must fix before submitting (otherwise Editorial Manager rejects)

| # | Issue | Source | Fix |
|---|---|---|---|
| P0-1 | IST word total ≈ 16,779 (cap 15,000). Hard auto-check at submission. | AE, compliance doc | Trim Background (-600), Empirical Design (-700), consolidate Tables 5.4–5.6 (-800). Plan already in `28_ist_format_compliance_check.md`. |
| P0-2 | Manuscript is currently *named*, not anonymous. IST regular track defaults to double-anonymous. Authors, emails, affiliations, and grant numbers are all present. | AE (FAIL row) | Switch to anonymous version: replace author/affiliation block, CRediT, and grant numbers with `[anonymized]` placeholders; keep a `named-camera-ready` branch. |
| P0-3 | Title is 107 chars and noun-stacked. Hurts EM auto-reviewer assignment and Google Scholar indexing. | AE (item 3) | Shorten to ≤70 chars, e.g. "Domain-Validity-Gated Metamorphic Testing for Scientific ML Surrogates". |

### P1 — Strongly recommended before sending out for review

| # | Issue | Source | Fix |
|---|---|---|---|
| P1-1 | Abstract Conclusion broadcasts four "not" claims at the EIC. | AE (item 4) | Reframe as scoped positive: "...within one MeshGraphNets architecture family on cylinder flow; broader generalization is left to future work." Stay within ledger `wording_forbidden`. |
| P1-2 | The Highlights miss the two strongest empirical findings (operator-floor calibration; R3 non-monotone detection). | AE (item 5), R2 (Sec IV) | Replace one Highlight to "MRs localize 5/10 seeded faults by class" or "MR severity sweep reveals a fault hiding in its own symmetry." |
| P1-3 | "Conservation MR" is misnamed; it is a non-regression diagnostic. | R2 (M4) | Rename in §5.2 Table 3 to `PC5-conservation-NON-REGRESSION-diagnostic`; tighten the §1 / abstract phrasing. |
| P1-4 | Node-permutation V = 0 is by-construction GNN equivariance, not a model achievement. Currently listed alongside two model-level MRs in §5.7. | R2 (M3) | Tag node-perm in §5.7 / Table 4 as "pipeline-implementation sanity, not a model-level diagnostic". |
| P1-5 | The claim-ledger system never appears in Abstract or Highlights. | R1 (Section IV), R3 (Section V) | Add one sentence to Abstract Method ("...with a structured claim ledger that binds every numerical result to a tracked artifact") and one Highlight entry. |
| P1-6 | No effect size (Cliff's δ) and no non-parametric test (Wilcoxon / Mann-Whitney) on the multi-checkpoint and severity-sweep comparisons. | R1 (M3) | Add Cliff's δ + Wilcoxon to §5.4 and §5.7; declare in §4.4. |
| P1-7 | Operator-floor slope is reported as "0.988 / R²=1.000" with no SE / CI on the slope. | R1 (m3) | Add a jackknife or bootstrap CI on the slope. |
| P1-8 | "2D verdict reading" places P3 in the SUT-inconsistency region from a *qualitative* domain axis, but §6.1 then uses that placement to "remove the OOD objection". | R2 (M2) | Either provide a minimum continuous domain-violation score (operator admissibility + bijection error + BC-label mismatch fraction) or downgrade the claim to "structural verification by construction". |
| P1-9 | S0 reuses the original pilot checkpoint, not a freshly trained one. K=6 is closer to K=5+1. | R3 (Section II, condition pass) | Disclose this explicitly in §4.6 or §5.4. |

### P2 — Major-Revision-cycle items (after submission, given a revise verdict)

| # | Issue | Source | Fix |
|---|---|---|---|
| P2-1 | One cross-family pilot SUT (FNO or PINN on cylinder flow). | R1 (M1), R2 (M5) | Even a negative result reduces external-validity pressure substantially. |
| P2-2 | At least one head-to-head baseline (e.g., LLM-assisted MR candidate generation), even if minimal. | R1 (M2) | Run a 2-vendor × 3-temperature LLM probe → rubric-rate the candidates → compare retention rate. |
| P2-3 | Adversarial mutant catalogue (≥ 10 mutants targeting MR-specific thresholds, e.g. subtle weight perturbations). | R1 (M4), R2 (M4 + implied) | Removes the experimenter-bias hole on construct validity. |
| P2-4 | Per-pilot details for R3 PC_zero_vy non-monotone: fill in p ∈ {0.85, 0.9, 0.95, 0.99}. | R1 (M5) | Confirms step vs. continuous transition. |
| P2-5 | Re-center the manuscript: operator-floor calibration + R3 non-monotone as the headline contributions; the rubric becomes "systematic packaging of established SciML MT criteria, with one SciML-specific gate (operator-floor tolerance)". | R2 (Section IV) | Major reframing of §1, §3, §6, §7. |
| P2-6 | Coverage gap in Related Work: Saha & Kanewala 2018, Kanewala et al. 2016 graph-kernel MR prediction, Chen 2018 CSUR survey, Wang 2021 (PINN failure modes), Mandrioli 2025 CPS deeper. | R2 (Section V) | Add ~5 references; rebalance §2 to keep word count flat. |

### P3 — Light editorial / submission packaging

| # | Issue | Source | Fix |
|---|---|---|---|
| P3-1 | Data availability section lacks DOI / archive / license. | R3 (Section III item 2) | Add "the replication package will be deposited at Zenodo under CC-BY-4.0 (code MIT) upon acceptance; DOI to be assigned." |
| P3-2 | Hardware envelope not reported. | R3 (M1) | One sentence in §4.6: CPU-only PyTorch 2.12, ~N CPU-min per checkpoint, total CPU-hours. |
| P3-3 | Minimum-MR-SubSet SHA dependency not stated in main.tex. | R3 (M3) | Add SUT-repo commit `8c0b7ef` next to Data availability. |
| P3-4 | Highlights line 2 is at 78 chars (near the 85-char limit); keywords are at the 7-keyword ceiling. | AE (item 1, 4) | Re-edit; consider dropping "neural surrogates" or "MeshGraphNets". |
| P3-5 | Worked-examples in §3.5 may be read as empirical results. | R1 (m5) | Add "These examples were drafted *before* the experiments of §5." |

---

## 4. Per-reviewer summaries

### Action Editor
"Send out, but pre-review revisions needed." Scope fits IST (regular track has
accepted SE × testing × SciML papers in 2023–2025; JSS is the only comparable
backup; TOSEM and EMSE are riskier). Every IST format requirement passes
except the **word count (over by 1,779)** and the **anonymization state
(currently named)** — both are hard blockers at Editorial Manager.

### Reviewer #1 — Empirical SE Methodology
"Major Revision, borderline." Methodological transparency (claim ledger,
honest scope, no over-claim) is in the **top decile** of IST submissions, but
empirical breadth (single family + single dataset + 3-of-4 baselines blocked +
no effect size) is in the **bottom third**. Two minimum-viable additions
(LLM-candidate baseline + one contrast SUT family) would push the verdict
from borderline to accept.

### Reviewer #2 — Domain expert (MT / SciML V&V)
"Major Revision." The rubric is largely a systematic re-packaging of existing
SciML-MT checklists; the operator-floor-tolerance gate and the R3 non-monotone
detection finding are the genuinely new contributions, and the manuscript
should be re-centered around them. Conservation MR is misnamed (it is a
non-regression guard, not a conservation check). Eight references missing
in §2 (Saha & Kanewala, Kanewala graph-kernel, Chen 2018 CSUR, Wang 2021,
Mandrioli 2025 deeper, etc.).

### Reviewer #3 — Replication & Open Science
"Minor Revision, no integrity red lines." Three ACM badges (Available,
Functional, Reusable) are within reach; Reproducible badge is blocked only
by the missing hardware envelope and the unannounced Zenodo DOI. Claim-ledger
system is **better than every other IST paper this reviewer has seen** and
should be promoted from "hidden plumbing" to "named contribution" in the
Abstract.

---

## 5. Two viable paths forward

**Path A — Major-revise then resubmit IST (5–8 weeks).**
Do all P0 + all P1 + at least P2-1, P2-2, P2-5. Predicted post-revision
verdict: borderline accept (Accept probability 25–40 %).

**Path B — Repackage for JSS (1–2 weeks).**
Do P0 + P1 only. JSS is friendlier to single-deep-case-study + SciML, and the
external-validity bar is materially lower. Predicted JSS verdict: Minor
Revision (Accept probability 55–70 %). The four "not" Conclusion lines and
the "single architecture family" honest-scope framing are read very
differently at JSS than at IST.

**Path C — Hybrid (3–4 weeks).**
Do P0 + P1 + P2-2 (LLM-candidate baseline) + P2-5 (re-centering), then send
to JSS. Captures most of A's defensive value without the cost of A1
(cross-family pilot).

---

## 6. Standing constraints honored

- STVR remains excluded (`stvr不考虑`).
- `Minimum-MR-SubSet` remained read-only throughout the simulation; no
  reviewer touched the SUT repo.
- Every numerical claim cited above is traceable to a manuscript line number,
  a claim-ledger entry, or a `research_assets/runs/` artifact.
