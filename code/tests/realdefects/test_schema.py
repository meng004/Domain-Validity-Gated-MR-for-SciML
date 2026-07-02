"""TDD for the Real-MRDefect-10 defect-card schema and validator.

Fields required per seed-pilot plan (docs/superpowers/plans/2026-07-01-...md):
  project, url, affected_version, fixed_version_or_commit, behavioral_symptom,
  mr_family, source_input_x, transformed_input_Tx, expected_relation_R,
  violating_observation, why_not_crash_only, reproduction_cost,
  sms_vs_ms_hypothesis, status in {candidate, reproducible, verified}.

The validator must NOT relax the candidate/reproducible/verified bar and must
reject non-MR-detectable entries (missing MR oracle) and crash-only entries.
"""
import copy

import pytest

import schema
import validator


def _minimal_candidate():
    """A minimal VALID candidate card (URL + symptom + full MR oracle)."""
    return {
        "id": "RMD-NUMPY-0001",
        "project": "numpy",
        "url": "https://github.com/numpy/numpy/issues/12345",
        "affected_version": "1.20.0",
        "fixed_version_or_commit": "",
        "behavioral_symptom": "sum along axis disagrees with add.reduce for float32",
        "mr_family": "numerical-equivalence",
        "source_input_x": "x = float32 array, axis=0",
        "transformed_input_Tx": "T(x) = same array, reduce via add.reduce",
        "expected_relation_R": "np.sum(x, axis=0) == np.add.reduce(x, axis=0)",
        "violating_observation": "results differ beyond float32 tolerance",
        "why_not_crash_only": "no exception; wrong numeric value violates equivalence MR",
        "reproduction_cost": "low (pip, CPU, seconds)",
        "sms_vs_ms_hypothesis": "SMS catches this; MS's syntactic mutants miss the axis interaction",
        "status": "candidate",
        "repro_artifact": "",
    }


# ---- schema surface ----------------------------------------------------------

def test_required_fields_constant_matches_plan():
    for f in [
        "project", "url", "affected_version", "fixed_version_or_commit",
        "behavioral_symptom", "mr_family", "source_input_x", "transformed_input_Tx",
        "expected_relation_R", "violating_observation", "why_not_crash_only",
        "reproduction_cost", "sms_vs_ms_hypothesis", "status",
    ]:
        assert f in schema.REQUIRED_FIELDS


def test_status_values_are_exactly_three():
    assert set(schema.STATUS_VALUES) == {"candidate", "reproducible", "verified"}


def test_mr_oracle_fields_defined():
    for f in ["source_input_x", "transformed_input_Tx",
              "expected_relation_R", "violating_observation"]:
        assert f in schema.MR_ORACLE_FIELDS


def test_dl_tensor_projects_defined():
    # DL/tensor cap population must include exactly these four.
    assert set(schema.DL_TENSOR_PROJECTS) == {
        "tensorflow", "pytorch", "tvm", "opencv"}


# ---- validator: happy path ---------------------------------------------------

def test_minimal_candidate_is_valid():
    errs = validator.validate_card(_minimal_candidate())
    assert errs == [], errs


# ---- validator: evidence completeness ---------------------------------------

def test_missing_required_field_is_error():
    card = _minimal_candidate()
    del card["url"]
    errs = validator.validate_card(card)
    assert any("url" in e for e in errs)


def test_empty_required_field_is_error():
    card = _minimal_candidate()
    card["behavioral_symptom"] = "   "
    errs = validator.validate_card(card)
    assert any("behavioral_symptom" in e for e in errs)


def test_bad_status_is_error():
    card = _minimal_candidate()
    card["status"] = "confirmed"
    errs = validator.validate_card(card)
    assert any("status" in e for e in errs)


# ---- validator: MR-oracle completeness (reject non-MR-detectable) -----------

def test_missing_mr_oracle_component_is_error():
    card = _minimal_candidate()
    card["expected_relation_R"] = ""
    errs = validator.validate_card(card)
    assert any("expected_relation_R" in e for e in errs)


def test_crash_only_symptom_is_rejected():
    card = _minimal_candidate()
    card["why_not_crash_only"] = "it just crashes with a segfault"
    card["violating_observation"] = "segfault / raises RuntimeError"
    errs = validator.validate_card(card)
    assert any("crash-only" in e.lower() for e in errs)


# ---- validator: status-transition rules (do NOT relax the bar) --------------

def test_reproducible_requires_repro_artifact():
    card = _minimal_candidate()
    card["status"] = "reproducible"
    card["repro_artifact"] = ""  # no repro evidence
    errs = validator.validate_card(card)
    assert any("reproducible" in e.lower() and "repro" in e.lower() for e in errs)


def test_reproducible_with_artifact_ok():
    card = _minimal_candidate()
    card["status"] = "reproducible"
    card["repro_artifact"] = "code/realdefects/repro/rmd_numpy_0001.py"
    errs = validator.validate_card(card)
    assert errs == [], errs


def test_verified_requires_affected_and_fixed_and_repro():
    card = _minimal_candidate()
    card["status"] = "verified"
    card["repro_artifact"] = "code/realdefects/repro/rmd_numpy_0001.py"
    card["fixed_version_or_commit"] = ""  # missing fix point
    errs = validator.validate_card(card)
    assert any("verified" in e.lower() for e in errs)


def test_verified_full_chain_ok():
    card = _minimal_candidate()
    card["status"] = "verified"
    card["fixed_version_or_commit"] = "1.20.3 (commit abc123)"
    card["repro_artifact"] = "code/realdefects/repro/rmd_numpy_0001.py"
    errs = validator.validate_card(card)
    assert errs == [], errs


# ---- validator: domain cap (DL/tensor <= 40% of a card set) -----------------

def test_domain_cap_flags_over_40pct_dl_tensor():
    cards = []
    for i in range(3):
        c = _minimal_candidate()
        c["id"] = f"RMD-PT-{i}"
        c["project"] = "pytorch"
        cards.append(c)
    for i in range(2):
        c = _minimal_candidate()
        c["id"] = f"RMD-NP-{i}"
        c["project"] = "numpy"
        cards.append(c)
    # 3/5 = 60% DL/tensor > 40% cap
    errs = validator.validate_cardset(cards)
    assert any("cap" in e.lower() for e in errs)


def test_domain_cap_ok_at_40pct():
    cards = []
    for i in range(2):
        c = _minimal_candidate()
        c["id"] = f"RMD-PT-{i}"
        c["project"] = "pytorch"
        cards.append(c)
    for i in range(3):
        c = _minimal_candidate()
        c["id"] = f"RMD-NP-{i}"
        c["project"] = "numpy"
        cards.append(c)
    # 2/5 = 40% == cap, allowed
    errs = validator.validate_cardset(cards)
    assert not any("cap" in e.lower() for e in errs), errs


def test_cardset_flags_duplicate_ids():
    a = _minimal_candidate()
    b = copy.deepcopy(_minimal_candidate())  # same id
    errs = validator.validate_cardset([a, b])
    assert any("duplicate" in e.lower() for e in errs)
