"""Phase 3 guards for the unified fault catalogue/statistics report."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research_assets/runs/phase3-unified-fault-catalog/phase3_unified_fault_catalog.json"
MANUSCRIPT = ROOT / "paper/manuscript.md"
LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"


class TestPhase3UnifiedFaultCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r = json.loads(REPORT.read_text())

    def test_catalogue_size_and_breakdown(self) -> None:
        self.assertGreaterEqual(self.r["catalogue_size"], 60)
        self.assertEqual(
            self.r["catalogue_breakdown"],
            {
                "mgn_canonical_executed_mutants": 10,
                "mgn_adversarial_executed_mutants": 2,
                "pinn_output_level_closed_form_probes": 24,
                "fno_output_level_closed_form_probes": 24,
            },
        )
        self.assertEqual(len(self.r["entries"]), self.r["catalogue_size"])
        self.assertGreaterEqual(self.r["trial_count"], 456)

    def test_localization_precision_recall_wilson_fields(self) -> None:
        pr = self.r["by_detector_localization_precision_recall"]
        self.assertEqual(set(pr), {"node_perm", "conservation", "mirror_y"})
        for detector, stats in pr.items():
            for metric in ("precision", "recall"):
                cell = stats[metric]
                self.assertIn("ci_lo", cell)
                self.assertIn("ci_hi", cell)
                self.assertGreaterEqual(cell["value"], 0.0, detector)
                self.assertLessEqual(cell["value"], 1.0, detector)
                self.assertLessEqual(cell["ci_lo"], cell["value"], detector)
                self.assertGreaterEqual(cell["ci_hi"], cell["value"], detector)
        self.assertGreaterEqual(pr["node_perm"]["precision"]["value"], 0.9)
        self.assertGreaterEqual(pr["conservation"]["precision"]["value"], 0.9)
        self.assertGreaterEqual(pr["mirror_y"]["precision"]["value"], 0.8)

    def test_effect_size_tests_present(self) -> None:
        eff = self.r["effect_size_and_nonparametric_tests"]
        self.assertIn("mgn_mirror_ood_vs_rollout", eff)
        pinn = eff["pinn_diffusion_vs_burgers_mr_b_ratio"]
        # n pinned to >=15 after PINN roster deepening (was 3 before b5abdaa-mirror);
        # the Wilcoxon here is an inter-PDE physics-magnitude test (diffusion Neumann BC
        # vs Burgers Dirichlet BC), not a gate-reliability test -- significance at n=15
        # reflects the physics difference, not gate reliability. The valid statistic is
        # the per-PDE Wilson CI in pinn_k6_aggregate.json.
        self.assertGreaterEqual(pinn["wilcoxon_signed_rank"]["n"], 15)
        self.assertEqual(pinn["cliffs_delta"]["magnitude"], "large")
        self.assertGreater(pinn["cliffs_delta"]["delta"], 0.0)

    def test_honesty_boundary_for_pinn_probes(self) -> None:
        boundary = self.r["honesty_boundary"]
        self.assertIn("closed-form", boundary)
        self.assertIn("not retrained PINN mutant checkpoints", boundary)
        pinn_entries = [e for e in self.r["entries"] if e["source_family"].startswith("PINN-")]
        self.assertEqual(len(pinn_entries), 24)
        for entry in pinn_entries:
            self.assertIn("no retraining", entry["evaluation_basis"])

    def test_honesty_boundary_for_fno_probes(self) -> None:
        boundary = self.r["honesty_boundary"]
        self.assertIn("FNO", boundary)
        self.assertIn("closed-form output-level", boundary)
        fno_entries = [e for e in self.r["entries"] if e["source_family"].startswith("FNO-")]
        self.assertEqual(len(fno_entries), 24)
        for entry in fno_entries:
            self.assertIn("no retraining", entry["evaluation_basis"])


class TestPhase3TextSync(unittest.TestCase):
    def test_manuscript_and_ledger_reference_phase3_catalogue(self) -> None:
        m = MANUSCRIPT.read_text()
        l = LEDGER.read_text()
        self.assertIn("phase3-unified-fault-catalog", m)
        self.assertIn("60-entry unified fault catalogue", m)
        self.assertIn("FNO", m)
        self.assertIn("precision/recall", m)
        self.assertIn("C16-unified-fault-catalog-statistics", l)
        self.assertIn("C19-third-family-fno-roster", l)
        self.assertIn("phase3-unified-fault-catalog/phase3_unified_fault_catalog.json", l)


if __name__ == "__main__":
    unittest.main()
