# Stage 10 — Root-Cause Analysis + Uncompromising IST Gap-Closure Plan

Date: 2026-06-07
Trigger: After the four-role IST review simulation (Stage 9) returned Major
Revision, the user asked: *the manuscript was supposed to be IST-ready before
we ran E1+E2+E3 and rewrote the front matter — where did the gap come from?*

This document does three things:
1. Verifies the manuscript has **not** drifted from the README thesis.
2. Identifies the three real sources of the gap.
3. Lays out a no-compromise plan to close that gap and submit to IST regular
   track.

The standing constraints are honored: STVR is excluded, `Minimum-MR-SubSet`
remains read-only, every commitment below maps onto a tracked artifact or a
ledger ID.

---

## 1. The manuscript has not drifted from the README

| README element | Where in the manuscript | Drift? |
|---|---|---|
| Thesis #1: admissibility predicate (4-clause; physical/software basis ∧ preconditions ∧ BC/output mapping ∧ numerical decidability) | §3.3 rubric, §3.4 condition (iv), §5.5 operator-floor calibration | No. README only had the concept; §5.5 now empirically calibrates the numerical-decidability gate (slope 0.988, R²=1.000). |
| Thesis #2: two-dimensional verdict, with the domain-violation axis "currently operationalized qualitatively; a calibrated continuous score is future work" | §3.5 + Fig 3 (qualitative bin) | No. R2's Major comment M2 — "the domain axis is qualitative" — is **literally what the README already declared as future work**. |
| Thesis #3: relation-indexed applicability map, with current evidence "one bounded within-SUT point on such a map, not a completed map" | §5.3 within-SUT, §5.4 K=6 within-family | No. K=6 multi-checkpoint is still inside the README's own "one bounded point" envelope; it tightens it from K=1 to K=6 but does not exit one architecture family. |
| Evidence boundary list (within one SUT / one checkpoint) and the "Still blocked / not claimed" list (cross-SUT, expert-MR / generic-MR / LLM baselines, fault-detection rates, validated localization, runtime, reliability, accuracy) | `claim-ledger.yml` C3 blocked; `wording_forbidden` rows | No. Every "blocked" element in the README still maps to a ledger entry the manuscript honors. |
| Positioning: "intended venue is a software V&V method paper (e.g. **IST / JSS**); not framed as outperforming accuracy or UQ" | Abstract + §7 | No. Both IST and JSS are README-allowed venues. |

**Verdict: the manuscript executed the README faithfully. The Major
Revision in Stage 9 is not a drift from the design.**

---

## 2. Three real sources of the gap

### Source 1 — The early "IST-ready at 7.5/10" judgment was conditioned on a venue that no longer exists

Doc 26 (Stage 6) scored the submission at 7.5/10 against the IST **Metamorphic
Testing special issue**. That special issue **closed in 2025**. Doc 27
(Stage 7, regular-track v2) explicitly supersedes doc 26 and re-scores at
≈ 5.5/10 against the regular-track benchmark, predicting:

- Major Revision ≈ 55 %
- Reject and Resubmit ≈ 30 %
- Minor Revision < 5 %
- Accept ≈ 0 %

**Stage 9's four-reviewer simulation today returned Major Revision, exactly
matching doc 27's prediction.** The "we already evaluated IST-ready" memory
is from doc 26 — a judgment whose premise no longer holds. Doc 27 was the
correction.

### Source 2 — Doc 27's Path A had four headline items; only one and a half were executed

Doc 27 (paper/27_ist_regular_track_maturity_assessment_v2.md, lines 102–110)
lists the highest-ROI items for IST regular-track:

| Doc-27 ID | Action | Status today |
|---|---|---|
| **A1** | One cross-family SUT pilot (PINN or FNO, same cylinder-flow problem; one external data point) | **NOT DONE** |
| A2 | Expert-MR baseline mini-study (N=2 authors role-play "naive expert") | NOT DONE |
| A3 | Mutant catalogue extended to ≥ 25 + 1–2 adversarial mutants | NOT DONE |
| A4 | Statistical upgrade: ≥ 10 random repeats; Wilcoxon + Cliff's δ; Empirical Standards | **partial** — bootstrap and Wilson CIs done in E1+E3; non-parametric tests and effect size still missing |

