"""Generic automatic-MR-generation baseline (scope contrast for C3).

A domain-agnostic automatic MR generator proposes candidate relations from a
fixed catalogue of generic metamorphic-transformation templates (the standard
MT patterns: additive/multiplicative input changes, permutations, geometric
symmetries, translations, channel swaps, temporal reversal, resolution change).
Such generators are *domain-blind*: they do not know the cylinder-flow geometry,
boundary conditions, or governing equations.

This script encodes that catalogue and runs each template through this paper's
four-condition admissibility predicate. The admissibility of each template for
the MeshGraphNets cylinder-flow SUT is a determinable fact, recorded here as
four booleans with a one-line justification each:

  basis        : does the transformation rest on a real physical or software
                 invariance of THIS SUT (conservation, symmetry, BC, graph
                 relabelling), as opposed to an arbitrary perturbation?
  precond      : can the source case satisfy the transformation's preconditions
                 within the cylinder-flow regime?
  bc_output    : does the transformation preserve the boundary-condition
                 structure and commute with the output mapping?
  numerically  : is there a verdict tolerance that dominates the measuring
  decidable      operator's error floor (machine precision / mapping floor /
                 discretization floor)?

A template is ADMITTED by the predicate iff all four hold. The headline is the
contrast: a generic generator yields many candidates but the rubric admits only
the few that happen to encode a true SUT invariance, rejecting the rest with a
stated reason -- the empirical form of the "what does the rubric add" question.

This is a deterministic, offline scope contrast (no LLM, no network); it is NOT
a claim that generic generators are useless, only that, unguided, their
admissible yield on this SUT is low and the rubric makes the rejections
explicit and auditable.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/generic-mr-baseline/generic_mr_report.json"

# Each template: (id, transformation, basis, precond, bc_output, numerically_
# decidable, justification, overlaps_paper_mr). The four booleans are
# determinable admissibility facts for the cylinder-flow SUT.
TEMPLATES = [
    ("node_permutation", "relabel mesh nodes by a permutation",
     True, True, True, True,
     "Graph-relabelling invariance is a true software contract of a GNN; exact to machine precision.",
     "node_permutation_equivariance"),
    ("edge_reorder", "shuffle the edge list / edge features",
     True, True, True, True,
     "Edge-set permutation invariance is a true GNN contract; exact.",
     "node_permutation_equivariance"),
    ("mirror_y_reflection", "reflect domain and velocity about y=0",
     True, True, False, True,
     "A real symmetry, but the BOUNDARY/output compatibility fails on the asymmetric eval mesh (non-bijective reflection); admissible only on a symmetric mesh.",
     "mirror_y_reflection"),
    ("mirror_x_reflection", "reflect domain and velocity about x=0",
     False, False, False, True,
     "Inflow/outflow boundaries are not x-symmetric; reflecting swaps inlet and outlet, so there is no x-reflection invariance.",
     None),
    ("rotation_90", "rotate the domain by 90 degrees",
     False, False, False, True,
     "The cylinder-flow inflow direction and channel walls are not rotation-invariant; no basis.",
     None),
    ("domain_translation", "translate all node positions by a vector",
     False, False, False, True,
     "Translating moves nodes out of the bounded channel and breaks the fixed wall/inflow BCs.",
     None),
    ("discrete_divergence_conservation", "compare predicted vs reference divergence",
     True, True, True, True,
     "Incompressibility is a true governing constraint; reference-relative ratio is numerically decidable against the O(h) operator floor.",
     "discrete_divergence_free_conservation"),
    ("additive_output_constant", "add a constant to the predicted velocity",
     False, True, False, True,
     "No physical invariance: the surrogate output is not invariant to an arbitrary additive offset, and walls fix velocity to zero.",
     None),
    ("input_global_scaling", "multiply the input velocity field by a constant",
     False, False, True, True,
     "Navier-Stokes is not scale-invariant at fixed viscosity/Reynolds; arbitrary scaling leaves the regime.",
     None),
    ("input_additive_noise", "add random noise to the input field",
     False, True, True, False,
     "No invariance basis, and no verdict tolerance dominates a noise-magnitude-dependent floor; at best a robustness probe, not an MR.",
     None),
    ("channel_swap", "swap the vx and vy velocity channels",
     False, True, False, True,
     "Swapping channels is not a symmetry of an anisotropic channel flow; useful only as a fault injection, not as a relation the SUT should satisfy.",
     None),
    ("time_reversal", "reverse the temporal stepping direction",
     False, False, True, True,
     "Viscous diffusion is irreversible; the surrogate is not time-reversal invariant.",
     None),
    ("mesh_coarsening", "predict on a coarsened mesh and compare",
     False, False, False, False,
     "Changing the discretization changes the SUT input distribution; no fixed tolerance separates model error from discretization change.",
     None),
]

PAPER_MRS = {"node_permutation_equivariance", "mirror_y_reflection",
             "discrete_divergence_free_conservation"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(OUT.parent))
    args = ap.parse_args(argv)
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    per_template = []
    for (tid, transform, basis, precond, bc, num, why, overlap) in TEMPLATES:
        dims = {"physical_or_software_basis": basis,
                "transformation_preconditions": precond,
                "boundary_output_compatibility": bc,
                "numerical_decidability": num}
        admitted = all(dims.values())
        per_template.append({
            "template_id": tid, "transformation": transform,
            "admissibility": dims, "predicate_admitted": admitted,
            "justification": why,
            "overlaps_paper_mr": overlap,
        })

    n = len(per_template)
    n_admit = sum(1 for t in per_template if t["predicate_admitted"])
    admitted_ids = [t["template_id"] for t in per_template if t["predicate_admitted"]]
    # Of the admitted templates, how many coincide with a paper MR?
    admitted_overlap = [t["template_id"] for t in per_template
                        if t["predicate_admitted"] and t["overlaps_paper_mr"]]
    # Failure breakdown: which condition most often blocks a template.
    fail_by_dim = {d: 0 for d in
                   ("physical_or_software_basis", "transformation_preconditions",
                    "boundary_output_compatibility", "numerical_decidability")}
    for t in per_template:
        if not t["predicate_admitted"]:
            for d, v in t["admissibility"].items():
                if not v:
                    fail_by_dim[d] += 1

    report = {
        "record_type": "generic-mr-baseline",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "domain-agnostic template catalogue (standard MT transformation patterns)",
        "predicate": "four-condition admissibility (basis ^ preconditions ^ BC/output ^ numerical decidability)",
        "n_templates": n,
        "n_admitted_by_predicate": n_admit,
        "admitted_template_ids": admitted_ids,
        "admitted_overlapping_paper_mrs": admitted_overlap,
        "rejection_breakdown_by_failed_condition": fail_by_dim,
        "per_template": per_template,
        "headline": (
            f"A domain-blind generic generator proposes {n} candidate templates; "
            f"the admissibility predicate admits {n_admit}/{n}, and every admitted "
            f"template coincides with an MR this paper already identifies "
            f"({admitted_overlap}). The rubric's value is the {n - n_admit} reasoned "
            f"rejections, each tied to a specific failed condition."),
        "honesty_boundary": (
            "Deterministic offline scope contrast over a fixed template catalogue "
            "with determinable per-template admissibility facts; not a learned "
            "generator, not a claim that generic generation is useless, and not a "
            "real-world yield rate beyond this SUT and catalogue."),
    }
    (outdir / "generic_mr_report.json").write_text(json.dumps(report, indent=2),
                                                   encoding="utf-8")
    print(f"wrote {outdir / 'generic_mr_report.json'}")
    print(f"  templates: {n}; admitted: {n_admit}; admitted ids: {admitted_ids}")
    print(f"  all admitted overlap a paper MR: "
          f"{set(admitted_ids) == set(admitted_overlap)}")
    print(f"  rejection breakdown by failed condition: {fail_by_dim}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
