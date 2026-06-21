#!/usr/bin/env bash
# Deterministic eval-only regeneration of the airfoil primary-roster report + ledgers + npz
# from the six already-converged epoch-40 resume checkpoints (no training). Produces the
# canonical, recomputable evidence after the working tree was reset to HEAD.
set -uo pipefail
export http_proxy="http://127.0.0.1:7897" https_proxy="http://127.0.0.1:7897" no_proxy="localhost,127.0.0.1"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
source "$HOME/ext1-venv/bin/activate"
cd /mnt/d/Codes/Domain-Validity-Gated-MR-for-SciML

OUT="research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster"
LOG="$HOME/ext1_regen.log"
: > "$LOG"
python tools/run_physicsnemo_mgn_airfoil_workflow.py \
  --out "$OUT" --n-train 100 --n-test 40 --snaps-per-traj-train 20 \
  --hidden 128 --processor-size 15 --loss huber --grad-clip 1.0 --batch-size 12 \
  --lr 1e-3 --epochs 40 --k-checkpoints 6 --seed 20260616 --threads 12 >>"$LOG" 2>&1
rc=$?
echo "=== REGEN EXIT rc=${rc} ==="
tail -4 "$LOG"
exit $rc
