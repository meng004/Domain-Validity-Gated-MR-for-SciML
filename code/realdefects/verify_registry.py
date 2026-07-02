"""Registry of VERIFIED Real-MRDefect cards.

Each entry maps a verified card id to a callable returning:
  fixed_confirmed   -- live check that the fix holds on the current version;
  current_version   -- the version the fix was confirmed on;
  affected_evidence -- recorded provenance of the reproduced violation on the
                       affected version (see the repro module's AFFECTED_EVIDENCE).
"""
from repro import rmd_xarray_0001


def _verify_xarray_0001():
    cur = rmd_xarray_0001.check_current()
    aff = rmd_xarray_0001.AFFECTED_EVIDENCE
    return {
        "id": "RMD-XARRAY-0001",
        "fixed_confirmed": bool(cur["correspondence_correct"]),
        "current_version": cur["version"],
        "affected_evidence": aff,
    }


VERIFY_REGISTRY = {
    "RMD-XARRAY-0001": _verify_xarray_0001,
}
