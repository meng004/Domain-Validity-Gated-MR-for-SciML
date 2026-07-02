"""TDD for the minimal SMS-vs-MS discrimination proof-of-concept.

Scope (existence proof, NOT a statistical claim): show that there exists a
setting where a metamorphic test suite scores HIGH on synthetic-syntactic
mutants (high MS) yet FAILS to detect a real, reproduced defect, while another
suite scores LOWER MS yet DETECTS the real defect. That is: the MS ranking of
suite quality can run OPPOSITE to real-defect detection (SMS) ranking.

Anchor: the real defect is RMD-PANDAS-0001 (pandas #59350, groupby+resample
index-order invariance), reproduced on pandas 2.2.3 by the repro registry. The
PoC uses a faithful reference implementation of that behavior so that mutation
analysis is tractable (standard real-fault + SUT methodology, cf. Just 2014).

These tests assert RELATIONAL properties only; the concrete MS values are
computed by the harness, not hard-coded.
"""
import sms_vs_ms_poc as poc


def test_real_defect_anchor_is_reproducible():
    # The PoC must be anchored to a card that is actually reproduced, not a
    # candidate -- otherwise "real defect detection" would be unfounded.
    assert poc.ANCHOR_CARD_ID == "RMD-PANDAS-0001"
    import repro
    assert repro.REGISTRY[poc.ANCHOR_CARD_ID]()["reproduced"] is True


def test_reference_impl_matches_correct_semantics_on_sorted_input():
    # On an already-sorted frame the buggy behavior does not manifest, so the
    # reference impl agrees with the correct (canonical) aggregation.
    df = poc.make_frame(shuffle=False)
    assert poc.reference_sum(df) == poc.correct_sum(df)


def test_reference_impl_exhibits_the_real_defect_on_shuffled_input():
    # The reference impl faithfully reproduces #59350: shuffled index changes
    # the aggregated result (index-order invariance violated).
    df = poc.make_frame(shuffle=True)
    assert poc.reference_sum(df) != poc.correct_sum(df)


def test_conservation_mr_kills_many_mutants_but_misses_real_defect():
    r = poc.evaluate()
    cons = r["conservation_suite"]
    # high MS: the sum-conservation MR kills most arithmetic mutants
    assert cons["ms"] >= 0.6, cons
    # but it is BLIND to the real defect (misplacement preserves the total)
    assert cons["detects_real_defect"] is False, cons


def test_orderinv_mr_detects_real_defect_but_low_ms():
    r = poc.evaluate()
    inv = r["order_invariance_suite"]
    # detects the real, reproduced defect
    assert inv["detects_real_defect"] is True, inv
    # yet scores LOWER MS than the conservation suite
    assert inv["ms"] < r["conservation_suite"]["ms"], r


def test_ms_ranking_inverts_real_defect_detection():
    # The headline: MS ranks the conservation suite ABOVE the order-invariance
    # suite, but only the order-invariance suite catches the real defect.
    r = poc.evaluate()
    assert r["ms_ranking_prefers"] == "conservation_suite"
    assert r["real_defect_detected_only_by"] == "order_invariance_suite"
    assert r["ms_contradicts_real_detection"] is True


def test_poc_is_labeled_non_statistical():
    r = poc.evaluate()
    assert r["is_statistical_claim"] is False
    assert "existence" in r["interpretation"].lower()
    assert r["n_real_defects"] == 1
