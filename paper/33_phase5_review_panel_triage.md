# Phase 5 Review Panel v4 Triage

Date: 2026-06-11

Artifact: `research_assets/runs/academic-review-panel-phase5-baseurl-v1/review_panel_report.json`

## Gate outcome

Phase 5 gate from `paper/32_ist_empirical_80_gap_closure_plan.md`:

- empirical rigor >= 8.0
- overall >= 7.8
- accept probability >= 0.65
- clarity >= 7.0

Observed v4 panel result:

| Metric | Observed | Gate | Status |
|---|---:|---:|---|
| Empirical rigor | 6.6 | 8.0 | not met |
| Overall dimension mean | 7.34 | 7.8 | not met |
| Mean accept probability | 0.452 | 0.65 | not met |
| Clarity | 7.0 | 7.0 | met |
| Majority verdict | major_revision | minor-or-better target | not met |

## Dominant reviewer concerns

The five-reviewer panel converged on four concerns:

1. **Narrow empirical base.** The MGN evidence is still one architecture family / one dataset; K=6 is a seed/configuration roster, not six independent SUTs.
2. **Partially operationalized domain axis.** The two-dimensional verdict has a numeric D-score for mirror-y, but other MR classes still use qualitative placement.
3. **Fault-catalogue realism.** The seeded faults and adversarial probes are useful stress tests but remain synthetic/gross rather than real-world defect evidence.
4. **Residual clarity/repetition.** Phase 4 raised clarity to the gate threshold, but some reviewers still saw too much boundary language and ledger-heavy prose.

## Decision

The v4 panel does **not** meet the Phase 5 submission gate. Because the failed dimensions are mostly evidence breadth and domain-axis operationalization, this should not be repaired by prose alone. The honest next step is a targeted v5 cycle only if new evidence is added, for example:

- add at least one genuinely different SUT family or architecture-family artifact;
- extend domain-violation scoring beyond mirror-y to at least one non-geometric MR class;
- replace or supplement synthetic seeded faults with naturally occurring regression/fix-history faults or a stronger adversarial catalogue;
- archive the exact replication package on a permanent DOI-backed service before final submission.

Until such evidence exists, the manuscript should stay in **major-revision / not-yet-submit** status rather than claiming that Phase 5 passed.
