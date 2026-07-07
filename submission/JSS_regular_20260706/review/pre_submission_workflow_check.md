# Pre-Submission Workflow Check

Date: 2026-07-06

Workflow source: `/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/科研工作流/科研工作流指南.md`.

Target package: `submission/JSS_regular_20260706/`.

## Workflow Scope

This check follows the guide's late-stage path for a near-submission manuscript: Phase 10.0 checks editor reviewability and Phase 10.1 checks submission-package compliance.

## Phase 10.0 Editor Reviewability Gate

| Gate | Result | Evidence |
|---|---|---|
| Scope | Pass | The abstract, introduction, and cover letter frame the work as a software V&V/testing method for SciML surrogate software. |
| Novelty and impact | Pass with bounded residual risk | The manuscript states that the novelty is not MR outcome recording, but a SciML-specific numerical-decidability gate tied to physical basis, representation mapping, and measurement floor. |
| Scale / maturity | Qualified pass | Evidence spans bounded cylinder-flow, airfoil, PINN/FNO, periodic-advection, RealPDEBench, external issue/PR/commit-linked witnesses, and cross-program checks. It is not a representative real-defect corpus or production-validation study, and the manuscript says so. |
| Research excellence / transparency | Pass | MR cards, ledgers, manifests, validators, Zenodo/source links, and fail-closed evidence gates are declared. |
| Audience readability | Pass with normal reviewer risk | The five-concept reader map and formal spine are present; concept-density tests pass. Some conceptual density remains a review risk, not a desk-rejection trigger. |

Desk-rejection audit record: `review/rejection_risk_audit.md`.

## Phase 10.1 Submission Compliance Gate

| Check | Result | Evidence |
|---|---|---|
| JSS precheck | Pass | `tools/precheck_jss.py submission/JSS_regular_20260706/source/main.tex` passed. |
| Main PDF build | Pass | Final log reports `Output written on main.pdf (36 pages, 436531 bytes).`. |
| Warning patterns | Pass | Final main log has 0 warning-pattern hits in `review/package_review.md`. |
| Abstract | Pass | 223 words; no citation or cross-reference commands in the abstract. |
| Highlights | Pass | 5 separate editable highlights; each is within the 85-character JSS limit. |
| Required statements | Pass | CRediT, competing-interest declaration, generative-AI declaration, data/code availability, and evidence boundary are present in `declarations.md`. |
| Unique LaTeX source | Pass | Repository-level `manuscript/` is the canonical paper source; package-level `source/` contains generated upload copies of `main.tex` and `supplementary.tex`. |
| Source archive | Pass | `jss_latex_source.zip` is flat and has no temporary, backup, log, nested, or compiled-output entries. |
| Package archive | Pass | `jss_submission_package_20260706.zip` includes the submission materials and no temporary, backup, log, or auxiliary files outside `review/`. |
| PDF/source consistency | Pass | The top-level `main.pdf` excludes highlights and supplementary appendix content; `supplementary.pdf` is copied from the separately compiled file in `source/`. |

## LaTeX Audit

The six broken math/subscript scans were run on the final `source/main.tex`: P1 `$X$\_Y`, P2 plain-text Greek with underscore, P3 `\mathrm{..._...}`, P4 italic version/label subscript pattern, P5 adjacent short `$...$` groups, and P6 text-mode base plus isolated subscript. No hits were found.

Version-leakage scan found no revision-process terms. Em-dash/en-dash scan found no hits in the final submit-facing manuscript and declarations. The only generic humanization scan hits were ordinary uses of `robustness` in technical section headings/text, not unsupported inflated-significance claims.

## Evidence Gates

- `tools/validate_research_assets.py`: pass
- `tools/validate_experiment_protocol.py`: pass
- `python -m pytest tests -q`: 477 passed
- `python -m pytest tests/test_jss_concept_density_repair.py -q`: 6 passed

## Residual Risks

- Editorial Manager item labels still need to be selected manually during upload.
- The manuscript is ready for serious JSS review, but this check does not claim guaranteed acceptance. The main residual scholarly risks remain bounded external validity and conceptual density, both already disclosed in the manuscript and review-risk audit.
