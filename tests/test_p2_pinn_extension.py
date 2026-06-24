"""P2-1 regression guards for the cross-family PINN extension.

The committed pinn_mr_report.json must carry the three MR verdicts and the
rollout baseline; the manuscript Section 5.6.5 / LaTeX subsec:pinn-extension
must reference them; and the ledger C14 must remain status: observed with the
honesty boundaries intact.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINN_DIR = ROOT / "research_assets/runs/pinn-cross-family"
REPORT = PINN_DIR / "pinn_mr_report.json"
CKPT = PINN_DIR / "sut/checkpoint.pt"
MANIFEST = PINN_DIR / "checkpoint_manifest.json"
REF = PINN_DIR / "reference_solution.npz"
DIFF_DIR = ROOT / "research_assets/runs/pinn-cross-family-diffusion"
DIFF_REPORT = DIFF_DIR / "pinn_mr_report.json"
DIFF_CKPT = DIFF_DIR / "sut/checkpoint.pt"
DIFF_REF = DIFF_DIR / "reference_solution.npz"
MANUSCRIPT = ROOT / "manuscript/manuscript.md"
LATEX = ROOT / "manuscript/main.tex"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


class TestPinnArtifactsCommitted(unittest.TestCase):
    def test_all_artifacts_present(self):
        for p in (REPORT, CKPT, MANIFEST, REF,
                  DIFF_REPORT, DIFF_CKPT, DIFF_REF):
            self.assertTrue(p.exists(), f"missing PINN artifact: {p}")


class TestDiffusionPinnReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(DIFF_REPORT.read_text())

    def test_sut_identity(self):
        sut = self.r["sut"]
        self.assertEqual(sut["model_type"], "PINN")
        self.assertEqual(sut["pde_id"], "heat2d")
        self.assertEqual(sut["output_dim"], 1)
        self.assertTrue(sut["has_mirror_symmetry"])
        self.assertEqual(len(sut["checkpoint_sha256"]), 64)

    def test_three_mrs_pass(self):
        self.assertEqual(self.r["mr_A_permutation_equivariance"]["verdict"], "pass")
        b = self.r["mr_B_symmetry_equivariance"]
        self.assertEqual(b["verdict"], "pass")
        self.assertLess(b["ratio"], 1.0)
        c = self.r["mr_C_conservation"]
        self.assertEqual(c["verdict"], "pass")
        self.assertTrue(0.667 <= c["median_ratio"] <= 1.5)

    def test_rollout_present(self):
        self.assertLess(self.r["rollout_accuracy_baseline"]["median_relative_l2"], 0.1)


class TestPinnReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(REPORT.read_text())

    def test_sut_identity(self):
        sut = self.r["sut"]
        self.assertEqual(sut["model_type"], "PINN")
        self.assertEqual(sut["pde_id"], "burgers2d_viscous")
        self.assertEqual(sut["spatial_dim"], 2)
        self.assertEqual(sut["output_dim"], 2)
        self.assertTrue(sut["has_mirror_symmetry"])
        self.assertEqual(len(sut["checkpoint_sha256"]), 64)

    def test_three_mr_verdicts_match_committed_numbers(self):
        a = self.r["mr_A_permutation_equivariance"]
        self.assertEqual(a["verdict"], "pass")
        self.assertLess(a["violation"], a["tolerance"])
        b = self.r["mr_B_symmetry_equivariance"]
        self.assertEqual(b["verdict"], "pass")
        self.assertLess(b["ratio"], 1.0,
                        "MR-B ratio (violation/floor) must remain below 1 for pass")
        c = self.r["mr_C_conservation"]
        self.assertEqual(c["verdict"], "pass")
        self.assertTrue(0.667 <= c["median_ratio_ux"] <= 1.5)

    def test_rollout_baseline_present(self):
        rb = self.r["rollout_accuracy_baseline"]
        self.assertIn("median_relative_l2", rb)
        self.assertLess(rb["median_relative_l2"], 0.1,
                        "rollout median rel L2 should be small for a converged PINN")

    def test_honesty_boundary_intact(self):
        self.assertIn("One PINN", self.r["honesty_boundary"])
        self.assertIn("Not a generalization", self.r["honesty_boundary"])


class TestManuscriptSyncedToReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = MANUSCRIPT.read_text()
        cls.l = LATEX.read_text()
        cls.led = LEDGER.read_text()

    def test_manuscript_subsection_present(self):
        self.assertIn("Cross-family PINN extension", self.m)
        self.assertIn("Cross-family PINN extension", self.l)

    def test_headline_numbers_present(self):
        # K=15 PINN roster headline values must stay synchronized.
        # Numbers updated from n=3 to n=15 seeds per PDE (pinn_k6_aggregate.json
        # generated 2026-06-15; old 0.615/1.682/0.992 were n=3 means, now superseded).
        for txt in (self.m, self.l):
            self.assertTrue(re.search(r"K=6 roster|K=6 PINN roster|K=15 PINN roster|K=15 roster", txt),
                            "subsection must frame the executed PINN roster")
            self.assertTrue(re.search(r"0\.712", txt),
                            "MR-B Burgers K=15 mean ratio 0.712 must be cited")
            self.assertTrue(re.search(r"1\.495", txt),
                            "MR-B heat K=15 mean ratio 1.495 must be cited")
            self.assertTrue(re.search(r"1\.007", txt),
                            "MR-C Burgers K=15 mean ratio 1.007 must be cited")
            self.assertTrue(re.search(r"1\.006", txt),
                            "MR-C heat K=15 mean ratio 1.006 must be cited")
            self.assertTrue(re.search(r"mixed", txt),
                            "heat MR-B must stay reported as mixed")
            # MR-A must stay flagged as evidentially vacuous for the PINN, so a
            # future edit cannot silently re-inflate the cross-family MR count.
            self.assertTrue(re.search(r"vacuous by construction", txt),
                            "MR-A must be marked vacuous-by-construction for the PINN")
            self.assertTrue(re.search(r"two non-trivial MR", txt),
                            "cross-family evidence must be attributed to the two "
                            "non-trivial MRs (MR-B, MR-C), not all three")

    def test_ledger_C14_observed(self):
        self.assertIn('claim_id: "C14-cross-family-pinn-extension"', self.led)
        m = re.search(r'claim_id: "C14-cross-family-pinn-extension"\s*\n\s*status:\s*"([^"]+)"',
                      self.led)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "observed")


if __name__ == "__main__":
    unittest.main()
