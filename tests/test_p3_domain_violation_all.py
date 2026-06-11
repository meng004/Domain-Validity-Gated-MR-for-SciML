"""P3 guard: the all-MR domain-violation score report must exist, be sourced
entirely from committed artifacts, and stay within its honesty boundary."""
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/domain-violation-score-all/domain_violation_scores_all.json"
SINGLE = ROOT / "research_assets/runs/domain-violation-score/domain_violation_report.json"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"
TOOL = ROOT / "tools/compute_domain_violation_scores_all.py"
OLD_TOOL = ROOT / "tools/compute_domain_violation_score.py"

ALLOWED_STATUSES = {
    "operationalized-from-committed-data",
    "exact-by-construction",
    "not-operationalizable-from-committed-data",
}

EXPECTED_RELATION_IDS = {
    "mgn-node-permutation",
    "mgn-mirror-y-synthetic-symmetric-mesh",
    "mgn-mirror-y-real-asymmetric-mesh",
    "mgn-conservation-absolute-divergence-free",
    "mgn-operator-floor-diagnostic",
    "pinn-mr-a-collocation-permutation",
    "pinn-mr-b-mirror-y-burgers",
    "pinn-mr-b-mirror-y-heat",
    "pinn-mr-c-conservation-burgers",
    "pinn-mr-c-conservation-heat",
    "pinn-mr-c-conservation-k6-per-seed",
}


class P3DomainViolationAllTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text())
        cls.by_id = {e["relation_id"]: e for e in cls.report["relations"]}

    def test_report_and_tool_exist(self):
        self.assertTrue(REPORT.exists())
        self.assertTrue(TOOL.exists())
        # The single-relation script must remain untouched alongside.
        self.assertTrue(OLD_TOOL.exists())
        self.assertEqual(self.report["record_type"], "domain-violation-score-all")

    def test_covers_all_executed_mr_classes(self):
        self.assertEqual(set(self.by_id), EXPECTED_RELATION_IDS)

    def test_every_entry_well_formed(self):
        for e in self.report["relations"]:
            with self.subTest(relation=e["relation_id"]):
                self.assertIn(e["status"], ALLOWED_STATUSES)
                self.assertTrue(e["m_definition"].strip())
                self.assertTrue(e["honesty_boundary"].strip())
                self.assertIn(e["family"], {"MGN", "PINN"})

    def test_sources_exist_and_are_committed_paths(self):
        for e in self.report["relations"]:
            self.assertTrue(e["sources"], e["relation_id"])
            for s in e["sources"]:
                p = ROOT / s
                self.assertTrue(p.exists(), f"{e['relation_id']}: missing source {s}")
                self.assertFalse(Path(s).is_absolute(), s)

    def test_scores_in_range_with_saturating_map(self):
        for e in self.report["relations"]:
            if e["status"] == "not-operationalizable-from-committed-data":
                continue
            with self.subTest(relation=e["relation_id"]):
                m, d = e["m"], e["D"]
                self.assertGreaterEqual(m, 0.0)
                self.assertTrue(0.0 <= d < 1.0)
                self.assertTrue(math.isclose(d, m / (m + 1.0), rel_tol=1e-12, abs_tol=1e-300))

    def test_node_permutation_entries_are_exactly_zero(self):
        for rid in ("mgn-node-permutation", "pinn-mr-a-collocation-permutation"):
            e = self.by_id[rid]
            self.assertEqual(e["status"], "exact-by-construction")
            self.assertEqual(e["m"], 0.0)
            self.assertEqual(e["D"], 0.0)

    def test_mirror_y_consistent_with_single_relation_report(self):
        single = json.loads(SINGLE.read_text())
        d_old = single["cases"]["mirror_y_real_asymmetric_mesh"]["D"]
        d_new = self.by_id["mgn-mirror-y-real-asymmetric-mesh"]["D"]
        self.assertTrue(math.isclose(d_old, d_new, rel_tol=1e-9))
        # Real asymmetric mesh stays in the high-domain-violation half plane.
        self.assertGreater(d_new, 0.5)
        self.assertLess(self.by_id["mgn-mirror-y-synthetic-symmetric-mesh"]["D"], 1e-10)

    def test_not_operationalizable_entry_is_honest(self):
        e = self.by_id["pinn-mr-c-conservation-k6-per-seed"]
        self.assertEqual(e["status"], "not-operationalizable-from-committed-data")
        self.assertIsNone(e["m"])
        self.assertIsNone(e["D"])
        self.assertTrue(e.get("reason", "").strip())

    def test_heat_conservation_reference_exactly_conserved(self):
        e = self.by_id["pinn-mr-c-conservation-heat"]
        self.assertEqual(e["m"], 0.0)
        self.assertEqual(e["D"], 0.0)

    def test_top_level_honesty_boundary_forbids_calibration_claim(self):
        hb = self.report["honesty_boundary"]
        self.assertIn("NOT mutually calibrated", hb)
        self.assertIn("committed measurements", hb)

    def test_ledger_has_c17_multi_relation_claim(self):
        import yaml
        ledger = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))
        by_id = {c["claim_id"]: c for c in ledger["claims"]}
        self.assertIn("C17-domain-violation-score-all", by_id)
        c17 = by_id["C17-domain-violation-score-all"]
        self.assertEqual(c17["status"], "observed")
        # Every evidence path must exist, including the new report.
        self.assertIn(
            "research_assets/runs/domain-violation-score-all/domain_violation_scores_all.json",
            c17["evidence"])
        for ev in c17["evidence"]:
            self.assertTrue((ROOT / ev).exists(), ev)
        wording = " ".join(c17["wording_allowed"].split())
        self.assertIn("per-relation operationalization from committed measurements", wording)
        self.assertIn("not mutually calibrated across MR classes or domains", wording)
        # The forbidden-wording guard for cross-domain calibration claims.
        forbidden = " ".join(" ".join(c17["wording_forbidden"]).split())
        self.assertIn("calibrated or validated across domains", forbidden)

    def test_report_is_regenerable_deterministically(self):
        import subprocess, sys, tempfile, os
        before = self.report
        env = dict(os.environ)
        proc = subprocess.run(
            [sys.executable, str(TOOL)], cwd=ROOT, env=env,
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        after = json.loads(REPORT.read_text())
        b = {k: v for k, v in before.items() if k != "generated_at"}
        a = {k: v for k, v in after.items() if k != "generated_at"}
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
