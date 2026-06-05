from pathlib import Path
import importlib.util
import json
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_research_assets.py"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_research_assets", VALIDATOR_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ResearchAssetValidationTests(unittest.TestCase):
    def test_mr_card_contains_required_executable_fields(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [error for error in errors if error["asset"] == "mr_card"], errors
        )

    def test_validator_checks_all_mr_cards_and_not_only_node_permutation(self):
        validator = load_validator()
        self.assertTrue(
            hasattr(validator, "validate_all_mr_cards"),
            "validator must validate every JSON MR card under research_assets/mr_cards",
        )
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [error for error in errors if error["asset"] == "mr_card"],
            errors,
        )

    def test_all_mr_card_validation_visits_invalid_extra_card(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            card_dir = temp_root / "research_assets" / "mr_cards"
            card_dir.mkdir(parents=True)

            node_card = ROOT / "research_assets" / "mr_cards" / "node_permutation_equivariance.json"
            mirror_card = ROOT / "research_assets" / "mr_cards" / "mirror_y_equivariance.json"
            (card_dir / node_card.name).write_text(node_card.read_text(encoding="utf-8"), encoding="utf-8")
            (card_dir / mirror_card.name).write_text(mirror_card.read_text(encoding="utf-8"), encoding="utf-8")

            invalid_card = json.loads(node_card.read_text(encoding="utf-8"))
            invalid_card.pop("title")
            invalid_path = card_dir / "invalid_extra_card.json"
            invalid_path.write_text(json.dumps(invalid_card), encoding="utf-8")

            errors = validator.validate_all_mr_cards(temp_root)
            self.assertTrue(
                [
                    error
                    for error in errors
                    if "invalid_extra_card.json" in error["path"]
                    and "missing key: title" in error["message"]
                ],
                errors,
            )

    def test_retained_mr_cards_require_numeric_threshold(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            node_card = ROOT / "research_assets" / "mr_cards" / "node_permutation_equivariance.json"
            data = json.loads(node_card.read_text(encoding="utf-8"))
            data["tolerance"]["threshold"] = None
            path = Path(temp_dir) / "retained_without_threshold.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            errors = validator.validate_single_mr_card(path)
            self.assertTrue(
                [
                    error
                    for error in errors
                    if "threshold" in error["message"]
                ],
                errors,
            )

    def test_design_time_candidate_cards_cannot_carry_pass_fail_thresholds(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            divergence_card = ROOT / "research_assets" / "mr_cards" / "discrete_divergence_boundedness.json"
            data = json.loads(divergence_card.read_text(encoding="utf-8"))
            data["status"] = "design-time-retained"
            data["allowed_verdicts"] = ["pass", "fail"]
            data["tolerance"]["threshold"] = 1.0
            path = Path(temp_dir) / "candidate_with_asset_claims.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            errors = validator.validate_single_mr_card(path)
            self.assertTrue(
                [
                    error
                    for error in errors
                    if "candidate" in error["message"]
                ],
                errors,
            )

    def test_candidate_ledger_has_evidence_bounded_decisions(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [error for error in errors if error["asset"] == "candidate_ledger"],
            errors,
        )

    def test_candidate_ledger_evidence_references_resolve_locally(self):
        validator = load_validator()
        self.assertTrue(
            hasattr(validator, "validate_candidate_evidence_references"),
            "validator must resolve candidate evidence references",
        )
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [error for error in errors if error["asset"] == "candidate_evidence"],
            errors,
        )

    def test_candidate_evidence_references_must_name_fields_or_markers(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            ledger_dir = temp_root / "research_assets" / "ledgers"
            ledger_dir.mkdir(parents=True)
            (temp_root / "evidence.md").write_text("local evidence", encoding="utf-8")
            (ledger_dir / "candidate_ledger.json").write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "candidate_id": "bad-reference",
                                "evidence_reference": [{"path": "evidence.md"}],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            errors = validator.validate_candidate_evidence_references(temp_root)
            self.assertTrue(
                [
                    error
                    for error in errors
                    if "fields or local_markers" in error["message"]
                ],
                errors,
            )

    def test_candidate_ledger_shows_rubric_accept_reject_defer_and_ood_stress(self):
        validator = load_validator()
        self.assertTrue(
            hasattr(validator, "validate_rubric_decision_coverage"),
            "validator must check rubric decision coverage",
        )
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [error for error in errors if error["asset"] == "rubric_decision_coverage"],
            errors,
        )

    def test_rubric_file_controls_candidate_ledger_decisions(self):
        validator = load_validator()
        self.assertTrue(
            hasattr(validator, "validate_domain_validity_rubric"),
            "validator must check the domain-validity rubric file",
        )
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [
                error
                for error in errors
                if error["asset"] in {"domain_validity_rubric", "candidate_ledger"}
            ],
            errors,
        )

    def test_verdict_ledger_schema_disallows_empirical_claims_without_runs(self):
        validator = load_validator()
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [error for error in errors if error["asset"] == "verdict_ledger"],
            errors,
        )

    def test_verdict_schema_contains_strict_runtime_contract(self):
        validator = load_validator()
        self.assertTrue(
            hasattr(validator, "validate_verdict_schema_contract"),
            "validator must check verdict schema required fields and enum",
        )
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [error for error in errors if error["asset"] == "verdict_schema_contract"],
            errors,
        )

    def test_reference_ledger_marks_unverified_sources_explicitly(self):
        validator = load_validator()
        self.assertTrue(
            hasattr(validator, "validate_reference_ledger"),
            "validator must include reference ledger checks",
        )
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [error for error in errors if error["asset"] == "reference_ledger"],
            errors,
        )

    def test_reference_ledger_rows_have_status_evidence_and_limits(self):
        validator = load_validator()
        self.assertTrue(
            hasattr(validator, "validate_reference_ledger_rows"),
            "validator must check per-reference ledger rows",
        )
        errors = validator.validate_repo(ROOT)
        self.assertFalse(
            [error for error in errors if error["asset"] == "reference_ledger_row"],
            errors,
        )


if __name__ == "__main__":
    unittest.main()
