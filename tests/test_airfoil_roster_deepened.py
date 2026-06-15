"""Guard: airfoil K=6 multi-checkpoint roster + full typed-MR suite.

This test pins the deepened airfoil second-task roster that was run locally
on Apple MPS (with CPU fallback).  It asserts:

 1. The workflow report records a K=6 completed roster.
 2. Each checkpoint file exists on disk.
 3. The full four-relation typed-MR suite is recorded in the report and the
    individual ledgers:
      - node-permutation equivariance : admitted (60/60 across roster)
      - incompressible continuity     : rejected-domain-invalid (physical-basis)
      - compressible mass conservation: deferred + reference-relative-diagnostic
      - mirror-y chord symmetry       : rejected-domain-invalid (boundary-precondition)
 4. Density compressibility evidence justifying the incompressible rejection
    (median density max/min > 1.15 across all test trajectories).
 5. The per-checkpoint timing summary and device record are present.

This test is intentionally backward-compatible with test_physicsnemo_airfoil_workflow.py:
that test still passes against the canonical single-checkpoint artifact
(physicsnemo_mgn_airfoil_checkpoint.pt) which is now produced from the last
roster checkpoint.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-second-task"
REPORT = OUT / "physicsnemo_mgn_airfoil_workflow_report.json"

K_EXPECTED = 6  # required number of completed checkpoints


class AirfoilRosterDeepenedTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text())

    # ------------------------------------------------------------------ #
    # 1. Roster completeness                                               #
    # ------------------------------------------------------------------ #

    def test_roster_k_checkpoints_requested_and_completed(self):
        roster = self.report["roster"]
        self.assertGreaterEqual(roster["k_checkpoints"], K_EXPECTED,
                                "k_checkpoints field must be >= 6")
        self.assertGreaterEqual(roster["k_checkpoints_completed"], K_EXPECTED,
                                "k_checkpoints_completed must be >= 6")

    def test_roster_per_checkpoint_summary_length(self):
        summary = self.report["roster"]["per_checkpoint_summary"]
        self.assertGreaterEqual(len(summary), K_EXPECTED,
                                f"Expected >= {K_EXPECTED} checkpoint summaries")

    def test_roster_checkpoint_files_exist(self):
        summary = self.report["roster"]["per_checkpoint_summary"]
        for entry in summary:
            ckpt_path = OUT / entry["checkpoint_file"]
            self.assertTrue(ckpt_path.exists(),
                            f"checkpoint file missing: {ckpt_path.name}")

    def test_roster_timing_recorded(self):
        roster = self.report["roster"]
        wall_clocks = roster["ckpt_wall_clocks_s"]
        self.assertGreaterEqual(len(wall_clocks), K_EXPECTED)
        for w in wall_clocks:
            self.assertGreater(w, 0.0, "wall-clock must be positive")
        self.assertIsNotNone(roster["total_wall_clock_s"])
        self.assertGreater(roster["total_wall_clock_s"], 0.0)

    def test_device_field_present(self):
        """The report must record which device was used (mps or cpu)."""
        device = self.report.get("device_used", "")
        self.assertIn(device, ("mps", "cpu"),
                      f"device_used must be 'mps' or 'cpu', got {device!r}")

    # ------------------------------------------------------------------ #
    # 2. Full typed-MR suite                                               #
    # ------------------------------------------------------------------ #

    def test_node_permutation_admitted_all_roster_passes(self):
        """Node-permutation must pass for ALL checkpoints x ALL test trajectories."""
        led_path = OUT / "node_permutation_metric_ledger.json"
        led = json.loads(led_path.read_text())
        self.assertEqual(led["rubric_decision"], "admitted")
        self.assertEqual(led["verdict"], "pass")
        # Roster covers K_EXPECTED checkpoints * 10 test trajectories = 60 rows
        n = led["denominator"]
        self.assertGreaterEqual(n, K_EXPECTED * 8,  # at least 8 test trajs per ckpt
                                "denominator must cover multiple checkpoints")
        self.assertEqual(led["passes"], n,
                         f"All {n} perm tests must pass; got {led['passes']}")
        self.assertLessEqual(led["max_relative_l2"], 1e-5,
                             "max relative L2 must be below threshold 1e-5")

    def test_incompressible_continuity_rejected_physical_basis(self):
        led_path = OUT / "incompressible_continuity_rejection_ledger.json"
        led = json.loads(led_path.read_text())
        self.assertEqual(led["verdict"], "rejected-domain-invalid")
        self.assertIn("physical-basis", led["rubric_decision"])
        self.assertGreater(led["median_density_max_over_min"], 1.15,
                           "Must show measured compressibility > 1.15x")
        self.assertIn("condition (i)", led["rejection_basis"])
        self.assertIn("compressible", led["rejection_basis"].lower())

    def test_compressible_conservation_deferred_with_diagnostic(self):
        led_path = OUT / "compressible_conservation_metric_ledger.json"
        led = json.loads(led_path.read_text())
        self.assertIn("deferred", led["rubric_decision"])
        self.assertIn("reference-relative-diagnostic-recorded", led["verdict"])
        self.assertIn("no absolute", led["honesty_boundary"].lower())
        # denominator must cover the full roster
        self.assertGreaterEqual(led["denominator"], K_EXPECTED * 8)

    def test_mirror_y_symmetry_rejected_boundary_precondition(self):
        led_path = OUT / "mirror_y_symmetry_rejection_ledger.json"
        led = json.loads(led_path.read_text())
        self.assertEqual(led["verdict"], "rejected-domain-invalid")
        self.assertIn("boundary-precondition", led["rubric_decision"])
        self.assertIn("angle of attack", led["rejection_basis"].lower())

    # ------------------------------------------------------------------ #
    # 3. Headline verdict structure in the report                          #
    # ------------------------------------------------------------------ #

    def test_report_headline_verdict_structure(self):
        verdicts = self.report["headline_typed_verdict_structure"]
        self.assertIn("admitted", verdicts["node_permutation_equivariance"])
        self.assertIn("rejected", verdicts["incompressible_continuity"])
        self.assertIn("rejected", verdicts["mirror_y_symmetry"])
        self.assertIn("deferred", verdicts["compressible_mass_conservation"])

    # ------------------------------------------------------------------ #
    # 4. Per-checkpoint passes in summary                                  #
    # ------------------------------------------------------------------ #

    def test_each_checkpoint_reports_node_perm_passes(self):
        summary = self.report["roster"]["per_checkpoint_summary"]
        for entry in summary:
            passes_str = entry.get("node_perm_passes", "")
            # Format: "N/N" where both N should be equal
            self.assertIn("/", passes_str,
                          f"node_perm_passes malformed: {passes_str!r}")
            passed, total = (int(x) for x in passes_str.split("/"))
            self.assertEqual(passed, total,
                             f"checkpoint {entry['checkpoint_index']} "
                             f"node perm not 100%: {passes_str}")

    # ------------------------------------------------------------------ #
    # 5. Honesty boundary and forbidden claims intact                      #
    # ------------------------------------------------------------------ #

    def test_honesty_boundary_still_intact(self):
        hb = self.report["honesty_boundary"]
        for needle in ("NOT a production-scale airfoil benchmark",
                       "NOT an official NVIDIA checkpoint"):
            self.assertIn(needle, hb,
                          f"honesty boundary missing: {needle!r}")

    def test_forbidden_claims_present(self):
        forbidden = " ".join(self.report["forbidden_claims"])
        self.assertIn("production-scale airfoil", forbidden)
        self.assertIn("absolute compressible mass conservation", forbidden)


if __name__ == "__main__":
    unittest.main()
