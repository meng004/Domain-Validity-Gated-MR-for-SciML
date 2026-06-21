#!/usr/bin/env bash
set -uo pipefail
export http_proxy="http://127.0.0.1:7897"
export https_proxy="http://127.0.0.1:7897"
export no_proxy="localhost,127.0.0.1"
source "$HOME/ext1-venv/bin/activate"
echo "=== WSL nvidia-smi (host driver via passthrough) ==="
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader 2>&1 | head -2 || echo "nvidia-smi FAIL"
echo "=== torch real GPU matmul ==="
python - <<'PY'
import torch, math
print("torch", torch.__version__, "cuda_build", torch.version.cuda, "avail", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device", torch.cuda.get_device_name(0))
    x = torch.randn(4096,4096,device="cuda")
    y = x @ x
    torch.cuda.synchronize()
    print("MATMUL_OK", math.isfinite(float(y.sum())))
    # exercise a scatter (torch_scatter) op on GPU too
    import torch_scatter
    idx = torch.randint(0,100,(10000,),device="cuda")
    src = torch.randn(10000,8,device="cuda")
    out = torch_scatter.scatter_add(src, idx, dim=0, dim_size=100)
    torch.cuda.synchronize()
    print("SCATTER_OK", tuple(out.shape), math.isfinite(float(out.sum())))
else:
    print("CUDA STILL UNAVAILABLE")
PY
echo "=== proxy reachability to googleapis ==="
curl -sI --max-time 25 "https://storage.googleapis.com/dm-meshgraphnets/airfoil/meta.json" 2>&1 | grep -E "HTTP/|Content-Length" || echo "GOOGLEAPIS UNREACHABLE FROM WSL"
