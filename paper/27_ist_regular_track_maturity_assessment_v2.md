# Stage 7 — IST Regular Track Submission Maturity Assessment (v2)

Date: 2026-06-06
Inputs: two independent parallel agents (external IST 2023-2025 benchmark + internal
manuscript audit) plus the empirical-enhancement E1+E2+E3 results (claim ledger C11-C13).

**This document supersedes `26_ist_submission_maturity_assessment.md` for the regular-track
target. The earlier 7.5/10 verdict was conditional on the IST Metamorphic Testing special
issue (which closed in 2025). Without that channel, the benchmark is IST regular track,
and the bar is materially higher.**

---

## One-line verdict

The manuscript should **not** be submitted to IST regular track in its current form. Two
independent analyses (external IST 2023-2025 benchmark, internal manuscript audit) agree:
the empirical strength is below the regular-track norm and the probability of first-round
rejection or major revision is ≥80%. Two viable paths exist:

- **Path A — Strengthen, then submit IST** (4-6 weeks of additional work).
- **Path B — Switch venue to JSS** (1-2 weeks of repositioning).

STVR is excluded per standing user constraint.

---

## Maturity scorecard (v2, regular-track benchmark)

| Dimension | IST 2023-2025 typical bar | This manuscript | Status |
|---|---|---|---|
| Independent SUTs / datasets | ≥3 independent SUTs or 1 SUT × multiple datasets | 1 architecture family (MGN) × 1 dataset (DeepMind cylinder-flow); K=6 checkpoints share one family | 🔴 severe gap |
| Baseline comparison | 10/10 sampled IST 2023-2025 papers have ≥1 baseline; ≥2 common | 0 baselines; PC3 still blocked (expert MR, generic MR generation, LLM candidates) | 🔴 most critical |
| Mutant / seeded-fault catalogue | Mutation work typically ≥20-30 mutants, mature tooling (mutmut / DeepMutation++) | 10 mutants, re-implemented from witness taxonomy, author-acknowledged non-adversarial | 🟡 small |
| Statistical inference | Wilcoxon / Mann-Whitney + Cliff's δ or Vargha-Delaney Â12, 10-30 random repeats | Bootstrap CI (B=2000) + Wilson CI; 5 input-permutation seeds; no significance test, no effect size | 🟡 approaching adequate |
| Replication package | Strongly encouraged (not strict); near-universal in recent accepts | claim ledger + manifests + raw outputs + validators + 105 regression tests | 🟢 strength |
| Threats to validity / integrity discipline | Verdecchia et al. IST 2023 is a reviewer touchstone | Cited; fail-closed validators; multi-role reviewer simulation; claim-ledger forbid/allow | 🟢 above norm |
| Format / scope fit | Structured abstract; ≤ word limit; SE-first framing | Compliant (43 pages PDF, structured abstract, SE framing) | 🟢 ready |

Net maturity (regular track): **≈ 5.5/10**, mid-low percentile of recent IST regular-track
accepts (≈ 30-40th percentile).

---

## What the empirical extension (E1+E2+E3) actually added

The most recent work (this session) extended evidence in three directions; the honest
delta against the regular-track bar is:

- **C11 multi-checkpoint replication (E1).** K=6 SUTs is up from K=1, with bootstrap 95%
  CIs. But S0–S3 are training-seed replicas of one base config (author admits "shares
  more variance than independent SUTs would"); only S4 and S5 are configuration variants.
  This closes the "single-checkpoint" objection but **does not** close the "single
  architecture family" objection.
- **C12 operator-floor O(h) sweep (E2).** Slope 0.988 / 0.995, R² = 1.000 — clean theory-to-
  empirics alignment, but scope is one mesh family + one analytic field. A reviewer will
  ask why the calibration was not done on a non-structured or obstacle-bearing mesh.
- **C13 fault-detection robustness (E3).** Wilson 95% CIs across (K=6 SUTs × 5 input
  seeds × 10 mutants × 3 detectors). Two genuine new insights: (i) PC_zero_vy
  non-monotone severity (partial p∈{0.25,0.5,0.75} detected 6/6; canonical p=1.0
  detected 0/6 because uniform vy=0 is itself mirror-y-symmetric), (ii)
  MA_permute_edges configuration-sensitive (S0–S3 detect 20/20, S4/S5 detect 0/10).
  These are publishable structural insights, but the underlying catalogue is still 10
  mutants and still non-adversarial.

**Bottom line on E1+E2+E3:** they upgrade the work from "single-checkpoint pilot" to
"K=6 within-family case study with calibrated operator floor and bounded detection
profile." That is a real improvement, but it does not by itself meet IST regular-track
multi-SUT / multi-baseline norms.

---

## Predicted first-round verdict (if submitted as-is to IST regular track)

- Major Revision: ≈ 55%
- Reject and Resubmit: ≈ 30%
- Minor Revision: < 5%
- Accept: ≈ 0%

### Predicted reviewer comments (most likely to appear verbatim)

1. *"The empirical evaluation is limited to a single architecture family (MeshGraphNets)
   on a single dataset. The K=6 'multi-checkpoint roster' largely consists of
   training-seed replicas of one base configuration, which the authors themselves
   acknowledge 'shares more variance than independent SUTs would.' Without at least one
   cross-family SUT (e.g., a PINN or FNO surrogate on a comparable problem), the central
   claim that the workflow generalizes to 'SciML surrogates' is not supported."*
2. *"All four planned baselines (expert MR design, generic MR generation, LLM-assisted
   candidates, rollout accuracy) except the last remain marked as 'blocked protocol
   commitments.' The counterfactual argument in §6.1 cannot substitute for a head-to-head
   comparison. As stands, the paper cannot quantify what the domain-validity rubric adds
   over conventional expert MR elicitation."*
