# Phase 17 — Gate-closure execution record (2026-06-12)

Objective: close the four-part Phase-5 gate (empirical >= 8.0, overall >= 7.8,
accept >= 0.65, clarity >= 7.0) on the v16 plateau (overall 7.31, accept 0.572,
clarity 6.0, empirical 7.2), acting on the v16 reviewer signals rather than
re-running prose-only iteration.

## v16 signal triage

1. EIC (clarity 5): "over-scoped, artifact-heavy narrative obscures the core
   contribution"; "empirical story mixes primary evidence with many secondary
   comparators".
2. MethodologyRigor (clarity 5): defensive prose, ledger cross-references,
   "most planned statistical analyses still blocked" (stale framing — the
   statistics exist but were presented as blocked plans).
3. DomainExpert: "primary MGN evidence limited to one architecture family and
   dataset; cross-family extensions on different PDEs reduce direct
   applicability" — same-task breadth is what counts.
4. DevilsAdvocate: incremental positioning vs Duque-Torres/Eniser; no DOI.

## Executed actions

### A. Same-task production-framework evidence (P0c Task-4 upgrade)

`tools/run_physicsnemo_mgn_scaled_workflow.py` upgrades the Object-A smoke
workflow (1 trajectory, wiring-test model) to a multi-trajectory CPU evaluation
of the OFFICIAL production MeshGraphNet architecture (processor_size=15,
hidden=128, 2.33M parameters — the DeepMind/PhysicsNeMo default):

- staged the first 25 official train + 40 official test DeepMind cylinder_flow
  TFRecord trajectories outside git via ranged downloads;
- trained 2 epochs x 3,725 one-step samples on CPU (honestly bounded: not the
  official 10M-step schedule);
- evaluated the MR battery per test trajectory: node permutation (40 cells),
  mirror-y OOD stress (40 cells), conservation diagnostic (200 cells), one-step
  rollout accuracy (200 cells).

A real harness defect was found and fixed during bring-up: PhysicsNeMo's
`VortexSheddingDataset.__getitem__` mutates a shared graph object in place, so
caching graph references across snapshots silently corrupted the
source/follow-up pairing (node-perm read 1.5e-1 instead of exact 0.0). The fix
re-fetches the mid-snapshot graph immediately before follow-up execution.

### B. Clarity surgery (manuscript.md + main.tex in lockstep)

- removed reviewer-visible internal draft-policy blocks;
- rewrote the abstract Results from a 340-word run-on into tiered sentences;
- rewrote Subject Systems and Statistical Reporting around executed evidence
  (the inferential statistics were already committed but were framed as
  "blocked plans" — that framing alone fed the v16 MethodologyRigor concern);
- reorganized Section 5 into primary / supporting / secondary tiers, fixed the
  5.6.4-5.6.6 numbering, renamed "Still blocked" to "Boundary of the evidence";
- compressed the five 5.3 mega-bullets (~35% shorter) while keeping every
  pinned honesty marker;
- promoted S4/S5, PointMLP, and PhysicsNeMo into 5.4 prose as same-task
  multi-architecture replication.

### C. Novelty repositioning

- 2.7 now states the first-end-to-end-pipeline claim with the per-ingredient
  contrast (Reichert: informal filter; Eniser: calibrated tolerance;
  Duque-Torres: binary pre-filter; none combines/grounds/types/maps);
- added a closest-prior capability table to 2.4;
- emphasized that the same predicate executes unchanged across MeshGraphNet,
  PointMLP, PhysicsNeMo, PINN, and FNO subjects.

### D. Hygiene

- `--out` flag for the D-score regenerator: pytest no longer rewrites the
  committed report timestamp;
- internal word-count buffer raised 11000 -> 11500 with documented rationale
  (IST hard limit 15000; conservative counter).

## Verification

- Full guard suite green after every step (278 tests + subtests).
- LaTeX recompiled clean: 0 Overfull, no undefined references.

## Blocker

Panel execution (v17) requires `OPENAI_API_KEY`/`OPENAI_BASE_URL` (bltcy
gateway), which are not configured in this execution environment. The panel
tool fails closed (`BLOCKED_NO_LLM_CREDENTIALS`). Scores for the revised
manuscript cannot be measured until the environment provides gateway
credentials.
