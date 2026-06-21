#!/usr/bin/env bash
set -uo pipefail
source "$HOME/ext1-venv/bin/activate"
echo "=== reinstall torchvision matching torch 2.12.1+cu126 ==="
python -m pip install --force-reinstall --no-deps \
  --index-url https://download.pytorch.org/whl/cu126 \
  "torchvision==0.27.1" 2>&1 | tail -5
echo "=== versions ==="
python -c 'import torch,torchvision; print("torch",torch.__version__,"torchvision",torchvision.__version__)'
echo "=== re-run import smoke (physicsnemo) ==="
python - <<'PY'
try:
    import torchvision
    from torchvision.ops import nms  # forces C++ op load
    print("OK torchvision ops load", torchvision.__version__)
except Exception as e:
    print("FAIL torchvision ops", type(e).__name__, str(e)[:160])
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
