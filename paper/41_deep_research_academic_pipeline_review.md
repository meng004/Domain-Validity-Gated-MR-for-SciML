# 41 — Deep-Research + Academic-Pipeline Peer Review

> Date: 2026-06-17
> Reviewer mode: literature-grounded peer review (paper-search-mcp deep research)
> + §10/§11 academic-pipeline structured review + §10.6 Reviewer-2 adversarial pass.
> Target venue: Elsevier Information and Software Technology (IST), regular track.
> Subject of review: `paper/ist-submission/main.tex` (11,792 IST-counted words; 41 pp).
> Scope note: this complements — does not replace — the gateway review panels
> (v33–v36), which were LLM reviewers without literature access. The distinctive
> value here is the literature audit the panels structurally cannot perform.

---

## 0. What was actually done (honesty boundary)

- **Deep research executed** via paper-search-mcp (dblp, crossref, openalex,
  semantic) on 2026-06-17: closest-prior verification, novelty-gap scan, and a
  missed-work sweep across the MT4ML / SciML-V&V / physical-consistency space.
- **Verified by retrieval:** the three closest-prior works (DOIs below).
- **NOT re-verified in this pass:** the author-added 2025–2026 citations
  (`gopakumar2025calibrated`, `zhao2026noether`, `baral2025xrepit`,
  `wang2025deeponetfe`, `mandrioli2025cps`) — these passed earlier
  citation-integrity gates (phase-21b), but were not re-pulled here.
- **Could not run:** the live gateway panel (`run_academic_review_panel.py`) —
  the gateway key is exhausted and the URLs are scrubbed to placeholders by
  design. Panel evidence is the committed v33–v36 history.

---

## 1. Literature audit (deep research)

### 1.1 Closest-prior verification — ALL THREE CONFIRMED, characterizations fair

| Cite key | Retrieved record | DOI | Paper's characterization |
|---|---|---|---|
| `reichert2024hess` | Reichert, Ma, Höge, Fenicia, Baity-Jesi, Feng, Shen, "Metamorphic testing of machine learning and conceptual hydrologic models," HESS 28:2505 (2024) | 10.5194/hess-28-2505-2024 | Accurate. Physics-derived MRs on trained hydrologic ML surrogates; response can deviate and even flip sign with training data; multi-model + sensitivity. The manuscript's "informal filtering / stratification" framing is fair. |
| `eniser2022relaxations` | Eniser, Gros, Wüstholz, Hoffmann, Christakis, "Metamorphic relations via relaxations…action-policy testing," ISSTA 2022, p.52–63 | 10.1145/3533767.3534392 | Accurate. Relaxations = numerical tolerances in MR oracles for (stochastic) policy testing. |
| `duqueTorres2023bugornot` | Duque-Torres, Pfahl, Klammer, Fischer, "Bug or not Bug? Analysing the Reasons Behind MR Violations," SANER 2023, p.905–912 (also arXiv:2305.09640) | 10.1109/SANER56733.2023.00109 | Accurate. Bug-vs-inapplicability separation via explicit MR constraints. |

**Verdict:** the closest-prior triad is real, correctly attributed, and fairly
characterized. The positioning table (`tab:closest-prior-positioning`) is
honestly drawn — no straw-manning detected.

### 1.2 Novelty-gap assessment — the gap is REAL

- dblp `metamorphic testing numerical simulation scientific computing` → **empty.**
- semantic `metamorphic testing physics-informed neural network surrogate PDE` →
  returns only PINN **surrogate-modeling** papers (GAPINN, shock-wave PINN,
  bladed-disk PINN…), **none of which do metamorphic testing.**
- The active MT4ML literature targets **classifiers, unsupervised learning, RL
  policies, credit scoring** — not physics-governed mesh/operator surrogates.

The claim "first end-to-end validity-gated metamorphic-testing pipeline for
physics-governed SciML" is **defensible**: no retrieved work occupies that
specific cell. The novelty is *configurational* (admissibility gate + typed 2D
verdict + by-class fault diagnosis assembled and executed), which is a genuine
but contestable form of novelty — see §3.1.

### 1.3 Missed / adjacent work — three items a reviewer may raise

1. **Same-venue, recent, uncited (moderate concern).**
   Ying, Bellotti, Breeden, Towey, "Metamorphic Testing and exploration for
   Machine Learning credit score models," *Inf. Softw. Technol.* 188:107903
   (2025), 10.1016/j.infsof.2025.107903. IST editors/reviewers frequently expect
   engagement with recent same-venue work. Not SciML, so no novelty threat —
   but a one-line related-work nod is cheap insurance.

2. **The closest *conceptual* competitor the paper does not engage (substantive).**
   A "physical-consistency diagnostics for SciML surrogates" cluster is active:
   e.g. Saccardi et al. (2025, arXiv:2510.13722) evaluate geographic
   generalization and **physical consistency** (divergence/vorticity) of climate
   downscaling surrogates, with OOD stress tests; Najafi et al. (2026,
   Water 18:271) survey OOD stress-testing + physics-consistency for SciML.
   These are not framed as metamorphic testing, but a reviewer will ask: *how
   does a validity-gated MR differ from a physics-consistency diagnostic?* The
   paper should pre-empt this — the answer (MRs are relational input-transform
   oracles with an admissibility predicate, not single-output residual checks)
   is strong but currently unstated.

3. **Follow-up from the Eniser group (minor).**
   Christakis, Eniser, Hoffmann, Singla, Wüstholz, "Specifying and Testing
   k-Safety Properties for ML Models," IJCAI 2023, 10.24963/ijcai.2023/528 —
   extends the relaxations line to k-safety via MT. Optional supporting cite;
   strengthens the "calibrated-tolerance principle" lineage.

