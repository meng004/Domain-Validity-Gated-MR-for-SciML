#!/usr/bin/env bash
# Post-convergence: rerun the airfoil seeded-fault detection on the converged checkpoint
# (checkpoint_k01_seed20260616.pt from the primary-roster). Now that the model is trained,
# baseline node-perm rel-L2 != 0 and the detection matrix is non-trivial (unlike the
# under-trained collapse). Writes the cross-SUT metric ledger that claim C36 / test
# test_seeded_fault_detection_airfoil_cross_sut.py consume.
set -uo pipefail
export http_proxy="http://127.0.0.1:7897" https_proxy="http://127.0.0.1:7897" no_proxy="localhost,127.0.0.1"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
source "$HOME/ext1-venv/bin/activate"
cd /mnt/d/Codes/Domain-Validity-Gated-MR-for-SciML

python tools/run_seeded_fault_detection_physicsnemo_airfoil.py \
  --traj-indices 0,1,2,3,4 --n-frames 9 2>&1 | tail -30

echo "=== seeded-fault ledger summary ==="
python - <<'PY'
import json
from pathlib import Path
p = Path("research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-seeded-fault-detection/raw/metric_ledger.json")
d = json.loads(p.read_text())
rob = d["robustness"]; xs = d["cross_sut_comparison"]
print("n_trajectories:", rob["n_trajectories"])
print("robustly_detected:", rob["robustly_detected_mutants"])
print("unstable:", rob["unstable_mutants"])
print("never_detected:", rob["never_detected_mutants"])
print("node_perm_MR_detection_rate:", rob["node_permutation_MR_detection_rate"])
print("conservation_robustly_localizes:", rob["conservation_robustly_localizes"])
print("shared_localization_across_suts:", xs["shared_localization_across_suts"])
print("mirror_y_status:", xs["mirror_y_status_on_airfoil"])
PY
