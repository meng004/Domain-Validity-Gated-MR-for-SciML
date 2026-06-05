from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_conservation_diagnostic.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_conservation_diagnostic", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _unit_square():
    pos = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    cells = np.array([[0, 1, 2], [0, 2, 3]])
    return pos, cells


def _complete_fields() -> dict[str, str]:
    return {
        "run_id": "real-sut-conservation-x",
        "sut_id": "cylinder_flow_meshgraphnet",
        "sut_repo": "/repo",
        "sut_commit": "abc123",
        "checkpoint_path": "sut/checkpoint.pt",
        "checkpoint_sha256": "deadbeef",
        "dataset_root": "/data",
        "source_case_path": "case.npz",
        "mr_id": "mgn-discrete-divergence-boundedness",
        "command": "python3 tools/run_conservation_diagnostic.py --manifest m.yml",
        "raw_output_dir": "raw",
        "seed": "0",
        "device": "cpu",
        "python_version": "3.11.0",
        "framework_version": "torch 2.12.0",
        "regression_threshold": "1.5",
    }


class ConservationRunnerContractTests(unittest.TestCase):
    def test_probe_computes_ratio_from_injected_prediction(self):
        runner = load_runner()
        pos, cells = _unit_square()
        vel_t = np.zeros((4, 2))
        vel_t1 = np.stack([-pos[:, 1], pos[:, 0]], axis=-1)  # divergence-free reference

        # A prediction equal to a 2x expansion field has div_rms = 2.
        def predict_next(_v):
            return np.stack([2 * pos[:, 0], 2 * pos[:, 1]], axis=-1)

        out = runner.conservation_probe(predict_next, pos, cells, vel_t, vel_t1)
        self.assertAlmostEqual(out["divergence_pred_rms"], 4.0, places=10)
        self.assertAlmostEqual(out["divergence_reference_rms"], 0.0, places=10)
        # reference zero -> ratio is infinite -> verdict logic handles inconclusive
        self.assertFalse(np.isfinite(out["ratio"]))

    def test_probe_ratio_near_one_for_matching_divergence(self):
        runner = load_runner()
        pos, cells = _unit_square()
        ref = np.stack([2 * pos[:, 0], -3 * pos[:, 1]], axis=-1)  # div_rms = 1

        def predict_next(_v):
            return np.stack([2 * pos[:, 0], -3 * pos[:, 1]], axis=-1)

        out = runner.conservation_probe(predict_next, pos, cells, np.zeros((4, 2)), ref)
        self.assertAlmostEqual(out["ratio"], 1.0, places=10)

    def test_probe_reports_interior_only_ratio_when_node_types_given(self):
        runner = load_runner()
        pos, cells = _unit_square()
        ref = np.stack([2 * pos[:, 0], -3 * pos[:, 1]], axis=-1)
        node_type = np.array([0, 6, 0, 0])  # node 1 is wall -> cell 0 excluded

        def predict_next(_v):
            return np.stack([2 * pos[:, 0], -3 * pos[:, 1]], axis=-1)

        out = runner.conservation_probe(predict_next, pos, cells, np.zeros((4, 2)), ref,
                                        node_type=node_type)
        self.assertIn("ratio_interior", out)
        self.assertEqual(out["interior_cell_count"], 1)  # only cell (0,2,3)
        self.assertAlmostEqual(out["ratio_interior"], 1.0, places=10)

    def test_metric_ledger_refuses_without_raw_outputs(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temp_dir:
            raw = Path(temp_dir)
            with self.assertRaises(ValueError):
                runner.build_conservation_metric_ledger(
                    fields=_complete_fields(),
                    entries=[{"frame": 0}],
                    raw_output_paths={"predicted_next_velocity": raw / "missing.npy"},
                )

    def test_metric_ledger_declares_required_outputs_and_fields(self):
        runner = load_runner()
        with tempfile.TemporaryDirectory() as temp_dir:
            raw = Path(temp_dir)
            names = ["predicted_next_velocity", "reference_next_velocity",
                     "cell_divergence_pred", "cell_divergence_reference"]
            for name in names:
                np.save(raw / f"{name}.npy", np.zeros((2, 2)))
            entry = runner.build_entry(
                fields=_complete_fields(), frame=0, ratio=1.003,
                pred_div=2.090, ref_div=2.085, verdict="pass",
                tolerance={"assertion": "less_or_equal", "threshold": 1.5},
                evidence_artifact="raw")
            ledger = runner.build_conservation_metric_ledger(
                fields=_complete_fields(), entries=[entry],
                raw_output_paths={n: raw / f"{n}.npy" for n in names})
            sys.path.insert(0, str(ROOT / "tools"))
            from manifest_contract import METRIC_LEDGER_FIELDS
            for field in METRIC_LEDGER_FIELDS:
                self.assertIn(field, ledger["entries"][0])
            self.assertEqual(set(ledger["required_raw_outputs"]), set(names))
            self.assertEqual(
                ledger["exact_relation_status"],
                "deferred-uncalibrated-absolute-tolerance",
            )


if __name__ == "__main__":
    unittest.main()
