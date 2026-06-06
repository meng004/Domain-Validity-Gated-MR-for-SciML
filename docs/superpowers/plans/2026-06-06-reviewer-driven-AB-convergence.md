# Plan + Outcome: Reviewer-Driven A+B Convergence

Date: 2026-06-06
Branch: claude/trusting-curie-i2VHM
Trigger: a four-role multi-LLM academic review (R1 methodology, R2 metamorphic
testing, R3 SciML/numerics, DA adversarial) of the theory-lifted manuscript
returned 3x Major Revision + 1x Reject. This round acts on that review.

## Track A — text-only integrity fixes (no new evidence)

1. Dial back the two comparative/parity sentences the lift itself introduced:
   - Sec 2.6 "in a way a residual magnitude alone cannot" -> grounded in Sec 5.3
     evidence instead of asserted.
   - Sec 2.7 "two organizing devices" -> note the verdict's domain-violation axis is
     only qualitatively operationalized (interpretive structure pending calibration).
2. Acknowledge + rebut the circularity objection (predicate "fits" the 3 outcomes):
   Sec 6.1 now frames the symmetric-mesh run as an out-of-sample use of the predicate.
3. Mirror-y caveats: temporal dependence of the 10 frames + wide exact binomial
   interval [0.69, 1.00]; V/floor cannot fully separate model violation from geometric
   artifact on the asymmetric mesh.
4. Conservation caveats: reference divergence 0.037 not yet decomposed (operator vs
   solver vs non-solenoidal data); 1.5x threshold on 2 frames = non-regression guard,
   not a conservation measurement; abstract "passes" qualified.

## Track B — two cheap, real experiments on the existing SUT (no new SUT)

Both run against the committed checkpoint (sha256 cf281f85...) and the DeepMind eval
trajectory, via the same SUT inference path as the prior pilots.

- **B1 rollout-accuracy baseline** (`tools/run_rollout_accuracy.py`,
  `research_assets/runs/rollout-accuracy-baseline/`): one-step next-state error
  v_pred = v_t + delta_norm.denormalize(model(...)) (trainer convention, verified).
  RESULT: median relative L2 0.0216 (min 0.0116, max 0.0788, 9 transitions). The
  mirror-y OOD-stress violation (0.737) is ~34x this in-distribution accuracy ->
  substantiates "MRs answer a different question than accuracy" with real data.
- **B2 exact mirror-y on a provably symmetric mesh**
  (`tools/run_mirror_y_symmetric_mesh.py`,
  `research_assets/runs/mirror-y-symmetric-mesh/`): a synthetic structured channel mesh
  whose lower half is the reflected upper half, so the reflection is an exact involution
  (bijection True, node-type match 1.0, offset < 1e-12, edge-set invariant -- all
  asserted fail-closed before any verdict). The admissibility predicate RETAINS the
  exact relation. RESULT: exact mirror-y equivariance fails, relative L2 1.10 (verdict
  fail) on one input state. Oracle-free structural test; nonzero => genuine learned
  -symmetry violation, not geometry/accuracy artifact. Kills the circularity + the
  "self-downgraded probe" objection. Caveat: synthetic no-obstacle OOD mesh, one input.

## Ledger / evidence registration

- claim-ledger.yml: added C8-rollout-accuracy-baseline, C9-mirror-y-exact-symmetric-mesh
  (observed, scoped, with wording_forbidden guards); C3 updated (rollout-accuracy no
  longer a commitment-only baseline; expert/generic/LLM baselines still blocked).
- evidence-package.md, 22_stage2p5 audit: new inventory/claim-gate/numeric-trace rows.
- manuscript.md + ist-submission/main.tex: abstract, Sec 2.6/2.7, Sec 5.1/5.2/5.3/5.4,
  Sec 6.1 updated with PC8/PC9 and the two results; PDF rebuilt clean (296 KB).

## Acceptance (met)

- 102 unit tests OK (added markers for B1/B2 numbers + honesty caveats in both files).
- validate_experiment_protocol.py and validate_research_assets.py exit 0.
- claim-ledger parses C1..C9; every new evidence path exists on disk.
- PDF rebuilt, main.log clean (no overfull/underfull/undefined/rerun).

## Honest residual (still open after this round)

Still one SUT and one checkpoint. Cross-SUT, expert/generic/LLM baselines, and
seeded-fault detection remain blocked. Expected decision is still Major Revision, but
the circularity and accuracy-comparator objections are now answered with real evidence,
and the lift no longer overclaims.
