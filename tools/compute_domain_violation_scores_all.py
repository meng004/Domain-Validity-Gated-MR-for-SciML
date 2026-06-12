"""Extend the domain-violation score D to every executed MR class, from
already-committed artifacts only (no new experiment, no invented numbers).

Background. The two-dimensional verdict of the paper reads each MR outcome as
(relation-violation magnitude) x (domain-violation magnitude). The existing
single-relation script (tools/compute_domain_violation_score.py, unchanged)
operationalizes the domain axis only for mirror-y. The review panel flagged
this as the largest gap. This script gives every executed MR class an honest,
per-relation D from committed precondition measurements, keeping the same
saturating map

    D = m / (m + 1)        in [0, 1),

where m is a dimensionless measure of how far the relation's precondition is
violated on the case actually executed. Per-relation definitions of m:

  MGN family
  ----------
  - node-permutation: a permutation is an exact relabeling of the node set;
    there is no geometric or physical precondition that a permutation could
    violate, and the follow-up input is samplable exactly (bit-identical
    coordinates). m = 0 by construction, hence D = 0.
  - mirror-y, synthetic symmetric mesh: m = worst reflection involution offset
    over the median edge length (committed symmetric-mesh ledger), as in the
    existing single-relation script.
  - mirror-y, real asymmetric eval mesh: m = max nearest-existing-node
    distance of reflected nodes in median-edge-length units (committed
    precondition report), as in the existing single-relation script.
  - absolute conservation (discrete divergence-free): the relation's validity
    domain requires the underlying flow data, restricted to the deployed
    open-boundary mesh, to be discretely divergence-free. The committed
    measurement of how far the deployed case sits from that domain is the
    reference field's own nondimensional discrete-divergence imbalance
    (mean_reference_nondim_divergence, an open-boundary flux-imbalance
    relative quantity). m = that imbalance. Note: the executed verdict for
    this MR was DEFERRED via the numerical-decidability gate (no calibratable
    absolute tolerance: imbalance / tol ~ 3.7e4), which is the tolerance axis
    of the verdict plane, not the domain axis; D quantifies only the
    domain-side precondition imbalance.
  - operator-floor diagnostic (P1 divergence resolution sweep): the reference
    field is an analytic stream-function field with div(u) = 0 exactly, on a
    mesh family symmetric by construction; the precondition is satisfied
    exactly. m = 0 by construction, D = 0. (This is the calibration
    diagnostic that feeds the admissibility predicate, not a verdict-bearing
    MR execution.)

  PINN family (closed-form domain [-1,1]^2, committed cross-family reports)
  --------------------------------------------------------------------------
  - MR-A collocation-point permutation: pointwise MLP evaluation is
    row-independent, so permuting evaluation points and inverting is an exact
    relabeling with no precondition to violate (the relation is vacuous by
    construction, per claim C14). m = 0 by construction, D = 0; committed
    measured violations <= ~1e-8 are consistency checks only.
  - MR-B mirror-y equivariance: the closed-form square domain is exactly
    invariant under the mirror, reflected evaluation points are computed in
    closed form (no mesh, no interpolation), and the committed SUT manifests
    record has_mirror_symmetry = true for PDE/BC/IC. The reflected-point
    placement error, the same m used for the MGN mirror-y score, is exactly 0
    by construction, hence D = 0. (So a measured MR-B failure on the heat
    seeds reads as SUT inconsistency, not out-of-domain, modulo the
    self-reported residual floor caveat of C14.)
  - MR-C reference-relative conservation: the precondition for an exact
    conservation reading is that the committed reference solution actually
    conserves the tracked quantity Q over the snapshot window; the committed
    measurement is the relative drift of Q_ref. m = max_t |Q_ref(t) -
    Q_ref(0)| / |Q_ref(0)| from the committed per-snapshot raw tables:
    Burgers (Dirichlet zero BC, open imbalance) m ~ 0.042; heat (Neumann
    zero-flux) m = 0 (Q_ref bit-identical across snapshots).
  - MR-C per-K=6-roster-seed: the K=6 roster reports commit only median
    conservation ratios, not per-snapshot Q_ref, so a per-seed D cannot be
    computed from committed data. Status:
    not-operationalizable-from-committed-data (class-level D comes from the
    cross-family pilot artifacts above).

Honesty boundary. Each D is a per-relation operationalization from committed
measurements. The D values are NOT mutually calibrated across MR classes or
domains, and no claim of a validated cross-domain score is made.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "research_assets/runs"

SRC = {
    "node_perm_ledger": RUNS / "real-sut-node-permutation-pilot/raw/metric_ledger.json",
    "mirror_real_precond": RUNS / "mirror-y-rate-upgrade/raw/precondition_report.json",
    "mirror_sym_ledger": RUNS / "mirror-y-symmetric-mesh/raw/metric_ledger.json",
    "conservation_report": RUNS / "conservation-diagnostic-pilot/raw/conservation_report.json",
    "operator_floor": RUNS / "operator-floor-sweep/operator_floor_report.json",
    "pinn_k6_aggregate": RUNS / "pinn-k6-roster/pinn_k6_aggregate.json",
    "pinn_burgers_report": RUNS / "pinn-cross-family/pinn_mr_report.json",
    "pinn_heat_report": RUNS / "pinn-cross-family-diffusion/pinn_mr_report.json",
}

OUT = RUNS / "domain-violation-score-all/domain_violation_scores_all.json"

STATUS_OK = "operationalized-from-committed-data"
STATUS_CONSTRUCTION = "exact-by-construction"
STATUS_BLOCKED = "not-operationalizable-from-committed-data"


def saturating(m: float) -> float:
    return m / (m + 1.0)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def entry(relation_id, family, status, m, sources, m_definition, honesty_boundary, **extra):
    d = None if m is None else saturating(float(m))
    if m is not None:
        assert m >= 0.0, relation_id
        assert d is not None and 0.0 <= d < 1.0, relation_id
    e = {
        "relation_id": relation_id,
        "family": family,
        "status": status,
        "m": m,
        "D": d,
        "m_definition": m_definition,
        "sources": [rel(s) for s in sources],
        "honesty_boundary": honesty_boundary,
    }
    e.update(extra)
    return e


def main() -> int:
    for name, p in SRC.items():
        if not p.exists():
            raise SystemExit(f"missing committed source {name}: {p}")

    node_perm = json.loads(SRC["node_perm_ledger"].read_text())
    real = json.loads(SRC["mirror_real_precond"].read_text())
    sym = json.loads(SRC["mirror_sym_ledger"].read_text())["precondition_report"]
    cons = json.loads(SRC["conservation_report"].read_text())
    floor = json.loads(SRC["operator_floor"].read_text())
    k6 = json.loads(SRC["pinn_k6_aggregate"].read_text())
    pb = json.loads(SRC["pinn_burgers_report"].read_text())
    ph = json.loads(SRC["pinn_heat_report"].read_text())

    edge = float(real["median_edge_length"])

    # --- MGN ---
    e_node_perm = entry(
        "mgn-node-permutation", "MGN", STATUS_CONSTRUCTION, 0.0,
        [SRC["node_perm_ledger"]],
        "m = 0 by construction: a node permutation is an exact relabeling with "
        "no geometric/physical precondition to violate; the follow-up input is "
        "exactly samplable (bit-identical coordinates).",
        "Construction argument; the committed pilot ledger records the executed "
        "relation (measured violation 0.0 <= 1e-6) but D = 0 does not depend on "
        "the measurement.",
        measured_relation_violation=node_perm["entries"][0]["metric_value"],
    )

    m_sym = float(sym["reflection_offset_max"]) / edge
    e_mirror_sym = entry(
        "mgn-mirror-y-synthetic-symmetric-mesh", "MGN", STATUS_OK, m_sym,
        [SRC["mirror_sym_ledger"], SRC["mirror_real_precond"]],
        "m = worst reflection involution offset (committed symmetric-mesh "
        "ledger, ~machine epsilon) over the real-mesh median edge length, the "
        "common length scale used by the existing single-relation script.",
        "Geometry-only score; same definition as the committed single-relation "
        "report (low D: a violation here reads as SUT inconsistency).",
        reflection_offset_max=sym["reflection_offset_max"],
        bijection=sym.get("bijection"),
    )

    m_real = float(real["max_nn_over_edge"])
    e_mirror_real = entry(
        "mgn-mirror-y-real-asymmetric-mesh", "MGN", STATUS_OK, m_real,
        [SRC["mirror_real_precond"]],
        "m = worst reflected-node nearest-existing-node distance in "
        "median-edge-length units (committed precondition report).",
        "Geometry-only score; same definition and value as the committed "
        "single-relation report (high D: out-of-relation-domain / OOD-stress).",
        bijection=real.get("bijection"),
        precondition_decision=real.get("precondition_decision"),
    )

    m_cons = float(cons["mean_reference_nondim_divergence"])
    e_cons = entry(
        "mgn-conservation-absolute-divergence-free", "MGN", STATUS_OK, m_cons,
        [SRC["conservation_report"]],
        "m = mean nondimensional discrete-divergence imbalance of the committed "
        "reference field on the deployed open-boundary mesh "
        "(mean_reference_nondim_divergence): the open-boundary flux-imbalance "
        "relative quantity, i.e. how far the deployed data sit from the "
        "divergence-free validity domain of the absolute relation.",
        "D quantifies only the domain-side precondition imbalance. The executed "
        "verdict for this MR was DEFERRED through the numerical-decidability "
        "gate (the absolute tolerance 1e-6 is uncalibratable: imbalance/tol "
        "~ 3.7e4), which is the tolerance axis of the verdict plane, not the "
        "domain axis. No absolute conservation claim is made or implied.",
        absolute_divergence_tol=cons["absolute_divergence_tol"],
        imbalance_over_absolute_tol=m_cons / float(cons["absolute_divergence_tol"]),
        executed_verdict=cons["absolute_relation_decision"],
    )

    e_floor = entry(
        "mgn-operator-floor-diagnostic", "MGN", STATUS_CONSTRUCTION, 0.0,
        [SRC["operator_floor"]],
        "m = 0 by construction: the committed sweep evaluates the P1 divergence "
        "operator on an analytic stream-function field with div(u) = 0 exactly, "
        "on a mesh family symmetric by construction, so the precondition is "
        "satisfied exactly.",
        "Calibration diagnostic feeding the admissibility predicate, not a "
        "verdict-bearing MR execution; D = 0 states only that its reference "
        "field is in-domain by construction.",
        analytic_reference=floor["analytic_reference"]["velocity"],
    )

    # --- PINN ---
    mr_a_max = max(float(s["mr_a_violation"]) for s in k6["per_sut"])
    e_pinn_a = entry(
        "pinn-mr-a-collocation-permutation", "PINN", STATUS_CONSTRUCTION, 0.0,
        [SRC["pinn_k6_aggregate"]],
        "m = 0 by construction: pointwise MLP evaluation is row-independent, so "
        "permuting evaluation points and inverting is an exact relabeling with "
        "no precondition to violate (relation vacuous by construction, C14).",
        "Construction argument; committed K=6 measured violations (max "
        f"{mr_a_max:.3g}) are well-definedness checks only and carry no "
        "evidential weight.",
        measured_relation_violation_max=mr_a_max,
    )

    pinn_b_entries = []
    for pid, rep, src in (("burgers", pb, SRC["pinn_burgers_report"]),
                          ("heat", ph, SRC["pinn_heat_report"])):
        pinn_b_entries.append(entry(
            f"pinn-mr-b-mirror-y-{pid}", "PINN", STATUS_CONSTRUCTION, 0.0,
            [src, SRC["pinn_k6_aggregate"]],
            "m = 0 by construction: the closed-form domain [-1,1]^2 is exactly "
            "invariant under the mirror and reflected evaluation points are "
            "computed in closed form (no mesh, no interpolation), so the "
            "reflected-point placement error (the same m as the MGN mirror-y "
            "score) is exactly zero; the committed SUT manifest records "
            "has_mirror_symmetry = true.",
            "With D = 0, a measured MR-B failure (heat seeds s1/s2 in the K=6 "
            "roster) reads as SUT inconsistency on the verdict plane, subject "
            "to C14's caveat that the floor is the PINN's self-reported PDE "
            "residual, not an independently calibrated floor.",
            has_mirror_symmetry=rep["sut"]["has_mirror_symmetry"],
        ))

    qb = [float(r["Q_ref"]) for r in pb["per_snapshot_raw"]]
    m_c_burgers = max(abs(q - qb[0]) for q in qb) / abs(qb[0])
    e_pinn_c_b = entry(
        "pinn-mr-c-conservation-burgers", "PINN", STATUS_OK, m_c_burgers,
        [SRC["pinn_burgers_report"]],
        "m = max_t |Q_ref(t) - Q_ref(0)| / |Q_ref(0)| over the committed "
        "per-snapshot reference table (Q = integral of u_x, Dirichlet zero BC): "
        "the open-boundary flux-imbalance relative quantity of the reference "
        "itself.",
        "Nonzero m is exactly why the executed MR is reference-relative rather "
        "than absolute; D quantifies the distance of the deployed case from an "
        "exact-conservation validity domain.",
        q_ref_first=qb[0], q_ref_last=qb[-1],
    )

    qh = [float(r["Q_ref"]) for r in ph["per_snapshot_raw"]]
    m_c_heat = max(abs(q - qh[0]) for q in qh) / abs(qh[0])
    e_pinn_c_h = entry(
        "pinn-mr-c-conservation-heat", "PINN", STATUS_OK, m_c_heat,
        [SRC["pinn_heat_report"]],
        "m = max_t |Q_ref(t) - Q_ref(0)| / |Q_ref(0)| over the committed "
        "per-snapshot reference table (Q = integral of u, Neumann zero-flux "
        "BC): the committed reference conserves Q bit-identically, so m = 0.",
        "Exact-conservation precondition holds on the committed reference "
        "(zero-flux boundary); a conservation violation here would read as "
        "SUT inconsistency.",
        q_ref_first=qh[0], q_ref_last=qh[-1],
    )

    e_pinn_c_k6 = entry(
        "pinn-mr-c-conservation-k6-per-seed", "PINN", STATUS_BLOCKED, None,
        [SRC["pinn_k6_aggregate"]],
        "A per-K=6-seed D would need per-snapshot Q_ref tables, which the "
        "committed K=6 roster reports do not contain (they commit only median "
        "conservation ratios).",
        "Not operationalizable from committed data; no number is invented. The "
        "class-level D for PINN MR-C comes from the cross-family pilot "
        "artifacts (entries pinn-mr-c-conservation-burgers / -heat).",
        reason="pinn-k6-roster/*/mr_report.json commit only mr_c_median_ratio; "
               "no per-snapshot Q_ref is committed.",
    )

    relations = [
        e_node_perm, e_mirror_sym, e_mirror_real, e_cons, e_floor,
        e_pinn_a, *pinn_b_entries, e_pinn_c_b, e_pinn_c_h, e_pinn_c_k6,
    ]

    report = {
        "record_type": "domain-violation-score-all",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "definition": (
            "Per-relation domain-violation score D = m/(m+1) in [0,1), where m "
            "is a dimensionless, relation-specific measure of precondition "
            "violation computed from already-committed artifacts only; see "
            "m_definition per entry."),
        "relations": relations,
        "honesty_boundary": (
            "Per-relation operationalization from committed measurements only. "
            "The per-relation m's use different relation-specific units, so the "
            "D values are NOT mutually calibrated across MR classes or domains; "
            "no cross-domain calibrated or validated domain-violation metric is "
            "claimed. Entries marked exact-by-construction rest on construction "
            "arguments recorded alongside committed artifacts; the one entry "
            "without committed support is explicitly marked "
            "not-operationalizable-from-committed-data."),
    }

    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    for e in relations:
        d = "  None" if e["D"] is None else f"{e['D']:.4f}"
        m = "None" if e["m"] is None else f"{e['m']:.4g}"
        print(f"  {e['relation_id']:<45} D={d}  m={m}  [{e['status']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
