"""TDD for local reproduction of the OPEN Real-MRDefect cards.

Each OPEN defect (numpy #30349, scipy #21876, pandas #59350) still exists on
the installed library version, so its MR violation can be reproduced WITHOUT
downgrading. A card may only be status='reproducible' if its repro_artifact
runs and returns reproduced=True here. This is the evidence that promotes
candidate -> reproducible; it must not be weakened.
"""
import json
import os

import pytest

import repro

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
_DATASET = os.path.join(_ROOT, "data", "realdefects", "seed_cards.json")

EXPECTED_REPRO_IDS = {"RMD-NUMPY-0002", "RMD-SCIPY-0001", "RMD-PANDAS-0001",
                      "RMD-NETWORKX-0001"}


def _cards():
    with open(_DATASET, encoding="utf-8") as fh:
        return json.load(fh)["cards"]


def test_registry_covers_expected_open_defects():
    assert EXPECTED_REPRO_IDS <= set(repro.REGISTRY)


@pytest.mark.parametrize("cid", sorted(EXPECTED_REPRO_IDS))
def test_each_open_defect_reproduces_now(cid):
    result = repro.REGISTRY[cid]()
    assert result["id"] == cid
    assert result["reproduced"] is True, result
    assert result["version"], "must record the library version reproduced on"
    assert result["mr_family"]
    # the oracle must carry a concrete observed-vs-expected contrast
    assert result["expected"] and result["observed"]


def test_reproduced_cards_point_to_runnable_artifact():
    """Every dataset card marked 'reproducible' must have a repro_artifact
    file that exists and whose reproduce() returns reproduced=True."""
    for c in _cards():
        if c["status"] != "reproducible":
            continue
        art = c["repro_artifact"].strip()
        assert art, f"{c['id']} reproducible but no repro_artifact"
        assert os.path.exists(os.path.join(_ROOT, art)), (
            f"{c['id']} repro_artifact missing on disk: {art}")
        assert c["id"] in repro.REGISTRY, f"{c['id']} not in repro registry"
        assert repro.REGISTRY[c["id"]]()["reproduced"] is True


def test_no_reproducible_card_without_registry_backing():
    reproducible = {c["id"] for c in _cards()
                    if c["status"] == "reproducible"}
    # honesty: a 'reproducible' claim requires a registered, passing repro
    assert reproducible <= set(repro.REGISTRY)
