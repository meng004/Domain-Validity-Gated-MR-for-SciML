from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


TOL = 1e-12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def old_l1_radius(kx: int, ky: int) -> float:
    return abs(kx) + abs(ky)


def corrected_l2_radius(kx: int, ky: int) -> float:
    return math.sqrt(kx**2 + ky**2)


def old_power_after_sum(coefficients: list[complex]) -> float:
    return abs(sum(coefficients)) ** 2


def corrected_power_sum_of_squares(coefficients: list[complex]) -> float:
    return sum(abs(value) ** 2 for value in coefficients)


def build_report(raw_dir: Path) -> dict[str, object]:
    issue = load_json(raw_dir / "neuraloperator_issue_532.json")
    comments = load_json(raw_dir / "neuraloperator_issue_532_comments.json")
    pr = load_json(raw_dir / "neuraloperator_pr_661.json")
    files = load_json(raw_dir / "neuraloperator_pr_661_files.json")

    patch_text = "\n".join(file.get("patch", "") for file in files)
    source_checks = {
        "issue_532_closed": issue.get("state") == "closed",
        "issue_532_url": issue.get("html_url"),
        "issue_532_title": issue.get("title"),
        "maintainer_comment_marks_power_order_as_bug": any(
            "I believe this is a bug" in (comment.get("body") or "")
            for comment in comments
        ),
        "pr_661_merged": bool(pr.get("merged")),
        "pr_661_merged_at": pr.get("merged_at"),
        "pr_661_url": pr.get("html_url"),
        "pr_661_body_addresses_issue_532": "addresses issue #532"
        in (pr.get("body") or ""),
        "patch_replaces_l1_with_l2_radius": "torch.sqrt(k_x**2 + k_y**2)"
        in patch_text
        and "torch.abs(k_x) + torch.abs(k_y)" in patch_text,
        "patch_squares_before_bin_sum": ".abs()**2).sum" in patch_text
        and ".sum(dim=1)).abs() ** 2" in patch_text,
    }

    radial_pair = {
        "source_mode": {"kx": 2, "ky": 0},
        "follow_up_mode": {"kx": 1, "ky": 1},
        "old_l1_radius_source": old_l1_radius(2, 0),
        "old_l1_radius_follow_up": old_l1_radius(1, 1),
        "corrected_l2_radius_source": corrected_l2_radius(2, 0),
        "corrected_l2_radius_follow_up": corrected_l2_radius(1, 1),
    }
    radial_pair["old_l1_bin_collision"] = (
        radial_pair["old_l1_radius_source"] == radial_pair["old_l1_radius_follow_up"]
    )
    radial_pair["corrected_l2_separates_modes"] = abs(
        radial_pair["corrected_l2_radius_source"]
        - radial_pair["corrected_l2_radius_follow_up"]
    ) > TOL

    cancellation_pair = {
        "source_coefficients": [
            {"real": 1.0, "imag": 0.0},
            {"real": -1.0, "imag": 0.0},
        ],
    }
    coefficients = [complex(1.0, 0.0), complex(-1.0, 0.0)]
    cancellation_pair["old_power_after_complex_sum"] = old_power_after_sum(
        coefficients
    )
    cancellation_pair["corrected_sum_of_squared_magnitudes"] = (
        corrected_power_sum_of_squares(coefficients)
    )
    cancellation_pair["old_power_cancels_nonzero_energy"] = (
        cancellation_pair["old_power_after_complex_sum"] <= TOL
        and cancellation_pair["corrected_sum_of_squared_magnitudes"] > 1.0
    )

    verdict_checks = {
        "external_defect_source_complete": all(source_checks.values()),
        "old_l1_radius_collides_distinct_l2_modes": radial_pair[
            "old_l1_bin_collision"
        ]
        and radial_pair["corrected_l2_separates_modes"],
        "old_power_order_cancels_nonzero_energy": cancellation_pair[
            "old_power_cancels_nonzero_energy"
        ],
    }
    verdict = "pass" if all(verdict_checks.values()) else "fail"

    return {
        "run_id": "neuraloperator-spectrum2d-real-defect-witness-001",
        "date": "2026-07-03",
        "subject": "NeuralOperator issue #532 / PR #661 spectrum_2d semantic witness",
        "mr_card": "research_assets/mr_cards/neuraloperator_spectrum2d_radial_power_consistency.json",
        "source_artifacts": {
            path.name: {
                "path": str(path),
                "sha256": sha256_file(path),
            }
            for path in sorted(raw_dir.glob("neuraloperator_issue_532*.json"))
            + sorted(raw_dir.glob("neuraloperator_pr_661*.json"))
            if path.is_file()
        },
        "source_checks": source_checks,
        "source_follow_up_cases": {
            "radial_binning_case": radial_pair,
            "power_accumulation_case": cancellation_pair,
        },
        "metric": {
            "name": "spectrum_2d_radial_power_consistency",
            "tolerance": TOL,
            "old_l1_radius_collision": radial_pair["old_l1_bin_collision"],
            "corrected_l2_radius_gap": abs(
                radial_pair["corrected_l2_radius_source"]
                - radial_pair["corrected_l2_radius_follow_up"]
            ),
            "old_power_after_sum": cancellation_pair["old_power_after_complex_sum"],
            "corrected_power_sum_of_squares": cancellation_pair[
                "corrected_sum_of_squared_magnitudes"
            ],
        },
        "verdict_checks": verdict_checks,
        "typed_verdict": verdict,
        "claim_limitations": (
            "One external issue/PR-linked spectral-metric witness for a "
            "NeuralOperator utility function. It is not a trained-FNO result, "
            "not a neural-operator reliability claim, and not a defect-rate "
            "estimate."
        ),
        "forbidden_claims": [
            "The method validates NeuralOperator model accuracy.",
            "The paper measures NeuralOperator defect prevalence.",
            "The witness proves all spectral utilities are correct.",
            "The witness is a production training workload.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    report = build_report(args.raw_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
