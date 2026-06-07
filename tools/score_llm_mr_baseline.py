"""P2-2 companion: score LLM-generated candidate MRs by this paper's predicate.

Reads `research_assets/runs/llm-mr-baseline/llm_candidates.json`, applies the
four-condition admissibility predicate from the manuscript thesis (physical /
software basis  ^  transformation preconditions  ^  boundary + output-mapping
compatibility  ^  numerical decidability) to each candidate using only the
fields the LLM was instructed to provide, and reports overlap with the three
MRs this paper identifies (node-permutation equivariance, mirror-y reflection,
discrete divergence-free conservation).

Grading is deterministic and explainable: each dimension is scored from the
candidate's own self-declared fields (not a hidden rubric), with three discrete
levels (admit / qualified / reject) per dimension. A candidate is admitted by
the predicate iff every dimension is at least `qualified` AND `numerical
decidability` is explicitly addressed (not "unspecified"). This mirrors the
predicate's "all four conditions hold together" semantics from the manuscript.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "research_assets/runs/llm-mr-baseline/llm_candidates.json"
DEFAULT_OUT = ROOT / "research_assets/runs/llm-mr-baseline/llm_baseline_report.json"

PAPER_MRS = {
    "node_permutation_equivariance": [
        "node permutation", "permutation equivariance", "relabeling",
        "node relabel", "vertex permutation", "permute node", "node ordering",
        "permute the node", "graph-isomorphism", "graph isomorphism"],
    "mirror_y_reflection": [
        "mirror", "reflection", "y-symmetry", "transverse symmetry",
        "y-reflect", "reflect across"],
    "discrete_divergence_free_conservation": [
        "divergence", "incompressibility", "incompressible", "mass conservation",
        "continuity", "div(u)", "div u"],
}


def _has_any(text: str, needles: list[str]) -> bool:
    t = (text or "").lower()
    return any(n.lower() in t for n in needles)


def _word_hit(text: str, needles: list[str]) -> bool:
    for n in needles:
        if re.search(rf"(?<![a-z]){re.escape(n)}(?![a-z])", text):
            return True
    return False


def _grade_dim(value: str | None, positive: list[str], negative: list[str]) -> str:
    v = (value or "").strip().lower()
    if not v or v in {"none", "unspecified", "n/a"}:
        return "reject"
    if _word_hit(v, negative):
        return "reject"
    if _word_hit(v, positive):
        return "admit"
    return "qualified"


def grade_candidate(c: dict) -> dict:
    basis = _grade_dim(c.get("physical_basis"),
                       positive=["conservation", "symmetry", "boundary",
                                 "invariance", "incompressibility",
                                 "newton", "navier-stokes", "contract"],
                       negative=["unknown", "guess"])
    pre = _grade_dim(c.get("preconditions"),
                     positive=["geometry", "bc ", "boundary", "regime",
                               "initial", "mesh", "reynolds", "field"],
                     negative=["unknown"])
    bo_raw = (c.get("boundary_output_compatibility") or "").strip().lower()
    if not bo_raw or bo_raw in {"none", "unspecified", "n/a"}:
        bo = "reject"
    elif _word_hit(bo_raw, ["incompatible", "incompat", "breaks", "violates"]) \
            or re.search(r"\b(does not|do not|doesn't|don't)\b.*\b(preserve|commute|compatible)\b", bo_raw) \
            or re.search(r"^\s*no[,\.\s]", bo_raw):
        bo = "reject"
    elif _word_hit(bo_raw, ["preserve", "preserved", "commute", "commutes",
                            "compatible", "consistent", "yes"]):
        bo = "admit"
    else:
        bo = "qualified"
    tol_text = c.get("tolerance_rationale") or ""
    has_floor = bool(re.search(
        r"floor|truncation|operator error|discretization|rounding|h\^|mesh size|step size|epsilon machine|machine precision",
        tol_text.lower()))
    if not tol_text.strip():
        num = "reject"
    elif has_floor:
        num = "admit"
    else:
        num = "qualified"

    dims = {"physical_basis": basis,
            "preconditions": pre,
            "boundary_output_compatibility": bo,
            "numerical_decidability": num}
    admitted = all(v in {"admit", "qualified"} for v in dims.values()) and num != "reject"

    blob = " ".join(str(c.get(k, "")) for k in
                    ("name", "source_transformation", "expected_relation",
                     "physical_basis", "preconditions"))
    overlap = {label: _has_any(blob, needles)
               for label, needles in PAPER_MRS.items()}

    return {"name": c.get("name", "?"),
            "dimensions": dims,
            "predicate_admitted": admitted,
            "overlaps_paper_mr": overlap,
            "any_overlap": any(overlap.values())}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default=str(DEFAULT_IN))
    p.add_argument("--output", default=str(DEFAULT_OUT))
    args = p.parse_args(argv)

    src = Path(args.input)
    if not src.exists():
        raise SystemExit(
            f"BLOCKED_NO_LLM_OUTPUT: {src} not found. Run "
            f"tools/run_llm_mr_baseline.py first (it requires OPENAI_API_KEY + "
            f"OPENAI_BASE_URL).")
    doc = json.loads(src.read_text())
    graded = [grade_candidate(c) for c in doc.get("candidates", [])]
    n = len(graded)
    n_admit = sum(1 for g in graded if g["predicate_admitted"])
    n_overlap = sum(1 for g in graded if g["any_overlap"])
    per_mr_overlap = {label: sum(1 for g in graded if g["overlaps_paper_mr"][label])
                      for label in PAPER_MRS}

    report = {
        "record_type": "llm-mr-baseline-report",
        "schema_version": "0.1.0",
        "input": str(src.relative_to(ROOT)) if ROOT in src.parents else str(src),
        "model_used": doc.get("model_used"),
        "n_candidates": n,
        "n_admitted_by_predicate": n_admit,
        "n_overlap_with_paper_mrs": n_overlap,
        "per_paper_mr_overlap_count": per_mr_overlap,
        "per_candidate": graded,
        "predicate_definition": (
            "physical/software basis ^ transformation preconditions ^ boundary + "
            "output-mapping compatibility ^ numerical decidability "
            "(verdict tolerance must dominate the operator floor)."),
        "honesty_boundary": (
            "Self-reported fields by one LLM, graded by this paper's own "
            "rubric. Not a multi-rater study; not a claim that this LLM is "
            "representative of LLMs in general. The point is the comparison "
            "the paper claims is missing: which LLM-proposed MRs survive the "
            "admissibility gate."),
    }
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"summary: {n_admit}/{n} admitted by predicate, "
          f"{n_overlap}/{n} overlap with this paper's MRs")
    for label, k in per_mr_overlap.items():
        print(f"  overlap with {label}: {k}/{n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
