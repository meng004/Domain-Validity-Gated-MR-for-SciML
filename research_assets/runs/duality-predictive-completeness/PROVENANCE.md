# Provenance: duality predictive coverage-completeness (claim C50)

Scope: **upgrade the observed realistic-fault by-class structure (C48/C49) into a falsifiable,
a-priori prediction, and confirm the two genuinely non-trivial parts** — blind-completeness (a
fault preserving every measured invariant is invisible to the *whole* MR suite) and
amplitude-independence (blindness does not depend on how badly the fault corrupts the output).
**Not** a quantitative/validated coverage model, a detection-rate or probability prediction, a
cross-architecture generalization, a baseline-superiority claim, or a proof of the duality for all
MRs/faults.

## Why this experiment, and the scope discipline

C48/C49 *observed* the 2x2 by-class structure. The open question a reviewer would press: is it
predictable in advance, and does the blind region reflect a real completeness property of the
coverage rather than an artefact? Two cautions shaped the design:

- **Single-invariant detection is near-definitional.** "The fault changed the integral, so the
  conservation MR fired" is not a finding — the conservation detector *is* the moved-integral
  test. The report labels every single-invariant cell `near-definitional, not a finding`.
- **The non-trivial, falsifiable core is the blind region**: (1) preserve-ALL-invariants ⇒
  invisible to the WHOLE suite, and (2) that this holds at large corruption magnitude.

## Non-circularity (hard constraint)

Each fault's invariant signature is computed **a priori from the operator's mathematics on generic,
model-independent test fields** — never from last round's detections. The detections (C48/C49) are
used only afterwards, to verify the predictions.

- Generic fields (pre-declared, **not** tuned to reproduce any result): a low-frequency coherent
  field with distinct per-channel means (`default_rng(50_2026)`) and a deterministic analytic
  asymmetric field, each built at the architecture's native resolution (FNO 16x16, PINN 129x129).
- `perturbs_conservation` := the operator changes the conserved sum past the MR's own tolerance
  (FNO 5%, PINN 10%); the magnitude is recorded because for boundary/region faults it is genuinely
  field/resolution dependent.
- `breaks_symmetry` := the operator does not commute with the symmetry/translation map,
  `||R F g − F R g|| / ||F g|| > 1e-6` (a commutator: exactly zero or clearly non-zero).
- A fault is **a-priori blind** iff it has an **exact double zero** (preserves the sum to < 1e-9
  AND commutes) — a resolution/field-independent property, the falsifiable core.

## Inputs (all committed; CPU + torch, no credentials)

| Input | Path |
|---|---|
| FNO realistic-fault detections (C48) | `research_assets/runs/fno-realistic-fault/fno_realistic_fault_report.json` |
| PINN realistic-fault detections (C49) | `research_assets/runs/pinn-realistic-fault/pinn_realistic_fault_report.json` |
| Shared fault operators | `tools/run_realistic_fault_fno.py` (`apply_fault`) |
| FNO checkpoints (Task-C probe) | `research_assets/runs/fno-k6-roster/{burgers,heat}_s{0,1,2}/sut/checkpoint.pt` |
| Reused MR thresholds | `tools/run_seeded_fault_detection_fno.py`, `tools/run_seeded_fault_detection_pinn.py` |

## Environment

CPU-only; `pip install torch` (committed run used `torch 2.12.0+cpu`); numpy from the verifiable
tier. The a-priori analysis is deterministic (fixed generic-field seed); the Task-C FNO probe loads
read-only checkpoints. Reruns are byte-identical modulo the report timestamp.

## Operation steps

```bash
python tools/run_duality_predictive_completeness.py \
    --outdir research_assets/runs/duality-predictive-completeness
python tools/validate_research_assets.py
python -m pytest tests/test_duality_predictive_completeness.py -q
```

## Pinned results (verification) — generated 2026-06-20

### A-priori prediction table (operator maths on generic fields) vs actual by-class (C48/C49)

| fault | a-priori FNO | a-priori PINN | actual FNO | actual PINN |
|---|---|---|---|---|
| global_renorm | conservation | conservation | conservation | conservation |
| channel_swap | conservation | both | conservation | both |
| gaussian_noise | symmetry-translation | symmetry-mirror | translation | mirror |
| boundary_band_corrupt | both | subthreshold-undetected | both | none (untestable) |
| region_dropout | both | symmetry-mirror | both | none (untestable) |
| mode_truncation | **blind** | **blind** | none | none |
| spatial_shift | **blind** | **blind** | none | none |
| sharpen | **blind** | **blind** | none | none |
| halffield_roll (Task C) | **blind** | **blind** | 0/24 (probe) | — |

The channel-swap FNO-vs-PINN *difference* (conservation vs both) is predicted **a priori** from
the operator: a channel swap commutes with translation but anti-commutes with the mirror channel
map. boundary/region conservation cells are flagged field/resolution dependent (a 1-cell band /
low-energy corner is sub-threshold on the fine PINN grid).

### §5 — the four questions answered

1. **A-priori vs actual agreement.** Layered: (i) single-invariant cells agree where faults reach
   testable magnitude, but are **near-definitional** (not a finding); (ii) **blind-completeness**:
   all four exact-double-zero faults predicted blind are detected by no MR; (iii) **mismatches: none**
   among testable faults (the untestable sub-magnitude PINN boundary/region faults are recorded, not
   counted as agreement).
2. **Blind-completeness holds.** The four preserve-all faults (mode truncation, spatial shift,
   sharpen, half-domain roll) are caught by **no MR** — 0/24 each on FNO, 0/6 each on PINN, 0/24 for
   the half-roll probe — with **zero falsifying cases** (no preserve-all fault is caught by any MR).
3. **Amplitude-independence.** Confirmed on both families: the PINN spatial shift corrupts the
   output by rel-L2 **0.63** and the FNO half-domain roll by rel-L2 **0.43** (on heat seed 0, the
   one roster member whose field retains structure; the smooth Burgers members stay near no-op), and
   both still escape **every** MR. FNO is not amplitude-limited here (0.43 ≥ 0.10 realistic), though
   it does not reach 0.5; the strongest large-amplitude confirmation is the PINN's 0.63.
4. **Honest verdict.** The duality, as "a-priori qualitatively predictable + coverage-complete",
   **holds (bounded)** on these two architecture families: blind-completeness with no falsifier, and
   amplitude-independent blindness. It is a **qualitative, falsifiable** statement — single-invariant
   cells are near-definitional, boundary/region cells are field-dependent — **not** a quantitative
   coverage model.

Full claim wording is in `research_assets/experiments/claim-ledger.yml`
(`C50-duality-predictive-completeness`).
