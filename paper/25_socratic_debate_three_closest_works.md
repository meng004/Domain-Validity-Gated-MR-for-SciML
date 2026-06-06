# Stage 5 — Socratic Debate Against the Three Closest Prior Works

Date: 2026-06-06
Source: 3 independent Sonnet sub-agents instructed to play the authors of the three closest
prior works and conduct a Socratic debate against this paper's three headline contributions.
Verified by the upstream deep-research pass (5 angles, fact-checked URLs).
Status: written record of the cross-examination and the concrete repairs it demands.

## Why these three (and not the Undermind picks)

`paper/09_undermind_related_work_contribution.md` named Qi 2025 (P1), Yu 2025 (P2),
Mandrioli 2025 (P3) as closest. `paper/citation_audit.md` and `paper/reference_ledger.md`
then downgraded the picks: `qi2025physicalfield` is UNVERIFIED (no DOI/publisher record);
`yu2025fluidvelocity` is PARTIAL/NOT_CITED_LEAD; `mandrioli2025cps` is VERIFIED but targets
CPS control, not SciML/PDE. The Undermind shortlist therefore cannot carry closest-work
debate weight on the current evidence ledger.

The upstream deep-research pass (5 angles) surfaced three independently verifiable works
that are demonstrably the strongest threats:

- **P1' Reichert et al. 2024 (HESS 28, 2505-2529)** — physics-derived MRs applied to a trained
  LSTM hydrologic surrogate; basin-stratified pass/fail; explicit physically inconsistent
  generalisation finding.
- **P2' Eniser et al. 2022 (ISSTA)** — "Metamorphic Relations via Relaxations": numerical
  tolerance is embedded inside the MR oracle as a calibrated relaxation, derived empirically.
- **P3' 2023 violation-attribution cluster** — Duque-Torres SANER 2023 + Towards a Complete
  Metamorphic Testing Pipeline 2023 + MetaTrimmer 2023: the "bug vs MR-inapplicability"
  dichotomy named, addressed as a constraint architecture, and automated data-drivenly.

Each is exactly the closest prior on one of the paper's three headline contributions.

## P1' Reichert 2024 (HESS) — debate on Contribution 3 (relation-indexed applicability map)

Authors' best defense (per the simulated debate): the predicate is a quantitative inequality,
not a qualitative domain condition; the applicability map is constructed a-priori by active
transformations, not derived post-hoc from passive aggregation.

Reichert's counter (consolidated): we already applied physics-derived MRs to a trained neural
surrogate; we stratified pass/fail by basin elevation and found the LSTM is consistent in
high-elevation basins and breaks under low-elevation warming — that is operationally a
relation-indexed applicability map, denser than what the paper has on one cylinder-flow
checkpoint. Our exclusion criteria (e.g. skip basins where forcing uncertainty dominates the
signal) are exactly the informal admissibility filter the paper formalises.

What survives the counter: the seeded-fault by-class localization (Reichert did not attempt
to map MR failures back to fault classes) is genuinely new.

Reichert's verdict as a reviewer: Major Revision (substantive missing citation; reframe).

## P2' Eniser et al. 2022 (ISSTA) — debate on Contribution 1 (admissibility predicate)

Authors' best defense: relaxations are an empirical reward-margin in RL; the admissibility
predicate is an a-priori condition on a discrete operator's truncation error; analytic floor
vs empirical floor is a real engineering shift.

Eniser's counter: at the level of principle this is a notation change. Both ask the same
question — what minimum threshold makes an MR verdict signal rather than noise? Calling it
a "predicate" rather than a "relaxation" is presentation. There is no theorem of soundness,
no decidability result, no composition lemma; the formalism is notational, not mathematical.

What survives the counter: identifying the *discretisation truncation error of the
measurement operator* (FEM/FVM) as the floor for SciML MRs. This connects numerical
analysis to MR calibration and is not present in Eniser. The contribution is a
**domain-specific instantiation that enables a-priori floor computation**, not a new
foundational principle.

Eniser's verdict as a reviewer: Major Revision (overclaimed novelty; reposition as a
SciML-specific extension of calibrated relaxation).

## P3' 2023 cluster — debate on Contribution 2 (two-dimensional verdict)

Authors' best defense: the 2D verdict makes the bug-vs-inapplicability split first-class in
the MR card, not just a post-hoc diagnostic; verdict cells are typed (out-of-relation-domain,
numerical-tolerance, inconclusive) rather than a binary skip/proceed.

Cluster's counter: Duque-Torres named the dichotomy as a research problem; the Complete MT
Pipeline introduced explicit MR constraints as a pipeline stage; MetaTrimmer automates the
domain-constraint derivation. The paper's "simultaneous 2D" is conceptually identical to a
sequential constrain-then-test architecture — and since the paper itself states the
domain-violation axis is currently only qualitatively operationalized, the plane is in fact
still sequential, just with the sequencing made implicit. A 2D plot whose y-axis is a sticky
note is not simultaneous measurement.

What survives the counter: the *typed ontology of the domain-violation axis* —
precondition / geometry / boundary-condition / operator inadmissibility — as named,
separable sub-dimensions calibrated to PDE-domain physics. No prior MR framework, including
this cluster, provides a typed ontology of *why* a domain constraint is violated in a
physics-governed ML context.

Cluster's verdict as a reviewer: Major Revision (reframe Contribution 2 as a physics-domain
instantiation of an established architectural pattern, plus the new typed ontology).

