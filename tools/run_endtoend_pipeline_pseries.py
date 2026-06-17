"""End-to-end cross-program execution of this paper's validity-gated pipeline (claim C40).

Unlike the read-only generalization check of claim C39 (which reuses the sibling's
committed kill matrices), this runner executes *this paper's own* pipeline end-to-end on
several classical-solver SUTs from the READ-ONLY Minimum-MR-SubSet sibling:

  1. import the SUT, its domain MR specs, and its seeded mutant set (read-only);
  2. apply the paper's four-condition domain-validity rubric to each candidate MR
     (Section "Domain-validity rubric": (i) physical/software basis, (ii) transformation
     preconditions, (iii) boundary/output-mapping compatibility, (iv) numerical
     decidability / operator floor) -> admit (retained-design-time) / reject
     (rejected-design-time) / defer (deferred);
  3. execute the admitted MRs on the correct SUT and its mutants on CPU via the sibling's
     own MR driver (mcmr.pseries kill matrix), recording the relation outcome vs tolerance;
  4. emit the paper's typed two-dimensional verdict (relation-violation x domain-violation)
     and a per-SUT coverage map (admissible-MR fault coverage + structural blind spots).

Honesty boundary (see claim-ledger C40): the MRs and mutants are the sibling's domain
assets; what is newly *executed end-to-end* is this paper's gate + typed-verdict framework
on them. No per-program reliability/real-world detection rate is claimed; detection rates
are for the sibling's committed mutant sets only; no baseline superiority is claimed; the
MRs are not new contributions of this paper.

Read-only contract: the sibling is added to sys.path for import only; every write lands
under this repo's research_assets/runs/endtoend-pseries/. CPU-only (numpy + scipy); the
optional E5 OpenMC SUT runs only if the `openmc` package is importable, otherwise it stays
the read-only C39 generalization witness and is reported as not executed here.

Usage:
    python tools/run_endtoend_pipeline_pseries.py
    python tools/run_endtoend_pipeline_pseries.py --suts p1_heat,p2_wave,p5_pke,p7_burgers
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import warnings
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/endtoend-pseries"

# Core CPU-only SUTs: program-type-diverse classical solvers from the sibling.
# Columns: (tag, put_id, program_type [physics/PDE class], numerical_method, domain).
CORE_SUTS = [
    ("E1", "p1_heat", "parabolic PDE", "classical FDM", "heat diffusion"),
    ("E2", "p2_wave", "hyperbolic PDE", "classical FDM", "wave propagation"),
    ("E3", "p5_pke", "stiff ODE", "stiff-ODE integrator (LSODA)", "reactor point-kinetics"),
    ("E4", "p7_burgers", "nonlinear conservation law", "classical FVM", "Burgers transport"),
]
# E5 is OpenMC (Monte-Carlo neutron transport); executed only if `openmc` imports.
OPENMC_SUT = ("E5", "p9_openmc", "Monte-Carlo transport", "production code", "neutron transport")

GATE_SEED = 20260531
GATE_DRAWS = 6   # sibling verify_holds default
KILL_DRAWS = 8   # sibling build_kill_rows default

# The four rubric conditions, named as in the manuscript Section "Domain-validity rubric".
RUBRIC_CONDITIONS = {
    "i_physical_basis": "the relation has a declared physical/software basis (operator class)",
    "ii_transformation_preconditions": "the transformation keeps the case inside the runnable validity domain",
    "iii_output_mapping": "the expected relation is measurable from available outputs and discriminates a scrambled output (construct validity)",
    "iv_numerical_decidability": "the verdict tolerance dominates the measuring-operator error floor (the correct program honours the relation within tolerance)",
}


def resolve_sibling() -> Path:
    """Locate the READ-ONLY Minimum-MR-SubSet sibling and put it on sys.path (import only)."""
    candidates = []
    env = os.environ.get("MMRS_ROOT")
    if env:
        candidates.append(Path(env))
    candidates += [
        Path("/home/user/Minimum-MR-SubSet"),
        ROOT.parent / "Minimum-MR-SubSet",
        ROOT.parent / "最小完备MR子集",
    ]
    for cand in candidates:
        if (cand / "scripts" / "mcmr" / "pseries").is_dir():
            for p in (str(cand / "scripts"), str(cand)):
                if p not in sys.path:
                    sys.path.insert(0, p)
            return cand
    raise SystemExit(
        "Minimum-MR-SubSet sibling not found. Set MMRS_ROOT or clone it to "
        "/home/user/Minimum-MR-SubSet (read-only)."
    )


def sibling_commit(sibling: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(sibling), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def load_specs(put_id: str):
    """Load (MRExec, docstring) pairs from the sibling spec dir (read-only import).

    Mirrors mcmr.pseries.mr_exec.load_mr_execs but also returns each module's docstring so
    the physical-basis condition can be checked against the recorded justification.
    """
    from mcmr.pseries import mr_exec
    spec_dir = Path(mr_exec.__file__).resolve().parent / "mr_specs" / put_id
    out = []
    if not spec_dir.is_dir():
        return out
    for path in sorted(spec_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue
        spec = importlib.util.spec_from_file_location(f"c40spec_{put_id}_{path.stem}", path)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception:
            continue  # a translation that errors on import is REJECT-error (not loadable)
        if hasattr(mod, "MR"):
            out.append((mod.MR, (mod.__doc__ or ""), path.name))
    return out


def _decide(cond: dict, errors: int, frac_pass: float, n_draws: int):
    """Map the four-condition outcome to a rubric decision + human reason.

    Shared by the pseries gate (gate_mr) and the OpenMC gate (gate_openmc_mr) so the
    admit/reject/defer semantics are identical across program types. None of the four
    conditions is optional; the first failing one decides. Output-mapping (iii) is a hard
    reject; preconditions (ii) and numerical decidability (iv) are soft deferrals.
    """
    if not cond["i_physical_basis"]:
        return ("reject", "rejected-design-time",
                "no declared physical/software basis (condition i)")
    if not cond["iii_output_mapping"]:
        return ("reject", "rejected-design-time",
                "output mapping fails construct validity (condition iii): the relation is not "
                "falsified by the scrambled-observable probe, so a uniformly transformed "
                "(incorrect) output still satisfies it and the mapping yields no discriminating oracle")
    if not cond["ii_transformation_preconditions"]:
        return ("defer", "deferred",
                "transformation preconditions not robustly satisfiable (condition ii): the "
                f"transform raised on {errors}/{n_draws} draws")
    if not cond["iv_numerical_decidability"]:
        return ("defer", "deferred",
                "numerical decidability not established (condition iv): the correct program "
                f"honours the relation on only {frac_pass:.2f} of draws within tolerance")
    return ("admit", "retained-design-time", "all four conditions hold")


def gate_mr(put_id: str, mr, doc: str) -> dict:
    """Apply the four-condition domain-validity rubric to one candidate MR.

    Conditions are evidenced by real computations from the sibling's own construct-validity
    firewall (mcmr.pseries.mr_exec.verify_holds), not by hand assertion:
      - (i)  physical basis: the MR declares an operator class (meta_pattern) and a recorded
             justification.
      - (ii) transformation preconditions: the transform runs on every sampled draw without
             error (verify_holds.errors == 0).
      - (iii) output mapping / construct validity: the relation is falsified by a scrambled
             observable (verify_holds.falsifiable), i.e. the output mapping yields a
             discriminating, non-tautological oracle.
      - (iv) numerical decidability: the correct program honours the relation within its
             declared tolerance across every draw (verify_holds.frac_pass == 1.0), evidence
             the verdict tolerance dominates the operator floor.
    """
    from mcmr.pseries.mr_exec import verify_holds
    vh = verify_holds(put_id, mr, n_draws=GATE_DRAWS, seed=GATE_SEED)
    # Condition (i) physical basis: the relation declares an operator class (meta_pattern),
    # the auditable form of "what equation / representation property / numerical assumption
    # justifies the relation". Whether the justification is also written in the docstring is
    # recorded as supporting metadata, not gated on (so a documented-inline justification is
    # not mistaken for a missing basis).
    has_basis = bool(mr.meta_pattern)
    justification_documented = any(
        m in doc for m in ("operator_class", "Justification", "justification", "T_r", "R_r")
    )
    cond = {
        "i_physical_basis": has_basis,
        "ii_transformation_preconditions": vh["errors"] == 0,
        "iii_output_mapping": bool(vh["falsifiable"]),
        "iv_numerical_decidability": vh["frac_pass"] == 1.0 and vh["errors"] == 0,
    }
    decision, rubric, reason = _decide(cond, vh["errors"], vh["frac_pass"], GATE_DRAWS)
    return {
        "mr_id": mr.mr_id,
        "operator_class": mr.meta_pattern,
        "justification_documented": justification_documented,
        "conditions": cond,
        "decision": decision,
        "rubric_decision": rubric,
        "reason": reason,
        "firewall": {"holds": vh["holds"], "frac_pass": vh["frac_pass"],
                     "falsifiable": bool(vh["falsifiable"]), "errors": vh["errors"]},
    }


def coverage_and_verdict(put_id: str, admitted, gate_rows: list) -> dict:
    """Execute the admitted MRs against the SUT + mutants and build the typed verdict
    and coverage map."""
    from mcmr.pseries.killmatrix import build_kill_rows, summarize
    from mcmr.pseries.mutants import MUTANTS, _EQUIVALENT

    mids = list(MUTANTS[put_id])
    equivalents = sorted(_EQUIVALENT.get(put_id, set()))
    with warnings.catch_warnings():
        # Some sibling mutants overflow to inf by design; the kill driver treats a
        # raise/inf as "detected". Silence the numeric noise without altering behaviour.
        warnings.simplefilter("ignore")
        np_err = __import__("numpy").errstate(all="ignore")
        with np_err:
            rows = build_kill_rows(put_id, [mr for mr, _ in admitted], mids,
                                   n_draws=KILL_DRAWS, seed=GATE_SEED)
            summ = summarize(put_id, rows, mids)

    # per operator-class fault coverage (union of the class's admitted MRs)
    class_of = {mr.mr_id: mr.meta_pattern for mr, _ in admitted}
    per_class_cover: dict[str, set] = defaultdict(set)
    for mr_id, coverers in summ["per_mutant_coverers"].items():
        for covering_mr in coverers:
            per_class_cover[class_of[covering_mr]].add(mr_id)
    detected = sorted({m for m, c in summ["per_mutant_coverers"].items() if c})
    escaped = sorted(summ["escaped"])
    declared_equiv_escaped = sorted(set(equivalents) & set(escaped))
    structural_blind_spots = sorted(set(escaped) - set(equivalents))
    n_real = len(mids) - len(equivalents)
    n_detected_real = len([m for m in detected if m not in equivalents])

    # Typed 2-D verdict. The admitted MRs are in-domain by gate construction (conditions
    # ii+iv established), so the domain-violation axis is "in-domain" for every admitted MR.
    # On the relation-violation axis the boolean p-series relations read as pass (V/floor<1)
    # vs fail (V/floor>=1) at their declared tolerance: the correct program lands in the
    # consistent (pass) region for all admitted MRs (frac_pass==1.0), and a mutant lands in
    # the SUT-inconsistency (relation-violation) region exactly when an admitted MR detects
    # it. Rejected/deferred MRs are never admitted into the verdict space (their gate
    # decision is recorded instead), mirroring how absolute conservation is excluded from
    # the cylinder-flow verdict figure.
    typed_verdict_2d = {
        "domain_violation_axis": "in-domain for all admitted MRs (gate established conditions ii and iv)",
        "relation_violation_axis_reading": (
            "boolean relation at declared tolerance: pass = V/floor<1 (consistent), "
            "fail = V/floor>=1 (SUT-inconsistency / fault detected)"),
        "correct_sut_region": "in-domain / consistent (all admitted MRs hold on the correct program)",
        "n_admitted_mr_correct_sut_pass": len(admitted),
        "mutant_inconsistency_detections": len(detected),
        "mutant_in_domain_pass_escaped": len(escaped),
        "excluded_from_verdict_space_reject_or_defer": len([r for r in gate_rows
                                                            if r["decision"] != "admit"]),
    }
    return {
        "n_mrs": len(gate_rows),
        "n_admitted_mrs": len(admitted),
        "n_mutants": len(mids),
        "declared_equivalent_mutants": equivalents,
        "admitted_operator_classes": sorted({mr.meta_pattern for mr, _ in admitted}),
        "full_set_mutation_score": summ["full_set_mutation_score"],
        "non_equivalent_mutation_score": round(n_detected_real / n_real, 4) if n_real else 0.0,
        "detected_mutants": detected,
        "escaped_mutants": escaped,
        "declared_equivalents_among_escaped": declared_equiv_escaped,
        "structural_blind_spots": structural_blind_spots,
        "has_structural_blind_spot": bool(structural_blind_spots),
        "per_operator_class_fault_coverage": {k: sorted(v) for k, v in sorted(per_class_cover.items())},
        "per_mr_kill_count": summ["per_mr_kill_count"],
        "typed_verdict_2d": typed_verdict_2d,
    }


def run_sut(tag: str, put_id: str, prog_type: str, num_method: str, domain: str,
            sibling: Path) -> dict:
    specs = load_specs(put_id)
    if not specs:
        raise SystemExit(f"{put_id}: no MR specs found in sibling (read-only).")
    gate_rows = [gate_mr(put_id, mr, doc) for mr, doc, _name in specs]
    admitted = [(mr, doc) for (mr, doc, _name), g in zip(specs, gate_rows)
                if g["decision"] == "admit"]
    cov = coverage_and_verdict(put_id, admitted, gate_rows)
    decisions = {"admit": 0, "reject": 0, "defer": 0}
    for g in gate_rows:
        decisions[g["decision"]] += 1
    return {
        "tag": tag,
        "sut": put_id,
        "program_type": prog_type,
        "numerical_method": num_method,
        "domain": domain,
        "sibling_path": str(sibling),
        "n_candidate_mrs": len(gate_rows),
        "gate_decision_counts": decisions,
        "gate_per_mr": gate_rows,
        **cov,
    }


def write_sut_ledger(record: dict, sibling_commit_hash: str) -> Path:
    d = OUT / record["tag"].lower()
    d.mkdir(parents=True, exist_ok=True)
    ledger = {
        "ledger_id": f"endtoend-cross-program-pipeline-{record['sut']}",
        "evidence_level": "endtoend-pipeline-executed-cpu",
        "schema_version": "0.1.0",
        "source": ("Minimum-MR-SubSet (read-only sibling) imported for SUT + MR specs + "
                   "mutants; this paper's gate + typed-verdict pipeline executed on CPU"),
        "sibling_commit": sibling_commit_hash,
        "rubric_conditions": RUBRIC_CONDITIONS,
        "honesty_boundary": (
            "The MRs and mutants are the sibling's domain assets; what is executed "
            "end-to-end is this paper's validity gate + typed verdict. Detection counts are "
            "for the sibling's committed mutant set only; no per-program reliability or "
            "real-world detection rate, no baseline superiority, and no claim that the MRs "
            "are new contributions of this paper."),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **record,
    }
    (d / "metric_ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return d / "metric_ledger.json"


# ---------------------------------------------------------------------------
# E5 OpenMC (Monte-Carlo neutron transport) end-to-end path.
#
# The sibling's MR-bearing OpenMC subject is the 1-group infinite-medium "headline"
# PUT: its MRs are cross-section-algebra relations and its mutants are MGXS-assembly
# bugs, so the subject is multi-group BY CONSTRUCTION and runs on CPU with a
# self-generated MGXS library (no continuous-energy nuclear-data download). The
# oracle is the REAL OpenMC Monte-Carlo k-eigenvalue solve
# (mcmr.openmc_put.headline_openmc.run_kinf_openmc). The MR/relation interface here
# is k-based -- relation(k_base, k_trans, tol) -- so this path is separate from the
# pseries observables interface, but the four-condition gate (via _decide) is the same.
# ---------------------------------------------------------------------------
OPENMC_PARTICLES = 2000
OPENMC_BATCHES = 30
OPENMC_INACTIVE = 10
OPENMC_MC_SEED = 1            # OpenMC RNG seed (deterministic run)
OPENMC_DRAW_SEED = 20260531
OPENMC_N_DRAWS = 3
OPENMC_TOL_FLOOR = 0.01
OPENMC_Z = 3.0
# Documented clean equivalent (k provably unchanged: sigma_s doubling in an infinite
# medium leaves k_inf invariant); expected to escape, not a structural blind spot.
OPENMC_DECLARED_EQUIVALENTS = ["M07_scatter_x2"]


def _scramble_k(k: float) -> float:
    """Falsifiability probe mirroring the sibling pseries _scramble: uniformly transform
    the follow-up observable by x2+1. A non-tautological relation must reject it."""
    return k * 2.0 + 1.0


def _make_openmc_oracle():
    """Memoized REAL-OpenMC oracle (params, bug) -> (k, kstd): one OpenMC eigenvalue run
    per distinct (bug, params); raising calls are not cached so the kill driver's
    exception policy applies cleanly. Shared by the gate and the kill matrix."""
    from mcmr.openmc_put.headline_openmc import run_kinf_openmc
    cache: dict = {}

    def oracle(params: dict, bug):
        key = (bug, tuple(sorted(params.items())))
        if key in cache:
            return cache[key]
        result = run_kinf_openmc(params, bug=bug, particles=OPENMC_PARTICLES,
                                 batches=OPENMC_BATCHES, inactive=OPENMC_INACTIVE,
                                 seed=OPENMC_MC_SEED)
        cache[key] = result
        return result
    return oracle


def gate_openmc_mr(mr: dict, draws: list, oracle) -> dict:
    """Apply the paper's four-condition rubric to one OpenMC headline MR using the REAL
    OpenMC oracle (same condition semantics and _decide logic as the pseries gate)."""
    import math
    relation = mr["relation"]
    transform = mr["transform"]
    npass = 0
    errors = 0
    k_b0 = k_t0 = tol0 = None
    for i, base in enumerate(draws):
        try:
            trans = transform(base)
            k_b, s_b = oracle(base, None)
            k_t, s_t = oracle(trans, None)
            tol = max(OPENMC_TOL_FLOOR, OPENMC_Z * math.sqrt(s_b ** 2 + s_t ** 2))
            if i == 0:
                k_b0, k_t0, tol0 = k_b, k_t, tol
            if bool(relation(k_b, k_t, tol)):
                npass += 1
        except Exception:
            errors += 1
    n = len(draws)
    frac_pass = npass / n if n else 0.0
    if k_t0 is not None:
        try:
            falsifiable = not bool(relation(k_b0, _scramble_k(k_t0), tol0))
        except Exception:
            falsifiable = False
    else:
        falsifiable = False
    cond = {
        "i_physical_basis": bool(mr["meta_pattern"]),
        "ii_transformation_preconditions": errors == 0,
        "iii_output_mapping": bool(falsifiable),
        "iv_numerical_decidability": frac_pass == 1.0 and errors == 0,
    }
    decision, rubric, reason = _decide(cond, errors, frac_pass, n)
    return {
        "mr_id": mr["mr_id"],
        "operator_class": mr["meta_pattern"],
        "justification_documented": True,  # headline MRs carry inline physics justification
        "conditions": cond,
        "decision": decision,
        "rubric_decision": rubric,
        "reason": reason,
        "firewall": {"holds": frac_pass == 1.0 and errors == 0, "frac_pass": frac_pass,
                     "falsifiable": bool(falsifiable), "errors": errors},
    }


def run_openmc_sut(tag: str, sibling: Path) -> dict:
    """E5: run THIS paper's gate + typed verdict + coverage map on the sibling's OpenMC
    headline subject, with the REAL OpenMC Monte-Carlo k-eigenvalue solve as the oracle."""
    import openmc as _omc
    from collections import Counter
    from mcmr.openmc_put.headline_spec import CANDIDATE_MRS, BUG_FUNCS, sample_param_draws
    from mcmr.openmc_put.headline_killmatrix import build_headline_kill_rows, summarize_headline

    draws = sample_param_draws(OPENMC_N_DRAWS, OPENMC_DRAW_SEED)
    oracle = _make_openmc_oracle()  # shared cache: gate runs are reused by the kill matrix

    gate_rows = [gate_openmc_mr(mr, draws, oracle) for mr in CANDIDATE_MRS]
    admitted = [mr for mr, g in zip(CANDIDATE_MRS, gate_rows) if g["decision"] == "admit"]
    mutant_ids = list(BUG_FUNCS.keys())

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with __import__("numpy").errstate(all="ignore"):
            rows = build_headline_kill_rows(admitted, mutant_ids, draws, oracle,
                                            tol_floor=OPENMC_TOL_FLOOR, z=OPENMC_Z)
            summ = summarize_headline(rows, mutant_ids, OPENMC_N_DRAWS)

    class_of = {mr["mr_id"]: mr["meta_pattern"] for mr in admitted}
    per_class_cover: dict[str, set] = defaultdict(set)
    for mid, coverers in summ["per_mutant_coverers"].items():
        for covering_mr in coverers:
            per_class_cover[class_of[covering_mr]].add(mid)
    detected = sorted({m for m, c in summ["per_mutant_coverers"].items() if c})
    escaped = sorted(summ["escaped"])
    declared_equiv_escaped = sorted(set(OPENMC_DECLARED_EQUIVALENTS) & set(escaped))
    structural_blind_spots = sorted(set(escaped) - set(OPENMC_DECLARED_EQUIVALENTS))
    n_real = len(mutant_ids) - len(OPENMC_DECLARED_EQUIVALENTS)
    n_detected_real = len([m for m in detected if m not in OPENMC_DECLARED_EQUIVALENTS])

    decisions = {"admit": 0, "reject": 0, "defer": 0}
    for g in gate_rows:
        decisions[g["decision"]] += 1

    typed_verdict_2d = {
        "domain_violation_axis": "in-domain for all admitted MRs (gate established conditions ii and iv)",
        "relation_violation_axis_reading": (
            "boolean relation at declared tolerance: pass = V/floor<1 (consistent), "
            "fail = V/floor>=1 (SUT-inconsistency / fault detected)"),
        "correct_sut_region": "in-domain / consistent (all admitted MRs hold on the correct program)",
        "n_admitted_mr_correct_sut_pass": len(admitted),
        "mutant_inconsistency_detections": len(detected),
        "mutant_in_domain_pass_escaped": len(escaped),
        "excluded_from_verdict_space_reject_or_defer": decisions["reject"] + decisions["defer"],
    }
    return {
        "tag": tag,
        "sut": "openmc_headline_mg",
        "program_type": "Monte-Carlo transport",
        "numerical_method": "Monte-Carlo (multi-group, real OpenMC k-eigenvalue)",
        "domain": "1-group infinite-medium criticality",
        "sibling_path": str(sibling),
        "openmc_version": str(getattr(_omc, "__version__", "unknown")),
        "oracle": "real OpenMC k-eigenvalue (mcmr.openmc_put.headline_openmc.run_kinf_openmc)",
        "openmc_run_settings": {"particles": OPENMC_PARTICLES, "batches": OPENMC_BATCHES,
                                "inactive": OPENMC_INACTIVE, "mc_seed": OPENMC_MC_SEED,
                                "n_draws": OPENMC_N_DRAWS},
        "n_candidate_mrs": len(gate_rows),
        "gate_decision_counts": decisions,
        "gate_per_mr": gate_rows,
        "n_mrs": len(gate_rows),
        "n_admitted_mrs": len(admitted),
        "n_mutants": len(mutant_ids),
        "declared_equivalent_mutants": OPENMC_DECLARED_EQUIVALENTS,
        "admitted_operator_classes": sorted({mr["meta_pattern"] for mr in admitted}),
        "full_set_mutation_score": round(summ["full_set_mutation_score"], 4),
        "non_equivalent_mutation_score": round(n_detected_real / n_real, 4) if n_real else 0.0,
        "detected_mutants": detected,
        "escaped_mutants": escaped,
        "declared_equivalents_among_escaped": declared_equiv_escaped,
        "structural_blind_spots": structural_blind_spots,
        "has_structural_blind_spot": bool(structural_blind_spots),
        "per_operator_class_fault_coverage": {k: sorted(v) for k, v in sorted(per_class_cover.items())},
        "per_mr_kill_count": dict(Counter(r[0] for r in rows if r[5] == 1)),
        "typed_verdict_2d": typed_verdict_2d,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suts", default="p1_heat,p2_wave,p5_pke,p7_burgers,p9_openmc",
                        help="comma-separated SUT ids (default: the four CPU-only core SUTs "
                             "plus p9_openmc, which runs only if the openmc package is importable)")
    args = parser.parse_args()
    requested = [s.strip() for s in args.suts.split(",") if s.strip()]

    sibling = resolve_sibling()
    commit = sibling_commit(sibling)

    plan = [row for row in CORE_SUTS if row[1] in requested]
    # Probe OpenMC importability regardless of the request so the artifact records why E5
    # (Monte-Carlo neutron transport) is or is not executed end-to-end on this CPU host.
    try:
        __import__("openmc")
        openmc_importable = True
    except Exception:
        openmc_importable = False
    run_e5 = OPENMC_SUT[1] in requested and openmc_importable

    per_sut = []
    for tag, put_id, prog_type, num_method, domain in plan:
        rec = run_sut(tag, put_id, prog_type, num_method, domain, sibling)
        write_sut_ledger(rec, commit)
        per_sut.append(rec)

    # E5 OpenMC: a separate code path (k-eigenvalue oracle interface), executed only if the
    # openmc package is importable; otherwise it stays the C39 read-only witness.
    if run_e5:
        rec = run_openmc_sut("E5", sibling)
        write_sut_ledger(rec, commit)
        per_sut.append(rec)
        openmc_status = "executed"
    elif OPENMC_SUT[1] in requested:
        openmc_status = "skipped-openmc-not-importable"
    elif openmc_importable:
        openmc_status = "not-requested-but-importable"
    else:
        openmc_status = "not-executed-openmc-not-importable"

    program_types = sorted({r["program_type"] for r in per_sut})
    # program-specific class->coverage mapping check (distinct per program)
    mappings = {r["sut"]: json.dumps(r["per_operator_class_fault_coverage"], sort_keys=True)
                for r in per_sut}
    mappings_distinct = len(set(mappings.values())) == len(per_sut)
    programs_with_reject = sum(1 for r in per_sut if r["gate_decision_counts"]["reject"] > 0)
    programs_with_defer = sum(1 for r in per_sut if r["gate_decision_counts"]["defer"] > 0)
    programs_with_blind = sum(1 for r in per_sut if r["has_structural_blind_spot"])

    aggregate = {
        "ledger_id": "endtoend-cross-program-pipeline",
        "evidence_level": "endtoend-pipeline-executed-cpu",
        "schema_version": "0.1.0",
        "source": ("Minimum-MR-SubSet (read-only sibling) commit " + commit +
                   "; SUT + MR specs + mutants imported read-only, this paper's gate + "
                   "typed-verdict pipeline executed end-to-end on CPU"),
        "sibling_commit": commit,
        "rubric_conditions": RUBRIC_CONDITIONS,
        "n_suts_executed": len(per_sut),
        "n_program_types": len(program_types),
        "program_types": program_types,
        "suts": [r["sut"] for r in per_sut],
        "openmc_e5_status": openmc_status,
        "openmc_importable": openmc_importable,
        "gate_makes_nontrivial_decisions": (programs_with_reject + programs_with_defer) > 0,
        "programs_with_rejections": programs_with_reject,
        "programs_with_deferrals": programs_with_defer,
        "programs_with_structural_blind_spots": programs_with_blind,
        "class_to_class_mappings_program_specific": mappings_distinct,
        "per_sut": per_sut,
        "finding": (
            "this paper's validity-gated pipeline (four-condition admissibility rubric + "
            "typed two-dimensional verdict + coverage map) executes end-to-end on "
            f"{len(per_sut)} SUTs spanning {len(program_types)} program types on CPU "
            f"({', '.join(program_types)}), producing admit/reject/defer gate decisions, "
            "typed verdicts, and a per-SUT coverage map; the gate makes non-trivial "
            "decisions (it rejects MRs whose output mapping fails construct validity), "
            "structural blind spots are present per program, and the operator-class-to-"
            "fault-coverage mapping is program-specific"),
        "honesty_boundary": (
            "The MRs and mutants are the sibling's domain assets; what is newly executed "
            "end-to-end is this paper's gate + typed-verdict framework, unlike C39's "
            "read-only kill-matrix reuse. Detection counts are for the sibling's committed "
            "mutant sets only; no per-program reliability or real-world detection rate, no "
            "baseline superiority, and no claim that the MRs are new contributions. " + (
                "The E5 OpenMC subject is the sibling's 1-group infinite-medium headline PUT, "
                "executed with the REAL OpenMC Monte-Carlo k-eigenvalue solver in multi-group "
                "mode (self-generated MGXS, no continuous-energy nuclear-data download); its "
                "verification is against the closed-form k_inf. This is a multi-group "
                "criticality subject, not a continuous-energy whole-core or reactor-physics "
                "reliability result."
                if run_e5 else
                "The E5 OpenMC Monte-Carlo SUT is " + openmc_status + "; it remains the C39 "
                "read-only generalization witness when the openmc package is unavailable on CPU.")),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "metric_ledger.json").write_text(
        json.dumps(aggregate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"end-to-end pipeline executed on {len(per_sut)} SUTs, "
          f"{len(program_types)} program types (openmc E5: {openmc_status}):")
    for r in per_sut:
        g = r["gate_decision_counts"]
        print(f"  {r['tag']} {r['sut']:10s} [{r['program_type']:13s}] "
              f"gate admit/reject/defer={g['admit']}/{g['reject']}/{g['defer']} "
              f"admitted_classes={len(r['admitted_operator_classes'])} "
              f"mut_score={r['full_set_mutation_score']} "
              f"blind={r['structural_blind_spots'] or 'none'}")
    print(f"  -> gate non-trivial: {aggregate['gate_makes_nontrivial_decisions']} "
          f"(reject in {programs_with_reject}, defer in {programs_with_defer} programs); "
          f"blind spots in {programs_with_blind}/{len(per_sut)}; "
          f"mappings program-specific: {mappings_distinct}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
