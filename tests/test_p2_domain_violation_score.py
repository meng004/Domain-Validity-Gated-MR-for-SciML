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
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
LATEX = ROOT / "submissions/IST/main.tex"


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


class TestGenericMRBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = ROOT / "research_assets/runs/generic-mr-baseline/generic_mr_report.json"
        cls.r = json.loads(p.read_text())

    def test_admit_count_and_overlap(self):
        # 3/13 admitted, and every admitted template coincides with a paper MR.
        self.assertEqual(self.r["n_templates"], 13)
        self.assertEqual(self.r["n_admitted_by_predicate"], 3)
        self.assertEqual(set(self.r["admitted_template_ids"]),
                         set(self.r["admitted_overlapping_paper_mrs"]))

    def test_basis_is_dominant_rejection(self):
        fb = self.r["rejection_breakdown_by_failed_condition"]
        self.assertEqual(fb["physical_or_software_basis"], 9)

    def test_papers_cite_generic_baseline(self):
        for p in (MANUSCRIPT, LATEX):
            t = p.read_text()
            self.assertIn("3/13", t)
            self.assertTrue(re.search(r"generic-MR|generic MR", t))


if __name__ == "__main__":
    unittest.main()
