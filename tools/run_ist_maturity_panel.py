"""IST submission-maturity panel — DESIGNER / EXECUTOR split, ensemble EIC.

  * DESIGNER  — the 5 reviewer personas and the quantitative IST submission-
    maturity rubric below were authored by the `academic-paper-reviewer` skill
    (field_analyst persona-configuration protocol + quality_rubrics 0-100
    decision mapping), calibrated to Elsevier Information and Software
    Technology (IST) regular track (CAS Tier-2 / JCR Q1-Q2, software-V&V remit,
    single-anonymized). The skill does NOT itself score the paper.
  * EXECUTOR  — vendor-diverse gateway models play the designed roles and
    return quantitative maturity scores. This script is only the executor;
    it does not itself judge the paper.

Five reviewer SEATS. Four specialist seats are single-model; the EIC seat is an
ENSEMBLE of three different LLMs whose results are mean-combined into one seat,
because gpt-5.5 is known to carry bias and must not decide the gatekeeper
verdict alone (the other two votes hold it to 1/3 weight):

  EIC (ensemble)      gpt-5.5 + claude-opus-4-7 + grok-4.3   gatekeeper / IST remit
  EmpiricalRigor      claude-opus-4-7    (Anthropic)  design / stats / threats
  SciMLDomain         glm-5.1            (ZhipuAI)    MR / floor / admissibility
  NoveltyPositioning  grok-4.3           (xAI)        novelty vs MT/oracle prior
  DevilsAdvocate      qwen3-max          (Alibaba)    over-claim / reject hunter

(The user wrote "opus 4.7": the gateway alias `opus-4.7` 503s in this group;
the served Anthropic model is `claude-opus-4-7`, used here. opus and grok play
both a specialist seat and an EIC-ensemble vote — distinct system prompts,
independent calls.)

Each reviewer scores seven IST-tuned dimensions (1-10), an accept probability, a
verdict, a 0-100 submission-maturity index, the blocking gaps, and the single
highest-ROI fix. The EIC seat reports the three sub-reviews and their spread so
gpt-5.5's divergence from the non-gpt votes is auditable. The script aggregates a
panel maturity index and persists every raw response.

Credentials: OPENAI_API_KEY + OPENAI_BASE_URL. Fails closed without them.
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Review exactly what is submitted: the LaTeX source is the single source of truth.
PAPER = ROOT / "paper" / "ist-submission" / "main.tex"
OUTDIR = ROOT / "research_assets" / "runs" / "ist-maturity-panel-eic3"
# glm-5.1 / grok are reasoning models that can spend the whole budget on hidden
# reasoning and emit empty content; the ladder gives them headroom.
TOKEN_LADDER = (16000, 28000, 40000)

# EIC gatekeeper ensemble: gpt-5.5 kept but held to 1/3 by two non-gpt votes.
EIC_ENSEMBLE = ["gpt-5.5", "claude-opus-4-7", "grok-4.3"]

# --- DESIGNER output: field-matched IST personas (academic-paper-reviewer) ---
PANEL = [
    ("EIC", EIC_ENSEMBLE,
     "You are the Editor-in-Chief of Elsevier Information and Software "
     "Technology (IST), regular research-paper track. IST's remit is software "
     "engineering, in particular software verification & validation. Judge "
     "journal fit, significance, and whether this contribution clears the bar "
     "for an IST regular paper (a sound, useful V&V method with credible "
     "evidence) — NOT whether it would clear a Tier-1 (TSE/TOSEM) bar. You are "
     "uniquely responsible for catching: scope mismatch to IST's V&V remit, an "
     "over-claimed central contribution, and a contribution that is really a "
     "SciML result rather than a software-V&V method. Do not go deep into "
     "numerics or statistics — that is the specialist reviewers' job."),
    ("EmpiricalRigor", "claude-opus-4-7",
     "You are an empirical software-engineering methodologist of EMSE / ESEM "
     "caliber. You are uniquely responsible for catching experimental-design "
     "and statistics defects: underpowered or wide-CI cells (e.g. n=3/5/6 with "
     "Wilson intervals), evidence cells that are designed-in rather than "
     "independent, seeded-fault catalog validity, descriptive vs inferential "
     "rates presented as if independent, claim-to-evidence mismatch, threats to "
     "validity, and reproducibility (committed ledgers, DOI, deterministic "
     "re-runs). Call out any claim the evidence does not license."),
    ("SciMLDomain", "glm-5.1",
     "You are a scientific-ML and scientific-software-testing domain expert "
     "with a numerical-methods background. You are uniquely responsible for "
     "catching domain/numerics defects: whether the metamorphic relations "
     "(mirror-y equivariance, node-permutation equivariance, discrete-"
     "divergence boundedness) are numerically correct; whether the domain-"
     "validity admissibility predicate actually holds; whether the measurement-"
     "/operator-floor reasoning (O(h) truncation, the analytic Hessian bound) "
     "is right; and whether the MeshGraphNet / FNO / PINN evidence is "
     "physically plausible. Judge technical depth for a domain venue, not mere "
     "soundness."),
    ("NoveltyPositioning", "grok-4.3",
     "You are a software-testing-theory reviewer expert in metamorphic testing, "
     "the oracle problem, pseudo/relaxed oracles, and ML testing. You are "
     "uniquely responsible for catching novelty and positioning defects: is the "
     "core idea (gating MR admissibility on numerical decidability / domain "
     "validity, and the validity-coverage duality) genuinely new relative to MT "
     "constraint work, relaxed-oracle work, SciML diagnostics, and the "
     "Kanewala scientific-software-MT cluster, or is it an incremental "
     "recombination? Is the closest prior work cited and is the delta crisp? "
     "Flag any tautological framing (detector measures what it is built to "
     "catch) and any missing closest-prior reference."),
    ("DevilsAdvocate", "qwen3-max",
     "You are an adversarial Reviewer 2 who defaults to rejection. Give the "
     "strongest honest case against IST acceptance. You are uniquely "
     "responsible for catching what the other four reviewers soft-pedal: "
     "over-claims, unsupported generalisations, over-extension that dilutes the "
     "central validity-coverage contribution, descriptive/non-independent "
     "empirical cells, fragile statistics, reproducibility gaps, and the "
     "'so what?' test. Do not be charitable."),
]

DIMENSIONS = [
    "novelty_contribution",
    "technical_soundness",
    "empirical_rigor",
    "related_work_positioning",
    "clarity_writing",
    "reproducibility",
    "scope_fit_ist",
]

VERDICTS = ("accept", "minor_revision", "major_revision", "reject")
SEVERITY = {"accept": 0, "minor_revision": 1, "major_revision": 2, "reject": 3}

# --- DESIGNER output: quantitative IST submission-maturity rubric ---
RUBRIC = """Score each dimension on an integer 1-10 scale CALIBRATED TO IST, a
CAS Tier-2 / JCR Q1-Q2 software-engineering journal (1 = unacceptable,
5 = borderline for IST, 8 = clearly IST-publishable, 10 = exemplary). Calibrate
to IST, NOT to a Tier-1 venue (TSE/TOSEM): a solid, well-scoped, honestly
bounded V&V method paper can score 8 here even if it is incremental.
  - novelty_contribution: is the contribution new and non-trivial for IST?
  - technical_soundness: are the method and its claims internally correct?
  - empirical_rigor: honest scope, CIs, threats, evidence that licenses the
    claims; underpowered or non-independent cells must be penalised.
  - related_work_positioning: is positioning against prior MT / relaxed-oracle /
    SciML-V&V work adequate and is the delta crisp?
  - clarity_writing: focused and well structured, or overloaded/diluted?
  - reproducibility: committed artifacts, ledgers, DOI, deterministic re-runs?
  - scope_fit_ist: does it fit IST's software-V&V remit?

