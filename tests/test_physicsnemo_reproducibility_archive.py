from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/reproducibility/physicsnemo-object-a-smoke.md"
RUN_DOC = ROOT / "research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-vortex-shedding/REPRODUCIBILITY.md"
REQ = ROOT / "requirements/physicsnemo-object-a-smoke.txt"


def test_physicsnemo_object_a_requirements_are_archived():
    text = REQ.read_text(encoding="utf-8")
    required = [
        "nvidia-physicsnemo==2.1.1",
        "torch",
        "torch-geometric",
        "torch-scatter",
        "tfrecord",
        "vtk",
        "wandb",
        "--extra-index-url https://download.pytorch.org/whl/cpu",
        "--find-links https://data.pyg.org/whl/torch-2.12.0+cpu.html",
    ]
    for item in required:
        assert item in text


def test_physicsnemo_object_a_reproducibility_steps_are_archived_with_outputs():
    text = DOC.read_text(encoding="utf-8")
    run_text = RUN_DOC.read_text(encoding="utf-8")
    assert text == run_text
    required_snippets = [
        "python3 -m pip install -r requirements/physicsnemo-object-a-smoke.txt",
        "python3 tools/audit_production_sut_feasibility.py",
        "python3 tools/build_production_sut_candidate_ledgers.py",
        "python3 tools/stage_physicsnemo_runtime.py",
        "python3 tools/stage_physicsnemo_mgn_assets.py",
        "python3 tools/stage_production_sut_official_access.py",
        "python3 tools/run_physicsnemo_mgn_smoke_workflow.py --epochs 2 --num-steps 4 --hidden 16 --processor-size 1",
        "python3 -m pytest tests/test_physicsnemo_mgn_smoke_workflow.py",
        "physicsnemo_mgn_smoke_checkpoint.pt",
        "raw_outputs/source_followup_outputs.npz",
        "physicsnemo_mgn_smoke_workflow_report.json",
        "node_permutation_metric_ledger.json",
        "mirror_ood_stress_metric_ledger.json",
        "conservation_reference_relative_metric_ledger.json",
        "rollout_accuracy_metric_ledger.json",
        "/workspace/physicsnemo_staged_assets/mgn/cylinder_flow_smoke/",
        "Forbidden statements",
    ]
    for snippet in required_snippets:
        assert snippet in text
