"""Guard for the end-to-end cross-program pipeline execution (claim C40).

Pins that this paper's validity-gated pipeline runs end-to-end on five CPU-only SUTs from
the read-only Minimum-MR-SubSet sibling: four classical solvers (p1_heat, p2_wave, p5_pke,
p7_burgers) plus the sibling's OpenMC headline subject executed with the REAL OpenMC
Monte-Carlo k-eigenvalue solver in multi-group mode. The five span five program types
(parabolic / hyperbolic / stiff-ODE / conservation / Monte-Carlo transport), producing:
  - admit / reject / defer gate decisions per SUT, with several programs where the gate
    makes a non-trivial decision (it rejects MRs that fail the output-mapping / construct-
    validity condition, not a rubber stamp);
  - a typed two-dimensional verdict per SUT (relation-violation x domain-violation);
  - a per-SUT coverage map with structural blind spots and declared equivalent mutants
    separated out;
  - a program-specific operator-class-to-fault-coverage mapping.

Also pins the honesty boundary: the MRs/mutants are the sibling's domain assets, what is
executed end-to-end is this paper's gate + typed verdict, and no reliability/superiority/
new-MR-contribution claim is made. The OpenMC subject is the multi-group 1-group
infinite-medium criticality PUT (no continuous-energy nuclear data), not a whole-core
reactor-physics result. Unlike C39 (read-only kill-matrix reuse), C40 executes the pipeline.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "research_assets/runs/endtoend-pseries"
AGG = RUN / "metric_ledger.json"
PROVENANCE = RUN / "PROVENANCE.md"
OPENMC_BUILD_SCRIPT = ROOT / "tools/build_openmc_e5.sh"

CLASSICAL_SUTS = ["p1_heat", "p2_wave", "p5_pke", "p7_burgers"]
OPENMC_SUT = "openmc_headline_mg"
ALL_SUTS = CLASSICAL_SUTS + [OPENMC_SUT]


class EndToEndPipelinePseriesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.d = json.loads(AGG.read_text(encoding="utf-8"))
        cls.per = {r["sut"]: r for r in cls.d["per_sut"]}

    def test_five_suts_five_program_types_executed(self) -> None:
        self.assertEqual(self.d["evidence_level"], "endtoend-pipeline-executed-cpu")
        self.assertEqual(self.d["n_suts_executed"], 5)
        self.assertEqual(self.d["suts"], ALL_SUTS)
        self.assertEqual(self.d["n_program_types"], 5)
        self.assertEqual(set(self.d["program_types"]),
                         {"parabolic PDE", "hyperbolic PDE", "stiff ODE",
                          "nonlinear conservation law", "Monte-Carlo transport"})

    def test_per_sut_ledgers_and_provenance_present(self) -> None:
        self.assertTrue(self.d["sibling_commit"] and self.d["sibling_commit"] != "unknown")
        for sut in ALL_SUTS:
            tag = self.per[sut]["tag"].lower()
            self.assertTrue((RUN / tag / "metric_ledger.json").exists(),
                            f"missing per-SUT ledger for {sut}")

    def test_gate_decisions_present_and_well_formed(self) -> None:
        for sut in ALL_SUTS:
            r = self.per[sut]
            g = r["gate_decision_counts"]
            self.assertEqual(set(g), {"admit", "reject", "defer"})
            self.assertEqual(g["admit"] + g["reject"] + g["defer"], r["n_candidate_mrs"])
            self.assertGreaterEqual(g["admit"], 1)
            for mr in r["gate_per_mr"]:
                self.assertEqual(set(mr["conditions"]),
                                 {"i_physical_basis", "ii_transformation_preconditions",
                                  "iii_output_mapping", "iv_numerical_decidability"})
                self.assertIn(mr["rubric_decision"],
                              {"retained-design-time", "rejected-design-time", "deferred"})

    def test_gate_is_not_a_rubber_stamp(self) -> None:
        # Pinned result on the sibling commit: admit/reject/defer = heat 9/0/0, wave 7/2/0,
        # pke 7/3/0, burgers 10/0/0, openmc 5/2/0. The gate's non-trivial action is rejection
        # at the output-mapping/construct-validity condition (one-sided monotonicity MRs that
        # a uniformly-inflated follow-up output does not falsify).
        self.assertTrue(self.d["gate_makes_nontrivial_decisions"])
        self.assertGreaterEqual(self.d["programs_with_rejections"], 3)
        total_reject = sum(r["gate_decision_counts"]["reject"] for r in self.d["per_sut"])
        self.assertEqual(total_reject, 7)
        for r in self.d["per_sut"]:
            for mr in r["gate_per_mr"]:
                if mr["decision"] == "reject":
                    self.assertFalse(mr["conditions"]["iii_output_mapping"])
                    self.assertFalse(mr["firewall"]["falsifiable"])
                    self.assertIn("construct validity", mr["reason"])

    def test_typed_2d_verdict_present(self) -> None:
        for sut in ALL_SUTS:
            v = self.per[sut]["typed_verdict_2d"]
            self.assertIn("domain_violation_axis", v)
            self.assertIn("relation_violation_axis_reading", v)
            self.assertEqual(v["n_admitted_mr_correct_sut_pass"],
                             self.per[sut]["n_admitted_mrs"])
            excluded = (self.per[sut]["gate_decision_counts"]["reject"]
                        + self.per[sut]["gate_decision_counts"]["defer"])
            self.assertEqual(v["excluded_from_verdict_space_reject_or_defer"], excluded)

    def test_coverage_map_blind_spots_and_equivalents(self) -> None:
        # Every program has a structural blind spot, and declared equivalent mutants are
        # separated out (expected to escape; not counted as blind spots).
        self.assertEqual(self.d["programs_with_structural_blind_spots"], 5)
        for sut in ALL_SUTS:
            r = self.per[sut]
            self.assertTrue(r["has_structural_blind_spot"])
            self.assertTrue(r["structural_blind_spots"])
            self.assertTrue(r["declared_equivalents_among_escaped"])
            self.assertEqual(
                set(r["structural_blind_spots"]) & set(r["declared_equivalents_among_escaped"]),
                set())
            self.assertTrue(r["per_operator_class_fault_coverage"])

    def test_detection_is_heterogeneous_not_uniform(self) -> None:
        scores = [r["full_set_mutation_score"] for r in self.d["per_sut"]]
        self.assertTrue(all(0.0 < s <= 1.0 for s in scores))
        # tracks the admissible MR set, not a uniform rate
        self.assertLess(min(scores), max(scores))

    def test_mapping_is_program_specific(self) -> None:
        self.assertTrue(self.d["class_to_class_mappings_program_specific"])

    def test_openmc_e5_executed_with_real_solver(self) -> None:
        self.assertEqual(self.d["openmc_e5_status"], "executed")
        self.assertTrue(self.d["openmc_importable"])
        e5 = self.per[OPENMC_SUT]
        self.assertEqual(e5["program_type"], "Monte-Carlo transport")
        # real OpenMC Monte-Carlo k-eigenvalue oracle, recorded version + run settings
        self.assertIn("real OpenMC", e5["oracle"])
        self.assertTrue(e5["openmc_version"])
        self.assertIn("particles", e5["openmc_run_settings"])
        # gate ran on the 7 headline MRs and admitted at least one per executed class
        self.assertEqual(e5["n_candidate_mrs"], 7)
        self.assertGreaterEqual(e5["n_admitted_mrs"], 1)

    def test_reproducibility_artifacts_present(self) -> None:
        # Provenance for the run (incl. the OpenMC environment/data/steps) and the
        # from-source OpenMC build recipe behind E5 must be committed so the result is
        # reproducible from a fresh clone.
        self.assertTrue(PROVENANCE.exists(), f"missing provenance: {PROVENANCE}")
        self.assertTrue(OPENMC_BUILD_SCRIPT.exists(),
                        f"missing OpenMC build recipe: {OPENMC_BUILD_SCRIPT}")
        prov = PROVENANCE.read_text(encoding="utf-8")
        # the provenance documents the multi-group (no continuous-energy data) choice
        self.assertIn("multi-group", prov)
        self.assertIn(self.d["sibling_commit"], prov)

    def test_honesty_boundary(self) -> None:
        hb = self.d["honesty_boundary"].lower()
        self.assertIn("read-only", hb)
        self.assertIn("this paper's gate", hb)
        for forbidden in ("reliability", "superiority", "new contributions"):
            self.assertIn(forbidden, hb)
        self.assertIn("end-to-end", hb)
        # OpenMC executed: the boundary records the multi-group (not continuous-energy) scope
        self.assertIn("multi-group", hb)


if __name__ == "__main__":
    unittest.main()
