"""Guard for the end-to-end cross-program pipeline execution (claim C40).

Pins that this paper's validity-gated pipeline runs end-to-end on four CPU-only classical
SUTs from the read-only Minimum-MR-SubSet sibling (p1_heat, p2_wave, p5_pke, p7_burgers),
spanning four program types (parabolic / hyperbolic / stiff-ODE / conservation), producing:
  - admit / reject / defer gate decisions per SUT, with at least one program where the gate
    makes a non-trivial decision (it rejects MRs that fail the output-mapping / construct-
    validity condition, not a rubber stamp);
  - a typed two-dimensional verdict per SUT (relation-violation x domain-violation);
  - a per-SUT coverage map with structural blind spots and the sibling's declared
    equivalent mutants separated out;
  - a program-specific operator-class-to-fault-coverage mapping.

Also pins the honesty boundary: the MRs/mutants are the sibling's domain assets, what is
executed end-to-end is this paper's gate + typed verdict, and no reliability/superiority/
new-MR-contribution claim is made. Prevents prose from overclaiming a validated cross-
program detector. Unlike C39 (read-only kill-matrix reuse), C40 executes the pipeline.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "research_assets/runs/endtoend-pseries"
AGG = RUN / "metric_ledger.json"

CORE_SUTS = ["p1_heat", "p2_wave", "p5_pke", "p7_burgers"]


class EndToEndPipelinePseriesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(AGG.read_text(encoding="utf-8"))
        cls.per = {r["sut"]: r for r in cls.d["per_sut"]}

    def test_four_suts_four_program_types_executed(self) -> None:
        self.assertEqual(self.d["evidence_level"], "endtoend-pipeline-executed-cpu")
        self.assertEqual(self.d["n_suts_executed"], 4)
        self.assertEqual(self.d["suts"], CORE_SUTS)
        self.assertEqual(self.d["n_program_types"], 4)
        self.assertEqual(set(self.d["program_types"]),
                         {"parabolic PDE", "hyperbolic PDE", "stiff ODE",
                          "nonlinear conservation law"})

    def test_per_sut_ledgers_and_provenance_present(self) -> None:
        self.assertTrue(self.d["sibling_commit"] and self.d["sibling_commit"] != "unknown")
        for sut in CORE_SUTS:
            tag = self.per[sut]["tag"].lower()
            self.assertTrue((RUN / tag / "metric_ledger.json").exists(),
                            f"missing per-SUT ledger for {sut}")

    def test_gate_decisions_present_and_well_formed(self) -> None:
        for sut in CORE_SUTS:
            r = self.per[sut]
            g = r["gate_decision_counts"]
            self.assertEqual(set(g), {"admit", "reject", "defer"})
            self.assertEqual(g["admit"] + g["reject"] + g["defer"], r["n_candidate_mrs"])
            self.assertGreaterEqual(g["admit"], 1)
            # every candidate MR carries a four-condition record and a rubric decision
            for mr in r["gate_per_mr"]:
                self.assertEqual(set(mr["conditions"]),
                                 {"i_physical_basis", "ii_transformation_preconditions",
                                  "iii_output_mapping", "iv_numerical_decidability"})
                self.assertIn(mr["rubric_decision"],
                              {"retained-design-time", "rejected-design-time", "deferred"})

    def test_gate_is_not_a_rubber_stamp(self) -> None:
        # The pinned sibling commit yields exactly: heat 9/0/0, wave 7/2/0, pke 7/3/0,
        # burgers 10/0/0 (admit/reject/defer). The gate's non-trivial action is rejection.
        self.assertTrue(self.d["gate_makes_nontrivial_decisions"])
        self.assertGreaterEqual(self.d["programs_with_rejections"], 2)
        total_reject = sum(r["gate_decision_counts"]["reject"] for r in self.d["per_sut"])
        self.assertEqual(total_reject, 5)
        # Every rejection is an output-mapping / construct-validity (condition iii) failure:
        # the relation is not falsified by the scrambled-observable probe.
        for r in self.d["per_sut"]:
            for mr in r["gate_per_mr"]:
                if mr["decision"] == "reject":
                    self.assertFalse(mr["conditions"]["iii_output_mapping"])
                    self.assertFalse(mr["firewall"]["falsifiable"])
                    self.assertIn("construct validity", mr["reason"])

    def test_typed_2d_verdict_present(self) -> None:
        for sut in CORE_SUTS:
            v = self.per[sut]["typed_verdict_2d"]
            self.assertIn("domain_violation_axis", v)
            self.assertIn("relation_violation_axis_reading", v)
            # all admitted MRs are consistent (pass) on the correct SUT (in-domain region)
            self.assertEqual(v["n_admitted_mr_correct_sut_pass"],
                             self.per[sut]["n_admitted_mrs"])
            # rejected/deferred MRs are excluded from the verdict space
            excluded = (self.per[sut]["gate_decision_counts"]["reject"]
                        + self.per[sut]["gate_decision_counts"]["defer"])
            self.assertEqual(v["excluded_from_verdict_space_reject_or_defer"], excluded)

    def test_coverage_map_blind_spots_and_equivalents(self) -> None:
        # Every program has a structural blind spot, and the sibling's declared equivalent
        # mutants are separated out (they are expected to escape; not counted as blind spots).
        self.assertEqual(self.d["programs_with_structural_blind_spots"], 4)
        for sut in CORE_SUTS:
            r = self.per[sut]
            self.assertTrue(r["has_structural_blind_spot"])
            self.assertTrue(r["structural_blind_spots"])
            self.assertTrue(r["declared_equivalents_among_escaped"])
            # blind spots and declared equivalents are disjoint
            self.assertEqual(
                set(r["structural_blind_spots"]) & set(r["declared_equivalents_among_escaped"]),
                set())
            self.assertTrue(r["per_operator_class_fault_coverage"])

    def test_detection_is_heterogeneous_not_uniform(self) -> None:
        scores = [r["full_set_mutation_score"] for r in self.d["per_sut"]]
        self.assertTrue(all(0.0 < s <= 1.0 for s in scores))
        # tracks the admissible MR set, not a uniform rate (heat is richer than the rest)
        self.assertLess(min(scores), max(scores))

    def test_mapping_is_program_specific(self) -> None:
        self.assertTrue(self.d["class_to_class_mappings_program_specific"])

    def test_openmc_e5_status_recorded(self) -> None:
        self.assertIn(self.d["openmc_e5_status"],
                      {"executed", "skipped-openmc-not-importable",
                       "not-requested-but-importable", "not-executed-openmc-not-importable"})
        self.assertIsInstance(self.d["openmc_importable"], bool)
        # when openmc is unavailable, E5 is not counted among the executed SUTs
        if not self.d["openmc_importable"]:
            self.assertNotIn("p9_openmc", self.d["suts"])

    def test_honesty_boundary(self) -> None:
        hb = self.d["honesty_boundary"].lower()
        self.assertIn("read-only", hb)
        self.assertIn("this paper's gate", hb)
        for forbidden in ("reliability", "superiority", "new contributions"):
            self.assertIn(forbidden, hb)
        # end-to-end execution, distinct from C39's read-only reuse
        self.assertIn("end-to-end", hb)


if __name__ == "__main__":
    unittest.main()
