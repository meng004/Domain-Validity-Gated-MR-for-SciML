from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
JSS_MAIN = ROOT / "manuscript" / "main.tex"
AUDIT = ROOT / "paper" / "100_jss_concept_density_audit.md"
REVIEW = ROOT / "paper" / "101_jss_concept_density_repair_review.md"


class JSSConceptDensityRepairTests(unittest.TestCase):
    def read_main(self) -> str:
        return JSS_MAIN.read_text(encoding="utf-8")

    def test_phase_a_audit_records_density_findings_and_drift_check(self):
        audit = AUDIT.read_text(encoding="utf-8")

        self.assertIn("Phase A review: pass", audit)
        self.assertIn("Theme-drift check: pass", audit)
        self.assertIn("lines 88--109", audit)
        self.assertIn("lines 135--149", audit)
        self.assertIn("numerical decidability", audit)
        self.assertIn("MR card", audit)
        self.assertIn("typed verdict", audit)
        self.assertIn("claim ledger", audit)
        self.assertIn("No new experiment", audit)

    def test_main_text_places_definitions_in_method_not_intro_reader_map(self):
        tex = self.read_main()

        self.assertNotIn(r"\paragraph{Reader map.}", tex)
        self.assertIn(
            "The method turns a physics-derived candidate relation into an auditable V\\&V check only after three steps are made explicit: admissibility, executable checking, and verdict interpretation.",
            tex,
        )
        self.assertIn(r"\textbf{Definitions.}", tex)
        for marker in [
            "candidate relation",
            "admissibility gate",
            "executable check",
            "typed verdict",
            "numerically decidable",
        ]:
            self.assertIn(marker, tex)

    def test_core_workflow_is_formalized_once(self):
        tex = self.read_main()

        self.assertIn(r"r=(b,T,M,m,\tau,P)", tex)
        self.assertIn(r"G(r,s,x)\in\{\mathrm{admit},\mathrm{reject},\mathrm{stress},\mathrm{defer}\}", tex)
        self.assertIn(r"E(r,s,x)=(y,y',z)", tex)
        self.assertIn(r"V(G,z)", tex)
        self.assertIn(
            "Only an admitted relation with an in-domain fail verdict may support a SUT-inconsistency claim",
            tex,
        )

    def test_intro_keeps_detailed_definitions_out_of_front_matter(self):
        tex = self.read_main()
        intro_start = tex.index(r"\section{Introduction}")
        method_start = tex.index(r"\label{sec:method}")
        intro = tex[intro_start:method_start]

        for term in ["MR card", "semantic witness", r"r=(b,T,M,m,\tau,P)"]:
            with self.subTest(term=term):
                self.assertNotIn(term, intro)

    def test_concept_density_repair_review_passes_without_major_drift(self):
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Concept-density decision: pass", review)
        self.assertIn("No reviewer viewpoint classifies concept density as a Major blocker", review)
        self.assertIn("Theme-drift check: pass", review)
        self.assertIn("Data and conclusion honesty: pass", review)

    def test_plain_language_rqs_preserve_scope(self):
        tex = self.read_main()
        rqs = re.search(
            r"This objective is decomposed into four research questions:(.*?)\\subsection\{Experimental subjects\}",
            tex,
            re.S,
        )
        self.assertIsNotNone(rqs)
        block = rqs.group(1)

        self.assertNotIn(r"\begin{description}", block)
        for verb in ["admissible", "executable", "verdicts", "utility"]:
            self.assertIn(verb, block)
        self.assertIn("not population-wide defect-detection effectiveness", tex)


if __name__ == "__main__":
    unittest.main()