Doc 27 ranks A1 as **"highest ROI single item"**. In the four-role review:

- Reviewer #1 (Empirical SE methodology) Major comment M1 = "single
  architecture family / single dataset" → asks for at least one contrasting
  family.
- Reviewer #2 (Domain expert) Major comment M5 = "case study scope vs.
  abstract framing tension" → asks for one external family.

**Two independent reviewers ranked A1 as their top hot spot. A1 is exactly
the doc-27 item never executed.** The gap is concrete and pre-identified.

### Source 3 — The single most transferable empirical finding (R3 non-monotone detection) post-dates the README, and the README/Abstract/Highlights never absorbed it

R3 — "uniform $v_y = 0$ is itself mirror-y-symmetric, so the worst severity
$p = 1.0$ is detected 0/6 while intermediate $p \in \{0.25, 0.5, 0.75\}$ are
detected 6/6" — is an E3 byproduct (added 2026-06-06, after the README and
after the original Abstract). It is the finding Reviewer #2 names as
"transferable to the MT community, more valuable than the rubric itself."

The README's thesis triple still ends at "applicability map (current point,
not completed map)" and never names this kind of structural-symmetry
detection blind region as a contribution. The Abstract Results paragraph
mentions it implicitly ("MRs catch 5 of 10") but Highlights does not, the
Conclusion does not, and §1 contributions do not.

**The README is not wrong — it is simply older than the strongest finding
the manuscript now carries.** This is the third gap source.

---

## 3. Distance to IST acceptance, measured against each Stage-9 hot spot

The four reviewers between them identified 5 consensus hot spots. The
distance to "no-reviewer-can-block-this-on-that-axis" is:

| Hot spot | Current state | Distance to IST defensible |
|---|---|---|
| External validity | K=6 within MGN family, one dataset | **Need 1 cross-family pilot (A1)** + Threats-to-Validity citation to Verdecchia 2023 |
| Rubric novelty overstated | rubric framed as headline contribution | **Need re-centering**: operator-floor-grounded tolerance gate + R3 non-monotone become the headline; rubric becomes "systematic packaging + one SciML-specific gate" |
| Headline mis-framed | §5.5 + §5.6 buried in Results | **Need re-write** of §1 contributions, Abstract Results, Highlights |
| Claim ledger invisible | hidden plumbing | **Need promotion**: 1 sentence in Abstract Method, 1 Highlight, 1 §1 contribution bullet |
| Baselines absent | 3 of 4 planned comparators blocked | **Need A2 (LLM-candidate baseline)** + 1 expert-MR mini-study |

Plus three submission-system blockers (word count, anonymization, title
length) that are independent of content.

---

## 4. No-compromise IST gap-closure plan

Phases are sized by reviewer impact, not by ease. The order is fixed by
prerequisite (P0 unblocks Editorial Manager; P1 unblocks reviewer assignment
on the merits; P2 closes the methodological deficits).

### Phase P0 — Editorial Manager unblockers (5–7 working days)

| ID | Item | Acceptance gate |
|---|---|---|
| P0-1 | Trim IST-counted total from ~16,779 to ≤ 14,500 words (1,500-word slack). Background −600, Empirical Design −700, consolidate three §5.4–§5.6 tables into one (−400). | `paper/28_ist_format_compliance_check.md` total ≤ 14,500 |
| ~~P0-2~~ | **DROPPED 2026-06-07.** A factual check of IST's peer-review model found IST uses **single-anonymized** review (reviewers see authors), not double-anonymized. The Stage-9 Action Editor's "not anonymous → FAIL" was a hallucinated requirement, and the README's "double-anonymized for review" note was wrong (now corrected). The submission **keeps** author names, affiliations, CRediT, and funding. No anonymization is performed. | n/a — keep named submission |
| P0-3 | Shorten title to ≤ 70 chars, lower jargon. Candidate: *"Domain-Validity-Gated Metamorphic Testing for Scientific ML Surrogates"*. | `\title{...}` length ≤ 70 |
| P0-4 | Rewrite Abstract Conclusion from four "not"s to scoped positive framing (stay inside ledger `wording_forbidden`). | Conclusion contains no "is not" sentences; 3 sentences max |