Then give:
  - accept_probability: float 0.0-1.0 that it is accepted at IST regular track
    after a normal revision cycle.
  - verdict: one of "accept", "minor_revision", "major_revision", "reject".
  - submission_maturity_0_100: integer, how close this manuscript is to IST
    acceptance (0 = far from submittable, 50 = major-revision territory,
    65 = minor-revision territory, 80 = accept-ready, 100 = exemplary accept).
  - blocking_gaps: list of 2-4 short strings, the concrete things that most
    hold this manuscript back from IST acceptance.
  - highest_roi_fix: ONE short string, the single change with the most impact on
    IST submission maturity per unit of author effort.
  - top_strengths: list of 1-3 short strings.

Output JSON ONLY, no prose, no fences, in EXACTLY this shape:
{
  "scores": {"novelty_contribution": <int>, "technical_soundness": <int>,
             "empirical_rigor": <int>, "related_work_positioning": <int>,
             "clarity_writing": <int>, "reproducibility": <int>,
             "scope_fit_ist": <int>},
  "accept_probability": <float>,
  "verdict": "<one of the four>",
  "submission_maturity_0_100": <int>,
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
    if d.get("verdict") not in set(VERDICTS):
        raise RuntimeError(f"bad verdict: {d.get('verdict')!r}")
    if not isinstance(d.get("accept_probability"), (int, float)):
        raise RuntimeError("missing accept_probability")
    m = d.get("submission_maturity_0_100")
    if not isinstance(m, (int, float)) or not (0 <= m <= 100):
        raise RuntimeError(f"submission_maturity_0_100 out of range: {m!r}")
    return d


def _review_one(api_key, base_url, model, prompt, label, failures):
    """Token-ladder a single model review; return (parsed, raw) or (None, None)."""
    for mt in TOKEN_LADDER:
        try:
            print(f"== {label} :: {model} (max_tokens={mt}) ==", flush=True)
            raw = _post(api_key, base_url, model, prompt, mt)
            return _validate(_extract_json(raw)), raw
        except (urllib.error.URLError, OSError, http.client.HTTPException,
                RuntimeError, json.JSONDecodeError) as e:
            failures.append({"label": label, "model": model, "max_tokens": mt,
                             "error": str(e)[:300]})
            print(f"!! {label}/{model} mt={mt}: {type(e).__name__}: {str(e)[:160]}",
                  flush=True)
    return None, None


def _combine_verdict(verdicts):
    """Modal verdict; ties broken toward the more conservative (higher severity)."""
    c = Counter(verdicts)
    top = max(c.values())
    cands = [v for v, n in c.items() if n == top]
    return max(cands, key=lambda v: SEVERITY[v])


def _combine_ensemble(sub_reviews):
    """Mean-combine N sub-reviews into one seat-level review."""
    revs = list(sub_reviews.values())
    n = len(revs)
    scores = {dim: round(sum(r["scores"][dim] for r in revs) / n, 2)
              for dim in DIMENSIONS}
    gaps, fixes, strengths = [], [], []
    for m, r in sub_reviews.items():
        for g in r.get("blocking_gaps", []):
            gaps.append(f"[{m}] {g}")
        fixes.append(f"[{m}] {r.get('highest_roi_fix', '')}")
        for s in r.get("top_strengths", []):
            strengths.append(f"[{m}] {s}")
    return {
        "scores": scores,
        "accept_probability": round(sum(r["accept_probability"] for r in revs) / n, 3),
        "verdict": _combine_verdict([r["verdict"] for r in revs]),
        "submission_maturity_0_100": round(sum(r["submission_maturity_0_100"]
                                               for r in revs) / n, 1),
        "blocking_gaps": gaps,
        "highest_roi_fix": fixes,
        "top_strengths": strengths,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(OUTDIR))
    args = ap.parse_args(argv)
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not base_url:
        return fail_closed("set OPENAI_API_KEY and OPENAI_BASE_URL.")

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    paper_text = PAPER.read_text(encoding="utf-8")
    base_prompt = (
        "You are reviewing the following manuscript submitted to Elsevier "
        "Information and Software Technology (IST), regular research-paper track "
        "(<=15000 words, software-V&V remit, single-anonymized). The paper is a "
        "software V&V method paper: a domain-validity-gated metamorphic-testing "
        "workflow for scientific-ML surrogates evaluated out of distribution.\n\n"
        "ROLE: {role_desc}\n\n" + RUBRIC +
        "\n\n=== MANUSCRIPT START ===\n" + paper_text + "\n=== MANUSCRIPT END ===\n")

    results = {}
    failures = []
    eic_detail = None
    for role, model_spec, role_desc in PANEL:
        prompt = base_prompt.replace("{role_desc}", role_desc)
        if isinstance(model_spec, (list, tuple)):
            subs, raws = {}, {}
            for m in model_spec:
                parsed, raw = _review_one(api_key, base_url, m, prompt, role, failures)
                if parsed is not None:
                    subs[m] = parsed
                    raws[m] = raw
            if not subs:
                print(f"!! {role}: all ensemble members failed", flush=True)
                continue
            combined = _combine_ensemble(subs)
            results[role] = {"model": " + ".join(model_spec), "ensemble": True,
                             "review": combined, "raw_response_for_audit": raws}
            eic_detail = {
                "members": list(model_spec),
                "succeeded": list(subs.keys()),
                "per_member": {m: subs[m] for m in subs},
                "per_member_verdict": {m: subs[m]["verdict"] for m in subs},
                "per_member_maturity": {m: subs[m]["submission_maturity_0_100"]
                                        for m in subs},
                "per_member_accept_prob": {m: subs[m]["accept_probability"]
                                           for m in subs},
                "combined_verdict": combined["verdict"],
                "combined_maturity": combined["submission_maturity_0_100"],
            }
        else:
            parsed, raw = _review_one(api_key, base_url, model_spec, prompt, role,
                                      failures)
            if parsed is not None:
                results[role] = {"model": model_spec, "ensemble": False,
                                 "review": parsed, "raw_response_for_audit": raw}
            else:
                print(f"!! {role}: all attempts failed", flush=True)

    if len(results) < 2:
        sys.stderr.write(f"BLOCKED_INSUFFICIENT_REVIEWERS: only {len(results)}.\n")
        (outdir / "review_failures.json").write_text(json.dumps(failures, indent=2))
        return 5

    # Aggregate (each seat = one vote; EIC seat value is its 3-model mean).
    dim_means = {}
    for dim in DIMENSIONS:
        vals = [r["review"]["scores"][dim] for r in results.values()]
        dim_means[dim] = round(sum(vals) / len(vals), 2)
    probs = [r["review"]["accept_probability"] for r in results.values()]
    maturities = [r["review"]["submission_maturity_0_100"] for r in results.values()]
    verdict_counts = {}
    for r in results.values():
        v = r["review"]["verdict"]
        verdict_counts[v] = verdict_counts.get(v, 0) + 1
    overall_mean = round(sum(dim_means.values()) / len(dim_means), 2)
    panel_verdict = max(verdict_counts.items(), key=lambda kv: kv[1])[0]

    report = {
        "record_type": "ist-maturity-panel-eic3",
        "schema_version": "0.2.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "venue": "Elsevier IST regular track (CAS Tier-2 / JCR Q1-Q2)",
        "designer": "academic-paper-reviewer skill (field_analyst + quality_rubrics)",
        "executor": ("vendor-diverse gateway models, temperature 0; EIC seat is a "
                     "3-model mean ensemble (gpt-5.5 + claude-opus-4-7 + grok-4.3) "
                     "to dilute gpt-5.5 bias to 1/3"),
        "paper": str(PAPER.relative_to(ROOT)),
        "panel": [{"role": r, "model": (m if isinstance(m, str) else " + ".join(m)),
                   "ensemble": not isinstance(m, str)} for r, m, _ in PANEL],
        "reviewers_succeeded": list(results.keys()),
        "review_failures": failures,
        "eic_ensemble": eic_detail,
        "per_dimension_mean": dim_means,
        "overall_dimension_mean": overall_mean,
        "accept_probability_mean": round(sum(probs) / len(probs), 3),
        "accept_probability_range": [min(probs), max(probs)],
        "maturity_index_mean": round(sum(maturities) / len(maturities), 1),
        "maturity_index_range": [min(maturities), max(maturities)],
        "verdict_distribution": verdict_counts,
        "panel_majority_verdict": panel_verdict,
        "blocking_gaps_by_reviewer": {
            r: d["review"].get("blocking_gaps", []) for r, d in results.items()},
        "highest_roi_fix_by_reviewer": {
            r: d["review"].get("highest_roi_fix", "") for r, d in results.items()},
        "per_reviewer": {r: {"model": d["model"], "ensemble": d.get("ensemble", False),
                             "review": d["review"]} for r, d in results.items()},
        "raw_responses": {r: d["raw_response_for_audit"] for r, d in results.items()},
        "honesty_boundary": (
            "Single-call temperature-0 LLM reviews via one gateway, scored against "
            "an IST submission-maturity rubric; the EIC seat mean-combines three "
            "models. An automated maturity estimate, NOT human peer review and NOT "
            "a prediction of an actual IST editorial decision."),
    }
    (outdir / "review_panel_report.json").write_text(json.dumps(report, indent=2))
    print(f"\nwrote {outdir / 'review_panel_report.json'}")
    print(f"seats: {len(results)}/{len(PANEL)}")
    if eic_detail:
        print(f"EIC ensemble per-member maturity: {eic_detail['per_member_maturity']}")
        print(f"EIC ensemble per-member verdict:  {eic_detail['per_member_verdict']}")
        print(f"EIC combined -> verdict {eic_detail['combined_verdict']} "
              f"maturity {eic_detail['combined_maturity']}")
    print(f"per-dimension mean: {dim_means}")
    print(f"overall mean: {overall_mean}/10")
    print(f"maturity index mean: {report['maturity_index_mean']}/100 "
          f"range {report['maturity_index_range']}")
    print(f"accept_prob mean {report['accept_probability_mean']} "
          f"range {report['accept_probability_range']}")
    print(f"verdicts: {verdict_counts} -> majority {panel_verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
