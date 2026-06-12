"""TDD guards for P0c Task 2 production-SUT MR candidate ledgers."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research_assets/runs/production-grade-sut-extension"
FEASIBILITY = BASE / "feasibility_report.json"
PLAN = ROOT / "docs/superpowers/plans/2026-06-12-production-grade-sut-extension-plan.md"
CLAIM_LEDGER = ROOT / "research_assets/experiments/claim-ledger.yml"

OBJECT_IDS = (
    "physicsnemo-mgn-vortex-shedding",
    "physicsnemo-aerographnet-external-aero",
    "physicsnemo-domino-external-aero",
)
REQUIRED_FIELDS = {
    "candidate_id",
    "relation_class",
    "source_category",
    "basis",
    "preconditions",
    "output_mapping",
    "metric",
    "tolerance_floor_status",
    "admissibility_predicate",
    "decision",
    "execution_gate",
}
REQUIRED_RELATION_CLASSES = {
    "representation",
    "symmetry",
    "conservation_flux",
    "boundary_contract",
    "numerical_floor",
}


class ProductionSutCandidateLedgersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.feasibility = json.loads(FEASIBILITY.read_text(encoding="utf-8"))
        cls.ledgers = {}
        for object_id in OBJECT_IDS:
            path = BASE / object_id / "candidate_ledger.json"
            cls.ledgers[object_id] = json.loads(path.read_text(encoding="utf-8"))

    def test_all_three_objects_have_candidate_ledgers(self) -> None:
        self.assertEqual(set(self.ledgers), set(OBJECT_IDS))
        for object_id, ledger in self.ledgers.items():
            self.assertEqual(ledger["record_type"], "production-sut-mr-candidate-ledger")
            self.assertEqual(ledger["object_id"], object_id)
            self.assertEqual(ledger["feasibility_report"], "research_assets/runs/production-grade-sut-extension/feasibility_report.json")
            self.assertEqual(ledger["object_feasibility_status"], "blocked")
            self.assertFalse(ledger["workflow_execution_allowed"])
            self.assertGreaterEqual(len(ledger["candidates"]), 5)

    def test_candidate_schema_and_relation_class_coverage(self) -> None:
        for object_id, ledger in self.ledgers.items():
            classes = {candidate["relation_class"] for candidate in ledger["candidates"]}
            self.assertTrue(REQUIRED_RELATION_CLASSES.issubset(classes), object_id)
            for candidate in ledger["candidates"]:
                self.assertTrue(REQUIRED_FIELDS.issubset(candidate), candidate.get("candidate_id"))
                predicate = candidate["admissibility_predicate"]
                self.assertEqual(
                    set(predicate),
                    {"domain_preconditions", "semantic_invariance", "output_mapping_defined", "numerical_floor_defined"},
                )
                self.assertIn(candidate["decision"], {"admitted", "downgraded", "rejected", "deferred", "blocked"})
                self.assertIn(candidate["tolerance_floor_status"], {"defined", "needs_calibration", "not_applicable", "deferred"})

    def test_blocked_feasibility_prevents_exact_execution_for_every_candidate(self) -> None:
        for ledger in self.ledgers.values():
            for candidate in ledger["candidates"]:
                gate = candidate["execution_gate"]
                self.assertFalse(gate["planned_workflow_execution"])
                self.assertEqual(gate["blocked_by"], "P0c Task 1 feasibility gate")
                self.assertIn("No raw production outputs", gate["reason"])

    def test_rejected_or_downgraded_candidates_are_never_marked_exact(self) -> None:
        for ledger in self.ledgers.values():
            for candidate in ledger["candidates"]:
                if candidate["decision"] in {"rejected", "downgraded", "deferred", "blocked"}:
                    self.assertFalse(candidate["execution_gate"]["executable_as_exact_mr"])
                    self.assertTrue(candidate["decision_reason"])

    def test_each_object_selects_only_blocked_future_subset_without_results(self) -> None:
        for ledger in self.ledgers.values():
            subset = ledger["selected_future_subset"]
            self.assertGreaterEqual(len(subset), 1)
            self.assertTrue(set(subset).issubset({c["candidate_id"] for c in ledger["candidates"]}))
            self.assertEqual(ledger["current_result_claim"], "none")
            self.assertFalse(ledger["raw_outputs_available"])
            self.assertFalse(ledger["metric_ledgers_available"])

    def test_plan_and_claim_ledger_record_task2_without_advancing_workflows(self) -> None:
        plan = PLAN.read_text(encoding="utf-8")
        self.assertIn("- [x] Create per-object candidate ledgers", plan)
        self.assertIn("- [x] Apply the four-part admissibility predicate.", plan)
        self.assertIn("- [ ] Implement `tools/run_physicsnemo_mgn_primary_workflow.py`.", plan)
        claim_text = CLAIM_LEDGER.read_text(encoding="utf-8")
        self.assertIn("candidate ledgers classify planned MR relations", claim_text)
        self.assertIn("No production MR has been executed", claim_text)


if __name__ == "__main__":
    unittest.main()
