import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "research_assets" / "runs" / "external-defect-corpus-scan"
CLAIM_LEDGER = ROOT / "research_assets" / "experiments" / "claim-ledger.yml"
EXPERIMENT_LEDGER = ROOT / "research_assets" / "experiments" / "experiment-ledger.yml"
JSS_MAIN = ROOT / "manuscript" / "main.tex"
JSS_SUPPLEMENT = ROOT / "manuscript" / "supplementary.tex"
JSS_COVER_LETTER = ROOT / "venues" / "jss" / "cover_letter.md"
REVIEW = ROOT / "paper" / "93_external_defect_corpus_experiment_review.md"
REVIEWER_PACK = ROOT / "paper" / "95_jss_external_corpus_reviewer_facing_pack.md"


class ExternalDefectCorpusWitnessTests(unittest.TestCase):
    def load_json(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_summary_records_five_external_units(self):
        summary = self.load_json(RUN / "external_defect_corpus_summary.json")

        self.assertEqual(summary["typed_verdict"], "pass")
        self.assertEqual(summary["unit_count"], 5)
        self.assertEqual(summary["repository_or_subsystem_count"], 4)
        self.assertEqual(summary["verdict_counts"], {"pass": 5})
        self.assertTrue(all(summary["minimum_success_checks"].values()))
        self.assertIn("not a real-world defect-rate", summary["claim_limitations"])

    def test_neuraloperator_spectrum2d_witness(self):
        report = self.load_json(
            RUN / "neuraloperator_spectrum2d_real_defect_witness_report.json"
        )

        self.assertEqual(report["typed_verdict"], "pass")
        self.assertTrue(report["source_checks"]["pr_661_merged"])
        self.assertTrue(report["source_checks"]["patch_replaces_l1_with_l2_radius"])
        self.assertTrue(report["source_checks"]["patch_squares_before_bin_sum"])
        self.assertTrue(
            report["verdict_checks"]["old_l1_radius_collides_distinct_l2_modes"]
        )
        self.assertEqual(report["metric"]["old_power_after_sum"], 0.0)
        self.assertEqual(report["metric"]["corrected_power_sum_of_squares"], 2.0)

    def test_neuraloperator_hermitian_witness_is_bounded(self):
        report = self.load_json(
            RUN / "neuraloperator_hermitian_symmetry_real_defect_witness_report.json"
        )

        self.assertEqual(report["typed_verdict"], "pass")
        self.assertTrue(report["source_checks"]["pr_702_merged"])
        self.assertTrue(report["source_checks"]["patch_zeroes_dc_imag"])
        self.assertTrue(report["source_checks"]["patch_zeroes_nyquist_imag"])
        self.assertEqual(
            report["metric"]["corrected_boundary_metric"]["max_boundary_abs_imag"],
            0.0,
        )
        self.assertIn(
            "does not reproduce GPU-specific line artifacts",
            report["claim_limitations"],
        )

    def test_jaxcfd_flux_boundary_witness(self):
        report = self.load_json(RUN / "jaxcfd_flux_boundary_real_defect_witness_report.json")

        self.assertEqual(report["typed_verdict"], "pass")
        self.assertTrue(report["source_checks"]["pr_167_merged"])
        self.assertTrue(report["source_checks"]["patch_adds_flux_bc_inference_function"])
        self.assertEqual(report["metric"]["old_flux_bc"], ["neumann", "neumann"])
        self.assertEqual(report["metric"]["corrected_flux_bc"], ["dirichlet", "dirichlet"])
        self.assertFalse(report["metric"]["old_matches_expected"])
        self.assertTrue(report["metric"]["corrected_matches_expected"])

    def test_phiml_custom_gradient_witness(self):
        report = self.load_json(
            RUN / "phiml_custom_gradient_transpose_real_defect_witness_report.json"
        )

        self.assertEqual(report["typed_verdict"], "pass")
        self.assertTrue(
            report["source_checks"]["commit_message_mentions_transposed_custom_gradients"]
        )
        self.assertTrue(report["source_checks"]["patch_handles_dense_native_names"])
        self.assertEqual(report["metric"]["old_native_shape"], [2, 3])
        self.assertEqual(report["metric"]["corrected_native_shape"], [3, 2])
        self.assertFalse(report["metric"]["old_matches_expected"])
        self.assertTrue(report["metric"]["corrected_matches_expected"])

    def test_ledgers_bound_external_defect_corpus_claim(self):
        claim_ledger = CLAIM_LEDGER.read_text(encoding="utf-8")
        experiment_ledger = EXPERIMENT_LEDGER.read_text(encoding="utf-8")

        self.assertIn("C57-external-defect-witness-corpus", claim_ledger)
        self.assertIn("external-defect-corpus-summary-001", experiment_ledger)
        self.assertIn("five units across four repositories", claim_ledger)
        self.assertIn("real-world defect-detection rate", claim_ledger)
        self.assertIn(
            "not a representative sample of SciML software defects",
            experiment_ledger,
        )

    def test_jss_text_integrates_corpus_without_overclaiming(self):
        main = JSS_MAIN.read_text(encoding="utf-8")
        supplement = JSS_SUPPLEMENT.read_text(encoding="utf-8")

        self.assertIn("External defect-witness corpus", supplement)
        self.assertIn(
            "Five public external witnesses across four repositories/subsystems",
            supplement,
        )
        self.assertIn("NeuralOperator \\texttt{spectrum\\_2d}", supplement)
        self.assertIn("JAX-CFD advection flux", supplement)
        forbidden_main_phrases = [
            "is a representative sample of SciML defects",
            "validates production SciML",
            "proves trained-SUT correctness",
            "measures a real-world defect-detection rate",
        ]
        for phrase in forbidden_main_phrases:
            self.assertNotIn(phrase, main + supplement)

    def test_experiment_review_records_drift_and_truth_boundaries(self):
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Theme-drift decision", review)
        self.assertIn("The external-defect corpus experiment task is complete.", review)
        self.assertIn("not production CFD validation", review)
        self.assertIn("not trained-SUT correctness evidence", review)
        self.assertIn("not a real-world defect-detection rate", review)
        self.assertIn("stable accept guaranteed", review)

    def test_reviewer_facing_pack_locks_quasi_representative_boundary(self):
        pack = REVIEWER_PACK.read_text(encoding="utf-8")

        self.assertIn("quasi-representative reviewer-facing evidence", pack)
        self.assertIn("not statistically representative", pack)
        self.assertIn("Phase A review: pass", pack)
        self.assertIn("Phase B review: pass", pack)
        self.assertIn("Phase C review: pass", pack)
        self.assertIn("Phase D review: pass", pack)
        self.assertIn("purposeful screen", pack)
        self.assertIn("not random sampling", pack)
        self.assertIn("external-witness tier", pack)
        self.assertIn("stronger future tier", pack)
        self.assertIn("Current paper reaches the external-witness tier", pack)
        for unit in ["EDC-01", "EDC-02", "EDC-03", "EDC-04", "EDC-05"]:
            self.assertIn(unit, pack)
        for forbidden in [
            "production validation",
            "trained-SUT correctness",
            "defect rate",
            "representative sampling",
        ]:
            self.assertIn(forbidden, pack)

    def test_jss_supplement_explains_screening_coverage_and_evidence_ladder(self):
        supplement = JSS_SUPPLEMENT.read_text(encoding="utf-8")

        self.assertIn("Reviewer-facing screening protocol", supplement)
        self.assertIn("Inclusion criteria", supplement)
        self.assertIn("Exclusion criteria", supplement)
        self.assertIn("Purposeful screen", supplement)
        self.assertIn("Component coverage map", supplement)
        self.assertIn("Evidence ladder and claim boundary", supplement)
        self.assertIn("The current paper reaches the external-witness tier", supplement)
        for component in [
            "periodic boundary-condition derivative semantics",
            "spectral metric numerical-decidability semantics",
            "Hermitian frequency-domain symmetry semantics",
            "coordinate/component axis-order gradient semantics",
            "advection flux boundary-condition inference semantics",
        ]:
            self.assertIn(component, supplement)

    def test_cover_letter_frames_corpus_as_curated_not_representative(self):
        cover = JSS_COVER_LETTER.read_text(encoding="utf-8")

        self.assertIn("purposefully screened external witness corpus", cover)
        self.assertIn("curated external evidence", cover)
        self.assertIn("not statistically representative", cover)
        self.assertIn("not presented as production-CFD validation", cover)


if __name__ == "__main__":
    unittest.main()
