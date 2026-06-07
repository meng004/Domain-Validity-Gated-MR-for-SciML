"""P2-2: three-LLM independent voting on the LLM-generated candidate MRs.

Reads `research_assets/runs/llm-mr-baseline/llm_candidates.json` (produced by
tools/run_llm_mr_baseline.py) and asks three different LLMs from three
different vendors to vote independently on whether each candidate is a VALID
metamorphic relation for the MeshGraphNets cylinder-flow surrogate. Saves the
raw votes (including each rater's per-candidate justification and the raw API
response) to `research_assets/runs/llm-mr-baseline/llm_votes.json`.

Why these three raters
----------------------
The companion sibling project Minimum-MR-SubSet benchmarked twelve LLMs as MR
triviality raters on a 25-MR gold set (HT25); the production-quality pool is
`gpt-5.5` (balanced), `glm-5.1` (high alignment), and `kimi-k2.6` (skeptic).
This script uses `glm-5.1`, `kimi-k2.6`, and `deepseek-v4-flash` instead:

  - `gpt-5.5` is reserved as the *generator fallback* in
    tools/run_llm_mr_baseline.py, so excluding it from the rater pool avoids a
    self-preference conflict whenever the fallback path fires;
  - `claude-opus-4-8` is the primary generator and is excluded for the same
    reason;
  - the chosen triplet spans three distinct vendors (ZhipuAI, Moonshot,
    DeepSeek) to satisfy vendor-diversity discipline.

Vote labels (deliberately 3-class, mirroring the HT25 protocol):
  - "valid"       : a defensible MR for this SUT
  - "borderline"  : ambiguous; could be made valid with a sharper precondition
                    or tolerance, or applies only to a restricted regime
  - "invalid"     : not a valid MR (no physical/software basis, broken under
                    the SUT's geometry/BC, or trivial in a way that has no
                    discriminative power)

Aggregation guards (recorded in the same JSON):
  - Fleiss kappa over the 3 raters x 3 labels (computed; with the
    small-sample paradox caveat from the HT25 rubric).
  - Raw pointwise agreement and item-unanimous rate.
  - Per-rater distinct-label count: a rater that emits a single label across
    all candidates is flagged as a constant-rater (judgement of zero
    discriminative power) and the per-candidate majority for that rater is
    reported but excluded from the kappa.

Failure handling
----------------
Each rater is attempted with timeout 180s. If a rater fails (parse, timeout,
network), it is dropped from the aggregate and recorded in `rater_failures`;
the script does not silently substitute a different LLM. If fewer than 2
raters survive, the script exits non-zero with `BLOCKED_INSUFFICIENT_RATERS`.

Credentials contract
--------------------
Same as the generator: OPENAI_API_KEY + OPENAI_BASE_URL must be set.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "research_assets/runs/llm-mr-baseline/llm_candidates.json"
DEFAULT_OUT = ROOT / "research_assets/runs/llm-mr-baseline/llm_votes.json"

RATERS = [
    os.environ.get("LLM_RATER_1", "glm-5.1"),
    os.environ.get("LLM_RATER_2", "kimi-k2.6"),
    os.environ.get("LLM_RATER_3", "deepseek-v4-flash"),
]
LABELS = ["valid", "borderline", "invalid"]

VOTE_PROMPT_TEMPLATE = """You are validating proposed metamorphic relations (MRs) for testing a learned
neural-network surrogate. The system under test is a MeshGraphNets-family
graph neural network for incompressible 2D flow past a circular cylinder (no-slip
walls, Poiseuille inflow, Reynolds around 1000, fixed unstructured triangular
mesh per trajectory). The SUT takes the velocity field on the mesh at time t
and predicts the velocity field at time t+1.

You will be given a list of CANDIDATE METAMORPHIC RELATIONS. For each
candidate, return EXACTLY ONE label in {"valid", "borderline", "invalid"} and a
one-sentence justification.

Label definitions:
- "valid": the relation has a defensible physical or software-contract basis
   for this SUT, holds under the stated preconditions, and the tolerance
   rationale is meaningful (says what numerical floor it must dominate, or
   makes a comparable concrete commitment).
- "borderline": ambiguous - the candidate could be made valid with a sharper
   precondition or tolerance, or holds only in a restricted regime.
- "invalid": not a valid MR (no defensible basis, broken under the SUT's
   geometry/BC, trivially holds in a way that has zero discriminative power,
   or the tolerance rationale is unfalsifiable).

