"""Phase 12 guards for the multi-trajectory primary empirical-scope upgrade."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
IST_MAIN = ROOT / "manuscript/main.tex"
REPORT = ROOT / "research_assets/runs/primary-scope-upgrade/primary_scope_report.json"


class Phase12PrimaryEmpiricalScopeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.md = MANUSCRIPT.read_text(encoding="utf-8")
        cls.tex = IST_MAIN.read_text(encoding="utf-8")

    def test_scope_report_removes_single_trajectory_denominator(self) -> None:
        self.assertTrue(REPORT.exists(), "primary empirical scope report is missing")
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["record_type"], "primary-empirical-scope-upgrade")
        self.assertEqual(report["source_repo"], "https://github.com/meng004/Minimum-MR-SubSet")
        self.assertEqual(report["source_head"], "9ef862ec37335b4834d0a1fb38b4b613af702f34")
        self.assertEqual(report["mgn_checkpoints"], ["S0", "S1", "S2", "S3", "S4", "S5"])
        self.assertEqual(report["heldout_test_trajectories"], [0, 1, 2])
        self.assertEqual(report["n_independent_test_trajectories"], 3)

        mirror = report["mirror_ood"]
        self.assertEqual(mirror["n_checkpoints"], 6)
        self.assertEqual(mirror["n_trajectories"], 3)
        self.assertEqual(mirror["frames_per_checkpoint_trajectory"], 10)
        self.assertEqual(mirror["total_frame_cells"], 180)
        self.assertEqual(mirror["fail_count"], 180)
        self.assertEqual(mirror["pass_count"], 0)
        self.assertIn("not a single-source-trajectory estimate", mirror["honesty_boundary"])

        conservation = report["conservation"]
        self.assertEqual(conservation["n_checkpoints"], 6)
        self.assertEqual(conservation["n_trajectories"], 3)
        self.assertEqual(conservation["transition_frames_per_checkpoint_trajectory"], 9)
        self.assertEqual(conservation["total_transition_cells"], 162)
        self.assertEqual(conservation["pass_count"], 162)
        self.assertLessEqual(conservation["max_ratio"], 1.5)
        self.assertIn("absolute", conservation["honesty_boundary"].lower())

        exact = report["exact_symmetric_mesh"]
        self.assertEqual(exact["n_checkpoints"], 6)
        self.assertEqual(exact["input_seeds_per_checkpoint"], 3)
        self.assertEqual(exact["total_input_cells"], 18)
        self.assertEqual(exact["fail_count"], 18)

        boundary = report["honesty_boundary"]
        self.assertIn("not a single-source-trajectory estimate", boundary)
        self.assertIn("not a cross-SUT", boundary)
        self.assertNotIn("one source trajectory", boundary.lower())

    def test_manuscripts_surface_scope_upgrade_without_reintroducing_single_trajectory_claim(self) -> None:
        required_markers = [
            "primary empirical scope upgrade",
            "K=6 x 3 trajectories x 10 mirror-y OOD-stress grid",
            "K=6 x 3 trajectories x 9 conservation-transition grid",
            "not a single-source-trajectory estimate",
            "not a cross-SUT",
        ]
        for text in (self.md, self.tex):
            for marker in required_markers:
                self.assertIn(marker, text)
            self.assertNotIn("one source trajectory", text)


if __name__ == "__main__":
    unittest.main()
