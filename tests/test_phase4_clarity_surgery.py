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
        # Buffer history: 11000 (Phase 4) -> 11500 (Phase 17, scaled PhysicsNeMo
        # evidence) -> 11700 (Phase 19). The Phase-19 increment is the sharpened
        # novelty argument the v18 panel asked for (the measurement-floor gate's
        # categorical distinction from relaxations/constraint-filtering); five
        # secondary prose passages were genuinely condensed in the same pass to
        # offset most of it. The IST hard limit is 15000 on a deliberately
        # conservative counter that double-counts table text, so 11700 still
        # leaves a >3.3k margin while preserving the clarity-discipline intent.
        counts = ist_word_count()
        self.assertLessEqual(
            counts["total"],
            11700,
            f"Phase 4/17/19 clarity buffer requires IST-counted text <=11700; got {counts}",
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
        self.assertIn("The canonical block list is narrowed but still active", text)
        self.assertIn("The canonical blocked list is narrowed but still active", text)


if __name__ == "__main__":
    unittest.main()
