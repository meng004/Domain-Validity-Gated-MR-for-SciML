"""Non-parametric effect-size and significance tests for the K=6 roster.

Reviewer #1 (empirical SE methodology) asked for Cliff's delta and a
non-parametric test alongside the bootstrap / Wilson CIs. This module computes,
with no third-party dependency (no scipy):

  - Cliff's delta: a rank-based effect size in [-1, 1]; |delta| >= 0.474 is
    "large" (Romano et al. 2006). delta = 1 means complete dominance (every
    value in group A exceeds every value in group B).
  - Exact Wilcoxon signed-rank test for paired samples, computed by full
    enumeration of the 2^n sign assignments (valid and exact for the small
    n the roster provides; n=6 gives a minimum two-sided p of 2/2^6 = 0.03125).

The headline comparison is the per-checkpoint mirror-y OOD-stress violation
against the per-checkpoint one-step rollout accuracy across all six checkpoints:
it tests whether the relation-level violation is separated from in-distribution
predictive error, which is what makes the mirror-y finding more than a
restatement of accuracy.

Input:  research_assets/runs/multicheckpoint/e1_aggregate.json
Output: research_assets/runs/multicheckpoint/effect_size_report.json
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "research_assets" / "runs" / "multicheckpoint" / "e1_aggregate.json"
OUT = ROOT / "research_assets" / "runs" / "multicheckpoint" / "effect_size_report.json"


def six_values(agg: dict, mr: str) -> list[float]:
    a = agg["per_mr_aggregates"][mr]
    return [float(v) for v in a["seed_family_values"]] + [
        float(a["S4_value"]), float(a["S5_value"])]


def cliffs_delta(a: list[float], b: list[float]) -> dict:
    gt = sum(1 for x in a for y in b if x > y)
    lt = sum(1 for x in a for y in b if x < y)
    n = len(a) * len(b)
    delta = (gt - lt) / n if n else float("nan")
    mag = abs(delta)
    label = ("negligible" if mag < 0.147 else "small" if mag < 0.33
             else "medium" if mag < 0.474 else "large")
    return {"delta": delta, "magnitude": label, "gt_pairs": gt, "lt_pairs": lt,
            "total_pairs": n}


def wilcoxon_signed_rank_exact(x: list[float], y: list[float]) -> dict:
    """Exact two-sided Wilcoxon signed-rank test by sign enumeration.

    Differences d_i = x_i - y_i; zeros dropped. Ranks of |d|; W+ is the sum of
    ranks of positive differences. The exact null distribution enumerates all
    2^n sign assignments of those ranks. Returns the observed W+ and the
    two-sided p-value.
    """
    diffs = [xi - yi for xi, yi in zip(x, y) if xi != yi]
    n = len(diffs)
    if n == 0:
        return {"n": 0, "W_plus": float("nan"), "p_two_sided": float("nan")}
    order = sorted(range(n), key=lambda i: abs(diffs[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(diffs[order[j + 1]]) == abs(diffs[order[i]]):
            j += 1
        avg = (i + 1 + j + 1) / 2.0  # average rank for ties (1-based)
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    w_plus = sum(r for d, r in zip(diffs, ranks) if d > 0)
    # exact null: each rank gets +/- sign with equal probability
    total = 2 ** n
    count_ge = 0
    count_le = 0
    for signs in itertools.product([0, 1], repeat=n):
        s = sum(r for r, sg in zip(ranks, signs) if sg)
        if s >= w_plus:
            count_ge += 1
        if s <= w_plus:
            count_le += 1
    p_two = min(1.0, 2.0 * min(count_ge, count_le) / total)
    return {"n": n, "W_plus": w_plus, "p_two_sided": p_two,
            "exact_min_two_sided_p": 2.0 / total}


def compare(agg: dict, mr_a: str, mr_b: str) -> dict:
    a = six_values(agg, mr_a)
    b = six_values(agg, mr_b)
    return {
        "group_a": mr_a, "group_b": mr_b,
        "a_values": a, "b_values": b,
        "cliffs_delta": cliffs_delta(a, b),
        "wilcoxon_signed_rank": wilcoxon_signed_rank_exact(a, b),
    }


def main() -> int:
    agg = json.loads(AGG.read_text())
    report = {
        "record_type": "effect-size-and-nonparametric-tests",
        "roster_size": 6,
        "note": ("Paired per-checkpoint comparisons across the K=6 roster "
                 "(S0-S3 seed family + S4 wider + S5 deeper). Wilcoxon is exact "
                 "by enumeration; at n=6 the minimum attainable two-sided p is "
                 "0.03125."),
        "comparisons": {
            "mirror_ood_vs_rollout": compare(agg, "mirror_ood", "rollout"),
            "mirror_sym_vs_conservation": compare(agg, "mirror_sym", "conservation"),
        },
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for name, c in report["comparisons"].items():
        cd = c["cliffs_delta"]; w = c["wilcoxon_signed_rank"]
        print(f"{name}: Cliff's delta={cd['delta']:+.3f} ({cd['magnitude']}); "
              f"Wilcoxon W+={w['W_plus']:.1f}, p2={w['p_two_sided']:.4f} (n={w['n']})")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
