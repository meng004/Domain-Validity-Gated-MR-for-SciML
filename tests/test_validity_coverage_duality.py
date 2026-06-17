"""Guard for the validity-coverage duality principle (claim C37).

C37 is a proposed, falsifiable organizing principle: the same physics-based
admissibility gate that decides whether an MR yields a meaningful verdict also
fixes which faults that MR can detect. Two of its predictions are confirmed --
the R3 knife-edge collapse and the C36 cross-SUT MR-removal experiment. This
guard pins (a) that the cross-SUT keystone evidence backs the principle, (b) that
the manuscript frames the principle as proposed/falsifiable (the courage of an
explicit refutation surface), and (c) that the manuscript does not overclaim a
validated quantitative coverage model (the honesty boundary).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IST_MAIN = ROOT / "paper/ist-submission/main.tex"
CROSS_SUT = (ROOT / "research_assets/runs/production-grade-sut-extension"
            / "physicsnemo-mgn-airfoil-seeded-fault-detection/raw/metric_ledger.json")
CYLINDER = ROOT / "research_assets/runs/seeded-fault-detection/raw/metric_ledger.json"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


class ValidityCoverageDualityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tex = IST_MAIN.read_text(encoding="utf-8")
        cls.cross = json.loads(CROSS_SUT.read_text(encoding="utf-8"))
        cls.ledger = LEDGER.read_text(encoding="utf-8")

    def test_claim_registered(self) -> None:
        self.assertIn("C37-validity-coverage-duality", self.ledger)

    def test_both_seeded_fault_ledgers_exist(self) -> None:
        self.assertTrue(CYLINDER.exists())
        self.assertTrue(CROSS_SUT.exists())

    def test_keystone_prediction_backed_by_cross_sut(self) -> None:
        # The keystone falsifiable prediction: changing the physics makes the gate
        # rule mirror-y inadmissible and removes exactly its coverage, while the
        # admissible MRs' coverage (normalization) persists.
        x = self.cross["cross_sut_comparison"]
        self.assertEqual(x["mirror_y_status_on_airfoil"], "inadmissible")
        self.assertEqual(x["shared_localization_across_suts"], ["normalization_scale_fault"])

    def test_manuscript_frames_principle_as_falsifiable(self) -> None:
        low = self.tex.lower()
        self.assertIn("falsifiable", low)
        # The duality is named (validity and coverage linked through the one gate).
        self.assertTrue("two faces" in low or "duality" in low,
                        "manuscript should name the validity-coverage duality")

    def test_manuscript_does_not_overclaim_validated_model(self) -> None:
        low = self.tex.lower()
        for bad in ["validated predictive coverage model",
                    "validated quantitative coverage model",
                    "proven coverage model"]:
            self.assertNotIn(bad, low)


if __name__ == "__main__":
    unittest.main()
