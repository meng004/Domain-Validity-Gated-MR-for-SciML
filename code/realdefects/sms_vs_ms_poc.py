"""Minimal SMS-vs-MS discrimination proof-of-concept (existence proof).

NOT a statistical claim. With a single real, reproduced defect it shows that
there EXISTS a case where the traditional mutation score (MS, kill rate on
synthetic syntactic mutants) ranks a test suite ABOVE another, while only the
lower-MS suite detects the real defect. I.e. MS ranking can contradict
real-defect (SMS) detection.

Real defect anchor: RMD-PANDAS-0001 (pandas #59350, groupby+resample index-order
invariance), reproduced on pandas 2.2.3 by repro.REGISTRY. The reducer below
faithfully reproduces that misplacement so mutant analysis is tractable
(real-fault + reference-SUT methodology, cf. Just et al. FSE 2014).

SUT semantics: sum `value` per `bucket` over records (idx, bucket, value).
  - correct(): group strictly by bucket (index-order independent).
  - reference(): reproduces #59350 -- output values are ordered by row index,
    not by bucket, so an out-of-order index permutes bucket<->sum (total kept).
"""

ANCHOR_CARD_ID = "RMD-PANDAS-0001"

# Aggregation dataset for mutation analysis (positive values, 2 buckets).
_RECORDS = [(0, "A", 3), (1, "A", 5), (2, "B", 7), (3, "B", 2)]


# ---- SUT: correct vs reference(buggy) ---------------------------------------

def correct(records):
    """Strict group-by-bucket sum; invariant to row/index order."""
    out = {}
    for _idx, b, v in records:
        out[b] = out.get(b, 0) + v
    return out


def reference(records):
    """Faithful model of pandas #59350: labels sorted by bucket, but values
    taken in ascending row-index order, so an out-of-order index misplaces
    (permutes) the per-bucket sums while preserving the total."""
    sums, first_index = {}, {}
    for idx, b, v in records:
        sums[b] = sums.get(b, 0) + v
        first_index.setdefault(b, idx)
    labels = sorted(sums)
    values_in_index_order = [sums[b]
                             for b in sorted(sums, key=lambda b: first_index[b])]
    return dict(zip(labels, values_in_index_order))


# ---- frame helpers used by the frame-level tests ----------------------------

def make_frame(shuffle):
    """Two buckets A(100) and B(200). shuffle=False -> index in bucket order;
    shuffle=True -> out-of-order index [1,0] (the #59350 trigger)."""
    if shuffle:
        return [(1, "A", 100), (0, "B", 200)]
    return [(0, "A", 100), (1, "B", 200)]


def _canonical(d):
    return sorted(d.items())


def reference_sum(frame):
    return _canonical(reference(frame))


def correct_sum(frame):
    return _canonical(correct(frame))


# ---- metamorphic relations (return True iff the relation HOLDS on f) ---------

def _mr_conservation_holds(f):
    out = f(_RECORDS)
    return sum(out.values()) == sum(v for _idx, _b, v in _RECORDS)


def _mr_order_invariance_holds(f):
    # Index-order invariance (the #59350 relation): the result must not depend
    # on the row-index order. Transform T reassigns ascending indices in a
    # DIFFERENT record order (reverse), modelling an out-of-order index over the
    # same data. A correct reducer is invariant; reference() is not.
    def _reindex(records):
        return [(new_idx, b, v)
                for new_idx, (_old, b, v) in enumerate(records)]

    base = f(_reindex(_RECORDS))
    permuted = f(_reindex(list(reversed(_RECORDS))))
    return base == permuted


# ---- synthetic syntactic mutants of the correct reducer ---------------------
# Each is a small syntactic variation of correct(). Order-independent value
# transforms break conservation but not order-invariance; the two order-
# dependent mutants break both; the abs() mutant is equivalent on positive data.

def _mut_plus_one(records):
    out = {}
    for _i, b, v in records:
        out[b] = out.get(b, 0) + (v + 1)
    return out


