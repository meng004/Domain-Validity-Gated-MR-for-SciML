"""Academic review panel: score this manuscript on IST regular-track dimensions
using a vendor-diverse multi-LLM panel via the bltcy OpenAI-compatible gateway.

Five reviewer roles, five distinct models requested for the current
submission-maturity audit:

  EIC               gpt-5.5            (OpenAI)
  MethodologyRigor  claude-opus-4-7    (Anthropic-compatible gateway model)
  DomainExpert      glm-5.2            (ZhipuAI)
  Perspective       deepseek-v4-pro    (DeepSeek)
  DevilsAdvocate    qwen3-max          (Alibaba)

Each reviewer scores seven IST-standard dimensions on 1-10, gives an accept
probability and a verdict (Accept / Minor / Major / Reject), and lists its top
concerns. The script aggregates per-dimension means and a panel verdict, and
persists every raw response for audit.

Credentials: OPENAI_API_KEY + OPENAI_BASE_URL (bltcy gateway).
Fails closed without them. Reasoning models get an escalating max_tokens ladder
(same JSON-extract hardening as the LLM-MR baseline tools).
"""
from __future__ import annotations

import argparse
import json
import http.client
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Canonical submission document is the LaTeX source (single source of truth);
# the panel reviews exactly what is submitted to IST.
PAPER = ROOT / "submissions" / "IST" / "main.tex"
OUTDIR = ROOT / "research_assets" / "runs" / "academic-review-panel"
TOKEN_LADDER = (16000, 28000)

PANEL = [
    ("EIC", "gpt-5.5",
     "You are the Editor-in-Chief of Information and Software Technology (IST). "
     "Judge overall fit, significance, and whether the contribution clears the "
     "bar for a regular research paper at IST."),
    ("MethodologyRigor", "claude-opus-4-7",
     "You are a methodology-focused reviewer. Scrutinise experimental design, "
     "statistics, threats to validity, and whether the claims are matched by the "
     "evidence."),
    ("DomainExpert", "glm-5.2",
     "You are a SciML / scientific-software-testing domain expert. Judge whether "
     "the metamorphic relations, the admissibility predicate, and the PINN/MGN "
     "evidence are technically sound for this domain."),
    ("Perspective", "deepseek-v4-pro",
     "You are a software-engineering-research reviewer focused on novelty, "
     "positioning against related work, and practical relevance."),
    ("DevilsAdvocate", "qwen3-max",
     "You are an adversarial, skeptical reviewer. Hunt for over-claims, "
     "unsupported generalisations, reproducibility gaps, and reasons to reject."),
]

DIMENSIONS = [
    "novelty_contribution",
    "technical_soundness",
    "empirical_rigor",
    "related_work",
    "clarity",
    "reproducibility",
    "scope_match_to_ist",
]

RUBRIC = """Score each dimension on an integer 1-10 scale (1 = unacceptable,
5 = borderline, 8 = clearly publishable, 10 = exemplary):
  - novelty_contribution: is the contribution new and non-trivial for IST?
  - technical_soundness: are the method and its claims internally correct?
  - empirical_rigor: are the experiments well-designed, with honest scope, CIs,
    and threats? (This paper deliberately keeps a narrow, within-/cross-family
    evidence boundary; judge rigor, not breadth.)
  - related_work: is positioning against prior MT / SciML-V&V work adequate?
  - clarity: is it well written and well structured?
  - reproducibility: committed artifacts, ledgers, deterministic re-runs?
  - scope_match_to_ist: does it fit IST's software-V&V remit?

Then give:
  - accept_probability: a float 0.0-1.0 (your estimate it is accepted at IST
    regular track after a normal revision cycle).
  - verdict: one of "accept", "minor_revision", "major_revision", "reject".
  - top_concerns: a list of 2-4 short strings.
  - top_strengths: a list of 1-3 short strings.

Output JSON ONLY, no prose, in EXACTLY this shape:
{
  "scores": {"novelty_contribution": <int>, "technical_soundness": <int>,
             "empirical_rigor": <int>, "related_work": <int>, "clarity": <int>,
             "reproducibility": <int>, "scope_match_to_ist": <int>},
  "accept_probability": <float>,
  "verdict": "<one of the four>",
  "top_concerns": ["..."],
  "top_strengths": ["..."]
}
"""


def fail_closed(msg: str) -> int:
    sys.stderr.write("BLOCKED_NO_LLM_CREDENTIALS: " + msg + "\n")
    return 2


