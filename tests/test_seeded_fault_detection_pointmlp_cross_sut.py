"""Guard for PointMLP cross-architecture seeded-fault detection (claim C41, MVP-A).

Pins that the paper's three domain-validity MR detectors, run with their predeclared
thresholds on the converged row-wise PointMLP cylinder SUT, reproduce the MeshGraphNets
"about half the catalogue, localized by MR family" reading on a SECOND architecture family,
while honestly recording the two mesh-adjacency mutants as not-applicable (no-ops on a
row-wise network) rather than as detector misses. Prevents prose from overclaiming a
proven cross-architecture generalization.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research_assets/runs/pointmlp-cylinder-seeded-fault-detection/raw/metric_ledger.json"
MGN_LEDGER = ROOT / "research_assets/runs/seeded-fault-detection/raw/metric_ledger.json"


class PointMLPSeededFaultCrossSutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.s = cls.d["summary"]

    def test_converged_sut_and_aligned_thresholds(self) -> None:
        # iron rule: comparisons only on a converged SUT
        self.assertLess(self.d["rollout_convergence"]["median_relative_l2"], 0.05)
        self.assertTrue(self.d["thresholds_aligned_to_mgn"])
        self.assertEqual(self.d["detectors"]["node_permutation_equivariance"]["tolerance"], 1e-5)
        self.assertEqual(
            self.d["detectors"]["conservation_divergence"]["reference_relative_regression_threshold"], 1.5)
        self.assertEqual(
            self.d["detectors"]["mirror_y_ood_stress"]["relative_change_detection_threshold"], 0.5)

    def test_applicable_and_not_applicable_split(self) -> None:
        self.assertEqual(self.s["num_mutants_total"], 10)
        self.assertEqual(self.s["num_applicable_mutants"], 8)
        self.assertEqual(self.s["num_not_applicable_mutants"], 2)
        self.assertEqual(set(self.s["not_applicable_mutants"]),
                         {"MA_drop_edges", "MA_permute_edges"})
        # the two mesh-adjacency mutants are recorded not-applicable with a reason, not as misses
        na = [d for d in self.d["detection_matrix"] if not d.get("applicable")]
        self.assertEqual(len(na), 2)
        for d in na:
            self.assertEqual(d["fault_class"], "mesh_adjacency_fault")
            self.assertIn("no-op", d["not_applicable_reason"])
            self.assertNotIn("detected_by_any", d)

    def test_detection_rates_pinned(self) -> None:
        self.assertEqual(self.s["union_detected_count_over_applicable"], [4, 8])
        self.assertEqual(self.s["union_detection_rate"], 0.5)
        self.assertEqual(self.s["node_permutation_MR_detection_rate"], 0.0)
        self.assertEqual(self.s["conservation_MR_detection_rate"], 0.5)
        self.assertEqual(self.s["mirror_y_MR_detection_rate"], 0.25)
        detected = sorted(d["mutant"] for d in self.d["detection_matrix"]
                          if d.get("applicable") and d["detected_by_any"])
        self.assertEqual(detected,
                         ["BC_nonzero_wall", "BC_zero_inflow", "NS_skip_denorm", "PC_swap_xy"])

    def test_by_class_localization_matches_mgn_on_shared_classes(self) -> None:
        mgn = json.loads(MGN_LEDGER.read_text(encoding="utf-8"))["summary"]
        # node-permutation localizes nothing on either architecture (row-wise => exact)
        self.assertEqual(self.s["fault_classes_localized_by_node_permutation"], [])
        self.assertEqual(mgn["fault_classes_localized_by_node_permutation"], [])
        # exact PointMLP by-class sets (pinned to real data)
        self.assertEqual(self.s["fault_classes_localized_by_conservation"],
                         ["boundary_condition_fault", "normalization_scale_fault",
                          "physical_channel_fault"])
        self.assertEqual(self.s["fault_classes_localized_by_mirror_y"],
                         ["normalization_scale_fault", "physical_channel_fault"])
        # SHARED / reproduced classes across both architectures:
        #   conservation -> boundary + normalization-scale; mirror-y -> physical-channel.
        self.assertTrue({"boundary_condition_fault", "normalization_scale_fault"}.issubset(
            set(self.s["fault_classes_localized_by_conservation"])))
        self.assertTrue({"boundary_condition_fault", "normalization_scale_fault"}.issubset(
            set(mgn["fault_classes_localized_by_conservation"])))
        self.assertIn("physical_channel_fault", self.s["fault_classes_localized_by_mirror_y"])
        self.assertIn("physical_channel_fault", mgn["fault_classes_localized_by_mirror_y"])
        # architecture-specific: mesh-adjacency is MGN-only (it is N/A on row-wise PointMLP)
        self.assertIn("mesh_adjacency_fault", mgn["fault_classes_localized_by_mirror_y"])
        self.assertNotIn("mesh_adjacency_fault", self.s["fault_classes_localized_by_conservation"]
                         + self.s["fault_classes_localized_by_mirror_y"])

    def test_comparison_to_mgn_is_a_reproduction_not_generalization(self) -> None:
        c = self.d["comparison_to_mgn"]
        self.assertTrue(c["node_permutation_zero_on_both"])
        self.assertEqual(c["pointmlp_union_detection_rate_over_applicable"], 0.5)
        # the MGN reference is the committed 5/10 result
        self.assertTrue(MGN_LEDGER.exists())
        self.assertEqual(c["mgn_union_detection_rate_over_10"], 0.5)
        self.assertIn("reproduce", c["interpretation"].lower())
        self.assertIn("not prove it generalizes", c["interpretation"].lower())

    def test_reproduction_provenance_present(self) -> None:
        prov = LEDGER.parent.parent / "PROVENANCE.md"
        self.assertTrue(prov.exists(), f"missing reproduction provenance: {prov}")
        text = prov.read_text(encoding="utf-8")
        self.assertIn("run_seeded_fault_detection_pointmlp.py", text)
        self.assertIn("checkpoint.pt", text)   # the committed input is named

    def test_honesty_boundary_present(self) -> None:
        lim = self.d["claim_limitations"].lower()
        for marker in ("one converged sut", "not a real-world", "baseline-superiority"):
            self.assertIn(marker, lim)


if __name__ == "__main__":
    unittest.main()
