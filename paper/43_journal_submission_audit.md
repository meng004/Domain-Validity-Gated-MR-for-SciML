# 43 — §15 Journal Submission Audit (IST regular track)

> Date: 2026-06-17 · Subject: `paper/ist-submission/main.tex` (Elsevier elsarticle).
> Run after the phase-22 reframe (R2-1 cross-SUT, validity–coverage duality central
> thesis, R2-3/R2-4). IST is **single-anonymized**, so author info is kept (not a
> double-blind target). Verdict: **submission-ready, no blockers.**

## §15.3 reviewer-leak / placeholder grep audit — ALL CLEAN (0 hits)
| Check | Pattern | Result |
|---|---|---|
| A reviewer-speak | `this/prior revision, Round N, in response to a Round` | 0 ✓ |
| B reviewer-process | `R[0-9]+ W[0-9]+, round-N, DA-MAJOR-N, in this revision` | 0 ✓ |
| C placeholders | `<ARXIV_ID>, <DOI>, placeholder, XXXX, TBD` | 0 ✓ |
| D/E dangling section nums | `subsubsection{N.X}, §N.N.N` | 0 ✓ |
| §6.5 version narrative | `v1.0, R[1-9] adds, round-N, first/second adversarial` | 0 ✓ |
| F double-blind leak | n/a (IST single-anonymized; authors/CRediT kept) | n/a |

## §15.4 compile audit — CLEAN
Full clean build (`pdflatex → bibtex → pdflatex ×2`): 42 pp.
- Missing character: **0** · undefined: **0** · bibtex didn't-find: **0**
- Overfull \hbox >50pt: **0** (Underfull 40 — cosmetic loose lines, acceptable)
- Bib all-cited: **32 cited / 32 defined**, 0 undefined, 0 uncited.

## §15.5 numbering / layout — CLEAN
- Inline enumeration is consistent: only roman `(i)(ii)(iii)(iv)`; no mixing with
  `(a)(b)` or `(1)(2)`.
- `\clearpage` precedes `\appendix` (appendix starts on a fresh page).
- Native `\section` auto-numbering (no manual numbers → no double-numbering;
  `secnumdepth` override not needed here).

## §15.6 visual check — CLEAN
Rasterized p1 (highlights), p30, p31. All render without overflow or overlap.
- Highlights show the R2-4 fix: "MR tolerances are gated by the measuring operator's
  floor (O(h) for divergence)".
- The new central-thesis content renders correctly: the "Cross-SUT keystone" and
  "Falsifiable predictions, and what would refute them" paragraphs (p30–31).
- (An initial garbled raster of p30 was a display artifact; the text layer is clean
  in `pdftotext` and the re-render is clean.)

## Findings (non-blocking)
1. **⚠ Stale intermediate in the submission folder.**
   `paper/ist-submission/manuscript-body.raw.tex` is a tracked Pandoc intermediate
   that `main.tex` does **not** `\input` (main.tex is self-contained). No
   `build_submission.sh` exists, so the tarball is assembled by hand — exclude this
   file (or `git rm` / gitignore it) so it does not ship in the submission package.
2. **ℹ `(R1)–(R4)` experiment labels** in §Results (fault-robustness battery) read as
   experiment IDs, not revision rounds. They pass the project's own §15.3-B/§6.5
   patterns and are referenced by `tests/test_p2_adversarial_mutants.py`, so they are
   left as-is; an optional `(E1)–(E4)` rename would remove any round/revision
   ambiguity for a cautious reviewer.
3. **ℹ §15.2 overflow-safety block** — only `emergencystretch` is present (not the full
   `adjustbox`/`fvextra`/`sloppy` block), but the compile is clean (0 overfull >50pt),
   so it is empirically sufficient for this manuscript.

## Verdict
**Submission-ready.** §15.3 grep, §15.4 compile, §15.5 numbering, and §15.6 visual all
pass. Only finding #1 (exclude the stale `manuscript-body.raw.tex` from the tarball)
needs a one-line action at packaging time; #2 and #3 are optional.
