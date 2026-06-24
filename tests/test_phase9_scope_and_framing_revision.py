"""Phase 9 guards for empirical-scope and framing revision."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
IST_MAIN = ROOT / "manuscript/main.tex"
AUDIT = ROOT / "research_assets/runs/minimum-mr-subset-external-scope-audit/minimum_mr_subset_scope_audit.json"


class Phase9ScopeAndFramingRevisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.md = MANUSCRIPT.read_text(encoding="utf-8")
        cls.tex = IST_MAIN.read_text(encoding="utf-8")

    def test_external_scope_audit_records_relevant_t2_witnesses(self) -> None:
        self.assertTrue(AUDIT.exists(), "T2 external-scope audit artifact is missing")
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(audit["record_type"], "minimum-mr-subset-external-scope-audit")
        self.assertEqual(audit["source_repo"], "https://github.com/meng004/Minimum-MR-SubSet")
        self.assertEqual(audit["source_head"], "9ef862ec37335b4834d0a1fb38b4b613af702f34")
        self.assertGreaterEqual(audit["external_real_rows"], 70)
        self.assertGreaterEqual(audit["external_true_fault_class_rows"], 20)
        witness_ids = {w["sut_id"] for w in audit["primary_sci_ml_witnesses"]}
        self.assertEqual(
            witness_ids,
            {"cylinder_flow_meshgraphnet", "burgers2d_pinn", "diffusion2d_pinn"},
        )
        for witness in audit["primary_sci_ml_witnesses"]:
            self.assertEqual(witness["status"], "PASS_WITNESS")
            self.assertEqual(witness["label_scope"], "true_fault_class")
            self.assertIn("honesty_boundary", witness)

    def test_manuscripts_surface_external_scope_without_overclaiming(self) -> None:
        for text in (self.md, self.tex):
            self.assertIn("Minimum-MR-SubSet external-scope audit", text)
            self.assertIn("external witness evidence", text)
            self.assertIn("does not add new primary SUT executions to this paper", text)

    def test_llm_baselines_are_secondary_scope_contrasts(self) -> None:
        for text in (self.md, self.tex):
            self.assertIn("Secondary baseline and external-scope audit", text)
            self.assertIn("LLM baselines are secondary exploratory scope contrasts", text)
            self.assertNotIn("expert-MR baseline as primary comparator", text)

    def test_domain_axis_is_framed_as_per_relation_not_calibrated_metric(self) -> None:
        required = [
            "per-relation normalized coordinate",
            "not a cross-relation calibrated metric",
            "cannot be averaged or ranked across MR families",
        ]
        for text in (self.md, self.tex):
            for marker in required:
                self.assertIn(marker, text)

    def test_fault_contribution_is_framed_as_stress_test(self) -> None:
        for text in (self.md, self.tex):
            self.assertIn("seeded-fault diagnostic stress test", text)
            self.assertIn("not a validated localization model", text)


if __name__ == "__main__":
    unittest.main()
