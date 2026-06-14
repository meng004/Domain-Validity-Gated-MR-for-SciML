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
| `gopakumar2025calibrated` | VERIFIED (author list corrected 2026-06-06) | Calibrated Physics-Informed Uncertainty Quantification, Gopakumar, Gray, Zanisi, Nunn, Pamela, Giles, Kusner, Deisenroth; arXiv:2502.04406; ICML 2025 (PMLR v267). Prior local author list was wrong and is fixed. | Calibrated UQ/residual comparator context; not MT evidence. |
| `baral2025xrepit` | VERIFIED_WITH_LIMITS | ScienceDirect page and DOI `10.1016/j.compfluid.2026.107075`. | Hybrid ML-CFD trust/switching context; not MT or relation-level violation statistics. |
| `wang2025deeponetfe` | VERIFIED_WITH_LIMITS | ScienceDirect page and DOI `10.1016/j.cma.2025.118319`. | Hybrid neural-operator/FE coupling context; not MT evidence. |
| `zhao2026noether` | VERIFIED_WITH_LIMITS | arXiv `2605.17390` and DOI `10.48550/arXiv.2605.17390`. | Preprint-level candidate pattern organization context only; not peer-reviewed validation of this paper's MRs. |
| `yang2020hierarchical` | VERIFIED_WITH_LIMITS | Publisher page jsjkx.com for DOI `10.11896/jsjkx.200200015`: 计算机科学 (Computer Science) 2020, 47(11A): 557-561. Authors verified as YANG Xiao-hua, YAN Shi-yu, LIU Jie, LI Meng (the prior BibTeX authors "Zhang Jian / Tsong Yueh Chen / Liu Huai / Yang Fan" were fabricated and have been corrected). | Prior scientific-computing MR classification. NOTE: the public abstract page lists three levels (physical-model / computing-model / code-model); the author reports a fourth "likelihood" (似然) level in the full text. Recheck the full text and the exact English level names (esp. the likelihood level) before camera-ready. |

## Excluded or Non-Cited Leads

| Key | Status | Reason |
|---|---|---|
| `qi2025physicalfield` | UNVERIFIED | No trusted DOI, publisher, arXiv, official proceedings, Crossref, or Semantic Scholar-grade record was found in the prior ledger pass. It is excluded from the submission bibliography. |
| `yu2025fluidvelocity` | NOT_CITED_LEAD | The DOI lead exists, but the paper text and publisher landing page were not inspected in this pass. It remains a novelty guardrail and should not support detailed closest-work claims yet. |

## Stage 5 additions (2026-06-06): three closest prior works after Socratic debate

| Key | Status | DOI / arXiv | Why added |
|---|---|---|---|
| `reichert2024hess` | VERIFIED | doi 10.5194/hess-28-2505-2024 | Closest prior on Contribution 3 (relation-indexed applicability map for a trained neural surrogate); must be cited in Section 2.4 and the discussion of active-transformation MT vs passive UQ. |
| `eniser2022relaxations` | VERIFIED | doi 10.1145/3533767.3534392 | Closest prior on Contribution 1 (calibrated MR tolerance / admissibility floor); must be cited where the admissibility predicate is introduced. |
| `duqueTorres2023bugornot` | VERIFIED | doi 10.1109/SANER56733.2023.00080 | Part of the 2023 cluster on bug-vs-inapplicability; closest prior on Contribution 2 (2D verdict). |
| `duqueTorres2023completePipeline` | VERIFIED_PREPRINT | arXiv:2310.00338 | Companion 2023-cluster paper introducing MR constraints as a pipeline stage. |
| `duqueTorres2023metaTrimmer` | VERIFIED_PREPRINT | arXiv:2307.15522 | Companion 2023-cluster paper automating domain-constraint derivation. |
| `verdecchia2023threats` | VERIFIED | doi 10.1016/j.infsof.2023.107329 | Threats-to-validity standard (IST 164, 2023); cited in Section Threats to Validity as the classification reference. |
| `ralph2021empirical` | VERIFIED | ACM SIGSOFT Empirical Standards | Reporting standard for SE empirical research; cited in Threats to Validity and the statistical plan. |

## P2-5 additions (2026-06-07): reference-coverage gap-closure

| Key | Status | DOI / arXiv | Why added |
|---|---|---|---|
| `chen2018mtSurvey` | VERIFIED | doi 10.1145/3143561 | Canonical MT review (ACM CSUR 51(1)); cited as the MT review of record in §2.2. |
| `kanewala2016graphkernel` | VERIFIED | doi 10.1002/stvr.1594 | Closest prior on predictive MR identification with graph kernels over scientific source code; cited in §2.3 alongside Hiremath et al. and Mandrioli et al. |
| `wang2021gradflow` | VERIFIED | doi 10.1137/20M1318043 | PINN training gradient-flow pathologies (SIAM J. Sci. Comput. 43(5)); cited in §2.4 alongside Krishnapriyan et al. to sharpen the case for relation-level validation independent of training stability. |
