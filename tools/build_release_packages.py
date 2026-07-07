#!/usr/bin/env python3
"""Build arXiv and Zenodo release packages from the current workspace."""

from __future__ import annotations

import argparse
import os
import shutil
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


CANONICAL_SOURCE = ROOT / "manuscript"
CURRENT_MANUSCRIPT_SOURCE = ROOT / "submission" / "JSS_regular_20260705" / "source"
JSS_TEMPLATE = ROOT / "venues" / "jss" / "template"

ARXIV_FILES = [
    "main.tex",
    "main.bbl",
    "references.bib",
    "elsarticle.cls",
    "elsarticle-harv.bst",
    "supplementary.tex",
]

ARXIV_FIGURES = [
    "fig_1_validity_gated_workflow.pdf",
    "fig_3_verdict_2d.pdf",
    "fig_4_operator_floor_loglog.pdf",
]

ZENODO_TOP_LEVEL = [
    ".dockerignore",
    ".gitattributes",
    ".github",
    ".gitignore",
    ".zenodo.json",
    "CITATION.cff",
    "Dockerfile",
    "LICENSE",
    "NEXT_STEPS.md",
    "README.md",
    "REPRODUCIBILITY.md",
    "docs",
    "experiment",
    "manuscript",
    "paper",
    "requirements",
    "requirements.txt",
    "research_assets",
    "submission",
    "source",
    "tests",
    "theory",
    "tools",
    "venues",
]

EXCLUDED_NAMES = {
    ".DS_Store",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "__pycache__",
    "dist",
    "tmp",
}

EXCLUDED_SUFFIXES = {
    ".aux",
    ".blg",
    ".fls",
    ".fdb_latexmk",
    ".log",
    ".out",
    ".pyc",
    ".spl",
    ".synctex.gz",
}


def remove_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def should_exclude(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDED_NAMES:
        return True
    name = path.name
    if name in EXCLUDED_NAMES:
        return True
    return any(name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES)


def zip_dir_contents(source_dir: Path, zip_path: Path) -> None:
    remove_path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file() and not should_exclude(file_path.relative_to(source_dir)):
                zf.write(file_path, file_path.relative_to(source_dir))


def tar_dir_contents(source_dir: Path, tar_path: Path) -> None:
    remove_path(tar_path)
    tar_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, "w:gz") as tf:
        for file_path in sorted(source_dir.rglob("*")):
            rel = file_path.relative_to(source_dir)
            if file_path.is_file() and not should_exclude(rel):
                tf.add(file_path, arcname=rel)


def build_arxiv(version_label: str) -> tuple[Path, Path]:
    generated_source = CURRENT_MANUSCRIPT_SOURCE
    stage = ROOT / "submission" / f"arxiv-{version_label}"
    source_stage = stage / "source"
    remove_path(stage)
    source_stage.mkdir(parents=True, exist_ok=True)

    for filename in ARXIV_FILES:
        if filename == "main.bbl":
            copy_file(generated_source / filename, source_stage / filename)
        elif filename in {"elsarticle.cls", "elsarticle-harv.bst"}:
            copy_file(JSS_TEMPLATE / filename, source_stage / filename)
        else:
            copy_file(CANONICAL_SOURCE / filename, source_stage / filename)
    for figure in ARXIV_FIGURES:
        figure_src = generated_source / figure
        if not figure_src.exists():
            figure_src = CANONICAL_SOURCE / "figures" / figure
        copy_file(figure_src, source_stage / figure)
    main_pdf = ROOT / "submission" / "JSS_regular_20260705" / "main.pdf"
    copy_file(main_pdf, stage / "main.pdf")

    readme = stage / "README.md"
    readme.write_text(
        "\n".join(
            [
                f"# arXiv {version_label} Package",
                "",
                "Manuscript: Numerical-Decidability-Gated Metamorphic Testing for SciML Surrogates",
                "arXiv identifier: 2606.17529",
                "",
                "Upload the contents of `source/` to arXiv. The source package includes",
                "`main.tex`, `main.bbl`, `references.bib`, the Elsevier class/style files,",
                "PDF figures, and the supplementary evidence appendix source.",
                "`main.pdf` is provided for local visual verification.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    dist_dir = ROOT / "dist" / "arxiv"
    zip_path = dist_dir / f"numerical-decidability-gated-mr-sciml-arxiv-{version_label}-source.zip"
    tar_path = dist_dir / f"numerical-decidability-gated-mr-sciml-arxiv-{version_label}-source.tar.gz"
    zip_dir_contents(source_stage, zip_path)
    tar_dir_contents(source_stage, tar_path)
    return zip_path, tar_path


def build_ist_submission(version_label: str) -> Path:
    stage = ROOT / "submission" / "IST"
    remove_path(stage)
    source_stage = stage / "source"
    source_stage.mkdir(parents=True, exist_ok=True)

    for filename in ["README.md", "cover_letter.md", "highlights.txt"]:
        copy_file(ROOT / "venues" / "ist" / filename, stage / filename)
    copy_file(ROOT / "submission" / "JSS_regular_20260705" / "main.pdf", stage / "main.pdf")
    for filename in ARXIV_FILES:
        if filename == "main.bbl":
            copy_file(CURRENT_MANUSCRIPT_SOURCE / filename, source_stage / filename)
        elif filename in {"elsarticle.cls", "elsarticle-harv.bst"}:
            copy_file(JSS_TEMPLATE / filename, source_stage / filename)
        else:
            copy_file(CANONICAL_SOURCE / filename, source_stage / filename)
    copy_file(ROOT / "submission" / "JSS_regular_20260705" / "main.pdf", source_stage / "main.pdf")
    for figure in ARXIV_FIGURES:
        copy_file(CANONICAL_SOURCE / "figures" / figure, source_stage / "figures" / figure)

    package_readme = stage / "SUBMISSION_README.md"
    package_readme.write_text(
        "\n".join(
            [
                "# IST Submission Mirror",
                "",
                "This directory mirrors the current IST submission materials and the LaTeX",
                "source synced from repository-level `manuscript/`. It is kept under the singular",
                "`submission/` tree so the project has one place for upload-ready artifacts.",
                "",
                f"Release label: {version_label}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return stage


def build_zenodo(version: str) -> Path:
    archive_root = f"DVGMR-SciML-replication-{version}"
    tar_path = ROOT / "dist" / "zenodo" / f"{archive_root}.tar.gz"
    remove_path(tar_path)
    tar_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(tar_path, "w:gz") as tf:
        for entry in ZENODO_TOP_LEVEL:
            path = ROOT / entry
            if not path.exists():
                continue
            if path.is_file():
                if not should_exclude(Path(entry)):
                    tf.add(path, arcname=f"{archive_root}/{entry}")
                continue
            for file_path in sorted(path.rglob("*")):
                rel_to_root = file_path.relative_to(ROOT)
                if file_path.is_file() and not should_exclude(rel_to_root):
                    tf.add(file_path, arcname=f"{archive_root}/{rel_to_root}")
    return tar_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="2.0.0")
    parser.add_argument("--arxiv-label", default="v2")
    parser.add_argument("--include-ist", action="store_true")
    args = parser.parse_args()

    if args.include_ist:
        build_ist_submission(args.arxiv_label)
    arxiv_zip, arxiv_tar = build_arxiv(args.arxiv_label)
    zenodo_tar = build_zenodo(args.version)

    print(f"arxiv_zip={arxiv_zip.relative_to(ROOT)}")
    print(f"arxiv_tar={arxiv_tar.relative_to(ROOT)}")
    print(f"zenodo_tar={zenodo_tar.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
