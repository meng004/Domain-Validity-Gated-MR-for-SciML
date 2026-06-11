"""Phase 5 review-panel gate guards."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/academic-review-panel-phase5-baseurl-v1/review_panel_report.json"
TRIAGE = ROOT / "paper/33_phase5_review_panel_triage.md"
PLAN = ROOT / "paper/32_ist_empirical_80_gap_closure_plan.md"


class Phase5ReviewPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.triage = TRIAGE.read_text(encoding="utf-8")
        cls.plan = PLAN.read_text(encoding="utf-8")

    def test_panel_report_records_five_successful_reviewers(self) -> None:
        self.assertEqual(len(self.report["reviewers_succeeded"]), 5)
        self.assertEqual(self.report["panel_majority_verdict"], "major_revision")
        self.assertEqual(self.report["per_dimension_mean"]["clarity"], 7.0)

    def test_phase5_gate_is_explicitly_not_met(self) -> None:
        self.assertLess(self.report["per_dimension_mean"]["empirical_rigor"], 8.0)
        self.assertLess(self.report["overall_dimension_mean"], 7.8)
        self.assertLess(self.report["accept_probability_mean"], 0.65)
        self.assertIn("not met", self.triage)
        self.assertIn("not-yet-submit", self.triage)

    def test_plan_records_no_submission_pipeline_start(self) -> None:
        self.assertIn("v4 已执行，未达标", self.plan)
        self.assertIn("§11 final submission pipeline 不应启动", self.plan)
        self.assertIn("不能仅靠改写措辞声称达标", self.plan)


if __name__ == "__main__":
    unittest.main()
