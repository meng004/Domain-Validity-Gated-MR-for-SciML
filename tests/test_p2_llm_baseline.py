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
SCORER = ROOT / "tools/score_llm_mr_baseline.py"


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


if __name__ == "__main__":
    unittest.main()
