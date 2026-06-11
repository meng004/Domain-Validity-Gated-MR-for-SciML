"""P1: LLM-simulated expert MR baseline (3-expert proposal × 3-rater vote).

Protocol
--------
Phase A — Proposal (simulating human domain experts):
  Three vendor-disjoint LLMs role-play experienced SciML/CFD engineers who have
  never seen this paper's rubric. Each independently proposes candidate MRs for
  the MeshGraphNets cylinder-flow surrogate from first principles and domain
  expertise, given only the SUT I/O contract and physical setup.

Phase B — Rubric evaluation (3-rater majority vote):
  Three different vendor-disjoint LLMs evaluate each proposed MR against this
  paper's four-condition admissibility predicate. Per-MR verdict = majority vote.

Phase C — Synthesis:
  Deduplicate proposals across experts; compute overlap with the paper's three
  retained MRs; report what the rubric adds over unguided expert elicitation.

Honest scope:
  - LLM-simulated, not human experts. Recorded as such in the claim ledger.
  - Temperature=0, single sample per model. Not a generative-model benchmark.
  - The rubric is this paper's own predicate, not an independent standard.

Credentials (env vars):
  OPENAI_API_KEY   (required)
  OPENAI_BASE_URL  (required)  e.g. https://llm-api.net/v1
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets" / "runs" / "expert-mr-baseline"

EXPERT_MODELS = [
    "gpt-5.1-chat",
    "deepseek-v4-pro",
    "qwen3-max",
]

RATER_MODELS = [
    "claude-opus-4-8",
    "Kimi-K2-Instruct",
    "glm-4",
]

TOKEN_LADDER = (12000, 24000)

EXPERT_PROMPT = """You are a senior software-testing researcher with 10+ years of experience
in metamorphic testing for scientific computing. You also have strong domain
knowledge of computational fluid dynamics, mesh-based numerical methods, and
neural-network surrogates for physics simulation.

A colleague asks you to propose candidate metamorphic relations (MRs) for
testing the following system:

SYSTEM UNDER TEST (SUT):
  A MeshGraphNets-family graph neural network surrogate.
  - Input: velocity field (vx, vy) on an unstructured 2D triangular mesh at
    time t. The mesh encodes a channel with a circular cylinder obstacle.
    Incompressible Newtonian flow, Reynolds ~1000, no-slip walls, Poiseuille
    inflow profile. The mesh is fixed across the trajectory.
  - Output: predicted velocity field (vx, vy) at time t+1 (one-step rollout).
  - The model was trained by supervised learning on simulation data from the
    DeepMind cylinder-flow benchmark.
  - The mesh has ~1,885 nodes and ~5,500 triangular cells. Node features
    include coordinates, velocity, node type (interior/wall/inflow/outflow/
    obstacle). Edge features encode relative displacement and distance.

Your task: propose as many candidate MRs as you can think of — at least 8.
For each, provide:

  - "name": short identifier
  - "source_transformation": how to build the follow-up input from the source
  - "expected_relation": what equality/inequality the outputs should satisfy
  - "tolerance_rationale": how to set the tolerance (what numerical floor it
    must dominate, what metric to use, what normalization)
  - "physical_basis": the conservation law, symmetry, boundary condition,
    representation contract, or implementation invariant it relies on
  - "preconditions": conditions the source case must satisfy for the relation
    to hold (geometry, boundary types, flow regime, mesh properties)
  - "failure_interpretation": what a violation of this relation would indicate
    about the SUT
  - "expected_difficulty": one of "exact", "approximate", "diagnostic_only"

Think carefully about:
  - Representation-level invariants of the GNN architecture
  - Physical symmetries of the governing equations and this specific geometry
  - Conservation laws (mass, momentum) and how they apply on discrete meshes
  - Boundary-condition compatibility under transformations
  - What can and cannot be checked without a reference oracle

Output JSON only, shape: {"candidates": [{"name": "...", ...}, ...]}
No surrounding prose, no markdown fences.
"""

RATER_PROMPT_TEMPLATE = """You are reviewing a candidate metamorphic relation (MR) proposed
for testing a MeshGraphNets neural-network cylinder-flow surrogate.

The paper uses a four-condition admissibility predicate to screen MRs:
  (i)   Physical or software basis: the relation must rest on a stated
        equation, symmetry, boundary condition, representation contract, or
        implementation invariant.
  (ii)  Transformation preconditions: it must be clear what changes from source
        to follow-up, and what must be preserved.
  (iii) Boundary-condition and output-mapping compatibility: the transformation
        must preserve boundary semantics, and the output comparison must be
        well-defined after the transformation.
  (iv)  Numerical decidability: the verdict tolerance must dominate the
        intrinsic error floor of the measurement operator (machine precision
        for exact relations, interpolation floor for geometric relations,
        discretization floor for PDE-operator relations).

The paper's three retained MRs are:
  1. Node-permutation equivariance (representation-level, exact)
  2. Mirror-y reflection equivariance (geometric symmetry, approximate/OOD-stress
     on the asymmetric DeepMind mesh; exact on a provably symmetric mesh)
  3. Discrete divergence boundedness (continuity constraint, deferred for
     absolute but retained as reference-relative diagnostic)

