from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Callable


TOL = 1e-12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def endpoint_pair(func: Callable[[float], float]) -> dict[str, float]:
    return {"left_x0": func(0.0), "right_x1": func(1.0)}


def residual(left: float, right: float) -> float:
    return left - right


def case_record(
    case_id: str,
    description: str,
    u: Callable[[float], float],
    dudx: Callable[[float], float],
) -> dict[str, object]:
    value_pair = endpoint_pair(u)
    derivative_pair = endpoint_pair(dudx)
    value_residual = residual(value_pair["left_x0"], value_pair["right_x1"])
    derivative_residual = residual(
        derivative_pair["left_x0"], derivative_pair["right_x1"]
    )
    return {
        "case_id": case_id,
        "description": description,
        "source_boundary_point": {"x": 0.0},
        "follow_up_boundary_point": {"x": 1.0},
        "deepxde_pre_pr27_periodicbc_value_residual": value_residual,
        "deepxde_pr27_derivative_order_0_residual": value_residual,
        "deepxde_pr27_derivative_order_1_residual": derivative_residual,
        "absolute_value_residual": abs(value_residual),
        "absolute_derivative_residual": abs(derivative_residual),
        "value_pair": value_pair,
        "derivative_pair": derivative_pair,
    }


def build_report(raw_dir: Path) -> dict[str, object]:
    issue = load_json(raw_dir / "deepxde_issue_26.json")
    comments = load_json(raw_dir / "deepxde_issue_26_comments.json")
    pr = load_json(raw_dir / "deepxde_pr_27.json")
    commit_search = load_json(raw_dir / "deepxde_periodicbc_commit_search.json")
    patch_path = raw_dir / "deepxde_pr_27.patch"
    patch_text = patch_path.read_text(encoding="utf-8")

    source_checks = {
        "issue_26_closed": issue.get("state") == "closed",
        "issue_26_url": issue.get("html_url"),
        "issue_26_title": issue.get("title"),
        "pr_27_merged": bool(pr.get("merged")),
        "pr_27_merged_at": pr.get("merged_at"),
        "pr_27_url": pr.get("html_url"),
        "merge_commit_sha": pr.get("merge_commit_sha"),
        "patch_adds_derivative_order_argument": "derivative_order=0" in patch_text,
        "patch_adds_derivative_order_1_branch": "self.derivative_order == 0" in patch_text
        and "tf.gradients" in patch_text,
        "commit_search_contains_periodicbc_support_commit": any(
            item.get("sha") == pr.get("merge_commit_sha")
            and "PeriodicBC supports first order derivative"
            in item.get("commit", {}).get("message", "")
            for item in commit_search.get("items", [])
        ),
        "owner_comment_promises_derivative_periodic_bc": any(
            comment.get("user", {}).get("login") == "lululxvi"
            and "u'(0)=u'(1)" in comment.get("body", "")
            and "implement another periodic BC" in comment.get("body", "")
            for comment in comments
        ),
    }

    cases = [
        case_record(
            "value_periodic_derivative_mismatch",
            "u=x(1-x) has equal endpoint values but unequal endpoint derivatives.",
            lambda x: x * (1.0 - x),
            lambda x: 1.0 - 2.0 * x,
        ),
        case_record(
            "smooth_periodic_control",
            "u=sin(2*pi*x) has equal endpoint values and equal endpoint derivatives.",
            lambda x: math.sin(2.0 * math.pi * x),
            lambda x: 2.0 * math.pi * math.cos(2.0 * math.pi * x),
        ),
        case_record(
            "value_nonperiodic_control",
            "u=x violates value periodicity while satisfying equal endpoint derivative.",
            lambda x: x,
            lambda x: 1.0,
        ),
    ]
    case_by_id = {case["case_id"]: case for case in cases}
    mismatch = case_by_id["value_periodic_derivative_mismatch"]
    periodic = case_by_id["smooth_periodic_control"]
    nonperiodic = case_by_id["value_nonperiodic_control"]

    verdict_checks = {
        "external_defect_source_complete": all(source_checks.values()),
        "pre_pr27_value_only_residual_is_blind_on_derivative_mismatch": mismatch[
            "absolute_value_residual"
        ]
        <= TOL,
        "pr27_derivative_order_1_detects_derivative_mismatch": mismatch[
            "absolute_derivative_residual"
        ]
        > 1.0,
        "smooth_periodic_control_passes_value_and_derivative": periodic[
            "absolute_value_residual"
        ]
        <= TOL
        and periodic["absolute_derivative_residual"] <= TOL,
        "value_nonperiodic_control_fails_value_periodicity": nonperiodic[
            "absolute_value_residual"
        ]
        > 1.0 - TOL,
    }
    verdict = "pass" if all(verdict_checks.values()) else "fail"

    return {
        "run_id": "deepxde-periodicbc-real-defect-witness-001",
        "date": "2026-07-03",
        "subject": "DeepXDE PeriodicBC issue #26 / PR #27 semantic witness",
        "mr_card": "research_assets/mr_cards/deepxde_periodicbc_derivative_enforcement.json",
        "source_artifacts": {
            path.name: {
                "path": str(path),
                "sha256": sha256_file(path),
            }
            for path in sorted(raw_dir.glob("*"))
            if path.is_file()
        },
        "source_checks": source_checks,
        "source_follow_up_cases": cases,
        "metric": {
            "name": "periodic_boundary_derivative_residual",
            "tolerance": TOL,
            "primary_case": "value_periodic_derivative_mismatch",
            "pre_pr27_value_only_abs_residual": mismatch["absolute_value_residual"],
            "pr27_derivative_order_1_abs_residual": mismatch[
                "absolute_derivative_residual"
            ],
        },
        "verdict_checks": verdict_checks,
        "typed_verdict": verdict,
        "claim_limitations": (
            "One external issue/PR-linked boundary-condition witness for a SciML "
            "library component. It is not a trained-surrogate result, not a "
            "defect-detection rate, and not evidence that all DeepXDE or PINN "
            "periodic boundary conditions are correct."
        ),
        "forbidden_claims": [
            "The paper measures a real-world defect-detection rate.",
            "The method detects all DeepXDE periodic-boundary defects.",
            "This witness validates trained PINN accuracy or reliability.",
            "This witness establishes production CFD readiness.",
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
