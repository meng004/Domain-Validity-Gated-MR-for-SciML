"""Render Figure 2 (MR-card-to-executable-asset data flow) as a hand-placed matplotlib diagram.

Replaces the earlier Mermaid source so node positions and edge routing are exact:
  1. Run logs sits between Source run and Follow-up run; the run->output-mapping
     edges enter Output mapping at its corners, so no edge crosses Source run->Run logs.
  2. Metric outputs is to the right of Metric computation; the MR card->Exclusion
     check edge is routed down the left margin, clear of Metric outputs.
  3. The eligible / excluded labels sit beside their (oppositely bowed) edges, off the lines.

Output: manuscript/figures/fig_2_mr_asset_dataflow.{pdf,png}
"""
from __future__ import annotations

from pathlib import Path

import figstyle
from figdiagram import Diagram
import matplotlib.pyplot as plt

OUTDIR = str(Path(__file__).resolve().parents[1])


def main() -> None:
    figstyle.apply_style()
    fig, ax = plt.subplots(figsize=(7.8, 9.4))
    ax.set_aspect("auto")
    ax.axis("off")
    ax.set_xlim(-0.4, 10.4)
    ax.set_ylim(-2.4, 17.2)

    d = Diagram(ax)

    d.add("A", 3.9, 15.7, 4.8, 1.9,
          "MR card\nbasis; preconditions; mapping;\nmetric; tolerance; exclusion rule",
          fontsize=8.5)
    d.add("C", 5.8, 13.2, 2.7, 1.0, "Follow-up transform", fontsize=8.5)
    d.add("B", 1.8, 11.3, 2.4, 1.0, "Source case", fontsize=8.5)
    d.add("D", 5.8, 11.3, 2.4, 1.0, "Follow-up case", fontsize=8.5)
    d.add("N", 8.8, 11.3, 2.7, 1.0, "Transformation record", shape="artifact", fontsize=8.5)
    d.add("E", 1.8, 9.4, 2.4, 1.0, "Source run", fontsize=8.5)
    d.add("F", 5.8, 9.4, 2.4, 1.0, "Follow-up run", fontsize=8.5)
    d.add("M", 3.8, 7.95, 2.0, 0.95, "Run logs", shape="artifact", fontsize=8.5)
    d.add("G", 3.8, 6.3, 2.6, 1.0, "Output mapping", fontsize=8.5)
    d.add("H", 3.8, 4.6, 2.7, 1.0, "Metric computation", fontsize=8.5)
    d.add("L", 7.6, 4.6, 2.5, 1.0, "Metric outputs", shape="artifact", fontsize=8.5)
    d.add("I", 3.8, 3.0, 2.8, 1.6, "Exclusion check", shape="diamond", fontsize=8.5)
    d.add("J", 3.8, 0.8, 2.8, 1.6, "Verdict rule", shape="diamond", fontsize=8.5)
    d.add("K", 3.8, -1.5, 2.7, 1.0, "Verdict ledger", shape="artifact", fontsize=8.5)

    # top fan-out from the MR card
    d.edge(d.bottom_at("A", 1.9), d.anchor("B", "N"))          # A -> Source case
    d.edge(d.bottom_at("A", 5.8), d.anchor("C", "N"))          # A -> Follow-up transform
    d.edge(d.anchor("C", "S"), d.anchor("D", "N"))             # C -> Follow-up case
    d.elbow([d.anchor("C", "E"), (8.8, 13.2), d.anchor("N", "N")])  # C -> Transformation record (enter from top, clear of Follow-up case)
    d.edge(d.anchor("B", "S"), d.anchor("E", "N"))             # B -> Source run
    d.edge(d.anchor("D", "S"), d.anchor("F", "N"))             # D -> Follow-up run

    # runs -> run logs (centered) and -> output mapping (entering at corners)
    d.edge(d.anchor("E", "S"), d.anchor("G", "NW"))            # Source run -> Output mapping (left)
    d.edge(d.anchor("F", "S"), d.anchor("G", "NE"))            # Follow-up run -> Output mapping (right)
    d.edge((2.55, 8.95), d.anchor("M", "NW"))                  # Source run -> Run logs
    d.edge((5.05, 8.95), d.anchor("M", "NE"))                  # Follow-up run -> Run logs

    d.edge(d.anchor("G", "S"), d.anchor("H", "N"))             # Output mapping -> Metric computation
    d.edge(d.anchor("H", "E"), d.anchor("L", "W"))             # Metric computation -> Metric outputs (right)
    d.edge(d.anchor("H", "S"), d.anchor("I", "N"))             # Metric computation -> Exclusion check

    # MR card -> Exclusion check / Verdict rule, as two nested left-margin buses,
    # routed clear of the left boxes (Source case/run left edge is at x=0.6) and of
    # each other: inner rail -> Exclusion check (higher), outer rail -> Verdict rule (lower).
    d.elbow([(1.5, 15.2), (0.3, 15.2), (0.3, 3.0), d.anchor("I", "W")])
    d.elbow([d.anchor("A", "W"), (0.0, 15.7), (0.0, 0.8), d.anchor("J", "W")])

    # Exclusion check decision: eligible proceeds to the verdict rule; excluded is logged directly.
    d.edge(d.anchor("I", "S"), d.anchor("J", "N"),
           label="eligible", label_xy=(3.05, 1.95), fontsize=8)
    d.elbow([d.anchor("I", "E"), (6.2, 3.0), (6.2, -1.5), d.anchor("K", "E")],
            label="excluded", label_xy=(6.55, 0.9), fontsize=8)

    # Verdict rule decision: pass / fail, both recorded in the ledger.
    d.edge(d.anchor("J", "S"), d.anchor("K", "N"), rad=0.5,
           label="pass", label_xy=(3.05, -0.55), fontsize=8)
    d.edge(d.anchor("J", "S"), d.anchor("K", "N"), rad=-0.5,
           label="fail", label_xy=(4.55, -0.55), fontsize=8)

    figstyle.save_figure(fig, "fig_2_mr_asset_dataflow", outdir=OUTDIR, dpi=300)


if __name__ == "__main__":
    main()
