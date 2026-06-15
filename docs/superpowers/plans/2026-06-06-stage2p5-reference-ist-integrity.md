# Stage 2.5 Reference, IST, and Integrity Convergence Plan

Date: 2026-06-06

## Goal

Move the paper from a minimal empirically supported method-paper draft to a submission-readiness draft by converging references, citations, the IST LaTeX package, and claim-level evidence tracing.

## Preconditions

- Work only in `<PROJECT_ROOT>`.
- Prefix every shell command with `rtk`.
- Preserve existing user/PR4 changes; do not reset or revert dirty files.
- Treat PR4 as a bounded evidence source only: one SUT, one checkpoint, one mirror-y OOD-stress MR, one eval trajectory, 10 recorded frames.
- Do not cite unverified literature as submission-ready evidence.

## Main Steps

1. Add readiness tests before editing paper text.
   - Test stale planned-study language is absent from `paper/manuscript.md` and `paper/ist-submission/main.tex`.
   - Test PR4 bounded evidence wording is present in the IST package.
   - Test cited keys in the IST package exist in `references.bib` and are covered by a citation audit.
   - Test Stage 2.5 audit records claim-to-evidence links and blocked boundaries.

2. Converge references and citations.
   - Correct BibTeX metadata for cited keys whose ledger already has DOI/arXiv/publisher evidence.
   - Remove or avoid citation of unverified keys.
   - Add `paper/citation_audit.md` to map each cited key to source evidence and claim limits.

3. Sync manuscript and IST LaTeX package.
   - Replace planned Results, Discussion, Threats, and Conclusion language with PR4-bounded evidence.
   - Keep exact claim boundaries: no reliability, accuracy, baseline, multi-SUT, exact-symmetry, or geometry-independent claim.
   - Preserve the role of LLMs as candidate-generation and material-organization support only.

4. Create Stage 2.5 integrity audit.
   - For each paper claim, record location, allowed wording, forbidden overclaim, and evidence source.
   - Mark blocked/deferred items explicitly.

5. Review and verify.
   - Run the new readiness tests.
   - Run existing PR4/evidence validators.
   - Ask a subagent to review changed files for unsupported claims, citation risk, and stale wording.

## Acceptance Criteria

- The new readiness test passes.
- Existing PR4 evidence convergence tests pass.
- Existing research-asset/protocol validators pass.
- `paper/manuscript.md` no longer ends with a placeholder reference section.
- `paper/ist-submission/main.tex` no longer contains planned-results language and includes PR4-bounded results.
- Every submission-cited key is represented in `references.bib` and `paper/citation_audit.md`.
- Stage 2.5 audit can trace each major claim to a ledger, artifact, or external literature source.

## Review Standard

The review must be evidence-first. A conclusion is accepted only when the reviewer can point to a file path, line, artifact, ledger entry, DOI, arXiv record, or explicit blocked status. Unverified or partially verified material must be downgraded or removed from submission claims.
