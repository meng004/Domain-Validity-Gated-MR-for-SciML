"""P0 guard for the independent periodic-advection primary workflow."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "research_assets/runs/periodic-advection-primary-workflow/"
    / "periodic_advection_primary_workflow_report.json"
)
PLAN = ROOT / "paper/82_p0_independent_primary_sut_scan_plan.md"
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
JSS_MAIN = ROOT / "manuscript/main.tex"
CLAIM_LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


class P0PeriodicAdvectionPrimaryWorkflowTest(unittest.TestCase):
    def test_report_has_full_rubric_to_verdict_chain(self) -> None:
        self.assertTrue(REPORT.exists(), "missing periodic-advection workflow report")
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["record_type"], "periodic-advection-primary-workflow")
        self.assertEqual(report["task"], "2D scalar periodic advection")
        self.assertEqual(report["architecture_family"], "NumPy periodic convolution surrogate")
        self.assertEqual(report["trained_sut_count"], 6)
        self.assertEqual(report["n_eval_per_sut"], 10)
        self.assertEqual(report["seeds"], [0, 1, 2, 3, 4, 5])

        for key in (
            "trained_checkpoints",
            "rubric_decisions",
            "source_followup_outputs",
            "metric_ledgers",
            "relation_verdicts",
        ):
            self.assertTrue(report["full_workflow_flags"][key], key)

        translation = report["periodic_translation"]
        self.assertEqual(translation["admissibility"], "admitted")
        self.assertEqual(translation["total_case_cells"], 60)
        self.assertEqual(translation["pass_count"], 60)
        self.assertEqual(translation["fail_count"], 0)
        self.assertLessEqual(translation["max_violation"], translation["threshold"])

        mass = report["periodic_mass_conservation"]
        self.assertEqual(mass["admissibility"], "admitted")
        self.assertEqual(mass["total_case_cells"], 60)
        self.assertEqual(mass["pass_count"], 60)
        self.assertEqual(mass["fail_count"], 0)
        self.assertLessEqual(mass["max_rms_normalized_mean_drift"], mass["threshold"])

        rejected = report["fixed_velocity_mirror_rejection"]
        self.assertEqual(rejected["admissibility"], "rejected")
        self.assertEqual(rejected["rejected_count"], 6)
        self.assertEqual(rejected["executed_as_exact_mr_count"], 0)

        self.assertIn("full rubric-to-verdict", report["honesty_boundary"])
        self.assertIn("not CFD evidence", report["honesty_boundary"])
        for sut in report["per_sut"]:
            self.assertTrue((ROOT / sut["metric_ledger"]).exists())
            self.assertTrue((ROOT / sut["rubric_decisions"]).exists())
            self.assertTrue((ROOT / sut["checkpoint"]).exists())

    def test_plan_and_manuscript_bind_the_claim_boundary(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")
        md = MANUSCRIPT.read_text(encoding="utf-8")
        tex = JSS_MAIN.read_text(encoding="utf-8")
        ledger = CLAIM_LEDGER.read_text(encoding="utf-8")

        self.assertIn("2D periodic scalar advection surrogate", plan)
        self.assertIn("Candidate Scan", plan)
        self.assertIn("C54-periodic-advection-primary-workflow", ledger)
        self.assertIn("periodic_advection_primary_workflow_report.json", ledger)
        required_markers = [
            "periodic-advection primary workflow",
            "60/60 translation passes",
            "60/60 mass-conservation passes",
            "fixed-velocity mirror candidate is rejected",
            "not production CFD or real-defect evidence",
        ]
        for text in (md, tex):
            for marker in required_markers:
                self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
