# Domain-Validity-Gated-MR-for-SciML

A domain-admissibility-gated, relation-indexed workflow for identifying and executing
**metamorphic relations (MRs)** as auditable, oracle-free test assets for scientific
machine-learning (SciML) surrogates. The case study targets MeshGraphNets-family
cylinder-flow surrogates, but the contribution is a software testing / V&V method, not a
CFD-accuracy result.

## The gap this addresses

Existing work already provides physics constraints, scenario testing, residual/UQ
diagnostics, and a metamorphic-testing foundation. What is missing is a SciML-oriented,
*domain-validity-first* pipeline in which every MR states:

- where it comes from (physical equation, boundary condition, representation contract,
  numerical assumption, or implementation contract);
- under what physical **and numerical** conditions it holds;
- how the follow-up case is generated;
- how the threshold is set and where it comes from;
- how the relation-level verdict is assigned;
- how a violation is interpreted as the SUT's applicability boundary.

In other words, the gap is not "are there MRs" but: MR validity boundaries are not
systematically recorded; the candidate-to-executable path is under-structured; violations
are reported as metrics instead of relation-level verdict evidence; and the relationship
between accuracy, residual, UQ, equivariance error, and MRs is left implicit.

## The thesis (what lifts this above a checklist)

1. **Admissibility predicate.** A candidate is an admissible MR only when four conditions
   hold together: physical/software basis ∧ transformation preconditions ∧ boundary +
   output-mapping compatibility ∧ **numerical decidability** (the verdict tolerance must
   dominate the intrinsic error floor of the operator that measures the relation). The
   first three remain gating conditions; provenance is the recording mechanism, not a
   substitute for the gate.
2. **Two-dimensional verdict.** Verdicts are regions of a plane: *relation-violation*
   magnitude (e.g. V/tolerance or V/floor) against *domain-violation* magnitude
   (precondition / geometry / boundary / operator inadmissibility). Only low-domain +
   high-relation violation may be read as SUT inconsistency; high domain-violation is
   out-of-relation-domain or, near the boundary, OOD-stress. The domain-violation axis is
   currently operationalized qualitatively; a calibrated continuous score is future work.
3. **Relation-indexed applicability map.** Unlike UQ / trust-region methods that locate
   unreliability passively in feature/residual space, this method acts in *relation
   space* via controlled physical transformations and reports which relation breaks,
   indexed by that transformation. The current evidence is one bounded within-SUT point
   on such a map, not a completed map.

## Evidence boundary (read before citing any number)

The current evidence is **within one SUT and one MeshGraphNets checkpoint** (cross-SUT is
infeasible in this environment: only one checkpoint exists). It comprises:

- node-permutation equivariance holds to machine precision (relative L2 = 0.0, tol 1e-6);
- an approximate mirror-y OOD-stress probe (exact relation out-of-relation-domain on the
  asymmetric eval mesh) failed on 10/10 eval frames (median relative L2 0.737, V/floor 3.96);
- an absolute mass-conservation relation stays deferred; the reference-relative divergence
  diagnostic is recorded as *inconclusive* (non-regression guard on 2 frames, not a pass);
- a one-step rollout-accuracy comparator (median relative L2 0.0216) — the mirror-y violation
  is ~34x the median / ~17x the mean in-distribution accuracy;
- exact mirror-y on a synthetic, provably symmetric (admissible) mesh fails (relative L2 1.10);
  a control shows the input normalizer accounts for ~0.2%, so the violation is dominated by the
  learned weights. Read as a binary equivariance failure (OOD magnitude not calibrated);
- seeded-fault detection: the MRs as detectors catch 5/10 injected mutants and, in a first
  suggestive test, localize by MR class (continuity to boundary/scale, symmetry to
  physical-channel/adjacency; node-permutation none, exact-by-design).

**Still blocked / not claimed:** cross-SUT or geometry-independent rates; expert-MR,
generic-MR, and LLM baselines; general or real-world fault-detection rates; validated
localization; runtime; reliability; model accuracy. The authoritative runtime claims live in
`research_assets/experiments/claim-ledger.yml` (claims `C1`–`C10`); the paper-level claims
(`PC1`–`PC10`) map onto them and are kept in a distinct namespace to avoid collision.

## Repository layout

- `paper/manuscript.md` — working manuscript (source of truth for prose).
- `paper/ist-submission/` — Elsevier/IST LaTeX package (`main.tex`, `references.bib`,
  vendored `elsarticle` class); double-anonymized for review.
- `paper/22_stage2p5_integrity_audit.md`, `paper/23_stage3_reviewer_simulation.md` —
  integrity audit and multi-role reviewer simulations.
- `research_assets/experiments/` — `claim-ledger.yml` (authoritative claims),
  `experiment-ledger.yml`, `evidence-package.md`.
- `research_assets/runs/` — committed raw outputs, manifests, and metric ledgers for the
  three pilots.
- `research_assets/rubric/`, `research_assets/mr_cards/` — the domain-validity rubric and
  MR-card assets.
- `tools/` — `validate_experiment_protocol.py`, `validate_research_assets.py`
  (fail-closed evidence gates).
- `tests/` — readiness / integrity regression guards.
- `docs/superpowers/plans/` — plan-driven development records.

## Reproducing the gates

```bash
python tools/validate_experiment_protocol.py
python tools/validate_research_assets.py
python -m unittest discover -s tests -v
```

Real-SUT pilots require the `METBENCH_MGN_*` environment variables to be set; absent those,
the precondition gate fails closed and the SUT runs stay blocked by design.

## Positioning

The intended venue is a software V&V method paper (e.g. IST / JSS), framed as:

> A domain-validity-aware workflow for identifying and executing metamorphic relations in
> SciML OOD validation.

It is **not** framed as a new metamorphic-testing method that outperforms accuracy-based
validation, and **not** as a claim of superiority over uncertainty quantification.
