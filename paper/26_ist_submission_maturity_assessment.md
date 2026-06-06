# Stage 6 — IST Submission Maturity Assessment (deep-research grounded)

Date: 2026-06-06
Inputs: three IST-focused deep-research search passes (journal scope/guidelines/desk-reject;
recent IST testing-paper norms 2023-2026; SciML-in-SE-venue scope-fit risk) + the paper's
current state (post round-4, ~9.4k words) + the four-round multi-role review history.

## Verdict: submittable now (maturity ~7.5/10), "scoped empirical case-study methods paper"
Realistic outcome: Major -> Minor. Desk-reject risk LOW given the current SE-first framing.
Best target: the IST **Special Issue on Metamorphic Testing** (explicitly solicits real-world
MT case studies), which lowers the single-SUT bar relative to the regular track.

## Scorecard vs IST's real bar

| Dimension | Rating | Evidence |
|---|---|---|
| Scope fit | READY | IST covers "software testing and V&V"; runs an MT special issue. TSE-2024 editorial confirms testing of ML components is in-scope at peer SE venues. Paper frames "testing contribution first, SciML as application context" (the recommended tactic). |
| Format compliance | READY | Structured abstract (mandatory) present; ~9.4k words < 15k limit; no desk-reject trigger present. |
| Single-SUT acceptability | OK (precedented) | IST repeatedly publishes single-SUT MT papers (Stockfish chess engine 2023+2025; MT-Nod single ADS; LKAS single ADAS). Single-system is a reviewer external-validity concern, not a desk-reject. |
| Evidence rigor vs IST norm | MID-HIGH | IST MT norm: 1-3 SUTs, MR-violation rate as fault proxy. This paper: 1 SUT but multiple MR classes + rollout comparator + symmetric-mesh out-of-sample + real seeded-fault (5/10, which many IST MT papers omit) + claim-ledger/reproducibility discipline. Rigor above the modal IST MT paper; system count below. |
| Novelty | DEFENSIBLE | Repositioned (round-4) with three closest-prior citations; no SciML neural-surrogate MT paper found in IST 2023-26 (genuine gap); typed-classification verdict + seeded-fault by-class localization unprecedented. |
| Reproducibility | STRENGTH | tools/ + runs/ + validators + 105 tests + sha256 checkpoint; exceeds most IST MT papers. |
| Related work | READY | 25 citations incl. Reichert/Eniser/Duque-Torres cluster with explicit deltas. |

## Decisive risks and status
1. SciML-as-non-SE desk-reject (real per deep-research) -> MITIGATED: abstract leads with the
   oracle problem; Target&Scope states "testing contribution first". Keep SE vocabulary leading.
2. Single-SUT external validity -> HANDLED honestly (threats to validity + blocked-claims).
3. "exploratory/preliminary" archival-journal risk -> NOT PRESENT in submission files (only the
   `lin2020exploratory` citation key appears); positioning uses "empirical" framing already.
4. gopakumar2025calibrated bib had a wrong author list -> CORRECTED this stage (verified
   authors + arXiv:2502.04406, ICML 2025).
5. Five-contribution fragmentation (R1's "largest rhetorical vulnerability") -> CONSOLIDATED to
   three this stage (rubric+MR-card merged; case study demoted to evaluation vehicle).

## Honest ceiling
Single SUT / single checkpoint is the structural ceiling (no second checkpoint exists in this
environment). It caps the paper at "scoped case-study methods paper" -- a fit for the IST MT
Special Issue, but Major-revision-grade on the regular track. Reaching a "strong empirical"
tier requires a second SUT, which is out of scope here.

## Sources (deep-research)
- IST guide for authors / scope: https://www.sciencedirect.com/journal/information-and-software-technology/publish/guide-for-authors
- IST Special Issue on Metamorphic Testing: https://www.sciencedirect.com/special-issue/317272/special-issue-on-metamorphic-testing
- Single-SUT IST MT precedents: chess-engine MT https://dl.acm.org/doi/10.1016/j.infsof.2023.107263 ; replication https://www.sciencedirect.com/science/article/abs/pii/S0950584925000187 ; MT-Nod https://www.sciencedirect.com/science/article/abs/pii/S0950584924002647
- SE-for-AI scope (TSE 2024 editorial): https://sigsoft.medium.com/exploring-the-scope-of-software-engineering-for-ai-insights-from-ieee-tse-0f60e464b3da
- Interdisciplinary SE publishing risk: https://arxiv.org/abs/2501.06523
- Gopakumar calibrated PI-UQ (corrected ref): https://arxiv.org/abs/2502.04406
