from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "manuscript.md"
IST_MAIN = ROOT / "manuscript" / "main.tex"
STAGE4_REVIEW = ROOT / "paper" / "24_stage4_revision_re_review.md"
LATEX_LOG = ROOT / "manuscript" / "main.log"
BIB = ROOT / "manuscript" / "main.bbl"
PDF = ROOT / "submissions" / "IST" / "main.pdf"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Stage4RevisionReadinessTest(unittest.TestCase):
    def test_manuscript_has_reviewer_facing_tables_and_related_work_positioning(self) -> None:
        text = read(MANUSCRIPT)
        for marker in [
            "### 5.1 Claim-to-Evidence Map",
            "### 5.2 MR-Card-to-Verdict Map",
            "### 2.7 What Is New and What Is Not New",
            "PC6-mirror-y-ood-stress",
            "failed on 10 of 10 recorded eval frames",
            "not a reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim",
            "absolute conservation remains deferred",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_ist_latex_has_compact_tables_and_new_not_new_section(self) -> None:
        text = read(IST_MAIN)
        for marker in [
            "\\subsection{Claim-to-evidence map}",
            "\\subsection{MR-card-to-verdict map}",
            "\\subsection{What is new and what is not new}",
            "\\small",
            "\\setlength{\\tabcolsep}{3pt}",
            "PC6-mirror-y-ood-stress",
            "failed on 10 of 10 recorded eval frames",
            "absolute conservation remains deferred",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_stage4_re_review_record_exists_and_is_evidence_limited(self) -> None:
        text = read(STAGE4_REVIEW)
        for marker in [
            "Stage 4 revision and Stage 3' re-review record",
            "Revision decision: proceed to focused re-review",
            "claim-to-evidence table",
            "MR-card-to-verdict table",
            "what is new and what is not new",
            "Remaining risk: table layout polish and external reviewer judgment",
        ]:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_final_latex_artifacts_exist_without_unresolved_references_or_overfull_boxes(self) -> None:
        self.assertTrue(PDF.exists() and PDF.stat().st_size > 100_000)
        self.assertTrue(BIB.exists() and BIB.stat().st_size > 5_000)
        # pdflatex logs are not guaranteed UTF-8: Under/Overfull-box warnings
        # echo font-encoded glyph bytes (e.g. the "o-umlaut" in the Engstrom
        # reference), which are never part of the strings checked below. Decode
        # tolerantly so a benign accented byte cannot mask the substantive build
        # checks. The forbidden-string assertions are unchanged.
        log = LATEX_LOG.read_text(encoding="utf-8", errors="ignore")
        self.assertNotIn("Citation(s) may have changed", log)
        self.assertNotIn("Label(s) may have changed", log)
        self.assertNotIn("undefined", log.lower())
        self.assertNotRegex(log, re.compile(r"Overfull \\hbox"))
