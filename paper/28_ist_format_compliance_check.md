# IST format compliance check

Date: 2026-06-07
Target: Elsevier *Information and Software Technology*, regular track.
Source: `paper/ist-submission/main.tex` at HEAD `951ef4e`, after the 2026-06-07
front-matter edits (title shortened, abstract rewritten to satisfy the 300-word
cap, highlights tightened, CRediT / competing-interest / GenAI / data-availability
sections added).

## Hard requirements: pass / fail

| Requirement                          | Limit            | Current        | Status |
|--------------------------------------|------------------|----------------|--------|
| Title                                | (no fixed limit) | 107 chars      | PASS   |
| Structured abstract sections         | C/O/M/R/C required | all 5 present | PASS   |
| Abstract length                      | ≤ 300 words      | **283 words**  | PASS   |
| Highlights count                     | 3–5              | 4              | PASS   |
| Highlights per item                  | ≤ 85 chars       | max 76 chars   | PASS   |
| Keywords count                       | 1–7              | 7              | PASS (at ceiling) |
| LaTeX class                          | `elsarticle`     | `elsarticle`   | PASS   |
| Reference style                      | numbered / harv  | `elsarticle-harv` | PASS  |
| CRediT statement                     | required         | present (placeholder for double-anonymized) | PASS |
| Declaration of competing interest    | required         | present        | PASS   |
| Generative-AI usage declaration      | required         | present        | PASS   |
| Data availability statement          | required         | present        | PASS   |
| **Total length (IST counting rule)** | **≤ 15,000 words** | **~16,779 words** | **FAIL — over by ~1,779** |

IST counts references and appendices in the total, and assigns **200 words per
figure or table**. The current estimate is:

```
detex body (incl. abstract, headings, captions): 11,534 words
+ 25 references (bbl text):                        1,645 words
+ 4 figures + 14 tables, 200 words each:           3,600 words
-----------------------------------------------------------
                            IST-counted total: ~16,779 words
                            IST regular limit:   15,000 words
                                       Over by:    1,779 words (11.9%)
```

Figure regime delta since the previous compliance pass: the 1 figure + 16
tables baseline became 4 figures + 14 tables. Figures Fig.\,1 (validity-gated
workflow), Fig.\,2 (MR-asset data flow), and Fig.\,4 (P1 operator-floor log-log)
were inserted; the orphan Fig.\,3 hierarchy mermaid was deleted (its content is
already carried by Tables 5/6). The MR-card skeleton table was deleted (its
information is in Tables 5/6). Net IST count change: +200 (best lever is now
table consolidation in Sec.\,5.4--5.6).

## Targeted trimming plan (to fit ≤ 15,000)

Section word counts (from `detex main.tex`, approximate):

| Section                          | Words | Target trim |
|----------------------------------|------:|------------:|
| Introduction                     | 1,410 |        −250 |
| Background and Related Work      | 4,166 |        −600 |
| Method                           |  ~900 |        −150 |
| Empirical Design                 | 4,266 |        −700 |
| Results                          | ~1,500 |       −150 |
| Discussion                       |   666 |         −50 |
| Threats to Validity              |   469 |           0 |
| Conclusion                       |  ~250 |           0 |
| (Reduce 16 tables → 12 by merging C11/C12/C13 etc.) | -- | −800 |
| **Total expected reduction**     |       | **≈ 2,700** |

Two parallel levers (use both):

1. **Prose trim** (~1,900 words across Background, Method, Empirical Design,
   Introduction). Background has 4,166 words and likely repeats parts of
   Related Work that could move to a single comparison table. Empirical Design
   carries reproduction details (manifest fields, exact CLI flags) that should
   move to the replication package, not the manuscript body.
2. **Table consolidation** (−800 words at the 200-words-per-table rate).
   - Merge the three C11/C12/C13 compact tables in §5.4–§5.6 into one
     "multi-checkpoint evidence summary" table.
   - Merge the two MR-card-to-verdict tables into one wide table with a
     verdict column per MR.
   - Net: 16 tables → 12 tables, saves 4 × 200 = 800 words.

Together these get to ~13,900 IST-counted words, leaving ~1,100 words of slack
for reviewer-driven additions.

## Other Elsevier requirements (verified, no manuscript change)

- IST is **not** in "Your Paper Your Way"; initial submission must follow
  formal `elsarticle` formatting (no double-spaced single-column free draft).
- Editorial Manager: `https://www.editorialmanager.com/infsof/`.
- Highlights submitted as a separate file (we keep them in `\begin{highlights}`
  for traceability and copy them at submission time).
- AI-generated images are **not** permitted in graphical abstracts (we ship
  no graphical abstract; the R3 figure is a matplotlib errorbar plot).
- Word template also accepted; we stay on LaTeX.

## Editorial-manager-time checklist (not yet executed)

- [ ] Copy `Highlights` block into a separate `highlights.txt` for upload.
- [ ] Fill in concrete CRediT role assignments per author (currently
      placeholder under double-anonymization).
- [ ] Generate the Elsevier Declaration of Competing Interest via
      `https://declarations.elsevier.com/` and attach the signed PDF.
- [ ] Confirm the GenAI declaration text matches the final tooling list.
- [ ] Recompute total word count after the trimming plan above is applied.

## Files touched in this pass

- `paper/ist-submission/main.tex` (title, abstract, highlight h3+h4, keywords,
  added CRediT / competing-interest / GenAI / data-availability sections).
- `paper/ist-submission/main.pdf` (rebuilt; 0 compile errors, 0 overfull boxes,
  0 unresolved citations).
- `CLAUDE.md` (added; records the standing IST submission requirements).
- `paper/28_ist_format_compliance_check.md` (this file).