def _post(api_key, base_url, model, prompt, max_tokens, timeout=420):
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model, "temperature": 0, "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": "You output JSON only. No prose, no fences."},
            {"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "content-type": "application/json", "authorization": f"Bearer {api_key}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _extract_json(raw: dict) -> dict:
    content = (raw.get("choices", [{}])[0].get("message", {}).get("content") or "")
    finish = raw.get("choices", [{}])[0].get("finish_reason")
    s = re.sub(r"<thinking>.*?</thinking>", "", content, flags=re.S).strip()
    if not s:
        raise RuntimeError(f"empty content (finish_reason={finish!r})")
    fenced = re.search(r"```(?:json)?\s*(.*?)```", s, flags=re.S)
    if fenced:
        s = fenced.group(1).strip()
    o0, o1 = s.find("{"), s.rfind("}")
    if o0 >= 0 and o1 > o0:
        return json.loads(s[o0:o1 + 1])
    raise RuntimeError(f"no JSON object in content[:200]={s[:200]!r}")


def _validate(d: dict) -> dict:
    if not isinstance(d.get("scores"), dict):
        raise RuntimeError("missing scores object")
    for dim in DIMENSIONS:
        v = d["scores"].get(dim)
        if not isinstance(v, (int, float)) or not (1 <= v <= 10):
            raise RuntimeError(f"score for {dim} out of range: {v!r}")
    if d.get("verdict") not in {"accept", "minor_revision", "major_revision", "reject"}:
        raise RuntimeError(f"bad verdict: {d.get('verdict')!r}")
    if not isinstance(d.get("accept_probability"), (int, float)):
        raise RuntimeError("missing accept_probability")
    return d


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(OUTDIR))
    args = ap.parse_args(argv)
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not base_url:
        return fail_closed("set OPENAI_API_KEY and OPENAI_BASE_URL (bltcy).")

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    paper_text = PAPER.read_text(encoding="utf-8")
    base_prompt = (
        "You are reviewing the following manuscript submitted to Elsevier "
        "Information and Software Technology (IST), regular research-paper track "
        "(<=15000 words, software V&V remit, single-anonymized).\n\n"
        "ROLE: {role_desc}\n\n" + RUBRIC +
        "\n\n=== MANUSCRIPT START ===\n" + paper_text + "\n=== MANUSCRIPT END ===\n")

    results = {}
    failures = []
    for role, model, role_desc in PANEL:
        prompt = base_prompt.replace("{role_desc}", role_desc)
        ok = False
        for mt in TOKEN_LADDER:
            try:
                print(f"== {role} :: {model} (max_tokens={mt}) ==", flush=True)
                raw = _post(api_key, base_url, model, prompt, mt)
                parsed = _validate(_extract_json(raw))
                results[role] = {"model": model, "review": parsed,
                                 "raw_response_for_audit": raw}
                ok = True
                break
            except (urllib.error.URLError, OSError, http.client.HTTPException,
                    RuntimeError, json.JSONDecodeError) as e:
                failures.append({"role": role, "model": model, "max_tokens": mt,
                                 "error": str(e)[:300]})
                print(f"!! {role}/{model} mt={mt}: {type(e).__name__}: {str(e)[:160]}",
                      flush=True)
        if not ok:
            print(f"!! {role}: all attempts failed", flush=True)

    if len(results) < 2:
        sys.stderr.write(f"BLOCKED_INSUFFICIENT_REVIEWERS: only {len(results)}.\n")
        (outdir / "review_failures.json").write_text(json.dumps(failures, indent=2))
        return 5

    # Aggregate.
    dim_means = {}
    for dim in DIMENSIONS:
        vals = [r["review"]["scores"][dim] for r in results.values()]
        dim_means[dim] = round(sum(vals) / len(vals), 2)
    probs = [r["review"]["accept_probability"] for r in results.values()]
    verdict_counts = {}
    for r in results.values():
        v = r["review"]["verdict"]
        verdict_counts[v] = verdict_counts.get(v, 0) + 1
    overall_mean = round(sum(dim_means.values()) / len(dim_means), 2)
    panel_verdict = max(verdict_counts.items(), key=lambda kv: kv[1])[0]

    report = {
        "record_type": "academic-review-panel",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "venue": "Elsevier IST regular track",
        "paper": str(PAPER.relative_to(ROOT)),
        "panel": [{"role": r, "model": m} for r, m, _ in PANEL],
        "reviewers_succeeded": list(results.keys()),
        "review_failures": failures,
        "per_dimension_mean": dim_means,
        "overall_dimension_mean": overall_mean,
        "accept_probability_mean": round(sum(probs) / len(probs), 3),
        "accept_probability_range": [min(probs), max(probs)],
        "verdict_distribution": verdict_counts,
        "panel_majority_verdict": panel_verdict,
        "per_reviewer": {r: {"model": d["model"], "review": d["review"]}
                         for r, d in results.items()},
        "raw_responses": {r: d["raw_response_for_audit"] for r, d in results.items()},
        "honesty_boundary": (
            "Five single-call temperature-0 LLM reviews via one gateway; an "
            "automated panel estimate, NOT a substitute for human peer review "
            "and NOT a prediction of an actual IST editorial decision."),
    }
    (outdir / "review_panel_report.json").write_text(json.dumps(report, indent=2))
    print(f"\nwrote {outdir / 'review_panel_report.json'}")
    print(f"reviewers: {len(results)}/{len(PANEL)}")
    print(f"per-dimension mean: {dim_means}")
    print(f"overall mean: {overall_mean}/10 | accept_prob mean "
          f"{report['accept_probability_mean']} range {report['accept_probability_range']}")
    print(f"verdicts: {verdict_counts} -> majority {panel_verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
