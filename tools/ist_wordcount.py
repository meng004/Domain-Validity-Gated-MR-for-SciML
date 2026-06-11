"""Single source of truth for the IST-counted word total of the submission.

IST counts references and appendices toward the total and assigns 200 words to
every figure and every table. This module computes a *conservative* estimate:
it counts all detex'd body text (including table-cell text and captions) and
then adds 200 per float on top. That double-counts table content, so the number
is an over-estimate -- which is the safe side for a hard cap: being under the
cap by this measure means being comfortably under the real IST count.

Usage:
    python tools/ist_wordcount.py
    from tools.ist_wordcount import ist_word_count
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_TEX = ROOT / "paper" / "ist-submission" / "main.tex"
BBL = ROOT / "paper" / "ist-submission" / "main.bbl"

_WORD = re.compile(r"[A-Za-z][A-Za-z0-9'\-]*")
WORDS_PER_FLOAT = 200


def _detex(tex_path: Path) -> str | None:
    if shutil.which("detex") is None:
        return None
    out = subprocess.run(["detex", tex_path.name], cwd=tex_path.parent,
                         capture_output=True, text=True)
    return out.stdout


def _strip_latex(text: str) -> str:
    """Fallback stripper used only when detex is unavailable."""
    text = re.sub(r"(?m)%.*$", "", text)
    text = re.sub(r"\\begin\{(equation|align|tabular|tabularx|longtable)\*?\}.*?"
                  r"\\end\{\1\*?\}", " ", text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", text)
    text = re.sub(r"[{}\\&_^~$]", " ", text)
    return text


def count_floats(tex: str) -> tuple[int, int]:
    n_fig = len(re.findall(r"\\begin\{figure", tex))
    n_tab = len(re.findall(r"\\begin\{(?:table|longtable|tabularx)", tex))
    return n_fig, n_tab


def ist_word_count(main_tex: Path = MAIN_TEX, bbl: Path = BBL) -> dict:
    tex = main_tex.read_text(encoding="utf-8")
    detexed = _detex(main_tex)
    used_detex = detexed is not None
    body_text = detexed if used_detex else _strip_latex(tex)
    body = len(_WORD.findall(body_text))
    bib = len(_WORD.findall(bbl.read_text(encoding="utf-8"))) if bbl.exists() else 0
    n_fig, n_tab = count_floats(tex)
    floats = (n_fig + n_tab) * WORDS_PER_FLOAT
    total = body + bib + floats
    return {
        "total": total, "body": body, "bib": bib,
        "figures": n_fig, "tables": n_tab, "float_words": floats,
        "method": "detex" if used_detex else "builtin-stripper",
    }


if __name__ == "__main__":
    r = ist_word_count()
    print(f"IST-counted total: {r['total']}  "
          f"(body={r['body']} bib={r['bib']} "
          f"figs={r['figures']} tabs={r['tables']} "
          f"floats={r['float_words']}; method={r['method']})")
    print(f"cap=15000 (regular paper, hard); "
          f"headroom={15000 - r['total']}")
