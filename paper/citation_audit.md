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
- `qi2025physicalfield` and `yu2025fluidvelocity` are DOI-verified but are not
  cited in the current submission draft. They remain related-work leads and
  novelty guardrails; citing them would require a deliberate Related Work
  expansion rather than metadata repair.

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
| `li2021fno` | VERIFIED | ICLR/OpenReview/arXiv record for Fourier Neural Operator; arXiv `2010.08895`, DOI `10.48550/arXiv.2010.08895`. | Neural-operator background. |
| `krishnapriyan2021failure` | VERIFIED | NeurIPS 2021 proceedings record. | PINN failure-mode background; no claim about MeshGraphNets. |
| `gopakumar2025calibrated` | VERIFIED (author list corrected 2026-06-18) | Calibrated Physics-Informed Uncertainty Quantification, Gopakumar, Gray, Zanisi, Nunn, Giles, Kusner, Pamela, Deisenroth; arXiv:2502.04406; ICML 2025. Prior local author order placed Pamela before Giles/Kusner and is fixed to the current arXiv record. | Calibrated UQ/residual comparator context; not MT evidence. |
| `baral2025xrepit` | VERIFIED_WITH_LIMITS | ScienceDirect page and DOI `10.1016/j.compfluid.2026.107075`. | Hybrid ML-CFD trust/switching context; not MT or relation-level violation statistics. |
| `wang2025deeponetfe` | VERIFIED_WITH_LIMITS | ScienceDirect page and DOI `10.1016/j.cma.2025.118319`. | Hybrid neural-operator/FE coupling context; not MT evidence. |
| `zhao2026noether` | VERIFIED_WITH_LIMITS | arXiv `2605.17390` and DOI `10.48550/arXiv.2605.17390`. | Preprint-level candidate pattern organization context only; not peer-reviewed validation of this paper's MRs. |
| `yang2020hierarchical` | VERIFIED | Publisher page jsjkx.com for DOI `10.11896/jsjkx.200200015`: 计算机科学 (Computer Science) 2020, 47(11A): 557-561. Authors verified as YANG Xiao-hua, YAN Shi-yu, LIU Jie, LI Meng (the prior BibTeX authors "Zhang Jian / Tsong Yueh Chen / Liu Huai / Yang Fan" were fabricated and have been corrected). Full Chinese abstract + keywords verified on the publisher page. | Three-level scientific-computing MR classification: physical-model / computational-model / code-model. The full Chinese abstract states "3 类蜕变关系"; no "likelihood" (似然) level exists in the published paper. An earlier draft transiently described it as four-level (incl. likelihood); reverted to the verified three-level on recheck. |

## Excluded or Non-Cited Leads

| Key | Status | Reason |
|---|---|---|
| `qi2025physicalfield` | VERIFIED_NOT_CITED | MCP paper-search/CrossRef verified DOI `10.1145/3796731.3796804`: ACM proceedings article, Proceedings of the 2025 5th International Conference on Computational Modeling, Simulation and Data Analysis, pp.470--482. It remains a close application lead on scenario-based physical-field prediction testing, but the current IST draft does not cite it because the Related Work already uses stronger method-neighbor citations for the paper's core RQ0--RQ4 gap. |
| `yu2025fluidvelocity` | VERIFIED_NOT_CITED | MCP paper-search/CrossRef verified DOI `10.1109/IAECST68792.2025.11415187`: IEEE proceedings article, 2025 7th International Academic Exchange Conference on Science and Technology Innovation, pp.178--182. It remains a close physical-field mutation-testing lead, but the current IST draft does not cite it because it would mainly add an application-adjacent example, not strengthen the exact novelty claim around measurement-floor admissibility, MR cards, and typed verdict ledgers. |

## Stage 5 additions (2026-06-06): three closest prior works after Socratic debate

| Key | Status | DOI / arXiv | Why added |
|---|---|---|---|
| `reichert2024hess` | VERIFIED | doi 10.5194/hess-28-2505-2024 | Closest prior on Contribution 3 (relation-indexed applicability map for a trained neural surrogate); must be cited in Section 2.4 and the discussion of active-transformation MT vs passive UQ. |
| `eniser2022relaxations` | VERIFIED | doi 10.1145/3533767.3534392 | Closest prior on Contribution 1 (calibrated MR tolerance / admissibility floor); must be cited where the admissibility predicate is introduced. |
| `duqueTorres2023bugornot` | VERIFIED | doi 10.1109/SANER56733.2023.00080 | Part of the 2023 cluster on bug-vs-inapplicability; closest prior on Contribution 2 (2D verdict). |
| `duqueTorres2023completePipeline` | VERIFIED (corrected 2026-06-18) | IEEE ICSME 2023 DOI `10.1109/ICSME58846.2023.00081`, pp.606--610; arXiv:2310.00338 lists the same two authors and links the related DOI. Prior local BibTeX incorrectly kept the arXiv DOI as the main DOI and included Klammer/Fischer as coauthors. | Companion 2023-cluster paper introducing MR constraints as a pipeline stage. |
| `duqueTorres2023metaTrimmer` | VERIFIED (corrected 2026-06-18) | IEEE SEAA 2023 DOI `10.1109/SEAA60479.2023.00063`, pp.370--377; arXiv:2307.15522 retained as eprint. Prior local BibTeX kept only the arXiv DOI. | Companion 2023-cluster paper automating domain-constraint derivation. |
| `verdecchia2023threats` | VERIFIED | doi 10.1016/j.infsof.2023.107329 | Threats-to-validity standard (IST 164, 2023); cited in Section Threats to Validity as the classification reference. |
| `ralph2021empirical` | VERIFIED | ACM SIGSOFT Empirical Standards | Reporting standard for SE empirical research; cited in Threats to Validity and the statistical plan. |

