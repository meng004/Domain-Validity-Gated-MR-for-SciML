"""TDD guards for the P0c production-grade SUT feasibility audit."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/production-grade-sut-extension/feasibility_report.json"
PLAN = ROOT / "docs/superpowers/plans/2026-06-12-production-grade-sut-extension-plan.md"
CLAIM_LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"

EXPECTED_OBJECTS = {
    "physicsnemo-mgn-vortex-shedding": "PhysicsNeMo MeshGraphNet transient vortex shedding",
    "physicsnemo-aerographnet-external-aero": "PhysicsNeMo AeroGraphNet external aerodynamic evaluation",
    "physicsnemo-domino-external-aero": "PhysicsNeMo DoMINO external aerodynamics",
}


class ProductionSutFeasibilityPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.objects = {entry["object_id"]: entry for entry in cls.report["objects"]}

    def test_report_records_three_selected_production_objects(self) -> None:
        self.assertEqual(self.report["record_type"], "production-grade-sut-feasibility-audit")
        self.assertEqual(set(self.objects), set(EXPECTED_OBJECTS))
        self.assertEqual(self.report["scope"], "P0c production-grade external SciML/CFD SUT feasibility")
        self.assertEqual(self.report["selection_standard"], "argument-function-first")
        self.assertFalse(self.report["manuscript_result_claim_added"])

    def test_each_object_has_official_provenance_and_smoke_attempt(self) -> None:
        for object_id, expected_name in EXPECTED_OBJECTS.items():
            obj = self.objects[object_id]
            self.assertEqual(obj["name"], expected_name)
            self.assertEqual(obj["provenance"], "NVIDIA PhysicsNeMo official example")
            self.assertTrue(obj["official_url"].startswith("https://docs.nvidia.com/"), object_id)
            self.assertIn(obj["status"], {"ready", "partial", "blocked"})
            self.assertIn("version_probe", obj)
            self.assertIn("smoke_attempt", obj)
            smoke = obj["smoke_attempt"]
            self.assertTrue(smoke["attempted"], object_id)
            self.assertIn(smoke["outcome"], {"passed", "blocked", "failed"})
            self.assertNotEqual(smoke["outcome"], "passed", "Do not pass without raw production outputs")
            self.assertNotIn("toy", " ".join(obj.get("fallback_policy", [])).lower())

    def test_artifact_gate_blocks_claims_until_raw_outputs_exist(self) -> None:
        for obj in self.objects.values():
            gate = obj["artifact_gate"]
            self.assertFalse(gate["workflow_claim_allowed"])
            self.assertEqual(gate["claim_state"], "blocked")
            self.assertFalse(gate["raw_outputs_available"])
            self.assertFalse(gate["metric_ledgers_available"])
            self.assertIn("blocked rather than replaced", obj["fallback_policy"])
        self.assertEqual(self.report["aggregate_status"], "blocked")

    def test_plan_task1_checkboxes_are_updated_without_advancing_result_tasks(self) -> None:
        text = PLAN.read_text(encoding="utf-8")
        for marker in (
            "- [x] Create `tools/audit_production_sut_feasibility.py`.",
            "- [x] Create `tests/test_production_sut_feasibility_plan.py`.",
            "- [x] Attempt official minimal inference smoke test for PhysicsNeMo MeshGraphNet transient vortex shedding.",
            "- [x] Attempt official minimal inference smoke test for PhysicsNeMo AeroGraphNet.",
            "- [x] Attempt official minimal inference smoke test for PhysicsNeMo DoMINO.",
            "- [x] Write `research_assets/runs/production-grade-sut-extension/feasibility_report.json`.",
        ):
            self.assertIn(marker, text)
        self.assertIn("### Task 3 — PhysicsNeMo MeshGraphNet workflow", text)
        self.assertIn("- [ ] Implement `tools/run_physicsnemo_mgn_primary_workflow.py`.", text)

    def test_claim_ledger_only_adds_blocked_feasibility_entry(self) -> None:
        text = CLAIM_LEDGER.read_text(encoding="utf-8")
        self.assertIn("C28-production-sut-feasibility-audit", text)
        self.assertIn("status: blocked", text)
        self.assertIn("Production workflows have not produced raw outputs yet", text)
        self.assertIn("Do not claim PhysicsNeMo/AeroGraphNet/DoMINO primary workflow results", text)


if __name__ == "__main__":
    unittest.main()
