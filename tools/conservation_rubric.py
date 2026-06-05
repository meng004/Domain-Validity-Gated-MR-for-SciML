"""Evidence-gated logic for the discrete divergence / mass-conservation MR.

For incompressible flow the continuity equation requires a divergence-free
velocity field. On a coarse unstructured mesh, however, even the ground-truth
field has a non-negligible *discrete* divergence, so an absolute ``div ~ 0``
tolerance is not calibratable -- which is exactly why the design-time candidate
ledger keeps this relation ``deferred``.

This module supplies:

- a P1 (linear, constant-per-cell) discrete divergence operator on a triangular
  mesh, with an area-weighted RMS summary;
- ``classify_absolute_admissible`` -- whether an absolute divergence-free
  tolerance is justifiable given the measured reference divergence (it is not
  when the reference divergence dwarfs the absolute tolerance);
- ``classify_conservation_verdict`` -- a *reference-relative* diagnostic that
  flags a conservation regression only when the surrogate's discrete divergence
  exceeds the ground-truth field's by more than a documented factor.

All functions are pure (numpy only, no SUT/torch dependency).
"""
from __future__ import annotations

import numpy as np

DEFERRED_UNCALIBRATED = "deferred-uncalibrated-absolute-tolerance"
ABSOLUTE_ADMISSIBLE = "absolute-divergence-free-admissible"


def cell_divergence(
    pos: np.ndarray, cells: np.ndarray, vel: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Constant-per-triangle divergence of a P1-interpolated velocity field.

    Returns ``(divergence_per_cell, area_per_cell)``. Uses the standard linear
    shape-function gradients: for a triangle with vertices ``p0,p1,p2`` and
    ``2A = x0(y1-y2)+x1(y2-y0)+x2(y0-y1)``,
    ``du/dx = (u0 b0 + u1 b1 + u2 b2)/2A`` with ``b_i = y_j - y_k`` and
    ``dv/dy = (v0 c0 + v1 c1 + v2 c2)/2A`` with ``c_i = x_k - x_j``.
    """
    pos = np.asarray(pos, dtype=np.float64)
    vel = np.asarray(vel, dtype=np.float64)
    cells = np.asarray(cells)
    p = pos[cells]                       # (C, 3, 2)
    x0, x1, x2 = p[:, 0, 0], p[:, 1, 0], p[:, 2, 0]
    y0, y1, y2 = p[:, 0, 1], p[:, 1, 1], p[:, 2, 1]
    two_a = x0 * (y1 - y2) + x1 * (y2 - y0) + x2 * (y0 - y1)
    b0, b1, b2 = y1 - y2, y2 - y0, y0 - y1
    c0, c1, c2 = x2 - x1, x0 - x2, x1 - x0
    ux = vel[cells][:, :, 0]
    uy = vel[cells][:, :, 1]
    dux_dx = (ux[:, 0] * b0 + ux[:, 1] * b1 + ux[:, 2] * b2) / two_a
    duy_dy = (uy[:, 0] * c0 + uy[:, 1] * c1 + uy[:, 2] * c2) / two_a
    return dux_dx + duy_dy, 0.5 * np.abs(two_a)


def divergence_rms(
    pos: np.ndarray, cells: np.ndarray, vel: np.ndarray, mask: np.ndarray | None = None
) -> float:
    """Area-weighted root-mean-square of the per-cell discrete divergence.

    When ``mask`` (a per-cell boolean array) is given, only the selected cells
    contribute -- e.g. interior cells, to isolate the bulk field from cells that
    touch prescribed-boundary nodes.
    """
    div, area = cell_divergence(pos, cells, vel)
    if mask is not None:
        mask = np.asarray(mask, dtype=bool)
        div, area = div[mask], area[mask]
    total = float(area.sum())
    if total <= 0.0:
        return float("nan")
    return float(np.sqrt(np.sum(area * div ** 2) / total))


def interior_cell_mask(
    cells: np.ndarray, node_type: np.ndarray, interior_types: tuple = (0, 5)
) -> np.ndarray:
    """Per-cell mask: True when all three nodes are interior (not prescribed).

    For cylinder flow the prescribed-boundary nodes are INFLOW (Dirichlet) and
    WALL (no-slip); interior cells (NORMAL/OUTFLOW only) carry the bulk field the
    model is free to choose, so they isolate model behaviour from copied
    boundary values.
    """
    node_type = np.asarray(node_type)
    cells = np.asarray(cells)
    in_interior = np.isin(node_type[cells], list(interior_types))  # (C, 3)
    return in_interior.all(axis=1)


def classify_absolute_admissible(
    reference_nondim_divergence: float, *, abs_tol: float
) -> str:
    """Decide whether an absolute divergence-free tolerance is justifiable.

    When the reference (ground-truth) dimensionless divergence is far above the
    absolute tolerance, an absolute ``div <= abs_tol`` relation cannot be honestly
    applied and the absolute relation stays deferred.
    """
    if not np.isfinite(reference_nondim_divergence):
        return DEFERRED_UNCALIBRATED
    if reference_nondim_divergence > abs_tol:
        return DEFERRED_UNCALIBRATED
    return ABSOLUTE_ADMISSIBLE


def classify_conservation_verdict(
    pred_divergence_rms: float,
    reference_divergence_rms: float,
    *,
    threshold: float,
) -> str:
    """Reference-relative conservation diagnostic.

    - ``pass``: the surrogate's discrete divergence is at most ``threshold`` times
      the reference field's (no conservation regression);
    - ``fail``: it exceeds that factor;
    - ``inconclusive``: the reference divergence is zero/non-finite (no ratio) or
      either input is non-finite.
    """
    if not (np.isfinite(pred_divergence_rms) and np.isfinite(reference_divergence_rms)):
        return "inconclusive"
    if reference_divergence_rms <= 0.0:
        return "inconclusive"
    ratio = pred_divergence_rms / reference_divergence_rms
    return "pass" if ratio <= threshold else "fail"
