"""Render Figure 1 (validity-gated V&V workflow).

The figure is drawn with reportlab rather than matplotlib so the submission can
be regenerated in the bundled Codex runtime. Node sizes and line breaks are
authored explicitly to avoid text touching box borders.

Output: manuscript/figures/fig_1_validity_gated_workflow.pdf
"""
from __future__ import annotations

from math import atan2, cos, sin, pi
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OUTDIR = Path(__file__).resolve().parents[1]
PDF = OUTDIR / "fig_1_validity_gated_workflow.pdf"

WIDTH = 7.2 * inch
HEIGHT = 9.0 * inch
EDGE = colors.HexColor("#333333")
BLACK = colors.HexColor("#111111")
WHITE = colors.white
LIGHT = colors.HexColor("#f4f4f4")
ARTIFACT = colors.HexColor("#ededed")

X_MIN, X_MAX = 0.0, 12.8
Y_MIN, Y_MAX = -0.2, 18.4
MARGIN_X = 0.36 * inch
MARGIN_Y = 0.32 * inch
DRAW_W = WIDTH - 2 * MARGIN_X
DRAW_H = HEIGHT - 2 * MARGIN_Y


def sx(x: float) -> float:
    return MARGIN_X + (x - X_MIN) / (X_MAX - X_MIN) * DRAW_W


def sy(y: float) -> float:
    return MARGIN_Y + (y - Y_MIN) / (Y_MAX - Y_MIN) * DRAW_H


def sw(w: float) -> float:
    return w / (X_MAX - X_MIN) * DRAW_W


def sh(h: float) -> float:
    return h / (Y_MAX - Y_MIN) * DRAW_H


class Diagram:
    def __init__(self, c: canvas.Canvas) -> None:
        self.c = c
        self.nodes: dict[str, tuple[float, float, float, float]] = {}

    def add(
        self,
        name: str,
        cx: float,
        cy: float,
        w: float,
        h: float,
        text: str,
        *,
        shape: str = "box",
        fontsize: float = 9.0,
    ) -> None:
        pcx, pcy, pw, ph = sx(cx), sy(cy), sw(w), sh(h)
        self.c.setStrokeColor(EDGE)
        self.c.setLineWidth(1.0)
        fill = ARTIFACT if shape == "artifact" else (LIGHT if shape in {"round", "diamond"} else WHITE)
        self.c.setFillColor(fill)

        if shape == "diamond":
            path = self.c.beginPath()
            path.moveTo(pcx, pcy + ph / 2)
            path.lineTo(pcx + pw / 2, pcy)
            path.lineTo(pcx, pcy - ph / 2)
            path.lineTo(pcx - pw / 2, pcy)
            path.close()
            self.c.drawPath(path, stroke=1, fill=1)
        elif shape == "round":
            self.c.roundRect(pcx - pw / 2, pcy - ph / 2, pw, ph, ph / 2, stroke=1, fill=1)
        else:
            self.c.rect(pcx - pw / 2, pcy - ph / 2, pw, ph, stroke=1, fill=1)

        self._text(pcx, pcy, text, fontsize)
        self.nodes[name] = (cx, cy, w, h)

    def anchor(self, name: str, side: str) -> tuple[float, float]:
        cx, cy, w, h = self.nodes[name]
        dx, dy = w / 2, h / 2
        anchors = {
            "N": (cx, cy + dy),
            "S": (cx, cy - dy),
            "E": (cx + dx, cy),
            "W": (cx - dx, cy),
        }
        return sx(anchors[side][0]), sy(anchors[side][1])

    def edge(self, p0: tuple[float, float], p1: tuple[float, float], *, label: str | None = None,
             label_xy: tuple[float, float] | None = None, fontsize: float = 7.6) -> None:
        self._arrow(p0, p1)
        if label and label_xy:
            self._label(sx(label_xy[0]), sy(label_xy[1]), label, fontsize)

    def _arrow(self, p0: tuple[float, float], p1: tuple[float, float]) -> None:
        x0, y0 = p0
        x1, y1 = p1
        angle = atan2(y1 - y0, x1 - x0)
        shorten = 4.0
        x1s = x1 - shorten * cos(angle)
        y1s = y1 - shorten * sin(angle)
        self.c.setStrokeColor(EDGE)
        self.c.setLineWidth(0.9)
        self.c.line(x0, y0, x1s, y1s)
        head = 6.0
        left = angle + pi * 0.82
        right = angle - pi * 0.82
        path = self.c.beginPath()
        path.moveTo(x1, y1)
        path.lineTo(x1 + head * cos(left), y1 + head * sin(left))
        path.lineTo(x1 + head * cos(right), y1 + head * sin(right))
        path.close()
        self.c.setFillColor(EDGE)
        self.c.drawPath(path, stroke=0, fill=1)

    def _text(self, x: float, y: float, text: str, fontsize: float) -> None:
        self.c.setFillColor(BLACK)
        self.c.setFont("Times-Roman", fontsize)
        lines = text.split("\n")
        leading = fontsize * 1.18
        start = y + (len(lines) - 1) * leading / 2 - fontsize * 0.35
        for i, line in enumerate(lines):
            self.c.drawCentredString(x, start - i * leading, line)

    def _label(self, x: float, y: float, text: str, fontsize: float) -> None:
        lines = text.split("\n")
        self.c.setFont("Times-Roman", fontsize)
        pad = 3.0
        leading = fontsize * 1.15
        width = max(stringWidth(line, "Times-Roman", fontsize) for line in lines) + 2 * pad
        height = len(lines) * leading + 2 * pad
        self.c.setFillColor(WHITE)
        self.c.roundRect(x - width / 2, y - height / 2, width, height, 3, stroke=0, fill=1)
        self.c.setFillColor(BLACK)
        start = y + (len(lines) - 1) * leading / 2 - fontsize * 0.35
        for i, line in enumerate(lines):
            self.c.drawCentredString(x, start - i * leading, line)


