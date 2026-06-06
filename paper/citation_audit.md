# Citation Audit for IST Submission Draft

Date: 2026-06-06

Scope: Cited-key audit for `paper/ist-submission/main.tex` and
`paper/ist-submission/references.bib`. This file is a submission-facing audit,
not a claim that every related-work lead in `paper/reference_ledger.md` is ready
for citation.

Decision rule:

- A cited key must exist in `references.bib`.
- A cited key must have a DOI, arXiv record, publisher page, official venue
  metadata, or a stable canonical source named below.
- A cited key may support only the claim-limit stated in the last column.
- `qi2025physicalfield` is excluded because the current ledger marks it
  unverified.
- `yu2025fluidvelocity` is not cited in the current submission draft; it remains
  a related-work lead and novelty guardrail until publisher-level verification
  and paper-text inspection are complete.

| Key | Submission status | Evidence source used in this pass | Claim limit in this paper |
|---|---|---|---|
| `pfaff2021meshgraphnets` | VERIFIED | ICLR/OpenReview/arXiv record for "Learning Mesh-Based Simulation with Graph Networks"; arXiv DOI `10.48550/arXiv.2010.03409`. | MeshGraphNets and cylinder-flow context only; no claim that this paper improves the model. |
| `barr2015oracle` | VERIFIED | IEEE TSE DOI `10.1109/TSE.2014.2372785`. | General test-oracle problem background. |
| `chen1998metamorphic` | VERIFIED | HKUST technical report `HKUST-CS98-01`. | Foundational MT concept. |
| `segura2016survey` | VERIFIED | IEEE TSE DOI `10.1109/TSE.2016.2532875`. | MT survey/background. |
| `chen2011ml` | VERIFIED | JSS DOI `10.1016/j.jss.2010.11.920`. | MT for machine-learning classifier background. |
| `kanewala2019scientific` | VERIFIED | Journal of Software: Evolution and Process DOI `10.1002/smr.1894`. | Scientific-software MR identification background; not direct SciML surrogate evidence. |
| `lin2020exploratory` | VERIFIED | Computing in Science and Engineering DOI `10.1109/MCSE.2018.2880577`. | Exploratory MT for scientific software; not direct cylinder-flow SciML evidence. |
| `olsen2019simulation` | VERIFIED | IEEE Transactions on Reliability DOI `10.1109/TR.2019.2906504`. | Simulation-testing V&V background. |
| `raunak2021continuum` | VERIFIED | NIST publication page and MET 2021 DOI `10.1109/MET52542.2021.00015`. | Simulation-model MT and oracle-continuum context. |
| `hiremath2021ocean` | VERIFIED_WITH_LIMITS | arXiv `2103.09782` and MET 2021 DOI `10.1109/MET52542.2021.00014`. | Automated MR identification for ocean system models; not neural PDE surrogates or this paper's tolerance calibration. |
| `mandrioli2025cps` | VERIFIED | IEEE TSE DOI `10.1109/TSE.2025.3563121` and repository metadata. | Design-assumption-based MRs for CPS; not direct SciML/PDE evidence. |
| `raissi2019pinn` | VERIFIED | Journal of Computational Physics DOI `10.1016/j.jcp.2018.10.045`. | PINN/SciML background. |
| `karniadakis2021piml` | VERIFIED | Nature Reviews Physics DOI `10.1038/s42254-021-00314-5`. | Physics-informed machine-learning background. |
| `li2021fno` | VERIFIED | ICLR/OpenReview record for Fourier Neural Operator. | Neural-operator background. |
| `krishnapriyan2021failure` | VERIFIED | NeurIPS 2021 proceedings record. | PINN failure-mode background; no claim about MeshGraphNets. |
| `gopakumar2025calibrated` | VERIFIED | ICML 2025/PMLR record. | Calibrated uncertainty/residual comparator context; not MT evidence. |
| `baral2025xrepit` | VERIFIED_WITH_LIMITS | ScienceDirect page and DOI `10.1016/j.compfluid.2026.107075`. | Hybrid ML-CFD trust/switching context; not MT or relation-level violation statistics. |
| `wang2025deeponetfe` | VERIFIED_WITH_LIMITS | ScienceDirect page and DOI `10.1016/j.cma.2025.118319`. | Hybrid neural-operator/FE coupling context; not MT evidence. |
| `zhao2026noether` | VERIFIED_WITH_LIMITS | arXiv `2605.17390` and DOI `10.48550/arXiv.2605.17390`. | Preprint-level candidate pattern organization context only; not peer-reviewed validation of this paper's MRs. |
| `yang2020hierarchical` | VERIFIED_WITH_LIMITS | Existing local BibTeX DOI `10.11896/jsjkx.200200015`. | Prior scientific-computing MR classification context; exact English metadata should be rechecked before final camera-ready submission. |

## Excluded or Non-Cited Leads

| Key | Status | Reason |
|---|---|---|
| `qi2025physicalfield` | UNVERIFIED | No trusted DOI, publisher, arXiv, official proceedings, Crossref, or Semantic Scholar-grade record was found in the prior ledger pass. It is excluded from the submission bibliography. |
| `yu2025fluidvelocity` | NOT_CITED_LEAD | The DOI lead exists, but the paper text and publisher landing page were not inspected in this pass. It remains a novelty guardrail and should not support detailed closest-work claims yet. |
