"""Prose-binding guard: main.tex must cite the deepened FNO roster (n=15, Wilson CI).

TDD guard for the FNO roster power deepening (reviewer concern: FNO n=3
underpowered). The manuscript must report the K=15-per-PDE admissibility roster
so the prose matches the committed aggregate. tex-only (manuscript.md is frozen).
"""
from __future__ import annotations
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IST_MAIN = ROOT / "paper/ist-submission/main.tex"


class TestFnoRosterProseBinding(unittest.TestCase):
    def test_main_tex_cites_deepened_fno_roster(self) -> None:
        tex = IST_MAIN.read_text(encoding="utf-8")
        self.assertIn("FNO admissibility roster", tex)
        self.assertIn("admitted on 15/15 per PDE", tex)
