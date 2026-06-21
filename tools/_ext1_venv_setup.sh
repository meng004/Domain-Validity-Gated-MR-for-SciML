#!/usr/bin/env bash
set -euo pipefail
VENV="$HOME/ext1-venv"
echo "=== creating venv at $VENV ==="
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV" || { echo "VENV CREATE FAILED (need python3-venv apt pkg?)"; exit 3; }
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
echo "=== bootstrapping pip ==="
python -m ensurepip --upgrade 2>&1 | tail -2 || true
python -m pip install --upgrade pip 2>&1 | tail -3
echo "=== versions ==="
python --version
python -m pip --version
echo "=== probe available torch 2.12 cuda builds ==="
python -m pip index versions torch 2>&1 | head -5 || echo "(index versions unsupported; will resolve at install)"
