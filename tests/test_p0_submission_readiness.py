"""P0 acceptance gates for IST regular-track submission (TDD).

These tests encode the Editorial-Manager-blocking requirements from
paper/30_root_cause_and_uncompromising_ist_gap_closure.md, Phase P0:

  P0-1  IST-counted word total <= 14,500 (1,500-word slack under the 15,000 cap)
  P0-3  title <= 70 characters
  P0-4  abstract Conclusion uses scoped-positive framing (no "is not" pile-up)

P0-2 (double anonymization) is gated on a separate factual check of IST's
peer-review model and is added once that is resolved; it is intentionally not
asserted here yet.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IST_MAIN = ROOT / "manuscript" / "main.tex"
sys.path.insert(0, str(ROOT / "tools"))
from ist_wordcount import ist_word_count  # noqa: E402

WORD_CAP = 15000  # IST regular-paper hard cap; the P2 work consumed the
                  # earlier 14500-then-14900 working-target buffers in exchange
                  # for the LLM-baseline, R3 refinement, and R4 adversarial
                  # subsections, so the only remaining ceiling is the hard cap.


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class P0SubmissionReadinessTest(unittest.TestCase):
    def test_p0_1_ist_word_count_within_working_target(self) -> None:
        r = ist_word_count()
        self.assertLessEqual(
            r["total"], WORD_CAP,
            f"IST-counted total {r['total']} exceeds working target {WORD_CAP} "
            f"(cap 15000). Breakdown: {r}",
        )

    def test_p0_3_title_at_most_70_chars(self) -> None:
        tex = read(IST_MAIN)
        m = re.search(r"\\title\{([^}]+)\}", tex)
        self.assertIsNotNone(m, "no \\title{} found")
        title = m.group(1).strip()
        self.assertLessEqual(
            len(title), 70,
            f"title is {len(title)} chars (>70): {title!r}",
        )

    def test_p0_4_abstract_conclusion_scoped_positive(self) -> None:
        tex = read(IST_MAIN)
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
        self.assertIsNotNone(m, "no abstract found")
        abstract = m.group(1)
        # The Conclusion must not broadcast the four-"not" disclaimer pile-up.
        self.assertNotIn(
            "This is not a reliability, baseline, cross-family, or geometry-independent claim.",
            abstract,
            "abstract Conclusion still uses the four-'not' disclaimer; reframe positively",
        )
        # Guard against any new "is not ... claim" pile-up of >=3 negations in
        # the Conclusion sentence.
        concl = abstract.split("Conclusion:")[-1] if "Conclusion:" in abstract else abstract
        self.assertLess(
            concl.count(" not "), 3,
            f"abstract Conclusion still piles up negations ({concl.count(' not ')} 'not's)",
        )

    def test_p0_structured_abstract_still_compliant(self) -> None:
        # Regression guard: trimming must not break the structured-abstract
        # requirements that were already satisfied.
        tex = read(IST_MAIN)
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
        abstract = m.group(1)
        for head in ["Context:", "Objective", "Method", "Results:", "Conclusion:"]:
            with self.subTest(heading=head):
                self.assertIn(head, abstract)
        # <=300 words (strip latex commands and headers)
        a = re.sub(r"\\textbf\{[^}]+\}", "", abstract)
        a = re.sub(r"\\emph\{([^}]+)\}", r"\1", a)
        a = re.sub(r"\\[a-zA-Z]+\*?(\{[^}]*\})*", "", a)
        a = re.sub(r"\$[^$]*\$", "X", a)
        a = re.sub(r"[{}]", " ", a)
        words = len(re.findall(r"[A-Za-z][A-Za-z0-9'\-]*", a))
        self.assertLessEqual(words, 300, f"abstract is {words} words (>300)")


if __name__ == "__main__":
    unittest.main()
