import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "research_assets" / "runs" / "realpdebench-foil-metadata-screen"
PREFLIGHT = ROOT / "research_assets" / "runs" / "realpdebench-foil-preflight"
CARD = ROOT / "research_assets" / "mr_cards" / "realpdebench_foil_mirror_y_gate.json"
CLAIM_LEDGER = ROOT / "research_assets" / "experiments" / "claim-ledger.yml"
JSS_MAIN = ROOT / "manuscript" / "main.tex"
JSS_SUPPLEMENT = ROOT / "manuscript" / "supplementary.tex"


class RealPDEBenchFoilMetadataScreenTests(unittest.TestCase):
    def load_json(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_metadata_screen_finds_zero_aoa_real_and_numerical_cases(self):
        summary = self.load_json(SCREEN / "metadata_screen_summary.json")

        self.assertGreaterEqual(
            len(summary["real_zero_aoa"]["out_dist"]),
            1,
            "RealPDEBench foil metadata must expose held-out zero-AoA real cases before mirror-y can proceed.",
        )
        self.assertGreaterEqual(
            len(summary["real_test_index"]["zero_aoa_sims"]),
            1,
            "Real test index must include zero-AoA foil cases.",
        )
        self.assertGreaterEqual(
            len(summary["numerical_test_index"]["zero_aoa_sims"]),
            1,
            "Numerical test index must include zero-AoA foil cases.",
        )

    def test_metadata_screen_has_velocity_and_coordinate_fields(self):
        summary = self.load_json(SCREEN / "metadata_screen_summary.json")

        real_features = set(summary["dataset_features"]["real"])
        numerical_features = set(summary["dataset_features"]["numerical"])
        self.assertTrue({"u", "v", "x", "y", "t"}.issubset(real_features))
        self.assertTrue({"u", "v", "p", "x", "y", "t"}.issubset(numerical_features))

    def test_foil_mirror_card_is_fail_closed_candidate_not_result(self):
        card = self.load_json(CARD)

        self.assertEqual(card["evidence_level"], "design-time-candidate")
        self.assertEqual(card["status"], "design-time-deferred")
        self.assertIsNone(card["tolerance"]["threshold"])
        self.assertNotIn("pass", card["allowed_verdicts"])
        self.assertNotIn("fail", card["allowed_verdicts"])
        self.assertIn("out-of-relation-domain", card["allowed_verdicts"])
        self.assertIn("numerical-tolerance-issue", card["allowed_verdicts"])
        self.assertIn("AoA = 0.0 degrees", " ".join(card["transformation_preconditions"]))
        rejection_text = (card["claim_limitations"] + " " + card["exclusion_rules"][0]).lower()
        self.assertIn("non-zero", rejection_text)
        self.assertIn("angle-of-attack", rejection_text)

    def test_preflight_report_records_metric_but_no_pass_fail(self):
        report = self.load_json(PREFLIGHT / "foil_mirror_preflight_report.json")

        self.assertEqual(report["sim_id"], "10000_0.0.h5")
        self.assertEqual(report["angle_of_attack_degrees"], 0.0)
        self.assertEqual(report["coordinate_floor_max_norm"], 0.0)
        self.assertEqual(report["verdict"], "inconclusive")
        self.assertIsNotNone(report["metric"])
        self.assertIn("combined_uv_relative_l2", report["metric"])
        self.assertIn("no pass/fail claim is licensed", report["reason"])
        self.assertIn("not a SUT pass/fail result", report["claim_limitations"])
        self.assertIn("not a real-defect detection result", report["claim_limitations"])

    def test_claim_ledger_keeps_realpdebench_claim_bounded(self):
        ledger = CLAIM_LEDGER.read_text(encoding="utf-8")

        self.assertIn("C55-realpdebench-foil-mirror-preflight", ledger)
        self.assertIn("typed verdict is inconclusive rather than", ledger)
        self.assertIn("not a trained-SUT correctness result", ledger)
        self.assertIn("The foil result is a SUT pass/fail result.", ledger)
        self.assertIn("The method detects real defects on RealPDEBench.", ledger)

    def test_jss_text_mentions_preflight_without_overclaiming(self):
        main = JSS_MAIN.read_text(encoding="utf-8")
        supplement = JSS_SUPPLEMENT.read_text(encoding="utf-8")

        self.assertIn("RealPDEBench foil preflight", supplement)
        self.assertIn("Production-adjacent RealPDEBench foil preflight", supplement)
        self.assertIn("typed verdict", supplement)
        self.assertIn("inconclusive", supplement)
        forbidden_main_phrases = [
            "RealPDEBench validates",
            "detects real defects on RealPDEBench",
            "is production CFD validation",
            "trained-SUT correctness result",
        ]
        for phrase in forbidden_main_phrases:
            self.assertNotIn(phrase, main + supplement)


if __name__ == "__main__":
    unittest.main()
