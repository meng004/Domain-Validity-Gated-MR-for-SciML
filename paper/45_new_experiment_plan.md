# 45 — New-Experiment Plan: complementarity table + empirical breadth

> Date: 2026-06-17 · Status: **plan only, pending approval** (no experiment run yet).
> Addresses the two deep-research / IST-gap findings in paper/44: (1) "no comparison"
> → a fault-detection-vs-accuracy complementarity table; (2) empirical breadth / the
> duality resting on two SUTs → a cross-program-type test of the coverage principle.
> Priority constraint (user): reuse cases from the READ-ONLY sibling Minimum-MR-SubSet
> (`../最小完备MR子集`, never modified; we only read its committed kill matrices).

---

## Step 1 — Fault-detection-vs-accuracy complementarity table (small new run)

**Gap.** Reviewers will ask what the MRs add over an accuracy/rollout-error monitor.
The paper states complementarity conceptually (the in-distribution-accurate surrogate
that still violates mirror-y); step 1 makes it **empirical on the seeded faults**.

**What exists.** `tools/run_seeded_fault_detection.py` already computes, per mutant, the
deployed next-state prediction `predict(...)` and a `relative_l2`. The committed ledger
(`research_assets/runs/seeded-fault-detection/raw/metric_ledger.json`) stores per-mutant
MR metrics but **no per-mutant rollout error**.

**Work (small, in-scope, one SUT).**
1. Extend the cylinder harness to record, per mutant, the **rollout error** = relative
   L2 of the (faulted) predicted next-state vs the ground-truth next-state, alongside the
   existing MR metrics. (Also do it for the airfoil harness for a second-SUT row.)
2. Emit a table: per fault, `[caught by an MR? | rollout-error rank/flagged?]`, plus the
   union/complement sets.
3. **Honest expected reading** (not pre-judged): NS_skip_denorm (gross scale) likely
   blows up *both* MR and accuracy; symmetry/adjacency faults likely break an MR while
   leaving rollout error modest → the complementarity cell. Report whatever the data show,
   including faults accuracy catches that the MRs miss.
4. New claim `C38-detection-vs-accuracy-complementarity` (status observed; wording allows
   "complementary, the MRs catch a subset accuracy does not flag and vice versa";
   **forbids** any superiority/"MRs are better" claim — keeps the no-superiority scope).
5. One guard test; one short results paragraph + a small table (≤1 float).

**Cost:** ~1 short local run (reuses trained checkpoints already on disk). No new training.

---

## Step 2 — Empirical breadth via the committed Minimum-MR-SubSet kill matrices

**Gap.** The duality/coverage principle is evidenced on two CFD SUTs; reviewers will say
"two SUTs is thin for a principle." The sibling repo already contains **committed
kill matrices** (`sut, mutant_id, fault_class, mr_id, mr_meta_pattern, killed, residual,
tolerance, status`) for many program types — exactly the data the coverage analysis needs.
This lets us test the principle across program types **with no re-training and no
modification of the read-only repo** (we only read its `runs/*/kill_matrix.csv`).

**Method (reuse, not re-run).** A new script in *this* repo reads each selected program's
committed `kill_matrix.csv`, computes the **MR-class → fault-class coverage map** (which
admissible MR catches which fault class) and its blind spots, and tests the
coverage-geometry prediction per program: *a fault is caught iff it perturbs a measured
invariant of an admissible MR*. We then report whether the principle (coverage is fixed
by the admissible-MR set; blind spots are structural) **generalizes across program types**.

**Candidate program types (only `kind=real`, committed kill matrices):**

| # | Program | Type | Domain | Path (sibling `runs/…`) | Reuse |
|---|---|---|---|---|---|
| S1 | cylinder-flow MGN | neural surrogate (mesh) | CFD (incompressible) | `abd-witness-cylinder-flow-mgn-runtime-20260605T021457Z/` | committed (primary) |
| S2 | Burgers2D PINN | neural surrogate (PINN) | 2D conservation law | `abd-witness-burgers2d-pinn-20260607T161215Z/` | committed |
| S3 | Diffusion2D PINN | neural surrogate (PINN) | 2D parabolic | `abd-witness-diffusion2d-pinn-20260608T032704Z/` | committed |
| C1 | P2 wave | classical solver (FDM) | hyperbolic PDE | `pseries-faultclass-p2_wave-*/` | committed |
| C2 | P5 PKE | classical solver (stiff ODE) | reactor kinetics | `pseries-faultclass-p5_pke-*/` | committed |
| C3 | P7 Burgers | classical solver (FVM) | conservation law | `pseries-faultclass-p7_burgers-*/` | committed |
| R1 | OpenMC (p9) | production physics code | Monte-Carlo neutron transport | `abd-p9-openmc-20260604T030626Z/` | committed |

This spans **three program families** — neural surrogates (S1–S3), classical numerical
solvers (C1–C3), and a real production physics code (R1) — across CFD, conservation,
parabolic, hyperbolic, stiff-ODE, and Monte-Carlo domains. All have committed kill
matrices (`kind=real`); `blocked_runtime` cases (MetBench MB01–08, some cylinder runs)
are excluded as not-runnable.

**Honesty boundaries (hard).**
- We **read** the sibling's committed kill matrices; we do **not** re-run or modify it.
- The cross-program result is a **generalization check of the coverage principle**, not a
  claim that the validity-gate workflow was *executed end-to-end* on each program (the
  sibling produced those kill matrices under its own protocol). Wording must say
  "the coverage principle holds on N committed kill matrices spanning M program types,"
  not "we tested N new SUTs with our pipeline."
- New claim `C39-cross-program-coverage-generalization` (status qualified): wording allows
  "the coverage-geometry reading reproduces across program families from committed
  Minimum-MR-SubSet kill matrices"; forbids "our pipeline was executed on each" and any
  per-program reliability/rate claim.
- A clean negative (a program where coverage is *not* recovered from its admissible MRs)
  is reported as such — it bounds the principle, consistent with the falsifiable framing.

**Scope decision needed (see below).** Including C1–C3 and R1 broadens the paper from
"SciML surrogates" toward "MR-tested scientific software." The surrogate focus stays
primary; the corpus is positioned as a *generalization-beyond-surrogates* check.

**Cost:** read-only analysis of committed CSVs + one new analysis script + claim/test +
one results subsection. No training, no sibling modification.

---

## Execution order (after approval)
1. Step 1 harness extension + run + ledger/claim/test + table. (in-scope, low risk)
2. Step 2 read-only cross-program coverage script + claim/test + subsection.
3. Integrate both; re-verify (suite + compile + wordcount/buffer); §15 re-audit; commit.

## Open decision for the user
How broad should Step 2's program-type coverage be? (affects positioning + word budget)
