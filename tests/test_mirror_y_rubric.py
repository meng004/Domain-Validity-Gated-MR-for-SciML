from pathlib import Path
import importlib.util
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUBRIC_PATH = ROOT / "tools" / "mirror_y_rubric.py"


def load_rubric():
    spec = importlib.util.spec_from_file_location("mirror_y_rubric", RUBRIC_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _symmetric_mesh():
    # Nodes mirror-symmetric about y=0: partners (x, y) <-> (x, -y); the node on
    # the axis maps to itself. node_type respects the symmetry.
    pos = np.array(
        [[0.0, 1.0], [0.0, -1.0], [1.0, 1.0], [1.0, -1.0], [0.5, 0.0]],
        dtype=np.float64,
    )
    node_type = np.array([6, 6, 0, 0, 0], dtype=np.int64)
    cells = np.array([[0, 2, 4], [1, 3, 4]], dtype=np.int64)
    return pos, node_type, cells


class MirrorYRubricTests(unittest.TestCase):
    # ---- geometry math ---------------------------------------------------- #
    def test_reflection_map_recovers_symmetric_partners(self):
        rubric = load_rubric()
        pos, _, _ = _symmetric_mesh()
        pi = rubric.reflection_map(pos, axis=0.0)
        self.assertTrue(np.array_equal(pi, np.array([1, 0, 3, 2, 4])))

    def test_measure_reflection_symmetry_on_symmetric_mesh(self):
        rubric = load_rubric()
        pos, node_type, cells = _symmetric_mesh()
        m = rubric.measure_reflection_symmetry(pos, node_type, cells, axis=0.0)
        self.assertTrue(m["bijection"])
        self.assertLess(m["max_nn_dist"], 1e-9)
        self.assertEqual(m["type_match_rate"], 1.0)
        self.assertGreater(m["median_edge_length"], 0.0)

    def test_measure_reflection_symmetry_flags_asymmetry(self):
        rubric = load_rubric()
        pos, node_type, cells = _symmetric_mesh()
        pos = pos.copy()
        pos[0, 0] += 0.6  # break symmetry of one node well beyond edge scale
        m = rubric.measure_reflection_symmetry(pos, node_type, cells, axis=0.0)
        self.assertGreater(m["max_nn_dist"], 0.0)

    # ---- precondition decision ------------------------------------------- #
    def test_preconditions_admit_exact_when_symmetric(self):
        rubric = load_rubric()
        metrics = {"bijection": True, "max_nn_over_edge": 0.0, "type_match_rate": 1.0}
        self.assertEqual(
            rubric.classify_mirror_preconditions(metrics), rubric.EXACT_ADMISSIBLE
        )

    def test_preconditions_reject_when_non_bijective(self):
        rubric = load_rubric()
        metrics = {"bijection": False, "max_nn_over_edge": 0.0, "type_match_rate": 1.0}
        self.assertEqual(
            rubric.classify_mirror_preconditions(metrics),
            rubric.OUT_OF_RELATION_DOMAIN,
        )

    def test_preconditions_reject_when_nodes_misalign(self):
        rubric = load_rubric()
        metrics = {"bijection": True, "max_nn_over_edge": 1.0, "type_match_rate": 1.0}
        self.assertEqual(
            rubric.classify_mirror_preconditions(metrics),
            rubric.OUT_OF_RELATION_DOMAIN,
        )

    def test_preconditions_reject_when_types_mismatch(self):
        rubric = load_rubric()
        metrics = {"bijection": True, "max_nn_over_edge": 0.0, "type_match_rate": 0.9}
        self.assertEqual(
            rubric.classify_mirror_preconditions(metrics),
            rubric.OUT_OF_RELATION_DOMAIN,
        )

    # ---- OOD-stress verdict ---------------------------------------------- #
    def test_ood_stress_fail_when_violation_exceeds_floor(self):
        rubric = load_rubric()
        v = rubric.classify_ood_stress_verdict(0.70, 0.15, tolerance=1e-6, ratio_threshold=2.0)
        self.assertEqual(v, "fail")

    def test_ood_stress_inconclusive_when_violation_near_floor(self):
        rubric = load_rubric()
        v = rubric.classify_ood_stress_verdict(0.20, 0.18, tolerance=1e-6, ratio_threshold=2.0)
        self.assertEqual(v, "inconclusive")

    def test_ood_stress_pass_when_below_tolerance(self):
        rubric = load_rubric()
        v = rubric.classify_ood_stress_verdict(1e-9, 0.15, tolerance=1e-6, ratio_threshold=2.0)
        self.assertEqual(v, "pass")

    def test_ood_stress_inconclusive_on_nonfinite(self):
        rubric = load_rubric()
        v = rubric.classify_ood_stress_verdict(float("inf"), 0.15, tolerance=1e-6)
        self.assertEqual(v, "inconclusive")


if __name__ == "__main__":
    unittest.main()
