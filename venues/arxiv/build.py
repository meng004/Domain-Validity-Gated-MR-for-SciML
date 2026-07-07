#!/usr/bin/env python3
"""Build the arXiv release package from the canonical repository source."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_release_packages import build_arxiv  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="20260705")
    args = parser.parse_args()
    zip_path, tar_path = build_arxiv(args.label)
    print(f"arxiv_zip={zip_path.relative_to(ROOT)}")
    print(f"arxiv_tar={tar_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
