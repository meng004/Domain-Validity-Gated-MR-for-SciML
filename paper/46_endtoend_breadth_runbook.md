# 46 — End-to-end cross-program breadth: self-contained execution runbook (claim C40)

> Date: 2026-06-17 · Status: **PLAN / RUNBOOK, not yet executed.**
> This is the "bigger lever" from paper/44 §A.2: run *this paper's* validity-gated
> pipeline (admissibility rubric → typed verdict → coverage analysis) **end-to-end** on
> several diverse program types, upgrading C39 (read-only reuse of committed kill matrices)
> to C40 (the paper's own pipeline executed on each program). Designed to be picked up by a
> future session with one instruction: *"switch to branch `<B>`, read `paper/46`, execute."*

---

## 0. GPU dependency — ANSWER: NO (for the selected SUTs)

Verified against the sibling repo (`../最小完备MR子集`, read-only):

| SUT | Imports | GPU? |
|---|---|---|
| `experiments/puts/p1_heat.py` … `p8_schrodinger.py` | `numpy` (+ scipy) only | **CPU-only** |
| `experiments/puts/p5_pke.py` (stiff ODE) | `numpy` | **CPU-only** |
| `experiments/puts/p9_openmc.py` | `numpy` + `openmc` | **CPU-only** (Monte-Carlo is CPU-bound; needs the `openmc` package) |
| neural surrogates (MGN/PINN/FNO) | `torch` | GPU for *training*; inference CPU/MPS — **already covered** (cylinder, airfoil) |

The classical P-series solvers and OpenMC carry **no GPU dependency**. The end-to-end
breadth expansion therefore runs on **CPU only** (a plain Python + numpy/scipy environment;
`openmc` optional). No GPU, no METBENCH_MGN_* env, no DeepMind data download.

---

## 1. Goal
Convert the cross-program result from a *read-only generalization check* (C39: we read the
sibling's committed kill matrices) into an *end-to-end execution* (C40: we run the paper's
own admissibility rubric + typed verdict on each program, producing the paper's verdicts).
This is the strongest honest answer to the IST "empirical breadth / two-SUT principle" gap.

## 2. Representative SUT selection (GPU-free, prioritized from the sibling)
Chosen for program-type diversity + reusability + CPU-only runnability:

| Tag | SUT (sibling path) | Program type | Domain | MR specs |
|---|---|---|---|---|
| E1 | `experiments/puts/p1_heat.py` | classical FDM | parabolic PDE | `scripts/mcmr/pseries/mr_specs/p1_heat/` |
| E2 | `experiments/puts/p2_wave.py` | classical FDM | hyperbolic PDE | `…/mr_specs/p2_wave/` |
| E3 | `experiments/puts/p5_pke.py` | stiff ODE | reactor point-kinetics | `…/mr_specs/p5_pke/` |
| E4 | `experiments/puts/p7_burgers.py` | classical FVM | nonlinear conservation law | `…/mr_specs/p7_burgers/` |
| E5 *(optional)* | `experiments/puts/p9_openmc.py` | production code | Monte-Carlo neutron transport | sibling OpenMC MR features |

Core = E1–E4 (numpy-only, always runnable). E5 included iff `openmc` importable. Each has
committed MR specs + a mutant set (`scripts/mcmr/pseries/mutants.py`) + an execution driver
(`scripts/mcmr/pseries/{mr_exec,killmatrix,put_adapter}.py`). The sibling already executes
MRs→mutants to build kill matrices; the **new** step is to wrap each SUT's MRs in *this
paper's* gate + typed verdict.

## 3. Method — apply THIS paper's pipeline end-to-end (per SUT, CPU)
New runner in this repo: `tools/run_endtoend_pipeline_pseries.py` (to be written). For each SUT:
1. **Import the SUT + its MR specs + mutants** from the read-only sibling (add
   `<sibling>/scripts` and `<sibling>` to `sys.path`; never write to the sibling).
2. **Apply the paper's 4-condition domain-validity rubric** (physical basis, transformation
   preconditions, output mapping, operator/numerical floor) from
   `research_assets/rubric/domain_validity_rubric.json` to each MR → admit / reject / defer.
3. **Execute the admitted MRs** on the SUT and its mutants via the sibling's CPU MR driver
   (`mcmr.pseries.mr_exec`), recording residual vs tolerance.
4. **Emit the paper's typed 2D verdict** per MR (relation-violation × domain-violation) and
   the per-SUT coverage map (admissible-MR fault coverage + structural blind spots).
5. Write `research_assets/runs/endtoend-pseries/<tag>/metric_ledger.json` (committed in THIS
   repo; sibling untouched).

Aggregate across E1–E4(+E5): the paper's pipeline produces typed verdicts on N program types
end-to-end; report whether (a) the gate admits/rejects/defers MRs for the physically correct
reason per program, (b) the coverage-geometry reading holds, (c) the by-class mapping is
program-specific (it should be, extending the SUT-specificity finding to executed evidence).

## 4. New claim + honesty boundary
- `C40-endtoend-cross-program-pipeline` (status: observed). **Allowed:** "this paper's
  validity-gated pipeline (admissibility rubric + typed verdict + coverage map) executes
  end-to-end on N classical/production SUTs spanning parabolic / hyperbolic / stiff-ODE /
  conservation / Monte-Carlo program types, on CPU, producing typed verdicts and a coverage
  map per SUT." **Forbidden:** "a reliability or real-world detection rate per program";
  "the MRs are new contributions" (the MRs are the sibling's domain MRs — the *pipeline*
  is what runs end-to-end); "superiority over any baseline."
- Honesty: the MRs and mutants are the sibling's; what is newly executed is *this paper's
  gate + typed-verdict framework* on them. This is genuinely end-to-end (the gate decides
  admissibility and the verdict types each outcome), unlike C39's read-only kill-matrix reuse.

## 5. Self-contained execution steps (the runbook)
On branch `<B>` (recommend a fresh branch `claude/endtoend-breadth-c40` off
`claude/youthful-feynman-qy22k2`), in a CPU Python env (numpy, scipy; `openmc` optional):
1. Confirm the sibling is present read-only (`../最小完备MR子集` locally, or
   `/home/user/Minimum-MR-SubSet` in cloud). Set `MMRS_ROOT` accordingly.
2. Write `tools/run_endtoend_pipeline_pseries.py` per §3 (gate + execute + typed verdict).
3. Run it for E1–E4 (and E5 if `openmc` imports): `python tools/run_endtoend_pipeline_pseries.py --suts p1_heat,p2_wave,p5_pke,p7_burgers`.
4. Add claim `C40` to `research_assets/experiments/claim-ledger.yml` (§4 wording).
5. Add a guard `tests/test_endtoend_pipeline_pseries.py` pinning: N SUTs executed, gate
   admit/reject/defer present per SUT, coverage map + structural blind spots, program-specific
   mappings, honesty boundary.
6. Integrate one short Results subsection ("End-to-end cross-program execution") +, if it
   strengthens, promote C40 over C39 in the cross-program paragraph; add C40 to the Threats
   external-validity discussion (§ Threats currently says "two CFD tasks" — update it).
7. Verify: `python -m pytest tests -q` (expect all green) + both validators rc=0 + rebuild
   PDF (0 undefined / 0 Missing character / 0 overfull >50pt) + `tools/ist_wordcount.py`
   (raise the phase-4 buffer if needed, documenting why) + the §15 grep audit.
8. Commit per step with the standard footer; push.

## 6. Coupling to §4 design (do not skip)
The current §4.1 subject-systems list and the Threats §external-validity mention only the two
CFD tasks. The cross-program work (C39, and C40 once run) must be **added to both** so the
breadth is set up in Design and bounded in Threats — otherwise it reads as bolted-on (a
known coherence gap flagged in the paper/41-style review). This is required, not optional.

## 7. What this does and does not buy
Buys: the paper's pipeline demonstrably runs end-to-end across ~5 diverse program types on
CPU — the empirical-breadth answer with the paper's own verdicts, not reused data. Does not
buy: a reliability/superiority claim, or coverage of *industrial neural surrogates at scale*
(those need GPU + are out of this GPU-free scope). The honest ceiling stays "the gate +
typed-verdict framework generalizes across program types," which is exactly the duality's
claim.
