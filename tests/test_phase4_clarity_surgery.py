"""Phase 4 clarity-surgery guards.

These tests encode the Phase-4 constraints from paper/32: reduce the IST body,
keep the abstract reviewer-facing rather than number-heavy, preserve short
highlights, and collapse stale repeated "blocked" wording into one canonical
boundary statement.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper/manuscript.md"
IST_MAIN = ROOT / "paper/ist-submission/main.tex"
sys.path.insert(0, str(ROOT / "tools"))
from ist_wordcount import ist_word_count  # noqa: E402


class Phase4ClaritySurgeryTest(unittest.TestCase):
    def test_ist_word_count_keeps_phase4_clarity_buffer(self) -> None:
        counts = ist_word_count()
        self.assertLessEqual(
            counts["total"],
            11000,
            f"Phase 4 clarity surgery should keep IST-counted text <=11000; got {counts}",
        )

    def test_abstract_results_and_conclusion_are_not_number_dump(self) -> None:
        tex = IST_MAIN.read_text(encoding="utf-8")
        m = re.search(r"\\textbf\{Results:\}(.*?)\\end\{abstract\}", tex, re.S)
        self.assertIsNotNone(m, "abstract Results/Conclusion block not found")
        block = m.group(1)
        self.assertIsNone(
            re.search(r"\b\d+(?:\.\d+)?\b", block),
            "Phase 4 abstract should summarize evidence boundaries without empirical-number dumping",
        )
        self.assertIn("Broader generalization is future work", block)

    def test_highlights_are_short_for_ist_upload(self) -> None:
        tex = IST_MAIN.read_text(encoding="utf-8")
        m = re.search(r"\\begin\{highlights\}(.*?)\\end\{highlights\}", tex, re.S)
        self.assertIsNotNone(m, "highlights block not found")
        items = re.findall(r"\\item\s+(.+)", m.group(1))
        self.assertEqual(len(items), 5)
        for item in items:
            plain = re.sub(r"\$[^$]*\$", "X", item).strip()
            self.assertLessEqual(len(plain), 85, item)

    def test_stale_pre_phase4_blocked_wording_removed(self) -> None:
        text = MANUSCRIPT.read_text(encoding="utf-8") + "\n" + IST_MAIN.read_text(encoding="utf-8")
        for stale in [
            "only one trained SUT and checkpoint",
            "the expert-MR, LLM-candidate, and generic-MR comparators remain planned",
            "comparative, and fault-detection results remain blocked",
        ]:
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text)
        self.assertIn("The canonical block list is unchanged", text)
        self.assertIn("The canonical blocked list is unchanged", text)


if __name__ == "__main__":
    unittest.main()
