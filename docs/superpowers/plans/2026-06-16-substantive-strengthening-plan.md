# Substantive Strengthening Plan (option 3) — reviewer-consensus root cause + fixes

> Basis: per-reviewer `top_concerns` from gateway panels **v33, v34, v35**
> (5 reviewer roles x 3 runs = 14 reviewer-instances; v35 was 4/5, kimi-k2.6
> dropped on HTTP 502). A concern is "consensus" when raised by **>= 3 distinct
> reviewer roles** across the runs. Evidence fixes must be REAL (run + commit
> artifacts under the claim-ledger discipline); no prose-only fabrication.

## Consensus concerns (>= 3 of 5 roles)

| # | Concern | Roles (count) | Type |
|---|---|---|---|
| C-A | Single-task / narrow external validity (cylinder flow dominates; airfoil bounded CPU-scale; PINN/FNO small pilots) | EIC, MethRigor, DomainExpert, Perspective, DevilsAdvocate (**5/5**) | evidence |
| C-B | Seeded-fault catalogue weak (10 author-implemented mutants, gross corruptions, stress-test framed near localization) | EIC, MethRigor, DomainExpert, DevilsAdvocate (**4/5**) | evidence + framing |
| C-C | Dense / over-defensive presentation (boundary qualifications, tiered evidence, repetition, claim-management overhead) | EIC, MethRigor, Perspective, DevilsAdvocate (**4/5**) | structure |
| C-D | Incremental novelty (operationalizes Duque-Torres / Eniser / Reichert; novel core under-differentiated) | EIC, DomainExpert, DevilsAdvocate (**3/5**) | framing |
| C-E | Two-dimensional verdict score D not cross-calibrated across MR classes | DomainExpert, Perspective, MethRigor (**3/5**) | framing + methodology |

Below threshold (note, not consensus): conservation-MR deferral on the primary
SUT (MethRigor, strong, 2 runs); operator-floor general-mesh bound (EIC, MethRigor = 2);
weak/distracting baselines (Perspective, DevilsAdvocate, ~EIC = 2-3).

## Root cause + fix per concern

### C-A Single-task / external validity (5/5 — strongest)
- **Root cause:** one primary task family; the second CFD task (airfoil) is a
  bounded CPU-scale study, and cross-family PINN/FNO are small pilots, so the
  method's generality is asserted faster than the evidence licenses.
- **Fix (treat-the-cause, expensive):** elevate a genuinely second task to
  **primary scale** — the deferred airfoil GPU run (NEXT_STEPS 2-B) at full
  roster, or a different dataset/architecture at primary scale. **Needs
  GPU/cloud; blocked locally.**
- **Fix (framing, cheap):** foreground the airfoil *rejection* result (predicate
  behaving differently under changed physics) as the generality evidence, and
  hard-scope the contribution to "method + protocol," not cross-domain rates.
  Reviewers already see this, so framing alone is partial.

### C-B Seeded-fault catalogue (4/5)
- **Root cause:** 10 author-implemented mutants = experimenter bias; gross
  corruptions; 5/10 over-readable as localization.
- **Fix (cause, medium-high):** add an **independent fault source** — a standard
  mutation-testing tool on the surrogate code, or a real defect set — removing
  author bias and raising N. Non-trivial for SciML surrogates.
- **Fix (framing, cheap):** downgrade all localization wording to "stress test,"
  bound 5/10 explicitly as "not a real-world detection rate," add experimenter
  bias to Threats. Mostly done; tighten further.

### C-C Dense / over-defensive presentation (4/5)
- **Root cause:** the claim-ledger rigor produces heavy boundary qualifications,
  tiered evidence, and repetition in the body, which obscures the through-line.
- **Fix (structural, medium):** move claim-management apparatus and auxiliary
  studies to **appendices**; keep a clean body (method -> key result -> honest
  scope); cut repetition. Bounded by the 15k cap and the prose-guard tests.
  This is the substantive version of the clarity work (restructure, not gloss).

### C-D Incremental novelty (3/5)
- **Root cause:** positioned as operationalizing existing MT ideas; the novel
  core (the numerical-decidability / measurement-floor admissibility gate + the
  evidence-gated conversion to an executable, claim-bound MR asset) is not
  sharply differentiated from the closest prior.
- **Fix (framing, cheap, HIGH value):** a crisp explicit novelty statement plus
  a **comparison table** (this work vs Duque-Torres vs Eniser vs Reichert)
  showing what each lacks and what this adds. No new experiments.

### C-E D-score cross-calibration (3/5)
- **Root cause:** D = m/(m+1) is a per-relation normalized coordinate; units
  differ across MR classes; it is not a cross-class metric (the paper admits
  this).
- **Fix (framing, cheap):** present D explicitly as a per-relation diagnostic
  ordinate, forbid any cross-relation reading, state cross-relation calibration
  as future work (partly present; make it unambiguous).
- **Fix (methodology, expensive):** define a genuinely cross-class-comparable
  domain-violation scale — a real methods contribution; research effort.

## Prioritized execution

- **Tier 1 (now, no experiments, cheap):** C-D novelty statement + comparison
  table; C-E D reframe; C-B fault-claim tempering; C-C targeted dedup. Addresses
  the *framing* of 4 of 5 consensus concerns and is fully local + guard-safe.
- **Tier 2 (medium, structural):** C-C body/appendix restructure (move auxiliary
  + boundary detail to appendices; tighten the body narrative).
- **Tier 3 (expensive, needs compute + a decision):** C-A second primary-scale
  task (GPU airfoil); C-B independent mutants; C-E cross-class D calibration.
  This is the real "treat-the-cause" evidence work, with real cost, and (for
  C-A) currently blocked without GPU/cloud.

**Honest bottom line:** Tier 1 tightens the paper now and answers the *framing*
half of the consensus. But the two strongest concerns (C-A single-task, C-B
fault catalogue) are **evidence-breadth** problems whose genuine fix needs new
experiments — that is the substantive strengthening with real cost, and any such
fix must add committed artifacts, not prose.
