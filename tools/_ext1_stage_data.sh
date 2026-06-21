#!/usr/bin/env bash
set -uo pipefail
export http_proxy="http://127.0.0.1:7897"
export https_proxy="http://127.0.0.1:7897"
export no_proxy="localhost,127.0.0.1"
source "$HOME/ext1-venv/bin/activate"
cd /mnt/d/Codes/Domain-Validity-Gated-MR-for-SciML
NTRAIN="${1:-100}"
NTEST="${2:-40}"
echo "=== staging airfoil data: n_train=${NTRAIN} n_test=${NTEST} (STAGE_DIR=~/.cache/dvgmr/airfoil_staged) ==="
python - "$NTRAIN" "$NTEST" <<'PY'
import sys, json
sys.path.insert(0, "tools")
import run_physicsnemo_mgn_airfoil_workflow as af
ntrain, ntest = int(sys.argv[1]), int(sys.argv[2])
rec = af.stage_data(ntrain, ntest)
print("stage_dir", rec["stage_dir"])
print("simulator", rec.get("simulator"))
meta = json.loads((af.STAGE_DIR / "meta.json").read_text())
print("meta keys:", list(meta.keys()))
for k in ("dt","trajectory_length","field_names"):
    if k in meta: print(" ", k, meta[k])
for r in rec["records"]:
    print("  split=%s n_records=%d bytes=%.1fMB" % (r["split"], r["n_records"], r["bytes"]/1e6))
PY
echo "=== staged files ==="
ls -la "$HOME/.cache/dvgmr/airfoil_staged/" 2>&1
