"""P2-2 guards for the LLM-MR baseline pipeline.

The pipeline is committed as a reproducible-by-protocol baseline: when
OPENAI_API_KEY + OPENAI_BASE_URL are set, `tools/run_llm_mr_baseline.py` calls
the bltcy gateway and writes candidates; otherwise it fails closed without
fabricating any output. The scorer then grades candidates against this paper's
admissibility predicate. These tests check the contract (CLI shape, fail-closed
behavior, scorer schema) without requiring real credentials.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_llm_mr_baseline.py"
RATER = ROOT / "tools/rate_llm_mr_baseline.py"
SCORER = ROOT / "tools/score_llm_mr_baseline.py"
sys.path.insert(0, str(ROOT / "tools"))
import rate_llm_mr_baseline as R  # noqa: E402


class TestRunnerFailsClosedWithoutCredentials(unittest.TestCase):
    def test_fail_closed_returns_nonzero_no_output(self):
        with tempfile.TemporaryDirectory() as td:
            env = {**os.environ}
            env.pop("OPENAI_API_KEY", None)
            env.pop("OPENAI_BASE_URL", None)
            proc = subprocess.run(
                [sys.executable, str(RUNNER), "--outdir", td],
                env=env, capture_output=True, text=True, timeout=15)
            self.assertNotEqual(proc.returncode, 0,
                                "runner must fail closed without credentials")
            self.assertIn("BLOCKED_NO_LLM_CREDENTIALS", proc.stderr)
            # No files written.
            self.assertEqual(list(Path(td).iterdir()), [])


class TestScorerHandlesMissingInput(unittest.TestCase):
    def test_scorer_blocks_when_candidates_missing(self):
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "no_such.json"
            out = Path(td) / "report.json"
            proc = subprocess.run(
                [sys.executable, str(SCORER),
                 "--input", str(missing), "--output", str(out)],
                capture_output=True, text=True, timeout=15)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("BLOCKED_NO_LLM_OUTPUT", proc.stderr)


class TestScorerGradesStubCandidates(unittest.TestCase):
    def _stub(self) -> dict:
        return {
            "model_used": "stub-model",
            "candidates": [
                # 1. exact recovery of this paper's node-permutation MR (should admit + overlap)
                {"name": "node_permutation_equivariance_stub",
                 "source_transformation": "permute node ordering",
                 "expected_relation": "f(perm(x)) == perm(f(x))",
                 "tolerance_rationale": "1e-6, dominates float32 rounding floor near machine precision",
                 "physical_basis": "graph-isomorphism invariance / software contract",
                 "preconditions": "fixed mesh; identical initial field; same Reynolds regime",
                 "boundary_output_compatibility": "BC indices are permuted consistently; preserve",
                 "expected_admissibility_class": "exact"},
                # 2. divergence-free conservation (overlap; admitted via floor language)
                {"name": "incompressibility_diagnostic",
                 "source_transformation": "identity",
                 "expected_relation": "div(u_pred) ~ 0",
                 "tolerance_rationale": "must dominate the P1 discrete divergence operator floor at mesh size h",
                 "physical_basis": "mass conservation for incompressible flow",
                 "preconditions": "incompressible regime; admissible mesh",
                 "boundary_output_compatibility": "consistent at no-slip walls",
                 "expected_admissibility_class": "approximate_OOD_stress"},
                # 3. ill-specified: no floor in tolerance, no preconditions -> qualified at best
                {"name": "rotational_invariance",
                 "source_transformation": "rotate domain by 90 degrees",
                 "expected_relation": "f(R x) == R f(x)",
                 "tolerance_rationale": "small",
                 "physical_basis": "rotation symmetry of Navier-Stokes",
                 "preconditions": "",
                 "boundary_output_compatibility": "no, cylinder breaks rotational symmetry",
                 "expected_admissibility_class": "exact"},
            ],
        }

    def test_predicate_and_overlap(self):
        with tempfile.TemporaryDirectory() as td:
            cand = Path(td) / "llm_candidates.json"
            cand.write_text(json.dumps(self._stub()))
            out = Path(td) / "report.json"
            proc = subprocess.run(
                [sys.executable, str(SCORER),
                 "--input", str(cand), "--output", str(out)],
                capture_output=True, text=True, timeout=15)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = json.loads(out.read_text())
            self.assertEqual(report["n_candidates"], 3)
            # Candidates 1 and 2 should pass the predicate; candidate 3 has
            # boundary_output_compatibility="no, cylinder breaks..." -> reject.
            self.assertGreaterEqual(report["n_admitted_by_predicate"], 2)
            self.assertLess(report["n_admitted_by_predicate"], 3)
            # Overlap with paper MRs: at least node-perm and conservation hits.
            self.assertGreaterEqual(report["per_paper_mr_overlap_count"][
                "node_permutation_equivariance"], 1)
            self.assertGreaterEqual(report["per_paper_mr_overlap_count"][
                "discrete_divergence_free_conservation"], 1)
            # Per-candidate structure carries the four predicate dimensions.
            for g in report["per_candidate"]:
                self.assertEqual(set(g["dimensions"]),
                                 {"physical_basis", "preconditions",
                                  "boundary_output_compatibility",
                                  "numerical_decidability"})


class TestRaterFailsClosedWithoutCredentials(unittest.TestCase):
    def test_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            env = {**os.environ}
            env.pop("OPENAI_API_KEY", None)
            env.pop("OPENAI_BASE_URL", None)
            # Provide a placeholder candidates file so the credentials check
            # is what fails, not the missing input.
            cand = Path(td) / "llm_candidates.json"
            cand.write_text(json.dumps({"candidates": [{"name": "x"}]}))
            out = Path(td) / "llm_votes.json"
            proc = subprocess.run(
                [sys.executable, str(RATER),
                 "--input", str(cand), "--output", str(out)],
                env=env, capture_output=True, text=True, timeout=15)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("BLOCKED_NO_LLM_CREDENTIALS", proc.stderr)
            self.assertFalse(out.exists())


def _stub_votes(name_label_map: dict, raters: list[str]) -> list[dict]:
    """Helper: build the per_candidate_votes structure rate_llm_mr_baseline emits."""
    out = []
    for name, per_rater_labels in name_label_map.items():
        per_rater = {r: {"vote": per_rater_labels[r], "justification": ""}
                     for r in raters if r in per_rater_labels}
        out.append({"name": name, "per_rater": per_rater,
                    "majority": R.majority(per_rater)})
    return out


class TestRaterAggregation(unittest.TestCase):
    def test_majority_tie_resolves_to_borderline(self):
        per_rater = {"r1": {"vote": "valid"}, "r2": {"vote": "invalid"}}
        self.assertEqual(R.majority(per_rater), "borderline")

    def test_majority_picks_strict_winner(self):
        per_rater = {"r1": {"vote": "valid"}, "r2": {"vote": "valid"},
                     "r3": {"vote": "invalid"}}
        self.assertEqual(R.majority(per_rater), "valid")

    def test_fleiss_kappa_one_when_all_agree(self):
        raters = ["r1", "r2", "r3"]
        # Three raters, three items, full agreement on a mix of labels.
        votes = _stub_votes(
            {"a": {r: "valid" for r in raters},
             "b": {r: "invalid" for r in raters},
             "c": {r: "borderline" for r in raters}},
            raters)
        k = R.fleiss_kappa(votes, raters)
        self.assertIsNotNone(k)
        self.assertAlmostEqual(k, 1.0, places=6)

    def test_pra_and_unanimous_split(self):
        raters = ["r1", "r2", "r3"]
        votes = _stub_votes(
            {"a": {"r1": "valid", "r2": "valid", "r3": "valid"},      # unanimous
             "b": {"r1": "valid", "r2": "invalid", "r3": "valid"}},   # 2/3 agree
            raters)
        pra, un = R.pointwise_agreement(votes, raters)
        # 6 pairs total (3+3), 4 agree (3 from a + 1 from b) => 4/6.
        self.assertAlmostEqual(pra, 4 / 6, places=6)
        self.assertAlmostEqual(un, 0.5, places=6)


class TestScorerMergesVotesWhenPresent(unittest.TestCase):
    def test_merge(self):
        with tempfile.TemporaryDirectory() as td:
            cand = Path(td) / "llm_candidates.json"
            cand.write_text(json.dumps({
                "candidates": [
                    {"name": "node_perm", "source_transformation": "permute nodes",
                     "expected_relation": "f(perm(x)) == perm(f(x))",
                     "tolerance_rationale": "1e-6, floor at machine precision",
                     "physical_basis": "graph-isomorphism invariance",
                     "preconditions": "fixed mesh; identical field",
                     "boundary_output_compatibility": "preserve",
                     "expected_admissibility_class": "exact"},
                ]}))
            votes = Path(td) / "llm_votes.json"
            votes.write_text(json.dumps({
                "fleiss_kappa": 0.5,
                "raw_pointwise_agreement": 0.9,
                "item_unanimous_rate": 0.8,
                "constant_raters_excluded_from_kappa": [],
                "per_candidate_votes": [
                    {"name": "node_perm",
                     "per_rater": {"glm-5.1": {"vote": "valid"},
                                   "kimi-k2.6": {"vote": "valid"},
                                   "deepseek-v4-flash": {"vote": "borderline"}},
                     "majority": "valid"},
                ]}))
            out = Path(td) / "report.json"
            proc = subprocess.run(
                [sys.executable, str(SCORER),
                 "--input", str(cand), "--votes", str(votes),
                 "--output", str(out)],
                capture_output=True, text=True, timeout=15)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rep = json.loads(out.read_text())
            self.assertTrue(rep["rater_panel_present"])
            self.assertEqual(rep["rater_panel_fleiss_kappa"], 0.5)
            self.assertEqual(rep["n_panel_majority_valid"], 1)
            self.assertEqual(rep["n_admitted_by_predicate_and_panel_valid"], 1)
            self.assertEqual(rep["per_candidate"][0]["rater_panel"]["majority"], "valid")


if __name__ == "__main__":
    unittest.main()
