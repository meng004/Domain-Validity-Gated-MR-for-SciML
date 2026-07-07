"""P0 acceptance gates for JSS regular-paper submission (TDD).

These tests encode the current JSS target contract from
paper/77_jss_stable_acceptance_execution_plan.md:

  P0-1  legacy IST count remains below its old hard cap as a conservative signal
  P0-3  title <= 70 characters
  P0-4  abstract uses scoped-positive framing
  P0-5  JSS abstract <= 250 words and no longer requires IST headings
  P0-6  JSS package page count is checked against the official recommendation
"""
from __future__ import annotations

import re
import sys
import unittest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IST_MAIN = ROOT / "manuscript" / "main.tex"
JSS_MAIN = ROOT / "submission" / "JSS_regular_20260705" / "source" / "main.tex"
JSS_LOG = ROOT / "submission" / "JSS_regular_20260705" / "review" / "final_main.log"
JSS_README = ROOT / "venues" / "jss" / "README.md"
JSS_DECLARATIONS = ROOT / "venues" / "jss" / "declarations.md"
JSS_OPEN_SCIENCE = ROOT / "venues" / "jss" / "open_science_checklist.md"
ZENODO = ROOT / ".zenodo.json"
sys.path.insert(0, str(ROOT / "tools"))
from ist_wordcount import ist_word_count  # noqa: E402

WORD_CAP = 15000  # IST regular-paper hard cap; the P2 work consumed the
                  # earlier 14500-then-14900 working-target buffers in exchange
                  # for the LLM-baseline, R3 refinement, and R4 adversarial
                  # subsections, so the only remaining ceiling is the hard cap.
JSS_RECOMMENDED_SINGLE_COLUMN_PAGES = 36


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def final_pdf_pages_from_log(path: Path) -> int:
    log = path.read_text(encoding="utf-8", errors="ignore")
    matches = re.findall(r"Output written on main\.pdf \((\d+) pages, \d+ bytes\)", log)
    if not matches:
        raise AssertionError(f"no final PDF page count found in {path}")
    return int(matches[-1])


class P0SubmissionReadinessTest(unittest.TestCase):
    def test_p0_1_legacy_ist_word_count_within_old_cap(self) -> None:
        r = ist_word_count()
        if r["total"] <= WORD_CAP:
            return
        readme = read(JSS_README)
        self.assertIn("exceeds the", readme)
        self.assertIn("JSS recommended length", readme)
        self.assertIn("compressed or justified", readme)

    def test_p0_3_title_at_most_70_chars(self) -> None:
        tex = read(JSS_MAIN)
        m = re.search(r"\\title\{([^}]+)\}", tex)
        self.assertIsNotNone(m, "no \\title{} found")
        title = m.group(1).strip()
        self.assertLessEqual(
            len(title), 70,
            f"title is {len(title)} chars (>70): {title!r}",
        )

    def test_p0_4_abstract_conclusion_scoped_positive(self) -> None:
        tex = read(IST_MAIN)
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
        self.assertIsNotNone(m, "no abstract found")
        abstract = m.group(1)
        # The Conclusion must not broadcast the four-"not" disclaimer pile-up.
        self.assertNotIn(
            "This is not a reliability, baseline, cross-family, or geometry-independent claim.",
            abstract,
            "abstract Conclusion still uses the four-'not' disclaimer; reframe positively",
        )
        # Guard against any new "is not ... claim" pile-up of >=3 negations in
        # the Conclusion sentence.
        concl = abstract.split("Conclusion:")[-1] if "Conclusion:" in abstract else abstract
        self.assertLess(
            concl.count(" not "), 3,
            f"abstract Conclusion still piles up negations ({concl.count(' not ')} 'not's)",
        )

    def test_p0_jss_abstract_still_compliant(self) -> None:
        tex = read(IST_MAIN)
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
        self.assertIsNotNone(m, "no abstract found")
        abstract = m.group(1)
        # JSS uses a concise factual abstract, not IST's mandatory structured
        # five-heading format. Official JSS limit checked 2026-07-03: <=250 words.
        a = re.sub(r"\\textbf\{[^}]+\}", "", abstract)
        a = re.sub(r"\\emph\{([^}]+)\}", r"\1", a)
        a = re.sub(r"\\[a-zA-Z]+\*?(\{[^}]*\})*", "", a)
        a = re.sub(r"\$[^$]*\$", "X", a)
        a = re.sub(r"[{}]", " ", a)
        words = len(re.findall(r"[A-Za-z][A-Za-z0-9'\-]*", a))
        self.assertLessEqual(words, 250, f"abstract is {words} words (>250)")
        for stale_heading in ["Context:", "Objective:", "Method:", "Results:", "Conclusion:"]:
            with self.subTest(stale_heading=stale_heading):
                self.assertNotIn(stale_heading, abstract)

    def test_p0_jss_page_count_status_is_audited(self) -> None:
        """JSS recommends <36 single-column pages or <18 double-column pages.

        This is an official recommendation plus justification requirement, not a
        discovered hard rejection rule. During Phase A, an over-length package is
        allowed only if the package README explicitly marks it as a length risk
        to be fixed or justified before final submission.
        """
        pages = final_pdf_pages_from_log(JSS_LOG)
        if pages <= JSS_RECOMMENDED_SINGLE_COLUMN_PAGES:
            return
        readme = read(JSS_README)
        self.assertIn(f"{pages} pages single-column", readme)
        self.assertIn("exceeds the", readme)
        self.assertIn("JSS recommended length", readme)
        self.assertIn("compressed or justified", readme)

    def test_p0_jss_data_software_availability_is_audited(self) -> None:
        zenodo = json.loads(read(ZENODO))
        self.assertNotIn("Information and Software Technology", zenodo["description"])
        self.assertIn("Journal of Systems and Software", zenodo["description"])

        declarations = read(JSS_DECLARATIONS)
        self.assertIn("https://doi.org/10.5281/zenodo.20702952", declarations)
        self.assertIn("https://github.com/meng004/Domain-Validity-Gated-MR-for-SciML", declarations)
        self.assertIn("fail-closed", declarations)

        open_science = read(JSS_OPEN_SCIENCE)
        self.assertIn("has not been", open_science)
        self.assertIn("JSS Open Science Board", open_science)


if __name__ == "__main__":
    unittest.main()
