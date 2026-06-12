# Reproducing the PhysicsNeMo Object-A Smoke Workflow

This note archives the exact environment, commands, data staging behavior, and expected artifacts for the P0c Object-A smoke workflow. It is intentionally scoped to the NVIDIA PhysicsNeMo MeshGraphNet class on a first-record DeepMind `cylinder_flow` smoke subset. It is **not** a full production-scale PhysicsNeMo benchmark and it does not cover AeroGraphNet or DoMINO.

## 1. Scope and expected claim

The workflow provides an artifact-gated smoke execution for the selected production framework object:

- **Object**: `physicsnemo-mgn-vortex-shedding`.
- **SUT class**: NVIDIA PhysicsNeMo `MeshGraphNet`.
- **Data source**: DeepMind public `cylinder_flow` TFRecord files from `https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/`.
- **Subset**: first complete TFRecord trajectory for `train` and `test`; `valid.tfrecord` is copied from the smoke `test.tfrecord` only to satisfy PhysicsNeMo datapipe completeness checks.
- **Allowed statement**: a CPU-executable PhysicsNeMo MeshGraphNet smoke-subset artifact chain was produced with a newly trained checkpoint, raw outputs, and metric ledgers.
- **Forbidden statements**: full production-scale pass/fail rates, AeroGraphNet results, DoMINO results, cross-dataset reliability, or geometry-independent validity.

## 2. Fresh environment

Use a fresh virtual environment so that dependency resolution is auditable:

```bash
python3 -m venv .venv-physicsnemo-object-a
source .venv-physicsnemo-object-a/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements/physicsnemo-object-a-smoke.txt
```

If the exact PyG wheel URL in the requirements file is unavailable for your platform, install a `torch-scatter` wheel matching the resolved `torch` version from the official PyG wheel index, then rerun the command above for the remaining packages.

## 3. Runtime and access preflight

Run the staging auditors before executing the smoke workflow. These commands do not claim production workflow results; they record whether the production objects are executable or blocked:

```bash
python3 tools/audit_production_sut_feasibility.py
python3 tools/build_production_sut_candidate_ledgers.py
python3 tools/stage_physicsnemo_runtime.py
python3 tools/stage_physicsnemo_mgn_assets.py
python3 tools/stage_production_sut_official_access.py
```

The auditors write JSON reports under `research_assets/runs/production-grade-sut-extension/` and keep large external data outside git.

## 4. Data staging behavior

The smoke runner writes temporary first-record TFRecord files under:

```text
/workspace/physicsnemo_staged_assets/mgn/cylinder_flow_smoke/
```

The staged files are intentionally outside the repository and are not committed. They are reproducible from the DeepMind public GCS URLs. The committed report records file sizes and SHA-256 prefixes for auditability.

## 5. Run the Object-A smoke workflow

Execute the same CPU-friendly command used for the archived artifact:

```bash
python3 tools/run_physicsnemo_mgn_smoke_workflow.py --epochs 2 --num-steps 4 --hidden 16 --processor-size 1
```

Expected committed outputs are written to:

```text
research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-vortex-shedding/
```

The key artifacts are:

- `physicsnemo_mgn_smoke_checkpoint.pt`
- `raw_outputs/source_followup_outputs.npz`
- `physicsnemo_mgn_smoke_workflow_report.json`
- `physicsnemo_mgn_smoke_manifest.json`
- `physicsnemo_mgn_smoke_rubric_decisions.json`
- `node_permutation_metric_ledger.json`
- `mirror_ood_stress_metric_ledger.json`
- `conservation_reference_relative_metric_ledger.json`
- `rollout_accuracy_metric_ledger.json`

## 6. Validation commands

Run the focused guards first, then the full suite:

```bash
python3 -m pytest tests/test_physicsnemo_mgn_smoke_workflow.py tests/test_physicsnemo_runtime_staging.py tests/test_physicsnemo_mgn_asset_staging.py tests/test_production_sut_official_access_staging.py -q
python3 -m pytest tests -q
```

The smoke workflow test checks the report identity, artifact-chain existence, metric bounds, and honesty boundary. The staging tests check that Object-A smoke execution does not silently become a full-scale production claim and that Object-B/Object-C remain blocked until their official data/checkpoint/API/raw-output/ledger gates are satisfied.

## 7. Troubleshooting notes

- If importing `physicsnemo` fails, rerun the requirements install in a clean virtual environment and check that `nvidia-physicsnemo==2.1.1` installed successfully.
- If `torch_scatter` fails to install, choose the PyG wheel index matching your resolved `torch` version and Python ABI.
- If the datapipe writes `edge_stats.json` or `node_stats.json`, verify that the runner is executing with the staging directory as the temporary working directory; those generated files should not appear in the repository root.
- If network access to `storage.googleapis.com` is blocked, pre-stage the first complete records at the external staging path above or run in an environment with access to the DeepMind public bucket.
