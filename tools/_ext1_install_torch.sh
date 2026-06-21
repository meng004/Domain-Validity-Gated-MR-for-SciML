#!/usr/bin/env bash
set -euo pipefail
source "$HOME/ext1-venv/bin/activate"
echo "=== installing torch==2.12.* (CUDA build from PyPI default Linux wheel) ==="
python -m pip install "torch==2.12.*" 2>&1 | tail -8
echo "=== torch cuda probe ==="
python - <<'PY'
import torch
print("torch", torch.__version__)
print("torch.version.cuda", torch.version.cuda)
print("cuda.is_available", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device", torch.cuda.get_device_name(0))
    x = torch.randn(1024, 1024, device="cuda")
    print("matmul ok", float((x@x).sum()) is not None)
PY
