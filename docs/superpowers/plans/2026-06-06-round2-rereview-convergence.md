# Plan + Outcome: Round-2 Re-review Convergence (Minor-Revision pass)

Date: 2026-06-06
Branch: claude/trusting-curie-i2VHM

## Re-review result (4 Sonnet roles, fresh-tree verified)

A first re-review attempt was INVALID: the cloud env reset the working tree to an old
branch (codex/mirror-y-rate-upgrade) after the push, so the reviewers read stale files.
Detected from a reviewer reporting "files do not exist / manuscript v0.3", restored the
tree to origin/claude/trusting-curie-i2VHM (d5ccdc8), and re-ran with a mandatory
freshness check (assert new files exist + manuscript line 4 == v0.4) in every prompt.

Valid second-round verdicts (vs first round 3x Major + 1x Reject):
- R1 methodology: Major -> Minor. All five first-round objections RESOLVED.
- R2 metamorphic testing: Major -> Minor. Independently verified run_mirror_y_symmetric_mesh.py
  is CODE-CORRECT (exact involution, fail-closed asserts, correct equivariance formula);
  circularity dissolved.
- R3 SciML/numerics: Major -> Minor. Confirmed equivariance is LEARNED (not architectural),
  so 1.10 is meaningful. Two blocking items: normalizer disclosure, conservation verdict label.
- DA adversarial: Reject -> Major (softened). O2/O4/O5/O6 DEAD; strongest surviving =
  symmetric-mesh OOD-confound on the magnitude.

## Convergent fix: normalizer-equivariance decomposition (real control, no new SUT)

The single most-cited surviving objection (R1-N2, R2-R1, R3-blocking, DA-strongest) was that
the 1.10 violation might come from the input normalizer (fit to asymmetric data, so not exactly
equivariant in vy) or from OOD-regime numerical incoherence rather than learned weights.
Answered with data: added a control to run_mirror_y_symmetric_mesh.py that re-runs with the
vel_norm vy-mean zeroed (making the input normalizer exactly equivariant in vy). Result:
  - real normalizer:        relative L2 1.1032
  - vy-mean-zeroed control:  relative L2 1.1014
  - normalizer-induced share: 0.16% (~0.2%)
=> the violation is dominated (>99.8%) by the learned message-passing weights. Recorded in the
ledger (normalizer_equivariance_control) and in the manuscript.

## Text fixes applied (manuscript.md + main.tex, lockstep)

1. Normalizer decomposition + caveat: replaced "genuine learned-symmetry violation, not a
   geometric or accuracy artifact" with the quantified control (0.2% normalizer share) PLUS
   R2's OOD caveat: read 1.10 as a binary equivariance failure, not a calibrated in-distribution
   magnitude (normalization-mismatch may amplify the magnitude).
2. Conservation verdict relabel (R3 blocking): Section 5.2 table "reference-relative diagnostic
   pass" -> "inconclusive: reference-relative non-regression guard on 2 frames (not scored as a
   conservation pass)".
3. Rollout 34x commensurability (R3, R1): report mean 0.044 (bimodal, ~17x) alongside median
   0.0216 (~34x); note both are relative L2 of different objects so the ratio is an
   order-of-magnitude gap, not a precise factor; do not compare 1.10 to 0.0216 directly.
4. Section 2.6 overclaim (R1): universal claim -> "as the present case illustrates".
5. RQ4 re-scope (R2): note only the rollout-accuracy comparator is answerable now; others blocked.
6. Contributions bullet 3 (R2): state the domain-violation axis is currently qualitative.

## Acceptance (met)

- 103 unit tests OK (added ROUND2_INTEGRITY_MARKERS: control "from 1.1032 to 1.1014",
  "binary equivariance failure", conservation relabel - asserted in BOTH files).
- validate_experiment_protocol.py and validate_research_assets.py exit 0.
- claim-ledger parses C1..C9; symmetric-mesh ledger now carries the normalizer control.
- PDF rebuilt clean (texlive was wiped again by the env and reinstalled; main.log clean, 299 KB).

## Net trajectory across the loop

Theory lift -> A+B real experiments -> reviewer-driven integrity fixes.
Review verdicts moved 3x Major + 1x Reject  ->  3x Minor + 1x Major.
Still one SUT/one checkpoint: cross-SUT, expert/generic/LLM baselines, and seeded-fault
detection remain blocked and are honestly scoped as future work.
