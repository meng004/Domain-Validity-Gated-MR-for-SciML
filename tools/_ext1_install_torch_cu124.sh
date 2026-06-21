#!/usr/bin/env bash
set -uo pipefail
source "$HOME/ext1-venv/bin/activate"
echo "=== purging cu130 torch + nvidia packages ==="
python -m pip uninstall -y torch triton $(python -m pip list 2>/dev/null | awk '/^nvidia-/{print $1}' | tr '\n' ' ') >/dev/null 2>&1 || true

try_cuda() {
  local tag="$1"
  echo "=== trying torch==2.12.* ${tag} ==="
  if python -m pip install "torch==2.12.*" --index-url "https://download.pytorch.org/whl/${tag}" 2>&1 | tail -3; then
    python - <<PY
import torch
ok = torch.cuda.is_available()
print("BUILD", torch.__version__, "cuda", torch.version.cuda, "avail", ok)
if ok:
    print("DEVICE", torch.cuda.get_device_name(0))
    x=torch.randn(2048,2048,device="cuda"); import math
    print("MATMUL_OK", math.isfinite(float((x@x).sum())))
PY
    return 0
  fi
  return 1
}

for tag in cu124 cu126 cu121 cu123; do
  try_cuda "$tag"
  AVAIL=$(python -c 'import torch;print(torch.cuda.is_available())' 2>/dev/null || echo False)
  if [ "$AVAIL" = "True" ]; then
    echo "=== SUCCESS with ${tag} ==="
    python -c 'import torch;print("FINAL", torch.__version__, torch.version.cuda)'
    exit 0
  else
    echo "=== ${tag} installed but cuda NOT available; purging and trying next ==="
    python -m pip uninstall -y torch triton $(python -m pip list 2>/dev/null | awk '/^nvidia-/{print $1}' | tr '\n' ' ') >/dev/null 2>&1 || true
  fi
done
echo "=== NO cuda-12.x torch 2.12 build worked on this driver (536.40 / CUDA 12.2) ==="
exit 4
