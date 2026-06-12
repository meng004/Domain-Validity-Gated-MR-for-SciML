"""Guards for the non-MGN PointMLP cylinder-flow primary workflow."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/pointmlp-cylinder-primary-workflow/pointmlp_cylinder_primary_workflow_report.json"
RUBRIC = ROOT / "research_assets/runs/pointmlp-cylinder-primary-workflow/rubric_decisions.json"
SMOKE = ROOT / "research_assets/runs/pointmlp-cylinder-primary-workflow/smoke_manifest.json"


class PointMlpCylinderPrimaryWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_report_is_different_architecture_cylinder_flow_sut(self) -> None:
        self.assertEqual(self.report["record_type"], "pointmlp-cylinder-primary-workflow")
        self.assertEqual(self.report["domain"], "DeepMind cylinder_flow")
        self.assertEqual(self.report["architecture_family"], "PointMLP row-wise coordinate network")
        self.assertEqual(self.report["sut_id"], "pointmlp-cylinder-sut-v1")
        self.assertTrue((ROOT / self.report["checkpoint_path"]).exists())
        self.assertEqual(self.report["train_meta"]["train_trajectories"], [0, 1])
        self.assertEqual(self.report["train_meta"]["eval_trajectories"], [2])

    def test_full_workflow_artifacts_and_flags_exist(self) -> None:
        self.assertTrue(RUBRIC.exists(), "missing PointMLP rubric decisions")
        self.assertTrue(SMOKE.exists(), "missing PointMLP smoke manifest")
        flags = self.report["full_workflow_flags"]
        for key in (
            "trained_checkpoint",
            "rubric_decisions",
            "source_followup_outputs",
            "metric_ledgers",
            "relation_verdicts",
            "different_architecture_from_mgn",
            "same_domain_real_dataset",
        ):
            self.assertTrue(flags[key], key)
        for path in self.report["metric_ledgers"].values():
            self.assertTrue((ROOT / path).exists(), path)

    def test_relation_denominators_match_executed_primary_workflow(self) -> None:
        node_perm = self.report["node_permutation"]
        self.assertEqual(node_perm["total_case_cells"], 9)
        self.assertEqual(node_perm["pass_count"], 9)
        self.assertEqual(node_perm["other_count"], 0)
        self.assertEqual(node_perm["max_metric_value"], 0.0)

        mirror = self.report["mirror_ood_stress"]
        self.assertEqual(mirror["total_case_cells"], 10)
        self.assertEqual(mirror["fail_count"], 10)
        self.assertGreater(mirror["median_violation_over_floor"], 0.0)
        self.assertEqual(mirror["precondition_report"]["decision"], "downgraded-to-ood-stress")

        conservation = self.report["conservation_reference_relative"]
        self.assertEqual(conservation["total_case_cells"], 9)
        self.assertEqual(conservation["pass_count"], 9)
        self.assertLessEqual(conservation["max_metric_value"], 1.5)
        self.assertIn("Absolute mass conservation remains deferred", conservation["honesty_boundary"])

        exact = self.report["exact_symmetric_mesh"]
        self.assertEqual(exact["total_case_cells"], 3)
        self.assertEqual(exact["fail_count"], 3)

    def test_rows_and_metric_ledgers_reference_committed_raw_outputs(self) -> None:
        relation_keys = [
            "node_permutation",
            "mirror_ood_stress",
            "conservation_reference_relative",
            "exact_symmetric_mesh",
        ]
        for key in relation_keys:
            ledger = json.loads((ROOT / self.report["metric_ledgers"][key]).read_text(encoding="utf-8"))
            self.assertEqual(len(ledger["entries"]), self.report[key]["total_case_cells"])
            for row in self.report[key]["rows"]:
                self.assertTrue((ROOT / row["raw_output"]).exists(), row["raw_output"])

    def test_honesty_boundary_prevents_overclaiming(self) -> None:
        boundary = self.report["honesty_boundary"]
        self.assertIn("different architecture family from MeshGraphNet", boundary)
        self.assertIn("not PhysicsNeMo", boundary)
        self.assertIn("not EchoWave", boundary)
        self.assertIn("not a cross-dataset", boundary)


if __name__ == "__main__":
    unittest.main()
