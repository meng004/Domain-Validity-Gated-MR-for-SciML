"""Guard for the PINN realistic-fault emergence test (claim C49).

Pins, on the K=6 Burgers PINN roster, the EMERGENT by-class structure obtained with the SAME
eight realistic faults as the FNO run (C48) and the PINN's predeclared C46 thresholds: the 2x2
partition among the faults that reach testable magnitude, the structural transport blind region
(spatial_shift still blind at large magnitude), the honest separation of below-magnitude
untestable faults from genuine misses, and the per-fault measured perturbations.

Honesty contract (runbook §5-C): asserts the report is COMPLETE, its numbers internally
consistent, and that it carries no positive-superiority wording. It deliberately does NOT assert
a clean 1:1 by-class diagonal, and it does NOT assert that the below-magnitude faults are blind.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/pinn-realistic-fault/pinn_realistic_fault_report.json"


class PinnRealisticFaultTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REPORT.read_text(encoding="utf-8")
        cls.d = json.loads(cls.text)

    def test_roster_thresholds_and_shared_catalogue(self) -> None:
        self.assertEqual(self.d["record_type"], "pinn-realistic-fault-emergence")
        self.assertEqual(self.d["trained_sut_count"], 6)
        self.assertTrue(self.d["thresholds_reused_from_constructed_runner"])
        # the fault catalogue is shared verbatim with the FNO run (not architecture-tailored)
        self.assertTrue(self.d["fault_catalogue_shared_with_fno"])

    def test_every_fault_carries_a_measured_perturbation(self) -> None:
        for s in self.d["per_sut"]:
            for fault, det in s["detections"].items():
                self.assertIn("output_perturbation_rel_l2", det)
                self.assertGreaterEqual(det["output_perturbation_rel_l2"], 0.0)
        for fault, pf in self.d["per_fault"].items():
            for key in ("median_output_perturbation_rel_l2",
                        "min_output_perturbation_rel_l2",
                        "max_output_perturbation_rel_l2"):
                self.assertIn(key, pf)

    def test_detected_faults_and_by_class(self) -> None:
        pf = self.d["per_fault"]
        self.assertEqual(pf["global_renorm"]["detected_any"], 6)
        self.assertEqual(pf["global_renorm"]["by_class_localization"], "conservation")
        self.assertEqual(pf["gaussian_noise"]["detected_any"], 6)
        self.assertEqual(pf["gaussian_noise"]["by_class_localization"], "mirror")
        self.assertEqual(pf["channel_swap"]["detected_any"], 6)
        self.assertEqual(pf["channel_swap"]["by_class_localization"], "both")

    def test_emergent_2x2_among_testable_faults(self) -> None:
        part = self.d["emergence_summary"]["emergent_2x2_partition"]
        self.assertEqual(part["conservation_only"], ["global_renorm"])
        self.assertEqual(part["mirror_only"], ["gaussian_noise"])
        self.assertEqual(part["both_mrs"], ["channel_swap"])
        # the transport fault is the one blind-at-magnitude entry
        self.assertEqual(part["neither_mr_at_realistic_magnitude"], ["spatial_shift"])

    def test_transport_blind_region_real_at_large_magnitude(self) -> None:
        es = self.d["emergence_summary"]
        self.assertEqual(es["blind_at_realistic_magnitude"], ["spatial_shift"])
        ob = es["old_blind_faults_retest"]["spatial_shift"]
        self.assertTrue(ob["structurally_blind_to_both_mrs"])
        self.assertEqual(ob["verdict"], "blind_above_realistic_magnitude")
        self.assertGreaterEqual(ob["max_output_perturbation_rel_l2"], 0.30)
        self.assertEqual(self.d["per_fault"]["spatial_shift"]["detected_any"], 0)

    def test_below_magnitude_faults_reported_not_as_misses(self) -> None:
        es = self.d["emergence_summary"]
        # exactly these four faults stay below the realistic band on the fine smooth grid
        self.assertEqual(es["below_realistic_magnitude_untestable"],
                         ["boundary_band_corrupt", "mode_truncation", "region_dropout", "sharpen"])
        for f in es["below_realistic_magnitude_untestable"]:
            self.assertLess(self.d["per_fault"][f]["max_output_perturbation_rel_l2"], 0.10)
        # four faults reach testable magnitude; three are detected
        self.assertEqual(es["n_tested_at_realistic_magnitude"], 4)
        self.assertEqual(es["n_detected_faults"], 3)

    def test_verdict_is_honest_about_structure(self) -> None:
        v = self.d["emergence_summary"]["honest_verdict"]
        self.assertIn("2x2 partition", v)
        self.assertIn("STILL escape both MRs", v)
        self.assertIn("not a construction artifact", v)
        self.assertIn("below the realistic damage band", v)
        # the structural-blindness mechanism is recorded as a flag on each transport/high-freq fault
        for f in ("spatial_shift", "sharpen", "mode_truncation"):
            self.assertTrue(
                self.d["emergence_summary"]["old_blind_faults_retest"][f]["structurally_blind_to_both_mrs"])

    def test_no_positive_superiority_wording(self) -> None:
        low = self.text.lower()
        for phrase in ("outperform", "better than", "superior to", "is superior",
                       "are superior", "more effective than"):
            self.assertNotIn(phrase, low, f"positive-superiority phrase present: {phrase!r}")

    def test_provenance_and_claim_present(self) -> None:
        prov = REPORT.parent / "PROVENANCE.md"
        self.assertTrue(prov.exists(), f"missing reproduction provenance: {prov}")
        ptext = prov.read_text(encoding="utf-8")
        self.assertIn("run_realistic_fault_pinn.py", ptext)
        self.assertIn("C49-pinn-realistic-fault-emergence", ptext)
        ledger = (ROOT / "research_assets/experiments/claim-ledger.yml").read_text(encoding="utf-8")
        self.assertIn("C49-pinn-realistic-fault-emergence", ledger)


if __name__ == "__main__":
    unittest.main()
