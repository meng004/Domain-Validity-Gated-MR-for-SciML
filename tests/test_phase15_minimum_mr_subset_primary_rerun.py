"""Phase 15 guards for the Minimum-MR-SubSet primary rerun boundary."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RERUN = ROOT / (
    "research_assets/runs/minimum-mr-subset-primary-rerun/"
    "cylinder-flow-mgn-runtime/abd_witness_report.json"
)
BURGERS_PINN_RERUN = ROOT / (
    "research_assets/runs/minimum-mr-subset-primary-rerun/"
    "burgers2d-pinn-witness/abd_witness_report.json"
)
DIFFUSION_PINN_RERUN = ROOT / (
    "research_assets/runs/minimum-mr-subset-primary-rerun/"
    "diffusion2d-pinn-witness/abd_witness_report.json"
)
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
IST_MAIN = ROOT / "manuscript/main.tex"


class Phase15MinimumMrSubsetPrimaryRerunTest(unittest.TestCase):
    def test_cylinder_flow_witness_rerun_is_primary_runtime_evidence(self) -> None:
        self.assertTrue(RERUN.exists(), "missing Minimum-MR-SubSet primary rerun report")
        report = json.loads(RERUN.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS_WITNESS")
        self.assertEqual(report["runtime_boundary"], "cylinder_flow_mgn_runtime")
        self.assertEqual(report["dataset"], "cylinder-flow-mgn-deepmind")
        self.assertTrue(report["real_runtime_output"])
        self.assertEqual(report["eval_split"], "test")
        self.assertEqual(report["kstar"], 6)
        self.assertEqual(report["fault_classes_active"], 4)
        self.assertEqual(report["max_fault_class_signature_rank"], 2)
        self.assertFalse(report["collapse"])
        self.assertIn("mesh_adjacency_fault", report["inactive_fault_classes"])

    def test_pinn_witness_reruns_are_primary_trained_sut_evidence(self) -> None:
        cases = [
            (BURGERS_PINN_RERUN, "burgers2d_pinn", 4, "ff3eae5b40eb"),
            (DIFFUSION_PINN_RERUN, "diffusion2d_pinn", 5, "b54a6b529aa0"),
        ]
        for path, sut_id, n_r, sha_prefix in cases:
            self.assertTrue(path.exists(), f"missing PINN witness report: {path}")
            report = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "PASS_WITNESS")
            self.assertEqual(report["kind"], "real")
            self.assertEqual(report["label_scope"], "true_fault_class")
            self.assertEqual(report["sut_id"], sut_id)
            self.assertEqual(report["checkpoint_sha256_prefix"], sha_prefix)
            self.assertEqual(report["kstar"], 1)
            self.assertEqual(report["fault_classes_active"], 5)
            self.assertEqual(report["max_fault_class_signature_rank"], 2)
            self.assertEqual(report["n_R"], n_r)
            self.assertEqual(report["m_raw"], 12)
            self.assertTrue(report["collapse"])

    def test_manuscripts_keep_rerun_boundary_honest(self) -> None:
        required = [
            "Minimum-MR-SubSet primary rerun",
            "Minimum-MR-SubSet PINN primary reruns",
            "PASS_WITNESS",
            "kstar = 6",
            "kstar = 1",
            "four active true fault classes",
            "five active true fault classes",
            "not a second architecture or dataset",
            "no cross-SUT rate",
        ]
        for text in (
            MANUSCRIPT.read_text(encoding="utf-8"),
            IST_MAIN.read_text(encoding="utf-8"),
        ):
            for marker in required:
                self.assertTrue(
                    marker in text or marker.replace("_", r"\_") in text,
                    marker,
                )


if __name__ == "__main__":
    unittest.main()
