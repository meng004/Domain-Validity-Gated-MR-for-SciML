from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MR_CARD_REQUIRED = {
    "mr_id",
    "title",
    "status",
    "evidence_level",
    "source_case_schema",
    "follow_up_transformation",
    "transformation_preconditions",
    "boundary_condition_compatibility",
    "output_mapping",
    "metric",
    "tolerance",
    "exclusion_rules",
    "allowed_verdicts",
    "verdict_interpretation",
    "claim_limitations",
}

CANDIDATE_LEDGER_REQUIRED = {
    "ledger_id",
    "evidence_level",
    "entries",
    "claim_limitations",
}

DOMAIN_VALIDITY_RUBRIC_REQUIRED = {
    "rubric_id",
    "evidence_level",
    "dimensions",
    "allowed_decisions",
    "claim_limitations",
}

CANDIDATE_ENTRY_REQUIRED = {
    "candidate_id",
    "mr_id",
    "title",
    "decision",
    "rubric_decision",
    "decision_basis",
    "rubric_reasons",
    "evidence_reference",
    "claim_limitations",
}

ALLOWED_VERDICTS = {
    "pass",
    "fail",
    "skip",
    "out-of-relation-domain",
    "numerical-tolerance-issue",
    "inconclusive",
}

ALLOWED_MR_CARD_EVIDENCE_LEVELS = {
    "design-time-asset",
    "design-time-candidate",
}

ALLOWED_CANDIDATE_DECISIONS = {
    "retained-design-time",
    "retained-ood-stress",
    "rejected-design-time",
    "deferred",
    "downgraded-to-diagnostic",
}

REFERENCE_KEYS = {
    "qi2025physicalfield",
    "yu2025fluidvelocity",
    "zhao2026noether",
    "hiremath2021ocean",
    "mandrioli2025cps",
    "baral2025xrepit",
    "wang2025deeponetfe",
}

REFERENCE_STATUS_MARKERS = {"VERIFIED", "PARTIAL", "UNVERIFIED"}


def error(asset: str, path: Path, message: str) -> dict[str, str]:
    return {"asset": asset, "path": str(path), "message": message}


def read_json(path: Path, asset: str) -> tuple[Any | None, list[dict[str, str]]]:
    if not path.exists():
        return None, [error(asset, path, "missing file")]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [error(asset, path, f"invalid JSON: {exc}")]


def require_keys(
    data: dict[str, Any], required: set[str], asset: str, path: Path
) -> list[dict[str, str]]:
    return [
        error(asset, path, f"missing key: {key}")
        for key in sorted(required - set(data))
    ]


