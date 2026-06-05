from pathlib import Path
import importlib.util
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_mirror_y_ood_stress.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_mirror_y_ood_stress", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _involution_pi(n):
    # adjacent-pair swap: a perfect reflection-like involution for n even
    pi = np.arange(n)
    pi[0::2], pi[1::2] = np.arange(1, n, 2), np.arange(0, n, 2)
    return pi


class MirrorYRunnerContractTests(unittest.TestCase):
    def test_mirror_velocity_flips_v_and_permutes(self):
        runner = load_runner()
        v = np.array([[1.0, 2.0], [3.0, 4.0]])
        pi = np.array([1, 0])
        out = runner.mirror_velocity_field(v, pi)
        self.assertTrue(np.array_equal(out, np.array([[3.0, -4.0], [1.0, -2.0]])))

    def test_mirror_prediction_flips_v_and_permutes(self):
        runner = load_runner()
        p = np.array([[1.0, 2.0], [3.0, 4.0]])
        pi = np.array([1, 0])
        out = runner.mirror_prediction(p, pi)
        self.assertTrue(np.array_equal(out, np.array([[3.0, -4.0], [1.0, -2.0]])))

    def test_probe_zero_for_mirror_equivariant_forward(self):
        runner = load_runner()
        # Elementwise scaling commutes with the mirror construction -> V == 0.
        def predict(v):
            return 2.0 * v

        n = 8
        v = np.random.default_rng(0).normal(size=(n, 2))
        pi = _involution_pi(n)
        out = runner.mirror_y_probe(predict, v, pi)
        self.assertAlmostEqual(float(out["violation"]), 0.0, places=12)
        self.assertAlmostEqual(float(out["mapping_error_floor"]), 0.0, places=12)

    def test_probe_nonzero_for_non_equivariant_forward(self):
        runner = load_runner()
        # Adding a constant to the y-channel breaks mirror equivariance.
        def predict(v):
            out = v.copy()
            out[:, 1] = v[:, 1] + 1.0
            return out

        n = 8
        v = np.random.default_rng(1).normal(size=(n, 2))
        pi = _involution_pi(n)
        out = runner.mirror_y_probe(predict, v, pi)
        self.assertGreater(float(out["violation"]), 0.0)

    def test_aggregate_violation_rate_keeps_all_frames_in_denominator(self):
        runner = load_runner()
        entries = [
            {"frame": 0, "verdict": "fail", "metric_value": 0.69, "violation_over_floor": 3.5},
            {"frame": 1, "verdict": "fail", "metric_value": 0.73, "violation_over_floor": 3.3},
            {"frame": 2, "verdict": "inconclusive", "metric_value": 0.10, "violation_over_floor": 1.1},
        ]
        agg = runner.aggregate_violation_rate(entries)
        # denominator includes the inconclusive frame; it is not silently dropped
        self.assertEqual(agg["n_frames"], 3)
        self.assertEqual(agg["n_fail"], 2)
        self.assertEqual(agg["n_inconclusive"], 1)
        self.assertEqual(agg["n_pass"], 0)
        self.assertEqual(agg["verdict_counts"]["fail"], 2)
        self.assertAlmostEqual(agg["violation_rate"], 2.0 / 3.0, places=10)
        self.assertAlmostEqual(agg["median_violation"], 0.69, places=10)

    def test_metric_ledger_refuses_without_raw_outputs(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temp_dir:
            raw = Path(temp_dir)
            with self.assertRaises(ValueError):
                runner.build_mirror_metric_ledger(
                    fields=_complete_fields(),
                    entries=[{"frame": 0}],
                    raw_output_paths={"source_output": raw / "missing.npy"},
                    precondition_decision="out-of-relation-domain",
                )

    def test_metric_ledger_has_required_fields_when_raw_outputs_exist(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temp_dir:
            raw = Path(temp_dir)
            for name in ("source_output", "follow_up_output", "mapped_output"):
                np.save(raw / f"{name}.npy", np.zeros((2, 2)))
            entry = runner.build_entry(
                fields=_complete_fields(),
                frame=0,
                violation=0.7,
                floor=0.15,
                verdict="fail",
                tolerance={"assertion": "less_or_equal", "threshold": 1e-6},
                evidence_artifact="raw",
            )
            ledger = runner.build_mirror_metric_ledger(
                fields=_complete_fields(),
                entries=[entry],
                raw_output_paths={
                    name: raw / f"{name}.npy"
                    for name in ("source_output", "follow_up_output", "mapped_output")
                },
                precondition_decision="out-of-relation-domain",
            )
            from importlib import import_module  # noqa: F401
            import sys
            sys.path.insert(0, str(ROOT / "tools"))
            from manifest_contract import METRIC_LEDGER_FIELDS
            for field in METRIC_LEDGER_FIELDS:
                self.assertIn(field, ledger["entries"][0])
            self.assertEqual(ledger["entries"][0]["verdict"], "fail")
            self.assertEqual(ledger["exact_relation_verdict"], "out-of-relation-domain")


def _complete_fields() -> dict[str, str]:
    return {
        "run_id": "real-sut-mirror-y-x",
        "sut_id": "cylinder_flow_meshgraphnet",
        "sut_repo": "/repo",
        "sut_commit": "abc123",
        "checkpoint_path": "sut/checkpoint.pt",
        "checkpoint_sha256": "deadbeef",
        "dataset_root": "/data",
        "source_case_path": "case.npz",
        "mr_id": "mgn-mirror-y-equivariance",
        "command": "python3 tools/run_mirror_y_ood_stress.py --manifest m.yml",
        "raw_output_dir": "raw",
        "seed": "0",
        "device": "cpu",
        "python_version": "3.11.0",
        "framework_version": "torch 2.12.0",
        "mirror_axis": "0.205",
    }


if __name__ == "__main__":
    unittest.main()
