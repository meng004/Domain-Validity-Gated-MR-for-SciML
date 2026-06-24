"""Regression guard for the closed-form operator-floor bound (C32).

Pins the analytic-bound artifact and the manuscript claim that the
measurement-floor gate is closed-form (predicted + rigorously bounded) for the
concrete deployed-scale mesh, not merely empirically estimated.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/operator-floor-analytic-bound/operator_floor_analytic_bound_report.json"
TOOL = ROOT / "tools/run_operator_floor_analytic_bound.py"
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
IST_MAIN = ROOT / "submissions/IST/main.tex"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


class OperatorFloorAnalyticBoundTest(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(REPORT.exists(), "analytic-bound report missing")
        self.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_report_shape_and_levels(self) -> None:
        self.assertEqual(self.report["experiment_id"], "E2b-operator-floor-analytic-bound")
        self.assertEqual(self.report["deployed_level"], "h0")
        self.assertGreaterEqual(len(self.report["levels"]), 3)

    def test_predictor_matches_measured_floor(self) -> None:
        deployed = self.report["levels"][0]
        # Closed-form leading-order predictor matches the measured floor at h0.
        self.assertLess(abs(deployed["predictor_ratio_meas_over_pred"] - 1.0), 0.05)
        # Ratio -> 1 as the mesh refines (governed by the closed-form expansion).
        ratios = [lv["predictor_ratio_meas_over_pred"] for lv in self.report["levels"]]
        self.assertLess(abs(ratios[-1] - 1.0), abs(ratios[0] - 1.0) + 1e-9)

    def test_bound_dominates_measured_floor_everywhere(self) -> None:
        for lv in self.report["levels"]:
            self.assertTrue(lv["bound_dominates_rms"], lv)
            self.assertTrue(lv["bound_dominates_pointwise"], lv)
            self.assertGreaterEqual(lv["bound_rms"], lv["measured_floor_rms"])

    def test_verdict_is_closed_form(self) -> None:
        v = self.report["verdict"]
        self.assertTrue(v["predictor_matches_measured"])
        self.assertTrue(v["bound_dominates_measured"])
        self.assertTrue(v["closed_form_floor_available_for_concrete_mesh"])
        self.assertEqual(v["general_unstructured_bound"], "future work")

    def test_artifact_is_reproducible(self) -> None:
        # Re-run the tool and confirm the deployed-level numbers are stable.
        before = json.dumps(self.report["levels"][0], sort_keys=True)
        subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(ROOT),
                       capture_output=True)
        after = json.loads(REPORT.read_text(encoding="utf-8"))["levels"][0]
        self.assertEqual(before, json.dumps(after, sort_keys=True))

    def test_ledger_has_c32_claim(self) -> None:
        ledger = LEDGER.read_text(encoding="utf-8")
        self.assertIn("C32-operator-floor-analytic-bound", ledger)

    def test_manuscript_states_closed_form_floor(self) -> None:
        for text in (MANUSCRIPT.read_text(encoding="utf-8"), IST_MAIN.read_text(encoding="utf-8")):
            self.assertTrue(
                re.search(r"closed[- ]form", text, re.I),
                "manuscript/ist must state the closed-form operator floor",
            )
        # The stale "closed-form bound left to future work" phrasing must be gone
        # from the measurement-floor contribution.
        man = MANUSCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("with a closed-form bound left to future work", man)


if __name__ == "__main__":
    unittest.main()
