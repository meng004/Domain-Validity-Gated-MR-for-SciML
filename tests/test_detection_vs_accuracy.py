"""Guard for the MR-detection-vs-accuracy complementarity (claim C38).

Pins the cylinder-MGN result that the domain-validity MRs and a rollout-accuracy monitor
are complementary, not redundant: two faults (mesh-adjacency edge permutation, physical-
channel swap) are caught by an MR while leaving rollout error within ~1.3x of the
in-distribution baseline (0.0216, below a 2x accuracy-regression threshold), so the MRs
surface relation violations an accuracy monitor leaves within band. Prevents prose from
overclaiming MR superiority over accuracy/UQ.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research_assets/runs/detection-vs-accuracy/raw/metric_ledger.json"


class DetectionVsAccuracyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.c = cls.d["complementarity"]

    def test_union_detection_consistent_with_c10(self) -> None:
        # The MR detection reproduces the committed C10 result (5 of 10).
        self.assertEqual(round(self.d["summary"]["union_detection_rate"] * 10), 5)

    def test_baseline_rollout_matches_in_distribution_accuracy(self) -> None:
        # Baseline rollout error is the paper's in-distribution one-step accuracy (~0.0216).
        self.assertAlmostEqual(self.c["baseline_rollout_relative_l2"], 0.0216, places=3)

    def test_mr_catches_what_accuracy_misses(self) -> None:
        # The complementarity cases: MRs catch these, the accuracy monitor does not.
        self.assertEqual(self.c["mr_catches_accuracy_misses"],
                         ["MA_permute_edges", "PC_swap_xy"])
        # Honest: on this SUT no fault is caught only by accuracy.
        self.assertEqual(self.c["accuracy_catches_mr_misses"], [])

    def test_mr_only_faults_stay_within_accuracy_band(self) -> None:
        mult = self.c["accuracy_rollout_multiplier"]
        mr_only = set(self.c["mr_catches_accuracy_misses"])
        for e in self.d["detection_matrix"]:
            if e["mutant"] in mr_only:
                # caught by an MR but rollout error stays below the accuracy threshold
                self.assertTrue(e["detected_by_any"])
                self.assertLess(e["rollout_over_baseline"], mult)
                self.assertFalse(e["accuracy_monitor_detects"])

    def test_complementarity_not_superiority_note(self) -> None:
        self.assertIn("not superiority", self.c["note"].lower())


if __name__ == "__main__":
    unittest.main()
