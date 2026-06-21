"""CAS Tier-2 (中科院大类二区) acceptance-rate matrix across three venues.

Design (per the user's brief):
  * Three candidate Tier-2 SE venues are assessed for THIS paper's acceptance
    prospects: IST, EMSE, JSS (all CAS 计算机科学 大类二区).
  * Only the TWO roles that are simultaneously lowest-scoring and most decisive
    for acceptance are run (grounded in the prior IST gate panels + Tier-1
    panel): the handling Editor / gatekeeper (the persistent major blocker;
    Tier-1 accept 0.28) and the adversarial Reviewer 2 (the only reject;
    accept 0.25). These two roles govern the acceptance decision at the margin.
  * Each (venue, role) cell is reviewed by FOUR distinct models for robustness:
    grok-4 (xAI), gpt-5.5 (OpenAI), claude-opus-4-7 (Anthropic), qwen3-max
    (Alibaba). Matrix = 3 venues x 2 roles x 4 models = 24 reviews.

Every review is calibrated to the SPECIFIC venue's real Tier-2 bar (NOT a
Tier-1/TSE generality bar). The script aggregates a per-venue acceptance
estimate and persists every raw response.

Credentials: OPENAI_API_KEY + OPENAI_BASE_URL (bltcy gateway). Fails closed
without them. A model the gateway does not serve fails soft (recorded, skipped).
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
PAPER = ROOT / "paper" / "ist-submission" / "main.tex"
OUTDIR = ROOT / "research_assets" / "runs" / "tier2-acceptance-matrix"
TOKEN_LADDER = (12000, 24000)

# grok-4.3 is the grok-4-series flagship (the gateway serves no bare "grok-4";
# the alternatives are fast/mini variants). Used here as the requested "grok-4".
MODELS = ["grok-4.3", "gpt-5.5", "claude-opus-4-7", "qwen3-max"]

VENUES = [
    ("IST",
     "Elsevier Information and Software Technology (IST), regular research-paper "
     "track. CAS 中科院 计算机科学 大类二区. Software V&V remit; single-anonymized; "
     "<=15000 words (refs + appendices + 200 words/float count). Values software "
     "verification & validation method/tooling contributions with honest scope."),
    ("EMSE",
     "Springer Empirical Software Engineering (EMSE). CAS 中科院 计算机科学 大类二区. "
     "Values rigorous empirical case studies, methodological transparency, honest "
     "threats-to-validity discussion, and replication packages; a well-bounded "
     "single-domain case study with strong artifacts is within its norms."),
    ("JSS",
     "Elsevier Journal of Systems and Software (JSS). CAS 中科院 计算机科学 大类二区. "
     "Mainstream outlet for SE methods, tools, and systems; values practical "
     "relevance, a clear method, and an adequate evaluation."),
]

ROLES = [
    ("Editor",
     "You are the handling Associate Editor at {venue} who makes the accept / "
     "reject recommendation. Apply THIS venue's REAL acceptance bar."),
    ("Adversary",
     "You are a skeptical Reviewer 2 at {venue} who looks hard for reasons to "
     "reject, but calibrated to THIS venue's bar (NOT a Tier-1/TSE generality "
     "bar). Give the strongest honest case, then your honest accept estimate."),
]

RUBRIC = """Judge this manuscript for ACCEPTANCE AT THIS SPECIFIC VENUE and its
real bar: a CAS 中科院 大类二区 software-engineering journal — a solid mid-tier
venue, NOT a Tier-1 flagship. Do NOT apply a Tier-1 (TSE/TOSEM) significance or
generality bar; a well-executed, honestly-bounded case-study-plus-method paper
can be acceptable here. Calibrate to this venue's typical accepted papers.

