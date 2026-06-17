# 44 — Academic-level & IST-gap Assessment + Proofread

> Date: 2026-06-17 · Methods: deep research (paper-search-mcp over IST + the MT/SciML
> literature) + academic-pipeline proofread (§11.3/§11.4). Subject: the post-phase-22
> manuscript (validity–coverage duality central thesis). Companion to paper/41 (review),
> paper/42 (responses), paper/43 (§15 audit).

## Part A — Deep-research: academic level and the gap to IST

### A.1 The IST bar (calibrated from recent IST testing papers, 2025–2026)
Recent IST (ISSN 0950-5849) testing/MT/ML papers: DL-library fuzzing with runtime
coverage feedback (108195); fault-tolerant online model-based testing with an
**industrial case study** (108149); an **empirical** LLM software-compliance-testing
study (108215); MT for ML credit-score models (Ying 2025, 107903); an
architecture-based-testing SLR (108206). Profile: testing-method or empirical papers,
frequently carrying an industrial case study, multiple systems, or statistical rigor;
MT-for-ML is an active IST topic. Single/dual case-study evaluation is itself defensible
in SE (Al-Ahmad et al. 2023, ESJ).

### A.2 Where this paper sits
**At or above the IST bar:**
- **Conceptual ambition.** The validity–coverage duality is a genuine organizing
  principle stated as a *falsifiable* thesis — more ambitious than the typical IST
  framework/empirical testing paper.
- **Reproducibility.** Claim-ledger SSOT + fail-closed validators + 352 regression
  guards + Zenodo concept DOI — well above the IST median.
- **Breadth of subjects.** Real SUTs across families (MeshGraphNet, PointMLP,
  PhysicsNeMo, PINN, FNO) including a production framework (PhysicsNeMo).
- **Honesty + a stated refutation surface** — rare and valued.

**At or below the IST bar (the gap):**
1. **Empirical breadth.** One primary case study (cylinder flow) + airfoil + cross-family
   transfer. Defensible (Al-Ahmad 2023), but IST method papers often have more systems
   or an industrial case study; the duality "principle" rests on two CFD SUTs.
2. **No comparative evaluation.** The paper positions against accuracy/UQ/residual
   baselines but does not empirically compare detection power against them. IST reviewers
   commonly expect a comparison.
3. **n-limited pilots.** The seeded-fault by-class pilot is one SUT/checkpoint with small
   denominators (0/6 cells, wide Wilson CIs).
4. **One missed related work.** Tsigkanos, Rani, Müller, Kehrer, "Variable Discovery with
   LLMs for Metamorphic Testing of Scientific Software," ICCS 2023
   (10.1007/978-3-031-35995-8_23, ~16 cites) — directly adjacent to the paper's own
   LLM-MR baseline, currently uncited.

### A.3 Novelty gap — confirmed
A 2024–2026 search for metamorphic testing of neural-PDE / physics surrogates returns no
direct competitor; the duality is not scooped. The "first end-to-end validity-gated
metamorphic-testing pipeline for physics-governed SciML" claim holds.

### A.4 Academic-level verdict
A solid, conceptually distinctive, exceptionally reproducible V&V method paper. The
duality reframe lifts it from "a useful workflow" to "a principle with a falsifiable
claim." Realistic IST outcome: **competitive, most likely major revision**, with the gap
being empirical breadth + a comparison rather than contribution quality. The
reproducibility and the honest, falsifiable framing are genuine differentiators.

## Part B — Academic-pipeline proofread (§11.3/§11.4)

### B.1 Fixed this pass
- **Em-dash regression (humanizer §11.4).** The phase-22 duality reframe reintroduced 5
  prose em-dashes (`---`) into a deliberately em-dash-free manuscript (abstract
  Conclusion, contribution bullet, cross-SUT keystone). Replaced with colon / parentheses
  / comma / period. Prose em-dash count is now 0 (only the closest-prior table's
  empty-cell dashes remain); Unicode U+2014 count is 0.

### B.2 Clean
- AI-isms (crucial/pivotal/delve/leverage/underscore/showcase/…): 0.
- **Framing consistency.** The seeded-fault experiment is "stress-test evidence" (for
  localization — honestly suggestive) while the coverage/duality is the "central claim";
  no contradiction between the humble localization scoping and the bold coverage thesis.
- **Internal consistency.** 352 regression guards pin prose↔evidence; clean compile
  (0 undefined, 0 Missing character, 0 overfull >50pt); bib 32/32 all-cited.

### B.3 Submission-readiness checklist (IST)
| Item | Status |
|---|---|
| Structured abstract (Context/Objective/Method/Results/Conclusion) | ✓ 299 words ≤300 |
| Highlights | ✓ 5 bullets, ≤85 chars each |
| Keywords | ✓ 7 (≤7) |
| CRediT author statement | ✓ present |
| Declaration of Competing Interest | ✓ present |
| Data availability | ✓ present |
| Generative-AI usage declaration | add in Editorial Manager at submission |
| Word count | ✓ 12,461 ≤ 15,000 |
| elsarticle (elsarticle-num) | ✓ |
| §15 pre-submission audit (paper/43) | ✓ submission-ready |

### B.4 Strengthening pass — done
- **Tsigkanos et al. 2023 added** (§2.3, as the LLM-driven MR-discovery prior alongside
  graph-kernel and data-driven approaches; bib entry + crossref-verified citation_audit
  row). Missed cite closed; bib now 33/33 all-cited.
- **Accuracy/UQ complementarity made explicit** (the related-work distinction): the
  gate-admitted MR surfaces a property failure that an in-distribution accuracy or UQ
  monitor, reading only output magnitude, does not — framed as *complementarity, not
  superiority* (per the no-baseline-superiority scope), using the committed
  0.0216-accuracy-vs-mirror-y datum; no new experiment. Clarity buffer 12500 → 12650
  (compiled count 12569; still ~2.4k under the 15000 hard cap).
- **DONE (C38, commit 374355c):** the per-seeded-fault rollout-error-vs-MR-detection
  comparison was run on the cylinder MGN — the symmetry MR catches a mesh-adjacency and a
  physical-channel fault that leave rollout error within 1.3x of the 0.0216 baseline (under
  a 2x threshold), turning the conceptual complementarity into an empirical one.
- **DONE (C39, commit fed25d9):** the empirical-breadth gap was addressed by a read-only
  cross-program generalization — the coverage-geometry reading reproduces across seven
  program types in three families (neural surrogates, classical solvers, OpenMC) from
  committed Minimum-MR-SubSet kill matrices (plan in paper/45). Both are integrated into the
  manuscript (commit 4f3538f).

## Verdict
**Submission-ready, no blockers.** The em-dash regression is fixed. Realistic IST outcome
is major revision, with empirical breadth + a comparison as the gap; the contribution and
reproducibility are at or above the IST bar. The single optional citation (Tsigkanos 2023)
would tighten related work.
