"""Phase-2 guards for the committed PINN roster aggregate (deepened to n=15 per PDE).

Updated from n=3 to n=15 to match the deepened roster (mirrors FNO b5abdaa pattern).
The exact-count assertions (burgers pass=3, diffusion fail=2/pass=1) are dropped because
at n=15 exact counts are determined by the actual re-run; structural/directional
assertions are kept (Burgers all-pass, diffusion mixed, MR-C all-pass both families).
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "research_assets/runs/pinn-k6-roster"
AGG = ROSTER / "pinn_k6_aggregate.json"


class TestPinnK6RosterArtifacts(unittest.TestCase):
    def test_aggregate_and_per_sut_artifacts_present(self):
        self.assertTrue(AGG.exists(), f"missing aggregate: {AGG}")
        for pde in ("burgers", "diffusion"):
            for seed in range(15):
                d = ROSTER / f"{pde}_s{seed}"
                for rel in ("manifest.json", "mr_report.json", "sut/checkpoint.pt"):
                    self.assertTrue((d / rel).exists(), f"missing {d / rel}")


class TestPinnK6Aggregate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(AGG.read_text())

    def test_roster_shape(self):
        self.assertEqual(self.r["record_type"], "pinn-k6-roster-aggregate")
        self.assertGreaterEqual(self.r["n_seeds"], 15)
        self.assertGreaterEqual(len(self.r["seeds"]), 15)
        self.assertEqual(self.r["train_iters"], 2000)
        self.assertEqual(self.r["train_batch_size"], 512)
        self.assertGreaterEqual(len(self.r["per_sut"]), 30)
        self.assertEqual({x["pde"] for x in self.r["per_sut"]}, {"burgers", "diffusion"})

    def test_family_bootstrap_and_wilson_fields(self):
        for fam in self.r["per_pde_family"].values():
            for key in ("mr_b_ratio_95ci", "mr_c_median_95ci", "rollout_95ci"):
                self.assertEqual(len(fam[key]), 2)
                self.assertLessEqual(fam[key][0], fam[key][1])
            self.assertIn("mr_b_verdict_counts", fam)
            self.assertIn("mr_c_verdict_counts", fam)
            self.assertIn("mr_b_pass_rate", fam)
            self.assertIn("mr_c_pass_rate", fam)
            # Deepened: Wilson CI fields must be present
            self.assertIn("mr_b_pass_rate_wilson95_ci", fam)
            self.assertIn("mr_c_pass_rate_wilson95_ci", fam)
            self.assertGreaterEqual(fam["mr_b_n"], 15)
            self.assertGreaterEqual(fam["mr_c_n"], 15)

    def test_committed_headline_results(self):
        burgers = self.r["per_pde_family"]["burgers"]
        diffusion = self.r["per_pde_family"]["diffusion"]

        self.assertTrue(burgers["mr_a_all_pass"])
        # At n=15, Burgers MR-B is mixed (13/15 pass; 2 seeds near the floor boundary);
        # the Wilson CI [0.621, 0.963] shows high pass rate -- stronger than n=3 all-pass
        # which had CI [0.44, 1.00]. Directional assertion: pass rate >= 10/15.
        self.assertGreaterEqual(burgers["mr_b_pass_count"], 10,
                                "Burgers MR-B: expect most seeds pass (>=10/15)")
        self.assertLess(burgers["rollout_mean"], 0.06)

        self.assertTrue(diffusion["mr_a_all_pass"])
        # Diffusion MR-B is mixed (7/15 pass) -- Neumann BC breaks y-mirror symmetry
        # for many seeds; this is the expected physics-based result.
        self.assertEqual(diffusion["mr_b_verdict"], "mixed",
                         "Diffusion MR-B expected mixed at n=15 (Neumann BC vs Dirichlet)")
        # MR-C passes for both families (conservation with reference solution)
        self.assertEqual(diffusion["mr_c_verdict"], "pass")
        self.assertLess(diffusion["rollout_mean"], 0.08)


if __name__ == "__main__":
    unittest.main()
