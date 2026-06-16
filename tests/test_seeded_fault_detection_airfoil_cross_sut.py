"""Guard for the cross-SUT seeded-fault replication (claim C36).

Pins the honest negative finding: the by-class fault-localization pattern observed
on the cylinder SUT does NOT replicate on the primary-scale PhysicsNeMo airfoil.
Only the gross normalization fault is robustly detected across trajectories,
mirror-y is domain-inadmissible (gate-excluded), and the single localization shared
across SUTs is continuity -> normalization-scale faults. This prevents manuscript
prose from claiming the by-class diagnostic generalizes across SUTs.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = (
    ROOT
    / "research_assets/runs/production-grade-sut-extension"
    / "physicsnemo-mgn-airfoil-seeded-fault-detection/raw/metric_ledger.json"
)


class AirfoilSeededFaultCrossSutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_five_trajectory_scope(self) -> None:
        self.assertEqual(self.d["robustness"]["n_trajectories"], 5)
        self.assertEqual(len(self.d["per_trajectory"]), 5)

    def test_only_gross_normalization_fault_robustly_detected(self) -> None:
        rob = self.d["robustness"]
        # The by-class pattern does NOT replicate: only NS_skip_denorm is detected
        # on every trajectory; node-permutation detects nothing.
        self.assertEqual(rob["robustly_detected_mutants"], ["NS_skip_denorm"])
        self.assertEqual(rob["node_permutation_MR_detection_rate"], 0.0)
        self.assertEqual(set(rob["unstable_mutants"]), {"NS_double_scale", "TR_double_step"})

    def test_seven_fault_classes_never_detected(self) -> None:
        never = set(self.d["robustness"]["never_detected_mutants"])
        self.assertEqual(never, {
            "BC_zero_outflow", "BC_nonzero_wall", "MA_drop_edges", "MA_permute_edges",
            "TR_sign_flip", "PC_swap_xy", "PC_zero_vy"})

    def test_mirror_y_domain_inadmissible(self) -> None:
        self.assertEqual(self.d["detectors"]["mirror_y_symmetry"]["status"], "inadmissible")
        self.assertEqual(self.d["cross_sut_comparison"]["mirror_y_status_on_airfoil"], "inadmissible")

    def test_only_normalization_localization_shared_across_suts(self) -> None:
        x = self.d["cross_sut_comparison"]
        self.assertEqual(self.d["robustness"]["conservation_robustly_localizes"],
                         ["normalization_scale_fault"])
        self.assertEqual(x["shared_localization_across_suts"], ["normalization_scale_fault"])
        # The cylinder localized to boundary+normalization; the airfoil does not
        # reproduce the boundary arm, so the mapping is SUT-specific.
        self.assertIn("boundary_condition_fault", x["cylinder_conservation_localizes"])
        self.assertNotIn("boundary_condition_fault",
                         x["airfoil_conservation_robustly_localizes"])


if __name__ == "__main__":
    unittest.main()