## P2-5 additions (2026-06-07): reference-coverage gap-closure

| Key | Status | DOI / arXiv | Why added |
|---|---|---|---|
| `chen2018mtSurvey` | VERIFIED | doi 10.1145/3143561 | Canonical MT review (ACM CSUR 51(1)); cited as the MT review of record in §2.2. |
| `kanewala2016graphkernel` | VERIFIED | doi 10.1002/stvr.1594 | Closest prior on predictive MR identification with graph kernels over scientific source code; cited in §2.3 alongside Hiremath et al. and Mandrioli et al. |
| `wang2021gradflow` | VERIFIED | doi 10.1137/20M1318043 | PINN training gradient-flow pathologies (SIAM J. Sci. Comput. 43(5)); cited in §2.4 alongside Krishnapriyan et al. to sharpen the case for relation-level validation independent of training stability. |
| `ying2025` | VERIFIED | doi 10.1016/j.infsof.2025.107903 | Recent same-venue MT-for-ML application (Inf. Softw. Technol. 188:107903, 2025) to tabular credit-scoring models; cited in §2.2 as a recent MT4ML example (not SciML). crossref-verified. |
| `najafi2026` | VERIFIED | doi 10.3390/w18020271 | Published review (Water 18(2):271, 2026) of physical-consistency and OOD-stress diagnostics for ML climate-downscaling surrogates; cited to contrast passive physical-consistency diagnostics with relation-space MR testing. crossref-verified. |
| `tsigkanos2023` | VERIFIED | doi 10.1007/978-3-031-35995-8_23 | LLM-based variable discovery for metamorphic testing of scientific software (ICCS 2023, LNCS pp.321--335); cited in §2.3 as the LLM-driven MR-identification prior alongside graph-kernel and data-driven approaches. crossref-verified. |

## Undermind-assisted related-work gap closure (2026-06-18)

Rows in this section were selected from the archived Undermind report and BibTeX under `research_assets/undermind/`. They are cited only to sharpen the Related Work gap around RQ0--RQ4, not as evidence for this paper's experimental results.

| Key | Status | DOI / venue | Why added |
|---|---|---|---|
| `chen2002pde` | VERIFIED_WITH_LIMITS | doi 10.1109/CMPSAC.2002.1045022; COMPSAC 2002 pp.327--333 | Foundational PDE-program MT case study. It supports the historical claim that physics/numerics-derived MRs predate this paper; it does not support MR-card assets, measurement-floor admissibility, or typed SciML verdicts. |
| `yang2021hydromt` | VERIFIED_WITH_LIMITS | doi 10.1029/2020WR029471; Water Resources Research 57, 2021 | Physics-informed MT for hydrological ML predictions where ground truth may be unavailable. It supports the learned-physical-model MT neighborhood; it does not provide executable MR cards, measurement-floor gates, or typed verdict ledgers. |
| `duqueTorres2024selecting` | VERIFIED_WITH_LIMITS | doi 10.1145/3639478.3639781; ICSE Companion 2024 pp.212--216 | Closest newer prior for standardized MR representation and constrained MR selection. It supports the claim that MR specification/constraint tooling exists; the manuscript distinguishes its physics-specific admissibility and evidence-ledger requirements. |
| `sun2026ccml` | VERIFIED_WITH_LIMITS | doi 10.1145/3796225; ACM Transactions on Software Engineering and Methodology, 2026 | Recent general MR specification language and supporting-system work. It is cited to avoid overclaiming around MR specification tooling; it does not cover SciML measurement floors or typed relation-domain verdicts. |

## Citation-integrity corrections + additions (2026-06-17, pre-submission §8.5 audit)

A full CrossRef re-verification (paper-search-mcp, DOI-first, field-by-field) found seven entries broken as previously recorded; all are corrected in `references.bib`, and the rows below **supersede** the corresponding rows above. BibTeX keys are unchanged. Full record: `docs/review_presubmission/reference_verification.md`.

