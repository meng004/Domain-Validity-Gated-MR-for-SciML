"""Guards for P0c Object A PhysicsNeMo MGN data/checkpoint staging."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research_assets/runs/production-grade-sut-extension"
REPORT = BASE / "physicsnemo_mgn_asset_staging_report.json"
PLAN = ROOT / "docs/superpowers/plans/2026-06-12-production-grade-sut-extension-plan.md"
CLAIM_LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


class PhysicsNeMoMgnAssetStagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_report_records_object_a_asset_staging_attempt(self) -> None:
        self.assertEqual(self.report["record_type"], "physicsnemo-mgn-asset-staging-report")
        self.assertEqual(self.report["object_id"], "physicsnemo-mgn-vortex-shedding")
        self.assertEqual(self.report["aggregate_status"], "blocked-assets-incomplete")
        self.assertTrue(self.report["official_data_source"]["public_gcs_url_prefix"].startswith("https://storage.googleapis.com/"))
        self.assertTrue(self.report["download_attempted"])

    def test_official_data_is_not_complete_enough_for_workflow(self) -> None:
        data = self.report["data_staging"]
        self.assertFalse(data["official_data_staged"])
        self.assertFalse(data["all_required_files_present"])
        self.assertIn("valid.tfrecord", data["missing_required_files"])
        self.assertIn("test.tfrecord", data["missing_required_files"])
        self.assertGreaterEqual(data["observed_bytes"], 0)
        self.assertIn("large", self.report["blocker_reason"].lower())

    def test_checkpoint_raw_outputs_and_ledgers_remain_absent(self) -> None:
        self.assertFalse(self.report["checkpoint_staging"]["official_checkpoint_staged"])
        self.assertFalse(self.report["raw_outputs_available"])
        self.assertFalse(self.report["metric_ledgers_available"])
        self.assertFalse(self.report["task3_workflow_execution_allowed"])
        self.assertIn("official_checkpoint", self.report["missing_for_task3"])
        self.assertIn("complete_official_data", self.report["missing_for_task3"])

    def test_plan_and_claim_ledger_record_blocker_without_claiming_results(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")
        self.assertIn("Task 2.6 execution note", plan)
        self.assertIn("official cylinder_flow data download was attempted", plan)
        self.assertIn("- [ ] Implement `tools/run_physicsnemo_mgn_primary_workflow.py`.", plan)
        claim_text = CLAIM_LEDGER.read_text(encoding="utf-8")
        self.assertIn("PhysicsNeMo MGN data/checkpoint staging", claim_text)
        self.assertIn("attempted", claim_text)
        self.assertIn("No production MR has been", claim_text)
        self.assertIn("executed", claim_text)


if __name__ == "__main__":
    unittest.main()
