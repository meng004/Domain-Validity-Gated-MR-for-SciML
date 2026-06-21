#!/usr/bin/env bash
set -uo pipefail
echo "=== uname ==="; uname -a
echo "=== python3 ==="; python3 --version; which python3
echo "=== venv module ==="; python3 -c 'import venv; print("venv ok")' 2>&1 || echo "venv MISSING"
echo "=== pip ==="; python3 -m pip --version 2>&1 || echo "pip MISSING"
echo "=== nvidia-smi (CUDA passthrough) ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv 2>&1 | head -3 || echo "nvidia-smi MISSING"
echo "=== repo mount ==="; ls /mnt/d/Codes/Domain-Validity-Gated-MR-for-SciML/CLAUDE.md 2>&1
echo "=== home ==="; echo "$HOME"; df -h "$HOME" 2>&1 | tail -1
