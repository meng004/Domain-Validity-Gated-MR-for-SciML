#!/usr/bin/env bash
# Reproduce the OpenMC build behind the C40 end-to-end E5 (Monte-Carlo) execution.
#
# Why a source build: openmc has no pip wheel/sdist on the default index, no conda is
# present, and there is no running Docker daemon in the CPU container, so the only way to
# get a runnable OpenMC here is to build it from source. Tag v0.15.2 is the Python-3.11-
# compatible release (main requires >=3.12). The C40 E5 subject runs OpenMC in MULTI-GROUP
# mode with a self-generated 1-group MGXS library, so NO continuous-energy nuclear data
# (~GB ENDF/B) is needed. CPU-only.
#
# After this script succeeds, run the pipeline (E5 then executes for real):
#   MMRS=/home/user/Minimum-MR-SubSet
#   PYTHONPATH="$MMRS/scripts:$MMRS" LD_LIBRARY_PATH=/usr/local/lib \
#     python3 tools/run_endtoend_pipeline_pseries.py
set -euo pipefail

OPENMC_TAG="${OPENMC_TAG:-v0.15.2}"
SRC="${OPENMC_SRC:-/tmp/openmc-${OPENMC_TAG}}"
PREFIX="${OPENMC_PREFIX:-/usr/local}"
MMRS="${MMRS_ROOT:-/home/user/Minimum-MR-SubSet}"

# 0. Idempotent skip: nothing to do if openmc is already importable and runnable.
if python3 -c "import openmc" >/dev/null 2>&1 && command -v openmc >/dev/null 2>&1; then
    echo "openmc already present: $(openmc --version 2>/dev/null | head -1); skipping build."
    exit 0
fi

# 1. Build dependencies: serial HDF5 + PNG; cmake + a C++ compiler. numpy/scipy are the
#    Python-side requirements for the classical SUTs and come from requirements + scipy.
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libhdf5-dev libpng-dev cmake g++ git

# 2. Source at the Python-3.11-compatible tag, with the vendored fmt/pugixml/xtensor/xtl
#    submodules (Catch2 is test-only). Shallow clone keeps it fast.
rm -rf "$SRC"
git clone --depth 1 --branch "$OPENMC_TAG" --recurse-submodules --shallow-submodules \
    https://github.com/openmc-dev/openmc.git "$SRC"

# 3. Build + install the C++ core (libopenmc + the `openmc` executable). Serial HDF5.
HDF5_ROOT="${HDF5_ROOT:-/usr/lib/x86_64-linux-gnu/hdf5/serial}" \
    cmake -S "$SRC" -B "$SRC/build" \
    -DCMAKE_INSTALL_PREFIX="$PREFIX" -DCMAKE_BUILD_TYPE=Release -DHDF5_PREFER_PARALLEL=OFF
cmake --build "$SRC/build" -j"$(nproc)"
cmake --install "$SRC/build"
ldconfig

# 4. Install the (pure-Python) OpenMC API. Build isolation is REQUIRED: the Debian system
#    setuptools lacks the patched `install_layout`, so --no-build-isolation fails; the
#    default isolated build pulls a clean setuptools and succeeds.
python3 -m pip install "$SRC"

# 5. Smoke-verify the real solver against the closed-form 1-group infinite-medium k_inf.
PYTHONPATH="$MMRS/scripts:$MMRS" LD_LIBRARY_PATH="$PREFIX/lib" python3 - <<'PY'
from mcmr.openmc_put.smoke_mg import run_inf_medium
k, kstd, kref = run_inf_medium(particles=2000, batches=30, inactive=10, seed=1)
tol = max(5.0 * kstd, 5e-3)
assert abs(k - kref) <= tol, f"OpenMC k_eff={k} disagrees with analytic k_inf={kref}"
import openmc
print(f"OpenMC {openmc.__version__} build verified: k_eff={k:.5f} == analytic k_inf={kref:.5f}")
PY

echo "Build OK. Now run the C40 pipeline so E5 executes:"
echo "  PYTHONPATH=$MMRS/scripts:$MMRS LD_LIBRARY_PATH=$PREFIX/lib python3 tools/run_endtoend_pipeline_pseries.py"
