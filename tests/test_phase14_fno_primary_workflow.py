"""Phase 14 guards for promoting FNO to a full primary workflow."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/fno-primary-workflow/fno_primary_workflow_report.json"
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
IST_MAIN = ROOT / "submissions/IST/main.tex"


class Phase14FnoPrimaryWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.md = MANUSCRIPT.read_text(encoding="utf-8")
        cls.tex = IST_MAIN.read_text(encoding="utf-8")

    def test_fno_primary_workflow_report_has_full_rubric_to_verdict_evidence(self) -> None:
        self.assertTrue(REPORT.exists(), "missing FNO primary workflow report")
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["record_type"], "fno-primary-workflow")
        self.assertEqual(report["architecture_family"], "FNO-2D")
        self.assertEqual(report["pdes"], ["burgers", "heat"])
        self.assertEqual(report["seeds"], [0, 1, 2])
        self.assertEqual(report["trained_sut_count"], 6)
        self.assertEqual(report["n_eval_per_sut"], 4)

        flags = report["full_workflow_flags"]
        for key in (
            "trained_checkpoints",
            "rubric_decisions",
            "source_followup_outputs",
            "metric_ledgers",
            "relation_verdicts",
        ):
            self.assertTrue(flags[key], key)

        translation = report["periodic_translation"]
        self.assertEqual(translation["admissibility"], "admitted")
        self.assertEqual(translation["total_case_cells"], 24)
        self.assertEqual(translation["pass_count"], 24)
        self.assertLess(translation["max_violation"], 1e-5)

        conservation = report["periodic_discrete_conservation"]
        self.assertEqual(conservation["admissibility"], "admitted-with-reference-floor")
        self.assertEqual(conservation["total_case_cells"], 24)
        self.assertEqual(conservation["fail_count"], 24)
        self.assertLessEqual(conservation["reference_floor_max"], 0.05)
        self.assertIn("not deferred", conservation["honesty_boundary"])

        rejected = report["dirichlet_translation_rejection"]
        self.assertEqual(rejected["rejected_count"], 6)
        self.assertEqual(rejected["executed_as_exact_mr_count"], 0)

        self.assertIn("full rubric-to-verdict", report["honesty_boundary"])
        self.assertNotIn("admissibility evidence only", report["honesty_boundary"])

    def test_manuscripts_promote_fno_beyond_admissibility_only(self) -> None:
        required_markers = [
            "FNO primary workflow upgrade",
            "periodic discrete-conservation MR",
            "24/24 translation passes",
            "24/24 conservation failures",
            "not only admissibility evidence",
        ]
        for text in (self.md, self.tex):
            for marker in required_markers:
                self.assertIn(marker, text)
            self.assertNotIn("Synthetic-data admissibility evidence only", text)
            self.assertNotIn("synthetic admissibility evidence rather than", text)


if __name__ == "__main__":
    unittest.main()
