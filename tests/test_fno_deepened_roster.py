"""Guards for the deepened FNO K=6 roster (n=15 seeds per PDE).

These checks verify STRUCTURE only — actual numbers come from the real run.
Reviewer concern: original n=3 is underpowered; n=15 provides adequate
cross-seed evidence for the periodic-translation admissibility claim.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "research_assets/runs/fno-k6-roster"
AGG = ROSTER / "fno_k6_aggregate.json"


class TestFnoRosterDeepened(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assertTrue(cls, AGG.exists(), f"aggregate JSON missing: {AGG}")
        cls.r = json.loads(AGG.read_text(encoding="utf-8"))

    def test_aggregate_json_exists(self) -> None:
        self.assertTrue(AGG.exists(), f"aggregate JSON missing: {AGG}")

    def test_n_seeds_at_least_15(self) -> None:
        self.assertGreaterEqual(
            self.r["n_seeds"], 15,
            f"n_seeds={self.r['n_seeds']} < 15; reviewer requires n≥15 per PDE",
        )

    def test_per_sut_entries_at_least_15_per_pde(self) -> None:
        for pde in ("burgers", "heat"):
            count = sum(1 for row in self.r["per_sut"] if row["pde"] == pde)
            self.assertGreaterEqual(
                count, 15,
                f"per_sut has only {count} entries for pde={pde}; need ≥15",
            )

    def test_per_pde_family_has_wilson95_ci(self) -> None:
        ppf = self.r.get("per_pde_family", {})
        for pde in ("burgers", "heat"):
            self.assertIn(pde, ppf, f"per_pde_family missing key '{pde}'")
            entry = ppf[pde]
            self.assertIn(
                "periodic_translation_pass_rate_wilson95_ci",
                entry,
                f"per_pde_family['{pde}'] missing 'periodic_translation_pass_rate_wilson95_ci'",
            )
            ci = entry["periodic_translation_pass_rate_wilson95_ci"]
            self.assertIsInstance(ci, list, "wilson95_ci must be a list")
            self.assertEqual(len(ci), 2, "wilson95_ci must have exactly 2 floats")
            self.assertIsInstance(ci[0], float, "wilson95_ci[0] must be float")
            self.assertIsInstance(ci[1], float, "wilson95_ci[1] must be float")
            self.assertLessEqual(ci[0], ci[1], "wilson95_ci[0] must be ≤ ci[1]")


if __name__ == "__main__":
    unittest.main()
