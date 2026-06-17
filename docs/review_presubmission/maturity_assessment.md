# Submission-maturity assessment — IST (2026-06-17, real multi-vendor gateway)

## How this was produced

- **Real multi-vendor gateway panel — RAN this session** (the deliverable that prior sessions could not run because the gateway key was exhausted). `tools/run_academic_review_panel.py` was executed twice, on two independent OpenAI-compatible gateways, each with **five distinct vendors**:
  - **EIC** = gpt-5.5 · **MethodologyRigor** = glm-5.1 · **DomainExpert** = deepseek-v4-flash · **Perspective** = qwen3-max · **DevilsAdvocate** = kimi-k2.6.
  - **v38** (user-provided OpenAI-compatible gateway this session) — records `research_assets/runs/academic-review-panel-v38/`.
  - **v37** (sibling bltcy gateway) — records `research_assets/runs/academic-review-panel-v37/`.
  - Both runs: 5/5 reviewers succeeded, zero failures, temperature 0.
- **deep-research literature assessment** via paper-search-mcp (dblp / arXiv / crossref / openalex / semantic), independently judging novelty and positioning against the real literature.
- **IST compliance scorecard** against the Guide-for-Authors hard requirements.
- **Honesty boundary:** these are temperature-0 single-call LLM reviews via gateways — an automated panel *estimate*, NOT a substitute for human peer review and NOT a prediction of an actual IST editorial decision. No manuscript (`main.tex`) edits were made; this is an evaluation.

## 1. IST compliance — 14/14 (desk-check clean)

| # | Requirement | Limit | Measured | OK |
|---|---|---|---|---|
| 1 | Body word count | ≤ 15,000 (refs+appendices+200/float) | **12,339** (headroom 2,661) | ✓ |
| 2 | Structured abstract sections | Context/Objective/Method/Results/Conclusion | all 5 present | ✓ |
| 3 | Abstract length | ≤ 300 words | 295 | ✓ |
| 4 | Highlights | 3–5 bullets, ≤85 chars each | 5 (75/80/75/76/67), separate file | ✓ |
| 5 | Keywords | 1–7 | 7 | ✓ |
| 6 | Title | required | present (7 words) | ✓ |
| 7 | Reference style | elsarticle-num (Vancouver) | elsarticle-num | ✓ |
| 8 | Document class | formal elsarticle (not free-form) | elsarticle [preprint,12pt] | ✓ |
| 9 | Single-anonymized → keep authors | NOT anonymized | 4 authors + 3 affiliations + corr. email | ✓ |
| 10 | CRediT statement | required | present | ✓ |
| 11 | Declaration of Competing Interest | required | present | ✓ |
| 12 | Generative-AI declaration | required | present | ✓ |
| 13 | Data availability | required | present (Zenodo concept DOI) | ✓ |
| 14 | Funding | declare | present (NSFC etc.) | ✓ |

→ Nothing a desk check looks at can block this submission.

## 2. Real gateway panel — cross-gateway + historical comparison

| Run | Gateway | Overall /10 | Accept-prob (range) | Clarity | Majority verdict | Distribution |
|---|---|---|---|---|---|---|
| **v38** | user gateway | **7.86** | **0.604** (0.30–0.85) | 7.0 | **major_revision** | 3 major / 2 minor |
| **v37** | bltcy (sibling) | **7.6** | **0.67** (0.45–0.85) | 6.8 | **minor_revision** | 2 major / 3 minor |
| v36 | bltcy (pre-E5, pre-bib-fix) | 7.37 | 0.664 | — | major_revision | 3 major / 2 minor |
| Claude council | simulated (5 Claude personas) | 7.0 | 0.478 | 5.8 | major_revision | 3 major / 2 minor |

Per-dimension means (the two real gateways agree within noise):

| Dimension | v38 | v37 |
|---|---|---|
| novelty_contribution | 7.4 | 7.0 |
| technical_soundness | 7.6 | 7.2 |
| empirical_rigor | 7.6 | 7.6 |
| related_work | 8.0 | 7.6 |
| **clarity** | **7.0** | **6.8** |
| reproducibility | 8.2 | 8.4 |
| scope_match_to_ist | 9.2 | 8.6 |

**The boundary story (quantitative).** Per-reviewer verdicts are stable across the two gateways for 4 of 5 reviewers:

| Reviewer (model) | v38 | v37 |
|---|---|---|
| EIC (gpt-5.5) | major (0.62) | major (0.55) |
| MethodologyRigor (glm-5.1) | minor (0.85) | minor (0.85) |
| **DomainExpert (deepseek-v4-flash)** | **major (0.40)** | **minor (0.65)** |
| Perspective (qwen3-max) | minor (0.85) | minor (0.85) |
| DevilsAdvocate (kimi-k2.6) | major (0.30) | major (0.45) |

The paper's overall verdict pivots on a **single borderline reviewer** (deepseek); the other four are gateway-invariant. Accept-probability means (0.604 / 0.67) straddle the minor/major threshold. This is the data-grounded meaning of "major-revision-ready / borderline": the manuscript sits *exactly* on the major↔minor line.

## 3. Consensus diagnosis (flagged by ≥3 reviewers, present in BOTH gateways)

