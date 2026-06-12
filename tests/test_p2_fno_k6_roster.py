"""Phase-2 guards for the FNO K=6 third-family roster."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ROSTER = ROOT / "research_assets/runs/fno-k6-roster"
AGG = ROSTER / "fno_k6_aggregate.json"


def load_tool(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestFnoK6Tooling(unittest.TestCase):
    def test_fno_tool_modules_are_importable(self) -> None:
        for name in ("gen_fd_dataset_2d", "fno2d", "train_fno_2d", "run_fno_k6_roster"):
            with self.subTest(name=name):
                load_tool(name)


class TestFnoK6RosterArtifacts(unittest.TestCase):
    def test_aggregate_and_per_sut_artifacts_present(self) -> None:
        self.assertTrue(AGG.exists(), f"missing aggregate: {AGG}")
        for pde in ("burgers", "heat"):
            for seed in range(3):
                d = ROSTER / f"{pde}_s{seed}"
                for rel in ("manifest.json", "mr_report.json", "sut/checkpoint.pt"):
                    self.assertTrue((d / rel).exists(), f"missing {d / rel}")


class TestFnoK6Aggregate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r = json.loads(AGG.read_text())

    def test_roster_shape(self) -> None:
        self.assertEqual(self.r["record_type"], "fno-k6-roster-aggregate")
        self.assertEqual(self.r["architecture_family"], "FNO-2D")
        self.assertEqual(self.r["n_seeds"], 3)
        self.assertEqual(self.r["seeds"], [0, 1, 2])
        self.assertEqual(len(self.r["per_sut"]), 6)
        self.assertEqual({x["pde"] for x in self.r["per_sut"]}, {"burgers", "heat"})

    def test_rubric_makes_nontrivial_admissibility_decisions(self) -> None:
        gate = self.r["admissibility_gate_summary"]
        self.assertEqual(gate["periodic_translation_admitted"], 6)
        self.assertEqual(gate["dirichlet_translation_rejected_or_downgraded"], 6)
        self.assertGreaterEqual(gate["nontrivial_decisions"], 6)
        for row in self.r["per_sut"]:
            self.assertEqual(row["mr_translation_periodic"]["admissibility"], "admitted")
            self.assertIn(
                row["mr_translation_dirichlet"]["admissibility"],
                {"rejected", "downgraded"},
            )
            self.assertIn("boundary condition", row["mr_translation_dirichlet"]["reason"])

    def test_family_bootstrap_fields(self) -> None:
        for fam in self.r["per_pde_family"].values():
            for key in ("eval_relative_l2_95ci", "periodic_translation_violation_95ci"):
                self.assertEqual(len(fam[key]), 2)
                self.assertLessEqual(fam[key][0], fam[key][1])
            self.assertEqual(fam["periodic_translation_admission_rate"], 1.0)
            self.assertEqual(fam["dirichlet_translation_rejection_rate"], 1.0)

    def test_honesty_boundary_is_scoped(self) -> None:
        boundary = self.r["honesty_boundary"]
        self.assertIn("closed-form synthetic data", boundary)
        self.assertIn("not a cylinder-flow", boundary)
        self.assertIn("not a cross-family performance benchmark", boundary)


if __name__ == "__main__":
    unittest.main()
