# 69 · Phase 0 Evidence Gate for TOSEM Refactoring

> Date: 2026-07-02. Purpose: execute Phase 0 of the TOSEM phase-loop plan before manuscript rewriting. This file separates claims that are already ledger-licensed from claims that remain blocked or insufficient. Source files read: `paper/66_pathA_tosem_execution_program.md`, `paper/67_deepresearch_verdict_and_ABC_program.md`, `paper/68_phaseC_refocus_skeleton.md`, `manuscript/main.tex`, and `research_assets/experiments/claim-ledger.yml` copied into `/private/tmp` for inspection.

## Gate verdict

The manuscript may be reframed around a numerical-decidability / operator-floor admissibility criterion, but it may not yet claim a general unstructured-mesh soundness theorem or any superiority over accuracy/UQ/baseline monitors.

Current state:

- Phase C is ready as a writing refocus: the core problem and novelty delta are one-sentence expressible.
- Phase B is not complete: the existing ledger only licenses a concrete structured-mesh analytic bound (C32) and a two-topology observed stability result (C44), while explicitly forbidding arbitrary unstructured-mesh generalization.
- Phase A is partially supported: C38, C42, C51, and C52 license complementarity and measured gate value, but not superiority.
- Ledger discipline is strong and must remain a hard gate: C42, C51, and C52 explicitly forbid baseline superiority and general fault-detection/reliability rates.

## Claim status table

| Candidate TOSEM claim | Status | Licensed wording | Forbidden wording / gap |
|---|---|---|---|
| Numerical decidability is a necessary admissibility condition for executing a SciML MR as a valid oracle-free test. | qualified | May be used as the central framing if stated as a criterion implemented by the four-condition gate and demonstrated on bounded subjects. | Do not state that all SciML MR soundness is solved. |
| Operator-floor analysis upgrades the gate from empirical tolerance setting to a derived floor for the concrete P1 divergence setting. | observed | C32 licenses a closed-form predictor and a-priori upper bound for the concrete y=0-symmetric structured triangular channel mesh. | C32 forbids arbitrary unstructured cylinder meshes or general fields. |
| Operator-floor behavior is stable across two mesh topologies. | observed | C44 licenses topology-stability over the structured mesh and one unstructured Delaunay jittered-grid topology for one analytic field. | C44 forbids generalization across arbitrary mesh families, geometries, or analytic fields. |
| The validity gate has measured value beyond bookkeeping. | observed | C42/C52 license measured gate value: admitted templates avoid baseline false positives while rejected templates false-alarm on fault-free SUTs in the studied settings. | Do not call this superiority, outperformance, or evidence that accuracy/UQ are inadequate. |
| MR checks and accuracy monitors are complementary. | observed | C38/C42/C52 license complementarity on bounded SUT/catalogue settings. | Do not claim the MR suite is better than accuracy monitoring. |
| Coverage follows the admitted MR set qualitatively. | qualified/observed synthesis | C47/C50/C51 license a qualitative falsifiable validity-coverage duality over committed artifacts. | Do not claim a validated quantitative coverage model, detection probabilities, or real-world fault-detection rate. |
| Realistic/non-tailored faults support the structural blind-region argument. | observed | C48/C49 license emergent 2x2 partitions and confirmed blind regions for FNO/PINN realistic-fault catalogues. | Do not claim broad real-world fault recall or exhaustive blind-region proof. |
| TOSEM-ready general mesh soundness theorem. | insufficient | Can be planned as Phase B. | Must not enter Abstract, Contributions, Results, or Conclusion until a new theorem/claim and proof artifact exist. |

## Main manuscript implications

Allowed Phase C rewrite:

1. Replace workflow-first framing with criterion-first framing.
2. Make C1 the head contribution: numerical-decidability / operator-floor admissibility as a soundness precondition.
3. Demote MR cards, typed verdicts, and claim ledgers to implementation and audit mechanisms.
4. Move measured gate value and complementarity to supporting evidence, with no superiority wording.
5. Preserve limitations: no arbitrary unstructured-mesh theorem, no general reliability, no real-world fault-detection rate.

Blocked until Phase B:

1. "We prove a general unstructured-mesh soundness theorem."
2. "The operator-floor bound holds for arbitrary unstructured meshes."
3. "The method is TOSEM-stable because the theory is closed."

Blocked until additional Phase A evidence:

1. Any high or general fault-detection recall.
2. Any baseline superiority ranking.
3. Any claim that the by-class fault-localization pattern generalizes uniformly across SUTs.

## Next Loop

Phase C can proceed immediately, but its manuscript wording must remain honest: "criterion", "precondition", "bounded soundness evidence", and "closed-form floor for a concrete P1 setting" are licensed; "general theorem" remains a Phase B target.
