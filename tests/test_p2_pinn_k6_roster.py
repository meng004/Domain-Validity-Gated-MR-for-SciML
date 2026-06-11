"""Phase-2 guards for the committed PINN K=6 roster aggregate."""
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
            for seed in range(3):
                d = ROSTER / f"{pde}_s{seed}"
                for rel in ("manifest.json", "mr_report.json", "sut/checkpoint.pt"):
                    self.assertTrue((d / rel).exists(), f"missing {d / rel}")


class TestPinnK6Aggregate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(AGG.read_text())

    def test_roster_shape(self):
        self.assertEqual(self.r["record_type"], "pinn-k6-roster-aggregate")
        self.assertEqual(self.r["n_seeds"], 3)
        self.assertEqual(self.r["seeds"], [0, 1, 2])
        self.assertEqual(self.r["train_iters"], 2000)
        self.assertEqual(self.r["train_batch_size"], 512)
        self.assertEqual(len(self.r["per_sut"]), 6)
        self.assertEqual({x["pde"] for x in self.r["per_sut"]}, {"burgers", "diffusion"})

    def test_family_bootstrap_fields(self):
        for fam in self.r["per_pde_family"].values():
            for key in ("mr_b_ratio_95ci", "mr_c_median_95ci", "rollout_95ci"):
                self.assertEqual(len(fam[key]), 2)
                self.assertLessEqual(fam[key][0], fam[key][1])
            self.assertIn("mr_b_verdict_counts", fam)
            self.assertIn("mr_c_verdict_counts", fam)
            self.assertIn("mr_b_pass_rate", fam)
            self.assertIn("mr_c_pass_rate", fam)

    def test_committed_headline_results(self):
        burgers = self.r["per_pde_family"]["burgers"]
        diffusion = self.r["per_pde_family"]["diffusion"]

        self.assertTrue(burgers["mr_a_all_pass"])
        self.assertEqual(burgers["mr_b_verdict_counts"], {"pass": 3})
        self.assertEqual(burgers["mr_c_verdict_counts"], {"pass": 3})
        self.assertLess(burgers["rollout_mean"], 0.04)

        self.assertTrue(diffusion["mr_a_all_pass"])
        self.assertEqual(diffusion["mr_b_verdict_counts"], {"fail": 2, "pass": 1})
        self.assertEqual(diffusion["mr_b_verdict"], "mixed")
        self.assertEqual(diffusion["mr_c_verdict_counts"], {"pass": 3})
        self.assertLess(diffusion["rollout_mean"], 0.05)


if __name__ == "__main__":
    unittest.main()