THE CANDIDATE MR TO EVALUATE:
{candidate_json}

For each of the four conditions, vote:
  - "admit": the candidate clearly satisfies this condition
  - "qualified": satisfies with stated caveats
  - "reject": does not satisfy, with reason

Then give an overall verdict:
  - "retain": all four conditions are admit or qualified
  - "downgrade_ood_stress": conditions (ii)-(iii) hold only approximately
  - "reject": at least one condition is clearly unsatisfied
  - "defer": condition (iv) cannot be established without further evidence

Also assess:
  - "overlaps_paper_mr": which of the paper's three MRs this candidate
    substantially duplicates (list by name, or empty list if novel)
  - "novelty_assessment": whether this candidate adds information beyond the
    paper's existing three MRs

Output JSON only:
{{
  "dimensions": {{
    "physical_basis": "admit|qualified|reject",
    "preconditions": "admit|qualified|reject",
    "boundary_output_compatibility": "admit|qualified|reject",
    "numerical_decidability": "admit|qualified|reject"
  }},
  "dimension_notes": {{
    "physical_basis": "...",
    "preconditions": "...",
    "boundary_output_compatibility": "...",
    "numerical_decidability": "..."
  }},
  "overall_verdict": "retain|downgrade_ood_stress|reject|defer",
  "verdict_justification": "...",
  "overlaps_paper_mr": ["node_permutation"|"mirror_y"|"divergence_conservation"],
  "novelty_assessment": "..."
}}
No surrounding prose, no markdown fences.
"""


def _post_chat(api_key: str, base_url: str, model: str, prompt: str,
               max_tokens: int, timeout: int = 360,
               system_msg: str = "You output JSON only. No prose, no markdown fences.") -> dict:
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "temperature": 0,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
    }).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"content-type": "application/json",
                 "authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _extract_json(raw: dict) -> dict:
    try:
        content = raw["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"unparseable chat response: {e}") from e
    s = re.sub(r"<thinking>.*?</thinking>", "", content, flags=re.S).strip()
    if not s:
        finish = raw.get("choices", [{}])[0].get("finish_reason")
        raise RuntimeError(f"empty content (finish_reason={finish!r})")
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```\s*$", "", s)
    depth = 0
    start = None
    for i, ch in enumerate(s):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                return json.loads(s[start:i + 1])
    if s.strip().startswith('['):
        return {"candidates": json.loads(s)}
    raise RuntimeError(f"no valid JSON object found in: {s[:200]}")


def _call_with_ladder(api_key, base_url, model, prompt, system_msg=None):
    kwargs = {}
    if system_msg:
        kwargs["system_msg"] = system_msg
    last_err = None
    for budget in TOKEN_LADDER:
        try:
            raw = _post_chat(api_key, base_url, model, prompt, budget, **kwargs)
            return _extract_json(raw), raw
        except Exception as e:
            last_err = e
            print(f"  {model} budget={budget} failed: {e}", file=sys.stderr)
            time.sleep(5)
    raise RuntimeError(f"all budgets exhausted for {model}: {last_err}")


def phase_a_propose(api_key, base_url):
    print("=== Phase A: Expert MR Proposal ===")
    results = {}
    for model in EXPERT_MODELS:
        print(f"  Expert: {model} ...", end=" ", flush=True)
        try:
            parsed, raw = _call_with_ladder(api_key, base_url, model, EXPERT_PROMPT)
            candidates = parsed.get("candidates", [])
            print(f"{len(candidates)} candidates")
            results[model] = {
                "candidates": candidates,
                "raw_finish_reason": raw.get("choices", [{}])[0].get("finish_reason"),
                "model": model,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            print(f"FAILED: {e}")
            results[model] = {"error": str(e), "candidates": []}
    return results


def _deduplicate(all_proposals: dict) -> list[dict]:
    seen_names = {}
    deduped = []
    for model, data in all_proposals.items():
        for c in data.get("candidates", []):
            name = c.get("name", "").lower().replace(" ", "_").replace("-", "_")
            key = re.sub(r"[^a-z0-9_]", "", name)
            if key not in seen_names:
                seen_names[key] = model
                c["proposed_by"] = model
                c["dedup_key"] = key
                deduped.append(c)
            else:
                c["proposed_by"] = model
                c["dedup_key"] = key
                c["duplicate_of_model"] = seen_names[key]
                deduped.append(c)
    return deduped


def phase_b_rate(api_key, base_url, all_candidates: list[dict]):
    print(f"\n=== Phase B: Rubric Evaluation ({len(all_candidates)} candidates × {len(RATER_MODELS)} raters) ===")
    results = []
    for i, cand in enumerate(all_candidates):
        cand_json = json.dumps(cand, indent=2, ensure_ascii=False)
        prompt = RATER_PROMPT_TEMPLATE.format(candidate_json=cand_json)
        votes = {}
        for rater in RATER_MODELS:
            print(f"  [{i+1}/{len(all_candidates)}] {cand.get('name','?')} <- {rater} ...", end=" ", flush=True)
            try:
                parsed, _ = _call_with_ladder(api_key, base_url, rater, prompt)
                votes[rater] = parsed
                print(parsed.get("overall_verdict", "?"))
            except Exception as e:
                print(f"FAILED: {e}")
                votes[rater] = {"error": str(e), "overall_verdict": "error"}
            time.sleep(1)

        verdicts = [v.get("overall_verdict", "error") for v in votes.values() if v.get("overall_verdict") != "error"]
        if verdicts:
            from collections import Counter
            vc = Counter(verdicts)
            majority_verdict = vc.most_common(1)[0][0]
        else:
            majority_verdict = "error"

        overlap_sets = []
        for v in votes.values():
            overlap_sets.extend(v.get("overlaps_paper_mr", []))
        overlap_union = list(set(overlap_sets))

        results.append({
            "candidate": cand,
            "per_rater_votes": votes,
            "majority_verdict": majority_verdict,
            "verdict_distribution": dict(Counter(verdicts)) if verdicts else {},
            "overlaps_paper_mr_union": overlap_union,
        })
    return results


def phase_c_synthesize(proposals: dict, rated: list[dict]) -> dict:
    n_total = len(rated)
    n_unique = len(set(r["candidate"].get("dedup_key", str(i)) for i, r in enumerate(rated)
                       if "duplicate_of_model" not in r["candidate"]))
    n_duplicate = n_total - n_unique

    verdict_counts = {}
    for r in rated:
        v = r["majority_verdict"]
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    retained = [r for r in rated if r["majority_verdict"] in ("retain", "downgrade_ood_stress")]
    rejected = [r for r in rated if r["majority_verdict"] == "reject"]
    deferred = [r for r in rated if r["majority_verdict"] == "defer"]

    overlap_with_paper = {"node_permutation": 0, "mirror_y": 0, "divergence_conservation": 0}
    novel_retained = []
    for r in retained:
        overlaps = r.get("overlaps_paper_mr_union", [])
        if overlaps:
            for o in overlaps:
                if o in overlap_with_paper:
                    overlap_with_paper[o] += 1
        else:
            novel_retained.append(r["candidate"].get("name", "?"))

    rubric_added_value = {
        "rejected_by_rubric": len(rejected),
        "deferred_by_rubric": len(deferred),
        "rubric_rejection_rate": len(rejected) / n_total if n_total else 0,
        "novel_candidates_retained": novel_retained,
        "interpretation": (
            f"Of {n_total} candidates proposed by {len(proposals)} expert-LLMs, "
            f"the admissibility predicate retained {len(retained)}, "
            f"rejected {len(rejected)}, and deferred {len(deferred)}. "
            f"The rubric's rejection/deferral rate ({(len(rejected)+len(deferred))/n_total*100:.0f}%) "
            f"quantifies the admissibility gap between unguided expert elicitation "
            f"and validity-gated MR identification."
        ),
    }

    return {
        "record_type": "expert-mr-baseline-report",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "protocol": "3-expert-proposal × 3-rater-majority-vote",
        "expert_models": EXPERT_MODELS,
        "rater_models": RATER_MODELS,
        "n_total_candidates": n_total,
        "n_unique_candidates": n_unique,
        "n_duplicates": n_duplicate,
        "verdict_counts": verdict_counts,
        "n_retained": len(retained),
        "n_rejected": len(rejected),
        "n_deferred": len(deferred),
        "overlap_with_paper_mrs": overlap_with_paper,
        "novel_retained_names": novel_retained,
        "rubric_added_value": rubric_added_value,
        "per_candidate": rated,
    }


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not base_url:
        return 2

    OUTDIR.mkdir(parents=True, exist_ok=True)

    proposals = phase_a_propose(api_key, base_url)
    (OUTDIR / "expert_proposals.json").write_text(
        json.dumps(proposals, indent=2, ensure_ascii=False))
    print(f"\nSaved proposals to {OUTDIR / 'expert_proposals.json'}")

    all_candidates = _deduplicate(proposals)
    print(f"\nTotal candidates (including duplicates): {len(all_candidates)}")

    rated = phase_b_rate(api_key, base_url, all_candidates)
    (OUTDIR / "expert_rated_candidates.json").write_text(
        json.dumps(rated, indent=2, ensure_ascii=False))

    report = phase_c_synthesize(proposals, rated)
    (OUTDIR / "expert_baseline_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False))

    print(f"\n=== Phase C: Synthesis ===")
    print(f"Total candidates: {report['n_total_candidates']}")
    print(f"Unique: {report['n_unique_candidates']}, Duplicates: {report['n_duplicates']}")
    print(f"Retained: {report['n_retained']}, Rejected: {report['n_rejected']}, Deferred: {report['n_deferred']}")
    print(f"Overlap with paper MRs: {report['overlap_with_paper_mrs']}")
    print(f"Novel retained: {report['novel_retained_names']}")
    print(f"\nRubric added value: {report['rubric_added_value']['interpretation']}")
    print(f"\nFull report: {OUTDIR / 'expert_baseline_report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
