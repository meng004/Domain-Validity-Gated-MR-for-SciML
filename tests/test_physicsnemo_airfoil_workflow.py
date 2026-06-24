"""Guards for the PhysicsNeMo MeshGraphNet second-task (airfoil) workflow.

This second CFD task exists to demonstrate that the SAME four-condition
admissibility predicate yields a DIFFERENT typed inadmissibility structure
because the physics differs: incompressible continuity is rejected here on
physical-basis grounds (compressible flow), whereas on cylinder it is only
deferred at the numerical gate. The guard pins that cross-task contrast and the
honest boundaries, not a production benchmark.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-second-task"
REPORT = OUT / "physicsnemo_mgn_airfoil_workflow_report.json"
RUBRIC = OUT / "physicsnemo_mgn_airfoil_rubric_decisions.json"
CHECKPOINT = OUT / "physicsnemo_mgn_airfoil_checkpoint.pt"
MANUSCRIPT = ROOT / "manuscript/manuscript.md"

LEDGERS = [
    "node_permutation_metric_ledger.json",
    "incompressible_continuity_rejection_ledger.json",
    "compressible_conservation_metric_ledger.json",
    "mirror_y_symmetry_rejection_ledger.json",
    "rollout_accuracy_metric_ledger.json",
]


class AirfoilSecondTaskTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text())
        cls.rubric = json.loads(RUBRIC.read_text())
        cls.ledgers = {n: json.loads((OUT / n).read_text()) for n in LEDGERS}

    def test_artifacts_exist(self):
        self.assertTrue(REPORT.exists() and RUBRIC.exists() and CHECKPOINT.exists())
        self.assertTrue(any((OUT / "raw_outputs").glob("airfoil_test_*.npz")))

    def test_is_a_distinct_second_task_and_dataset(self):
        self.assertIn("airfoil", self.report["task"].lower())
        self.assertIn("compressible", self.report["second_task_contrast_to_cylinder"].lower())
        self.assertIn("dm-meshgraphnets/airfoil", self.report["data"]["source_url_prefix"])
        self.assertEqual(self.report["data"]["simulator"], "su2")

    def test_official_architecture_and_real_denominators(self):
        n = self.report["evaluation"]["n_test_trajectories"]
        self.assertGreaterEqual(n, 8)
        self.assertGreater(self.report["architecture"]["n_parameters"], 100_000)
        for name in ("node_permutation_metric_ledger.json",
                     "compressible_conservation_metric_ledger.json"):
            # Denominator may exceed n_test_trajectories when a K>1 roster is run
            # (denominator = K_checkpoints * n_test_trajectories); require >= n.
            self.assertGreaterEqual(self.ledgers[name]["denominator"], n)

    def test_node_permutation_admitted_and_exact(self):
        led = self.ledgers["node_permutation_metric_ledger.json"]
        self.assertEqual(led["rubric_decision"], "admitted")
        self.assertEqual(led["passes"], led["denominator"])
        self.assertEqual(led["verdict"], "pass")

    def test_incompressible_continuity_rejected_on_physical_basis(self):
        led = self.ledgers["incompressible_continuity_rejection_ledger.json"]
        self.assertEqual(led["verdict"], "rejected-domain-invalid")
        self.assertIn("physical-basis", led["rubric_decision"])
        # the rejection must be grounded in measured material compressibility
        self.assertGreater(led["median_density_max_over_min"], 1.15)
        self.assertIn("compressible", led["rejection_basis"].lower())
        self.assertIn("condition (i)", led["rejection_basis"])

    def test_cross_task_contrast_is_explicit(self):
        c = self.rubric["cross_task_contrast"].lower()
        self.assertIn("deferred", c)
        self.assertIn("rejected", c)
        self.assertIn("cylinder", c)
        struct = self.report["headline_typed_verdict_structure"]
        self.assertIn("admitted", struct["node_permutation_equivariance"])
        self.assertIn("rejected", struct["incompressible_continuity"])

    def test_compressible_conservation_deferred_with_diagnostic(self):
        led = self.ledgers["compressible_conservation_metric_ledger.json"]
        self.assertIn("deferred", led["rubric_decision"])
        self.assertIn("no absolute", led["honesty_boundary"].lower())

    def test_forbidden_claims_and_honesty_boundary(self):
        hb = self.report["honesty_boundary"]
        for needle in ("CPU-scale", "NOT a production-scale", "NOT an official NVIDIA checkpoint"):
            self.assertIn(needle, hb)
        forbidden = " ".join(self.report["forbidden_claims"])
        self.assertIn("production-scale airfoil", forbidden)

    def test_manuscript_mentions_second_task_within_boundary(self):
        text = MANUSCRIPT.read_text()
        self.assertIn("airfoil", text.lower())
        self.assertNotIn("production airfoil benchmark", text)


if __name__ == "__main__":
    unittest.main()
