"""Patch the expert-MR-baseline: re-rate all candidates with a replacement rater
to fill in for a rate-limited model (e.g. Kimi-K2-Instruct → MiniMax-M3).

Usage:
  API_KEY=... BASE_URL=https://llm-api.net/v1 \
    python3 tools/patch_expert_rater.py \
      --failed-rater "Kimi-K2-Instruct" \
      --replacement-rater "MiniMax-M3"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from run_expert_mr_baseline import (
    RATER_MODELS,
    _gateway_credentials,
    _strict_three_rater_majority,
)

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets" / "runs" / "expert-mr-baseline"

TOKEN_LADDER = (12000, 24000)

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


def _post_chat(api_key, base_url, model, prompt, max_tokens, timeout=360):
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model, "temperature": 0, "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": "You output JSON only. No prose, no markdown fences."},
            {"role": "user", "content": prompt},
        ],
    }).encode()
    req = urllib.request.Request(url, data=body,
        headers={"content-type": "application/json", "authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _extract_json(raw):
    content = raw["choices"][0]["message"]["content"] or ""
    s = re.sub(r"<thinking>.*?</thinking>", "", content, flags=re.S).strip()
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```\s*$", "", s)
    depth = 0
    start = None
    for i, ch in enumerate(s):
        if ch == '{':
            if depth == 0: start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                return json.loads(s[start:i+1])
    raise RuntimeError(f"no JSON in: {s[:200]}")


def _call_with_ladder(api_key, base_url, model, prompt):
    last_err = None
    for budget in TOKEN_LADDER:
        try:
            raw = _post_chat(api_key, base_url, model, prompt, budget)
            return _extract_json(raw), raw
        except Exception as e:
            last_err = e
            time.sleep(5)
    raise RuntimeError(f"all budgets exhausted for {model}: {last_err}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--failed-rater", required=True)
    p.add_argument("--replacement-rater", required=True)
    args = p.parse_args()

    api_key, base_url, api_key_env, base_url_env = _gateway_credentials()
    if not api_key or not base_url:
        sys.exit(
            "Set one API-key env var (OPENAI_API_KEY, API_KEY, or "
            "LLM_GATEWAY_API_KEY) and one base-url env var (OPENAI_BASE_URL, "
            "BASE_URL, or LLM_GATEWAY_BASE_URL)"
        )
    print(f"Gateway credentials: api_key_env={api_key_env}; base_url_env={base_url_env}")

    rated_path = OUTDIR / "expert_rated_candidates.json"
    if not rated_path.exists():
        sys.exit(f"Not found: {rated_path}")
    rated = json.loads(rated_path.read_text())

    print(f"Patching {len(rated)} candidates: {args.failed_rater} -> {args.replacement_rater}")
    patched = 0
    for i, entry in enumerate(rated):
        cand = entry["candidate"]
        votes = entry["per_rater_votes"]
        old_vote = votes.get(args.failed_rater, {})
        if old_vote.get("overall_verdict") == "error" or "error" in old_vote:
            cand_json = json.dumps(cand, indent=2, ensure_ascii=False)
            prompt = RATER_PROMPT_TEMPLATE.format(candidate_json=cand_json)
            print(f"  [{i+1}/{len(rated)}] {cand.get('name','?')} <- {args.replacement_rater} ...", end=" ", flush=True)
            try:
                parsed, _ = _call_with_ladder(api_key, base_url, args.replacement_rater, prompt)
                votes[args.replacement_rater] = parsed
                print(parsed.get("overall_verdict", "?"))
                patched += 1
            except Exception as e:
                print(f"FAILED: {e}")
                votes[args.replacement_rater] = {"error": str(e), "overall_verdict": "error"}
            time.sleep(1)

            # Recompute the active three-rater vote; inactive historical raters
            # remain in per_rater_votes for audit but do not affect the verdict.
            verdict, distribution, active, note = _strict_three_rater_majority(
                votes, RATER_MODELS)
            entry["majority_verdict"] = verdict
            entry["verdict_distribution"] = distribution
            entry["active_rater_models"] = active
            entry["vote_note"] = note
            overlap_sets = []
            for v in votes.values():
                overlap_sets.extend(v.get("overlaps_paper_mr", []))
            entry["overlaps_paper_mr_union"] = list(set(overlap_sets))

    rated_path.write_text(json.dumps(rated, indent=2, ensure_ascii=False))
    print(f"\nPatched {patched} entries. Rebuilding report...")

    # Rebuild report
    report_path = OUTDIR / "expert_baseline_report.json"
    proposals_path = OUTDIR / "expert_proposals.json"
    proposals = json.loads(proposals_path.read_text()) if proposals_path.exists() else {}

    n_total = len(rated)
    n_unique = len(set(r["candidate"].get("dedup_key", str(i)) for i, r in enumerate(rated)
                       if "duplicate_of_model" not in r["candidate"]))
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

    all_raters = sorted(set().union(*(set(r["per_rater_votes"].keys()) for r in rated)))

    report = {
        "record_type": "expert-mr-baseline-report",
        "schema_version": "0.3.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "protocol": "3-expert-proposal × 3-rater-majority-vote (patched)",
        "expert_models": list(proposals.keys()),
        "rater_models": RATER_MODELS,
        "rater_vote_rule": "exactly 3 successful distinct configured LLM raters; 2-of-3 majority, with deterministic configured-rater-order tie resolution",
        "inactive_audit_trail_raters": [r for r in all_raters if r not in RATER_MODELS],
        "patch_applied": f"{args.failed_rater} -> {args.replacement_rater} ({patched} entries)",
        "n_total_candidates": n_total,
        "n_unique_candidates": n_unique,
        "n_duplicates": n_total - n_unique,
        "verdict_counts": verdict_counts,
        "n_retained": len(retained),
        "n_rejected": len(rejected),
        "n_deferred": len(deferred),
        "overlap_with_paper_mrs": overlap_with_paper,
        "novel_retained_names": novel_retained,
        "rubric_added_value": {
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
        },
        "per_candidate": rated,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Report: {report_path}")
    print(f"Retained: {len(retained)}, Rejected: {len(rejected)}, Deferred: {len(deferred)}")
    print(f"Novel retained: {novel_retained}")


if __name__ == "__main__":
    main()
