#!/usr/bin/env bash
set -uo pipefail
export http_proxy="http://127.0.0.1:7897" https_proxy="http://127.0.0.1:7897" no_proxy="localhost,127.0.0.1"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
source "$HOME/ext1-venv/bin/activate"
cd /mnt/d/Codes/Domain-Validity-Gated-MR-for-SciML
python tools/_ext1_sweep.py
