"""P2-4 regression guards for the refined R3 PC_zero_vy severity sweep.

The committed fault_robustness_report.json must carry the finer fraction grid
that resolves the detection cliff, and the manuscript + ledger must report the
corrected mechanism (partial zeroing is caught by the node-permutation detector,
not the symmetry MR; the blind spot is the exactly-uniform p=1.0 fault).
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/fault-robustness-e3/fault_robustness_report.json"
MANUSCRIPT = ROOT / "paper/manuscript.md"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"

REFINED = [0.85, 0.9, 0.95, 0.99]


class TestR3Refinement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text())
        cls.r3 = cls.report["R3_PC_zero_vy_partial_fraction_sweep"]

    def test_refined_levels_present(self):
        levels = set(self.r3["levels"])
        for f in REFINED:
            self.assertIn(f, levels, f"refined fraction {f} missing from R3 levels")
        self.assertEqual(self.r3["levels"], sorted(self.r3["levels"]),
                         "R3 levels must be sorted")

    def test_knife_edge_structure(self):
        rate = self.r3["per_level_detection_rate"]
        # Every partial fraction up to 0.99 is fully detected by the union detector.
        for p in [0.25, 0.5, 0.75, 0.85, 0.9, 0.95, 0.99]:
            cell = rate[str(p)]["any"]
            self.assertEqual((cell["k"], cell["n"]), (6, 6),
                             f"p={p} any-detector should be 6/6, got {cell['k']}/{cell['n']}")
        # The exactly-uniform fault is invisible to every detector.
        full = rate["1.0"]["any"]
        self.assertEqual((full["k"], full["n"]), (0, 6),
                         "p=1.0 any-detector should be 0/6 (symmetry blind spot)")

    def test_partial_detection_is_node_perm_not_symmetry(self):
        rate = self.r3["per_level_detection_rate"]
        for p in REFINED:
            self.assertEqual(rate[str(p)]["node_perm"]["k"], 6,
                             f"p={p} should be caught by node_perm on all 6 SUTs")
            self.assertEqual(rate[str(p)]["mirror_y"]["k"], 0,
                             f"p={p}: symmetry MR must NOT be the detector (0/6)")

    def test_manuscript_reports_refined_mechanism(self):
        m = MANUSCRIPT.read_text()
        self.assertIn("0.99", m, "manuscript must cite the refined grid")
        self.assertTrue(re.search(r"knife-edge|measure-zero blind", m),
                        "manuscript R3 should describe the knife-edge/measure-zero blind spot")
        self.assertIn("node-permutation* detector".replace("*", ""), m.replace("*", ""))

    def test_ledger_grid_and_mechanism_updated(self):
        led = LEDGER.read_text()
        self.assertIn("0.99", led, "ledger C13 scope must include the refined grid")
        self.assertNotIn("monotone-non-decreasing detection", led,
                         "ledger must drop the superseded monotone wording")


if __name__ == "__main__":
    unittest.main()
