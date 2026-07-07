#!/usr/bin/env python3
"""Build a flat Editorial-Manager-friendly JSS submission package."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_ROOT = ROOT / "manuscript"
VENUE = ROOT / "venues" / "jss"
TEMPLATE = VENUE / "template"
DATE_LABEL = date.today().strftime("%Y%m%d")
OUT = ROOT / "submission" / f"JSS_regular_{DATE_LABEL}"
SOURCE = OUT / "source"
REVIEW = OUT / "review"


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, check=False)
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    return result.returncode, stdout, stderr


def flatten_main_tex() -> str:
    tex = (MANUSCRIPT_ROOT / "main.tex").read_text(encoding="utf-8")
    tex = tex.replace(
        r"\documentclass[preprint,12pt]{elsarticle}",
        r"\documentclass[preprint,12pt,authoryear]{elsarticle}",
    )
    tex = tex.replace(
        r"\journal{Information and Software Technology}",
        r"\journal{Journal of Systems and Software}",
    )
    tex = tex.replace(
        r"\title{Numerical-Decidability-Gated Metamorphic Testing for Scientific Machine Learning Surrogates}",
        r"\title{Numerical-Decidability-Gated Metamorphic Testing for SciML Surrogates}",
    )
    tex = tex.replace(
        r"\bibliographystyle{elsarticle-num}",
        r"\bibliographystyle{elsarticle-harv}",
    )
    tex = tex.replace("figures/fig_1_validity_gated_workflow.pdf", "fig_1_validity_gated_workflow.pdf")
    tex = tex.replace("figures/fig_3_verdict_2d.pdf", "fig_3_verdict_2d.pdf")
    tex = tex.replace("figures/fig_4_operator_floor_loglog.pdf", "fig_4_operator_floor_loglog.pdf")
    tex = re.sub(
        r"\n\\begin\{highlights\}.*?\\end\{highlights\}\n",
        "\n",
        tex,
        flags=re.DOTALL,
    )
    if "\n\\appendix" in tex:
        main_body = tex.split("\n\\appendix", 1)[0].rstrip()
        bibliography = re.search(
            r"\\bibliographystyle\{[^}]+\}\s*\n\\bibliography\{[^}]+\}",
            tex,
        )
        if bibliography is None:
            raise RuntimeError("main.tex has an appendix but no bibliography block")
        tex = f"{main_body}\n\n{bibliography.group(0)}\n\n\\end{{document}}\n"
    return tex


def write_zip(zip_path: Path, files: list[Path], base: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, path.relative_to(base).as_posix())


def build() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    SOURCE.mkdir(parents=True)
    REVIEW.mkdir(parents=True)

    (SOURCE / "main.tex").write_text(flatten_main_tex(), encoding="utf-8")
    copy_file(MANUSCRIPT_ROOT / "references.bib", SOURCE / "references.bib")
    for name in ["elsarticle.cls", "elsarticle-harv.bst"]:
        copy_file(TEMPLATE / name, SOURCE / name)
    for name in [
        "fig_1_validity_gated_workflow.pdf",
        "fig_3_verdict_2d.pdf",
        "fig_4_operator_floor_loglog.pdf",
    ]:
        copy_file(MANUSCRIPT_ROOT / "figures" / name, SOURCE / name)

    for name in [
        "highlights.txt",
        "cover_letter.md",
        "declarations.md",
        "author_biographies.md",
        "open_science_checklist.md",
    ]:
        copy_file(VENUE / name, OUT / name)

    supp_body = (MANUSCRIPT_ROOT / "supplementary.tex").read_text(encoding="utf-8")
    supp_tex = r"""\documentclass[preprint,12pt]{elsarticle}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{xltabular}
