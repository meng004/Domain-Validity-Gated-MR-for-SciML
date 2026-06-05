from pathlib import Path
import importlib.util
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_mr_asset.py"
VERDICT_PATH = ROOT / "research_assets" / "runs" / "node_permutation_fixture_verdict.json"
VERDICT_SCHEMA_PATH = ROOT / "research_assets" / "ledgers" / "verdict_ledger.schema.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_mr_asset", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExecutableMRAssetTests(unittest.TestCase):
    def test_node_permutation_fixture_runner_writes_pass_verdict_without_sut_claim(self):
        runner = load_runner()
        result = runner.run_node_permutation_fixture(ROOT)
        self.assertEqual(result["mr_id"], "mgn-node-permutation-equivariance")
        self.assertEqual(result["execution_profile"], "fixture-transform-metric-only")
        self.assertEqual(result["sut_execution"], "not-run")
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["metric"]["value"], 0.0)
        self.assertEqual(
            result["transformed_graph"],
            {
                "x": [[3.0, 1.0], [1.0, 0.0], [2.0, 0.0]],
                "pos": [[0.5, 1.0], [0.0, 0.0], [1.0, 0.0]],
                "face": [[1, 2, 0]],
            },
        )
        self.assertTrue(VERDICT_PATH.exists())

        recorded = json.loads(VERDICT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(recorded["entries"][0]["verdict"], "pass")
        self.assertEqual(recorded["entries"][0]["sut_execution"], "not-run")
        self.assertEqual(recorded["entries"][0]["transformed_graph"]["face"], [[1, 2, 0]])
        self.assertIn(
            "does not report MeshGraphNets inference",
            recorded["claim_limitations"],
        )

    def test_fixture_verdict_profile_is_declared_in_schema(self):
        schema = json.loads(VERDICT_SCHEMA_PATH.read_text(encoding="utf-8"))
        evidence_levels = schema["properties"]["evidence_level"]["enum"]
        entry_properties = schema["properties"]["entries"]["items"]["properties"]

        self.assertIn("fixture-transform-metric-only", evidence_levels)
        self.assertIn("execution_profile", entry_properties)
        self.assertIn("sut_execution", entry_properties)
        self.assertIn("transformed_graph", entry_properties)

    def test_runner_rejects_invalid_node_permutations(self):
        runner = load_runner()
        with self.assertRaises(ValueError):
            runner.validate_permutation([0, 0, 1], 3)
        with self.assertRaises(ValueError):
            runner.validate_permutation([0, -1, 2], 3)
        with self.assertRaises(ValueError):
            runner.validate_inverse_permutation([2, 0, 1], [2, 1, 0])
        with self.assertRaises(ValueError):
            runner.validate_face_indices([[-1, 0, 1]], 3)
        with self.assertRaises(ValueError):
            runner.validate_face_indices([[0, 1, 3]], 3)


if __name__ == "__main__":
    unittest.main()
