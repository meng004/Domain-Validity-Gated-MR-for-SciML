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


def old_flux_bc_inherits_scalar(scalar_bc: tuple[str, str]) -> tuple[str, str]:
    return scalar_bc


def corrected_flux_bc_from_velocity(
    velocity_bc: tuple[str, str],
    scalar_bc: tuple[str, str],
    flux_direction: int,
    axis: int,
) -> tuple[str, str]:
    del scalar_bc
    if velocity_bc == ("periodic", "periodic"):
        return ("periodic", "periodic")
    if flux_direction != axis:
        return ("dirichlet", "dirichlet")
    if velocity_bc == ("dirichlet_zero", "dirichlet_zero"):
        return ("dirichlet", "dirichlet")
    raise NotImplementedError("unsupported flux boundary witness case")


def case_record(
    case_id: str,
    description: str,
    velocity_bc: tuple[str, str],
    scalar_bc: tuple[str, str],
    flux_direction: int,
    axis: int,
    expected_flux_bc: tuple[str, str],
) -> dict[str, object]:
    old_bc = old_flux_bc_inherits_scalar(scalar_bc)
    corrected_bc = corrected_flux_bc_from_velocity(
        velocity_bc, scalar_bc, flux_direction, axis
    )
    return {
        "case_id": case_id,
        "description": description,
        "velocity_bc": list(velocity_bc),
        "scalar_bc": list(scalar_bc),
        "flux_direction": flux_direction,
        "axis": axis,
        "old_flux_bc": list(old_bc),
        "corrected_flux_bc": list(corrected_bc),
        "expected_flux_bc": list(expected_flux_bc),
        "old_matches_expected": old_bc == expected_flux_bc,
        "corrected_matches_expected": corrected_bc == expected_flux_bc,
    }


def build_report(raw_dir: Path) -> dict[str, object]:
    pr = load_json(raw_dir / "jaxcfd_pr_167.json")
    files = load_json(raw_dir / "jaxcfd_pr_167_files.json")
    patch_text = "\n".join(file.get("patch", "") for file in files)

    source_checks = {
        "pr_167_merged": bool(pr.get("merged")),
        "pr_167_merged_at": pr.get("merged_at"),
        "pr_167_url": pr.get("html_url"),
        "pr_body_states_flux_bc_inferred_from_velocity": (
            "Advection flux boundary condition is now correctly inferred from "
            "the velocity boundary conditions"
        )
        in (pr.get("body") or ""),
        "patch_adds_flux_bc_inference_function": (
            "def get_advection_flux_bc_from_velocity_and_scalar" in patch_text
        ),
        "patch_replaces_scalar_bc_inheritance": (
            "Flux inherits boundary conditions from cs" in patch_text
            and "get_advection_flux_bc_from_velocity_and_scalar" in patch_text
        ),
        "patch_imposes_inferred_flux_bc": ".impose_bc(" in patch_text,
    }

    cases = [
        case_record(
            "normal_no_penetration_scalar_neumann",
            "For a nonporous wall, normal advection flux should be homogeneous Dirichlet even when the advected scalar has Neumann boundary conditions.",
            velocity_bc=("dirichlet_zero", "dirichlet_zero"),
            scalar_bc=("neumann", "neumann"),
            flux_direction=0,
            axis=0,
            expected_flux_bc=("dirichlet", "dirichlet"),
        ),
        case_record(
            "periodic_control",
            "Periodic velocity boundaries should keep the flux periodic.",
            velocity_bc=("periodic", "periodic"),
            scalar_bc=("periodic", "periodic"),
            flux_direction=0,
            axis=0,
            expected_flux_bc=("periodic", "periodic"),
        ),
        case_record(
            "tangential_wall_control",
            "Flux boundaries parallel to a nonperiodic wall are homogeneous Dirichlet in the corrected implementation.",
            velocity_bc=("dirichlet_zero", "dirichlet_zero"),
            scalar_bc=("neumann", "neumann"),
            flux_direction=1,
            axis=0,
            expected_flux_bc=("dirichlet", "dirichlet"),
        ),
    ]
    primary = cases[0]

    verdict_checks = {
        "external_fix_source_complete": all(source_checks.values()),
        "old_scalar_bc_inheritance_misses_no_penetration_flux_bc": not primary[
            "old_matches_expected"
        ],
        "corrected_inference_matches_no_penetration_flux_bc": primary[
            "corrected_matches_expected"
        ],
        "periodic_control_matches_expected": cases[1]["corrected_matches_expected"],
        "tangential_wall_control_matches_expected": cases[2][
            "corrected_matches_expected"
        ],
    }
    verdict = "pass" if all(verdict_checks.values()) else "fail"

    return {
        "run_id": "jaxcfd-flux-boundary-real-defect-witness-001",
        "date": "2026-07-03",
        "subject": "JAX-CFD PR #167 advection flux-boundary semantic witness",
        "mr_card": "research_assets/mr_cards/jaxcfd_flux_boundary_consistency.json",
        "source_artifacts": {
            path.name: {
                "path": str(path),
                "sha256": sha256_file(path),
            }
            for path in sorted(raw_dir.glob("jaxcfd_pr_167*.json"))
            if path.is_file()
        },
        "source_checks": source_checks,
        "source_follow_up_cases": cases,
        "metric": {
            "name": "advection_flux_boundary_consistency",
            "primary_case": "normal_no_penetration_scalar_neumann",
            "old_flux_bc": primary["old_flux_bc"],
            "corrected_flux_bc": primary["corrected_flux_bc"],
            "expected_flux_bc": primary["expected_flux_bc"],
            "old_matches_expected": primary["old_matches_expected"],
            "corrected_matches_expected": primary["corrected_matches_expected"],
        },
        "verdict_checks": verdict_checks,
        "typed_verdict": verdict,
        "claim_limitations": (
            "One external merged-PR-linked boundary-condition semantic witness "
            "for JAX-CFD advection flux handling. It is not a full solver "
            "validation, not a CFD benchmark result, and not a production "
            "defect-rate estimate."
        ),
        "forbidden_claims": [
            "The method validates JAX-CFD solver accuracy.",
            "The paper measures JAX-CFD defect prevalence.",
            "The witness proves CFD simulation correctness.",
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
