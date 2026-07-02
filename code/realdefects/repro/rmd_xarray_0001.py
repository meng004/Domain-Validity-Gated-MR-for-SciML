"""RMD-XARRAY-0001 (xarray groupby_bins label correspondence, issue #7766).

MR / oracle: groupby_bins assigns bins with pandas.cut, so the count of elements
in group[label] must equal the pandas.cut count for that label. On the affected
version the label->bin correspondence is scrambled (sorted by label NAME instead
of bin edge); on the fixed version it is correct.

This is a CLOSED defect whose fix ships in the currently installed xarray, so
check_current() performs a LIVE fix confirmation on the current version. The
affected-version violation was reproduced in an isolated venv (xarray 2023.4.0,
numpy 1.26.4, pandas 2.1.4) and is recorded below as provenance -- old wheels do
not build on Python 3.12, so that side is documented, not CI-re-runnable.
"""
import numpy as np
import pandas as pd
import xarray as xr

# Provenance: actual observed result on the AFFECTED version (isolated venv).
# xarray 2023.4.0 / numpy 1.26.4 / pandas 2.1.4 -> correspondence WRONG.
AFFECTED_EVIDENCE = {
    "version": "xarray 2023.4.0 (numpy 1.26.4, pandas 2.1.4, isolated venv)",
    "correspondence_correct": False,
    "reproduced": True,
    "mismatches": {
        "four": {"expected": 1, "got": 506},
        "five": {"expected": 2, "got": 27},
        "six": {"expected": 9, "got": 153},
        "seven": {"expected": 27, "got": 9},
        "eight": {"expected": 153, "got": 2},
        "nine": {"expected": 506, "got": 1},
    },
}


def check_current():
    """Run the label-correspondence oracle on the currently installed xarray."""
    rng = np.random.RandomState(42)
    coords = rng.normal(5, 5, 1000)
    bins = np.logspace(-4, 1, 10)
    labels = ["one", "two", "three", "four", "five", "six",
              "seven", "eight", "nine"]

    darr = xr.DataArray(coords, coords=[coords], dims=["coords"])
    groups = darr.groupby_bins("coords", bins, labels=labels).groups
    truth = pd.cut(coords, bins, labels=labels).value_counts()

    mism = {}
    for lab in labels:
        expected = int(truth.get(lab, 0))
        got = len(groups.get(lab, []))
        if expected != got:
            mism[lab] = {"expected": expected, "got": got}

    return {
        "version": xr.__version__,
        "correspondence_correct": not mism,
        "mismatches": mism,
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    print(json.dumps({"current": check_current(),
                      "affected": AFFECTED_EVIDENCE}, indent=2))