| Key | Status | Corrected evidence | Claim limit |
|---|---|---|---|
| `kanewala2019scientific` | VERIFIED (corrected) | Prior DOI 10.1002/smr.1894 resolved to a different paper (Codabux et al. 2017, technical debt). Now Kanewala & Chen, "Metamorphic Testing: A Simple Yet Effective Approach for Testing Scientific Software", Computing in Science and Engineering 21(1):66--72, DOI 10.1109/MCSE.2018.2875368. crossref-verified. | Scientific-software MT background. |
| `olsen2019simulation` | VERIFIED (corrected) | Prior DOI 10.1109/TR.2019.2906504 was dead and title/authors/issue/pages wrong. Now Olsen & Raunak, "Increasing Validity of Simulation Models Through Metamorphic Testing", IEEE Transactions on Reliability 68(1):91--108, DOI 10.1109/TR.2018.2850315. crossref-verified. | Simulation-testing V&V background. |
| `duqueTorres2023bugornot` | VERIFIED (corrected) | Prior DOI 10.1109/SANER56733.2023.00080 resolved to a different paper (HFCommunity). Now DOI 10.1109/SANER56733.2023.00109, SANER 2023 pp.905--912. crossref-verified. | 2D verdict / bug-vs-inapplicability prior. |
| `raunak2021continuum` | VERIFIED (corrected) | DOI was valid but title/authors/pages wrong. Now "Metamorphic Testing on the Continuum of Verification and Validation of Simulation Models", Raunak & Olsen (Megan M.), MET 2021 pp.47--52, DOI 10.1109/MET52542.2021.00015. crossref-verified. | Oracle-continuum / simulation-model MT context. |
| `lin2020exploratory` | VERIFIED (corrected) | Author list was wrong. Now Xuanyi Lin, Michelle Simon, Nan Niu; CiSE 22(2):78--87, DOI 10.1109/MCSE.2018.2880577. crossref-verified. | Exploratory MT for scientific software. |
| `reichert2024hess` | VERIFIED (corrected) | Author list was wrong. Now Reichert, Ma, Hoge, Fenicia, Baity-Jesi, Feng, Shen; HESS 28(11):2505--2529, DOI 10.5194/hess-28-2505-2024. crossref-verified. | Closest prior on relation-indexed applicability for a trained surrogate. |
| `hiremath2021ocean` | VERIFIED (corrected) | Pages 42--46 (were 31--35); title/authors/venue unchanged. crossref-verified. | Automated MR identification for ocean system models. |
| `spieker2024trajectory` | VERIFIED | Spieker, Belmecheri, Gotlieb, Lazaar, "Evaluating Human Trajectory Prediction with Metamorphic Testing", 9th ACM MET Workshop 2024 pp.34--40, DOI 10.1145/3679006.3685071. crossref-verified. | Symmetry-MR + statistical violation-criterion neighbor (trajectory prediction, not SciML); cited in §2.3. |
| `spieker2025multimodal` | VERIFIED | Spieker, Lazaar, Gotlieb, Belmecheri, "Metamorphic Testing of Multimodal Human Trajectory Prediction", Information and Software Technology 188:107890, 2025, DOI 10.1016/j.infsof.2025.107890. crossref-verified. | Same-venue symmetry-MR + violation-criterion neighbor; cited in §2.3. |

## Maturity-reassessment additions (2026-06-17, real multi-vendor gateway panel)

A real multi-vendor gateway review panel (v37+v38) plus a paper-search-mcp deep-research pass flagged the MR fault-coverage / prioritization neighbourhood as the closest *uncited* prior to the validity--coverage duality (every panel reviewer read the duality as near-tautological). Both rows crossref-verified DOI-first this session.

| Key | Status | DOI / venue | Why added |
|---|---|---|---|
| `srinivasan2022prioritization` | VERIFIED | doi 10.1002/stvr.1807 | Srinivasan & Kanewala, "Metamorphic Relation Prioritization for Effective Regression Testing", Software Testing, Verification and Reliability 32(3):e1807, 2022. Fault-based and coverage-based MR prioritization; cited in §2.3 to contrast empirically-measured/optimized MR coverage with this paper's coverage-from-admissibility-gate result (the duality). crossref-verified. |
| `saha2019faultdetection` | VERIFIED | doi 10.1109/aitest.2019.00019 | Saha & Kanewala, "Fault Detection Effectiveness of Metamorphic Relations Developed for Testing Supervised Classifiers", IEEE Int. Conf. on Artificial Intelligence Testing (AITest) 2019, pp.157--164. Empirical MR fault-detection-effectiveness precedent (the published venue for the arXiv:1904.07348 preprint); cited in §2.3 alongside the prioritization work. crossref-verified. |
