"""TDD for the seed-pilot power / go-no-go module.

The Real-MRDefect-10 seed can only support go/no-go and design calibration,
NOT a final statistical claim that SMS beats MS. This module makes that honesty
computable: exact-binomial (McNemar sign test) power for a small number of
discordant defects, Wilson CIs, and the minimum discordant n for a target power.
"""
import math

import power


# ---- Wilson CI ---------------------------------------------------------------

def test_wilson_ci_all_success_lower_below_one():
    lo, hi = power.wilson_ci(9, 9)
    assert 0.6 < lo < 1.0
    assert abs(hi - 1.0) < 1e-6 or hi <= 1.0
    assert lo < hi


def test_wilson_ci_half():
    lo, hi = power.wilson_ci(5, 10)
    assert lo < 0.5 < hi
    assert 0.0 <= lo and hi <= 1.0


def test_wilson_ci_rejects_bad_args():
    import pytest
    with pytest.raises(ValueError):
        power.wilson_ci(11, 10)
    with pytest.raises(ValueError):
        power.wilson_ci(-1, 10)


# ---- exact binomial sign-test power -----------------------------------------

def test_sign_test_power_large_effect_moderate():
    # n=9 discordant, one-sided alpha=0.05, p_favor=0.9 -> power ~0.77
    pw = power.sign_test_power(9, p_favor=0.9, alpha=0.05)
    assert 0.70 < pw < 0.85, pw


def test_sign_test_power_small_effect_is_low():
    # n=9, p_favor=0.6 -> severely underpowered (<0.3)
    pw = power.sign_test_power(9, p_favor=0.6, alpha=0.05)
    assert pw < 0.30, pw


def test_sign_test_power_monotone_in_n():
    a = power.sign_test_power(9, p_favor=0.8, alpha=0.05)
    b = power.sign_test_power(20, p_favor=0.8, alpha=0.05)
    assert b > a


def test_min_discordant_for_power():
    # smallest discordant n to reach 0.8 power at p_favor=0.9, alpha=0.05
    n = power.min_discordant_for_power(p_favor=0.9, target_power=0.8, alpha=0.05)
    # discreteness of the exact sign test makes the boundary the real check
    # (n=8 beats n=9 here); assert the boundary property, not a guessed value.
    assert isinstance(n, int) and n >= 1
    assert power.sign_test_power(n, p_favor=0.9, alpha=0.05) >= 0.8
    assert power.sign_test_power(n - 1, p_favor=0.9, alpha=0.05) < 0.8


# ---- go / no-go framing ------------------------------------------------------

def test_go_no_go_seed_is_underpowered_label():
    verdict = power.go_no_go(n_defects=9, n_discordant=4,
                             p_favor=0.9, alpha=0.05)
    assert verdict["decision"] in ("design-calibration-only",
                                   "go-signal", "no-go-signal")
    # A seed of 9 with 4 discordant cannot be a confirmatory result.
    assert verdict["confirmatory"] is False
    assert "underpowered" in verdict["note"].lower()
