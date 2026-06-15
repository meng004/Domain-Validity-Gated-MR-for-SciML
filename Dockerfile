# Reproducible Tier-1 (smoke) toolchain: manuscript regression suite + validators.
# CPU only, no API key, no external data. The from-scratch SUT runs (Tier 3)
# need a CUDA base image and are out of scope for this image by design.
FROM python:3.12-slim

WORKDIR /app

# Install the verifiable-tier dependencies first for layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir numpy==1.26.4 PyYAML==6.0.2

# Copy the repository (committed artifacts under research_assets/runs/ are
# required by the test suite and the fail-closed validators).
COPY . .

# Default: the compile-independent CI checks (validators + the unittest subset
# that needs no LaTeX artifacts). Non-zero exit if any gate fails. The full
# pytest suite's one compile-gate test (test_stage4) is out of scope here because
# this image has no TeX; see REPRODUCIBILITY.md.
CMD ["sh", "-c", "python -m unittest tests/test_research_assets.py tests/test_executable_mr_assets.py tests/test_experiment_protocol.py tests/test_real_sut_runner_contract.py tests/test_mirror_y_rubric.py tests/test_mirror_y_runner_contract.py tests/test_conservation_rubric.py tests/test_conservation_runner_contract.py && python tools/validate_research_assets.py && python tools/validate_experiment_protocol.py"]
