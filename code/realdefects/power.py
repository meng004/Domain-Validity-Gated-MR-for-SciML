"""Seed-pilot power / go-no-go for SMS-vs-MS discrimination.

Design: to ask whether SMS ranks MR suites more like true-defect detection than
MS does, the cleanest small-n statistic is a McNemar sign test over *discordant*
defects -- defects where exactly one of {SMS-favoring, MS-favoring} outcome
holds. With ~10 seed defects the discordant count is tiny, so only very large
effects are detectable. This module makes that limitation explicit and refuses
to dress a seed up as a confirmatory result.

Pure-Python (math only): no scipy dependency, so it runs in the light CI.
"""
import math


def wilson_ci(k, n, z=1.96):
    """Wilson score 95% CI for a binomial proportion k/n."""
    if n <= 0:
        raise ValueError("n must be positive")
    if k < 0 or k > n:
        raise ValueError("require 0 <= k <= n")
    phat = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (phat + z2 / (2 * n)) / denom
    half = (z * math.sqrt(phat * (1 - phat) / n + z2 / (4 * n * n))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def _binom_sf_ge(c, n, p):
    """P(X >= c) for X ~ Binomial(n, p), exact."""
    if c <= 0:
        return 1.0
    if c > n:
        return 0.0
    return sum(math.comb(n, k) * p**k * (1 - p)**(n - k)
               for k in range(c, n + 1))


def _critical_count(n, alpha):
    """Smallest c such that P(X >= c | p=0.5) <= alpha (one-sided sign test)."""
    for c in range(0, n + 1):
        if _binom_sf_ge(c, n, 0.5) <= alpha:
            return c
    return n + 1  # unreachable at this n


def sign_test_power(n_discordant, p_favor=0.9, alpha=0.05):
    """Power of a one-sided exact sign test on n_discordant paired defects.

    n_discordant : number of defects where SMS and MS disagree.
    p_favor      : P(a discordant defect favors SMS) under the alternative.
    """
    if n_discordant <= 0:
        return 0.0
    c = _critical_count(n_discordant, alpha)
    return _binom_sf_ge(c, n_discordant, p_favor)


def min_discordant_for_power(p_favor=0.9, target_power=0.8, alpha=0.05,
                             cap=1000):
    """Smallest discordant n reaching target_power at p_favor."""
    for n in range(1, cap + 1):
        if sign_test_power(n, p_favor=p_favor, alpha=alpha) >= target_power:
            return n
    return cap + 1


def go_no_go(n_defects, n_discordant, p_favor=0.9, alpha=0.05,
             confirmatory_power=0.8):
    """Return a go/no-go dict that is honest about seed underpowering.

    A seed is NEVER confirmatory: even in the best case its achievable power is
    reported, and the decision is framed as a design signal, not a proof.
    """
    pw = sign_test_power(n_discordant, p_favor=p_favor, alpha=alpha)
    need = min_discordant_for_power(p_favor=p_favor,
                                    target_power=confirmatory_power,
                                    alpha=alpha)
    lo, hi = wilson_ci(n_discordant, max(n_defects, 1))
    if pw >= confirmatory_power:
        decision = "go-signal"
    elif n_discordant == 0:
        decision = "no-go-signal"
    else:
        decision = "design-calibration-only"
    note = (
        f"seed underpowered: {n_discordant} discordant of {n_defects} defects "
        f"gives sign-test power {pw:.2f} at p_favor={p_favor} (alpha={alpha}); "
        f"~{need} discordant defects needed for {confirmatory_power:.0%} power. "
        f"Wilson 95% CI on discordant fraction: [{lo:.2f}, {hi:.2f}]. "
        f"Use for go/no-go and design calibration only, not a claim that "
        f"SMS beats MS."
    )
    return {
        "decision": decision,
        "confirmatory": False,
        "achieved_power": pw,
        "discordant_needed_for_confirmatory": need,
        "wilson_ci": (lo, hi),
        "note": note,
    }
