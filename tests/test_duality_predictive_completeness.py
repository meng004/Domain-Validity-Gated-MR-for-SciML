"""Guard for the duality predictive coverage-completeness analysis (claim C50).

Pins the a-priori operator-signature prediction table (computed from operator maths on generic
fields, NOT from the detections), the falsifiable blind-completeness result (every exact
double-zero / preserve-all fault is detected by no MR), and the amplitude-independence evidence
(large invariant-preserving faults still blind). Also asserts the single-invariant predictions
are labelled near-definitional and that the evidence carries no positive-superiority wording.

Honesty contract (runbook §4-D): this guard does NOT assert "all predictions agree". It asserts
the report RECORDS its predict-vs-actual outcome, including any mismatch list; a future genuine
mismatch must surface there rather than break a brittle equality.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/duality-predictive-completeness/duality_predictive_completeness_report.json"


class DualityPredictiveCompletenessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REPORT.read_text(encoding="utf-8")
        cls.d = json.loads(cls.text)

    def test_non_circular_provenance_declared(self) -> None:
        self.assertEqual(self.d["record_type"], "duality-predictive-completeness")
        self.assertIn("generic", self.d["non_circularity"])
        self.assertIn("only for verification", self.d["non_circularity"])
        self.assertEqual(self.d["generic_test_fields"], ["lowfreq_coherent", "analytic_asymmetric"])

    def test_apriori_table_predicted_classes(self) -> None:
        t = self.d["task_a_apriori_table"]
        # the four exact double-zero operators are predicted blind on BOTH architectures
        for f in ("mode_truncation", "spatial_shift", "sharpen", "halffield_roll"):
            self.assertEqual(t[f]["fno"]["predicted_class"], "blind")
            self.assertEqual(t[f]["pinn"]["predicted_class"], "blind")
            self.assertTrue(t[f]["fno"]["a_priori_blind"])
            self.assertTrue(t[f]["fno"]["preserves_sum_exactly"])
            self.assertFalse(t[f]["fno"]["breaks_symmetry"])
        # global renorm: conservation only, on both
        self.assertEqual(t["global_renorm"]["fno"]["predicted_class"], "conservation")
        self.assertEqual(t["global_renorm"]["pinn"]["predicted_class"], "conservation")
        # channel swap: the operator maths predict the FNO/PINN DIFFERENCE a priori
        # (commutes with translation but not with the mirror channel map)
        self.assertEqual(t["channel_swap"]["fno"]["predicted_class"], "conservation")
        self.assertEqual(t["channel_swap"]["pinn"]["predicted_class"], "both")
        # gaussian noise: symmetry only (zero-mean -> conservation untouched at threshold)
        self.assertEqual(t["gaussian_noise"]["fno"]["predicted_class"], "symmetry-translation")
        self.assertEqual(t["gaussian_noise"]["pinn"]["predicted_class"], "symmetry-mirror")

    def test_blind_completeness_holds_no_falsifier(self) -> None:
        cons = self.d["blind_completeness_consolidated"]
        self.assertEqual(cons["a_priori_blind_faults"],
                         ["halffield_roll", "mode_truncation", "sharpen", "spatial_shift"])
        self.assertTrue(cons["holds"])
        self.assertTrue(cons["verified_against_c48_c49"]["all_zero_detected"])
        self.assertEqual(cons["verified_against_c48_c49"]["falsifying_cases"], [])
        self.assertTrue(cons["verified_in_task_c_halffield_roll"]["fno_stays_blind"])
        self.assertEqual(cons["verified_in_task_c_halffield_roll"]["fno_total_detections"], 0)

    def test_amplitude_independence_evidence(self) -> None:
        ai = self.d["task_c_amplitude_independence"]
        self.assertTrue(ai["holds"])
        pinn = ai["pinn_large_blind_fault"]
        self.assertTrue(pinn["stays_blind"])
        self.assertEqual(pinn["detected_any"], 0)
        self.assertGreaterEqual(pinn["max_output_perturbation_rel_l2"], 0.50)   # large, still blind
        fno = ai["fno_large_blind_fault"]
        self.assertTrue(fno["stays_blind"])
        self.assertEqual(fno["total_detections"], 0)
        self.assertGreaterEqual(fno["max_output_perturbation_rel_l2"], 0.10)    # realistic, still blind

    def test_single_invariant_is_labelled_near_definitional(self) -> None:
        nd = self.d["task_b_predict_then_verify"]["near_definitional_single_invariant"]
        self.assertIn("near-definitional", nd["note"])
        self.assertIn("not a finding", nd["note"])
        # at least the global-renorm / gaussian-noise single-invariant cells were checked
        self.assertGreaterEqual(nd["count"], 2)

    def test_predict_vs_actual_outcome_is_recorded(self) -> None:
        # Honesty contract: do NOT require all-agree; require the report to RECORD the outcome,
        # including the (possibly empty) mismatch list, so a real future mismatch surfaces here.
        v = self.d["task_b_predict_then_verify"]
        self.assertIn("mismatches", v)
        self.assertIsInstance(v["mismatches"], list)
        self.assertIn("rows", v)
        self.assertTrue(any(r["a_priori_blind"] for r in v["rows"]))

    def test_no_positive_superiority_wording(self) -> None:
        low = self.text.lower()
        for phrase in ("outperform", "better than", "superior to", "is superior",
                       "are superior", "more effective than"):
            self.assertNotIn(phrase, low, f"positive-superiority phrase present: {phrase!r}")

    def test_provenance_and_claim_present(self) -> None:
        prov = REPORT.parent / "PROVENANCE.md"
        self.assertTrue(prov.exists(), f"missing reproduction provenance: {prov}")
        ptext = prov.read_text(encoding="utf-8")
        self.assertIn("run_duality_predictive_completeness.py", ptext)
        self.assertIn("C50-duality-predictive-completeness", ptext)
        ledger = (ROOT / "research_assets/experiments/claim-ledger.yml").read_text(encoding="utf-8")
        self.assertIn("C50-duality-predictive-completeness", ledger)


if __name__ == "__main__":
    unittest.main()
