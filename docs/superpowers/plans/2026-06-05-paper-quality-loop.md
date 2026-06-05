# Plan: Paper Quality Loop — Domain-Validity-Gated MR Paper

Date: 2026-06-05
Branch: `codex/paper-quality-loop`
Goal (session): drive `paper/manuscript.md` toward submission-ready quality for IST
via a loop: plan → implement → multi-role academic review → analyze → iterate.
Hard constraints: no fabricated evidence; no fabricated citations (cite only
VERIFIED refs per `paper/reference_ledger.md`); keep evidence-gating and validators
green; all reported numbers must trace to committed artifacts.

## Target ("highest goal")

A coherent, internally consistent, honestly-scoped IST methods paper whose
contributions, RQs, method, scoped pilot results, and limitations all agree, with
clear tables, a reproducibility package pointer, and a references section that does
not overclaim verification.

## Gap analysis (reviewer lens) — Round 1 targets

1. **Coherence break (highest):** Abstract Conclusion, §1.2 (contribution 4),
   §6, §8 still use "planning-stage / no results yet" framing that contradicts the
   scoped pilot results in §5.1. Reframe from "registered report" to
   "method + scoped pilot case study; full cross-SUT study future work."
2. **Missing tables:** (a) rubric decision table over the four real candidates
   (node permutation = retained; mirror-y = retained-OOD-stress; divergence =
   deferred; viscous time reversal = rejected) — direct RQ1 evidence; (b) pilot
   results table over the three executed MRs with numbers and verdict classes.
3. **SUT reconciliation:** §4.1 plans three SUTs but never names the one actually
   executed (the trained MeshGraphNet from `Minimum-MR-SubSet`, checkpoint
   sha256 `cf281f85…`). Mark one realized, two blocked.
4. **RQ4 honesty:** baseline comparison is blocked; state that the case study
   currently demonstrates the rubric/asset/verdict workflow and one set of
   relation-level verdicts, with baseline comparison as future work.
5. **Reproducibility package subsection:** point to the committed runners,
   manifests, metric ledgers, validators, and CI.
6. **References:** add the one VERIFIED citation (`mandrioli2025cps`); present the
   PARTIAL/UNVERIFIED items only as leads pending verification (per guardrails);
   keep the verification limitation explicit.

## Round 1 steps

- S1. Reframe planning-stage language → method + scoped pilot case study
  (Abstract Conclusion, §1.2 C4, §6.1/6.2, §8). Keep all "still blocked" honesty.
- S2. Add rubric decision table to §3.3 (four real candidates, four decisions).
- S3. Add pilot results table to §5.1 (three MRs, metric, value, verdict, scope).
- S4. Reconcile SUT story in §4.1 + a realized-subject note.
- S5. Scope RQ4 honestly (§1.1, §1.2 C4, §4.3).
- S6. Add §4.7 Reproducibility package + §5.3 artifact pointer.
- S7. References: cite `mandrioli2025cps`; restructure §9 to separate verified vs
  leads; keep limitation.
- S8. Bump draft banner to v0.4; run validators; commit.

## Review (Round 1 → analysis)

Spawn four sonnet academic-reviewer personas in parallel:
- R1. Software-testing / metamorphic-testing methods reviewer (IST regular).
- R2. SciML / CFD domain expert (cylinder flow, MeshGraphNets, conservation/symmetry).
- R3. Empirical methodology, claims, and statistics auditor.
- R4. Editor / venue-fit, novelty, structure, and reproducibility reviewer.
Synthesize, rank issues, decide whether "highest goal" met; else plan Round 2.

## Out of scope this loop

- No new SUT, no baseline runs, no second checkpoint (still blocked).
- No fabricated citations or upgraded reference statuses without real verification.
