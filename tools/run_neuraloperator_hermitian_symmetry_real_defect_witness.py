from __future__ import annotations

import argparse
import hashlib
import json
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


def enforce_real_irfft_boundary_frequencies(
    frequencies: list[complex], spatial_size: int
) -> list[complex]:
    corrected = list(frequencies)
    corrected[0] = complex(corrected[0].real, 0.0)
    if spatial_size % 2 == 0:
        corrected[-1] = complex(corrected[-1].real, 0.0)
    return corrected


def imag_boundary_metric(frequencies: list[complex], spatial_size: int) -> dict[str, float]:
    dc_imag = abs(frequencies[0].imag)
    nyquist_imag = abs(frequencies[-1].imag) if spatial_size % 2 == 0 else 0.0
    return {
        "dc_abs_imag": dc_imag,
        "nyquist_abs_imag": nyquist_imag,
        "max_boundary_abs_imag": max(dc_imag, nyquist_imag),
    }


def build_report(raw_dir: Path) -> dict[str, object]:
    pr = load_json(raw_dir / "neuraloperator_pr_702.json")
    files = load_json(raw_dir / "neuraloperator_pr_702_files.json")
    commits = load_json(raw_dir / "neuraloperator_pr_702_commits.json")
    patch_text = "\n".join(file.get("patch", "") for file in files)

    source_checks = {
        "pr_702_merged": bool(pr.get("merged")),
        "pr_702_merged_at": pr.get("merged_at"),
        "pr_702_url": pr.get("html_url"),
        "pr_body_mentions_line_artifacts": "line artifacts" in (pr.get("body") or ""),
        "pr_body_mentions_powers_of_2": "powers of 2" in (pr.get("body") or ""),
        "commit_mentions_hermitian_symmetry": any(
            "Hermitian symmetry" in item.get("commit", {}).get("message", "")
            for item in commits
        ),
        "patch_adds_enforce_hermitian_symmetry_flag": "enforce_hermitian_symmetry"
        in patch_text,
        "patch_zeroes_dc_imag": "out_fft[..., 0].imag.zero_()" in patch_text,
        "patch_zeroes_nyquist_imag": "out_fft[..., -1].imag.zero_()" in patch_text,
        "patch_splits_ifftn_and_irfft": "torch.fft.ifftn" in patch_text
        and "torch.fft.irfft" in patch_text,
    }

    spatial_size = 8
    source_frequencies = [
        complex(1.0, 0.25),
        complex(0.1, -0.2),
        complex(0.3, 0.4),
        complex(-0.2, 0.05),
        complex(2.0, -0.5),
    ]
    corrected_frequencies = enforce_real_irfft_boundary_frequencies(
        source_frequencies, spatial_size
    )
    source_metric = imag_boundary_metric(source_frequencies, spatial_size)
    corrected_metric = imag_boundary_metric(corrected_frequencies, spatial_size)

    verdict_checks = {
        "external_fix_source_complete": all(source_checks.values()),
        "source_has_nonzero_irfft_boundary_imaginary_parts": source_metric[
            "max_boundary_abs_imag"
        ]
        > 0.2,
        "corrected_zeroes_irfft_boundary_imaginary_parts": corrected_metric[
            "max_boundary_abs_imag"
        ]
        <= TOL,
        "interior_complex_modes_are_not_erased": abs(corrected_frequencies[2].imag)
        > 0.3,
    }
    verdict = "pass" if all(verdict_checks.values()) else "fail"

    return {
        "run_id": "neuraloperator-hermitian-symmetry-real-defect-witness-001",
        "date": "2026-07-03",
        "subject": "NeuralOperator PR #702 Hermitian-symmetry semantic witness",
        "mr_card": "research_assets/mr_cards/neuraloperator_hermitian_symmetry_irfft_boundary.json",
        "source_artifacts": {
            path.name: {
                "path": str(path),
                "sha256": sha256_file(path),
            }
            for path in sorted(raw_dir.glob("neuraloperator_pr_702*.json"))
            if path.is_file()
        },
        "source_checks": source_checks,
        "source_follow_up_cases": {
            "spatial_size": spatial_size,
            "source_frequencies": [
                {"real": value.real, "imag": value.imag}
                for value in source_frequencies
            ],
            "corrected_frequencies": [
                {"real": value.real, "imag": value.imag}
                for value in corrected_frequencies
            ],
        },
        "metric": {
            "name": "irfft_boundary_frequency_imaginary_part",
            "tolerance": TOL,
            "source_boundary_metric": source_metric,
            "corrected_boundary_metric": corrected_metric,
        },
        "verdict_checks": verdict_checks,
        "typed_verdict": verdict,
        "claim_limitations": (
            "One external merged-PR-linked semantic witness for the Hermitian "
            "symmetry enforcement added to NeuralOperator SpectralConv. It "
            "does not reproduce GPU-specific line artifacts, does not validate "
            "trained FNO accuracy, and does not measure defect prevalence."
        ),
        "forbidden_claims": [
            "The witness reproduces the GPU line artifact on this machine.",
            "The method validates NeuralOperator trained-model accuracy.",
            "The paper measures NeuralOperator defect prevalence.",
            "The witness proves all FFT paths are correct.",
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
