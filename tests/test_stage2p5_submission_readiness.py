from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "paper" / "manuscript.md"
IST_MAIN = ROOT / "paper" / "ist-submission" / "main.tex"
BIB = ROOT / "paper" / "ist-submission" / "references.bib"
CITATION_AUDIT = ROOT / "paper" / "citation_audit.md"
STAGE25_AUDIT = ROOT / "paper" / "22_stage2p5_integrity_audit.md"
STAGE3_REVIEW = ROOT / "paper" / "23_stage3_reviewer_simulation.md"
EXPERIMENT_LEDGER = ROOT / "research_assets" / "experiments" / "experiment-ledger.yml"
EVIDENCE_PACKAGE = ROOT / "research_assets" / "experiments" / "evidence-package.md"


STALE_MARKERS = [
    "Reference verification is ongoing",
    "Planned reference groups",
    "Empirical findings will be drafted only after",
    "This paper is planned around four contributions.",
    "This contribution will be stated as a result only after experiment artifacts exist.",
    "The planned result tables will include",
    "The planned study uses",
    "will record repository URL",
    "Violation rates will be reported",
    "The expected value of the study",
    "If the empirical study succeeds",
    "This draft does not provide a final conclusion because empirical evidence is not yet available.",
    "Bibliographic metadata to be verified before submission",
    "Preprint metadata to be verified before submission",
    "Metadata from the Undermind research report; verify venue details before submission",
    "yu2025fluidvelocity",
    "Author Name(s)",
    "organization={Institution}",
]


PR4_BOUNDARY_MARKERS = [
    "failed on 10 of 10 recorded eval frames",
    "median relative L2 0.737",
    "median V/floor 3.96",
    "bounded within-SUT frame-level OOD-stress",
    "one SUT, one checkpoint, one MR, one eval trajectory",
    "not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim",
]


# Theory-lift markers: the admissibility-predicate + two-axis-verdict + relation-space
# framing must appear in BOTH the manuscript and the IST package, kept in lockstep.
FRAMEWORK_MARKERS = [
    "domain-admissibility-gated, relation-indexed",
    "admissible MR",
    "intrinsic error floor",
    "domain-violation magnitude",
    "relation space",
]


# Boundary-guard markers: the hedges that keep the lift from overclaiming. Their
# presence is asserted so a future edit cannot silently turn the framing into a
# completed-applicability-map or calibrated-boundary claim.
FRAMEWORK_GUARD_MARKERS = [
    "We do not claim a completed applicability map",
    "one bounded within-SUT",
    "not as a calibrated boundary measurement",
    "is left to future work",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def bib_keys(text: str) -> set[str]:
    return set(re.findall(r"@\w+\{([^,\s]+)", text))


def tex_citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(r"\\cite[tp]?\{([^}]+)\}", text):
        keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


class Stage25SubmissionReadinessTest(unittest.TestCase):
    def test_manuscript_and_ist_package_have_no_stale_planning_or_unverified_markers(self) -> None:
        combined = read(MANUSCRIPT) + "\n" + read(IST_MAIN) + "\n" + read(BIB)
        for marker in STALE_MARKERS:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, combined)

    def test_ist_main_contains_pr4_bounded_evidence_and_boundaries(self) -> None:
        text = read(IST_MAIN)
        for marker in PR4_BOUNDARY_MARKERS:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_cited_ist_keys_are_bib_backed_and_audited(self) -> None:
        tex = read(IST_MAIN)
        bib = read(BIB)
        audit = read(CITATION_AUDIT)
        cited = tex_citation_keys(tex)
        self.assertGreater(len(cited), 10, "IST draft should contain concrete literature citations")
        available = bib_keys(bib)
        self.assertTrue(cited <= available, f"missing BibTeX keys: {sorted(cited - available)}")
        for key in cited:
            with self.subTest(key=key):
                self.assertIn(f"`{key}`", audit)
                self.assertNotIn(f"`{key}` | UNVERIFIED", audit)
                self.assertNotIn(f"`{key}` | PARTIAL", audit)
                self.assertNotIn(f"`{key}` | NOT_CITED_LEAD", audit)
        self.assertNotIn("\\citep{qi2025physicalfield}", tex)
        self.assertNotIn("\\citet{qi2025physicalfield}", tex)
        self.assertNotIn("\\citep{yu2025fluidvelocity}", tex)
        self.assertNotIn("\\citet{yu2025fluidvelocity}", tex)

    def test_stage25_claim_evidence_audit_records_claim_boundaries(self) -> None:
        text = read(STAGE25_AUDIT)
        required = [
            "PC1-domain-validity-rubric",
            "PC2-mr-card-executable-assets",
            "PC3-baseline-comparison-blocked",
            "PC4-node-permutation-sanity",
            "PC5-conservation-diagnostic-deferred",
            "PC6-mirror-y-ood-stress",
            "PC7-llm-candidate-support-only",
            "claim-ledger.yml",
            "experiment-ledger.yml",
            "metric_ledger.json",
            "failed on 10 of 10 recorded eval frames",
            "absolute conservation remains deferred",
            "seeded-fault and baseline superiority claims remain blocked",
            "not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim",
        ]
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_framework_lift_markers_present_in_manuscript_and_ist(self) -> None:
        manuscript = read(MANUSCRIPT)
        ist = read(IST_MAIN)
        for marker in FRAMEWORK_MARKERS:
            with self.subTest(file="manuscript", marker=marker):
                self.assertIn(marker, manuscript)
            with self.subTest(file="ist_main", marker=marker):
                self.assertIn(marker, ist)

    def test_framework_lift_keeps_evidence_boundary_guards(self) -> None:
        manuscript = read(MANUSCRIPT)
        ist = read(IST_MAIN)
        for marker in FRAMEWORK_GUARD_MARKERS:
            with self.subTest(file="manuscript", marker=marker):
                self.assertIn(marker, manuscript)
            with self.subTest(file="ist_main", marker=marker):
                self.assertIn(marker, ist)

    def test_experiment_ledger_has_single_precondition_check_and_no_phantom_enforcer(self) -> None:
        ledger = read(EXPERIMENT_LEDGER)
        # Exactly one top-level precondition_check (YAML duplicate keys parse unreliably).
        top_level = re.findall(r"(?m)^precondition_check:", ledger)
        self.assertEqual(len(top_level), 1, "experiment-ledger must have one precondition_check")
        # enforced_by must reference real validators, not the removed phantom function.
        phantom = "validate_pr4_mirror_y_artifacts"
        self.assertNotIn(phantom, ledger)
        self.assertNotIn(phantom, read(EVIDENCE_PACKAGE))

    def test_stage3_reviewer_simulation_records_evidence_limited_decision(self) -> None:
        text = read(STAGE3_REVIEW)
        required = [
            "Editorial decision: Major revision before external submission",
            "Reviewer 1 - methodology and evidence",
            "Reviewer 2 - software testing and MR contribution",
            "Reviewer 3 - SciML and domain validity",
            "Devil's Advocate",
            "bounded within-SUT frame-level OOD-stress",
            "one SUT, one checkpoint, one MR, one eval trajectory",
            "not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim",
            "Stage 3 revision roadmap",
        ]
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
