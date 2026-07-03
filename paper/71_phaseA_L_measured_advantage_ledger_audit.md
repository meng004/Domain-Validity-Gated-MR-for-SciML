# Phase A/L Loop: Measured-Advantage and Claim-Ledger Audit

Date: 2026-07-02

Scope: audit the revised manuscript and claim ledger after Phase 0, Phase C, and Phase B, with emphasis on claims that affect a stable mid-level TOSEM acceptance posture.

## Evidence Sources Actually Used

- `NEXT_STEPS.md`, read in Phase 0: latest execution route is `A+B+C 理论优先 -> TOSEM 稳投`.
- `paper/67_deepresearch_verdict_and_ABC_program.md`, read in Phase 0: raw manuscript was assessed as IST/STVR-level; TOSEM stability required closing Phase B theory, Phase A breadth, and ledger cleanliness.
- `paper/68_phaseC_refocus_skeleton.md`, read in Phase 0: Phase C was a framing skeleton, not final evidence.
- `paper/69_phase0_tosem_evidence_gate.md`, created in Phase 0: records permitted and forbidden claim classes after evidence-gate review.
- `paper/70_phaseB_operator_floor_soundness.md`, created in Phase B: provides the shape-regular P1 local divergence-floor theorem and explicit non-claims.
- `research_assets/experiments/claim-ledger.yml`, parsed from the written-back project mirror on 2026-07-02.
- `manuscript/main.tex`, scanned from the written-back project mirror on 2026-07-02.
- `manuscript/main.pdf`, regenerated in the temporary compile workspace on 2026-07-02 after the Phase C/B changes.

## Loop Entry Condition

Phase A/L starts only after:

1. Phase C has converted the paper from a workflow/tool narrative into a numerical-decidability and admissibility-gate narrative.
2. Phase B has added a bounded, provable operator-floor claim rather than claiming a general arbitrary-mesh theorem.
3. The revised LaTeX source has compiled successfully in the temporary workspace.
4. The claim ledger has been updated with C53 and can be parsed from the written-back mirror.

All four entry conditions were met. The full project validators could not be run directly from the OneDrive project path because the host returned `Operation not permitted`; this is recorded as an execution limitation, not a validation pass.

## Main Audit Findings

### Finding A1: The measured-advantage evidence supports complementarity, not superiority

Ledger extraction from `claim-ledger.yml` returned:

- `C38-detection-vs-accuracy-complementarity`: `observed`; scope is one cylinder MGN SUT, one checkpoint, one eval trajectory, one 10-mutant seeded-fault catalogue, and a predeclared `2x` rollout threshold.
- `C42-three-arm-complementarity`: `observed`; scope is one converged PointMLP cylinder SUT, one checkpoint, one eval trajectory, 20 faults, validity-gated MR suite versus rollout accuracy monitor and ungated generic templates; the ledger explicitly says complementarity and gate value, not superiority.
- `C51-cross-sut-three-arm-consolidation`: `observed`; consolidation over committed artifacts; no new model run.
- `C52-airfoil-three-arm`: `observed`; live converged PhysicsNeMo airfoil SUT, one checkpoint, 10-mutant catalogue, five official test trajectories by nine frames; mirror-y is inadmissible and not used as a detector.
- `C53-shape-regular-p1-operator-floor-soundness`: `supported-theory`; proof artifact for P1 constant-per-cell divergence on shape-regular triangular meshes and C2 divergence-free reference fields.

Conclusion: the manuscript may claim measured complementarity, measured gate value, and bounded multi-SUT consistency of the admissibility predicate. It must not claim baseline superiority, general reliability, or real-world defect-detection rates.

### Finding A2: Risk words remain in the manuscript only as boundary statements

Fixed-string scans of `manuscript/main.tex` found `superiority`, `fault-detection rate(s)`, `model correctness`, `arbitrary unstructured`, and `reliability`. The relevant matches are boundary or non-claim uses:

- Lines 108, 139, 182, 196, 346, 367, 537, 553, 571, 573, 644, and 672 use `superiority` to deny or limit superiority claims.
- Lines 553 and 571 use `fault-detection rates` in the blocked-claim context.
- Line 567 states that the construct is not model correctness and that arbitrary unstructured meshes are not proven.
- Lines 98, 127, 129, 182, 336, 363, 410, 438, 538, 548, 553, 571, 575, 650, 660, 672, and 690 use `reliability` mainly to deny general reliability claims or to distinguish scoped evidence from reliability estimation.
- A fixed-string scan for `outperform` returned no hits.
- A fixed-string scan for `better than` returned no hits.

Conclusion: no immediate wording repair is required for these terms, provided the final copyediting pass preserves them as explicit limitations rather than positive claims.

### Finding A3: Phase B closes the minimum soundness gap, but only under an explicitly bounded theorem

The Phase B theorem supports a local P1 divergence floor on shape-regular triangular meshes. It does not support:

- arbitrary unstructured cylinder meshes;
- degenerate or sliver meshes without shape regularity;
- non-P1, flux, discontinuous, or learned-output operators;
- model accuracy, reliability, or real-world fault-detection claims.

Conclusion: the former TOSEM-critical theory gap is reduced from "no operator-floor argument" to "bounded theorem plus empirical stability outside the proof setting." This is acceptable only if the paper keeps the proof boundary visible in the main text and claim map.

### Finding A4: Current distance to a stable mid-level TOSEM posture

After Phase C and Phase B, the largest remaining gap is no longer narrative identity or missing theory; it is evidence breadth and reviewer trust in the measured-advantage story.

Residual gaps ranked by expected effect on acceptance:

1. **High impact: external validity and denominator trust.** Current evidence is still a collection of bounded case studies and committed sibling artifacts. This is transparent, but a skeptical reviewer may still see the general SciML framing as wider than the evidence.
2. **High impact: comparator interpretation.** The three-arm evidence is useful only when framed as complementarity and gate value. Any slip into superiority language would reopen the strongest rejection risk.
3. **Medium impact: theory-to-implementation boundary.** C53 is a strong improvement, but it is not an arbitrary-mesh theorem. The main text must preserve the distinction between proved shape-regular P1 conditions, the concrete symmetric-mesh analytic run, and the observed Delaunay stability run.
4. **Medium impact: reproducibility of full validators.** LaTeX compilation and mirror parsing succeeded, but direct project-path validators were blocked by host filesystem permissions. Before submission, these validators should be rerun in an environment that can read the project path directly.
5. **Medium-to-low impact: style and density.** The manuscript is now more coherent, but several limitation sentences are dense. The final copyediting pass should reduce AI-like over-packaging without weakening evidential qualifiers.

## Phase A/L Exit Condition

Phase A/L can exit when:

- all measured-advantage claims are ledger-backed and classified as complementarity/gate value rather than superiority;
- high-risk words in the manuscript are either absent or used only in explicit boundary statements;
- C53 is present in the ledger and manuscript claim map;
- remaining execution limitations are recorded rather than hidden.

All four conditions are met for the current project mirror.

## Review and Theme-Drift Check

Review question: Does the paper now answer "when can an MR verdict be trusted as numerically decidable evidence for a SciML surrogate?" rather than "can a workflow generate more MRs?"

Answer: yes. The title, abstract, introduction, contributions, results interpretation, limitations, and claim map now center on numerical decidability and admissibility. The MR-card and typed-verdict machinery is presented as an operational mechanism, not as the paper's standalone novelty.

Theme-drift risk: moderate. The breadth sections can still pull the manuscript toward a general "SciML reliability workflow" claim. The final copyediting pass must keep the theme anchored to numerical decidability, bounded admissibility, and relation-indexed evidence.

