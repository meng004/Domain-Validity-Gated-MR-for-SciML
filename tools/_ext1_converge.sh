#!/usr/bin/env bash
# EXT-1 full convergence run: K=6 roster, converged recipe (huber + grad-clip + batched +
# bf16 AMP), seed 20260616 so checkpoint_k01_seed20260616.pt matches the seeded-fault runner.
# Overwrites the committed (under-trained) primary-roster report/ledgers with converged ones.
set -uo pipefail
export http_proxy="http://127.0.0.1:7897" https_proxy="http://127.0.0.1:7897" no_proxy="localhost,127.0.0.1"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
source "$HOME/ext1-venv/bin/activate"
cd /mnt/d/Codes/Domain-Validity-Gated-MR-for-SciML

OUT="research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster"
# Proven no-AMP recipe (bf16 autocast crashes layer_norm in this torch/physicsnemo stack):
# huber + grad-clip + batched GPU-preloaded training, batch 12 (max that fits 24GB at FP32).
python tools/run_physicsnemo_mgn_airfoil_workflow.py \
  --out "$OUT" \
  --n-train 100 --n-test 40 --snaps-per-traj-train 20 \
  --hidden 128 --processor-size 15 \
  --loss huber --grad-clip 1.0 --batch-size 12 \
  --lr 1e-3 --epochs 40 --k-checkpoints 6 --seed 20260616 --threads 12

echo "=== convergence report summary ==="
python - "$OUT" <<'PY'
import sys, json
from pathlib import Path
rep = json.loads((Path(sys.argv[1])/"physicsnemo_mgn_airfoil_workflow_report.json").read_text())
m = rep["metrics"]; r = rep["roster"]
print("device:", rep.get("device_used"))
print("rollout median rel-L2:", m["median_one_step_rollout_relative_l2"])
print("node_perm:", m["node_permutation_passes"], "max_rel_l2:", m["node_permutation_max_relative_l2"])
print("cons_ratio:", m["median_compressible_residual_ratio"], "density_var:", m["median_density_max_over_min"])
print("k_completed:", r["k_checkpoints_completed"], "total_wall_clock_s:", r.get("total_wall_clock_s"))
for s in r["per_checkpoint_summary"]:
    print(f"  ckpt{s['checkpoint_index']} seed{s['seed']} final_loss={s['final_loss']:.4f} "
          f"node_perm={s['node_perm_passes']} cons={s['median_cons_ratio']:.3f}")
PY