def main() -> None:
    c = canvas.Canvas(str(PDF), pagesize=(WIDTH, HEIGHT))
    d = Diagram(c)

    srcs = [
        ("A1", 1.4, "Equations and\nconstraints"),
        ("A2", 3.95, "Geometry and\nsymmetries"),
        ("A3", 6.4, "Nondimensional\nsimilarity"),
        ("A4", 8.85, "Mesh and graph\nrepresentation"),
        ("A5", 11.4, "Temporal rollout\nbehavior"),
    ]
    for name, cx, txt in srcs:
        d.add(name, cx, 17.1, 2.35, 1.05, txt, shape="artifact", fontsize=8)

    d.add("A", 6.4, 15.2, 4.3, 1.0, "Candidate relation sources", shape="round", fontsize=9)
    d.add("B", 6.4, 13.5, 3.8, 1.0, "NOETHER-informed\norganization", fontsize=9)
    d.add("C", 6.4, 11.4, 3.8, 1.7, "Domain-validity\nrubric", shape="diamond", fontsize=9)
    d.add("D", 2.5, 9.3, 3.2, 1.0, "Rejected / deferred\ncandidates", fontsize=8.5)
    d.add("E", 6.4, 9.3, 3.2, 1.0, "Retained MR card", shape="artifact", fontsize=9)
    d.add("F", 6.4, 7.6, 3.25, 1.08, "Executable\nMR asset", fontsize=9)
    d.add("G", 6.4, 6.0, 3.2, 1.0, "SUT executions", fontsize=9)
    d.add("H", 6.4, 4.1, 3.8, 1.7, "Relation-level\nverdict", shape="diamond", fontsize=9)

    verds = [
        ("J1", 1.6, "pass / fail"),
        ("J2", 4.8, "skip /\ninconclusive"),
        ("J3", 8.0, "out of domain"),
        ("J4", 11.2, "numerical\ntolerance"),
    ]
    for name, cx, txt in verds:
        d.add(name, cx, 2.05, 2.65, 1.0, txt, fontsize=8.5)

    d.add("I", 6.4, 0.35, 3.3, 1.0, "Evidence ledger", shape="artifact", fontsize=9)

    for name, _, _ in srcs:
        d.edge(d.anchor(name, "S"), d.anchor("A", "N"))
    d.edge(d.anchor("A", "S"), d.anchor("B", "N"))
    d.edge(d.anchor("B", "S"), d.anchor("C", "N"))
    d.edge(d.anchor("C", "W"), d.anchor("D", "N"),
           label="invalid, underspecified,\nor out of domain", label_xy=(3.65, 10.55))
    d.edge(d.anchor("C", "S"), d.anchor("E", "N"),
           label="physically valid\nand executable", label_xy=(8.65, 10.35))
    d.edge(d.anchor("E", "S"), d.anchor("F", "N"))
    d.edge(d.anchor("F", "S"), d.anchor("G", "N"))
    d.edge(d.anchor("G", "S"), d.anchor("H", "N"))

    for name, _, _ in verds:
        d.edge(d.anchor("H", "S"), d.anchor(name, "N"))
        d.edge(d.anchor(name, "S"), d.anchor("I", "N"))

    c.showPage()
    c.save()


if __name__ == "__main__":
    main()