Output JSON ONLY, no prose, no fences, EXACTLY:
{
  "accept_probability": <float 0.0-1.0, probability of acceptance at THIS venue
     after a normal revision cycle>,
  "verdict": "accept" | "minor_revision" | "major_revision" | "reject",
  "venue_fit": <int 1-10, topical/scope fit to THIS venue>,
  "top_concerns": ["..."],
  "blocking_gaps": ["..."]
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
    if not isinstance(d.get("accept_probability"), (int, float)) or \
            not (0 <= d["accept_probability"] <= 1):
        raise RuntimeError(f"bad accept_probability: {d.get('accept_probability')!r}")
    if d.get("verdict") not in {"accept", "minor_revision", "major_revision", "reject"}:
        raise RuntimeError(f"bad verdict: {d.get('verdict')!r}")
    v = d.get("venue_fit")
    if not isinstance(v, (int, float)) or not (1 <= v <= 10):
        raise RuntimeError(f"venue_fit out of range: {v!r}")
    return d


def _review(api_key, base_url, model, prompt, failures, tag):
    for mt in TOKEN_LADDER:
        try:
            print(f"== {tag} :: {model} (mt={mt}) ==", flush=True)
            raw = _post(api_key, base_url, model, prompt, mt)
            return _validate(_extract_json(raw)), raw
        except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as e:
            failures.append({"cell": tag, "model": model, "max_tokens": mt,
                             "error": str(e)[:300]})
            print(f"!! {tag}/{model} mt={mt}: {type(e).__name__}: {str(e)[:140]}",
                  flush=True)
    return None, None


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

    failures = []
    matrix = {}          # venue -> role -> model -> review
    raw_store = {}
    for vname, vdesc in VENUES:
        matrix[vname] = {}
        raw_store[vname] = {}
        for rname, rtmpl in ROLES:
            matrix[vname][rname] = {}
            raw_store[vname][rname] = {}
            role_desc = rtmpl.replace("{venue}", vname)
            prompt = (
                f"You are reviewing the following manuscript as a candidate for "
                f"{vname}.\nVENUE: {vdesc}\n\nROLE: {role_desc}\n\n" + RUBRIC +
                "\n\n=== MANUSCRIPT START ===\n" + paper_text + "\n=== MANUSCRIPT END ===\n")
            for model in MODELS:
                tag = f"{vname}/{rname}"
                review, raw = _review(api_key, base_url, model, prompt, failures, tag)
                if review is not None:
                    matrix[vname][rname][model] = review
                    raw_store[vname][rname][model] = raw

    # Aggregate per venue.
    per_venue = {}
    for vname, _ in VENUES:
        all_probs, fits, verdicts, gaps = [], [], {}, []
        per_role = {}
        for rname, _ in ROLES:
            cells = matrix[vname][rname]
            rprobs = [c["accept_probability"] for c in cells.values()]
            per_role[rname] = {
                "n": len(cells),
                "accept_prob_mean": round(sum(rprobs) / len(rprobs), 3) if rprobs else None,
                "by_model": {m: cells[m]["accept_probability"] for m in cells},
            }
            for c in cells.values():
                all_probs.append(c["accept_probability"])
                fits.append(c["venue_fit"])
                verdicts[c["verdict"]] = verdicts.get(c["verdict"], 0) + 1
                gaps.extend(c.get("blocking_gaps", []))
        per_venue[vname] = {
            "n_reviews": len(all_probs),
            "accept_prob_mean": round(sum(all_probs) / len(all_probs), 3) if all_probs else None,
            "accept_prob_range": [min(all_probs), max(all_probs)] if all_probs else None,
            "venue_fit_mean": round(sum(fits) / len(fits), 2) if fits else None,
            "verdict_distribution": verdicts,
            "per_role": per_role,
            "blocking_gaps_collected": gaps,
        }

    ranking = sorted(
        [{"venue": v, **{k: per_venue[v][k] for k in
                         ("accept_prob_mean", "accept_prob_range", "venue_fit_mean",
                          "verdict_distribution", "n_reviews")}}
         for v in per_venue],
        key=lambda x: (x["accept_prob_mean"] or 0), reverse=True)

    report = {
        "record_type": "tier2-acceptance-matrix",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "paper": str(PAPER.relative_to(ROOT)),
        "venues": [v for v, _ in VENUES],
        "roles": [r for r, _ in ROLES],
        "models_requested": MODELS,
        "role_selection_rationale": (
            "Editor = acceptance gatekeeper and persistent major blocker across "
            "prior IST gate panels (Tier-1 accept 0.28). Adversary = lowest-scoring "
            "reviewer and only reject in the Tier-1 panel (accept 0.25). These two "
            "roles govern the acceptance decision at the margin."),
        "per_venue": per_venue,
        "ranking": ranking,
        "best_venue": ranking[0]["venue"] if ranking else None,
        "failures": failures,
        "matrix": matrix,
        "raw_responses": raw_store,
        "honesty_boundary": (
            "Single-call temperature-0 LLM reviews via one gateway, two gatekeeping "
            "roles x four models per venue, calibrated to a Tier-2 bar; an automated "
            "acceptance estimate, NOT human peer review and NOT a prediction of an "
            "actual editorial decision."),
    }
    (outdir / "acceptance_matrix_report.json").write_text(json.dumps(report, indent=2))
    print(f"\nwrote {outdir / 'acceptance_matrix_report.json'}")
    for row in ranking:
        print(f"  {row['venue']:5s} accept={row['accept_prob_mean']} "
              f"range={row['accept_prob_range']} fit={row['venue_fit_mean']} "
              f"verdicts={row['verdict_distribution']} (n={row['n_reviews']})")
    served = sorted({f for v in matrix.values() for r in v.values() for f in r})
    print(f"models served: {served}")
    print(f"failures: {len(failures)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
