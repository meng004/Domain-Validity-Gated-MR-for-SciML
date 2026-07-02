"""Reproduce RMD-PANDAS-0001 (pandas groupby+resample row-order, issue #59350).

MR (row/index-order invariance): grouping and resampling use column keys
('group' and the 'datetime' column via on=), so the aggregated result must be
invariant to the row index order. With an out-of-order index [1, 0] the summed
values come out swapped versus the reset_index (canonical) computation.
"""
import pandas as pd


def _agg(df):
    return list(
        df.groupby("group")
          .resample("1min", on="datetime")
          .aggregate({"value": "sum"})["value"]
    )


def reproduce():
    df = pd.DataFrame(
        dict(
            datetime=[pd.to_datetime("2024-07-30T00:00Z"),
                      pd.to_datetime("2024-07-30T00:01Z")],
            group=["A", "A"],
            value=[100, 200],
        ),
        index=[1, 0],  # out-of-order index
    )
    out_of_order = _agg(df)
    canonical = _agg(df.reset_index(drop=True))  # index-order removed
    violated = out_of_order != canonical

    return {
        "id": "RMD-PANDAS-0001",
        "project": "pandas",
        "version": pd.__version__,
        "mr_family": "row-order invariance (dataframe-algebra / permutation)",
        "source": "groupby('group').resample('1min', on='datetime').sum() on canonical index",
        "transformed": "same aggregation with out-of-order index [1, 0]",
        "expected": f"index-order-invariant result {canonical}",
        "observed": f"out-of-order index gives {out_of_order}",
        "reproduced": bool(violated),
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    print(json.dumps(reproduce(), indent=2))
