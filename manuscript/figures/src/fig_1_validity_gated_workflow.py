"""Render Figure 1 (validity-gated V&V workflow) as a hand-placed matplotlib diagram.

Replaces the earlier Mermaid source. The decision node "Relation-level verdict"
is a genuine multi-way branch into the four verdict-class outcomes, each flowing
to the evidence ledger (the redundant intermediate "Verdict classes" box and its
direct ledger edge are removed).

Output: manuscript/figures/fig_1_validity_gated_workflow.{pdf,png}
"""
from __future__ import annotations

from pathlib import Path

import figstyle
from figdiagram import Diagram
import matplotlib.pyplot as plt

OUTDIR = str(Path(__file__).resolve().parents[1])


def main() -> None:
    figstyle.apply_style()
    fig, ax = plt.subplots(figsize=(7.2, 9.0))
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_xlim(0, 12.8)
    ax.set_ylim(-0.2, 18.4)

    d = Diagram(ax)

    # candidate-source row
    srcs = [
        ("A1", 1.4, "Equations and\nconstraints"),
        ("A2", 3.95, "Geometry and\nsymmetries"),
        ("A3", 6.4, "Nondimensional\nsimilarity"),
        ("A4", 8.85, "Mesh and graph\nrepresentation"),
        ("A5", 11.4, "Temporal rollout\nbehavior"),
    ]
    for name, cx, txt in srcs:
        d.add(name, cx, 17.1, 2.25, 1.0, txt, shape="artifact", fontsize=8)

    d.add("A", 6.4, 15.2, 4.2, 1.0, "Candidate relation sources", shape="round", fontsize=9)
    d.add("B", 6.4, 13.5, 3.6, 1.0, "NOETHER-informed\norganization", fontsize=9)
    d.add("C", 6.4, 11.4, 3.6, 1.7, "Domain-validity\nrubric", shape="diamond", fontsize=9)
    d.add("D", 2.5, 9.3, 3.1, 1.0, "Rejected / deferred\ncandidates", fontsize=8.5)
    d.add("E", 6.4, 9.3, 2.9, 1.0, "Retained MR card", shape="artifact", fontsize=9)
    d.add("F", 6.4, 7.6, 2.9, 1.0, "Executable MR asset", fontsize=9)
    d.add("G", 6.4, 6.0, 2.9, 1.0, "SUT executions", fontsize=9)
    d.add("H", 6.4, 4.1, 3.6, 1.7, "Relation-level\nverdict", shape="diamond", fontsize=9)

    verds = [
        ("J1", 1.6, "pass / fail"),
        ("J2", 4.8, "skip /\ninconclusive"),
        ("J3", 8.0, "out of domain"),
        ("J4", 11.2, "numerical\ntolerance"),
    ]
    for name, cx, txt in verds:
        d.add(name, cx, 2.05, 2.6, 1.0, txt, fontsize=8.5)

    d.add("I", 6.4, 0.35, 3.2, 1.0, "Evidence ledger", shape="artifact", fontsize=9)

    # edges -------------------------------------------------------------
    for name, cx, _ in srcs:
        d.edge(d.anchor(name, "S"), d.anchor("A", "N"))
    d.edge(d.anchor("A", "S"), d.anchor("B", "N"))
    d.edge(d.anchor("B", "S"), d.anchor("C", "N"))

    # rubric branch
    d.edge(d.anchor("C", "W"), d.anchor("D", "N"), rad=0.0,
           label="invalid, underspecified,\nor out of domain",
           label_xy=(3.7, 10.55), fontsize=7.6)
    d.edge(d.anchor("C", "S"), d.anchor("E", "N"),
           label="physically valid\nand executable",
           label_xy=(6.4, 10.35), label_dx=2.45, fontsize=7.6)

    d.edge(d.anchor("E", "S"), d.anchor("F", "N"))
    d.edge(d.anchor("F", "S"), d.anchor("G", "N"))
    d.edge(d.anchor("G", "S"), d.anchor("H", "N"))

    # verdict decision: multi-way branch, then converge on the ledger
    for name, cx, _ in verds:
        d.edge(d.anchor("H", "S"), d.anchor(name, "N"))
        d.edge(d.anchor(name, "S"), d.anchor("I", "N"))

    figstyle.save_figure(fig, "fig_1_validity_gated_workflow", outdir=OUTDIR, dpi=300)


if __name__ == "__main__":
    main()
