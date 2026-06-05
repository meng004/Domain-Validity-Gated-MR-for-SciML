from pathlib import Path
import importlib.util
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_real_sut_mr.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_real_sut_mr", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _complete_fields() -> dict[str, str]:
    return {
        "run_id": "real-sut-x",
        "sut_id": "cylinder_flow_meshgraphnet",
        "sut_repo": "/repo",
        "sut_commit": "abc123",
        "checkpoint_path": "sut/checkpoint.pt",
        "checkpoint_sha256": "deadbeef",
        "dataset_root": "/data",
        "source_case_path": "case.npz",
        "mr_id": "mgn-node-permutation-equivariance",
        "command": "python3 tools/run_real_sut_mr.py --manifest m.yml",
        "raw_output_dir": "raw",
        "seed": "0",
        "device": "cpu",
        "python_version": "3.11.0",
        "framework_version": "torch 2.12.0",
    }


class RealSutRunnerContractTests(unittest.TestCase):
    def test_inverse_permutation_round_trips(self):
        runner = load_runner()
        perm = np.array([2, 0, 3, 1])
        inv = runner.inverse_permutation(perm)
        self.assertTrue(np.array_equal(perm[inv], np.arange(4)))
        self.assertTrue(np.array_equal(inv[perm], np.arange(4)))

    def test_validate_permutation_rejects_non_bijection(self):
        runner = load_runner()
        with self.assertRaises(ValueError):
            runner.validate_permutation(np.array([0, 0, 1]))

    def test_relative_l2_zero_for_identical_arrays(self):
        runner = load_runner()
        a = np.array([[1.0, 2.0], [3.0, 4.0]])
        self.assertEqual(runner.relative_l2(a, a), 0.0)
        self.assertGreater(runner.relative_l2(a + 1.0, a), 0.0)

    def test_equivariance_harness_is_zero_for_equivariant_forward(self):
        runner = load_runner()
        # A per-node forward (ignores edges) is exactly permutation equivariant.
        def forward(node_feat, edge_feat, edge_index):
            return node_feat[:, :2] * 3.0 - 1.0

        n = 6
        node_feat = np.random.default_rng(0).normal(size=(n, 4))
        edge_index = np.array([[0, 1, 2, 3], [1, 2, 3, 4]])
        edge_feat = np.zeros((edge_index.shape[1], 3))
        perm = np.random.default_rng(1).permutation(n)
        result = runner.node_permutation_equivariance(
            forward, node_feat, edge_feat, edge_index, perm
        )
        self.assertAlmostEqual(float(result["metric_value"]), 0.0, places=12)

    def test_equivariance_harness_is_nonzero_for_index_dependent_forward(self):
        runner = load_runner()
        # A forward that depends on absolute node index breaks equivariance.
        def forward(node_feat, edge_feat, edge_index):
            idx = np.arange(node_feat.shape[0]).reshape(-1, 1)
            return node_feat[:, :2] + idx

        n = 6
        node_feat = np.random.default_rng(2).normal(size=(n, 4))
        edge_index = np.array([[0, 1], [1, 2]])
        edge_feat = np.zeros((2, 3))
        perm = np.array([1, 0, 2, 3, 4, 5])
        result = runner.node_permutation_equivariance(
            forward, node_feat, edge_feat, edge_index, perm
        )
        self.assertGreater(float(result["metric_value"]), 0.0)

    def test_classify_verdict(self):
        runner = load_runner()
        self.assertEqual(runner.classify_verdict(0.0, 1e-6, "less_or_equal"), "pass")
        self.assertEqual(runner.classify_verdict(1e-3, 1e-6, "less_or_equal"), "fail")
        self.assertEqual(
            runner.classify_verdict(float("inf"), 1e-6, "less_or_equal"),
            "numerical-tolerance-issue",
        )

    def test_missing_manifest_fields_detected(self):
        runner = load_runner()
        fields = _complete_fields()
        del fields["checkpoint_sha256"]
        self.assertIn("checkpoint_sha256", runner.missing_manifest_fields(fields))
        self.assertEqual(runner.missing_manifest_fields(_complete_fields()), [])

    def test_metric_ledger_refuses_without_raw_outputs(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temp_dir:
            raw = Path(temp_dir)
            paths = {"source_output": raw / "missing_source_output.npy"}
            with self.assertRaises(ValueError):
                runner.build_metric_ledger(
                    fields=_complete_fields(),
                    source_case_id="c0",
                    follow_up_case_id="c0-perm",
                    metric_name="permutation_relative_l2_error",
                    metric_value=0.0,
                    tolerance={"assertion": "less_or_equal", "threshold": 1e-6},
                    verdict="pass",
                    raw_output_paths=paths,
                    evidence_artifact="raw",
                )

    def test_metric_ledger_has_all_required_fields_when_raw_outputs_exist(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temp_dir:
            raw = Path(temp_dir)
            source = raw / "source_output.npy"
            np.save(source, np.zeros((3, 2)))
            ledger = runner.build_metric_ledger(
                fields=_complete_fields(),
                source_case_id="c0",
                follow_up_case_id="c0-perm",
                metric_name="permutation_relative_l2_error",
                metric_value=0.0,
                tolerance={"assertion": "less_or_equal", "threshold": 1e-6},
                verdict="pass",
                raw_output_paths={"source_output": source},
                evidence_artifact="raw",
            )
            entry = ledger["entries"][0]
            for field in runner.METRIC_LEDGER_FIELDS:
                self.assertIn(field, entry)
            self.assertEqual(entry["verdict"], "pass")


if __name__ == "__main__":
    unittest.main()