## Cross-cutting outcome (3/3 Major Revision; aligned with upstream deep-research)

The three simulated debates converge on the same diagnosis. None of the three headline
contributions, as currently framed, would survive a reviewer who knows the closest prior.
But each contribution has a defensible *narrower* form, and one element is genuinely
unprecedented across all three opponents.

### The headline contributions, repositioned (defensible measured form)

| As stated in README | After cross-examination |
|---|---|
| (1) Admissibility predicate (new principle) | A SciML-specific instantiation of Eniser's calibrated relaxation principle, grounded in the *a-priori-computable discretisation truncation error* of the measurement operator (a-priori floor vs Eniser's empirical floor). |
| (2) 2D verdict (structural novelty) | A physics-domain instantiation of the Duque-Torres / Complete-Pipeline / MetaTrimmer constraint-architecture, contributing a *typed ontology* of domain-inadmissibility sub-dimensions (precondition / geometry / BC / operator). |
| (3) Relation-indexed applicability map (active vs passive) | An extension of Reichert's basin-stratified applicability-map approach from hydrology LSTMs to mesh-based neural fluid surrogates, made explicit as an active-transformation product distinct from passive UQ/conformal residual fields. |

### The contribution the closest prior does NOT pre-empt

**Seeded-fault MR-as-detector with by-class fault localization**: the paper's MRs catch 5 of
10 injected mutants and *localise by MR class* (continuity -> boundary/scale faults;
symmetry -> physical-channel/adjacency faults; node-permutation -> exact-by-design, none).
None of the three closest works attempts this MR-to-fault-class mapping. Combined with the
honest single-SUT bounding, this is the most original element on the table. It should be
elevated in Section 1.2 (contributions) rather than left as a Section 5.3 paragraph.

### The unexplained finding the closest prior surfaced

Reichert noticed that the mirror-y MR fails with median relative L2 **0.737 on the
asymmetric eval mesh** but **1.10 on the synthetic symmetric mesh**. If the symmetric mesh
is a cleaner setting, the symmetric result should be smaller, not larger. The paper's
current text (normalizer 0.2% control, OOD binary-magnitude caveat) explains why 1.10 is
not a normalizer artifact but does *not* explain why it exceeds 0.737. The honest answer
appears to be that the synthetic symmetric mesh is more aggressively out-of-distribution
for a cylinder-trained surrogate (no obstacle, Poiseuille-like profile rather than vortex
shedding), so the magnitude reflects the OOD severity rather than a cleaner equivariance
measurement; the result should be read as a binary failure even on an admissible relation,
not as a magnitude comparison. This must be added in Section 5.3.

## Required citation sentences (verbatim from the debates)

1. **Reichert 2024 (HESS).** "Reichert et al. (2024, HESS 28, 2505-2529) applied
   physics-derived metamorphic relations to a trained LSTM hydrologic surrogate, stratified
   pass/fail outcomes by basin elevation to produce an implicit applicability map, and
   employed qualitative admissibility conditions to exclude tests where forcing uncertainty
   dominated the response signal; the present work formalises these practices as an explicit
   admissibility predicate, a two-dimensional verdict type, and a relation-indexed
   applicability map, and extends them from hydrology to mesh-based neural surrogates in
   computational fluid dynamics."

2. **Eniser 2022 (ISSTA).** "Calibrating MR tolerances to absorb system noise was introduced
   by Eniser et al. (ISSTA 2022) as *relaxations* for stochastic RL policy testing. The
   present work extends this principle to deterministic numerical surrogates by grounding
   the tolerance floor in the analytically computable truncation error of the discrete
   measurement operator, rather than empirically estimating it from model rollouts — a
   domain-specific instantiation that enables a-priori floor computation for scientific ML
   systems governed by known numerical schemes."

3. **2023 violation-attribution cluster.** "The separation of MR violations into model-fault
   and MR-inapplicability causes has been identified as an open problem by Duque-Torres
   et al. (SANER 2023), addressed architecturally via explicit MR constraints in *Towards a
   Complete Metamorphic Testing Pipeline* (2023), and automated data-drivenly by MetaTrimmer
   (2023); our two-dimensional verdict space instantiates this architectural pattern for
   physics-governed scientific ML by supplying a typed ontology of domain-inadmissibility
   drawn from PDE-domain preconditions, geometry constraints, boundary-condition
   compatibility, and operator-admissibility requirements."

## Concrete repairs (to be applied in this commit pair)

A1. References.bib: add `reichert2024hess`, `eniser2022relaxations`,
    `duqueTorres2023bugornot`, `velascoCompletePipeline2023`, `metaTrimmer2023` — all
    DOI-/arXiv-verifiable.
A2. citation_audit.md and reference_ledger.md: register the five new keys with
    verification-status notes.
A3. (next commit) manuscript.md and main.tex: insert the three required citation
    sentences into Section 2.4 (closest physics-MT-for-learned-surrogates), Section 3.3
    (admissibility predicate), and Section 3.5 (2D verdict); reposition Section 1.2
    contributions to the defensible-measured form; elevate seeded-fault by-class
    localization in the contributions list; add the mirror-y 1.10-vs-0.737 OOD-severity
    explanation in Section 5.3.

## Honest residual

This is still one SUT and one checkpoint; the repositioned contributions are narrower than
the README's original framing but each is grounded, defensible, and not pre-empted by the
three independently verifiable closest works. Realistic submission outcome at IST with
these repairs: Major revision at first round, but defensible toward Minor on second pass.
