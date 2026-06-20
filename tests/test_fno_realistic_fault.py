"""Guard for the FNO realistic-fault emergence test (claim C48).

Pins, on the K=6 FNO-2D roster, the EMERGENT by-class detection structure obtained with eight
realistic mechanism-level faults that are NOT tailored to the invariants and with the same
predeclared thresholds as the constructed C45 run: the 2x2 partition of detected faults, the
structural blind region of transport/high-frequency faults (still blind where they reach
realistic magnitude), and the per-fault measured perturbation magnitudes.

Honesty contract (runbook §5-C): this guard asserts the report is COMPLETE, that its numbers
are internally consistent, and that it carries no positive-superiority wording. It deliberately
does NOT assert a clean 1:1 by-class diagonal -- the realistic result is a messier 2x2 partition
with a confirmed blind region, and pinning a clean diagonal would re-introduce the very
construction the experiment set out to test.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/fno-realistic-fault/fno_realistic_fault_report.json"


class FnoRealisticFaultTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REPORT.read_text(encoding="utf-8")
        cls.d = json.loads(cls.text)

    def test_roster_and_reused_thresholds(self) -> None:
        self.assertEqual(self.d["record_type"], "fno-realistic-fault-emergence")
        self.assertEqual(self.d["trained_sut_count"], 6)
        self.assertEqual(self.d["pdes"], ["burgers", "heat"])
        # the thresholds were reused from the constructed runner, not re-tuned
        self.assertTrue(self.d["thresholds_reused_from_constructed_runner"])

    def test_every_fault_carries_a_measured_perturbation(self) -> None:
        # Every applicable per-case detection records the measured output perturbation magnitude
        # (the runbook's anti-cherry-pick requirement), and the per-fault rollup carries it too.
        for s in self.d["per_sut"]:
            for case in s["cases"]:
                for fault, det in case["detections"].items():
                    if det.get("applicable"):
                        self.assertIn("output_perturbation_rel_l2", det)
                        self.assertGreaterEqual(det["output_perturbation_rel_l2"], 0.0)
        for fault, pf in self.d["per_fault"].items():
            if pf.get("applicable_cells", 0) > 0:
                for key in ("median_output_perturbation_rel_l2",
                            "min_output_perturbation_rel_l2",
                            "max_output_perturbation_rel_l2"):
                    self.assertIn(key, pf)

    def test_detected_faults_and_by_class(self) -> None:
        pf = self.d["per_fault"]
        # The five detected faults, with their emergent (measured) localization.
        self.assertEqual(pf["boundary_band_corrupt"]["detected_any"], 24)
        self.assertEqual(pf["boundary_band_corrupt"]["by_class_localization"], "both")
        self.assertEqual(pf["region_dropout"]["detected_any"], 24)
        self.assertEqual(pf["region_dropout"]["by_class_localization"], "both")
        self.assertEqual(pf["global_renorm"]["detected_any"], 24)
        self.assertEqual(pf["global_renorm"]["by_class_localization"], "conservation")
        self.assertEqual(pf["gaussian_noise"]["detected_any"], 24)
        self.assertEqual(pf["gaussian_noise"]["by_class_localization"], "translation")
        # channel swap is Burgers-only (12 applicable cells), conservation-localized
        self.assertEqual(pf["channel_swap"]["applicable_cells"], 12)
        self.assertEqual(pf["channel_swap"]["by_class_localization"], "conservation")

    def test_emergent_2x2_partition(self) -> None:
        part = self.d["emergence_summary"]["emergent_2x2_partition"]
        self.assertEqual(part["conservation_only"], ["channel_swap", "global_renorm"])
        self.assertEqual(part["translation_only"], ["gaussian_noise"])
        self.assertEqual(part["both_mrs"], ["boundary_band_corrupt", "region_dropout"])
        self.assertEqual(part["neither_mr"], ["mode_truncation", "sharpen", "spatial_shift"])

    def test_structural_blind_region_real_at_realistic_magnitude(self) -> None:
        ob = self.d["emergence_summary"]["old_blind_faults_retest"]
        # spatial_shift and sharpen reach the realistic band on the structured roster member and
        # STILL escape both MRs -> the blind region is real, not a construction artifact.
        for f in ("spatial_shift", "sharpen"):
            self.assertTrue(ob[f]["structurally_blind_to_both_mrs"])
            self.assertEqual(ob[f]["verdict"], "blind_even_at_realistic_magnitude")
            self.assertGreaterEqual(ob[f]["in_band_cells"], 1)
            self.assertEqual(ob[f]["detection_rate_in_band"], 0.0)
            self.assertEqual(self.d["per_fault"][f]["detected_any"], 0)
        # mode truncation cannot reach the realistic band on these smooth low-res fields
        self.assertEqual(ob["mode_truncation"]["verdict"],
                         "magnitude_below_realistic_band_on_these_smooth_fields")
        self.assertEqual(ob["mode_truncation"]["in_band_cells"], 0)

    def test_emergence_accounting_is_consistent(self) -> None:
        es = self.d["emergence_summary"]
        self.assertEqual(es["n_applicable_faults"], 8)
        self.assertEqual(es["n_detected_faults"], 5)
        self.assertEqual(es["missed_by_both_MRs"],
                         ["mode_truncation", "sharpen", "spatial_shift"])
        # the verdict names the structure honestly (emergent, not a clean diagonal)
        self.assertIn("2x2 partition", es["honest_verdict"])
        self.assertIn("structurally invisible", es["honest_verdict"])

    def test_no_positive_superiority_wording(self) -> None:
        low = self.text.lower()
        for phrase in ("outperform", "better than", "superior to", "is superior",
                       "are superior", "more effective than"):
            self.assertNotIn(phrase, low, f"positive-superiority phrase present: {phrase!r}")

    def test_provenance_and_claim_present(self) -> None:
        prov = REPORT.parent / "PROVENANCE.md"
        self.assertTrue(prov.exists(), f"missing reproduction provenance: {prov}")
        ptext = prov.read_text(encoding="utf-8")
        self.assertIn("run_realistic_fault_fno.py", ptext)
        self.assertIn("C48-fno-realistic-fault-emergence", ptext)
        ledger = (ROOT / "research_assets/experiments/claim-ledger.yml").read_text(encoding="utf-8")
        self.assertIn("C48-fno-realistic-fault-emergence", ledger)


if __name__ == "__main__":
    unittest.main()
