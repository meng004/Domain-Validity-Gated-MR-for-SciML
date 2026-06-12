"""Guards for the P0c PhysicsNeMo runtime staging gate."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research_assets/runs/production-grade-sut-extension"
REPORT = BASE / "physicsnemo_runtime_staging_report.json"
PLAN = ROOT / "docs/superpowers/plans/2026-06-12-production-grade-sut-extension-plan.md"
CLAIM_LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"
OBJECT_IDS = {
    "physicsnemo-mgn-vortex-shedding",
    "physicsnemo-aerographnet-external-aero",
    "physicsnemo-domino-external-aero",
}


class PhysicsNeMoRuntimeStagingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.objects = {item["object_id"]: item for item in cls.report["objects"]}

    def test_runtime_package_is_staged_but_not_workflow_ready(self) -> None:
        self.assertEqual(self.report["record_type"], "physicsnemo-runtime-staging-report")
        self.assertEqual(self.report["aggregate_status"], "partial-runtime-staged")
        runtime = self.report["runtime"]
        self.assertTrue(runtime["physicsnemo_importable"])
        self.assertTrue(runtime["torch_importable"])
        self.assertTrue(runtime["torchvision_importable"])
        self.assertFalse(runtime["cuda_available"])
        self.assertFalse(self.report["workflow_execution_allowed"])

    def test_core_import_probes_cover_selected_production_objects(self) -> None:
        probes = {item["module"]: item for item in self.report["import_probes"]}
        for module in (
            "physicsnemo",
            "physicsnemo.models.meshgraphnet",
            "physicsnemo.datapipes.gnn.vortex_shedding_dataset",
            "physicsnemo.datapipes.cae.domino_datapipe",
        ):
            self.assertIn(module, probes)
            self.assertEqual(probes[module]["returncode"], 0, probes[module])
            self.assertEqual(probes[module]["status"], "ok")

    def test_each_object_remains_blocked_by_assets_after_runtime_staging(self) -> None:
        self.assertEqual(set(self.objects), OBJECT_IDS)
        for object_id, obj in self.objects.items():
            self.assertTrue(obj["runtime_import_ready"], object_id)
            self.assertFalse(obj["official_data_staged"], object_id)
            self.assertFalse(obj["official_checkpoint_staged"], object_id)
            self.assertFalse(obj["raw_outputs_available"], object_id)
            self.assertFalse(obj["metric_ledgers_available"], object_id)
            self.assertFalse(obj["workflow_execution_allowed"], object_id)
            self.assertIn("official_data", obj["missing_for_workflow"])
            self.assertIn("official_checkpoint", obj["missing_for_workflow"])

    def test_official_example_sources_are_reachable_or_recorded(self) -> None:
        for obj in self.objects.values():
            self.assertTrue(obj["official_doc_url"].startswith("https://docs.nvidia.com/"))
            self.assertTrue(obj["github_example_url"].startswith("https://github.com/NVIDIA/physicsnemo/"))
            source_probe = obj["github_source_probe"]
            self.assertTrue(source_probe["checked"])
            self.assertIn(source_probe["reachable"], {True, False})

    def test_plan_and_claim_ledger_record_runtime_staging_without_advancing_task3(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")
        self.assertIn("Task 2.5 execution note", plan)
        self.assertIn("PhysicsNeMo package/runtime import gate is now partially staged", plan)
        self.assertIn("- [ ] Implement `tools/run_physicsnemo_mgn_primary_workflow.py`.", plan)
        claim_text = CLAIM_LEDGER.read_text(encoding="utf-8")
        self.assertIn("PhysicsNeMo package/runtime import gate", claim_text)
        self.assertIn("is now partially staged", claim_text)
        self.assertIn("No production MR has been", claim_text)
        self.assertIn("executed", claim_text)


if __name__ == "__main__":
    unittest.main()
