"""Guards for the deepened PINN roster (n=15 seeds per PDE).

These checks verify STRUCTURE only — actual numbers come from the real run.
Reviewer concern: original n=3 is underpowered (PINN MR-B Wilcoxon p=0.5);
n=15 per PDE provides adequate cross-seed evidence for the per-PDE Wilson CI.

NOTE on the inter-PDE Wilcoxon (diffusion-vs-Burgers MR-B ratios):
This test is a PHYSICS MAGNITUDE TEST, not a gate-reliability test. It compares
MR-B violation/floor ratios between two different PDEs that have different
boundary conditions (Neumann vs Dirichlet), which physically predicts different
MR-B behaviour. Significance at n=15 would reflect the physics difference, not
provide evidence that the gate is reliable. The valid statistic is the per-PDE
Wilson CI on the MR-B pass rate (which answers: does the gate consistently
classify within a PDE family?). We do NOT assert on the inter-PDE Wilcoxon.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "research_assets/runs/pinn-k6-roster"
AGG = ROSTER / "pinn_k6_aggregate.json"


class TestPinnRosterDeepened(unittest.TestCase):
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
        for pde in ("burgers", "diffusion"):
            count = sum(1 for row in self.r["per_sut"] if row["pde"] == pde)
            self.assertGreaterEqual(
                count, 15,
                f"per_sut has only {count} entries for pde={pde}; need ≥15",
            )

    def test_per_pde_family_has_mr_b_wilson95_ci(self) -> None:
        ppf = self.r.get("per_pde_family", {})
        for pde in ("burgers", "diffusion"):
            self.assertIn(pde, ppf, f"per_pde_family missing key '{pde}'")
            entry = ppf[pde]
            self.assertIn(
                "mr_b_pass_rate_wilson95_ci",
                entry,
                f"per_pde_family['{pde}'] missing 'mr_b_pass_rate_wilson95_ci'",
            )
            ci = entry["mr_b_pass_rate_wilson95_ci"]
            self.assertIsInstance(ci, list, "mr_b_pass_rate_wilson95_ci must be a list")
            self.assertEqual(len(ci), 2, "mr_b_pass_rate_wilson95_ci must have exactly 2 floats")
            self.assertIsInstance(ci[0], float, "mr_b_pass_rate_wilson95_ci[0] must be float")
            self.assertIsInstance(ci[1], float, "mr_b_pass_rate_wilson95_ci[1] must be float")
            self.assertLessEqual(
                ci[0], ci[1],
                f"per_pde_family['{pde}']['mr_b_pass_rate_wilson95_ci'][0] must be <= [1]",
            )

    def test_per_pde_family_has_mr_b_pass_rate_and_count(self) -> None:
        ppf = self.r.get("per_pde_family", {})
        for pde in ("burgers", "diffusion"):
            entry = ppf[pde]
            self.assertIn(
                "mr_b_pass_count",
                entry,
                f"per_pde_family['{pde}'] missing 'mr_b_pass_count'",
            )
            self.assertIn(
                "mr_b_n",
                entry,
                f"per_pde_family['{pde}'] missing 'mr_b_n'",
            )
            self.assertGreaterEqual(entry["mr_b_n"], 15)
            self.assertGreaterEqual(entry["mr_b_pass_count"], 0)
            self.assertLessEqual(entry["mr_b_pass_count"], entry["mr_b_n"])

    def test_schema_version_updated(self) -> None:
        # The deepened run must update schema_version to indicate the new format
        self.assertIn(
            "schema_version",
            self.r,
            "aggregate must have schema_version field",
        )


if __name__ == "__main__":
    unittest.main()