def is_non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_mr_card_evidence_contract(
    data: dict[str, Any], path: Path
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    evidence_level = data.get("evidence_level")
    status = data.get("status")
    tolerance = data.get("tolerance")
    threshold = tolerance.get("threshold") if isinstance(tolerance, dict) else None
    verdicts = set(data.get("allowed_verdicts", []))

    if evidence_level == "design-time-asset":
        if not is_number(threshold):
            errors.append(
                error(
                    "mr_card",
                    path,
                    "design-time asset threshold must be numeric",
                )
            )
        if "pass" not in verdicts or "fail" not in verdicts:
            errors.append(
                error(
                    "mr_card",
                    path,
                    "design-time asset allowed_verdicts must include pass and fail",
                )
            )

    if evidence_level == "design-time-candidate":
        if status not in {"design-time-deferred", "design-time-downgraded-to-diagnostic"}:
            errors.append(
                error(
                    "mr_card",
                    path,
                    "design-time candidate status must remain deferred or downgraded",
                )
            )
        if threshold is not None:
            errors.append(
                error(
                    "mr_card",
                    path,
                    "design-time candidate threshold must remain uncalibrated",
                )
            )
        if "pass" in verdicts or "fail" in verdicts:
            errors.append(
                error(
                    "mr_card",
                    path,
                    "design-time candidate cannot carry pass/fail verdicts",
                )
            )
    return errors


def validate_single_mr_card(path: Path) -> list[dict[str, str]]:
    data, errors = read_json(path, "mr_card")
    if errors:
        return errors
    if not isinstance(data, dict):
        return [error("mr_card", path, "top-level value must be object")]

    errors.extend(require_keys(data, MR_CARD_REQUIRED, "mr_card", path))
    if errors:
        return errors

    if data["evidence_level"] not in ALLOWED_MR_CARD_EVIDENCE_LEVELS:
        errors.append(
            error("mr_card", path, "evidence_level must be design-time asset/candidate")
        )
    if not isinstance(data["allowed_verdicts"], list):
        errors.append(error("mr_card", path, "allowed_verdicts must be a list"))
    else:
        verdicts = set(data["allowed_verdicts"])
        if not verdicts:
            errors.append(error("mr_card", path, "allowed_verdicts must not be empty"))
        if not verdicts.issubset(ALLOWED_VERDICTS):
            errors.append(
                error("mr_card", path, "allowed_verdicts must be known classes")
            )
    if data.get("empirical_result") is not None:
        errors.append(
            error("mr_card", path, "empirical_result must be absent until SUT runs exist")
        )
    if not is_non_empty_text(data["claim_limitations"]):
        errors.append(error("mr_card", path, "claim_limitations must be non-empty text"))
    errors.extend(validate_mr_card_evidence_contract(data, path))
    return errors


def validate_all_mr_cards(root: Path) -> list[dict[str, str]]:
    card_dir = root / "research_assets" / "mr_cards"
    paths = sorted(card_dir.glob("*.json"))
    if len(paths) < 3:
        return [error("mr_card", card_dir, "expected at least three MR cards")]

    errors: list[dict[str, str]] = []
    for path in paths:
        errors.extend(validate_single_mr_card(path))
    return errors


def validate_mr_card(root: Path) -> list[dict[str, str]]:
    return validate_all_mr_cards(root)


def validate_candidate_ledger(root: Path) -> list[dict[str, str]]:
    path = root / "research_assets" / "ledgers" / "candidate_ledger.json"
    data, errors = read_json(path, "candidate_ledger")
    if errors:
        return errors
    if not isinstance(data, dict):
        return [error("candidate_ledger", path, "top-level value must be object")]

    errors.extend(
        require_keys(data, CANDIDATE_LEDGER_REQUIRED, "candidate_ledger", path)
    )
    if errors:
        return errors

    if data["evidence_level"] != "design-time-ledger":
        errors.append(
            error(
                "candidate_ledger",
                path,
                "evidence_level must be design-time-ledger",
            )
        )

    entries = data["entries"]
    if not isinstance(entries, list) or not entries:
        errors.append(error("candidate_ledger", path, "entries must be a non-empty list"))
        return errors

    for index, entry_data in enumerate(entries):
        if not isinstance(entry_data, dict):
            errors.append(
                error("candidate_ledger", path, f"entry {index} must be object")
            )
            continue
        errors.extend(
            require_keys(entry_data, CANDIDATE_ENTRY_REQUIRED, "candidate_ledger", path)
        )
        if entry_data.get("decision") not in ALLOWED_CANDIDATE_DECISIONS:
            errors.append(
                error(
                    "candidate_ledger",
                    path,
                    f"entry {index} decision must be evidence-bounded",
                )
            )
        if entry_data.get("rubric_decision") != entry_data.get("decision"):
            errors.append(
                error(
                    "candidate_ledger",
                    path,
                    f"entry {index} rubric_decision must match decision",
                )
            )
        rubric_reasons = entry_data.get("rubric_reasons")
        if not isinstance(rubric_reasons, list) or not rubric_reasons:
            errors.append(
                error(
                    "candidate_ledger",
                    path,
                    f"entry {index} rubric_reasons must be non-empty list",
                )
            )
        else:
            for reason_index, reason in enumerate(rubric_reasons):
                if not is_non_empty_text(reason):
                    errors.append(
                        error(
                            "candidate_ledger",
                            path,
                            f"entry {index} rubric_reasons {reason_index} must be non-empty text",
                        )
                    )
        if entry_data.get("empirical_result") is not None:
            errors.append(
                error(
                    "candidate_ledger",
                    path,
                    f"entry {index} empirical_result must be absent until SUT runs exist",
                )
            )
    return errors


def validate_domain_validity_rubric(root: Path) -> list[dict[str, str]]:
    path = root / "research_assets" / "rubric" / "domain_validity_rubric.json"
    data, errors = read_json(path, "domain_validity_rubric")
    if errors:
        return errors
    if not isinstance(data, dict):
        return [error("domain_validity_rubric", path, "top-level value must be object")]

    errors.extend(
        require_keys(data, DOMAIN_VALIDITY_RUBRIC_REQUIRED, "domain_validity_rubric", path)
    )
    if errors:
        return errors

    if data["evidence_level"] != "design-time-rubric":
        errors.append(
            error(
                "domain_validity_rubric",
                path,
                "evidence_level must be design-time-rubric",
            )
        )
    dimensions = data["dimensions"]
    if not isinstance(dimensions, list) or not dimensions:
        errors.append(
            error("domain_validity_rubric", path, "dimensions must be non-empty list")
        )
    elif not all(is_non_empty_text(dimension) for dimension in dimensions):
        errors.append(
            error(
                "domain_validity_rubric",
                path,
                "dimensions must contain non-empty text",
            )
        )

    allowed_decisions = data["allowed_decisions"]
    if not isinstance(allowed_decisions, list) or not allowed_decisions:
        errors.append(
            error(
                "domain_validity_rubric",
                path,
                "allowed_decisions must be non-empty list",
            )
        )
    else:
        allowed_set = set(allowed_decisions)
        if allowed_set != ALLOWED_CANDIDATE_DECISIONS:
            errors.append(
                error(
                    "domain_validity_rubric",
                    path,
                    "allowed_decisions must match validator decision classes",
                )
            )
    if not is_non_empty_text(data["claim_limitations"]):
        errors.append(
            error(
                "domain_validity_rubric",
                path,
                "claim_limitations must be non-empty text",
            )
        )
    return errors


def validate_rubric_decision_coverage(root: Path) -> list[dict[str, str]]:
    rubric_path = root / "research_assets" / "rubric" / "domain_validity_rubric.json"
    ledger_path = root / "research_assets" / "ledgers" / "candidate_ledger.json"
    rubric, errors = read_json(rubric_path, "rubric_decision_coverage")
    ledger, ledger_errors = read_json(ledger_path, "rubric_decision_coverage")
    errors.extend(ledger_errors)
    if errors:
        return errors
    if not isinstance(rubric, dict):
        return [error("rubric_decision_coverage", rubric_path, "rubric must be object")]
    if not isinstance(ledger, dict):
        return [error("rubric_decision_coverage", ledger_path, "ledger must be object")]

    allowed_decisions = rubric.get("allowed_decisions")
    if not isinstance(allowed_decisions, list):
        return [
            error(
                "rubric_decision_coverage",
                rubric_path,
                "rubric allowed_decisions must be list",
            )
        ]
    allowed_set = set(allowed_decisions)

    entries = ledger.get("entries")
    if not isinstance(entries, list):
        return [error("rubric_decision_coverage", ledger_path, "entries must be list")]

    required = {
        "retained-design-time",
        "retained-ood-stress",
        "deferred",
        "rejected-design-time",
    }
    decisions = set()
    for entry_index, entry_data in enumerate(entries):
        if not isinstance(entry_data, dict):
            continue
        decision = entry_data.get("decision")
        if decision not in allowed_set:
            errors.append(
                error(
                    "rubric_decision_coverage",
                    ledger_path,
                    f"entry {entry_index} decision must be allowed by rubric",
                )
            )
        else:
            decisions.add(decision)

    for decision in sorted(required - decisions):
        errors.append(
            error(
                "rubric_decision_coverage",
                ledger_path,
                f"missing decision class: {decision}",
            )
        )
    return errors


def validate_candidate_evidence_references(root: Path) -> list[dict[str, str]]:
    path = root / "research_assets" / "ledgers" / "candidate_ledger.json"
    data, errors = read_json(path, "candidate_evidence")
    if errors:
        return errors
    if not isinstance(data, dict):
        return [error("candidate_evidence", path, "top-level value must be object")]

    entries = data.get("entries")
    if not isinstance(entries, list):
        return [error("candidate_evidence", path, "entries must be a list")]

    for entry_index, entry_data in enumerate(entries):
        if not isinstance(entry_data, dict):
            continue
        references = entry_data.get("evidence_reference")
        if not isinstance(references, list) or not references:
            errors.append(
                error(
                    "candidate_evidence",
                    path,
                    f"entry {entry_index} evidence_reference must be non-empty list",
                )
            )
            continue
        for ref_index, reference in enumerate(references):
            if not isinstance(reference, dict):
                errors.append(
                    error(
                        "candidate_evidence",
                        path,
                        f"entry {entry_index} reference {ref_index} must be object",
                    )
                )
                continue
            ref_path_value = reference.get("path")
            if not is_non_empty_text(ref_path_value):
                errors.append(
                    error(
                        "candidate_evidence",
                        path,
                        f"entry {entry_index} reference {ref_index} path must be non-empty",
                    )
                )
                continue
            ref_path = root / ref_path_value
            if not ref_path.exists():
                errors.append(
                    error(
                        "candidate_evidence",
                        path,
                        f"entry {entry_index} reference {ref_index} path missing: {ref_path_value}",
                    )
                )
                continue

            fields = reference.get("fields", [])
            local_markers = reference.get("local_markers", [])
            has_fields = isinstance(fields, list) and any(
                is_non_empty_text(field) for field in fields
            )
            has_markers = isinstance(local_markers, list) and any(
                is_non_empty_text(marker) for marker in local_markers
            )
            if not has_fields and not has_markers:
                errors.append(
                    error(
                        "candidate_evidence",
                        path,
                        f"entry {entry_index} reference {ref_index} must name fields or local_markers",
                    )
                )
                continue
            if not isinstance(fields, list) or not all(
                is_non_empty_text(field) for field in fields
            ):
                errors.append(
                    error(
                        "candidate_evidence",
                        path,
                        f"entry {entry_index} reference {ref_index} fields must be non-empty text list when present",
                    )
                )
            if not isinstance(local_markers, list) or not all(
                is_non_empty_text(marker) for marker in local_markers
            ):
                errors.append(
                    error(
                        "candidate_evidence",
                        path,
                        f"entry {entry_index} reference {ref_index} local_markers must be non-empty text list when present",
                    )
                )

            text = ref_path.read_text(encoding="utf-8")
            for marker in local_markers:
                if marker not in text:
                    errors.append(
                        error(
                            "candidate_evidence",
                            path,
                            f"entry {entry_index} marker missing in {ref_path_value}: {marker}",
                        )
                    )
            if ref_path.suffix == ".json":
                ref_data, ref_errors = read_json(ref_path, "candidate_evidence")
                errors.extend(ref_errors)
                if isinstance(ref_data, dict):
                    for field in fields:
                        if field not in ref_data:
                            errors.append(
                                error(
                                    "candidate_evidence",
                                    path,
                                    f"entry {entry_index} field missing in {ref_path_value}: {field}",
                                )
                            )
    return errors


def validate_verdict_ledger(root: Path) -> list[dict[str, str]]:
    schema_path = root / "research_assets" / "ledgers" / "verdict_ledger.schema.json"
    example_path = root / "research_assets" / "ledgers" / "verdict_ledger.example.json"
    schema, errors = read_json(schema_path, "verdict_ledger")
    example, example_errors = read_json(example_path, "verdict_ledger")
    errors.extend(example_errors)
    if errors:
        return errors
    if not isinstance(schema, dict):
        errors.append(error("verdict_ledger", schema_path, "schema must be object"))
    if not isinstance(example, dict):
        errors.append(error("verdict_ledger", example_path, "example must be object"))
    if errors:
        return errors

    properties = schema.get("properties")
    if not isinstance(properties, dict) or "entries" not in properties:
        errors.append(
            error("verdict_ledger", schema_path, "schema must define entries property")
        )
    if example.get("evidence_level") != "schema-example-no-runs":
        errors.append(
            error(
                "verdict_ledger",
                example_path,
                "example must declare schema-example-no-runs",
            )
        )
    if example.get("entries") != []:
        errors.append(
            error(
                "verdict_ledger",
                example_path,
                "example entries must be empty until runs exist",
            )
        )
    return errors


def validate_verdict_schema_contract(root: Path) -> list[dict[str, str]]:
    path = root / "research_assets" / "ledgers" / "verdict_ledger.schema.json"
    schema, errors = read_json(path, "verdict_schema_contract")
    if errors:
        return errors
    if not isinstance(schema, dict):
        return [error("verdict_schema_contract", path, "schema must be object")]

    required_top = {
        "ledger_id",
        "evidence_level",
        "schema_version",
        "claim_limitations",
        "entries",
    }
    if set(schema.get("required", [])) != required_top:
        errors.append(
            error(
                "verdict_schema_contract",
                path,
                "top-level required fields must match ledger contract",
            )
        )
    if schema.get("additionalProperties") is not False:
        errors.append(
            error(
                "verdict_schema_contract",
                path,
                "top-level additionalProperties must be false",
            )
        )

    entries = schema.get("properties", {}).get("entries", {})
    item_schema = entries.get("items", {}) if isinstance(entries, dict) else {}
    required_item = {
        "run_id",
        "mr_id",
        "source_case_id",
        "follow_up_case_id",
        "verdict",
        "metric",
        "tolerance",
        "evidence_artifact",
    }
    if set(item_schema.get("required", [])) != required_item:
        errors.append(
            error(
                "verdict_schema_contract",
                path,
                "entry required fields must match runtime verdict contract",
            )
        )
    if item_schema.get("additionalProperties") is not False:
        errors.append(
            error(
                "verdict_schema_contract",
                path,
                "entry additionalProperties must be false",
            )
        )
    verdict_enum = (
        item_schema.get("properties", {}).get("verdict", {}).get("enum", [])
        if isinstance(item_schema, dict)
        else []
    )
    if set(verdict_enum) != ALLOWED_VERDICTS:
        errors.append(
            error(
                "verdict_schema_contract",
                path,
                "verdict enum must match allowed verdict classes",
            )
        )
    return errors


def validate_reference_ledger(root: Path) -> list[dict[str, str]]:
    path = root / "paper" / "reference_ledger.md"
    if not path.exists():
        return [error("reference_ledger", path, "missing file")]

    text = path.read_text(encoding="utf-8")
    errors: list[dict[str, str]] = []

    for marker in ["| Key |", "| Verification status |", "| Evidence sources |"]:
        if marker not in text:
            errors.append(error("reference_ledger", path, f"missing table marker: {marker}"))

    for status in REFERENCE_STATUS_MARKERS:
        if status not in text:
            errors.append(error("reference_ledger", path, f"missing status marker: {status}"))

    for key in sorted(REFERENCE_KEYS):
        if f"`{key}`" not in text:
            errors.append(error("reference_ledger", path, f"missing key: {key}"))

    guardrail_markers = [
        "Do not claim this paper is the first physics-based metamorphic testing work",
        "Do not treat NOETHER as a peer-reviewed validity proof",
        "Do not cite any key with PARTIAL status",
    ]
    for marker in guardrail_markers:
        if marker not in text:
            errors.append(
                error("reference_ledger", path, f"missing guardrail marker: {marker}")
            )

    return errors


def reference_ledger_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("| `"):
            continue
        columns = [column.strip() for column in line.strip("|").split("|")]
        if len(columns) >= 5:
            key = columns[0].strip("`")
            rows[key] = columns
    return rows


def validate_reference_ledger_rows(root: Path) -> list[dict[str, str]]:
    path = root / "paper" / "reference_ledger.md"
    if not path.exists():
        return [error("reference_ledger_row", path, "missing file")]

    rows = reference_ledger_rows(path.read_text(encoding="utf-8"))
    errors: list[dict[str, str]] = []
    for key in sorted(REFERENCE_KEYS):
        columns = rows.get(key)
        if columns is None:
            errors.append(error("reference_ledger_row", path, f"missing row: {key}"))
            continue
        if len(columns) < 5:
            errors.append(error("reference_ledger_row", path, f"row too short: {key}"))
            continue
        status = columns[1]
        facts = columns[2]
        sources = columns[3]
        limits = columns[4]
        if status not in REFERENCE_STATUS_MARKERS:
            errors.append(
                error("reference_ledger_row", path, f"invalid status for {key}: {status}")
            )
        if not facts or facts == "-":
            errors.append(
                error("reference_ledger_row", path, f"missing observed facts for {key}")
            )
        if not sources or sources == "-":
            errors.append(
                error("reference_ledger_row", path, f"missing evidence sources for {key}")
            )
        if not limits or limits == "-":
            errors.append(
                error("reference_ledger_row", path, f"missing claim support limits for {key}")
            )
    return errors


def validate_repo(root: Path) -> list[dict[str, str]]:
    root = Path(root)
    errors: list[dict[str, str]] = []
    errors.extend(validate_mr_card(root))
    errors.extend(validate_domain_validity_rubric(root))
    errors.extend(validate_candidate_ledger(root))
    errors.extend(validate_candidate_evidence_references(root))
    errors.extend(validate_rubric_decision_coverage(root))
    errors.extend(validate_verdict_ledger(root))
    errors.extend(validate_verdict_schema_contract(root))
    errors.extend(validate_reference_ledger(root))
    errors.extend(validate_reference_ledger_rows(root))
    return errors


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    failures = validate_repo(repo_root)
    for failure in failures:
        print(f"{failure['asset']}: {failure['path']}: {failure['message']}")
    raise SystemExit(1 if failures else 0)
