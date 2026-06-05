"""Evidence-gated decision logic for the mirror-y metamorphic relation.

Mirror-y equivariance is not guaranteed by the model architecture (unlike node
permutation): it holds only when the computational domain is mirror-symmetric
about the chosen axis and the model has learned that symmetry. This module turns
the *measured* geometry of a real source case into a rubric decision:

- ``classify_mirror_preconditions`` decides whether an EXACT mirror equivariance
  relation is admissible, or whether the case is ``out-of-relation-domain`` (the
  exact-mirror preconditions are not met on the real mesh) and must be handled
  only as an OOD-stress probe.
- ``classify_ood_stress_verdict`` scores the downgraded OOD-stress probe, never
  claiming a violation when the measured residual is within the mapping-error
  floor of the approximate reflection correspondence.

All functions are pure (numpy only, no SUT/torch dependency) so the decision
logic is unit-testable without running the model.
"""
from __future__ import annotations

import numpy as np

# Decision vocabulary (aligned with the MR card verdicts and the domain-validity
# rubric's allowed decisions).
EXACT_ADMISSIBLE = "exact-mirror-admissible"
OUT_OF_RELATION_DOMAIN = "out-of-relation-domain"
DOWNGRADE_OOD_STRESS = "retained-ood-stress"


def reflection_map(pos: np.ndarray, axis: float) -> np.ndarray:
    """Nearest-neighbour reflection correspondence about the line ``y = axis``.

    Returns ``pi`` with ``pi[i]`` the index of the original node closest to the
    reflection of node ``i``. For a perfectly mirror-symmetric mesh this is the
    exact reflection permutation; otherwise it is an approximate correspondence.
    """
    pos = np.asarray(pos, dtype=np.float64)
    reflected = pos.copy()
    reflected[:, 1] = 2.0 * axis - pos[:, 1]
    d2 = ((reflected[:, None, :] - pos[None, :, :]) ** 2).sum(-1)
    return d2.argmin(1)


def _median_edge_length(pos: np.ndarray, cells: np.ndarray) -> float:
    pairs = set()
    for cell in np.asarray(cells):
        a, b, c = (int(cell[0]), int(cell[1]), int(cell[2]))
        for u, v in ((a, b), (b, c), (c, a)):
            if u != v:
                pairs.add((u, v) if u < v else (v, u))
    if not pairs:
        return 0.0
    lengths = [float(np.linalg.norm(pos[u] - pos[v])) for u, v in pairs]
    return float(np.median(lengths))


def measure_reflection_symmetry(
    pos: np.ndarray, node_type: np.ndarray, cells: np.ndarray, axis: float
) -> dict:
    """Measure how mirror-symmetric a mesh is about ``y = axis`` (pure numbers)."""
    pos = np.asarray(pos, dtype=np.float64)
    node_type = np.asarray(node_type)
    n = pos.shape[0]
    pi = reflection_map(pos, axis)
    reflected = pos.copy()
    reflected[:, 1] = 2.0 * axis - pos[:, 1]
    nn_dist = np.linalg.norm(reflected - pos[pi], axis=1)
    median_edge = _median_edge_length(pos, cells)
    max_nn = float(nn_dist.max())
    return {
        "axis": float(axis),
        "num_nodes": int(n),
        "max_nn_dist": max_nn,
        "mean_nn_dist": float(nn_dist.mean()),
        "median_edge_length": median_edge,
        "max_nn_over_edge": float(max_nn / median_edge) if median_edge > 0 else float("inf"),
        "bijection": bool(len(set(pi.tolist())) == n),
        "type_match_rate": float((node_type[pi] == node_type).mean()),
    }


def classify_mirror_preconditions(
    metrics: dict, *, max_nn_over_edge: float = 0.05, min_type_match: float = 0.999
) -> str:
    """Decide whether exact mirror-y equivariance is admissible for this case.

    The exact relation requires a clean reflection permutation: the reflection
    must be a bijection, the reflected nodes must coincide with originals well
    within a mesh edge length, and node-type labels must be mirror-consistent.
    Otherwise the case is out-of-relation-domain for the exact MR.
    """
    if (
        metrics.get("bijection")
        and metrics.get("max_nn_over_edge", float("inf")) <= max_nn_over_edge
        and metrics.get("type_match_rate", 0.0) >= min_type_match
    ):
        return EXACT_ADMISSIBLE
    return OUT_OF_RELATION_DOMAIN


def classify_ood_stress_verdict(
    violation: float,
    floor: float,
    *,
    tolerance: float,
    ratio_threshold: float = 2.0,
) -> str:
    """Score the downgraded OOD-stress probe.

    - ``pass`` when the residual is within the MR tolerance;
    - ``fail`` when it both exceeds tolerance and stands clearly above the
      mapping-error floor (``violation / floor >= ratio_threshold``);
    - ``inconclusive`` when the residual is comparable to the floor (so the
      approximate reflection mapping, not the model, could explain it) or when
      any input is non-finite.
    """
    if not (np.isfinite(violation) and np.isfinite(floor)):
        return "inconclusive"
    if violation <= tolerance:
        return "pass"
    if floor > 0 and (violation / floor) < ratio_threshold:
        return "inconclusive"
    return "fail"
