"""CAS Tier-1 (中科院大类一区) submission-maturity panel.

Design split (per the user's brief):
  * DESIGNER  — the reviewer personas and the quantitative maturity rubric below
    are authored to the bar of a CAS Tier-1 software-engineering journal
    (IEEE TSE / ACM TOSEM caliber), deliberately stricter than the mid-tier
    (CAS Tier-2, e.g. IST) panel in tools/run_academic_review_panel.py.
  * EXECUTOR  — five vendor-diverse gateway models play the designed roles and
    return quantitative maturity scores. This script is only the executor;
    it does not itself judge the paper.

Five reviewer roles / five distinct vendors:

  AE_Tier1            gpt-5.5            (OpenAI)        gatekeeper, Tier-1 bar
  EmpiricalMethod     claude-opus-4-7    (Anthropic)     design / stats / threats
  SciMLDomain         glm-5.2            (ZhipuAI)       MR / admissibility depth
  NoveltyPositioning  deepseek-v4-pro    (DeepSeek)      novelty vs MT/oracle prior
  Adversary           qwen3-max          (Alibaba)       over-claim / reject hunter

Each reviewer scores seven Tier-1-tuned dimensions (1-10), an accept
probability, a verdict, a 0-100 maturity index toward Tier-1 readiness, a
tier1_ready boolean, the blocking gaps, and the single highest-ROI fix. The
script aggregates a panel maturity index and persists every raw response.

Credentials: OPENAI_API_KEY + OPENAI_BASE_URL (bltcy gateway). Fails closed
without them.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Review exactly what is submitted: the LaTeX source is the single source of truth.
PAPER = ROOT / "manuscript" / "main.tex"
OUTDIR = ROOT / "research_assets" / "runs" / "tier1-maturity-panel"
# Escalating ladder + a 3rd rung; glm-5.2 has emitted empty content on long inputs.
TOKEN_LADDER = (16000, 28000, 40000)

PANEL = [
    ("AE_Tier1", "gpt-5.5",
     "You are an Associate Editor at a CAS Tier-1 (中科院大类一区) software-"
     "engineering journal of IEEE TSE / ACM TOSEM caliber. Apply the Tier-1 "
     "bar explicitly: a Tier-1 paper must make a contribution that is not only "
     "correct and well-executed but also SIGNIFICANT and GENERAL enough to "
     "matter broadly to software V&V, with a single clearly delineated, non-"
     "incremental core idea. Judge whether this manuscript clears that bar, "
     "not merely whether it is publishable somewhere."),
    ("EmpiricalMethod", "claude-opus-4-7",
     "You are an empirical software-engineering methodologist of EMSE / ESEM "
     "caliber. Scrutinise experimental design, statistics, independence of "
     "evidence cells, threats to validity, and crucially whether the evidence "
     "base is broad and independent enough to license the GENERAL claims a "
     "Tier-1 paper makes. Underpowered or non-independent cells must be "
     "called out."),
    ("SciMLDomain", "glm-5.2",
     "You are a SciML and scientific-software-testing domain expert. Judge "
     "whether the metamorphic relations, the domain-validity admissibility "
     "predicate, the numerical measurement-floor reasoning, and the cross-"
     "architecture / cross-PDE evidence are technically deep and convincing "
     "enough for a Tier-1 venue, not merely sound."),
    ("NoveltyPositioning", "deepseek-v4-pro",
     "You are a software-testing-theory reviewer expert in metamorphic testing, "
     "the oracle problem, pseudo/relaxed oracles, and ML testing. Judge novelty "
     "and positioning ruthlessly: is the core idea (gating MR admissibility on "
     "numerical decidability) genuinely new and significant relative to MT "
     "constraint work, relaxed-oracle work, and SciML diagnostics, or is it "
     "incremental? Tier-1 requires the former."),
    ("Adversary", "qwen3-max",
     "You are an adversarial Reviewer 2 who defaults to rejection. Hunt for "
     "over-claims, unsupported generalisations, over-extension that dilutes the "
     "central contribution, descriptive/non-independent empirical cells, "
     "fragile statistics, and reproducibility gaps. Give the strongest honest "
     "case against Tier-1 acceptance."),
]

DIMENSIONS = [
    "novelty_significance",
    "technical_soundness",
    "empirical_rigor",
    "generalizability",
    "positioning_related_work",
    "reproducibility",
    "writing_clarity",
]

RUBRIC = """Score each dimension on an integer 1-10 scale CALIBRATED TO A CAS
Tier-1 (中科院大类一区) software-engineering journal (1 = unacceptable,
5 = borderline for Tier-1, 8 = clearly Tier-1-publishable, 10 = exemplary).
Do NOT calibrate to a mid-tier journal; a paper that would be a clear accept
at a Tier-2 venue may sit at 5-6 here.
  - novelty_significance: is the core idea new AND significant/broad enough for
    Tier-1, with one clearly delineated contribution (not incremental, not
    fragmented across many small studies)?
  - technical_soundness: are the method and its claims internally correct?
  - empirical_rigor: honest scope, CIs, threats, INDEPENDENT (not designed-in)
    evidence cells, adequate power?
  - generalizability: does the evidence license the general claims a Tier-1
    paper makes (multiple architectures / PDEs / fault models, not a single
    setting)? This is the key Tier-1 discriminator.
  - positioning_related_work: is positioning against prior MT / relaxed-oracle /
    SciML-V&V work adequate and is the delta crisp?
  - reproducibility: committed artifacts, ledgers, deterministic re-runs?
  - writing_clarity: focused and well structured, or overloaded/diluted?

