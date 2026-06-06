from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper" / "manuscript.md"
CLAIM_LEDGER = ROOT / "research_assets" / "experiments" / "claim-ledger.yml"
EXPERIMENT_LEDGER = ROOT / "research_assets" / "experiments" / "experiment-ledger.yml"
EVIDENCE_PACKAGE = ROOT / "research_assets" / "experiments" / "evidence-package.md"
PR4_RUN = ROOT / "research_assets" / "runs" / "mirror-y-rate-upgrade"
PR4_RAW = PR4_RUN / "raw"


OBSERVED_ARTIFACTS = [
    "research_assets/runs/real-sut-node-permutation-pilot/manifest.yml",
    "research_assets/runs/real-sut-node-permutation-pilot/raw/metric_ledger.json",
    "research_assets/runs/real-sut-node-permutation-pilot/raw/source_output.npy",
    "research_assets/runs/real-sut-node-permutation-pilot/raw/follow_up_output.npy",
    "research_assets/runs/real-sut-node-permutation-pilot/raw/mapped_output.npy",
    "research_assets/runs/real-sut-node-permutation-pilot/raw/stdout.log",
    "research_assets/runs/real-sut-node-permutation-pilot/raw/stderr.log",
    "research_assets/runs/mirror-y-ood-stress-pilot/manifest.yml",
    "research_assets/runs/mirror-y-ood-stress-pilot/raw/precondition_report.json",
    "research_assets/runs/mirror-y-ood-stress-pilot/raw/metric_ledger.json",
    "research_assets/runs/mirror-y-ood-stress-pilot/raw/source_output.npy",
    "research_assets/runs/mirror-y-ood-stress-pilot/raw/follow_up_output.npy",
    "research_assets/runs/mirror-y-ood-stress-pilot/raw/mapped_output.npy",
    "research_assets/runs/mirror-y-ood-stress-pilot/raw/stdout.log",
    "research_assets/runs/mirror-y-ood-stress-pilot/raw/stderr.log",
    "research_assets/runs/conservation-diagnostic-pilot/manifest.yml",
    "research_assets/runs/conservation-diagnostic-pilot/raw/conservation_report.json",
    "research_assets/runs/conservation-diagnostic-pilot/raw/metric_ledger.json",
    "research_assets/runs/conservation-diagnostic-pilot/raw/predicted_next_velocity.npy",
    "research_assets/runs/conservation-diagnostic-pilot/raw/reference_next_velocity.npy",
    "research_assets/runs/conservation-diagnostic-pilot/raw/cell_divergence_pred.npy",
    "research_assets/runs/conservation-diagnostic-pilot/raw/cell_divergence_reference.npy",
    "research_assets/runs/conservation-diagnostic-pilot/raw/stdout.log",
    "research_assets/runs/conservation-diagnostic-pilot/raw/stderr.log",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class PR4EvidenceConvergenceTest(unittest.TestCase):
    def assert_all_markers_present(self, text: str, markers: list[str]) -> None:
        for marker in markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_claim_ledger_records_pr4_mirror_y_bounded_rate(self) -> None:
        text = read(CLAIM_LEDGER)
        required = [
            'claim_id: "C6-mirror-y-ood-stress"',
            'status: "observed"',
            "bounded within-SUT frame-level approximate OOD-stress rate",
            "failed on 10 of 10 recorded eval frames",
            "median relative L2",
            "0.737",
            "median ratio 3.96",
            "not a reliability, accuracy, baseline, multi-SUT",
            "Mirror-y is a valid exact relation for this mesh.",
        ]
        self.assert_all_markers_present(text, required)

    def test_experiment_ledger_records_pr4_run_and_keeps_boundaries(self) -> None:
        text = read(EXPERIMENT_LEDGER)
        required = [
            'run_id: "real-sut-mirror-y-rate-upgrade-001"',
            'status: "observed"',
            'evidence_level: "real-sut-single-mr-ood-stress-frame-rate"',
            'recorded_frames: "0,1,2,3,4,5,6,7,8,9"',
            "ood_stress_frame_fail_count: 10",
            "ood_stress_frame_denominator: 10",
            "median_violation_rel_l2: 0.7368",
            "median_violation_over_floor: 3.96",
            "It is not a reliability, accuracy, baseline,",
        ]
        self.assert_all_markers_present(text, required)
        self.assertNotIn("It does not record real SUT verdicts, empirical rates", text)

    def test_evidence_package_summarizes_pr4_without_overclaim(self) -> None:
        text = read(EVIDENCE_PACKAGE)
        required = [
            "Mirror-y OOD-stress within-SUT frame rate",
            "failed on **10 of 10 recorded eval frames**",
            "median relative L2 `0.737`",
            "bounded within-SUT frame rate",
            "not a geometry-independent or cross-SUT rate",
        ]
        self.assert_all_markers_present(text, required)
        self.assertNotIn("reports no rate", text)
        self.assertNotIn("A pass/fail rate, violation rate, or model-reliability conclusion", text)

    def test_pr4_artifacts_cited_by_ledgers_exist_locally(self) -> None:
        required_paths = [
            PR4_RUN / "manifest.yml",
            PR4_RUN / "PROVENANCE.md",
            PR4_RAW / "metric_ledger.json",
            PR4_RAW / "stdout.log",
            PR4_RAW / "stderr.log",
            PR4_RAW / "source_output.npy",
            PR4_RAW / "follow_up_output.npy",
            PR4_RAW / "mapped_output.npy",
        ]
        for path in required_paths:
            with self.subTest(path=str(path)):
                self.assertTrue(path.exists(), f"missing PR4 artifact: {path}")

        metric_ledger = json.loads((PR4_RAW / "metric_ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(metric_ledger["evidence_level"], "real-sut-single-mr-ood-stress-frame-rate")
        summary = metric_ledger["rate_summary"]
        self.assertEqual(summary["n_frames"], 10)
        self.assertEqual(summary["n_fail"], 10)
        self.assertEqual(summary["n_pass"], 0)
        self.assertEqual(summary["n_inconclusive"], 0)
        self.assertEqual(summary["violation_rate"], 1.0)
        self.assertAlmostEqual(summary["median_violation"], 0.7367751777061563)
        self.assertAlmostEqual(summary["median_violation_over_floor"], 3.955645782723197)
        for relative_path in metric_ledger["raw_outputs"].values():
            path = ROOT / relative_path
            with self.subTest(path=relative_path):
                self.assertTrue(path.exists(), f"missing raw output listed in metric ledger: {path}")

    def test_all_observed_pilot_artifacts_cited_by_ledgers_exist_locally(self) -> None:
        for relative_path in OBSERVED_ARTIFACTS:
            path = ROOT / relative_path
            with self.subTest(path=relative_path):
                self.assertTrue(path.exists(), f"missing observed pilot artifact: {path}")

    def test_manuscript_results_discussion_and_conclusion_are_pr4_aligned(self) -> None:
        text = read(MANUSCRIPT)
        required = [
            "failed on 10 of 10 recorded eval frames",
            "median relative L2 0.737",
            "median V/floor 3.96",
            "out-of-relation-domain",
            "one SUT, one checkpoint, one MR, one eval trajectory",
            "not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim",
            "bounded within-SUT frame-level OOD-stress result",
        ]
        self.assert_all_markers_present(text, required)

        stale_two_frame_rate_wording = re.compile(
            r"V = 0\.6914 and 0\.7494; about 3\.6--3\.8 times the mapping-error floor"
        )
        self.assertIsNone(stale_two_frame_rate_wording.search(text))
        for stale_marker in [
            "This paper is planned around four contributions.",
            "The expected value of the study",
            "If the empirical study succeeds",
            "This contribution will be stated as a result only after experiment artifacts exist.",
        ]:
            with self.subTest(stale_marker=stale_marker):
                self.assertNotIn(stale_marker, text)
