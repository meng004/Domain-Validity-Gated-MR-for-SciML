import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "research_assets" / "runs" / "deepxde-periodicbc-real-defect-scan"
CARD = ROOT / "research_assets" / "mr_cards" / "deepxde_periodicbc_derivative_enforcement.json"
CLAIM_LEDGER = ROOT / "research_assets" / "experiments" / "claim-ledger.yml"
EXPERIMENT_LEDGER = ROOT / "research_assets" / "experiments" / "experiment-ledger.yml"
JSS_MAIN = ROOT / "manuscript" / "main.tex"
JSS_SUPPLEMENT = ROOT / "manuscript" / "supplementary.tex"


class DeepXDEPeriodicBCRealDefectWitnessTests(unittest.TestCase):
    def load_json(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_external_issue_pr_artifacts_are_archived(self):
        issue = self.load_json(RUN / "raw" / "deepxde_issue_26.json")
        pr = self.load_json(RUN / "raw" / "deepxde_pr_27.json")
        patch = (RUN / "raw" / "deepxde_pr_27.patch").read_text(encoding="utf-8")

        self.assertEqual(issue["html_url"], "https://github.com/lululxvi/deepxde/issues/26")
        self.assertEqual(issue["state"], "closed")
        self.assertEqual(pr["html_url"], "https://github.com/lululxvi/deepxde/pull/27")
        self.assertTrue(pr["merged"])
        self.assertEqual(pr["merge_commit_sha"], "c4b44313939aac1aa51430e9e2a1b6c2cbec0c10")
        self.assertIn("derivative_order=0", patch)
        self.assertIn("tf.gradients", patch)

    def test_mr_card_is_executable_but_bounded(self):
        card = self.load_json(CARD)

        self.assertEqual(card["evidence_level"], "design-time-asset")
        self.assertEqual(card["tolerance"]["threshold"], 1e-12)
        self.assertIn("pass", card["allowed_verdicts"])
        self.assertIn("fail", card["allowed_verdicts"])
        self.assertIn("issue #26", card["boundary_condition_compatibility"]["reason"])
        self.assertIn("not report a trained-SUT verdict", card["claim_limitations"])

    def test_witness_report_records_full_semantic_contrast(self):
        report = self.load_json(RUN / "deepxde_periodicbc_real_defect_witness_report.json")

        self.assertEqual(report["typed_verdict"], "pass")
        self.assertTrue(report["source_checks"]["pr_27_merged"])
        self.assertTrue(report["source_checks"]["patch_adds_derivative_order_argument"])
        self.assertTrue(report["verdict_checks"]["external_defect_source_complete"])
        self.assertEqual(report["metric"]["pre_pr27_value_only_abs_residual"], 0.0)
        self.assertEqual(report["metric"]["pr27_derivative_order_1_abs_residual"], 2.0)
        self.assertIn("not a defect-detection rate", report["claim_limitations"])

    def test_ledgers_bound_the_claim(self):
        claim_ledger = CLAIM_LEDGER.read_text(encoding="utf-8")
        experiment_ledger = EXPERIMENT_LEDGER.read_text(encoding="utf-8")

        self.assertIn("C56-deepxde-periodicbc-real-defect-witness", claim_ledger)
        self.assertIn("deepxde-periodicbc-real-defect-witness-001", experiment_ledger)
        self.assertIn("pre-PR", claim_ledger)
        self.assertIn("derivative_order=1 residual is", claim_ledger)
        self.assertIn("not a real-world", experiment_ledger)
        self.assertIn("The paper measures a real-world defect-detection rate.", claim_ledger)

    def test_jss_text_mentions_witness_without_rate_claim(self):
        main = JSS_MAIN.read_text(encoding="utf-8")
        supplement = JSS_SUPPLEMENT.read_text(encoding="utf-8")

        self.assertIn("DeepXDE PeriodicBC issue-linked witness", supplement)
        self.assertIn("derivative\\_order=1} residual is 2.0", supplement)
        forbidden_main_phrases = [
            "measures a real-world defect-detection rate",
            "detects all DeepXDE",
            "validates trained PINN accuracy",
            "production CFD readiness",
        ]
        for phrase in forbidden_main_phrases:
            self.assertNotIn(phrase, main + supplement)


if __name__ == "__main__":
    unittest.main()