def _mut_times_two(records):
    out = {}
    for _i, b, v in records:
        out[b] = out.get(b, 0) + (v * 2)
    return out


def _mut_minus_one(records):
    out = {}
    for _i, b, v in records:
        out[b] = out.get(b, 0) + (v - 1)
    return out


def _mut_init_five(records):
    out = {}
    for _i, b, v in records:
        out[b] = out.get(b, 5) + v
    return out


def _mut_square(records):
    out = {}
    for _i, b, v in records:
        out[b] = out.get(b, 0) + (v * v)
    return out


def _mut_max(records):
    out = {}
    for _i, b, v in records:
        out[b] = max(out.get(b, 0), v)
    return out


def _mut_times_three(records):
    out = {}
    for _i, b, v in records:
        out[b] = out.get(b, 0) + (v * 3)
    return out


def _mut_horner(records):  # order-dependent: acc*2 + v
    out = {}
    for _i, b, v in records:
        out[b] = out.get(b, 0) * 2 + v
    return out


def _mut_keep_last(records):  # order-dependent: acc = v (last wins)
    out = {}
    for _i, b, v in records:
        out[b] = v
    return out


def _mut_abs(records):  # equivalent on positive data
    out = {}
    for _i, b, v in records:
        out[b] = out.get(b, 0) + abs(v)
    return out


MUTANTS = {
    "plus_one": _mut_plus_one,
    "times_two": _mut_times_two,
    "minus_one": _mut_minus_one,
    "init_five": _mut_init_five,
    "square": _mut_square,
    "max_not_sum": _mut_max,
    "times_three": _mut_times_three,
    "horner": _mut_horner,
    "keep_last": _mut_keep_last,
    "abs_equivalent": _mut_abs,
}


def _mutation_score(mr_holds):
    """MS = fraction of mutants KILLED (mutant kills = MR violated on mutant),
    among non-equivalent kills; equivalent mutants that no suite can kill still
    count in the denominator (standard MS definition)."""
    killed = sum(1 for f in MUTANTS.values() if not mr_holds(f))
    return killed / len(MUTANTS)


def evaluate():
    cons_ms = _mutation_score(_mr_conservation_holds)
    inv_ms = _mutation_score(_mr_order_invariance_holds)

    # detection of the REAL defect: does the suite's MR fail on reference()?
    cons_detects = not _mr_conservation_holds(reference)
    inv_detects = not _mr_order_invariance_holds(reference)

    ms_prefers = ("conservation_suite" if cons_ms > inv_ms
                  else "order_invariance_suite" if inv_ms > cons_ms
                  else "tie")
    detected_only_by = None
    if inv_detects and not cons_detects:
        detected_only_by = "order_invariance_suite"
    elif cons_detects and not inv_detects:
        detected_only_by = "conservation_suite"

    contradicts = (ms_prefers == "conservation_suite"
                   and detected_only_by == "order_invariance_suite")

    return {
        "anchor_card": ANCHOR_CARD_ID,
        "n_real_defects": 1,
        "is_statistical_claim": False,
        "conservation_suite": {"ms": cons_ms,
                               "detects_real_defect": cons_detects},
        "order_invariance_suite": {"ms": inv_ms,
                                   "detects_real_defect": inv_detects},
        "ms_ranking_prefers": ms_prefers,
        "real_defect_detected_only_by": detected_only_by,
        "ms_contradicts_real_detection": contradicts,
        "interpretation": (
            "Existence proof (n=1 real defect, non-statistical): the "
            "conservation MR scores higher MS yet is blind to the real "
            "misplacement defect, while the lower-MS order-invariance MR "
            "detects it. MS ranking here contradicts real-defect detection. "
            "This motivates -- but does not statistically establish -- that "
            "SMS (real-defect detection) discriminates MR-suite quality "
            "differently from MS."
        ),
    }


if __name__ == "__main__":  # pragma: no cover
    import json
    print(json.dumps(evaluate(), indent=2))
