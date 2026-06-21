# 51 — Post-IST Tier-1 research program (validity–coverage as a calibrated, real-fault-validated theory)

> Date: 2026-06-21
> Status: **Backlog anchor — NOT an IST task, NOT started.** Requires user go-ahead.
> Relation to current submission: forbidden-by-design for the IST paper. The IST
> `claim-ledger.yml` explicitly bars these as `wording_forbidden` on C47/C50/C51/C52
> ("validated/quantitative predictive coverage model", "cross-MR calibration",
> "real-world fault-detection rate"). Pursuing them is a *new paper with a different
> contribution claim*, not a strengthening of the IST manuscript.

## Core thesis

The IST paper establishes the validity–coverage link **qualitatively**: the same
admissibility gate that decides whether an MR yields a meaningful verdict also fixes
which faults that MR can detect (manuscript §440; claims C37/C47/C50). This program
asks whether that qualitative, falsifiable principle can be upgraded into a
**calibrated, real-fault-validated, predictive theory of MR test adequacy for SciML
surrogates.**

This is an *operationalization → predictive-theory-plus-validation* jump. The IST
paper is a software-V&V **method** paper (auditable workflow); this is a
**test-adequacy theory** paper (predict + validate coverage). Different contribution
claim, different evidence burden, different venue tier.

## The three forbidden atoms → three research objects

| IST state (qualitative, capped) | Tier-1 target (ledger-forbidden) | Why a new object |
|---|---|---|
| duality is qualitative; C50 predictive-completeness is **binary** (blind / not-blind), 2 families, 0 falsifiers | **Calibrated predictive coverage model** `C: (admitted MR set S, fault f) → P(detect | S, f)`, derived a-priori from invariant-perturbation geometry, **calibrated** (predicted ≈ observed frequencies), multi-SUT validated | needs a **measure on fault space** + reliability-diagram calibration; graded coverage probability, not a binary blind flag |
| D = m/(m+1) **per-relation**; "D values cannot be averaged or ranked across MR classes" (§3.5/§5.1) | **Cross-class domain-distance metric** `D_cal`: one scale across symmetry / conservation / permutation / scaling, so domain-violation is comparable across relations | a **class-independent unit** for "distance outside the validity domain" — general solvability unknown |
| 10-mutant author catalogue, gross corruptions; "not a real-world defect-rate benchmark" (Threats) | **Real SciML fault corpus + detection-rate estimate** with a defensible sampling frame and external validity | real SciML defect corpora barely exist; building one is a **Defects4J-for-SciML**–class community resource |

## Research questions

**Main RQ (Tier-1).** Can a SciML surrogate's admissible MR set, from the
physics/discretization of its relations alone, yield a **calibrated predictive
coverage model** — predicting which *real* faults a suite will and will not detect,
with validated confidence — together with a **cross-relation domain-distance metric**
that makes verdicts comparable across MR classes?

- **RQ-A (coverage-as-theory).** Formalize the coverage geometry as a predictive
  model derived a-priori from admitted invariants; validate on a held-out,
  naturally-sampled fault population with calibrated error bars. *(upgrades C47/C50)*
- **RQ-B (cross-class calibration).** Derive `D_cal` so domain-violation magnitude is
  one coordinate across MR classes — the concrete cash-out of the manuscript's
  "cross-relation calibration is left to future work". *(upgrades §3.5 D-axis)*
- **RQ-C (real-fault coupling).** Build a real SciML fault corpus, estimate the
  suite's true detection rate, and test whether **seeded faults couple to real
  faults** — Just et al.'s mutant-vs-real-fault question (FSE 2014), posed for
  MR/SciML. *(upgrades C10/C50 seeded-fault stress test)*

**Prerequisite (geometry gate).** A rigorous a-priori divergence-floor bound for
**arbitrary unstructured meshes** (IST has closed-form for the deployed structured
mesh + one Delaunay topology; §5.5 / claim "general unstructured-mesh bound remains
future work"). RQ-A's coverage prediction cannot claim mesh-generality until the
admissibility tolerance generalizes.

## Why Tier-1 (TSE / TOSEM), not an IST increment

1. **Contribution-type jump.** IST = operationalization (the paper explicitly
   declines superiority and predictive claims, scope framing in `README.md`). Tier-1
   gatekeeps on conceptual/theoretical advance + rigorous external validity — exactly
   what this adds and the IST paper deliberately does not.
2. **Joins a recognized canon.** Test-adequacy theory; mutation-vs-real-fault
   coupling (Just et al. FSE 2014 → TSE line); MR adequacy & prioritization (Kanewala
   line: `srinivasan2022`, `saha2019`, already in `references.bib`). A calibrated,
   real-fault-validated MR-coverage-adequacy theory for SciML is a citable extension
   reviewers recognize on sight.
3. **Scale and risk are Tier-1 grade.** Multi-SUT + real-fault corpus + statistical
   power + calibration validation = multi-year, multi-person, with genuine
   falsification risk: `D_cal` may have no clean general solution; real SciML defects
   may be too few for a rate; the coverage model may be falsified; seeded and real
   faults may **not couple** (a valuable negative result that would also bound the
   IST duality's practical reach).
4. **It changes the paper's identity**, not extends it.

## Venue and paper-splitting

| Sub-result | Standalone venue | Notes |
|---|---|---|
| RQ-C real-fault corpus | ISSTA / ICSE / FSE (benchmark/tool, CCF-A) or EMSE | community resource; strengthens any later submission |
| RQ-B `D_cal` calibration theory | focused TSE / TOSEM methodology paper | the theoretical heart |
| RQ-A + B + C combined | **TOSEM (best, double-blind/acmart) or TSE (single-blind/IEEEtran)** | flagship; CAS 1区 Top / CCF-A |
| Prerequisite floor bound | numerical-analysis note, or folded into RQ-A | risk: drifts toward CFD/NA, out of SE venue scope if over-weighted |

**Most realistic sequencing.** RQ-C corpus first (independently publishable, and feeds
back to harden any submission) → RQ-B calibration theory → synthesize A+B+C into the
TSE/TOSEM flagship. The prerequisite floor bound runs in parallel as theory.

## Decision status

- **For the current IST submission: zero impact, zero necessity.** This is a
  post-acceptance / separate-line direction, not an IST revision item.
- **Go/no-go is a research-line decision, not a writing task** — needs user sign-off.
- If started, the first concrete feasibility gate is **RQ-C**: does a harvestable
  population of real, buggy-vs-fixed SciML surrogate faults exist at sufficient
  scale? If not, the real-world-rate leg (and much of the Tier-1 case) does not close.

> Reference grounding (Just et al. FSE 2014; Kanewala adequacy line) is by lineage for
> planning; formal §8 verification required before any of these enters a real proposal
> or manuscript.