Output JSON only, in this exact shape, with one entry per candidate in the
same order as given:

{
  "votes": [
    {"name": "<candidate name>", "vote": "valid|borderline|invalid",
     "justification": "<one sentence, <=200 chars>"},
    ...
  ]
}

Candidates:
CANDIDATES_JSON
"""


def fail_closed(msg: str, code: int = 2) -> int:
    sys.stderr.write(f"BLOCKED_NO_LLM_CREDENTIALS: {msg}\n"
                     "Set OPENAI_API_KEY and OPENAI_BASE_URL and rerun. "
                     "No output written.\n")
    return code


def _post_chat(api_key: str, base_url: str, model: str, prompt: str,
               timeout: int = 180) -> dict:
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "temperature": 0,
        "max_tokens": 4096,
        "messages": [
            {"role": "system",
             "content": "You output JSON only. No prose, no markdown fences."},
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
        content = raw["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"unparseable chat response: {e}") from e
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:].strip()
    return json.loads(content)


def fleiss_kappa(votes: list[dict], raters: list[str]) -> float | None:
    """Fleiss kappa over the (item x label) count matrix.

    Returns None when n < 2 items, all raters agree on everything, or only one
    rater is available (the kappa is undefined in those cases).
    """
    n = len(votes)
    R = len(raters)
    if n < 2 or R < 2:
        return None
    M = []
    for v in votes:
        row = {lab: 0 for lab in LABELS}
        for r in raters:
            lab = v["per_rater"].get(r, {}).get("vote")
            if lab in row:
                row[lab] += 1
        M.append([row[lab] for lab in LABELS])
    p_j = [sum(M[i][j] for i in range(n)) / (n * R) for j in range(len(LABELS))]
    if R == 1:
        return None
    P_i = [(sum(c * c for c in M[i]) - R) / (R * (R - 1)) for i in range(n)]
    P_bar = sum(P_i) / n
    P_e = sum(p * p for p in p_j)
    if abs(1 - P_e) < 1e-12:
        return None
    return (P_bar - P_e) / (1 - P_e)


def pointwise_agreement(votes: list[dict], raters: list[str]) -> tuple[float, float]:
    """(raw agreement: fraction of (item, pair) pairs that agree, item-unanimous rate)."""
    if len(raters) < 2:
        return 0.0, 0.0
    pair_total = pair_agree = 0
    unanimous = 0
    for v in votes:
        labels_here = [v["per_rater"].get(r, {}).get("vote") for r in raters
                       if v["per_rater"].get(r)]
        if len(set(labels_here)) == 1 and labels_here:
            unanimous += 1
        for i in range(len(labels_here)):
            for j in range(i + 1, len(labels_here)):
                pair_total += 1
                if labels_here[i] == labels_here[j]:
                    pair_agree += 1
    return (pair_agree / pair_total if pair_total else 0.0,
            unanimous / len(votes) if votes else 0.0)


def majority(per_rater: dict) -> str:
    counts = {lab: 0 for lab in LABELS}
    for r, info in per_rater.items():
        v = info.get("vote")
        if v in counts:
            counts[v] += 1
    best = max(counts.items(), key=lambda kv: kv[1])
    # Tie among non-zero -> borderline (HT25 fallback convention).
    if list(counts.values()).count(best[1]) > 1 and best[1] > 0:
        return "borderline"
    return best[0]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default=str(DEFAULT_IN))
    p.add_argument("--output", default=str(DEFAULT_OUT))
    args = p.parse_args(argv)

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not base_url:
        return fail_closed(
            f"OPENAI_API_KEY {'unset' if not api_key else 'set'}; "
            f"OPENAI_BASE_URL {'unset' if not base_url else 'set'}.")

    src = Path(args.input)
    if not src.exists():
        sys.stderr.write(
            f"BLOCKED_NO_LLM_CANDIDATES: {src} not found. Run "
            "tools/run_llm_mr_baseline.py first.\n")
        return 3
    doc = json.loads(src.read_text())
    candidates = doc.get("candidates", [])
    if not candidates:
        sys.stderr.write("BLOCKED_NO_CANDIDATES: input has no candidates.\n")
        return 4

    candidates_compact = [{k: c.get(k) for k in
                           ("name", "source_transformation", "expected_relation",
                            "tolerance_rationale", "physical_basis",
                            "preconditions", "boundary_output_compatibility",
                            "expected_admissibility_class")}
                          for c in candidates]
    prompt = VOTE_PROMPT_TEMPLATE.replace(
        "CANDIDATES_JSON",
        json.dumps({"candidates": candidates_compact}, indent=2))

    rater_results: dict[str, dict] = {}
    rater_failures: list[dict] = []
    for model in RATERS:
        try:
            print(f"== rating with {model} ==", flush=True)
            raw = _post_chat(api_key, base_url, model, prompt)
            parsed = _extract_json(raw)
            rv = parsed.get("votes")
            if not isinstance(rv, list) or len(rv) != len(candidates):
                raise RuntimeError(
                    f"expected {len(candidates)} votes, got "
                    f"{len(rv) if isinstance(rv, list) else type(rv).__name__}")
            by_name = {v["name"]: v for v in rv if isinstance(v, dict) and "name" in v}
            rater_results[model] = {"raw_response_for_audit": raw,
                                     "by_name": by_name}
        except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as e:
            rater_failures.append({"model": model, "error": str(e)[:400]})
            print(f"!! {model} failed: {type(e).__name__}: {str(e)[:200]}",
                  flush=True)

    surviving = list(rater_results.keys())
    if len(surviving) < 2:
        sys.stderr.write(
            f"BLOCKED_INSUFFICIENT_RATERS: only {len(surviving)} rater(s) "
            "produced parsable votes; need at least 2.\n")
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(
            {"rater_failures": rater_failures,
             "rater_results_present": surviving}, indent=2))
        return 5

    # Per-candidate consolidated votes.
    votes_consolidated = []
    for c in candidates:
        name = c.get("name")
        per_rater = {}
        for r in surviving:
            v = rater_results[r]["by_name"].get(name)
            if v:
                per_rater[r] = {"vote": v.get("vote"),
                                "justification": v.get("justification", "")}
        votes_consolidated.append({"name": name, "per_rater": per_rater,
                                   "majority": majority(per_rater)})

    # Rater-validity screen: a rater whose entire vote vector is one label has
    # zero discriminative power; we flag it and exclude from kappa/PRA.
    valid_raters = []
    constant_raters = []
    for r in surviving:
        labels_emitted = {v["per_rater"][r]["vote"]
                          for v in votes_consolidated if r in v["per_rater"]}
        labels_emitted.discard(None)
        if len(labels_emitted) <= 1:
            constant_raters.append({"model": r,
                                    "constant_label": next(iter(labels_emitted), None)})
        else:
            valid_raters.append(r)

    if len(valid_raters) >= 2:
        kappa = fleiss_kappa(votes_consolidated, valid_raters)
        pra, unanimous_rate = pointwise_agreement(votes_consolidated, valid_raters)
    else:
        kappa = None
        pra, unanimous_rate = pointwise_agreement(votes_consolidated, surviving)

    out = {
        "record_type": "llm-mr-baseline-votes",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "candidates_input": str(src.relative_to(ROOT)) if ROOT in src.parents else str(src),
        "generator_model": doc.get("model_used"),
        "raters_requested": RATERS,
        "raters_surviving": surviving,
        "rater_failures": rater_failures,
        "constant_raters_excluded_from_kappa": constant_raters,
        "raters_kappa_pool": valid_raters,
        "fleiss_kappa": kappa,
        "raw_pointwise_agreement": pra,
        "item_unanimous_rate": unanimous_rate,
        "n_candidates": len(candidates),
        "label_space": LABELS,
        "per_candidate_votes": votes_consolidated,
        "majority_summary": {lab: sum(1 for v in votes_consolidated
                                      if v["majority"] == lab) for lab in LABELS},
        "honesty_boundary": (
            "Three single-call temperature=0 votes by three vendor-diverse LLMs "
            "(not the generator's vendor) on this paper's specific cylinder-flow "
            "candidates. Small-sample (n_candidates around 8, R=3) Fleiss kappa is "
            "known to suffer paradox under near-unanimity; we therefore also "
            "report raw pointwise agreement and item-unanimous rate, and flag "
            "constant raters explicitly. Not a general LLM-MR-rating benchmark."
        ),
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {args.output}")
    print(f"raters surviving: {len(surviving)}/{len(RATERS)}; "
          f"constant raters: {[r['model'] for r in constant_raters] or 'none'}")
    print(f"majority: {out['majority_summary']}; PRA={pra:.3f}; "
          f"item-unanimous={unanimous_rate:.3f}; "
          f"Fleiss kappa={'n/a' if kappa is None else f'{kappa:.3f}'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