### Phase P1 — Send-to-reviewer readiness (10–14 working days)

| ID | Item | Source | Acceptance gate |
|---|---|---|---|
| P1-1 | Promote claim ledger to a named contribution. Add 1 line to Abstract Method, 1 Highlight, 1 §1 contribution. | R1 / R3 | All three new mentions land; word count delta tracked |
| P1-2 | Rename "conservation MR" to "operator-floor-grounded non-regression diagnostic" in Table 3 / §5.2 / Abstract; revise §5.3 prose so the name lines up with what the MR actually scores. | R2 (M4) | Manuscript no longer uses "conservation MR" as a noun without the qualifier |
| P1-3 | Tag node-permutation in §5.7 / Table 4 as "pipeline-implementation sanity, not a model-level diagnostic"; explain the structural-equivariance reason. | R2 (M3) | New explicit paragraph or footnote in §5.7 |
| P1-4 | Add Cliff's δ + Wilcoxon signed-rank to §5.4 multi-checkpoint and §5.7 severity sweeps; declare in §4.4 statistical plan. | R1 (M3) | Numbers reported, code added under `tools/` and re-run from the existing JSON aggregates |
| P1-5 | Add bootstrap or jackknife CI on the operator-floor log-log slope in §5.5; report SE on the slope. | R1 (m3) | New CI bracket in Section 5.5 prose and in the JSON report |
| P1-6 | Disclose that S0 reuses the original pilot checkpoint; reframe the roster as "1 pilot + 3 seed replicas + 2 configuration variants", and explicitly explain why the bootstrap CI is computed over S0–S3. | R3 (Section II) | New paragraph in §5.4 |
| P1-7 | 2D verdict either gets a minimum continuous domain-violation score OR is explicitly downgraded to "structural placement, not a calibrated coordinate". | R2 (M2) | §3.5 / Fig 3 caption updated |
| P1-8 | Re-center §1 contributions and Abstract Results around (a) operator-floor empirical calibration (b) R3 non-monotone detection (c) claim-ledger reproducibility, with the rubric explicitly described as "systematic packaging + one SciML-specific gate". | R2 (Section IV) | §1, Abstract, Highlights all updated |
| P1-9 | Update README's "Thesis" section to absorb R3 non-monotone detection as a fourth element ("a fault catalogue may contain instances that share the very symmetry an MR exploits; severity sweeps reveal these blind regions"). | this document | README diff lands |
| P1-10 | Threats to Validity: cite Verdecchia 2023 IST and Empirical Standards; widen construct validity to include experimenter bias and mono-method bias. | R1 (m1) | Two new citations land in §6 |

### Phase P2 — Methodological deficit closure (4–6 weeks)

This is where the uncompromising commitment lives. None of the items can be
skipped without re-opening a hot spot a Stage-9 reviewer already flagged.

| ID | Item | Source | Acceptance gate |
|---|---|---|---|
| **P2-1 = doc-27 A1** | **Cross-family pilot.** Train (or load a public checkpoint for) one PINN or FNO cylinder-flow surrogate. Run node-permutation, mirror-y OOD-stress, and operator-floor-grounded non-regression against it. Report results even if negative. | R1 (M1), R2 (M5), doc-27 A1 | New `research_assets/runs/cross-family-pilot/` directory; new claim C14; new Section in §5; manuscript explicitly reports "this MR transfers / does not transfer" |
| **P2-2 = doc-27 A2** | **Minimum LLM-candidate baseline.** 2 vendors × 3 temperatures → MR candidates → score each candidate against the rubric → measure rubric retention rate, agreement with the manuscript's three executed MRs. | R1 (M2), doc-27 A2 | New `research_assets/runs/llm-candidate-baseline/`; new claim C15; new Section in §5 |
| **P2-3 = doc-27 A3** | **Adversarial mutant catalogue.** Add ≥ 10 mutants targeted at MR-specific thresholds (subtle weight perturbations on the mirror-y axis; sub-threshold rescaling that the non-regression diagnostic should still detect). | R1 (M4), R2 (implied), doc-27 A3 | New `research_assets/runs/adversarial-mutants/`; new claim C16; updated §5.7 |
| P2-4 | Refine R3 non-monotone PC_zero_vy at $p \in \{0.85, 0.9, 0.95, 0.99\}$ to confirm step vs. continuous transition. | R1 (M5) | New rows in `fault_robustness_report.json`; updated Fig 5 |
| P2-5 | Reference coverage: add Saha & Kanewala 2018, Kanewala et al. 2016 graph-kernel MR prediction, Chen et al. 2018 CSUR survey, Wang 2021 PINN failure modes, deeper Mandrioli 2025 CPS discussion. Net reference count target ≥ 30 (R1 keeps pushing on coverage). | R2 (Section V) | 5 new entries in `references.bib`; corresponding paragraphs in §2 |

