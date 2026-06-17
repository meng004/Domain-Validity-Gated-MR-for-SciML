# Submission-maturity assessment — IST (2026-06-17)

## How this was produced

- **Gateway panel (requested): could NOT run.** `tools/run_academic_review_panel.py` fails closed without `OPENAI_BASE_URL` + `OPENAI_API_KEY` (bltcy gateway); both are unset this session and the prior key was exhausted. No multi-vendor (gpt-5.5 / glm-5.1 / deepseek-v4-flash / qwen3-max / kimi-k2.6) panel was run. To run it, provide/rotate the two env vars and re-run the script.
- **Substitute actually run: Claude-simulated adversarial council** (project CLAUDE.md §10.9 Council Mode) — 5 reviewer personas (EIC, MethodologyRigor, DomainExpert, Perspective, DevilsAdvocate) each read the current `main.tex` independently. Record: `research_assets/runs/academic-review-panel-claude-council/review_panel_report.json`. Scores are **not numerically comparable** to the v18–v36 gateway series; read them for consensus structure, not as a calibrated score.

## Quantitative result (Claude council)

| Dimension | Mean | Note |
|---|---|---|
| novelty_contribution | 6.4 | "incremental recombination," paper concedes this |
| technical_soundness | 7.2 | operator-floor derivation verified correct |
| empirical_rigor | 6.6 | DevilsAdvocate 4 (catalogue/airfoil); others 7–8 |
| related_work | 7.4 | Perspective 6 (missing Spieker neighbor) |
| **clarity** | **5.8** | **lowest — binding constraint, as in all prior panels** |
| reproducibility | 8.2 | DevilsAdvocate 5 (CI cannot exercise torch SUTs); others 9 |
| scope_match_to_ist | 7.4 | clean V&V-method fit |

Overall 7.0 · accept-probability mean 0.478 (range 0.32–0.62) · **majority verdict major_revision (3 major / 2 minor)**.

Gateway baseline v36 (pre-E5, pre-bib-fix): overall 7.37 · accept 0.664 · major_revision (3/2). The Claude council is harsher in absolute numbers (different models) but **reproduces the verdict structure and the clarity-is-weakest pattern** — the consistent signal across both panel types.

## Consensus (the real signal — flagged by ≥3 reviewers)

1. **Clarity / scope dilution is the ceiling.** Eleven Results subsections; the EIC and Perspective both read the secondary breadth studies (read-only cross-program C39; end-to-end OpenMC + classical solvers C40) as *diluting* the contribution — and note the paper *itself* says they "assert no per-program reliability, no superiority, no new MR contribution." Recommendation (EIC, verbatim sense): consolidate to cylinder-flow core + airfoil discriminator + one cross-family transfer; demote OpenMC/classical-solver + read-only kill-matrix material to a brief appendix.
   - **Tension worth naming:** the E5/C40 breadth was added to answer the prior "single-task external validity" criticism. A different reviewer lens now reads that same breadth as dilution. The resolution is *structural demotion* (appendix + one-line pointer), not deletion — it keeps the evidence while restoring focus.
2. **The validity–coverage duality (C37) is near-tautological.** All five touch it. "Each MR scores one invariant" makes predictions (i)/(iii) close to definitional; only the cross-SUT keystone (C36) is a genuine empirical test, and it is n=2 CFD, fault-class-level, qualitative. Stating it as a "confirmed falsifiable principle" in the Abstract is stronger than the evidence licenses.
3. **Airfoil second task is essentially untrained** (one-step rel L2 ≈ 1.00). The "primary-scale 240-cell" label oversells a gate-*discrimination* demo on a non-functional surrogate. The training-independence argument is sound, but the framing invites the objection.
4. **Statistical-treatment inconsistency.** The 180/180 and 162/162 grids are honestly labelled descriptive (non-independent frames), but detector precision/recall Wilson CIs are reported *inferentially* over the same kind of correlated cells.
5. **Novelty + one verified missing neighbor.** Novelty is honestly "combine + ground the floor"; the genuinely new atom is the O(h)-floor-grounded tolerance. Perspective flags **Spieker et al.** — verified real and on-point: *Evaluating Human Trajectory Prediction with Metamorphic Testing*, MET 2024 (DOI 10.1145/3679006.3685071), and same-venue *Metamorphic Testing of Multimodal Human Trajectory Prediction*, IST 188:107890, 2025 (DOI 10.1016/j.infsof.2025.107890). Both use symmetry MRs + a statistical violation criterion — adjacent to the mirror-y MR + V/floor device.

## Strengths (consistent)

Fail-closed claim-ledger / reproducibility (spot-checked numbers matched raw JSON); the measurement-floor admissibility gate (correct, well-grounded, the strongest novel atom); construct discrimination via the airfoil design; honest scope/threats with a falsifiable central claim.

## Maturity verdict

**Submission-mechanically ready, scientifically at "major-revision-ready / borderline."** Everything a desk check looks at is clean: IST-compliant (structured abstract 296 w, 5 highlights ≤85, 7 keywords, 12,158/15,000 words, numbered refs), citation integrity fixed (7 defects corrected this session), compiles 0-warning, every number ledger-backed. The paper *can* be submitted as-is and would likely draw major-revision — exactly the historical ceiling (v18–v36 plateaued at overall ~7.4–7.8, clarity-bound). No new *blocker* appeared; the gaps are the long-standing clarity/density and significance-ceiling ones.

## Prioritized pre-submission options (all the user's call — no manuscript edits made)

- **P1 (highest leverage, low risk): density/clarity surgery on Results §5.** Demote C39/C40 cross-program + OpenMC detail to an appendix with a one-line main-text pointer; this directly targets the binding constraint (clarity 5.8) without removing evidence. The historical record shows clarity is the only dimension that moves the panel.
- **P2 (low risk): add the verified Spieker citations** (MET 2024 + IST 2025) to the related-work symmetry-MR/violation-criterion discussion; same-venue IST 2025 cite also helps scope-fit.
- **P3 (trivial): tighten OpenMC wording** in the body from "multi-group" to "1-group infinite-medium" to match the ledger/PROVENANCE precision.
- **P4 (trivial): label detector precision/recall descriptively** (consistent with the 180/180 grids) or add the "non-independent cells" caveat to the CIs.
- **P5 (optional): soften the Abstract duality wording** from "confirmed falsifiable principle" toward the n=2 qualitative scope already stated in the body.

These are revision choices, not blockers. If you want, I can execute P2–P4 (small, verified, low-risk) directly, and draft a P1 consolidation plan for your approval before touching the Results structure.
