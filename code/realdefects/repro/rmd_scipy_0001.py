"""Reproduce RMD-SCIPY-0001 (scipy convolve mode-consistency, issue #21876).

MR (cross-mode broadcasting-invariance): for the same broadcast inputs and
axes, the batch/broadcast dimension result.shape[0] must be preserved across
modes. mode='valid'/'full' preserve B=7; mode='same' collapses it to 1.
Note: fftconvolve and oaconvolve AGREE with each other here -- the violated
relation is cross-MODE consistency, not cross-method equivalence.
"""
import numpy as np
from scipy.signal import fftconvolve


def reproduce():
    x = np.arange(100 * 1).reshape((1, 100))
    k = np.arange(10 * 7).reshape((7, 10))

    shapes = {mode: fftconvolve(x, k, axes=1, mode=mode).shape
              for mode in ("valid", "full", "same")}
    batch_dims = {mode: shp[0] for mode, shp in shapes.items()}

    ref_b = batch_dims["valid"]  # expected preserved batch dim (7)
    violated = batch_dims["same"] != ref_b

    import scipy
    return {
        "id": "RMD-SCIPY-0001",
        "project": "scipy",
        "version": scipy.__version__,
        "mr_family": "mode-consistency / broadcasting-invariance",
        "source": "fftconvolve(x(1,100), k(7,10), axes=1, mode='valid')",
        "transformed": "same inputs with mode='same'",
        "expected": f"batch dim preserved across modes (B={ref_b})",
        "observed": f"batch dims by mode: {batch_dims} (shapes {shapes})",
        "reproduced": bool(violated),
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    print(json.dumps(reproduce(), indent=2))
