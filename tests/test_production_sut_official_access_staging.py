"""Guards for P0c official source/access staging after runtime preflight."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research_assets/runs/production-grade-sut-extension"
REPORT = BASE / "official_access_staging_report.json"
PLAN = ROOT / "docs/superpowers/plans/2026-06-12-production-grade-sut-extension-plan.md"
NEXT = ROOT / "NEXT_STEPS.md"
CLAIM_LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


class ProductionSutOfficialAccessStagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_records_all_three_selected_objects(self) -> None:
        self.assertEqual(self.report["record_type"], "production-sut-official-access-staging-report")
        self.assertEqual(self.report["aggregate_status"], "blocked-official-access-incomplete")
        self.assertEqual(
            {item["object_id"] for item in self.report["objects"]},
            {
                "physicsnemo-mgn-vortex-shedding",
                "physicsnemo-aerographnet-external-aero",
                "physicsnemo-domino-external-aero",
            },
        )
        self.assertFalse(self.report["task3_to_task5_workflows_allowed"])

    def test_mgn_official_data_archives_are_staged_but_checkpoint_is_missing(self) -> None:
        mgn = self.report["objects_by_id"]["physicsnemo-mgn-vortex-shedding"]
        self.assertTrue(mgn["official_doc_reachable"])
        self.assertTrue(mgn["ngc_cylinder_flow_archive"]["local_archive_exists"])
        self.assertGreater(mgn["ngc_cylinder_flow_archive"]["local_archive_bytes"], 1_000_000_000)
        self.assertEqual(mgn["ngc_cylinder_flow_archive"]["nested_entries"], ["dataset.zip"])
        self.assertTrue(mgn["deepmind_tfrecord_bundle_complete"])
        self.assertGreater(mgn["deepmind_tfrecord_observed_bytes"], 16_000_000_000)
        self.assertFalse(mgn["checkpoint_or_api_staged"])
        self.assertNotIn("complete_deepmind_tfrecord_bundle", mgn["missing_for_workflow"])
        self.assertIn("official_or_new_physicsnemo_checkpoint", mgn["missing_for_workflow"])

    def test_external_aero_objects_record_access_blockers_not_results(self) -> None:
        aero = self.report["objects_by_id"]["physicsnemo-aerographnet-external-aero"]
        domino = self.report["objects_by_id"]["physicsnemo-domino-external-aero"]
        self.assertEqual(aero["access_status"], "blocked-access-request-required")
        self.assertIn("NVIDIA PhysicsNeMo team", aero["blocker_reason"])
        self.assertEqual(domino["access_status"], "blocked-ngc-auth-and-gpu-container-required")
        self.assertIn("NGC API key", domino["blocker_reason"])
        self.assertFalse(aero["raw_outputs_available"])
        self.assertFalse(domino["metric_ledgers_available"])

    def test_plan_next_steps_and_claim_ledger_are_fail_closed(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")
        next_steps = NEXT.read_text(encoding="utf-8")
        claims = CLAIM_LEDGER.read_text(encoding="utf-8")
        self.assertIn("Task 2.8", plan)
        self.assertIn("complete official DeepMind TFRecord data", plan)
        self.assertIn("Task 2.8 complete DeepMind TFRecord staging", next_steps)
        self.assertIn("official_access_staging_report.json", claims)
        self.assertIn("No full-scale production MR has been executed", claims)
        self.assertIn("Do not claim full-scale PhysicsNeMo/AeroGraphNet/DoMINO primary workflow results", claims)


if __name__ == "__main__":
    unittest.main()
