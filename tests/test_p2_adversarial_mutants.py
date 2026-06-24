"""P2-3 regression guards for the adversarial-mutants result.

The committed adversarial_mutants_report.json must carry the two-mutant
catalogue (A1 uniform_vx_offset, A2 vx_plus_squared_vy), the per-mutant
per-detector counts, and the headline finding that A2 evades every detector
(0/6) while A1 is caught only by mirror-y on a magnitude shift (not by
node-permutation or conservation). The manuscript R4 paragraph must carry
those numbers and the "subspace, not a point" framing.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/adversarial-mutants-e3-extra/adversarial_mutants_report.json"
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
LATEX = ROOT / "manuscript/main.tex"


class TestAdversarialReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(REPORT.read_text())

    def test_two_mutants_present(self):
        names = [m["id"] for m in self.r["adversarial_mutants"]]
        self.assertIn("ADV_uniform_vx_offset", names)
        self.assertIn("ADV_vx_plus_squared_vy", names)

    def test_a2_evades_every_detector(self):
        per = self.r["per_mutant_detection_rate"]["ADV_vx_plus_squared_vy"]["per_detector"]
        for det in ("node_perm", "conservation", "mirror_y", "any"):
            self.assertEqual(per[det]["k"], 0,
                             f"A2 should be missed by {det} on every checkpoint")
            self.assertEqual(per[det]["n"], 6)

    def test_a1_only_mirror_y_fires(self):
        per = self.r["per_mutant_detection_rate"]["ADV_uniform_vx_offset"]["per_detector"]
        self.assertEqual(per["node_perm"]["k"], 0,
                         "A1 must NOT be caught by node-perm (would invalidate the framing)")
        self.assertEqual(per["conservation"]["k"], 0,
                         "A1 must NOT be caught by conservation")
        self.assertEqual(per["mirror_y"]["k"], 6,
                         "A1 IS caught by mirror-y on magnitude shift (per the manuscript)")

    def test_six_suts_each(self):
        for m in ("ADV_uniform_vx_offset", "ADV_vx_plus_squared_vy"):
            for det in ("node_perm", "conservation", "mirror_y", "any"):
                self.assertEqual(
                    self.r["per_mutant_detection_rate"][m]["per_detector"][det]["n"], 6)


class TestManuscriptR4Section(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = MANUSCRIPT.read_text()
        cls.l = LATEX.read_text()

    def test_manuscript_r4_present(self):
        self.assertIn("Adversarial mutants (R4)", self.m)
        self.assertIn("subspace, not a point", self.m)
        self.assertIn("A2 escapes every detector", self.m)

    def test_latex_r4_present(self):
        self.assertIn("Adversarial mutants (R4)", self.l)
        self.assertIn("subspace, not a point", self.l)

    def test_r4_explains_a1_is_magnitude_not_symmetry(self):
        for txt in (self.m, self.l):
            self.assertTrue(
                re.search(r"magnitude", txt) and re.search(r"node-permutation 0/6", txt),
                "R4 must explain that A1's detection is magnitude-driven, "
                "not via node-perm or conservation")


if __name__ == "__main__":
    unittest.main()
