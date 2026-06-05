from pathlib import Path
import importlib.util
import tempfile
import unittest


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