---

## 2. Academic-pipeline structured review (§11 proofread + §10 ARS)

### 2.1 Technical soundness — strong
- The admissibility gate (tolerance floored at the discrete operator's intrinsic
  error, O(h) for a P1 divergence operator) is a principled, novel device and
  the headline theoretical contribution. Soundness is not in question; *generality*
  is scoped (§3.4).
- Typed verdicts are **training-independent** (they read the relation and the
  domain predicate, not the fit) — a genuinely clean property that the airfoil
  primary-scale roster (node-perm 240/240, exact) demonstrates convincingly.
- The same predicate executing across MeshGraphNet / PointMLP / PhysicsNeMo /
  PINN / FNO is real cross-SUT portability evidence.

### 2.2 Empirical rigor — the soft spot (see §3.2)
- The typed-verdict / admissibility evidence is now well-supported (two CFD
  tasks: cylinder flow + primary-scale airfoil).
- The **seeded-fault by-class diagnosis** — pitched as the third distinct
  empirical element — rests on a **single SUT family** (cylinder-flow MGN) with
  small denominators (0/6 detection cells, Wilson CIs to [0.00, 0.39]). The most
  novel empirical claim has the thinnest support.

### 2.3 Related work — good, with the §1.3 gaps
- Closest-prior handled honestly. Add the physical-consistency-diagnostics
  contrast (§1.3 item 2) and the same-venue nod (item 1).

### 2.4 Clarity / presentation — good post-revision
- 11,792 words (under the 15k hard cap and the 11,800 clarity buffer); structured
  abstract present; closest-prior table scannable; em-dashes purged; OOD/K=6
  glossed at first use. No further density surgery is safe without cutting
  pinned numbers or honest caveats (confirmed exhausted this session).

### 2.5 Reproducibility — exemplary
- Claim-ledger SSOT, fail-closed validators, 342 regression guards pinning prose
  to evidence, Zenodo concept DOI. This is well above IST median and should be
  foregrounded as a strength.

---

## 3. Reviewer-2 adversarial pass (§10.6) — most severe concerns

**R2-1 (most likely major-revision trigger). Single-SUT generalization of the
headline diagnostic.** The by-class fault-localization narrative (continuity→
boundary/scale, symmetry→channel/adjacency) is the paper's most original
empirical claim, yet it is established on one cylinder-flow MGN with 0/6 cells
and wide CIs. The primary-scale airfoil strengthens the *typed-verdict* axis but
does **not** replicate the *seeded-fault by-class* pilot. A reviewer will say the
diagnosis pattern may be SUT- or fault-catalogue-specific. → Either (a) replicate
the seeded-fault pilot on the airfoil SUT, or (b) explicitly down-scope the claim
to "observed on one SUT family; generalization is future work" in both abstract
and §Limitations. (b) is achievable now; (a) is the stronger answer.

**R2-2. Configurational novelty.** "Each prior supplies one ingredient; none
combines them" invites the incremental-combination critique. Mitigation: lead
with the two devices that are *not* in any prior (operator-floor admissibility
gate; training-independent typed 2D verdict), and state plainly that the
combination changes what the method can *do* (separate model-bug from
out-of-domain application automatically), not merely that it unions features.

**R2-3. Half-delivered 2D verdict.** The domain-violation axis is "operationalized
per relation but not calibrated across MR classes (future work)." A skeptic reads
the second dimension as partially delivered. Keep the honest scoping, but show at
least one cross-class calibration example or a concrete calibration protocol so
the axis does not read as aspirational.

**R2-4. Scoped theoretical floor.** The O(h) floor is proven for P1 / structured
meshes; the general unstructured-mesh bound is future work. Fair as written —
ensure the abstract/intro do not overstate the floor's generality.

**R2-5. Panel saturation is not evidence of quality.** The v33–v36 LLM panel
never rewarded the real improvements (noise band 7.4–8.0). Do not cite panel
scores as a maturity signal in any cover letter; they are a noisy proxy. (Noted
for submission strategy, not a manuscript defect.)

---

## 4. Verdict

**Recommendation: minor-to-major revision (borderline), leaning ACCEPTABLE for
IST regular track after addressing R2-1.**

The method is sound, genuinely novel in its configuration, exceptionally
reproducible, and honestly positioned against verified closest-prior. The single
blocking-class issue is R2-1: the headline by-class diagnostic outruns its
single-SUT evidence. This is fixable **today by honest down-scoping** (no new
runs) and fixable **stronger by one airfoil seeded-fault replication**. Everything
else is incremental polish.

## 5. Prioritized actionable items

- **P0 (R2-1):** down-scope the by-class fault-diagnosis claim to its one-SUT
  evidence in abstract + §Limitations, OR replicate the seeded-fault pilot on the
  airfoil SUT. (Ledger: would need a new claim ID if (a); pure prose if (b).)
- **P1 (R2-2/§1.3-2):** add a 2–3 sentence contrast with physical-consistency
  diagnostics (Saccardi 2025; Najafi 2026) and crisp the "two new devices"
  framing in the contributions paragraph.
- **P2 (§1.3-1):** one-line related-work nod to Ying et al. 2025 (IST 2025,
  same venue).
- **P3 (R2-3):** add one concrete cross-class calibration example or protocol
  for the domain-violation axis.
- **P4 (R2-4):** audit abstract/intro wording so the O(h) floor's generality is
  not overstated.

> None of P0–P4 requires weakening a regression guard or inventing a number.
> P0(a) and P3 touch the claim-ledger; P0(b)/P1/P2/P4 are prose-only.
