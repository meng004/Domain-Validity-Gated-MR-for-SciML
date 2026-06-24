"""Minimal flow-diagram primitives on matplotlib for the paper's process figures.

Unlike Mermaid (dagre auto-layout), node positions, edge routing, and label
sides are authored by hand here, so crossings and label placement are exact.
Shapes: process box, decision diamond, rounded terminal, artifact box.
Used by fig_1_validity_gated_workflow.py and fig_2_mr_asset_dataflow.py.
"""
from __future__ import annotations

import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from matplotlib.path import Path

EDGE = "#333333"
PROCESS_FC = "#ffffff"
ARTIFACT_FC = "#ededed"
DECISION_FC = "#f4f4f4"
ROUND_FC = "#f4f4f4"


class Diagram:
    """A hand-placed flow diagram on a matplotlib Axes (data coords, y-up)."""

    def __init__(self, ax):
        self.ax = ax
        self.nodes = {}

    # ---- nodes ----
    def add(self, name, cx, cy, w, h, text, shape="box", fc=None, fontsize=9):
        ax = self.ax
        if shape == "diamond":
            fc = fc or DECISION_FC
            pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
            ax.add_patch(mpatches.Polygon(pts, closed=True, facecolor=fc,
                                          edgecolor=EDGE, lw=1.0, zorder=2))
        elif shape == "round":
            fc = fc or ROUND_FC
            ax.add_patch(mpatches.FancyBboxPatch(
                (cx - w / 2 + 0.18, cy - h / 2), w - 0.36, h,
                boxstyle="round,pad=0.18,rounding_size=0.45",
                facecolor=fc, edgecolor=EDGE, lw=1.0, zorder=2))
        else:  # box / artifact
            fc = fc or (ARTIFACT_FC if shape == "artifact" else PROCESS_FC)
            ax.add_patch(mpatches.Rectangle((cx - w / 2, cy - h / 2), w, h,
                                            facecolor=fc, edgecolor=EDGE, lw=1.0, zorder=2))
        ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize,
                color="#111111", zorder=3, linespacing=1.25)
        self.nodes[name] = (cx, cy, w, h)
        return name

    def anchor(self, name, side):
        cx, cy, w, h = self.nodes[name]
        dx, dy = w / 2, h / 2
        return {
            "N": (cx, cy + dy), "S": (cx, cy - dy), "E": (cx + dx, cy), "W": (cx - dx, cy),
            "NE": (cx + dx, cy + dy), "NW": (cx - dx, cy + dy),
            "SE": (cx + dx, cy - dy), "SW": (cx - dx, cy - dy), "C": (cx, cy),
        }[side]

    def bottom_at(self, name, x):
        cx, cy, w, h = self.nodes[name]
        return (x, cy - h / 2)

    def top_at(self, name, x):
        cx, cy, w, h = self.nodes[name]
        return (x, cy + h / 2)

    # ---- edges ----
    def _arrowhead(self, path_or_pts, posA=None, posB=None):
        if posA is not None:
            return FancyArrowPatch(posA, posB, arrowstyle="-|>", mutation_scale=11,
                                   lw=0.9, color=EDGE, shrinkA=1, shrinkB=3, zorder=1)
        return FancyArrowPatch(path=path_or_pts, arrowstyle="-|>", mutation_scale=11,
                               lw=0.9, color=EDGE, shrinkA=1, shrinkB=3, zorder=1)

    def edge(self, p0, p1, rad=0.0, label=None, label_xy=None, label_dx=0.0,
             label_dy=0.0, fontsize=8):
        a = FancyArrowPatch(p0, p1, connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
                            mutation_scale=11, lw=0.9, color=EDGE, shrinkA=1, shrinkB=3, zorder=1)
        self.ax.add_patch(a)
        if label:
            x, y = label_xy or ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
            self._label(x + label_dx, y + label_dy, label, fontsize)

    def elbow(self, points, label=None, label_xy=None, label_dx=0.0, label_dy=0.0, fontsize=8):
        verts = list(points)
        path = Path(verts, [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1))
        self.ax.add_patch(self._arrowhead(path))
        if label:
            x, y = label_xy or verts[len(verts) // 2]
            self._label(x + label_dx, y + label_dy, label, fontsize)

    def _label(self, x, y, text, fontsize):
        self.ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
                     color="#111111", zorder=4,
                     bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