Then give:
  - accept_probability: float 0.0-1.0 that it is accepted at a CAS Tier-1 SE
    journal (TSE/TOSEM caliber) after a normal revision cycle.
  - verdict: one of "accept", "minor_revision", "major_revision", "reject".
  - tier1_ready: boolean, true ONLY if it would clear the Tier-1 bar after a
    normal (not heroic) revision.
  - maturity_0_100: integer, your estimate of how close this manuscript is to
    Tier-1 acceptance (0 = far, 100 = ready to accept).
  - blocking_gaps: list of 2-4 short strings, the concrete things that block
    Tier-1 acceptance.
  - highest_roi_fix: ONE short string, the single change with the most impact
    on Tier-1 readiness.
  - top_strengths: list of 1-3 short strings.

Output JSON ONLY, no prose, no fences, in EXACTLY this shape:
{
  "scores": {"novelty_significance": <int>, "technical_soundness": <int>,
             "empirical_rigor": <int>, "generalizability": <int>,
             "positioning_related_work": <int>, "reproducibility": <int>,
             "writing_clarity": <int>},
  "accept_probability": <float>,
  "verdict": "<one of the four>",
  "tier1_ready": <bool>,
  "maturity_0_100": <int>,
  "blocking_gaps": ["..."],
  "highest_roi_fix": "...",
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
    m = d.get("maturity_0_100")
    if not isinstance(m, (int, float)) or not (0 <= m <= 100):
        raise RuntimeError(f"maturity_0_100 out of range: {m!r}")
    if not isinstance(d.get("tier1_ready"), bool):
        raise RuntimeError("missing tier1_ready bool")
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
        "You are reviewing the following manuscript as a candidate for a CAS "
        "Tier-1 (中科院大类一区) software-engineering journal of IEEE TSE / "
        "ACM TOSEM caliber. The paper is a software V&V method paper: a domain-"
        "validity-gated metamorphic-testing workflow for scientific-ML "
        "surrogates evaluated out of distribution.\n\n"
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
            except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as e:
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
    maturities = [r["review"]["maturity_0_100"] for r in results.values()]
    tier1_votes = sum(1 for r in results.values() if r["review"]["tier1_ready"])
    verdict_counts = {}
    for r in results.values():
        v = r["review"]["verdict"]
        verdict_counts[v] = verdict_counts.get(v, 0) + 1
    overall_mean = round(sum(dim_means.values()) / len(dim_means), 2)
    panel_verdict = max(verdict_counts.items(), key=lambda kv: kv[1])[0]

    report = {
        "record_type": "tier1-maturity-panel",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "venue_bar": "CAS Tier-1 (中科院大类一区) SE journal, TSE/TOSEM caliber",
        "paper": str(PAPER.relative_to(ROOT)),
        "panel": [{"role": r, "model": m} for r, m, _ in PANEL],
        "reviewers_succeeded": list(results.keys()),
        "review_failures": failures,
        "per_dimension_mean": dim_means,
        "overall_dimension_mean": overall_mean,
        "accept_probability_mean": round(sum(probs) / len(probs), 3),
        "accept_probability_range": [min(probs), max(probs)],
        "maturity_index_mean": round(sum(maturities) / len(maturities), 1),
        "maturity_index_range": [min(maturities), max(maturities)],
        "tier1_ready_votes": f"{tier1_votes}/{len(results)}",
        "verdict_distribution": verdict_counts,
        "panel_majority_verdict": panel_verdict,
        "blocking_gaps_by_reviewer": {
            r: d["review"].get("blocking_gaps", []) for r, d in results.items()},
        "highest_roi_fix_by_reviewer": {
            r: d["review"].get("highest_roi_fix", "") for r, d in results.items()},
        "per_reviewer": {r: {"model": d["model"], "review": d["review"]}
                         for r, d in results.items()},
        "raw_responses": {r: d["raw_response_for_audit"] for r, d in results.items()},
        "honesty_boundary": (
            "Five single-call temperature-0 LLM reviews via one gateway, scored "
            "against a Tier-1 rubric; an automated maturity estimate, NOT human "
            "peer review and NOT a prediction of an actual editorial decision."),
    }
    (outdir / "review_panel_report.json").write_text(json.dumps(report, indent=2))
    print(f"\nwrote {outdir / 'review_panel_report.json'}")
    print(f"reviewers: {len(results)}/{len(PANEL)}")
    print(f"per-dimension mean: {dim_means}")
    print(f"overall mean: {overall_mean}/10")
    print(f"maturity index mean: {report['maturity_index_mean']}/100 "
          f"range {report['maturity_index_range']}")
    print(f"tier1_ready votes: {report['tier1_ready_votes']}")
    print(f"accept_prob mean {report['accept_probability_mean']} "
          f"range {report['accept_probability_range']}")
    print(f"verdicts: {verdict_counts} -> majority {panel_verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
