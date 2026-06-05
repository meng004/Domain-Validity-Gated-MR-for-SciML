from __future__ import annotations

import json
from math import sqrt
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_permutation(permutation: list[int], size: int) -> None:
    expected = set(range(size))
    observed = set(permutation)
    if len(permutation) != size or observed != expected:
        raise ValueError("permutation must be a bijection over node indices")


def validate_inverse_permutation(
    permutation: list[int], inverse_permutation: list[int]
) -> None:
    validate_permutation(permutation, len(permutation))
    validate_permutation(inverse_permutation, len(permutation))
    for new_index, old_index in enumerate(permutation):
        if inverse_permutation[old_index] != new_index:
            raise ValueError("inverse_permutation is inconsistent with permutation")


def validate_face_indices(face: list[list[int]], node_count: int) -> None:
    for cell in face:
        for node_index in cell:
            if not isinstance(node_index, int) or node_index < 0 or node_index >= node_count:
                raise ValueError("face contains node index outside permutation domain")


def apply_permutation(values: list[Any], permutation: list[int]) -> list[Any]:
    validate_permutation(permutation, len(values))
    return [values[index] for index in permutation]


def inverse_permute(values: list[Any], inverse_permutation: list[int]) -> list[Any]:
    validate_permutation(inverse_permutation, len(values))
    return [values[index] for index in inverse_permutation]


def permute_face(face: list[list[int]], inverse_permutation: list[int]) -> list[list[int]]:
    validate_face_indices(face, len(inverse_permutation))
    return [[inverse_permutation[node_index] for node_index in cell] for cell in face]


def relative_l2(left: list[list[float]], right: list[list[float]]) -> float:
    numerator = 0.0
    denominator = 0.0
    for left_row, right_row in zip(left, right, strict=True):
        for left_value, right_value in zip(left_row, right_row, strict=True):
            numerator += (left_value - right_value) ** 2
            denominator += right_value ** 2
    if denominator == 0.0:
        return 0.0 if numerator == 0.0 else float("inf")
    return sqrt(numerator) / sqrt(denominator)


def run_node_permutation_fixture(root: Path) -> dict[str, Any]:
    root = Path(root)
    fixture_path = root / "research_assets" / "fixtures" / "node_permutation_case.json"
    card_path = root / "research_assets" / "mr_cards" / "node_permutation_equivariance.json"
    output_path = root / "research_assets" / "runs" / "node_permutation_fixture_verdict.json"

    fixture = load_json(fixture_path)
    card = load_json(card_path)

    validate_inverse_permutation(fixture["permutation"], fixture["inverse_permutation"])
    transformed_graph = {
        "x": apply_permutation(fixture["x"], fixture["permutation"]),
        "pos": apply_permutation(fixture["pos"], fixture["permutation"]),
        "face": permute_face(fixture["face"], fixture["inverse_permutation"]),
    }
    restored_follow_up = inverse_permute(
        fixture["y_follow_up_permuted"], fixture["inverse_permutation"]
    )
    value = relative_l2(restored_follow_up, fixture["y_source"])
    threshold = float(card["tolerance"]["threshold"])
    verdict = "pass" if value <= threshold else "fail"

    entry = {
        "run_id": "fixture-node-permutation-run-001",
        "mr_id": fixture["mr_id"],
        "source_case_id": fixture["case_id"],
        "follow_up_case_id": fixture["case_id"] + "-permuted",
        "execution_profile": "fixture-transform-metric-only",
        "sut_execution": "not-run",
        "verdict": verdict,
        "metric": {"name": card["metric"]["name"], "value": value},
        "tolerance": card["tolerance"],
        "evidence_artifact": str(fixture_path.relative_to(root)),
        "transformed_graph": transformed_graph,
    }

    ledger = {
        "ledger_id": "node-permutation-fixture-verdict-ledger",
        "evidence_level": "fixture-transform-metric-only",
        "schema_version": "0.2.0",
        "claim_limitations": (
            "This ledger records a fixture-level asset execution path. It does not "
            "report MeshGraphNets inference, SUT reliability, violation rates, or "
            "empirical pass/fail rates."
        ),
        "entries": [entry],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return entry


if __name__ == "__main__":
    run_node_permutation_fixture(Path(__file__).resolve().parents[1])
