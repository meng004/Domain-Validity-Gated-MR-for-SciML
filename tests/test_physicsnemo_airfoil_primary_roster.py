"""Guard for the primary-scale airfoil roster (claim C35).

Pins the official PhysicsNeMo MeshGraphNet architecture, the K=6 roster shape,
the 40-test-trajectory primary-scale denominators (240 checkpoint-by-trajectory
cells), and the typed-verdict structure, so manuscript prose about the
primary-scale second CFD task cannot drift from the committed evidence.

The bounded pilot (C31, tests/test_physicsnemo_airfoil_workflow.py) is preserved
separately; this test does not touch it.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "research_assets/runs/production-grade-sut-extension"
    / "physicsnemo-mgn-airfoil-primary-roster"
    / "physicsnemo_mgn_airfoil_workflow_report.json"
)


class AirfoilPrimaryRosterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_primary_scale_roster_shape(self) -> None:
        r = self.d["roster"]
        self.assertEqual(r["k_checkpoints"], 6)
        self.assertEqual(r["k_checkpoints_completed"], 6)
        # Primary scale: 40 official test trajectories (vs 10 in the bounded C31 pilot).
        self.assertEqual(self.d["evaluation"]["n_test_trajectories"], 40)

    def test_official_meshgraphnet_architecture(self) -> None:
        a = self.d["architecture"]
        self.assertEqual(a["hidden_dim"], 128)
        self.assertEqual(a["processor_size"], 15)
        # Official-size MGN (~2.3M params) vs the bounded pilot's ~0.33M.
        self.assertGreater(a["n_parameters"], 2_000_000)

    def test_node_permutation_exact_across_full_roster(self) -> None:
        m = self.d["metrics"]
        self.assertEqual(m["node_permutation_passes"], "240/240")
        self.assertEqual(m["node_permutation_max_relative_l2"], 0.0)

    def test_compressible_density_and_reference_conservation(self) -> None:
        m = self.d["metrics"]
        # Compressible flow: density varies substantially across the field.
        self.assertGreater(m["median_density_max_over_min"], 1.5)
        # Reference-relative compressible conservation diagnostic near unity.
        self.assertLess(abs(m["median_compressible_residual_ratio"] - 1.0), 0.2)

    def test_typed_verdict_structure_holds(self) -> None:
        h = self.d["headline_typed_verdict_structure"]
        self.assertIn("admitted", h["node_permutation_equivariance"])
        self.assertIn("rejected", h["incompressible_continuity"])
        self.assertIn("deferred", h["compressible_mass_conservation"])
        self.assertIn("rejected", h["mirror_y_symmetry"])


if __name__ == "__main__":
    unittest.main()
