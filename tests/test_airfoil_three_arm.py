"""Guard for the converged-airfoil three-arm completion (claim C52).

Pins the honest three-arm result on the live converged PhysicsNeMo airfoil SUT:
the accuracy-monitor (arm2) and the ungated-generic gate value (arm3), added to the
already-committed MR arm (arm1, C36). The airfoil is a deliberately low-fidelity
surrogate, so the result is complementary and gate-value-positive, NOT strong
detection and NOT a superiority claim.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = (ROOT / "research_assets/runs/production-grade-sut-extension"
          / "physicsnemo-mgn-airfoil-three-arm/raw/metric_ledger.json")


class AirfoilThreeArmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_catalogue_and_thresholds(self) -> None:
        self.assertEqual(self.d["fault_catalogue_size"], 10)
        self.assertEqual(self.d["thresholds"]["accuracy_rollout_multiplier"], 2.0)
        self.assertEqual(self.d["thresholds"]["generic_exact_tolerance"], 1e-5)

    def test_arm1_reproduces_c36_robust_detection(self) -> None:
        a1 = self.d["arm1_validity_gated_mr"]
        # only the gross normalization fault is robustly MR-detected (matches C36)
        self.assertEqual(a1["detection_count"], 1)
        self.assertEqual(self.d["complementarity_2x2_mr_vs_accuracy"]["mr_only"], ["NS_skip_denorm"])

    def test_arm2_accuracy_catches_only_gross_boundary_faults(self) -> None:
        a2 = self.d["arm2_accuracy_monitor"]
        self.assertEqual(a2["detection_count"], 2)
        self.assertEqual(set(self.d["complementarity_2x2_mr_vs_accuracy"]["accuracy_only"]),
                         {"BC_zero_outflow", "BC_nonzero_wall"})

    def test_complementarity_is_disjoint(self) -> None:
        c = self.d["complementarity_2x2_mr_vs_accuracy"]["counts"]
        self.assertEqual(c["both"], 0)        # MR and accuracy catch disjoint faults
        self.assertEqual(c["mr_only"], 1)
        self.assertEqual(c["accuracy_only"], 2)
        self.assertEqual(c["neither"], 7)

    def test_arm3_gate_value_admitted_clean_rejected_fire(self) -> None:
        a3 = self.d["arm3_ungated_generic_false_positive"]
        # gate-admitted (node-permutation) raises no baseline false alarm
        self.assertEqual(a3["admitted_template_max_false_positive_rate"], 0.0)
        # every gate-rejected generic template fires on the fault-free SUT
        self.assertEqual(a3["n_rejected_templates"], 4)
        self.assertEqual(a3["n_rejected_templates_flagging_fault_free_sut"], 4)
        by = {t["template"]: t for t in a3["per_template"]}
        self.assertTrue(by["node_permutation"]["admitted_by_gate"])
        self.assertEqual(by["node_permutation"]["baseline_false_positive_rate"], 0.0)
        # mirror-y is the duality-critical rejected template: inadmissible here, and it fires
        self.assertFalse(by["mirror_y_reflection"]["admitted_by_gate"])
        self.assertEqual(by["mirror_y_reflection"]["baseline_false_positive_rate"], 1.0)

    def test_duality_no_falsifier(self) -> None:
        dz = self.d["duality_on_airfoil"]
        self.assertTrue(dz["mirror_y_inadmissible"])
        self.assertFalse(dz["falsifier_observed"])
        self.assertIsNone(dz["mirror_y_arm1_detects"])

    def test_honesty_accuracy_metric_distinct_from_c35_rollout(self) -> None:
        # arm2's deployed-state rollout (~7e-4) is documented as a DIFFERENT quantity from
        # C35's reported 0.92 delta-prediction rollout -- no contradiction is introduced.
        base = self.d["baseline"]
        self.assertLess(base["deployed_state_rollout_relative_l2_median"], 0.01)
        self.assertEqual(base["c35_delta_prediction_rollout_for_reference"], 0.92)
        note = base["metric_note"].lower()
        self.assertIn("different quantity", note)
        self.assertIn("0.92", note)

    def test_no_superiority_claim(self) -> None:
        blob = json.dumps(self.d).lower()
        for forbidden in ("outperform", "better than", "state-of-the-art"):
            self.assertNotIn(forbidden, blob, f"forbidden marketing term present: {forbidden!r}")
        # the honest non-superiority disclaimer is present
        self.assertIn("superiority claim", blob)


if __name__ == "__main__":
    unittest.main()
