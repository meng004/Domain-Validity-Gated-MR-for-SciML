# Desk-Rejection Risk Audit from the Reference PDF

Reference PDF used for risk extraction: Miroslaw Staron, `How not to get your paper rejected -- From the editors' notebook`, Information and Software Technology 197 (2026) 108197, DOI 10.1016/j.infsof.2026.108197.

Purpose: check whether the JSS package still exhibits desk-rejection risks identified by the editorial note. This is a risk audit, not a claim that JSS or IST will accept the paper.

| PDF-derived rejection risk | Current package evidence | Audit verdict | Residual action |
|---|---|---|---|
| Scope misalignment: manuscript is not clearly for software engineers. | Abstract frames a software V&V problem for SciML surrogate software; cover letter states JSS fit as a software-engineering testing and validation method. | No obvious desk-reject trigger found. | Keep the V&V framing visible; do not recast as a pure SciML modeling paper. |
| Low novelty/impact: tool or method described without explaining contribution to SE practice. | Introduction states numerical-decidability gating, executable MR cards, typed verdicts, and evidence ledgers; cover letter states how claims are bounded. | Mitigated, but reviewer-dependent because the contribution is specialized. | Preserve the reader map and closest-prior positioning. |
| Insufficient empirical validation or premature work. | Main paper reports bounded executions; supplement and open-science checklist expose MR cards, ledgers, manifests, and external issue/PR/commit-linked witnesses. | Mitigated within the paper's bounded claims. | Do not claim production validation, representative defect rates, or trained-SUT correctness. |
| Failure to follow reporting guidelines. | Separate highlights, declarations, author biographies, source zip, supplementary appendix, and availability checklist are present; JSS precheck passes. | No obvious desk-reject trigger found. | Editorial Manager item labels still need manual selection during upload. |
| Weak replicability/transparency. | Zenodo DOI, repository URL, claim ledger, experiment ledger, runners, and fail-closed validators are declared. | Mitigated. | Ensure the submitted repository/archive state matches the DOI and package manifest. |
| Inappropriate audience style or unclear reviewer assignment. | Abstract, cover letter, and reader map state the software-testing problem and evidence boundary; package avoids broad SciML reliability claims. | Mitigated, but conceptual density remains a normal review risk. | Retain definitions and avoid adding new terminology in final upload edits. |

Concrete repairs made during this audit: the cover letter was corrected to the verified 34-page main PDF; the title was aligned with the current contribution as `Numerical-Decidability-Gated Metamorphic Testing for SciML Surrogates`; and the abstract/introduction replaced broad soundness wording with bounded admissibility and interpretable-verdict wording. These repairs remove an internal inconsistency, reduce overclaim risk, and lower reviewer-usability risk without changing empirical claims.

Topic-drift check: the audit stays on JSS/SE desk-rejection risks and does not convert the paper into a production-CFD validation or statistical defect-corpus study.
