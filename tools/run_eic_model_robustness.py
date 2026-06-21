"""EIC-role model-bias probe.

Across all five IST panels the EIC role was fixed to gpt-5.5 and returned
major every time. This script isolates whether that verdict is a property of
the manuscript or of the gpt-5.5 grader: it runs the IDENTICAL EIC persona and
IST rubric (imported from run_academic_review_panel) on the current main.tex
across four vendors -- gpt-5.5, grok-4.3, claude-opus-4-7, qwen3-max -- and
reports each model's verdict and accept probability. If non-gpt models flip to
minor on the same text+role, the persistent EIC-major is substantially a
gpt-5.5 calibration artifact rather than a paper signal.

Credentials: OPENAI_API_KEY + OPENAI_BASE_URL (bltcy). Fails closed without.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from run_academic_review_panel import (  # noqa: E402
    PANEL, RUBRIC, PAPER, TOKEN_LADDER, _post, _extract_json, _validate)

EIC_ROLE_DESC = PANEL[0][2]  # the exact EIC persona used in the IST panels
MODELS = ["gpt-5.5", "grok-4.3", "claude-opus-4-7", "qwen3-max"]
OUTDIR = ROOT / "research_assets" / "runs" / "eic-model-robustness"


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not base_url:
        sys.stderr.write("BLOCKED_NO_LLM_CREDENTIALS\n")
        return 2
    outdir = Path(sys.argv[sys.argv.index("--outdir") + 1]) if "--outdir" in sys.argv else OUTDIR
    outdir.mkdir(parents=True, exist_ok=True)

    paper_text = PAPER.read_text(encoding="utf-8")
    prompt = (
        "You are reviewing the following manuscript submitted to Elsevier "
        "Information and Software Technology (IST), regular research-paper track "
        "(<=15000 words, software V&V remit, single-anonymized).\n\n"
        "ROLE: " + EIC_ROLE_DESC + "\n\n" + RUBRIC +
        "\n\n=== MANUSCRIPT START ===\n" + paper_text + "\n=== MANUSCRIPT END ===\n")

    results, failures = {}, []
    for model in MODELS:
        ok = False
        for mt in TOKEN_LADDER:
            try:
                print(f"== EIC :: {model} (mt={mt}) ==", flush=True)
                raw = _post(api_key, base_url, model, prompt, mt)
                results[model] = _validate(_extract_json(raw))
                ok = True
                break
            except Exception as e:  # noqa: BLE001 - record any gateway/parse error
                failures.append({"model": model, "mt": mt, "error": str(e)[:200]})
                print(f"!! {model} mt={mt}: {type(e).__name__}: {str(e)[:120]}", flush=True)
        if not ok:
            print(f"!! {model}: all attempts failed", flush=True)

    report = {
        "record_type": "eic-model-robustness",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "role": "EIC (IST persona, identical across models)",
        "paper": str(PAPER.relative_to(ROOT)),
        "models": MODELS,
        "per_model": {m: {"verdict": r["verdict"],
                          "accept_probability": r["accept_probability"],
                          "scores": r["scores"],
                          "top_concerns": r.get("top_concerns", [])}
                      for m, r in results.items()},
        "failures": failures,
    }
    (outdir / "eic_model_robustness_report.json").write_text(json.dumps(report, indent=2))
    print(f"\nwrote {outdir / 'eic_model_robustness_report.json'}")
    for m, r in results.items():
        print(f"  {m:18s} {r['verdict']:15s} accept={r['accept_probability']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