3. *"The seeded-fault catalogue is 're-implemented from the read-only Minimum-MR-SubSet
   witness taxonomy,' which the authors note is 'not adversarial to these MRs.'
   Detection rates measured against a non-adversarial, author-implemented catalogue
   cannot bound real-world fault-detection effectiveness."*

---

## Path A — Strengthen, then submit IST (4-6 weeks)

Highest-ROI items, in priority order:

| # | Action | ETA | Closes |
|---|---|---|---|
| A1 | One cross-family SUT pilot: a PINN or FNO on cylinder flow or Burgers; run the same 3 MRs + rollout-accuracy comparator. Even a single external data point ("MR does / does not apply") shrinks the external-validity attack surface. | 1-2 weeks | Reviewer comment #1 |
| A2 | Expert-MR baseline mini-study: N=2 authors role-play "naive expert" (no rubric), write MR candidates, record which ones the rubric would have rejected / downgraded. Lifts PC3 from "blocked" to "qualitative comparator observed." | 3-5 days | Reviewer comment #2 |
| A3 | Mutant catalogue extension to ≥25 + 1-2 adversarial mutants (subtle weight perturbations targeting the mirror-y / conservation thresholds); formalize §5.6 by-class mapping as precision / recall by fault class. | 3-5 days | Reviewer comment #3 |
| A4 | Statistical-inference upgrade: ≥10 random repeats per (MR, mutant) cell; Wilcoxon + Cliff's δ; cite Empirical Standards for SE Research. | 2-3 days | Implicit IST norm |

Post-strengthen prediction: Major Revision → Borderline Accept; Accept probability 15-30%.

## Path B — Switch venue to JSS (1-2 weeks)

The external benchmark explicitly observes that "single deep case study + scientific-
software angle" fits JSS or SoftwareX better than IST regular track. Recommendation:

- **JSS (Journal of Systems and Software, Elsevier, IF ≈ 3.5).** Same Elsevier ecosystem
  as IST, comparable rank, but historically friendlier to scientific-software V&V and
  to in-depth case studies. Repositioning effort is ~1-2 weeks (template + framing).
- **SoftwareX (IF ≈ 2.6).** Artifact-paper style; would require restructuring the paper
  as an artifact contribution, which is a poorer fit for the methodological claims.

Recommended within Path B: **JSS** — sell K=6 + O(h) calibration + non-monotone severity
finding + integrity engineering as deep case-study strengths rather than competing on
multi-SUT breadth.

---

## Standing user constraints honored

- STVR excluded per `stvr不考虑`.
- Minimum-MR-SubSet remains read-only (E1 wrapper writes only to this repo).
- No unsubstantiated claims; every conclusion above is backed by either a claim-ledger ID,
  a file path, or an external IST benchmark citation.

---

## Recommended next step

The decision belongs to the user. The three concrete options are:

- **Option 1 — Path A.** Allocate 4-6 weeks; start with A1 (cross-family pilot) since it
  has the largest single ROI.
- **Option 2 — Path B.** Allocate 1-2 weeks; reposition the existing manuscript for JSS.
- **Option 3 — Hybrid.** Run only A2 + A3 (the cheap baseline + adversarial mutants, ~1
  week total) and submit to JSS rather than IST. Gains some of A's defensive value
  without the cost of A1.

Whichever path is chosen, the previous `26_ist_submission_maturity_assessment.md` should
be treated as obsolete for the regular-track target.

---

## Appendix A — External benchmark sources

- [dblp: Information & Software Technology index](https://dblp.org/db/journals/infsof/index.html)
- Verdecchia et al., "Threats to validity in software engineering research", IST 164 (2023), DOI 10.1016/j.infsof.2023.107329
- SFIDMT-ART (IST 175, 2024), DOI 10.1016/j.infsof.2024.107528
- CriticalFuzz (IST 2024)
- Stratified random sampling for NN test input selection (IST 2023)
- Automated engineering of domain-specific MT environments (IST 2023)
- Empirical study on metamorphic testing for recommender systems (IST 2024)
- MT for textual and visual entailment (IST 2025)
- LLM + mutation testing (Dakhel et al., IST 2024)
- IST Guide for Authors
- Empirical Standards for SE Research (SIGSOFT)

## Appendix B — Internal evidence pointers

- Manuscript: `paper/manuscript.md` §5.3-§5.7, §6, §7, §8
- IST submission: `paper/ist-submission/main.tex`
- Claim ledger: `research_assets/experiments/claim-ledger.yml` (C1-C13)
- Empirical-extension plan: `docs/superpowers/plans/2026-06-06-empirical-enhancement-E1E2E3.md`
- E1 aggregate: `research_assets/runs/multicheckpoint/e1_aggregate.json`
- E2 report: `research_assets/runs/operator-floor-sweep/operator_floor_report.json`
- E3 report: `research_assets/runs/fault-robustness-e3/fault_robustness_report.json`
- Prior maturity assessment (superseded for regular track): `paper/26_ist_submission_maturity_assessment.md`
