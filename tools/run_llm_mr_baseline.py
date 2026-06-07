"""P2-2: LLM-generated candidate MR baseline (fail-closed, reproducible-by-protocol).

What this does
--------------
Asks an LLM (default `claude-opus-4-8` via the bltcy OpenAI-compatible gateway,
with `gpt-5.5` fallback) to propose K=8 candidate metamorphic relations for the
MeshGraphNets 2D incompressible cylinder-flow surrogate this paper studies.
Saves the raw JSON to `research_assets/runs/llm-mr-baseline/llm_candidates.json`.
The companion script `tools/score_llm_mr_baseline.py` then grades each candidate
against this paper's four-condition admissibility predicate (physical/software
basis, transformation preconditions, boundary + output-mapping compatibility,
numerical decidability) and reports overlap with the three MRs the paper already
identifies (node-permutation equivariance, mirror-y reflection, discrete
divergence-free conservation).

Honest scope (recorded in the ledger):
- ONE LLM family at a time (primary or fallback), ONE temperature=0 sample, ONE
  prompt. This is a *single-LLM single-sample* baseline, not a generative model
  benchmark.
- The grading is by this paper's predicate, not by an independent rater panel,
  so the result is "what survives this paper's admissibility gate" - which is
  the comparison the paper actually claims is missing.

Credentials contract
--------------------
This script reads exactly these environment variables:
  OPENAI_API_KEY        (required)  bltcy or OpenAI-compatible bearer key
  OPENAI_BASE_URL       (required)  e.g. https://api.bltcy.ai/v1
  LLM_PRIMARY_MODEL     (optional, default claude-opus-4-8)
  LLM_FALLBACK_MODEL    (optional, default gpt-5.5)
If any required env var is missing, the script fails closed with
`BLOCKED_NO_LLM_CREDENTIALS` so the protocol is preserved as a commitment but no
fabricated output is written. This matches the repo's "fail-closed evidence
gate" discipline (tools/validate_experiment_protocol.py).

Reproducibility
---------------
- temperature=0
- explicit model_id pinned (and recorded with the output)
- prompt is committed verbatim below (`MR_PROPOSAL_PROMPT`)
- raw API response is committed alongside the parsed candidates for audit
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets" / "runs" / "llm-mr-baseline"

PRIMARY = os.environ.get("LLM_PRIMARY_MODEL", "claude-opus-4-8")
FALLBACK = os.environ.get("LLM_FALLBACK_MODEL", "gpt-5.5")

# Committed verbatim so the prompt is part of the audit trail.
MR_PROPOSAL_PROMPT = """You are proposing metamorphic relations (MRs) for testing a learned
neural-network surrogate of a physical simulator. The system under test is a
MeshGraphNets-family graph neural network that takes a velocity field on an
unstructured 2D triangular mesh at time t (incompressible Newtonian flow past a
circular cylinder, Reynolds number around 1000, no-slip walls and a Poiseuille
inflow) and predicts the velocity field at time t+1. The mesh is fixed across
the trajectory.

Propose EXACTLY 8 candidate MRs that one could execute against this surrogate.
For each candidate, output the following fields (JSON):

  - "name": short identifier
  - "source_transformation": how you build the follow-up input from the source
  - "expected_relation": the equality / inequality the SUT output should satisfy
  - "tolerance_rationale": how a verdict tolerance should be set, including any
     numerical floor that the tolerance must dominate (do NOT propose
     "tolerance = epsilon" without saying what epsilon depends on)
  - "physical_basis": the conservation law, symmetry, BC, or contract it rests
     on (or "software_contract" if the basis is implementation, not physics)
  - "preconditions": the conditions the source case must satisfy for the
     relation to be admissible (geometry, BC, initial state, numerical regime)
  - "boundary_output_compatibility": whether the transformation preserves the
     BC structure and whether the SUT output mapping commutes with it
  - "expected_admissibility_class": one of "exact", "approximate_OOD_stress",
     "diagnostic_only" — your best guess before any execution

Output JSON only, in this exact shape, no surrounding prose:

{
  "candidates": [
    { "name": "...", "source_transformation": "...", ... },
    ... (8 total)
  ]
}

Do not cite or copy from any specific paper. Reason from first principles
about the cylinder-flow problem and from standard metamorphic-testing practice.
"""


def fail_closed(msg: str) -> int:
    sys.stderr.write(f"BLOCKED_NO_LLM_CREDENTIALS: {msg}\n")
    sys.stderr.write(
        "Set OPENAI_API_KEY and OPENAI_BASE_URL (e.g. https://api.bltcy.ai/v1) "
        "and rerun. No output written.\n")
    return 2


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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outdir", default=str(OUTDIR))
    args = p.parse_args(argv)

    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not base_url:
        return fail_closed(
            f"OPENAI_API_KEY {'unset' if not api_key else 'set'}; "
            f"OPENAI_BASE_URL {'unset' if not base_url else 'set'}.")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    log = []
    candidates = None
    raw_for_audit = None
    used_model = None
    for model in [PRIMARY, FALLBACK]:
        try:
            print(f"== calling {model} via {base_url} ==", flush=True)
            raw = _post_chat(api_key, base_url, model, MR_PROPOSAL_PROMPT)
            parsed = _extract_json(raw)
            cs = parsed.get("candidates")
            if not isinstance(cs, list) or len(cs) != 8:
                raise RuntimeError(
                    f"expected 8 candidates, got "
                    f"{len(cs) if isinstance(cs, list) else type(cs).__name__}")
            candidates = cs
            raw_for_audit = raw
            used_model = model
            break
        except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as e:
            log.append({"model": model, "error": str(e)[:400]})
            print(f"!! {model} failed: {type(e).__name__}: {str(e)[:200]}",
                  flush=True)

    if candidates is None:
        (outdir / "llm_call_failures.json").write_text(
            json.dumps({"attempts": log}, indent=2), encoding="utf-8")
        sys.stderr.write(
            "BLOCKED_LLM_PROVIDER_FAILURES: both primary and fallback failed; "
            "see llm_call_failures.json. No candidates written.\n")
        return 3

    prompt_sha = hashlib.sha256(MR_PROPOSAL_PROMPT.encode()).hexdigest()
    out = {
        "record_type": "llm-mr-baseline-candidates",
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "gateway_base_url": base_url,
        "model_used": used_model,
        "primary_model": PRIMARY,
        "fallback_model": FALLBACK,
        "temperature": 0,
        "prompt_sha256": prompt_sha,
        "prompt": MR_PROPOSAL_PROMPT,
        "candidates": candidates,
        "raw_response_for_audit": raw_for_audit,
        "fallback_log": log,
        "honesty_boundary": (
            "One LLM call (primary or fallback), one temperature=0 sample, "
            "one prompt. Not a generative-model benchmark; the grade in the "
            "companion scorer is by this paper's own admissibility predicate, "
            "not by an independent rater panel."
        ),
    }
    (outdir / "llm_candidates.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {outdir / 'llm_candidates.json'} "
          f"(model={used_model}, n_candidates={len(candidates)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
