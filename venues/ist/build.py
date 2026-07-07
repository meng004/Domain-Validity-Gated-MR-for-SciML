#!/usr/bin/env python3
"""Build the legacy IST mirror from the canonical repository source."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_release_packages import build_ist_submission  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="20260705")
    args = parser.parse_args()
    stage = build_ist_submission(args.label)
    print(f"ist_stage={stage.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