### Phase P3 — Submission packaging polish (2–3 days, in parallel with P1)

| ID | Item | Acceptance gate |
|---|---|---|
| P3-1 | Data availability rewritten with placeholder Zenodo DOI, license (CC-BY-4.0 data; MIT code), SUT-repo commit pin. | R3 (Section III) |
| P3-2 | §4.6 reproducibility envelope (hardware, wall-clock, CPU-hours, framework version). | R3 (M1) |
| P3-3 | Highlights re-balanced to cover R3, claim ledger, and operator-floor calibration (4 lines, each ≤ 85 chars). | R2 (Section IV), R1 (Section IV) |

---

## 5. Time and effort budget

| Phase | Wall-clock estimate | Critical path |
|---|---|---|
| P0 + P3 + Phase-P1 framing-only items (P1-1, P1-8, P1-9) | 1 week | Author writing time only |
| P1 statistical + numerical items (P1-4, P1-5, P1-7) | 1 additional week | Re-run analysis scripts on existing data; no new experiments |
| P1 disclosure + rename items (P1-2, P1-3, P1-6, P1-10) | concurrent with above | Editing pass |
| **P2-1 cross-family pilot** | **2–3 weeks** | New SUT acquisition + training + 3 MR runs; this is the bottleneck |
| P2-2 LLM-candidate baseline | 4–6 days | API access; no training |
| P2-3 adversarial mutants | 3–5 days | Author implementation |
| P2-4 R3 refinement | 1–2 days | Re-run severity sweep |
| P2-5 reference coverage | 2–3 days, in parallel with above | |
| Final integration + regression suite + re-run Stage 9 self-review | 1 week | Sanity check before submission |

**Total wall-clock: 6 to 9 weeks of focused work.** This is the
no-compromise number; doc 27 estimated 4–6 weeks, but doc 27 implicitly
assumed someone was already working on the items.

---

## 6. Decision gates

The plan above is a single irrevocable path: **submit to IST regular track,
no detour to JSS**. The user has explicitly chosen no compromise. The
go/no-go gates at the end of each phase are:

- **End of P0**: word count ≤ 14,500. If not, repeat the trim.
- **End of P1**: every Stage-9 hot spot that can be closed by writing alone
  is closed. If not, return to P1.
- **End of P2-1**: cross-family pilot produces an interpretable verdict
  (pass / fail / inconclusive). A negative result is fine; an inconclusive
  due to setup is not.
- **End of P2**: re-run Stage 9 four-reviewer simulation as a self-check.
  Hot spots flagged by ≥ 2 reviewers must drop to ≤ 1.
- **Submission gate**: the simulated post-revision verdict from the
  self-check must be **Minor Revision or Accept**. If still Major,
  one more revision cycle before Editorial Manager submission.

---

## 7. What this document replaces

- Doc 26 remains obsolete for the regular-track target (this was already
  declared in doc 27).
- Doc 27 remains valid as the maturity assessment; this document operationalizes its Path A.
- Doc 28 remains valid as the format compliance ledger; P0-1 updates its
  word-count target.
- Doc 29 remains the authoritative four-reviewer simulation transcript;
  every hot spot above traces back to a specific reviewer comment in doc 29.

---

## 8. Standing constraints honored

- Reply / discussion in Chinese; documents in English to stay journal-ready.
- `Minimum-MR-SubSet` read-only; new artifacts land in this repository.
- STVR excluded.
- Every commitment above is implementable from existing tools or is a
  named new run directory; no claim is added without a corresponding ledger
  entry.
