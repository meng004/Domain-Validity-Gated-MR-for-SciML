from __future__ import annotations

import argparse
import json
from pathlib import Path


UNIT_SPECS = [
    {
        "unit_id": "EDC-01",
        "repo_or_subsystem": "DeepXDE PeriodicBC",
        "report_path": "research_assets/runs/deepxde-periodicbc-real-defect-scan/deepxde_periodicbc_real_defect_witness_report.json",
        "external_source": "https://github.com/lululxvi/deepxde/issues/26 / https://github.com/lululxvi/deepxde/pull/27",
        "mr_family": "boundary-condition periodicity",
    },
    {
        "unit_id": "EDC-02",
        "repo_or_subsystem": "NeuralOperator spectrum_2d",
        "report_path": "research_assets/runs/external-defect-corpus-scan/neuraloperator_spectrum2d_real_defect_witness_report.json",
        "external_source": "https://github.com/neuraloperator/neuraloperator/issues/532 / https://github.com/neuraloperator/neuraloperator/pull/661",
        "mr_family": "spectral metric numerical decidability",
    },
    {
        "unit_id": "EDC-03",
        "repo_or_subsystem": "NeuralOperator SpectralConv",
        "report_path": "research_assets/runs/external-defect-corpus-scan/neuraloperator_hermitian_symmetry_real_defect_witness_report.json",
        "external_source": "https://github.com/neuraloperator/neuraloperator/pull/702",
        "mr_family": "frequency-domain symmetry",
    },
    {
        "unit_id": "EDC-04",
        "repo_or_subsystem": "PhiFlow/PhiML custom gradient",
        "report_path": "research_assets/runs/external-defect-corpus-scan/phiml_custom_gradient_transpose_real_defect_witness_report.json",
        "external_source": "https://github.com/tum-pbs/PhiFlow/issues/199 / https://github.com/tum-pbs/PhiML/commit/96ef3e4d8376502a1b75dcdd799d9ada1cb39f72",
        "mr_family": "coordinate/component transform",
    },
    {
        "unit_id": "EDC-05",
        "repo_or_subsystem": "JAX-CFD advection flux boundary",
        "report_path": "research_assets/runs/external-defect-corpus-scan/jaxcfd_flux_boundary_real_defect_witness_report.json",
        "external_source": "https://github.com/google/jax-cfd/pull/167",
        "mr_family": "boundary-condition consistency",
    },
]


def load_report(root: Path, report_path: str) -> dict[str, object]:
    path = root / report_path
    return json.loads(path.read_text(encoding="utf-8"))


def build_summary(root: Path) -> dict[str, object]:
    units = []
    verdict_counts: dict[str, int] = {}
    for spec in UNIT_SPECS:
        report = load_report(root, spec["report_path"])
        verdict = str(report["typed_verdict"])
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        units.append(
            {
                **spec,
                "typed_verdict": verdict,
                "run_id": report["run_id"],
                "metric": report["metric"],
                "claim_limitations": report["claim_limitations"],
                "forbidden_claims": report["forbidden_claims"],
            }
        )

    repo_roots = {
        "DeepXDE",
        "NeuralOperator",
        "PhiFlow/PhiML",
        "JAX-CFD",
    }
    passed_units = [unit for unit in units if unit["typed_verdict"] == "pass"]
    minimum_success_checks = {
        "at_least_five_external_units": len(units) >= 5,
        "at_least_three_repositories_or_subsystems": len(repo_roots) >= 3,
        "all_units_have_pass_typed_verdicts": len(passed_units) == len(units),
        "all_units_have_external_sources": all(unit["external_source"] for unit in units),
        "all_units_have_mr_family": all(unit["mr_family"] for unit in units),
    }

    return {
        "run_id": "external-defect-corpus-summary-001",
        "date": "2026-07-03",
        "purpose": "One-week external issue/PR/commit-linked SciML defect-witness corpus for JSS external-validity risk reduction.",
        "unit_count": len(units),
        "repository_or_subsystem_count": len(repo_roots),
        "repository_or_subsystem_roots": sorted(repo_roots),
        "verdict_counts": verdict_counts,
        "units": units,
        "minimum_success_checks": minimum_success_checks,
        "typed_verdict": "pass"
        if all(minimum_success_checks.values())
        else "inconclusive",
        "claim_limitations": (
            "The corpus supports a stronger external issue/PR/commit-linked "
            "semantic-witness statement across five units and four repositories "
            "or subsystems. It remains component/utility-level evidence, not a "
            "production CFD validation, not trained-SUT correctness evidence, "
            "not population defect prevalence, and not a real-world defect-rate "
            "estimate."
        ),
        "forbidden_claims": [
            "The paper measures a real-world defect-detection rate.",
            "The corpus validates production SciML or CFD deployments.",
            "The witnesses prove trained SUT accuracy or reliability.",
            "The witnesses establish broad NeuralOperator, DeepXDE, JAX-CFD, PhiFlow, or PhiML correctness.",
            "The corpus is a representative sample of SciML software defects.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    report = build_summary(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
