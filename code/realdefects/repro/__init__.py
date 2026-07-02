"""Registry of local reproductions for OPEN Real-MRDefect cards.

Each entry maps a card id to a reproduce() callable that runs the MR oracle on
the currently installed library version and returns a result dict with
reproduced=True iff the documented MR violation is present.
"""
from . import (rmd_networkx_0001, rmd_numpy_0002, rmd_pandas_0001,
               rmd_scipy_0001)

REGISTRY = {
    "RMD-NUMPY-0002": rmd_numpy_0002.reproduce,
    "RMD-SCIPY-0001": rmd_scipy_0001.reproduce,
    "RMD-PANDAS-0001": rmd_pandas_0001.reproduce,
    "RMD-NETWORKX-0001": rmd_networkx_0001.reproduce,
}
