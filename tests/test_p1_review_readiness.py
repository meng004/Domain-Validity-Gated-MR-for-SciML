"""P1 acceptance gates: send-to-reviewer readiness (TDD).

Encodes the Phase-P1 items from paper/30 that close every Stage-9 hot spot
reachable by writing and re-analysis alone (no new experiments).
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IST = ROOT / "paper" / "ist-submission" / "main.tex"
BIB = ROOT / "paper" / "ist-submission" / "references.bib"
README = ROOT / "README.md"
sys.path.insert(0, str(ROOT / "tools"))
from ist_wordcount import ist_word_count  # noqa: E402


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


class P1ReviewReadinessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tex = read(IST)
        self.abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
                                  self.tex, re.S).group(1)
        self.highlights = re.search(r"\\begin\{highlights\}(.*?)\\end\{highlights\}",
                                    self.tex, re.S).group(1)

    # P1-1 / P1-5: claim ledger promoted to a named contribution
    def test_p1_1_claim_ledger_in_abstract_and_highlights(self) -> None:
        self.assertIn("ledger", self.abstract.lower(),
                      "abstract Method should mention the claim/evidence ledger")
        self.assertIn("ledger", self.highlights.lower(),
                      "a Highlight should mention the ledger / tracked artifacts")

    # P1-2: conservation MR renamed to a non-regression diagnostic
    def test_p1_2_conservation_renamed_non_regression(self) -> None:
        self.assertIn("non-regression", self.tex.lower(),
                      "continuity/conservation MR must be qualified as a non-regression diagnostic")

    # P1-3: node-permutation tagged as pipeline-implementation sanity
    def test_p1_3_node_perm_tagged_pipeline_sanity(self) -> None:
        self.assertRegex(
            self.tex,
            r"pipeline-implementation sanity|implementation-level sanity|"
            r"structural (property|equivariance)[^.]*not a model-level",
            "node-permutation should be tagged as a pipeline/implementation sanity check",
        )

    # P1-4: Cliff's delta + Wilcoxon reported and declared
    def test_p1_4_effect_size_and_nonparametric_reported(self) -> None:
        self.assertIn("Cliff", self.tex, "Cliff's delta must be reported")
        self.assertIn("Wilcoxon", self.tex, "Wilcoxon test must be reported")

    # P1-6: S0 reuse of the pilot checkpoint disclosed
    def test_p1_6_s0_reuse_disclosed(self) -> None:
        self.assertRegex(
            self.tex.lower(),
            r"s0 reuses|reuses the (original )?pilot checkpoint|"
            r"s0 is the (original )?pilot checkpoint",
            "S0's reuse of the pilot checkpoint must be disclosed",
        )

    # P1-7: 2D verdict domain axis explicitly downgraded to structural placement
    def test_p1_7_verdict_axis_downgraded(self) -> None:
        self.assertRegex(
            self.tex,
            r"structural placement|not a calibrated (coordinate|score)|"
            r"qualitativ[^.]*not a calibrated",
            "the 2D verdict domain axis should be explicitly non-calibrated",
        )

    # P1-9: README thesis absorbs the R3 non-monotone finding
    def test_p1_9_readme_has_r3_finding(self) -> None:
        r = read(README).lower()
        self.assertTrue(
            ("non-monoton" in r) or ("shares the very symmetry" in r)
            or ("its own symmetry" in r),
            "README thesis should absorb the R3 non-monotone detection finding",
        )

    # P1-10: Threats cites Verdecchia 2023 + Empirical Standards
    def test_p1_10_threats_cites_standards(self) -> None:
        self.assertIn("verdecchia", read(BIB).lower(),
                      "references.bib should include Verdecchia 2023")
        self.assertIn("verdecchia", self.tex.lower(),
                      "Threats to Validity should cite Verdecchia 2023")
        self.assertIn("Empirical Standards", self.tex,
                      "Threats should reference the Empirical Standards for SE")

    # Regression: word count stays within the IST regular-paper hard cap. The
    # earlier working-target buffer (14500 -> 14900) was consumed by the P2
    # additions; only the hard cap is enforced now.
    def test_p1_word_count_still_within_cap(self) -> None:
        self.assertLessEqual(ist_word_count()["total"], 15000)


if __name__ == "__main__":
    unittest.main()
