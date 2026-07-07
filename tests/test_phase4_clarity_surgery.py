"""Phase 4 clarity-surgery guards.

These tests now encode the JSS-targeted clarity constraints from paper/77:
keep the paper within a conservative local readability budget, keep the abstract
reviewer-facing rather than number-heavy, preserve short highlights, and collapse
stale repeated "blocked" wording into one canonical boundary statement.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
IST_MAIN = ROOT / "manuscript/main.tex"
sys.path.insert(0, str(ROOT / "tools"))
from ist_wordcount import ist_word_count  # noqa: E402


class Phase4ClaritySurgeryTest(unittest.TestCase):
    def test_legacy_word_count_keeps_jss_readability_buffer(self) -> None:
        # JSS has no official regular-paper word cap found in the 2026-07-03
        # guide check. Keep the legacy IST cap only as a conservative density
        # diagnostic until Phase 6 compression.
        counts = ist_word_count()
        self.assertLessEqual(
            counts["total"],
            15000,
            f"legacy density diagnostic requires counted text <=15000; got {counts}",
        )

    def test_jss_abstract_is_not_number_dump(self) -> None:
        tex = IST_MAIN.read_text(encoding="utf-8")
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
        self.assertIsNotNone(m, "abstract block not found")
        block = m.group(1)
        self.assertIsNone(
            re.search(r"\b(?:24/24|180/180|162/162|10/10|0/6|5/10|13/20)\b", block),
            "JSS abstract should summarize evidence boundaries without empirical-number dumping",
        )
        self.assertIn("not general SciML reliability", block)

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
        self.assertIn("The canonical blocked list remains active", text)


if __name__ == "__main__":
    unittest.main()
