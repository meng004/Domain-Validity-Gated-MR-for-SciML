#!/usr/bin/env python3
"""Pre-submission checks for JSS/Elsevier LaTeX packages."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _strip_latex_commands(text: str) -> str:
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", " ", text)
    return text


def _word_count(text: str) -> int:
    cleaned = _strip_latex_commands(text)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", cleaned))


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: precheck_jss.py <main.tex>", file=sys.stderr)
        return 2

    tex_path = Path(sys.argv[1])
    content = tex_path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    if "elsarticle" not in content and "cas-" not in content:
        errors.append("document class should be an Elsevier elsarticle/CAS class")
    if "Journal of Systems and Software" not in content:
        errors.append("journal metadata is not Journal of Systems and Software")

    if "elsarticle" in content:
        if "authoryear" not in content:
            errors.append("JSS reference style is author-year; use the elsarticle authoryear option")
        if r"\bibliographystyle{elsarticle-harv}" not in content:
            errors.append("bibliographystyle should be elsarticle-harv for JSS author-year references")

    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", content, re.DOTALL)
    if not abstract:
        errors.append("missing abstract")
    else:
        body = abstract.group(1)
        words = _word_count(body)
        if words > 250:
            errors.append(f"abstract exceeds 250 words: {words}")
        if re.search(r"\\(?:cite|ref|cref|autoref)\b", body):
            errors.append("abstract contains citation/reference commands")

    keywords = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", content, re.DOTALL)
    if not keywords:
        errors.append("missing keyword environment")
    else:
        items = [x.strip() for x in re.split(r"\\sep", keywords.group(1)) if x.strip()]
        if not 1 <= len(items) <= 7:
            errors.append(f"keyword count must be 1-7, found {len(items)}")

    highlights = re.search(r"\\begin\{highlights\}(.*?)\\end\{highlights\}", content, re.DOTALL)
    if highlights:
        items = [
            re.sub(r"^\\item\s*", "", line.strip())
            for line in highlights.group(1).splitlines()
            if line.strip().startswith(r"\item")
        ]
        if not 3 <= len(items) <= 5:
            errors.append(f"highlight count must be 3-5, found {len(items)}")
        for idx, item in enumerate(items, 1):
            if len(item) > 85:
                errors.append(f"highlight {idx} exceeds 85 characters: {len(item)}")
    else:
        warnings.append("no highlights environment in main.tex; ensure separate editable highlights file exists")

    for label, pattern in [
        ("CRediT", r"CRediT"),
        ("competing interest", r"competing interest"),
        ("funding or acknowledgments", r"Funding|Acknowledg"),
        ("generative-AI declaration", r"generative AI"),
        ("data availability", r"Data availability"),
    ]:
        if not re.search(pattern, content, re.IGNORECASE):
            errors.append(f"missing required statement: {label}")

    if "author biography" in content.lower() or "author biographies" in content.lower():
        errors.append("JSS Vitae should be a separate editable file, not in main.tex")

    if re.search(r"\\includegraphics(?:\[[^\]]*\])?\{[^}]*[/\\][^}]+\}", content):
        warnings.append("main.tex references graphics in subfolders; flatten paths for Editorial Manager source zip if required")

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("JSS precheck failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("JSS precheck passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
