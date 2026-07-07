from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class NamedDense2D:
    def __init__(self, values: list[list[float]], names: tuple[str, str]):
        self.values = values
        self.names = names

    def native(self, requested_names: tuple[str, str]) -> list[list[float]]:
        if requested_names == self.names:
            return self.values
        if requested_names == (self.names[1], self.names[0]):
            return [list(row) for row in zip(*self.values)]
        raise ValueError(f"unsupported requested order {requested_names}")

    def old_natives_without_requested_names(self) -> list[list[list[float]]]:
        return [self.values]


def shape2d(values: list[list[float]]) -> list[int]:
    return [len(values), len(values[0]) if values else 0]


def build_report(raw_dir: Path) -> dict[str, object]:
    issue = load_json(raw_dir / "phiflow_issue_199.json")
    comments = load_json(raw_dir / "phiflow_issue_199_comments.json")
    commit = load_json(
        raw_dir / "phiml_commit_96ef3e4d8376502a1b75dcdd799d9ada1cb39f72.json"
    )
    patch_text = "\n".join(file.get("patch", "") for file in commit.get("files", []))

    source_checks = {
        "phiflow_issue_199_closed": issue.get("state") == "closed",
        "phiflow_issue_199_url": issue.get("html_url"),
        "maintainer_comment_links_phiml_fix_commit": any(
            "96ef3e4d8376502a1b75dcdd799d9ada1cb39f72"
            in (comment.get("body") or "")
            and "custom gradients" in (comment.get("body") or "")
            for comment in comments
        ),
        "commit_url": commit.get("html_url"),
        "commit_message_mentions_transposed_custom_gradients": (
            "Fix incorrectly transposed custom gradients"
            in commit.get("commit", {}).get("message", "")
        ),
        "patch_replaces_shapes_with_specs": "list(in_key.specs)" in patch_text
        and "list(in_key.shapes)" in patch_text,
        "patch_handles_dense_native_names": "isinstance(incomplete, Dense)"
        in patch_text
        and "incomplete.native(c_spec['names'])" in patch_text,
        "patch_warns_about_incorrectly_transposed_gradients": (
            "incorrectly transposed gradients" in patch_text
        ),
    }

    gradient = NamedDense2D([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], ("y", "x"))
    expected_names = ("x", "y")
    old_native = gradient.old_natives_without_requested_names()[0]
    corrected_native = gradient.native(expected_names)
    expected_native = [[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]]

    source_follow_up = {
        "gradient_tensor": {
            "names": list(gradient.names),
            "values": gradient.values,
        },
        "requested_input_names": list(expected_names),
        "old_native_without_requested_names": old_native,
        "corrected_native_with_requested_names": corrected_native,
        "expected_native": expected_native,
    }

    verdict_checks = {
        "external_fix_source_complete": all(source_checks.values()),
        "old_native_keeps_wrong_axis_order": old_native != expected_native
        and shape2d(old_native) == [2, 3],
        "corrected_native_transposes_to_requested_names": corrected_native
        == expected_native
        and shape2d(corrected_native) == [3, 2],
    }
    verdict = "pass" if all(verdict_checks.values()) else "fail"

    return {
        "run_id": "phiml-custom-gradient-transpose-real-defect-witness-001",
        "date": "2026-07-03",
        "subject": "PhiFlow issue #199 / PhiML commit custom-gradient transpose witness",
        "mr_card": "research_assets/mr_cards/phiml_custom_gradient_transpose_consistency.json",
        "source_artifacts": {
            path.name: {
                "path": str(path),
                "sha256": sha256_file(path),
            }
            for path in [
                raw_dir / "phiflow_issue_199.json",
                raw_dir / "phiflow_issue_199_comments.json",
                raw_dir
                / "phiml_commit_96ef3e4d8376502a1b75dcdd799d9ada1cb39f72.json",
            ]
            if path.is_file()
        },
        "source_checks": source_checks,
        "source_follow_up_cases": source_follow_up,
        "metric": {
            "name": "custom_gradient_native_axis_order_consistency",
            "old_native_shape": shape2d(old_native),
            "corrected_native_shape": shape2d(corrected_native),
            "expected_native_shape": shape2d(expected_native),
            "old_matches_expected": old_native == expected_native,
            "corrected_matches_expected": corrected_native == expected_native,
        },
        "verdict_checks": verdict_checks,
        "typed_verdict": verdict,
        "claim_limitations": (
            "One external issue/commit-linked semantic witness for PhiML custom "
            "gradient native-axis ordering. It is not a full PhiFlow simulation "
            "result, not an automatic-differentiation benchmark, and not a "
            "defect-rate estimate."
        ),
        "forbidden_claims": [
            "The method validates PhiFlow flow-past-obstacle simulations.",
            "The paper measures PhiML or PhiFlow defect prevalence.",
            "The witness proves all custom gradients are correct.",
            "The witness is a production CFD workload.",
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
