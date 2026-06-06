# Plan: Theory Lift — Domain-Admissibility-Gated, Relation-Indexed Framework

Date: 2026-06-06
Branch: claude/trusting-curie-i2VHM (off merged main 2594a3e)
Goal: lift the paper from "audit protocol / checklist" to "framework with a central
judgement", WITHOUT adding experiments and WITHOUT crossing the existing pilot
evidence boundary. Three theory moves, user-approved with calibrations.

## Motivation

The current method reads as six parallel rubric criteria + a flat verdict list. The
three executed pilots (node-permutation / mirror-y / conservation) are in fact three
instances of one principle — a relation's verdict must be normalized against an
intrinsic error floor — but the manuscript never states it. Reviewers will read the
method as engineering hygiene and will ask how it differs from UQ / trust-region work.

## Three moves (calibrated)

1. **Admissibility predicate (§3.3).** Reframe the six criteria as one predicate:
   admissible MR <=> (i) physical/software basis ∧ (ii) transformation preconditions ∧
   (iii) boundary + output-mapping compatibility ∧ (iv) numerically decidable
   (tolerance dominates the measuring operator's intrinsic error floor). CALIBRATION:
   (i)-(iii) remain gating conjuncts, NOT demoted to hygiene; provenance is the
   recording mechanism. The conservation pilot (reference divergence ~0.037 →
   uncalibratable → defer) is the worked instance of condition (iv).

2. **Two-dimensional verdict (§3.5).** Read the six verdicts as regions of a plane:
   x = relation-violation magnitude (V/tolerance or V/floor); y = domain-violation
   magnitude (precondition / geometry / BC / operator inadmissibility). Low-y+low-x =
   pass; low-y+high-x = the ONLY region readable as SUT inconsistency; high-y =
   out-of-relation-domain or, near the boundary, OOD-stress; x within the floor =
   numerical-tolerance issue. CALIBRATION: define the axes, but state that the
   domain-violation axis is only partially operationalized — mirror-y is placed near
   the boundary *qualitatively* (non-bijective reflection, worst mismatch ~ one edge
   length), NOT via a calibrated continuous domain-violation score. A calibrated score
   is future work.

3. **UQ / trust-region delta (§2.6 + §2.7 + §6).** UQ / conformal / residual-threshold
   trust regions locate unreliability passively in feature/residual/error space; this
   method acts in relation space via a controlled physical transformation and reports
   which relation breaks, indexed by that transformation. CALIBRATION: the product is
   "the evidence structure needed for a relation-indexed applicability map", NOT a
   completed map; the mirror-y 10-frame result is one bounded within-SUT point.

Positioning sentence (abstract/intro): a **domain-admissibility-gated, relation-indexed
SciML OOD validation framework** — a thesis, not an audit protocol; does not exceed the
pilot evidence.

## Files

- paper/manuscript.md: abstract framing; §1 two-ideas paragraph; §2.6 delta para;
  §2.7 structural-novelty sentence; §3.3 admissibility predicate + tolerance/floor;
  §3.5 two-axis paragraph + qualitative-boundary caveat; §6.3 applicability-map +
  guard.
- paper/ist-submission/main.tex: mirror all of the above with LaTeX formatting; keep
  numbers identical to manuscript.md; rebuild PDF if texlive available.
- README.md: replace the empty stub with a real project overview that carries the
  gap/positioning and the elevated framework framing (incorporates the user's design
  memo content).
- tests/test_stage2p5_submission_readiness.py: add markers guarding the framework
  framing in BOTH files; add a guard asserting the overclaim phrases
  ("completed applicability map", "calibrated continuous boundary") are ABSENT.

## Acceptance

- All existing scoped-claim markers preserved (PC1..PC7, "failed on 10 of 10 recorded
  eval frames", boundary phrases) — additive edits only.
- New framework markers present in manuscript.md AND main.tex.
- Overclaim guard: no "completed/complete applicability map", no "calibrated continuous
  boundary" assertion.
- Full unit-test suite OK; validate_experiment_protocol.py and
  validate_research_assets.py exit 0.
- PDF rebuilt clean if texlive present; otherwise commit source + note regeneration.
- Multi-role re-review (academic reviewers) confirms the lift stays within evidence.
