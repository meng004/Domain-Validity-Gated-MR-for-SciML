# IST submission-maturity synthesis — 2026-06-20

Three independent evidence streams on `paper/ist-submission/main.tex`
(commit `d8889e1`), for Elsevier Information and Software Technology regular track.

## Evidence streams

1. **Gateway review panel (5 real vendors, single-call, temperature 0)** via
   the configured OpenAI-compatible gateway (`OPENAI_BASE_URL`, kept in the
   gitignored `.env`) — `research_assets/runs/academic-review-panel-2026-06-20/review_panel_report.json`.
   - EIC `gpt-5.5` · MethodologyRigor `glm-5.2` · DomainExpert `deepseek-v4-pro`
     · Perspective `qwen3-max` · DevilsAdvocate `claude-opus-4-7`
     (`claude-opus-4-8` hard-429'd by the gateway on both token-ladder attempts;
     fell back to 4-7, the user-approved alternative).
2. **Deep-research literature positioning** — 6 paper-search angles (dblp /
   arxiv / semantic / crossref).
3. **Evidence-grounded reviewer panel (4 Claude-Opus personas)** reading the
   full submission + `claim-ledger.yml` + `README` evidence boundary + repo.

## Combined scorecard (9 reviewers, 1-10)

| Dimension | Gateway(5) | Grounded(4) | ALL(9) |
|---|---|---|---|
| scope_match_to_ist | 8.60 | 8.00 | **8.33** |
| technical_soundness | 7.60 | 7.50 | 7.56 |
| related_work | 7.40 | 7.75 | 7.56 |
| reproducibility | 7.60 | 7.50 | 7.56 |
| empirical_rigor | 7.20 | 6.50 | 6.89 |
| novelty_contribution | 7.00 | 6.50 | 6.78 |
| clarity | 7.20 | 6.00 | **6.67** |
| **Overall** | **7.51** | **7.11** | **7.33** |

- Accept probability: mean **0.598**, range 0.35–0.85.
- Verdicts: **4 major_revision + 5 minor_revision** (contested, leans minor).
- Prior Jun-08 panel (pre related-work fix): 7.51 / 0.54 / major-majority →
  acceptance odds have improved; novelty + clarity remain the drag.

## P0 — blocking (verifiable, fix before resubmission)

1. **Test suite is red: `pytest tests` = 12 failed / 360 passed** (verified
   2026-06-20). The repo's own "prose may only claim what the ledger licenses"
   invariant is broken: stale prose-pinning guards after the 2026-06-18
   `main.tex` rewrite (`test_phase8_*`, `test_phase9_*`, `test_stage4_*`,
   `test_p1/p2_*`, `test_phase4_clarity`, `test_validity_coverage_duality`).
   Either update the guards to the current wording or fix the prose; one guard
   (`test_stage4...overfull_boxes`) is a compile-output gate.
2. **`manuscript.md` (prose SSOT) vs `main.tex` (submission) have drifted** —
   markers present in one but not the other. Reconcile or add a diff-CI check.
3. **Front-matter overclaims body (converges across ~5 reviewers).**
   - Abstract L59: "these readings hold across the roster, further
     architectures, and PhysicsNeMo" + "same predicate transfers to PINN and
     FNO" reads as broader generalization than the body licenses.
   - Highlight 5 (L70): "K=6 rosters expose where MR detectors are structurally
     insensitive" states as established what the body demotes to a bounded,
     non-independent implication on author-built mutants.
   - Tighten both to the ledger's hedged wording ("applies unchanged to",
     "within-family", qualify PhysicsNeMo as smoke-subset).

## P1 — high-leverage (move verdict toward accept)

4. **Novelty defense / positioning.** Deep research: the *MR-identification*
   axis is HIGH overlap — do NOT frame "identification" as the contribution.
   Reframe pillar (1) as an admissibility/gating rubric. Add an explicit "MR
   identification is not our contribution" sentence and the must-cite gaps:
   Kanewala & Bieman 2014 (IST SLR — omitting an IST SLR on this exact topic is
   a near-certain objection); nuclear burnup numerical-MT line (Wang/Fu/Yang
   2021–22); Segura MR-template 2017 + MROP/MRP-family-tree; Yan & Zhu STVR
   2024; Stevens et al. MARS ICSE-NIER 2025; Mandrioli et al. TSE 2024
   (nearest neighbour); Kanewala 2016 STVR (MR prediction); Spieker et al. 2024
   (Wasserstein violation criterion); Kulshreshtha 2026 (FMU MT). Disclose the
   NOETHER + sibling SMS-preprint boundary to pre-empt salami-slicing.
5. **Clarity / density surgery** (lowest dimension, 6.67). Split the longest
   result sentences (L392/394/396/400/414/439) into verdict-first short
   sentences; add a "Terminology & verdict types" box at the Method start;
   lift per-result caveats into a `finding | denominator | what it licenses`
   table; raise Table 4 / A1 font from `\tiny` to ≥`\footnotesize`. Use the
   2,891-word headroom.
6. **Airfoil under-training threat.** The strongest discrimination evidence
   runs on a deliberately under-trained surrogate (median one-step rel-L2≈1.0).
   Separate the training-independent verdicts (node-perm admit, continuity
   physical-basis rejection, mirror-y boundary rejection) from the one
   quality-dependent diagnostic; ideally add a converged-checkpoint sanity run.
7. **Sharpen the affirmative, reusable contribution** (Intro + Conclusion):
   state precisely what a practitioner reuses beyond this case study; strengthen
   the measurement-floor result by sketching a general unstructured-mesh bound
   or adding one more mesh family to the operator-floor sweep.

## P2 — polish (non-blocking)

8. Demote the 34×/17× mirror-y-vs-accuracy figure to an order-of-magnitude
   statement (ratio of non-commensurable relative-L2 quantities).
9. Abstract headroom thin (297/300) — re-count after edits.
10. Keywords lean phrasey (7, at the cap); precision/recall reported to two
    decimals over non-independent cells — label descriptive.

## IST author-guide compliance — all 8 hard items PASS

Structured abstract (5 headings, 297w); highlights (5 bullets, ≤85 chars,
separate file); keywords (7); word count 12,109/15,000 (headroom 2,891);
elsarticle + elsarticle-num; single-anonymized (authors kept); CRediT +
competing-interest + GenAI declarations present. No compliance blocker.
