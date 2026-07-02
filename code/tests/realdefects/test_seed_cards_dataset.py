"""Guard: the committed Real-MRDefect seed dataset must satisfy the schema,
the validator (evidence + MR-oracle + status + domain cap), and seed-pilot
coverage properties. A dataset edit that breaks these means a card outran its
evidence -- fix the card, never weaken this guard.
"""
import json
import os

import schema
import validator

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
_DATASET = os.path.join(_ROOT, "data", "realdefects", "seed_cards.json")


def _load():
    with open(_DATASET, encoding="utf-8") as fh:
        return json.load(fh)["cards"]


def test_dataset_exists_and_parses():
    cards = _load()
    assert isinstance(cards, list) and cards


def test_dataset_validates_clean():
    cards = _load()
    errs = validator.validate_cardset(cards)
    assert errs == [], errs


def test_seed_count_is_meaningful():
    cards = _load()
    # A seed pilot: aim for ~10 high-quality cards, not volume padding.
    assert 8 <= len(cards) <= 12, len(cards)


def test_every_card_has_verified_issue_url():
    cards = _load()
    for c in cards:
        assert c["url"].startswith("https://github.com/"), c["id"]


def test_domain_cap_respected():
    cards = _load()
    dl = [c for c in cards
          if c["project"].lower() in schema.DL_TENSOR_PROJECTS]
    assert len(dl) / len(cards) <= schema.DL_TENSOR_CAP_FRACTION + 1e-9


def test_spans_multiple_mr_families():
    cards = _load()
    families = {c["mr_family"] for c in cards}
    assert len(families) >= 5, families


def test_all_ids_unique():
    cards = _load()
    ids = [c["id"] for c in cards]
    assert len(ids) == len(set(ids))


def test_seed_cards_are_candidate_until_reproduced():
    # Honesty gate: nothing is reproducible/verified without a repro artifact.
    cards = _load()
    for c in cards:
        if c["status"] in ("reproducible", "verified"):
            assert c["repro_artifact"].strip(), (
                f"{c['id']} claims {c['status']} without a repro artifact")
