"""P2-2 result-level guards: the committed LLM-MR baseline report and the
manuscript LLM-baseline subsection must stay in sync.

Distinct from tests/test_p2_llm_baseline.py (which guards the pipeline contract
without requiring credentials), these tests assert the structural facts of the
ONE committed baseline execution: the candidate count, the rater triple, the
predicate-admit and panel-valid counts, the per-paper-MR overlap counts, and
the presence of the section in the manuscript with the matching numbers.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/llm-mr-baseline/llm_baseline_report.json"
CANDIDATES = ROOT / "research_assets/runs/llm-mr-baseline/llm_candidates.json"
VOTES = ROOT / "research_assets/runs/llm-mr-baseline/llm_votes.json"
MANUSCRIPT = ROOT / "paper/manuscript.md"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"

EXPECTED_RATERS = {"glm-5.1", "kimi-k2.6", "deepseek-v4-flash"}


class TestBaselineArtifactsCommitted(unittest.TestCase):
    def test_files_present(self):
        for p in (REPORT, CANDIDATES, VOTES):
            self.assertTrue(p.exists(), f"missing baseline artifact: {p}")


class TestBaselineNumbers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(REPORT.read_text())
        cls.v = json.loads(VOTES.read_text())

    def test_eight_candidates(self):
        self.assertEqual(self.r["n_candidates"], 8)

    def test_predicate_admit_eight_of_eight(self):
        self.assertEqual(self.r["n_admitted_by_predicate"], 8)

    def test_panel_majority_valid_seven_of_eight(self):
        self.assertEqual(self.r["n_panel_majority_valid"], 7)

    def test_predicate_and_panel_seven(self):
        self.assertEqual(self.r["n_admitted_by_predicate_and_panel_valid"], 7)

    def test_overlap_counts_match_committed(self):
        # Stored as committed; if a future rerun changes these the assertion
        # forces the manuscript number to be re-synced first.
        counts = self.r["per_paper_mr_overlap_count"]
        self.assertEqual(counts["node_permutation_equivariance"], 2)
        self.assertEqual(counts["mirror_y_reflection"], 1)
        self.assertEqual(counts["discrete_divergence_free_conservation"], 4)
        self.assertEqual(self.r["n_overlap_with_paper_mrs"], 6)

    def test_three_vendor_disjoint_raters(self):
        surviving = set(self.v["raters_surviving"])
        self.assertEqual(surviving, EXPECTED_RATERS)
        # The generator vendor (claude/openai) must not be among the raters.
        gen = self.v.get("generator_model", "")
        self.assertNotIn(gen, surviving,
                         "generator vendor must not double as a rater")

    def test_no_constant_rater(self):
        self.assertEqual(self.v["constant_raters_excluded_from_kappa"], [])

    def test_inter_rater_metrics_present(self):
        for k in ("fleiss_kappa", "raw_pointwise_agreement",
                  "item_unanimous_rate"):
            self.assertIn(k, self.v)
            self.assertIsNotNone(self.v[k])


class TestManuscriptAndLedgerInSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = MANUSCRIPT.read_text()
        cls.l = LEDGER.read_text()

    def test_subsection_present(self):
        self.assertIn("5.6.4 LLM and generic-MR baselines", self.m)

    def test_subsection_carries_headline_numbers(self):
        self.assertIn("7/8", self.m)
        self.assertIn("K=8", self.m)
        self.assertTrue(re.search(r"glm-5\.1", self.m))
        self.assertTrue(re.search(r"kimi-k2\.6", self.m))
        self.assertTrue(re.search(r"deepseek-v4-flash", self.m))
        # Fleiss kappa value (3 sig figs allowed) must appear with the paradox call-out.
        self.assertTrue(re.search(r"Fleiss kappa is 0\.07", self.m))
        # Small-sample paradox explicitly named.
        self.assertIn("paradox", self.m)

    def test_ledger_promoted_from_blocked(self):
        self.assertIn('claim_id: "C3-baseline-comparison"', self.l)
        # The status line for C3 should now be observed: expert, LLM, and generic baselines are all committed.
        m = re.search(r'claim_id: "C3-baseline-comparison"\s*\n\s*status:\s*"([^"]+)"',
                      self.l)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "observed")


if __name__ == "__main__":
    unittest.main()
