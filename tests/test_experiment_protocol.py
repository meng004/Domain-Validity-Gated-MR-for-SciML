from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile
import unittest


def _write_real_run_fixture(
    root: Path, checkpoint_sha256: str, *, raw_outputs: bool = True
) -> Path:
    """Materialize a temp real-SUT run (manifest + artifacts) under ``root`` and
    return the manifest path. ``checkpoint_sha256`` is written verbatim into the
    manifest so callers can exercise both the matching and mismatching cases.
    When ``raw_outputs`` is False the run keeps a metric ledger but omits the
    source/follow-up/mapped raw output files, exercising the fail-closed gate."""
    run_dir = root / "research_assets" / "runs" / "r"
    (run_dir / "raw").mkdir(parents=True)
    (run_dir / "sut").mkdir()
    (run_dir / "sut" / "checkpoint.pt").write_bytes(b"trained-weights")
    (run_dir / "case.npz").write_bytes(b"source-case")

    raw_names = ["source_output", "follow_up_output", "mapped_output"]
    if raw_outputs:
        for name in raw_names:
            (run_dir / "raw" / f"{name}.npy").write_bytes(b"x")
        ledger = {
            "raw_outputs": {
                name: f"research_assets/runs/r/raw/{name}.npy" for name in raw_names
            }
        }
    else:
        ledger = {"raw_outputs": {}}
    (run_dir / "raw" / "metric_ledger.json").write_text(
        json.dumps(ledger), encoding="utf-8"
    )
    manifest = run_dir / "manifest.yml"
    manifest.write_text(
        "\n".join(
            [
                "run_id: real-sut-x",
                "sut_id: cylinder_flow_meshgraphnet",
                "sut_repo: /repo",
                "sut_commit: abc123",
                "checkpoint_path: research_assets/runs/r/sut/checkpoint.pt",
                f"checkpoint_sha256: {checkpoint_sha256}",
                "dataset_root: /data",
                "source_case_path: research_assets/runs/r/case.npz",
                "mr_id: mgn-node-permutation-equivariance",
                "command: python3 tools/run_real_sut_mr.py --manifest manifest.yml",
                "raw_output_dir: research_assets/runs/r/raw",
                "seed: 0",
                "device: cpu",
                "python_version: 3.11.0",
                "framework_version: torch 2.12.0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    ledger = root / "research_assets" / "experiments" / "experiment-ledger.yml"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(
        "\n".join(
            [
                "runs:",
                '  - run_id: "real-sut-x"',
                '    status: "observed"',
                '    sut_execution: "run"',
                '    manifest: "research_assets/runs/r/manifest.yml"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_experiment_protocol.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_experiment_protocol", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExperimentProtocolTests(unittest.TestCase):
    def test_experiment_protocol_files_exist_and_have_required_sections(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "experiment_protocol_files"], errors)

    def test_score_task_defines_subject_metrics_baselines_and_stopping_rule(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "score_task"], errors)

    def test_experiment_ledger_keeps_real_sut_runs_blocked_without_artifacts(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "experiment_ledger"], errors)

    def test_claim_ledger_blocks_empirical_result_claims(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "claim_ledger"], errors)

    def test_protocol_note_preserves_supported_and_blocked_boundaries(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "protocol_note"], errors)

    def test_experiment_ledger_rejects_empirical_result_fields_before_real_runs(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ledger = root / "research_assets" / "experiments" / "experiment-ledger.yml"
            ledger.parent.mkdir(parents=True)
            ledger.write_text(
                "\n".join(
                    [
                        "runs:",
                        "  - run_id: \"real-sut-bad\"",
                        "    status: passed",
                        "    sut_execution: \"run\"",
                        "    outcome: passed",
                        "    violation_rate: 0.25",
                    ]
                ),
                encoding="utf-8",
            )

            errors = validator.validate_experiment_ledger(root)
            messages = " ".join(error["message"] for error in errors)
            self.assertIn("forbidden empirical marker", messages)
            self.assertIn("status must remain blocked", messages)

    def test_claim_ledger_rejects_baseline_superiority_before_matched_runs(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ledger = root / "research_assets" / "experiments" / "claim-ledger.yml"
            ledger.parent.mkdir(parents=True)
            ledger.write_text(
                "\n".join(
                    [
                        "claims:",
                        "  - claim_id: \"bad-baseline\"",
                        "    status: \"supported\"",
                        "    baseline_superiority: true",
                        "    wording_allowed: \"The protocol outperforms rollout accuracy.\"",
                    ]
                ),
                encoding="utf-8",
            )

            errors = validator.validate_claim_ledger(root)
            messages = " ".join(error["message"] for error in errors)
            self.assertIn("forbidden empirical marker", messages)

    def test_score_task_contains_run_manifest_and_baseline_scoring_contracts(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "score_task"], errors)

    def test_real_sut_preconditions_block_runs_when_env_unset(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ledger = root / "research_assets" / "experiments" / "experiment-ledger.yml"
            ledger.parent.mkdir(parents=True)
            ledger.write_text(
                "\n".join(
                    [
                        "runs:",
                        "  - run_id: \"real-sut-echowve-blocked\"",
                        "    status: \"observed\"",
                        "    sut_execution: \"run\"",
                    ]
                ),
                encoding="utf-8",
            )

            errors = validator.validate_real_sut_preconditions(root, env={})
            messages = " ".join(error["message"] for error in errors)
            self.assertIn("must stay blocked", messages)
            self.assertIn("must stay not-run", messages)

    def test_real_sut_preconditions_pass_for_current_blocked_ledger(self):
        validator = load_validator()
        errors = validator.validate_real_sut_preconditions(ROOT, env={})
        self.assertEqual(errors, [], errors)

    def test_real_sut_preconditions_run_inside_validate_repo(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [e for e in errors if e["asset"] == "real_sut_preconditions"], errors
        )

    def test_real_sut_observed_run_requires_matching_checkpoint_sha256(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_real_run_fixture(root, checkpoint_sha256="0000deadbeef")
            # Even with all env vars set, a wrong checkpoint hash must be caught:
            # the gate is an artifact gate, not a prose/env gate.
            env = {name: "/set" for name in validator.REAL_SUT_REQUIRED_ENV}
            errors = validator.validate_real_sut_preconditions(root, env=env)
            messages = " ".join(error["message"] for error in errors)
            self.assertIn("sha256 mismatch", messages)

    def test_real_sut_observed_run_passes_with_verified_manifest(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            real_sha = hashlib.sha256(b"trained-weights").hexdigest()
            _write_real_run_fixture(root, checkpoint_sha256=real_sha)
            # A verified manifest unblocks the run even with env unset.
            errors = validator.validate_real_sut_preconditions(root, env={})
            self.assertEqual(errors, [], errors)

    def test_real_sut_observed_run_rejected_when_raw_outputs_absent(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            real_sha = hashlib.sha256(b"trained-weights").hexdigest()
            # Checkpoint hash matches, but the metric ledger lists no raw outputs
            # and none exist on disk: the gate must not admit a verdict.
            _write_real_run_fixture(root, checkpoint_sha256=real_sha, raw_outputs=False)
            errors = validator.validate_real_sut_preconditions(root, env={})
            messages = " ".join(error["message"] for error in errors)
            self.assertIn("raw output", messages)

    def test_run_manifest_example_declares_all_required_fields(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse([e for e in errors if e["asset"] == "run_manifest"], errors)

    def test_run_manifest_missing_field_fails(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = root / "m.yml"
            # Complete manifest minus checkpoint_sha256.
            lines = [
                "run_id: r1",
                "sut_id: s1",
                "sut_repo: /repo",
                "sut_commit: deadbeef",
                "checkpoint_path: ckpt.pt",
                "dataset_root: /data",
                "source_case_path: case.npz",
                "mr_id: mgn-node-permutation-equivariance",
                "command: python3 tools/run_real_sut_mr.py --manifest m.yml",
                "raw_output_dir: raw",
                "seed: 0",
                "device: cpu",
                "python_version: 3.11.0",
                "framework_version: torch 2.12.0",
            ]
            manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
            errors = validator.validate_run_manifest(manifest)
            messages = " ".join(error["message"] for error in errors)
            self.assertIn("checkpoint_sha256", messages)

    def test_run_manifest_complete_passes(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest = root / "m.yml"
            lines = [
                "run_id: r1",
                "sut_id: s1",
                "sut_repo: /repo",
                "sut_commit: deadbeef",
                "checkpoint_path: ckpt.pt",
                "checkpoint_sha256: abc123",
                "dataset_root: /data",
                "source_case_path: case.npz",
                "mr_id: mgn-node-permutation-equivariance",
                "command: python3 tools/run_real_sut_mr.py --manifest m.yml",
                "raw_output_dir: raw",
                "seed: 0",
                "device: cpu",
                "python_version: 3.11.0",
                "framework_version: torch 2.12.0",
            ]
            manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
            self.assertEqual(validator.validate_run_manifest(manifest), [])

    def test_score_task_command_template_has_no_cloud_shell_prefix(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            task = root / "research_assets" / "experiments" / "score-task.yml"
            task.parent.mkdir(parents=True)
            task.write_text(
                "command_template: \"rtk python3 tools/run_real_sut_mr.py --manifest <run-manifest.yml>\"\n",
                encoding="utf-8",
            )

            errors = validator.validate_score_task(root)
            messages = " ".join(error["message"] for error in errors)
            self.assertIn("rtk", messages)


if __name__ == "__main__":
    unittest.main()
