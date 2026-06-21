#!/usr/bin/env bash
# Parameterized single-checkpoint diagnostic training probe for EXT-1 airfoil convergence.
# Fixed: n_train=100 n_test=40 hidden=128 processor_size=15 k=1 (matches C35 architecture
# and the staged cache, so no re-staging race across concurrent probes).
# Usage: _ext1_diag_train.sh TAG EPOCHS LR SNAPS LOSS GRADCLIP SEED [HUBERDELTA]
set -uo pipefail
export http_proxy="http://127.0.0.1:7897" https_proxy="http://127.0.0.1:7897" no_proxy="localhost,127.0.0.1"
source "$HOME/ext1-venv/bin/activate"
cd /mnt/d/Codes/Domain-Validity-Gated-MR-for-SciML

TAG="${1:?tag}"; EPOCHS="${2:?epochs}"; LR="${3:?lr}"; SNAPS="${4:?snaps}"
LOSS="${5:?loss}"; GRADCLIP="${6:?gradclip}"; SEED="${7:?seed}"; HUBER="${8:-1.0}"
OUT="$HOME/ext1_scratch/${TAG}"
mkdir -p "$OUT"
echo "=== DIAG PROBE tag=${TAG} epochs=${EPOCHS} lr=${LR} snaps=${SNAPS} loss=${LOSS} clip=${GRADCLIP} seed=${SEED} ==="

python tools/run_physicsnemo_mgn_airfoil_workflow.py \
  --out "$OUT" --n-train 100 --n-test 40 --k-checkpoints 1 \
  --epochs "$EPOCHS" --lr "$LR" --snaps-per-traj-train "$SNAPS" \
  --loss "$LOSS" --grad-clip "$GRADCLIP" --huber-delta "$HUBER" \
  --hidden 128 --processor-size 15 --seed "$SEED" --threads 8 2>&1 | tail -40

python - "$OUT" "$TAG" <<'PY'
import sys, json
from pathlib import Path
out, tag = sys.argv[1], sys.argv[2]
rep = json.loads((Path(out)/"physicsnemo_mgn_airfoil_workflow_report.json").read_text())
losses = rep["training"]["losses"]
m = rep["metrics"]
res = {
  "tag": tag,
  "final_loss": round(losses[-1],5) if losses else None,
  "loss_first": round(losses[0],5) if losses else None,
  "loss_min": round(min(losses),5) if losses else None,
  "n_epochs": len(losses),
  "rollout_median_relL2": round(m["median_one_step_rollout_relative_l2"],5),
  "node_perm": m["node_permutation_passes"],
  "cons_ratio": round(m["median_compressible_residual_ratio"],4),
  "density_var": round(m["median_density_max_over_min"],3),
  "loss_curve": [round(x,4) for x in losses],
}
print("DIAG_RESULT " + json.dumps(res))
PY
