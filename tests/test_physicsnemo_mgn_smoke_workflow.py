"""Guards for the executable PhysicsNeMo MGN Object-A smoke workflow."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-vortex-shedding"
REPORT = RUN_DIR / "physicsnemo_mgn_smoke_workflow_report.json"
RUBRIC = RUN_DIR / "physicsnemo_mgn_smoke_rubric_decisions.json"
SMOKE = RUN_DIR / "physicsnemo_mgn_smoke_manifest.json"
PLAN = ROOT / "docs/superpowers/plans/2026-06-12-production-grade-sut-extension-plan.md"
CLAIMS = ROOT / "research_assets/experiments/claim-ledger.yml"
NEXT = ROOT / "NEXT_STEPS.md"


class PhysicsNeMoMgnSmokeWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.rubric = json.loads(RUBRIC.read_text(encoding="utf-8"))
        cls.smoke = json.loads(SMOKE.read_text(encoding="utf-8"))

    def test_report_records_real_physicsnemo_object_a_smoke_workflow(self) -> None:
        self.assertEqual(self.report["record_type"], "physicsnemo-mgn-smoke-primary-workflow")
        self.assertEqual(self.report["object_id"], "physicsnemo-mgn-vortex-shedding")
        self.assertEqual(self.report["sut_name"], "NVIDIA PhysicsNeMo MeshGraphNet")
        self.assertEqual(self.report["workflow_status"], "completed-smoke-subset")
        self.assertTrue(self.report["task3_minimal_workflow_completed"])
        self.assertFalse(self.report["task3_full_scale_workflow_completed"])
        self.assertIn("first official TFRecord trajectory", self.report["honesty_boundary"])
        self.assertIn("not a full production-scale", self.report["honesty_boundary"])

    def test_artifact_chain_contains_checkpoint_raw_outputs_and_ledgers(self) -> None:
        artifacts = self.report["artifacts"]
        for key in ("checkpoint", "raw_outputs", "rubric_decisions", "smoke_manifest"):
            self.assertTrue((ROOT / artifacts[key]).exists(), key)
        for relpath in artifacts["metric_ledgers"].values():
            self.assertTrue((ROOT / relpath).exists(), relpath)
        self.assertEqual(self.smoke["checkpoint_path"], artifacts["checkpoint"])
        self.assertEqual(self.smoke["raw_outputs"], artifacts["raw_outputs"])
        self.assertGreater((ROOT / artifacts["checkpoint"]).stat().st_size, 10_000)
        self.assertGreater((ROOT / artifacts["raw_outputs"]).stat().st_size, 1_000)

    def test_relation_verdicts_and_metrics_are_bounded(self) -> None:
        metrics = self.report["metrics"]
        self.assertEqual(self.report["relation_verdicts"]["node_permutation"], "pass")
        self.assertLessEqual(metrics["node_permutation_relative_l2"], 1e-5)
        self.assertGreaterEqual(metrics["rollout_relative_l2"], 0.0)
        self.assertGreaterEqual(metrics["mirror_ood_stress_relative_l2"], 0.0)
        self.assertGreaterEqual(metrics["reference_relative_conservation_ratio"], 0.0)
        self.assertIn("node_permutation_equivariance", self.rubric["admitted_relations"])
        self.assertIn("mirror_y_ood_stress", self.rubric["downgraded_relations"])

    def test_plan_next_steps_and_claim_ledger_do_not_overclaim(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")
        claims = CLAIMS.read_text(encoding="utf-8")
        next_steps = NEXT.read_text(encoding="utf-8")
        self.assertIn("Task 3 execution note", plan)
        self.assertIn("PhysicsNeMo MeshGraphNet CPU smoke workflow", plan)
        self.assertIn("Task 4--5 remain blocked", plan)
        self.assertIn("C29-physicsnemo-mgn-smoke-workflow", claims)
        self.assertIn("not yet a full production-scale PhysicsNeMo benchmark", claims)
        self.assertIn("AeroGraphNet workflow result", claims)
        self.assertIn("Task 3 minimal Object-A smoke workflow", next_steps)
        self.assertIn("Task 4-5 仍 blocked", next_steps)


if __name__ == "__main__":
    unittest.main()
