"""Guards for the continuous domain-violation score D (panel-review follow-up).

The committed domain_violation_report.json must place the synthetic symmetric
mesh near D=0 (admissible) and the real asymmetric eval mesh near D=0.51
(out-of-relation-domain), and both the manuscript and the IST package must cite
the operationalization with its honesty boundary intact.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/domain-violation-score/domain_violation_report.json"
MANUSCRIPT = ROOT / "paper/manuscript.md"
LATEX = ROOT / "paper/ist-submission/main.tex"


class TestDomainViolationScore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(REPORT.read_text())

    def test_symmetric_mesh_admissible(self):
        D = self.r["cases"]["mirror_y_synthetic_symmetric_mesh"]["D"]
        self.assertLess(D, 1e-6, "symmetric admissible mesh must score D ~ 0")

    def test_real_mesh_out_of_domain(self):
        D = self.r["cases"]["mirror_y_real_asymmetric_mesh"]["D"]
        self.assertTrue(0.45 <= D <= 0.55,
                        f"real asymmetric mesh D should be ~0.51, got {D}")

    def test_node_permutation_zero(self):
        self.assertEqual(self.r["cases"]["node_permutation_relation"]["D"], 0.0)

    def test_monotone_ordering(self):
        c = self.r["cases"]
        self.assertLess(c["mirror_y_synthetic_symmetric_mesh"]["D"],
                        c["mirror_y_real_asymmetric_mesh"]["D"])

    def test_honesty_boundary_present(self):
        self.assertIn("future work", self.r["honesty_boundary"])
        self.assertIn("Not a calibrated cross-MR", self.r["honesty_boundary"])


class TestPapersCiteD(unittest.TestCase):
    def test_both_files_cite_D(self):
        for p in (MANUSCRIPT, LATEX):
            t = p.read_text()
            self.assertTrue(re.search(r"D = m/\(m\+1\)|D = m/\(m \+ 1\)|D = m/\(m\+1\) ", t)
                            or "m/(m+1)" in t or "m/(m + 1)" in t,
                            f"{p.name} must define the domain-violation score D")
            self.assertIn("0.51", t)
            # The cross-class generalization must stay flagged as future work.
            self.assertIn("future work", t)


if __name__ == "__main__":
    unittest.main()
