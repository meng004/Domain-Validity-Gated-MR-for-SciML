# Periodic Advection Primary Workflow Provenance

Generated: 2026-07-03T11:39:17Z

Command:

```bash
python3 tools/run_periodic_advection_primary_workflow.py --n-eval 10
```

This run trains deterministic NumPy periodic-convolution surrogates on synthetic
2D scalar periodic-advection fields and records the complete rubric-to-verdict
chain. It uses no external dataset, network access, GPU runtime, or sibling
repository writes.

Aggregate report: `research_assets/runs/periodic-advection-primary-workflow/periodic_advection_primary_workflow_report.json`

Claim boundary: independent synthetic PDE/SciML surrogate evidence only; not
production CFD, real-defect, reliability, or model-accuracy evidence.
