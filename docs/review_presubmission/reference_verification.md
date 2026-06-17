# Reference verification — pre-submission (§8.5 hard-block gate)

> Date: 2026-06-17 · Venue: Elsevier IST · Bib: `paper/ist-submission/references.bib` (33 entries)
> Method: every entry verified against CrossRef via paper-search-mcp `get_crossref_paper_by_doi`
> (DOI-first), with `search_crossref` / `search_dblp` / `search_arxiv` fallback. Each DOI was
> opened and its returned title + author list + venue + volume/issue/pages compared field-by-field
> against the BibTeX. A first-pass subagent under-reported author-list errors (it caught page/issue
> slips on `lin2020exploratory` and `reichert2024hess` but missed that their author lists were wrong);
> every flagged entry was therefore re-verified by hand against the live CrossRef record.

## Outcome

- ✗ (broken as written) = **0 after fixes** (was 7 before). Gate **PASS**.
- All 33 cited works exist; 7 entries had wrong metadata (3 with a DOI that resolved to a
  *different* paper, 4 with confabulated author lists and/or wrong pages/issue). All 7 corrected
  in place; BibTeX keys unchanged, so no `\cite` in `main.tex` is affected.

## Fixes applied (each confirmed against the live CrossRef record)

| key | defect (verified) | correction |
|---|---|---|
| `kanewala2019scientific` | **Non-existent as specified.** DOI `10.1002/smr.1894` resolves to Codabux et al. 2017, "An empirical assessment of technical debt practices in industry" (JSEP 29(10)). No "Metamorphic Testing of Scientific Software: A Machine Learning Approach" exists in JSEP 2019. | Replaced with the real Kanewala & Chen 2019 paper matching the citation intent: "Metamorphic Testing: A Simple Yet Effective Approach for Testing Scientific Software", Computing in Science & Engineering 21(1):66–72, DOI `10.1109/MCSE.2018.2875368`. |
| `olsen2019simulation` | **Dead DOI** `10.1109/TR.2019.2906504` (empty). Title, authors (Philip C. Olsen + Rothermel), issue 4, pages 1322–1337 all wrong. | Real paper: "Increasing Validity of Simulation Models Through Metamorphic Testing", Megan Olsen & M. S. Raunak, IEEE TR 68(1):91–108, DOI `10.1109/TR.2018.2850315`. |
| `duqueTorres2023bugornot` | DOI `10.1109/SANER56733.2023.00080` resolves to a different paper (Ait et al., "HFCommunity", p728–732). | Correct DOI `10.1109/SANER56733.2023.00109`, pages 905–912 (title/authors were already correct). |
| `raunak2021continuum` | DOI valid but BibTeX title "A Continuum of Oracles for Testing Scientific Software" (no such paper found) + authors (Simko, Kuhn) + pages 18–25 all wrong. | DOI's real record: "Metamorphic Testing on the Continuum of Verification and Validation of Simulation Models", Raunak & Olsen (Megan M.), MET 2021 p47–52. Title/authors/pages corrected; DOI kept. |
| `lin2020exploratory` | **Wrong author list.** BibTeX had Qin Lin, Kuo, Liu, Poon, Chen, Tse; real authors are Xuanyi Lin, Michelle Simon, Nan Niu. Pages 78–89→78–87. | Authors + pages corrected (title/venue/year/volume/issue already correct). |
| `reichert2024hess` | **Wrong author list.** BibTeX had Marvin Reichert + the LSTM-hydrology group (Kratzert, Klotz, Gauch, Nearing, Hochreiter, …); real authors are Peter Reichert, Kai Ma, Marvin Höge, Fabrizio Fenicia, Marco Baity-Jesi, Dapeng Feng, Chaopeng Shen. Issue 12→11. | Author list + issue corrected. |
| `hiremath2021ocean` | Pages 31–35 → 42–46 (title/authors/venue correct). | Pages corrected. |

In-text author-year citations are unaffected by the author corrections (every first-author surname
is unchanged: Kanewala, Olsen, Raunak, Lin, Reichert, Hiremath); only the rendered reference list
and the two-author "X and Y" / "et al." forms become correct.

## Verified clean (no change needed)

The remaining 26 entries were checked and match CrossRef exactly: `pfaff2021meshgraphnets`,
`barr2015oracle`, `segura2016survey`, `chen2011ml` (first author Xie), `kanewala2019scientific`'s
sibling `kanewala2016graphkernel`, `mandrioli2025cps`, `raissi2019pinn`, `karniadakis2021piml`,
`li2021fno`, `krishnapriyan2021failure`, `gopakumar2025calibrated`, `baral2025xrepit`,
`wang2025deeponetfe`, `verdecchia2023threats`, `eniser2022relaxations`,
`duqueTorres2023completePipeline`, `duqueTorres2023metaTrimmer`, `chen2018mtSurvey`,
`wang2021gradflow`, `ying2025`, `najafi2026`, `tsigkanos2023`.

△ (existence confirmed, not in CrossRef — acceptable per §8.6):
- `chen1998metamorphic` — original HKUST tech report HKUST-CS98-01 (also rehosted at arXiv:2002.12543).
- `zhao2026noether` — author self-cite, arXiv:2605.17390 (preprint, not yet DOI-indexed).
- `yang2020hierarchical` — Chinese CNKI venue (计算机科学 47(11A)), not in international indexes.
- `ralph2021empirical` — ACM SIGSOFT Empirical Standards community asset, cited as `@misc`.