1. **Validity–coverage duality risks reading as tautological / over-claimed for the evidence** — *every* reviewer, both runs. "Each admissible MR scores one invariant ⇒ coverage = admissible set" makes the duality near-definitional; only the cross-SUT keystone is a genuine empirical test, and it is n=2 CFD, fault-class-level, qualitative. **The #1 signal.**
2. **Density / clarity is the binding constraint** — EIC ("sprawling, mixes primary/supporting/secondary evidence, obscures the core"), MethodologyRigor ("extremely dense, heavily hedged"), DevilsAdvocate ("jargon-heavy, impedes IST's broad audience"). Clarity is the lowest/near-lowest dimension (6.8–7.0) in every panel ever run.
3. **Narrow empirical core + synthetic faults + under-trained airfoil** — two CFD tasks; the 10-mutant catalogue is author-implemented gross corruptions; the airfoil SUT is deliberately under-trained (rel L2 ≈ 1.0). Real-world fault-detection relevance "tenuous" (MethRigor); K=6 are same-family variants, not independent SUTs (DevilsAdvocate).
4. **The 2D verdict's domain-violation axis is not calibrated across MR classes** (deferred to future work) — DomainExpert, Perspective; weakens cross-MR interpretability of the duality.
5. **Novelty is incremental recombination; delineation vs Duque-Torres / Reichert / Eniser not fully sharp** — DomainExpert, DevilsAdvocate. (deep-research adds the specific uncited threat — see §4.)

Consistent strengths (both gateways): exemplary fail-closed reproducibility / claim-ledger discipline; the measurement-floor admissibility gate as the strongest novel atom; construct discrimination via the airfoil design; unusually honest scope/threats with a falsifiable central claim.

## 4. deep-research novelty / academic-level verdict

- **Novelty = incremental recombination + one genuinely-new atom.** The paper says so itself (§2.8), and the literature confirms it. The single most-defensible new atom: *grounding an MR's admissibility/tolerance in the intrinsic discretization-error floor (O(h) P1 divergence floor, closed-form, verified <0.5%) as an admit/defer gate.* A discretization-/round-off-tolerance search across crossref + arXiv found **no MT paper that gates MR admissibility by a measurement-operator error floor** — this atom is well-supported as new.
- **Biggest novelty threat (verified, and actionable):** the validity–coverage / predictable-coverage claim is the territory of the **Kanewala coverage cluster** — **Srinivasan & Kanewala 2022, STVR, MR prioritization (DOI 10.1002/stvr.1807)** and **Saha & Kanewala 2018/2019, MR fault-detection effectiveness (arXiv 1904.07348)**. Both verified real; **both verified ABSENT** from the 35-entry `references.bib`. A Reviewer 2 will ask why "which MR catches which fault / where the suite is blind" is not cited or contrasted.
  - (deep-research also tentatively flagged Olsen & Raunak's validity-titled TR and Lin/Simon/Niu hierarchical MRs as possibly missing — **bib verification shows both are already cited**; those were false alarms. `yang2020hierarchical` is the authors' own 《计算机科学》/北大核心 2020 paper, DOI 10.11896/jsjkx.200200015 — real, just not in crossref/dblp because it is a Chinese journal.)
- **Significance for IST:** borderline-to-above-bar (lower half of acceptable), appropriate for a regular paper. Strong venue fit (IST has a 2025 MT-of-ML precedent, Spieker et al. 188:107890). The limiter is scope (one-task core, qualitative duality, deferred cross-relation calibration) and the recombination-not-paradigm novelty — all candidly flagged by the paper.

## 5. Maturity verdict

**Mechanically submission-ready; scientifically on the major/minor-revision boundary.** Quantitatively: overall ≈ 7.6–7.9, accept-prob ≈ 0.60–0.67, verdict flips major↔minor across gateways on one reviewer. This is the **historical ceiling** (v18–v36 plateaued at ~7.4–7.8, clarity-bound); the recent P1–P5 revision round lifted clarity from the council's 5.8 to the gateway's 6.8–7.0 and moved the verdict from major-only baselines onto the boundary, but did **not** dislodge the top-3 consensus concerns, which are now at their structural floor. **No new blocker** appeared. The one genuinely new, cheap, on-point lever surfaced this session is the Kanewala citation gap (§4).

## 6. Prioritized options (revision choices, NOT blockers; no manuscript edits made)

> The prior round already executed: density surgery (C39/C40 → Appendix B), Spieker citations, OpenMC wording, precision/recall descriptive labeling, abstract duality softening. The items below are what the *real gateway panel + deep-research* add on top.

- **P0 — NEW, highest value/risk ratio.** Add the two verified-absent Kanewala coverage-cluster citations (Srinivasan & Kanewala 2022 STVR; Saha & Kanewala 2018/2019) to related work and **contrast them with the duality claim**. This simultaneously defuses consensus concern #1 (duality tautology) and #5 (novelty delineation) and closes the single biggest novelty threat deep-research found. Cheap, verified, directly on the binding concern.
- **P1 — soften the duality in the BODY** (the abstract was already softened to "consistent with"; the body still frames it as a principle/law). Restate it explicitly as a *hypothesized generalization, qualitatively supported on two CFD tasks*, since every reviewer in both gateways reads the current framing as the strongest over-claim.
- **P2 — density/clarity (binding constraint, diminishing returns).** Despite the appendix demotion, clarity remains the lowest dimension and "sprawling / mixes primary-supporting-secondary evidence" is a repeated concern. Consider consolidating the Results subsections and sharpening primary-vs-secondary separation. Historically the only dimension that moves the panel — but also at its floor.
- **P3 — bound the synthetic-fault evidence.** Explicitly bound the 10-mutant author-implemented catalogue's real-world applicability and keep detector precision/recall descriptive (consistent with the 180/180 grids).

These are revision choices. The paper *can* be submitted as-is and would draw major-or-minor revision — exactly what the two gateways straddle.
