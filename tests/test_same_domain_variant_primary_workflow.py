"""Guards for the same-domain second-SUT primary workflow package."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/same-domain-variant-primary-workflow/same_domain_variant_primary_workflow_report.json"
RUBRIC = ROOT / "research_assets/runs/same-domain-variant-primary-workflow/rubric_decisions.json"
SMOKE = ROOT / "research_assets/runs/same-domain-variant-primary-workflow/smoke_manifest.json"


class SameDomainVariantPrimaryWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_report_promotes_second_same_domain_checkpoint_family(self) -> None:
        self.assertEqual(self.report["record_type"], "same-domain-variant-primary-workflow")
        self.assertEqual(self.report["domain"], "DeepMind cylinder_flow")
        self.assertEqual(self.report["architecture_family"], "MeshGraphNet configuration variants")
        self.assertEqual(self.report["checkpoints"], ["S4", "S5"])
        self.assertEqual(self.report["heldout_test_trajectories"], [0, 1, 2])
        self.assertIn("S4 is a wider", self.report["second_sut_family_definition"])
        self.assertIn("S5 is a deeper", self.report["second_sut_family_definition"])

    def test_full_primary_workflow_flags_and_rubric_artifacts_exist(self) -> None:
        self.assertTrue(RUBRIC.exists(), "missing rubric decisions artifact")
        self.assertTrue(SMOKE.exists(), "missing smoke manifest")
        flags = self.report["full_workflow_flags"]
        for key in (
            "trained_checkpoints",
            "rubric_decisions",
            "source_followup_outputs",
            "metric_ledgers",
            "relation_verdicts",
            "same_domain_real_dataset",
        ):
            self.assertTrue(flags[key], key)
        rubric = json.loads(RUBRIC.read_text(encoding="utf-8"))
        self.assertEqual(len(rubric), 4)
        self.assertEqual({item["relation_id"] for item in rubric}, {
            "mgn-node-permutation-equivariance",
            "mirror_y_ood_stress",
            "conservation_reference_relative",
            "mirror_y_exact_symmetric_mesh",
        })

    def test_relation_verdict_denominators_are_complete(self) -> None:
        node_perm = self.report["node_permutation"]
        self.assertEqual(node_perm["total_case_cells"], 2)
        self.assertEqual(node_perm["pass_count"], 2)
        self.assertEqual(node_perm["other_count"], 0)

        mirror = self.report["mirror_ood_stress"]
        self.assertEqual(mirror["total_case_cells"], 60)
        self.assertEqual(mirror["fail_count"], 60)
        self.assertEqual(mirror["other_count"], 0)
        self.assertGreater(mirror["median_violation_over_floor"], 1.0)

        conservation = self.report["conservation_reference_relative"]
        self.assertEqual(conservation["total_case_cells"], 54)
        self.assertEqual(conservation["pass_count"], 54)
        self.assertEqual(conservation["other_count"], 0)
        self.assertLessEqual(conservation["max_metric_value"], 1.5)
        self.assertIn("Absolute mass conservation remains deferred", conservation["honesty_boundary"])

        exact = self.report["exact_symmetric_mesh"]
        self.assertEqual(exact["total_case_cells"], 6)
        self.assertEqual(exact["fail_count"], 6)
        self.assertEqual(exact["other_count"], 0)

    def test_rows_point_to_existing_raw_outputs_and_ledgers(self) -> None:
        for relation_rows in self.report["rows"].values():
            for row in relation_rows:
                self.assertTrue((ROOT / row["ledger"]).exists(), row["ledger"])
                if "evidence_artifact" in row:
                    self.assertTrue((ROOT / row["evidence_artifact"]).exists(), row["evidence_artifact"])
                if "raw_outputs" in row:
                    for recorded in row["raw_outputs"].values():
                        self.assertTrue((ROOT / recorded).exists(), recorded)
                if "raw_output_dir" in row:
                    self.assertTrue((ROOT / row["raw_output_dir"]).is_dir(), row["raw_output_dir"])

    def test_honesty_boundary_prevents_overclaiming(self) -> None:
        boundary = self.report["honesty_boundary"]
        self.assertIn("not a new external architecture family", boundary)
        self.assertIn("real held-out test trajectories", boundary)
        self.assertIn("conservation item is a reference-relative diagnostic", boundary)
        self.assertIn("No PhysicsNeMo/EchoWave checkpoint is claimed.", self.report["claim_limitations"])


if __name__ == "__main__":
    unittest.main()
