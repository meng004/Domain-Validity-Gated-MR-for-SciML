# IST Submission-Readiness Assessment

Date: 2026-06-08
Branch: `claude/trusting-curie-i2VHM`
Venue: Elsevier Information and Software Technology (IST), regular research-paper track.

## 1. Method

Objective, reproducible estimate of the manuscript's maturity, produced by a
**five-vendor LLM review panel** routed through the bltcy OpenAI-compatible
gateway (`tools/run_academic_review_panel.py`):

| Role | Model | Vendor |
|---|---|---|
| EIC | gpt-5.5 | OpenAI |
| MethodologyRigor | glm-5.1 | ZhipuAI |
| DomainExpert | deepseek-v4-flash | DeepSeek |
| Perspective | qwen3-max | Alibaba |
| DevilsAdvocate | kimi-k2.6 | Moonshot |

Each reviewer scores seven IST-standard dimensions (1–10), an accept
probability, a verdict, and free-text concerns/strengths at temperature 0. Raw
responses are committed at `research_assets/runs/academic-review-panel/`
(per-round snapshots in git history: v1 `47b6194`, v2 `5fff660`, v3 `0d4e15a`).

**This is an automated panel estimate, not human peer review and not a
prediction of an actual IST editorial decision.** It is used here to triangulate
weak points, not as a grade.

## 2. Scores across three rounds

Round v1 = after P1; v2 = after the continuous domain-violation score D;
v3 = after the generic-MR baseline + clarity/consistency pass.

| Dimension | v1 | v2 | v3 |
|---|---|---|---|
| Novelty / contribution | 6.6 | 6.8 | 6.6 |
| Technical soundness | 7.6 | 7.4 | 7.6 |
| Empirical rigor | 7.2 | 7.0 | 7.2 |
| Related work | 7.8 | 8.2 | 8.0 |
| Clarity | 6.6 | 6.6 | 6.2 |
| Reproducibility | 8.4 | 7.6 | 8.2 |
| Scope match to IST | 8.8 | 8.8 | 8.8 |
| **Overall (mean of dims)** | **7.57** | **7.49** | **7.51** |
| **Accept probability (mean)** | **0.59** | **0.55** | **0.54** |
| Accept-prob range | 0.38–0.85 | 0.35–0.85 | 0.30–0.85 |
| Panel majority verdict | minor_revision | major_revision | major_revision |

**Interpretation.** The score is flat within panel noise across three rounds
(~7.5/10, accept ~0.55, at the minor/major-revision boundary). The targeted
additions each addressed a specific reviewer point (novelty/related-work ticked
up when D and the generic-MR contrast landed) but did not move the aggregate,
because they also add length — clarity drifted 6.6 → 6.2. **The panel has
plateaued.** No reviewer in any round returned *reject*; no reviewer returned
*accept*.

## 3. Per-dimension diagnosis

- **Scope match to IST (8.8) — strongest, stable.** Unanimously judged a clean
  fit for IST's software-V&V / oracle-problem / metamorphic-testing remit.
- **Reproducibility (8.2) — strong.** "Exemplary": committed artifacts, sha256
  checkpoints, run manifests, metric ledgers, deterministic re-runs, fail-closed
  gates. One round dipped to 7.6 (panel noise; nothing was removed).
- **Related work (8.0) — good.** Positioning against Reichert, Eniser, and the
  Duque-Torres cluster is judged precise; the +0.2/+0.4 came after the
  reference-coverage pass (30 entries) and the cross-vendor framing.
- **Technical soundness (7.6) / Empirical rigor (7.2) — solid.** The
  admissibility predicate and the O(h) operator-floor calibration are repeatedly
  called genuinely novel and well-executed; honesty/claim-scoping is praised.
  Held back by narrow scope and small effective sample sizes.
- **Novelty (6.6) — weak.** Seen as partly incremental over prior MT
  admissibility/tolerance work; the lift is "a structured workflow + rubric."
- **Clarity (6.2) — weakest.** "Overlong, ledger-heavy, excessive hedging;
  identical caveats repeated 3–4 times." This is the one dimension a writing
  pass (not new results) can move, and it currently trends *down* because new
  bounded sub-results add length.

## 4. Convergent concerns (v3, reviewers raising each / 5)

| Concern | /5 | Tractable in-repo? |
|---|---|---|
| Baselines blocked / thin | **5** | Partly. generic-MR + LLM done; **expert-MR needs a human expert** — not fabricable. |
| Narrow scope / one architecture family | **4** | Partly. Two PINNs added (cross-family), but the panel discounts 2 bounded points; a **real second-family large-scale study needs compute/time**. |
| Overlong / hedged / ledger-heavy | **4** | **Yes** — a deletion-only writing pass (move claim-ledger table to an appendix, collapse repeated caveats to single occurrences). |
| Domain-violation axis only qualitative | **3** | **Largely addressed** in v2: continuous score D (0.00 symmetric / 0.51 real); cross-MR-class calibration remains future work. |
| Novelty incremental | 2 | Hard — a positioning/framing question, not a quick fix. |
| Small-n statistics (n=4 bootstrap) | 1 | Partly — effect sizes already foregrounded; more SUTs would help. |

## 5. Gap-closure list (what would move 0.55 → 0.65+)

**A. Doable in-repo, honest, no external input** (highest ROI remaining):
1. **Deletion-only clarity pass.** Move the claim-to-evidence table to an
   appendix; collapse the per-subsection scope disclaimers to one canonical
   "Still blocked" statement; trim restated numbers in §5.3/§5.6. Target −15%
   body. Directly attacks the 4/5 "overlong" concern and the 6.2 clarity floor.
   *Risk:* ~25 test-guarded marker strings live in those sections; must preserve
   each in `main.tex` + `manuscript.md`.

**B. Doable but needs compute/time:**
2. **A genuinely different second architecture family at scale** (not 2 PINN
   points): e.g. a Fourier-Neural-Operator surrogate with a multi-case
   evaluation, to convert the cross-family claim from "two bounded points" into
   a rate. Addresses the 4/5 "narrow scope" concern.

**C. Needs a human / out of scope for this agent:**
3. **Expert-MR baseline** — requires a domain expert to author MRs
   independently; cannot be fabricated under the repo's "实事求是" constraint.
   This is the single 5/5 concern and the main ceiling on the score.
4. **Repositioning for novelty** — an authorial decision about how hard to
   claim the admissibility-predicate + operator-floor contribution.

## 6. Bottom line

- **Maturity: Major/Minor-Revision-ready, accept probability ≈ 0.55.**
- **Out of the reject zone** (0/5 reject across three rounds); the foundations
  (IST scope fit, reproducibility, honest claim-scoping) are strong and stable.
- **Not yet a clean accept.** The binding limiters are structural: the blocked
  expert-MR baseline (5/5), single-architecture-family empirical scope (4/5),
  and length/hedging (4/5).
- The score has saturated against further incremental sub-results; the next real
  gains are a deletion-only clarity pass (in-repo) and the expert-MR baseline +
  a scaled second-family study (external input / compute).

Reproduce: `OPENAI_API_KEY=… OPENAI_BASE_URL=https://api.bltcy.ai/v1 python3
tools/run_academic_review_panel.py`.
