from pathlib import Path
import importlib.util
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "tools" / "conservation_rubric.py"


def load_mod():
    spec = importlib.util.spec_from_file_location("conservation_rubric", MOD_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _unit_square():
    pos = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
    cells = np.array([[0, 1, 2], [0, 2, 3]])
    return pos, cells


class ConservationRubricTests(unittest.TestCase):
    def test_divergence_of_linear_expansion_field(self):
        mod = load_mod()
        pos, cells = _unit_square()
        vel = pos.copy()  # u = (x, y) -> div = 2 everywhere
        self.assertAlmostEqual(mod.divergence_rms(pos, cells, vel), 2.0, places=10)

    def test_divergence_of_rotation_field_is_zero(self):
        mod = load_mod()
        pos, cells = _unit_square()
        vel = np.stack([-pos[:, 1], pos[:, 0]], axis=-1)  # u = (-y, x) -> div = 0
        self.assertAlmostEqual(mod.divergence_rms(pos, cells, vel), 0.0, places=10)

    def test_divergence_of_mixed_linear_field(self):
        mod = load_mod()
        pos, cells = _unit_square()
        vel = np.stack([2 * pos[:, 0], -3 * pos[:, 1]], axis=-1)  # div = 2 - 3 = -1
        self.assertAlmostEqual(mod.divergence_rms(pos, cells, vel), 1.0, places=10)

    def test_cell_divergence_returns_per_cell_values_and_areas(self):
        mod = load_mod()
        pos, cells = _unit_square()
        div, area = mod.cell_divergence(pos, cells, pos.copy())
        self.assertEqual(div.shape, (2,))
        self.assertEqual(area.shape, (2,))
        self.assertTrue(np.allclose(div, 2.0))
        self.assertAlmostEqual(float(area.sum()), 1.0, places=10)  # unit square

    def test_interior_cell_mask_excludes_boundary_touching_cells(self):
        mod = load_mod()
        pos, cells = _unit_square()  # cells [[0,1,2],[0,2,3]]
        # node types: 0=NORMAL interior, others boundary. Mark node 1 as wall(6).
        node_type = np.array([0, 6, 0, 0])
        mask = mod.interior_cell_mask(cells, node_type, interior_types=(0, 5))
        # cell 0 touches node 1 (wall) -> excluded; cell 1 (0,2,3) all NORMAL -> kept
        self.assertTrue(np.array_equal(mask, np.array([False, True])))

    def test_masked_divergence_rms_uses_only_selected_cells(self):
        mod = load_mod()
        pos, cells = _unit_square()
        vel = np.stack([2 * pos[:, 0], -3 * pos[:, 1]], axis=-1)  # div = -1 per cell
        mask = np.array([False, True])
        self.assertAlmostEqual(mod.divergence_rms(pos, cells, vel, mask=mask), 1.0, places=10)

    def test_conservation_verdict_pass_when_ratio_within_threshold(self):
        mod = load_mod()
        self.assertEqual(
            mod.classify_conservation_verdict(2.090, 2.085, threshold=1.5), "pass"
        )

    def test_conservation_verdict_fail_when_ratio_exceeds_threshold(self):
        mod = load_mod()
        self.assertEqual(
            mod.classify_conservation_verdict(6.0, 2.0, threshold=1.5), "fail"
        )

    def test_conservation_verdict_inconclusive_when_reference_zero(self):
        mod = load_mod()
        self.assertEqual(
            mod.classify_conservation_verdict(1.0, 0.0, threshold=1.5), "inconclusive"
        )

    def test_conservation_verdict_inconclusive_on_nonfinite(self):
        mod = load_mod()
        self.assertEqual(
            mod.classify_conservation_verdict(float("inf"), 2.0, threshold=1.5),
            "inconclusive",
        )

    def test_absolute_tolerance_deferred_when_reference_divergence_nonnegligible(self):
        mod = load_mod()
        # reference dimensionless divergence (~0.037) dwarfs an absolute ~0 tol
        self.assertEqual(
            mod.classify_absolute_admissible(0.037, abs_tol=1e-6),
            mod.DEFERRED_UNCALIBRATED,
        )

    def test_absolute_tolerance_admissible_when_reference_divergence_tiny(self):
        mod = load_mod()
        self.assertEqual(
            mod.classify_absolute_admissible(1e-9, abs_tol=1e-6), mod.ABSOLUTE_ADMISSIBLE
        )


if __name__ == "__main__":
    unittest.main()
