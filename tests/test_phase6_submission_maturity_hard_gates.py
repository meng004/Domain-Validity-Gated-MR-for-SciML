"""Phase 6 submission-maturity hard gates.

These tests guard the immediate IST submission blockers identified in the
2026-06-11 maturity assessment. They intentionally do not assert that the paper
is ready to submit; Phase 5 remains not-yet-submit until new empirical evidence
closes the major-revision gaps.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IST_MAIN = ROOT / "manuscript" / "main.tex"
MANUSCRIPT = ROOT / "manuscript" / "manuscript.md"
PHASE5_TRIAGE = ROOT / "paper" / "33_phase5_review_panel_triage.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def latex_labels(tex: str) -> list[str]:
    return re.findall(r"\\label\{([^}]+)\}", tex)


def latex_refs(tex: str) -> list[str]:
    refs: list[str] = []
    for match in re.finditer(r"\\(?:page)?ref\{([^}]+)\}", tex):
        refs.extend(label.strip() for label in match.group(1).split(",") if label.strip())
    return refs


class Phase6SubmissionMaturityHardGatesTest(unittest.TestCase):
    def test_submission_sources_have_no_unresolved_merge_conflict_markers(self) -> None:
        for path in [IST_MAIN, MANUSCRIPT]:
            text = read(path)
            for marker in ["<<<<<<<", "=======", ">>>>>>>"]:
                with self.subTest(path=path.relative_to(ROOT), marker=marker):
                    self.assertNotIn(marker, text)

    def test_ist_source_has_no_unresolved_merge_conflict_markers(self) -> None:
        tex = read(IST_MAIN)
        for marker in ["<<<<<<<", "=======", ">>>>>>>"]:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, tex)

    def test_ist_source_has_no_duplicate_labels(self) -> None:
        labels = latex_labels(read(IST_MAIN))
        duplicates = sorted({label for label in labels if labels.count(label) > 1})
        self.assertEqual(duplicates, [], f"duplicate LaTeX labels: {duplicates}")

    def test_ist_source_has_no_undefined_internal_references(self) -> None:
        tex = read(IST_MAIN)
        labels = set(latex_labels(tex))
        refs = sorted(set(latex_refs(tex)))
        missing = [ref for ref in refs if ref not in labels]
        self.assertEqual(missing, [], f"undefined LaTeX refs: {missing}")

    def test_r3_nonmonotone_figure_reference_is_not_stale(self) -> None:
        tex = read(IST_MAIN)
        has_ref = "fig:r3-pc-nonmonotone" in latex_refs(tex)
        has_label = "fig:r3-pc-nonmonotone" in latex_labels(tex)
        self.assertEqual(
            has_ref,
            has_label,
            "fig:r3-pc-nonmonotone must either be defined as a figure label or not referenced",
        )

    def test_manuscript_avoids_stale_manual_figure_numbers(self) -> None:
        manuscript = read(MANUSCRIPT)
        self.assertIsNone(
            re.search(r"\bFigure\s+\d+(?:\.\d+)+", manuscript),
            "manuscript should not contain stale manual figure numbers such as 'Figure 5.6'",
        )

    def test_phase5_major_revision_status_remains_explicit(self) -> None:
        triage = read(PHASE5_TRIAGE)
        required = [
            "major-revision / not-yet-submit",
            "new evidence is added",
            "should not be repaired by prose alone",
        ]
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, triage)


if __name__ == "__main__":
    unittest.main()
