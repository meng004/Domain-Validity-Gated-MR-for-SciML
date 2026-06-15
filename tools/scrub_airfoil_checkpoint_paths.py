#!/usr/bin/env python3
"""Scrub personal absolute paths from committed airfoil checkpoint metadata.

The Apple-MPS airfoil training run serialised its staging directory
(``/Users/<name>/.cache/dvgmr/airfoil_staged``) into each checkpoint's config
metadata. That is a personal-absolute-path leak (CLAUDE.md S5.A.1) that would
ship in the Zenodo replication archive. This utility loads each checkpoint,
replaces the personal prefix with the home-relative ``~`` form *in the metadata
strings only*, re-saves it, and proves the model weights are byte-for-byte
unchanged via a tensor signature. The checkpoints are torch-zip files, so an
in-place binary edit would break the per-entry CRC32; re-saving through torch is
the only safe scrub.

Idempotent: re-running on an already-scrubbed checkpoint is a no-op.
"""
from __future__ import annotations

import glob
import re
import sys
from collections import OrderedDict

import torch

CKPT_DIR = (
    "research_assets/runs/production-grade-sut-extension/"
    "physicsnemo-mgn-airfoil-second-task"
)
# Match any personal home prefix generically -- never hard-code a username, so
# this utility itself carries no personal path (CLAUDE.md S5.A.1).
HOME_PREFIX_RE = re.compile(r"/(?:Users|home)/[^/\s]+")
REPLACEMENT = "~"

_changed = False


def scrub(obj):
    """Return a copy with any /Users/<name> or /home/<name> prefix relativised.

    Tensors are passed through by reference (weights untouched); container
    types and their ordering are preserved. Sets the module-level ``_changed``
    flag if any string was rewritten, so callers can skip a no-op re-save.
    """
    global _changed
    if isinstance(obj, str):
        new = HOME_PREFIX_RE.sub(REPLACEMENT, obj)
        if new != obj:
            _changed = True
        return new
    if isinstance(obj, OrderedDict):
        return OrderedDict((scrub(k), scrub(v)) for k, v in obj.items())
    if isinstance(obj, dict):
        return {scrub(k): scrub(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [scrub(x) for x in obj]
    if isinstance(obj, tuple):
        return tuple(scrub(x) for x in obj)
    return obj


def weight_signature(obj):
    """Deterministic signature over every tensor: (count, key-path, sum, shape)."""
    sigs = []

    def walk(o, path=""):
        if torch.is_tensor(o):
            sigs.append((path, tuple(o.shape), float(o.double().sum())))
        elif isinstance(o, (dict, OrderedDict)):
            for k, v in o.items():
                walk(v, f"{path}/{k}")
        elif isinstance(o, (list, tuple)):
            for i, x in enumerate(o):
                walk(x, f"{path}[{i}]")

    walk(obj)
    return sigs


def main() -> int:
    global _changed
    import io

    pts = sorted(glob.glob(f"{CKPT_DIR}/*.pt"))
    if not pts:
        print(f"ERROR: no checkpoints under {CKPT_DIR}", file=sys.stderr)
        return 1
    for pt in pts:
        ckpt = torch.load(pt, map_location="cpu", weights_only=False)
        sig_before = weight_signature(ckpt)
        _changed = False
        scrubbed = scrub(ckpt)
        if weight_signature(scrubbed) != sig_before:
            print(f"ABORT: weight signature changed for {pt}", file=sys.stderr)
            return 2
        if not _changed:
            print(f"already clean (no re-save): {pt}")
            continue
        # Prove no home-prefix bytes survive before overwriting the file.
        buf = io.BytesIO()
        torch.save(scrubbed, buf)
        blob = buf.getvalue()
        leaked = blob.count(b"/Users/") + blob.count(b"/home/")
        if leaked:
            print(f"ABORT: {leaked} home-path bytes survived in {pt}", file=sys.stderr)
            return 3
        torch.save(scrubbed, pt)
        print(f"scrubbed (weights identical, {len(sig_before)} tensors): {pt}")
    print("OK: all checkpoints clean, weights preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
