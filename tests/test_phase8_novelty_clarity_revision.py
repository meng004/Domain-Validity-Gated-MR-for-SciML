"""Phase 8 guards for the novelty/clarity revision."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
IST_MAIN = ROOT / "manuscript/main.tex"
SUPPLEMENTARY = ROOT / "manuscript/supplementary.tex"


class Phase8NoveltyClarityRevisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.md = MANUSCRIPT.read_text(encoding="utf-8")
        cls.tex = IST_MAIN.read_text(encoding="utf-8")
        cls.supp = SUPPLEMENTARY.read_text(encoding="utf-8")

    def test_positive_contribution_names_are_front_loaded(self) -> None:
        for text in (self.md, self.tex):
            self.assertTrue(
                "measurement-floor admissibility gate" in text
                or "numerical-decidability admissibility gate" in text
            )
            self.assertIn("typed domain-inadmissibility verdict", text)
            self.assertTrue(
                "MR-class-to-fault-class diagnostic" in text
                or "seeded-fault diagnostic stress test" in text
            )

    def test_closest_prior_positioning_table_is_present(self) -> None:
        self.assertIn("closest-prior capability matrix", self.tex)
        self.assertIn("tab:closest-prior-positioning-supp", self.supp)
        for marker in [
            "Reichert et al.",
            "Eniser et al.",
            "Duque-Torres / MetaTrimmer",
            "What this paper adds",
        ]:
            self.assertIn(marker, self.tex + self.supp)

    def test_main_text_is_not_ledger_dominated(self) -> None:
        # Claim IDs may remain in the ledger and appendical map, but the main
        # manuscript should not read as an internal bookkeeping document.
        main_body = self.tex.split(r"\appendix", 1)[0]
        self.assertLessEqual(len(re.findall(r"\bPC\d+", main_body)), 14)
        self.assertLessEqual(len(re.findall(r"\bC\d+", main_body)), 10)

    def test_repetitive_disclaimer_language_is_compressed(self) -> None:
        combined = self.md + "\n" + self.tex
        self.assertLessEqual(combined.count("not a "), 28)
        self.assertLessEqual(len(re.findall(r"not [^.]{0,80}claim", combined)), 12)
        self.assertIn("The positive claim is methodological", combined)


if __name__ == "__main__":
    unittest.main()
