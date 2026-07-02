"""TDD for VERIFIED Real-MRDefect cards (full affected->fixed evidence chain).

A card is 'verified' only when: the MR violation was reproduced on the affected
version AND the fix was confirmed on a fixed version, with a repro artifact and
a full MR oracle. For a CLOSED defect whose fix ships in the currently installed
library, the artifact does a LIVE fix confirmation on the current version and
records the affected-version evidence as provenance (old wheels are not
CI-re-runnable on Python 3.12 -- documented, not hidden).
"""
import json
import os

import verify_registry

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
_DATASET = os.path.join(_ROOT, "data", "realdefects", "seed_cards.json")

EXPECTED_VERIFIED_IDS = {"RMD-XARRAY-0001"}


def _cards():
    with open(_DATASET, encoding="utf-8") as fh:
        return json.load(fh)["cards"]


def test_registry_covers_expected_verified_defects():
    assert EXPECTED_VERIFIED_IDS <= set(verify_registry.VERIFY_REGISTRY)


def test_dataset_marks_expected_cards_verified():
    verified = {c["id"] for c in _cards() if c["status"] == "verified"}
    assert EXPECTED_VERIFIED_IDS <= verified


def test_live_fix_confirmation_on_current_version():
    for cid in sorted(EXPECTED_VERIFIED_IDS):
        res = verify_registry.VERIFY_REGISTRY[cid]()
        assert res["fixed_confirmed"] is True, res
        assert res["current_version"], "must record the version fix confirmed on"
        # provenance of the reproduced violation on the affected version
        aff = res["affected_evidence"]
        assert aff["reproduced"] is True, aff
        assert aff["version"], "affected evidence must name the affected version"


def test_verified_cards_have_full_chain_fields():
    for c in _cards():
        if c["status"] != "verified":
            continue
        assert c["affected_version"].strip()
        assert c["fixed_version_or_commit"].strip()
        assert c["repro_artifact"].strip()
        assert os.path.exists(os.path.join(_ROOT, c["repro_artifact"]))
        assert c["id"] in verify_registry.VERIFY_REGISTRY
