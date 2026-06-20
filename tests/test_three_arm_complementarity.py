"""Guard for the three-arm complementarity + gate value + knife-edge (claims C42, C43; MVP-B/C).

Pins, on the converged PointMLP SUT: the 2x2 MR-vs-accuracy complementarity table, the
measurable gate value (gate-admitted generic detector has 0 baseline false positives while
every gate-rejected template fires on the fault-free SUT), and the knife-edge PC_zero_vy
sweep (partial fractions detected, only the uniform fraction escapes). Also asserts the
evidence carries no positive superiority wording (the C42/C43 red line).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research_assets/runs/pointmlp-three-arm-complementarity/raw/metric_ledger.json"


class ThreeArmComplementarityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = LEDGER.read_text(encoding="utf-8")
        cls.d = json.loads(cls.text)

    def test_catalogue_and_predeclared_classes(self) -> None:
        self.assertEqual(self.d["fault_catalogue_size"], 20)
        self.assertEqual(self.d["fault_classes_predeclared"],
                         ["boundary_condition_fault", "normalization_scale_fault",
                          "physical_channel_fault", "temporal_rollout_fault"])
        self.assertTrue(self.d["ars_self_check"]["fault_classes_predeclared"])
        self.assertIn("not applicable", self.d["ars_self_check"]["multiple_comparison_correction"])

    def test_two_arm_complementarity_2x2(self) -> None:
        self.assertEqual(self.d["arm1_validity_gated_mr"]["detection_count"], 13)
        self.assertEqual(self.d["arm2_accuracy_monitor"]["detection_count"], 6)
        # each arm carries a Wilson 95% CI
        self.assertEqual(len(self.d["arm1_validity_gated_mr"]["detection_rate_wilson_ci95"]), 2)
        c = self.d["complementarity_2x2_mr_vs_accuracy"]["counts"]
        self.assertEqual(c, {"both": 4, "mr_only": 9, "accuracy_only": 2, "neither": 5})

    def test_gate_value_baseline_false_positive(self) -> None:
        a3 = self.d["arm3_ungated_generic_false_positive"]
        # gate-admitted detector never flags the fault-free SUT
        self.assertEqual(a3["admitted_template_max_false_positive_rate"], 0.0)
        # every gate-rejected template fires on the fault-free SUT
        self.assertEqual(a3["n_rejected_templates"], 6)
        self.assertEqual(a3["n_rejected_templates_flagging_fault_free_sut"], 6)
        for t in a3["per_template"]:
            if t["admitted_by_gate"]:
                self.assertEqual(t["baseline_false_positive_rate"], 0.0)
            else:
                self.assertGreater(t["baseline_false_positive_rate"], 0.0)

    def test_knife_edge_blind_region_is_uniform_fraction_only(self) -> None:
        k = self.d["knife_edge_pc_zero_vy_sweep"]
        self.assertEqual(k["mr_miss_fractions"], [1.0])
        self.assertNotIn(1.0, k["mr_detect_fractions"])
        self.assertIn(0.99, k["mr_detect_fractions"])

    def test_no_positive_superiority_wording(self) -> None:
        low = self.text.lower()
        # No positive-superiority phrasing anywhere in the evidence (the C42/C43 red line).
        # "baseline-superiority" is allowed only as the negated/forbidden compound noun.
        for phrase in ("outperform", "better than", "superior to", "is superior",
                       "are superior", "more effective than"):
            self.assertNotIn(phrase, low, f"positive-superiority phrase present: {phrase!r}")
        self.assertIn("complementarity", low)
        # the framing is explicit: complementarity, not a competition
        self.assertIn("complementarity, not superiority", low)

    def test_reproduction_provenance_present(self) -> None:
        prov = LEDGER.parent.parent / "PROVENANCE.md"
        self.assertTrue(prov.exists(), f"missing reproduction provenance: {prov}")
        text = prov.read_text(encoding="utf-8")
        self.assertIn("run_three_arm_complementarity_pointmlp.py", text)
        self.assertIn("baseline false-positive", text.lower())

    def test_honesty_boundary(self) -> None:
        lim = self.d["claim_limitations"].lower()
        self.assertIn("one converged sut", lim)
        self.assertIn("not a real-world", lim)
        self.assertIn("baseline-superiority", lim)
        self.assertIn("committed artifacts", lim)


if __name__ == "__main__":
    unittest.main()
