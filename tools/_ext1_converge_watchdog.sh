#!/usr/bin/env bash
# Self-healing launcher for the EXT-1 k=6 convergence run. WSL2 long CUDA jobs hang
# intermittently near full VRAM; this detects an output stall (no new training log for
# ~5 min), kills the hung process, waits for the GPU to free, and relaunches. The runner's
# per-epoch resume (resume_ckpt_seed*.pt in STAGE_DIR) means each relaunch continues where
# it stopped (completed checkpoints are reloaded + re-evaluated, the in-progress one resumes).
set -uo pipefail
export http_proxy="http://127.0.0.1:7897" https_proxy="http://127.0.0.1:7897" no_proxy="localhost,127.0.0.1"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
source "$HOME/ext1-venv/bin/activate"
cd /mnt/d/Codes/Domain-Validity-Gated-MR-for-SciML

OUT="research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster"
LOG="$HOME/ext1_converge_run.log"
REPORT="$OUT/physicsnemo_mgn_airfoil_workflow_report.json"
STALL_MIN=5

gpu_wait_free() {
  for i in $(seq 1 20); do
    m=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
    [ -n "$m" ] && [ "$m" -lt 2000 ] && { echo "  gpu free (${m} MiB)"; return 0; }
    sleep 3
  done
  echo "  gpu still busy after wait"
}

for attempt in $(seq 1 30); do
  echo "==== WATCHDOG attempt ${attempt} $(date -u +%H:%M:%S) ===="
  pkill -9 -f run_physicsnemo_mgn_airfoil_workflow 2>/dev/null || true
  gpu_wait_free
  : > "$LOG"
  python tools/run_physicsnemo_mgn_airfoil_workflow.py \
    --out "$OUT" --n-train 100 --n-test 40 --snaps-per-traj-train 20 \
    --hidden 128 --processor-size 15 --loss huber --grad-clip 1.0 --batch-size 12 \
    --lr 1e-3 --epochs 40 --k-checkpoints 6 --seed 20260616 --threads 12 >>"$LOG" 2>&1 &
  PID=$!
  last=-1; stall=0
  while kill -0 "$PID" 2>/dev/null; do
    sleep 60
    cur=$(stat -c%s "$LOG" 2>/dev/null || echo 0)
    if [ "$cur" -eq "$last" ]; then stall=$((stall+1)); else stall=0; fi
    last=$cur
    echo "  [watch] stall=${stall}min size=${cur} :: $(tail -1 "$LOG" 2>/dev/null | cut -c1-90)"
    if grep -q "wrote .*report" "$LOG" 2>/dev/null; then break; fi
    if [ "$stall" -ge "$STALL_MIN" ]; then
      echo "  >>> STALL ${stall}min: killing ${PID} and resuming"
      kill -9 "$PID" 2>/dev/null || true; sleep 8; break
    fi
  done
  wait "$PID" 2>/dev/null || true
  if grep -q "wrote .*report" "$LOG" 2>/dev/null && [ -f "$REPORT" ]; then
    echo "==== WATCHDOG: CONVERGENCE COMPLETE on attempt ${attempt} ===="
    tail -20 "$LOG"
    exit 0
  fi
  echo "  run ended without completion; relaunching (resume)"
done
echo "==== WATCHDOG: gave up after max attempts ===="
tail -25 "$LOG"
exit 1
