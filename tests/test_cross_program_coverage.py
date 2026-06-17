"""Guard for the cross-program coverage-geometry generalization (claim C39).

Pins the result that the coverage-geometry reading reproduces across seven program
types in three families (neural surrogates, classical solvers, a production physics
code), from committed Minimum-MR-SubSet kill matrices reused read-only: structural
blind spots are present in nearly every program, the class-to-class mapping is
program-specific, and detection rate tracks the admissible MR set (it is NOT uniform).
Also pins the honesty boundary (the paper's pipeline was not executed end-to-end on each
program). Prevents prose from overclaiming a validated cross-program detector.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research_assets/runs/cross-program-coverage/raw/metric_ledger.json"
FIX = ROOT / "research_assets/external/minimum-mr-subset-killmatrices"


class CrossProgramCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_seven_programs_three_families(self) -> None:
        self.assertEqual(self.d["n_programs"], 7)
        self.assertEqual(len(self.d["per_program"]), 7)
        self.assertEqual(set(self.d["families"]),
                         {"neural surrogate", "classical solver", "production code"})

    def test_all_fixtures_present_with_provenance(self) -> None:
        for p in self.d["per_program"]:
            self.assertTrue((FIX / p["program"] / "kill_matrix.csv").exists())
        self.assertTrue((FIX / "PROVENANCE.md").exists())

    def test_coverage_geometry_generalizes(self) -> None:
        a = self.d["aggregate"]
        # Structural blind spots in nearly every program (the coverage-geometry prediction);
        # the openmc rich-MR-set program is the one without a blind class.
        self.assertGreaterEqual(a["n_with_structural_blind_spot"], 6)
        # The class-to-class mapping is program-specific (distinct per program).
        self.assertTrue(a["class_to_class_mappings_program_specific"])
        # Detection tracks the MR set: NOT uniform (classical-solver minimal sets are low,
        # rich sets reach 1.0). Pin the wide range rather than a single rate.
        lo, hi = a["detection_rate_range"]
        self.assertLessEqual(lo, 0.25)
        self.assertGreaterEqual(hi, 0.95)

    def test_honesty_boundary_present(self) -> None:
        hb = self.d["honesty_boundary"].lower()
        self.assertIn("not", hb)
        self.assertIn("end-to-end", hb)
        self.assertEqual(self.d["evidence_level"], "reused-committed-kill-matrices-no-rerun")


if __name__ == "__main__":
    unittest.main()
