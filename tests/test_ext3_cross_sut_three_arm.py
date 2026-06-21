"""EXT-3 guard: cross-SUT three-arm + duality consolidation (claim C51).

Pins that the consolidation references committed artifacts only, that the airfoil
accuracy/generic arms are now folded in from the live-model run (C52) so all three
converged SUTs carry all three arms, records the cross-SUT validity-coverage duality
with a falsifiability condition, and carries zero superiority language.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/ext3-cross-sut-three-arm/raw/cross_sut_three_arm_report.json"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


class TestExt3CrossSutThreeArm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.led = LEDGER.read_text(encoding="utf-8")

    def test_three_converged_suts(self):
        suts = self.r["converged_suts"]
        self.assertEqual(len(suts), 3)
        names = " ".join(s["sut"] for s in suts).lower()
        self.assertIn("meshgraphnets", names)
        self.assertIn("pointmlp", names)
        self.assertIn("airfoil", names)

    def test_arm_coverage_matrix_honest(self):
        m = self.r["arm_coverage_matrix"]
        # PointMLP and the converged airfoil both now carry the full three arms (C52).
        pm = next(v for k, v in m.items() if "pointmlp" in k.lower())
        af = next(v for k, v in m.items() if "airfoil" in k.lower())
        self.assertEqual(pm, ["arm1", "arm2", "arm3"])
        self.assertEqual(af, ["arm1", "arm2", "arm3"])

    def test_airfoil_arms_now_run_from_c52(self):
        af = next(s for s in self.r["converged_suts"] if "airfoil" in s["sut"].lower())
        # arm2/arm3 are populated structured results, not GPU-pending strings.
        self.assertIsInstance(af["arm2_accuracy_monitor"], dict)
        self.assertIsInstance(af["arm3_gate_value"], dict)
        self.assertNotIn("GPU-pending", str(af["arm2_accuracy_monitor"]))
        self.assertIn("C52", af["source_claims"])
        # MR and accuracy stay complementary (disjoint) on the low-fidelity airfoil
        self.assertEqual(af["complementarity_2x2"]["both"], 0)
        # gate value: every rejected generic template fires on the fault-free SUT
        self.assertEqual(af["arm3_gate_value"]["rejected_templates_flagging_fault_free_sut"], "4/4")
        # mirror-y excluded on airfoil = the duality point
        self.assertEqual(len(af["admissible_mr_set"]), 2)
        self.assertTrue(any("mirror-y" in x for x in af["gate_excluded_mr"]))

    def test_cylinder_and_pointmlp_have_three_admissible_mrs(self):
        for key in ("meshgraphnets", "pointmlp"):
            s = next(s for s in self.r["converged_suts"] if key in s["sut"].lower())
            self.assertEqual(len(s["admissible_mr_set"]), 3)

    def test_duality_falsifiable(self):
        d = self.r["duality_cross_sut"]
        self.assertTrue(len(d["cross_sut_confirmations"]) >= 3)
        self.assertIn("refute", d["falsifiability"].lower())
        self.assertIn("C47", d["prior_synthesis"])

    def test_zero_superiority_language(self):
        # Scan for active superiority CLAIMS; compliant disclaimers legitimately use
        # the word "superiority" (e.g. "not a superiority claim"), so bare "superior"
        # is not in the ban-list -- the meaningful guard is the active phrasing.
        blob = json.dumps(self.r).lower()
        for bad in ("outperform", "better than", "state-of-the-art", "beats the"):
            self.assertNotIn(bad, blob)

    def test_c51_and_c52_claims_registered(self):
        self.assertIn("C51-cross-sut-three-arm-consolidation", self.led)
        # the airfoil three-arm completion is registered as its own GPU-run claim
        self.assertIn("C52-airfoil-three-arm", self.led)
        # superiority stays forbidden in both
        self.assertIn("outperforms the accuracy monitor or any baseline", self.led)


if __name__ == "__main__":
    unittest.main()
