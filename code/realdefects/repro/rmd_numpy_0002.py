"""Reproduce RMD-NUMPY-0002 (numpy einsum optimize-equivalence, issue #30349).

MR (optimization-invariance): np.einsum(expr, x, optimize=True) must equal
np.einsum(expr, x, optimize=False); an optimization flag cannot change the
result. Violation: optimize=True returns [18,18,18] while optimize=False
raises ValueError on the same call -> the two evaluation paths disagree.
"""
import numpy as np


def reproduce():
    x = np.array([[[1, 2, 3], [1, 2, 3], [1, 2, 3]],
                  [[1, 2, 3], [1, 2, 3], [1, 2, 3]],
                  [[1, 2, 3], [1, 2, 3], [1, 2, 3]]])
    expr = "i...->i"

    try:
        opt_true = np.einsum(expr, x, optimize=True)
        opt_true_repr = repr(opt_true.tolist())
    except Exception as e:  # pragma: no cover - not the reproduced branch
        opt_true_repr = f"RAISED {type(e).__name__}"

    try:
        opt_false = np.einsum(expr, x, optimize=False)
        opt_false_repr = repr(opt_false.tolist())
        paths_disagree = not np.array_equal(opt_true, opt_false)
    except Exception as e:
        opt_false_repr = f"RAISED {type(e).__name__}"
        paths_disagree = True  # one path errors, the other returns a value

    return {
        "id": "RMD-NUMPY-0002",
        "project": "numpy",
        "version": np.__version__,
        "mr_family": "optimization-equivalence (optimize flag invariance)",
        "source": f"np.einsum('{expr}', x, optimize=True)",
        "transformed": f"np.einsum('{expr}', x, optimize=False)",
        "expected": "identical result for optimize True/False",
        "observed": f"optimize=True={opt_true_repr}; optimize=False={opt_false_repr}",
        "reproduced": bool(paths_disagree),
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    print(json.dumps(reproduce(), indent=2))
