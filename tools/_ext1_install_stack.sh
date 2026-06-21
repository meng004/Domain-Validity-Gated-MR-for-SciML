#!/usr/bin/env bash
set -uo pipefail
source "$HOME/ext1-venv/bin/activate"

TORCH_VER=$(python -c 'import torch;print(torch.__version__.split("+")[0])')          # e.g. 2.12.1
TORCH_MINOR0="${TORCH_VER%.*}.0"                                                        # e.g. 2.12.0
CUDA_TAG=$(python -c 'import torch;print("cu"+torch.version.cuda.replace(".",""))')     # e.g. cu126
echo "=== torch ${TORCH_VER} (${CUDA_TAG}); PyG link candidates for ${TORCH_VER} and ${TORCH_MINOR0} ==="

echo "=== core deps ==="
python -m pip install "numpy==1.26.4" scipy pyyaml tfrecord 2>&1 | tail -4

echo "=== torch_geometric ==="
python -m pip install torch_geometric 2>&1 | tail -3

echo "=== torch_scatter (try matched prebuilt wheels) ==="
SCATTER_OK=0
for tv in "${TORCH_VER}" "${TORCH_MINOR0}"; do
  L="https://data.pyg.org/whl/torch-${tv}+${CUDA_TAG}.html"
  echo "--- trying find-links ${L}"
  if python -m pip install torch_scatter -f "${L}" 2>&1 | tail -4; then
    if python -c 'import torch_scatter' 2>/dev/null; then echo "torch_scatter OK via ${L}"; SCATTER_OK=1; break; fi
  fi
done
if [ "$SCATTER_OK" -ne 1 ]; then
  echo "--- prebuilt failed; attempting source build (may lack nvcc -> CPU-only ext)"
  python -m pip install --no-build-isolation torch_scatter 2>&1 | tail -8 || true
fi

echo "=== nvidia-physicsnemo==2.1.1 (pin torch so it is not downgraded) ==="
python -m pip install "nvidia-physicsnemo==2.1.1" "torch==${TORCH_VER}" 2>&1 | tail -15

echo "=== IMPORT SMOKE (CPU-side only; no GPU kernel) ==="
python - <<'PY'
import importlib, torch
print("torch", torch.__version__, "cuda_build", torch.version.cuda)
for m in ["numpy","scipy","yaml","tfrecord","torch_geometric","torch_scatter"]:
    try:
        mod=importlib.import_module(m); print("OK", m, getattr(mod,"__version__","?"))
    except Exception as e:
        print("FAIL", m, type(e).__name__, str(e)[:160])
try:
    from physicsnemo.models.meshgraphnet import MeshGraphNet
    m=MeshGraphNet(input_dim_nodes=6,input_dim_edges=3,output_dim=3,processor_size=2,
                   hidden_dim_processor=16,hidden_dim_node_encoder=16,hidden_dim_edge_encoder=16,
                   hidden_dim_node_decoder=16,num_layers_node_processor=1,num_layers_edge_processor=1,
                   num_layers_node_encoder=1,num_layers_edge_encoder=1,num_layers_node_decoder=1,
                   aggregation="sum")
    print("OK physicsnemo MeshGraphNet construct, params", sum(p.numel() for p in m.parameters()))
except Exception as e:
    print("FAIL physicsnemo", type(e).__name__, str(e)[:200])
PY
