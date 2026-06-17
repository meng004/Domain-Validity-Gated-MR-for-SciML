# 42 — Response to Simulated Review (paper/41) — Draft

> Status: draft, pre-submission. This is the reviewer-facing R&R traceability
> (CLAUDE.md §6.6): it stays OUT of the manuscript. Each entry maps a concern from
> the deep-research + academic-pipeline review (paper/41) to the change that
> addresses it, with evidence pointers. When the paper is actually submitted and
> reviewed, real reviewer comments replace these simulated ones.

## R2-1 (major-revision trigger) — single-SUT generalization of the by-class diagnostic — ADDRESSED

**Concern (paper/41 §3):** the by-class fault-localization narrative is the
paper's most original empirical claim, yet it rests on one cylinder-flow SUT; the
diagnosis pattern may be SUT- or fault-catalogue-specific.

**Action (strategy a, executed):** replicated the seeded-fault by-class diagnostic
on the second SUT (primary-scale PhysicsNeMo airfoil, C35 roster), with the same
10-mutant five-class catalogue and the same predeclared thresholds, over five
official test trajectories.

**Outcome (honest):** the by-class localization is **SUT-specific**. Across five
trajectories only the gross normalization fault (NS_skip_denorm) is robustly
detected by the conservation MR; mirror-y is domain-inadmissible (gate-excluded);
the boundary, mesh-adjacency, physical-channel, and sign-flip faults are
undetected; NS_double_scale and TR_double_step fire on one trajectory only. The
single localization shared across both SUTs is continuity -> normalization-scale
faults. What generalizes is the MR-as-detector mechanism for gross output-scale
faults, node-permutation's insensitivity to invariant-preserving faults, and the
admissibility gate excluding an MR whose precondition fails.

**Why this strengthens the paper:** the cross-SUT result is a natural experiment
that *confirms the coverage-geometry principle* — removing the inadmissible MR
(mirror-y) removes exactly its fault coverage, as the principle predicts. The
headline claim is now honestly bounded with real cross-SUT evidence rather than
overstated.

**Evidence:** claim C36; `tools/run_seeded_fault_detection_physicsnemo_airfoil.py`;
`research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-seeded-fault-detection/raw/metric_ledger.json`;
`tests/test_seeded_fault_detection_airfoil_cross_sut.py`. Manuscript: intro
contribution bullet, novelty paragraph, fault-robustness "Second-SUT replication"
paragraph. Commit `f002c80`.

## P1 (related work) — physical-consistency diagnostics contrast — ADDRESSED
Added a one-clause contrast (§2.4, `najafi2026`): physical-consistency diagnostics
score a physically derived residual on observed outputs passively; the present
method acts in relation space, applying a controlled transformation and reporting
which necessary relation breaks. Commit `f002c80`.

## P2 (related work) — same-venue MT4ML — ADDRESSED
Added a same-venue nod (§2.2, `ying2025`): recent MT applied to tabular ML models
such as credit scoring. Commit `f002c80`.

## OPEN — elevate the by-class diagnostic from "suggestive" to an evidence-supported coverage model — NEXT STEP
The cross-SUT result (C36) plus the within-SUT K=6 replication (R1), the knife-edge
blind-spot sweep (R3), and the adversarial mutants (R4) give four independent lines
supporting a *predictive coverage-geometry* reading: a fault is detected iff it
perturbs a measured invariant of an admissible MR, so the admissibility gate
predicts the detector suite's blind spots. Two of the four lines are falsifiable
confirmed predictions (R3 knife-edge collapse; C36 cross-SUT MR removal). Elevating
this from a buried sentence (current §Results) to a first-class contribution is the
next step. See NEXT_STEPS.md.

## Remaining review items (paper/41) — not yet actioned
- **R2-2** configurational-novelty framing (lead with the two genuinely new devices).
- **R2-3** one concrete cross-class calibration example for the domain-violation axis.
- **R2-4** audit abstract/intro wording so the O(h) floor's generality is not overstated.
