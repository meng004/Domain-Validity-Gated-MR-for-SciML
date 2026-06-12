"""Phase 11 guards for the primary empirical-volume upgrade."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/primary-volume-upgrade/primary_volume_report.json"


class Phase11PrimaryEmpiricalVolumeTest(unittest.TestCase):
    def test_primary_volume_report_expands_mgn_denominators(self) -> None:
        self.assertTrue(REPORT.exists(), "primary empirical volume report is missing")
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["record_type"], "primary-empirical-volume-upgrade")
        self.assertEqual(report["source_repo"], "https://github.com/meng004/Minimum-MR-SubSet")
        self.assertEqual(report["source_head"], "9ef862ec37335b4834d0a1fb38b4b613af702f34")
        self.assertEqual(report["mgn_checkpoints"], ["S0", "S1", "S2", "S3", "S4", "S5"])

        mirror = report["mirror_ood"]
        self.assertEqual(mirror["n_checkpoints"], 6)
        self.assertEqual(mirror["frames_per_checkpoint"], 10)
        self.assertEqual(mirror["total_frame_cells"], 60)
        self.assertEqual(mirror["fail_count"], 60)
        self.assertEqual(mirror["pass_count"], 0)
        self.assertGreaterEqual(mirror["wilson_fail_rate_ci95"][0], 0.93)

        conservation = report["conservation"]
        self.assertEqual(conservation["n_checkpoints"], 6)
        self.assertEqual(conservation["transition_frames_per_checkpoint"], 9)
        self.assertEqual(conservation["total_transition_cells"], 54)
        self.assertEqual(conservation["pass_count"], 54)
        self.assertLessEqual(conservation["max_ratio"], 1.5)
        self.assertIn("absolute", conservation["honesty_boundary"].lower())

        exact = report["exact_symmetric_mesh"]
        self.assertEqual(exact["n_checkpoints"], 6)
        self.assertEqual(exact["input_seeds_per_checkpoint"], 3)
        self.assertEqual(exact["total_input_cells"], 18)
        self.assertEqual(exact["fail_count"], 18)
        self.assertIn("synthetic", exact["honesty_boundary"].lower())

        self.assertIn("clustered", report["honesty_boundary"].lower())
        self.assertIn("one source trajectory", report["honesty_boundary"].lower())

    def test_volume_report_is_superseded_by_phase12_for_manuscript_claims(self) -> None:
        scope_report = ROOT / "research_assets/runs/primary-scope-upgrade/primary_scope_report.json"
        self.assertTrue(
            scope_report.exists(),
            "phase11 volume report should be superseded by the phase12 scope report",
        )


if __name__ == "__main__":
    unittest.main()