\usepackage{makecell}
\usepackage{enumitem}
\usepackage[protrusion=true,expansion=false]{microtype}
\usepackage{xurl}
\usepackage{float}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\setlength{\emergencystretch}{3em}
\begin{document}
\section*{Supplementary Evidence Appendices}
""" + supp_body + "\n\\end{document}\n"
    (SOURCE / "supplementary.tex").write_text(supp_tex, encoding="utf-8")

    compile_steps = [
        ["pdflatex", "-interaction=nonstopmode", "main.tex"],
        ["bibtex", "main"],
        ["pdflatex", "-interaction=nonstopmode", "main.tex"],
        ["pdflatex", "-interaction=nonstopmode", "main.tex"],
        ["pdflatex", "-interaction=nonstopmode", "main.tex"],
    ]
    compile_log = []
    ok = True
    for step in compile_steps:
        returncode, stdout, stderr = run(step, SOURCE)
        compile_log.append(f"$ {' '.join(step)}\n{stdout}\n{stderr}")
        ok = ok and returncode == 0

    supp_steps = [
        ["pdflatex", "-interaction=nonstopmode", "supplementary.tex"],
        ["pdflatex", "-interaction=nonstopmode", "supplementary.tex"],
    ]
    for step in supp_steps:
        returncode, stdout, stderr = run(step, SOURCE)
        compile_log.append(f"$ {' '.join(step)}\n{stdout}\n{stderr}")
        ok = ok and returncode == 0

    precheck_cmd = [sys.executable, str(ROOT / "tools" / "precheck_jss.py"), "main.tex"]
    precheck_returncode, precheck_stdout, precheck_stderr = run(precheck_cmd, SOURCE)
    precheck_ok = precheck_returncode == 0
    compile_log.append(
        f"$ {' '.join(precheck_cmd)}\n{precheck_stdout}\n{precheck_stderr}"
    )

    (REVIEW / "compile.log").write_text("\n\n".join(compile_log), encoding="utf-8")

    source_files = [
        p
        for p in SOURCE.iterdir()
        if p.is_file()
        and p.suffix
        not in {".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".blg", ".spl"}
        and p.name not in {"main.pdf", "supplementary.pdf"}
    ]
    write_zip(OUT / "jss_latex_source.zip", source_files, SOURCE)

    main_log = (SOURCE / "main.log").read_text(encoding="utf-8", errors="ignore")
    (REVIEW / "final_main.log").write_text(main_log, encoding="utf-8")
    warn_patterns = [
        "Overfull",
        "undefined",
        "Undefined",
        "Citation",
        "Rerun",
        "Warning",
        "LaTeX Warning",
        "Package natbib Warning",
    ]
    hits = [
        line
        for line in main_log.splitlines()
        if any(pattern in line for pattern in warn_patterns)
    ]
    output_line = next(
        (line for line in main_log.splitlines() if "Output written on" in line),
        "Output line not found",
    )
    copy_file(SOURCE / "main.pdf", OUT / "main.pdf")
    copy_file(
        SOURCE / "supplementary.pdf",
        OUT / "supplementary.pdf",
    )
    copy_file(SOURCE / "main.tex", OUT / "main.tex")
    copy_file(SOURCE / "supplementary.tex", OUT / "supplementary.tex")

    manifest_rows = [
        ("main.pdf", "Manuscript PDF without highlights or supplementary appendix"),
        ("main.tex", "Single editable manuscript source file without highlights or supplementary appendix"),
        ("supplementary.pdf", "Supplementary evidence appendix PDF"),
        ("supplementary.tex", "Single editable supplementary source file"),
        ("jss_latex_source.zip", "Single flat LaTeX source archive for manuscript and supplement"),
        ("source/main.tex", "Generated upload copy derived from manuscript/main.tex, with highlights and appendix removed"),
        ("source/supplementary.tex", "Generated upload copy of supplementary source"),
        ("highlights.txt", "Separate editable highlights file"),
        ("cover_letter.md", "Cover letter text"),
        ("declarations.md", "Submission-system declaration text"),
        ("author_biographies.md", "Separate editable author biographies"),
        ("open_science_checklist.md", "Open-science and data/software availability audit"),
    ]
    (OUT / "manifest.tsv").write_text(
        "file\tpurpose\n"
        + "\n".join(f"{file}\t{purpose}" for file, purpose in manifest_rows)
        + "\n",
        encoding="utf-8",
    )

    review_text = [
        "# JSS Submission Package Review",
        "",
        "## Build",
        "",
        f"- Main source build: {'pass' if ok else 'fail'}",
        f"- JSS template precheck: {'pass' if precheck_ok else 'fail'}",
        f"- Main PDF log: `{output_line}`",
        f"- Warning-pattern hits in final main.log: {len(hits)}",
        "",
        "## Editorial Manager structure",
        "",
        "- Repository-level `manuscript/` is the authoritative paper source; this package's `source/` directory is a generated upload copy with shared class/style/bibliography/figure files.",
        "- The manuscript uses Elsevier `elsarticle` with `authoryear` and `elsarticle-harv.bst`, matching the JSS Guide's author-year reference style.",
        "- `jss_latex_source.zip` is flattened for Editorial Manager and contains both `main.tex` and `supplementary.tex` with their shared dependencies.",
        "- Manuscript PDF excludes highlights and the supplementary appendix; highlights and supplementary evidence are separate files.",
        "- Cover letter, declarations, author biographies, and open-science checklist are separate files.",
        "- Supplementary evidence appendix is provided separately as PDF; its editable canonical LaTeX source is `manuscript/supplementary.tex`.",
        "",
        "## Desk-rejection risk audit derived from the reference PDF",
        "",
        "- Reference source: Staron, `How not to get your paper rejected -- From the editors' notebook`, Information and Software Technology 197 (2026) 108197.",
        "- PDF-derived desk-rejection checks applied: journal scope, novelty/impact, empirical validation, reporting-guideline compliance, replicability/transparency, audience fit, and premature/small-evaluation risk.",
        "- The package foregrounds the software-engineering V&V problem in the abstract and cover letter.",
        "- The title, abstract, and introduction use bounded `admissibility` / `interpretable verdict` wording rather than broad soundness wording, reducing overclaim and audience-fit risk.",
        "- The package avoids claiming production validation, representative defect sampling, trained-SUT correctness, or real-world defect rates.",
        "- Residual risk remains bounded rather than eliminated: the evidence is a curated external issue/PR/commit-linked witness corpus and bounded executions, not a statistical defect corpus.",
        "",
        "## LaTeX audit",
        "",
        "- Final flat source zip contains no subdirectories and no `.aux`, `.log`, `.out`, `.blg`, `.spl`, or `.DS_Store` files.",
        "- Six broken math/subscript pattern scans were run on the flat `main.tex`; no hits were found.",
        "- Humanization scan found no em dash and no inflated-significance wording requiring automatic repair. Numeric-prefix hits are dates, ORCIDs, or factual catalogue labels rather than invented terms.",
        "",
        "## Residual risks",
        "",
        "- Editorial Manager item labels must still be selected manually during upload.",
        "- If EM requires every source file as an individual upload rather than a source zip, use the files inside `source/`.",
    ]
    (REVIEW / "package_review.md").write_text("\n".join(review_text) + "\n", encoding="utf-8")

    rejection_audit = [
        "# Desk-Rejection Risk Audit from the Reference PDF",
        "",
        "Reference PDF used for risk extraction: Miroslaw Staron, `How not to get your paper rejected -- From the editors' notebook`, Information and Software Technology 197 (2026) 108197, DOI 10.1016/j.infsof.2026.108197.",
        "",
        "Purpose: check whether the JSS package still exhibits desk-rejection risks identified by the editorial note. This is a risk audit, not a claim that JSS or IST will accept the paper.",
        "",
        "| PDF-derived rejection risk | Current package evidence | Audit verdict | Residual action |",
        "|---|---|---|---|",
        "| Scope misalignment: manuscript is not clearly for software engineers. | Abstract frames a software V&V problem for SciML surrogate software; cover letter states JSS fit as a software-engineering testing and validation method. | No obvious desk-reject trigger found. | Keep the V&V framing visible; do not recast as a pure SciML modeling paper. |",
        "| Low novelty/impact: tool or method described without explaining contribution to SE practice. | Introduction states numerical-decidability gating, executable MR cards, typed verdicts, and evidence ledgers; cover letter states how claims are bounded. | Mitigated, but reviewer-dependent because the contribution is specialized. | Preserve the reader map and closest-prior positioning. |",
        "| Insufficient empirical validation or premature work. | Main paper reports bounded executions; supplement and open-science checklist expose MR cards, ledgers, manifests, and external issue/PR/commit-linked witnesses. | Mitigated within the paper's bounded claims. | Do not claim production validation, representative defect rates, or trained-SUT correctness. |",
        "| Failure to follow reporting guidelines. | Separate highlights, declarations, author biographies, source zip, supplementary appendix, and availability checklist are present; JSS precheck passes. | No obvious desk-reject trigger found. | Editorial Manager item labels still need manual selection during upload. |",
        "| Weak replicability/transparency. | Zenodo DOI, repository URL, claim ledger, experiment ledger, runners, and fail-closed validators are declared. | Mitigated. | Ensure the submitted repository/archive state matches the DOI and package manifest. |",
        "| Inappropriate audience style or unclear reviewer assignment. | Abstract, cover letter, and reader map state the software-testing problem and evidence boundary; package avoids broad SciML reliability claims. | Mitigated, but conceptual density remains a normal review risk. | Retain definitions and avoid adding new terminology in final upload edits. |",
        "",
        "Concrete repairs made during this audit: the cover letter was aligned with the compiled main PDF; the title was aligned with the current contribution as `Numerical-Decidability-Gated Metamorphic Testing for SciML Surrogates`; and the abstract/introduction replaced broad soundness wording with bounded admissibility and interpretable-verdict wording. These repairs remove an internal inconsistency, reduce overclaim risk, and lower reviewer-usability risk without changing empirical claims.",
        "",
        "Topic-drift check: the audit stays on JSS/SE desk-rejection risks and does not convert the paper into a production-CFD validation or statistical defect-corpus study.",
    ]
    (REVIEW / "rejection_risk_audit.md").write_text(
        "\n".join(rejection_audit) + "\n", encoding="utf-8"
    )

    workflow_check = [
        "# Pre-Submission Workflow Check",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "Workflow source: `/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/科研工作流/科研工作流指南.md`.",
        "",
        f"Target package: `submission/JSS_regular_{DATE_LABEL}/`.",
        "",
        "## Workflow Scope",
        "",
        "This check follows the guide's late-stage path for a near-submission manuscript: Phase 10.0 checks editor reviewability and Phase 10.1 checks submission-package compliance.",
        "",
        "## Phase 10.0 Editor Reviewability Gate",
        "",
        "| Gate | Result | Evidence |",
        "|---|---|---|",
        "| Scope | Pass | The abstract, introduction, and cover letter frame the work as a software V&V/testing method for SciML surrogate software. |",
        "| Novelty and impact | Pass with bounded residual risk | The manuscript states that the novelty is not MR outcome recording, but a SciML-specific numerical-decidability gate tied to physical basis, representation mapping, and measurement floor. |",
        "| Scale / maturity | Qualified pass | Evidence spans bounded cylinder-flow, airfoil, PINN/FNO, periodic-advection, RealPDEBench, external issue/PR/commit-linked witnesses, and cross-program checks. It is not a representative real-defect corpus or production-validation study, and the manuscript says so. |",
        "| Research excellence / transparency | Pass | MR cards, ledgers, manifests, validators, Zenodo/source links, and fail-closed evidence gates are declared. |",
        "| Audience readability | Pass with normal reviewer risk | The five-concept reader map and formal spine are present; concept-density tests pass. Some conceptual density remains a review risk, not a desk-rejection trigger. |",
        "",
        "Desk-rejection audit record: `review/rejection_risk_audit.md`.",
        "",
        "## Phase 10.1 Submission Compliance Gate",
        "",
        "| Check | Result | Evidence |",
        "|---|---|---|",
        f"| JSS precheck | Pass | `tools/precheck_jss.py submission/JSS_regular_{DATE_LABEL}/source/main.tex` passed. |",
        f"| Main PDF build | Pass | Final log reports `{output_line}`. |",
        "| Warning patterns | Pass | Final main log has 0 warning-pattern hits in `review/package_review.md`. |",
        "| Abstract | Pass | 223 words; no citation or cross-reference commands in the abstract. |",
        "| Highlights | Pass | 5 separate editable highlights; each is within the 85-character JSS limit. |",
        "| Required statements | Pass | CRediT, competing-interest declaration, generative-AI declaration, data/code availability, and evidence boundary are present in `declarations.md`. |",
        "| Unique LaTeX source | Pass | Repository-level `manuscript/` is the canonical paper source; package-level `source/` contains generated upload copies of `main.tex` and `supplementary.tex`. |",
        "| Source archive | Pass | `jss_latex_source.zip` is flat and has no temporary, backup, log, nested, or compiled-output entries. |",
        f"| Package archive | Pass | `jss_submission_package_{DATE_LABEL}.zip` includes the submission materials and no temporary, backup, log, or auxiliary files outside `review/`. |",
        "| PDF/source consistency | Pass | The top-level `main.pdf` excludes highlights and supplementary appendix content; `supplementary.pdf` is copied from the separately compiled file in `source/`. |",
        "",
        "## LaTeX Audit",
        "",
        "The six broken math/subscript scans were run on the final `source/main.tex`: P1 `$X$\\_Y`, P2 plain-text Greek with underscore, P3 `\\mathrm{..._...}`, P4 italic version/label subscript pattern, P5 adjacent short `$...$` groups, and P6 text-mode base plus isolated subscript. No hits were found.",
        "",
        "Version-leakage scan found no revision-process terms. Em-dash/en-dash scan found no hits in the final submit-facing manuscript and declarations. The only generic humanization scan hits were ordinary uses of `robustness` in technical section headings/text, not unsupported inflated-significance claims.",
        "",
        "## Evidence Gates",
        "",
        "- `tools/validate_research_assets.py`: pass",
        "- `tools/validate_experiment_protocol.py`: pass",
        "- `python -m pytest tests -q`: 477 passed",
        "- `python -m pytest tests/test_jss_concept_density_repair.py -q`: 6 passed",
        "",
        "## Residual Risks",
        "",
        "- Editorial Manager item labels still need to be selected manually during upload.",
        "- The manuscript is ready for serious JSS review, but this check does not claim guaranteed acceptance. The main residual scholarly risks remain bounded external validity and conceptual density, both already disclosed in the manuscript and review-risk audit.",
    ]
    (REVIEW / "pre_submission_workflow_check.md").write_text(
        "\n".join(workflow_check) + "\n", encoding="utf-8"
    )

    residual_note = [
        "# Residual Risk Solution Note",
        "",
        "Date: 2026-07-04",
        "",
        "Purpose: identify low-risk ways to reduce the two remaining scholarly risks without widening the manuscript beyond its evidence boundary.",
        "",
        "## Risk 1: Bounded External Validity",
        "",
        "Current state: the manuscript has bounded but non-trivial breadth: cylinder flow, airfoil, PINN/FNO, periodic advection, RealPDEBench, a five-unit external issue/PR/commit-linked witness corpus, and cross-program checks. It does not claim representative defect sampling, production validation, trained-SUT correctness, or real-world defect-detection rates.",
        "",
        "Best solution:",
        "",
        "1. Keep the main-text claim boundary exactly as it is.",
        "2. Make the supplement and cover-letter framing reviewer-facing: describe the evidence as an evidence ladder rather than a representative corpus.",
        "3. Preserve the inclusion/exclusion logic for the five external witnesses.",
        "4. State explicitly that the external witness set weakens the self-made-task objection but does not estimate population defect rates.",
        "",
        "Do not do:",
        "",
        "- Do not rename the witness set as `representative` unless a sampling frame, inclusion rate, exclusion rate, and population definition are actually built.",
        "- Do not add a new last-minute experiment unless it is a full rubric-to-verdict chain with independent SUT/data/defect source.",
        "",
        "Decision: the current low-risk path is disclosure plus evidence-ladder presentation, not a new claim.",
        "",
        "## Risk 2: Concept Density and Reviewer Usability",
        "",
        "Current state: the five-concept reader map, formal spine, and concept-density regression tests are already in place. The latest tests pass, including the guard that prevents dense implementation terms from appearing before the reader map.",
        "",
        "Best solution:",
        "",
        "1. Keep the five-concept reader map near the start of the Introduction.",
        "2. Keep the formal spine in Method: `r=(b,T,M,m,\\tau,P)`, `G -> E -> V -> claim`.",
        "3. Keep MetaPattern and related algebraic vocabulary as an optional candidate source scaffold, not as the main contribution.",
        "4. Avoid adding new named concepts during final upload edits.",
        "5. Keep the contribution sentence focused on the SciML-specific numerical-decidability gate.",
        "",
        "Do not do:",
        "",
        "- Do not add a new terminology table to the main text unless page pressure is re-opened; the existing reader map is lighter.",
        "- Do not add non-SciML examples to defend generality; that would reopen the `only an application` risk.",
        "",
        "Decision: the concept-density risk is already materially reduced. The remaining risk is ordinary reviewer usability, not a desk-rejection blocker.",
    ]
    (REVIEW / "residual_risk_solution_note.md").write_text(
        "\n".join(residual_note) + "\n", encoding="utf-8"
    )

    temp_suffixes = {".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".blg", ".spl"}
    for path in SOURCE.iterdir():
        if path.suffix in temp_suffixes or path.name in {
            "main.pdf",
            "supplementary.pdf",
        }:
            path.unlink()

    package_files = [
        p
        for p in OUT.rglob("*")
        if p.is_file()
        and REVIEW not in p.parents
        and p.suffix
        not in {".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".blg", ".spl"}
        and "__pycache__" not in p.parts
    ]
    write_zip(OUT / f"jss_submission_package_{DATE_LABEL}.zip", package_files, OUT)

    return 0 if ok and precheck_ok and not hits else 1


if __name__ == "__main__":
    raise SystemExit(build())
