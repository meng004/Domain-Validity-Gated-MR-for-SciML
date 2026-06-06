# Plan: Final Integrity Convergence (Stage 4.5) — PR #5

Date: 2026-06-06
Branch: codex/stage4-evidence-ist-package (PR #5)
Goal: pass Stage 4.5 final integrity by fixing the three external-submission blockers,
then re-run integrity gates and a multi-role academic re-review. No new experiments,
no scope creep into the separate paper-quality-loop line, no fabricated evidence.

## Blockers (from the user's fresh verification)

1. Claim-ID collision. Manuscript/audit/IST-LaTeX use paper claims C1-domain-validity-
   rubric … C7-llm-candidate-support-only; the authoritative runtime claim-ledger uses
   C1-fixture-asset-path … C7-conservation-diagnostic. Same "C#" prefix, different
   meaning → breaks claim traceability.
2. Duplicate top-level `precondition_check` in experiment-ledger.yml (lines 11 and 32);
   YAML duplicate keys make parse semantics unreliable. Block 1 also names a phantom
   enforcer `validate_pr4_mirror_y_artifacts` (no such function); evidence-package.md
   repeats the phantom.
3. IST main.tex still has `\author{Author Name(s)}` / Institution placeholders.

## Decisions

1. Rename the seven paper-level claims to a distinct namespace `PC1..PC7` in
   manuscript.md, paper/22 audit, and ist-submission/main.tex (and update the two
   readiness tests that assert them). Keep the authoritative claim-ledger C1..C7 and
   evidence-package references unchanged. Add one explicit mapping sentence
   (PC#→ledger C#) and name claim-ledger.yml as the single source of truth, so every
   paper claim is traceable to its runtime-evidence claim without prefix collision.
   Mapping: PC1→C4, PC2→C1/C4, PC3→C3, PC4→C2, PC5→C7, PC6→C6, PC7→(method/ethics
   boundary; no runtime-evidence claim).
2. Merge the duplicate `precondition_check` into one block; set `enforced_by` to the
   real functions `validate_experiment_ledger` and `validate_real_sut_preconditions`;
   fix the same phantom in evidence-package.md.
3. Author block: anonymized for double-anonymized review (user-confirmed), i.e.
   `\author{Anonymous Author(s)}` + affiliation "withheld for double-anonymized
   review" — an intentional, complete, submittable value (not a leftover placeholder).
   Rebuild main.pdf/main.bbl/main.log to match.

## Acceptance

- 97+ unit tests OK (incl. updated stage2p5/stage4 assertions).
- validate_experiment_protocol.py and validate_research_assets.py exit 0.
- experiment-ledger.yml parses with exactly one `precondition_check`.
- No "C#-" paper claim collides with the ledger; mapping is explicit.
- main.tex has no Author/Institution placeholder; PDF regenerated; main.log clean
  (no Overfull/Underfull/undefined/Citation|Label rerun warnings).
- Multi-role re-review (integrity + reviewer) confirms Stage 4.5 has no blocking item.
