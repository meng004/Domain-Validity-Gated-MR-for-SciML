"""Guards for the scaled PhysicsNeMo MGN primary workflow (P0c Task-4 upgrade).

The scaled workflow must stay an honest multi-trajectory CPU evaluation of the
official production architecture: per-trajectory denominators, committed metric
ledgers and raw outputs, an explicit honesty boundary, and no claim widening
beyond what the report supports.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-vortex-shedding-scaled"
REPORT = OUT / "physicsnemo_mgn_scaled_workflow_report.json"
RUBRIC = OUT / "physicsnemo_mgn_scaled_rubric_decisions.json"
CHECKPOINT = OUT / "physicsnemo_mgn_scaled_checkpoint.pt"
MANUSCRIPT = ROOT / "manuscript/manuscript.md"

LEDGERS = [
    "rollout_accuracy_metric_ledger.json",
    "node_permutation_metric_ledger.json",
    "mirror_ood_stress_metric_ledger.json",
    "conservation_reference_relative_metric_ledger.json",
]


class PhysicsNemoScaledWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text())
        cls.ledgers = {name: json.loads((OUT / name).read_text()) for name in LEDGERS}

    def test_artifacts_exist(self):
        self.assertTrue(REPORT.exists())
        self.assertTrue(RUBRIC.exists())
        self.assertTrue(CHECKPOINT.exists())
        raw = list((OUT / "raw_outputs").glob("trajectory_*_followup_outputs.npz"))
        self.assertGreaterEqual(len(raw), 1)

    def test_official_production_architecture(self):
        arch = self.report["architecture"]
        self.assertEqual(arch["processor_size"], 15)
        self.assertEqual(arch["hidden_dim"], 128)
        self.assertTrue(arch["official_default"])
        self.assertGreater(arch["n_parameters"], 2_000_000)

    def test_multi_trajectory_denominators(self):
        n = self.report["evaluation"]["n_test_trajectories"]
        self.assertGreaterEqual(n, 20)
        self.assertEqual(self.ledgers["node_permutation_metric_ledger.json"]["denominator"], n)
        self.assertEqual(self.ledgers["mirror_ood_stress_metric_ledger.json"]["denominator"], n)
        self.assertGreaterEqual(self.ledgers["rollout_accuracy_metric_ledger.json"]["denominator"], n)
        for name in LEDGERS:
            rows = self.ledgers[name]["rows"]
            self.assertEqual(len(rows), self.ledgers[name]["denominator"])

    def test_node_permutation_is_exact(self):
        led = self.ledgers["node_permutation_metric_ledger.json"]
        self.assertEqual(led["passes"], led["denominator"])
        self.assertLessEqual(led["max_relative_l2"], led["threshold"])
        self.assertEqual(led["verdict"], "pass")

    def test_mirror_is_recorded_as_ood_stress_not_pass(self):
        led = self.ledgers["mirror_ood_stress_metric_ledger.json"]
        self.assertEqual(led["verdict"], "fail-as-ood-stress")
        self.assertLess(led["passes"], led["denominator"])

    def test_honesty_boundary_and_forbidden_claims(self):
        hb = self.report["honesty_boundary"]
        for needle in ("CPU-scale", "NOT the official 10M-step training schedule",
                       "NOT an official NVIDIA checkpoint", "one-step"):
            self.assertIn(needle, hb)
        forbidden = " ".join(self.report["forbidden_claims"])
        for needle in ("official-checkpoint behaviour", "full production-benchmark",
                       "cross-dataset reliability"):
            self.assertIn(needle, forbidden)

    def test_data_is_official_deepmind_source(self):
        data = self.report["data"]
        self.assertIn("dm-meshgraphnets/cylinder_flow", data["source_url_prefix"])
        splits = {r["split"]: r for r in data["records"]}
        self.assertGreaterEqual(splits["train"]["n_records"], 20)
        self.assertGreaterEqual(splits["test"]["n_records"], 20)

    def test_manuscript_mentions_scaled_workflow_within_boundary(self):
        text = MANUSCRIPT.read_text()
        self.assertIn("PhysicsNeMo", text)
        # The scaled production-architecture numbers must appear.
        self.assertIn("2.33M parameters", text)
        self.assertIn("40/40", text)
        # The manuscript must keep the official-checkpoint hedge.
        self.assertNotIn("official NVIDIA checkpoint reproduces", text)
        self.assertIn("not an official NVIDIA checkpoint", text)


if __name__ == "__main__":
    unittest.main()
