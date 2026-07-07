Dear Editor-in-Chief,

We submit the manuscript "Numerical-Decidability-Gated Metamorphic Testing for SciML Surrogates" for consideration as a regular paper in the Journal of Systems and Software.

The manuscript is written as a software-engineering testing and validation paper. It addresses a practical problem for software engineers and AI engineers who test scientific machine-learning surrogate software: a physics-derived metamorphic relation is not automatically a valid oracle-free test. A failed relation check may indicate a surrogate inconsistency, an invalid relation application, or a numerical artifact of the measurement operator.

The central contribution is an admissibility-gated workflow for turning candidate metamorphic relations into interpretable software verdicts. The workflow checks physical applicability, transformation preconditions, representation mapping, and numerical decidability before a relation is executed as a test. It then records the transformation, metric, tolerance, exclusions, and typed verdict in auditable relation records. This is a JSS software V&V method paper: it is not an MR-discovery paper, a production CFD validation study, a defect-rate study, a model-performance paper, or a tool demonstration without validation.

The validation combines analytical and empirical evidence. Analytically, the manuscript derives and instantiates an operator-floor argument for the P1 divergence check, showing when an absolute conservation verdict is not numerically decidable. Empirically, the same gate is exercised across MeshGraphNets cylinder flow, a compressible airfoil task, PointMLP, PINN, FNO, an independent periodic-advection workflow, cross-program executions, and five external issue/PR/commit-linked witnesses. These studies show how admitted relation sets determine the evidence a test may support, while keeping reliability, production-CFD, and real-world defect-rate claims outside scope.

The five issue/PR/commit-linked witnesses are a purposefully screened external witness corpus: they provide curated external evidence across several components, but are not statistically representative and are not presented as production-CFD validation.

We have prepared the submission to make scope, novelty, validation, and transparency visible at editorial screening. The paper is within JSS scope because it contributes a software V&V method, executable test artifacts, and evidence-reporting discipline for AI-enabled scientific software. Its evidence supports bounded method utility and auditability, not production reliability, representative defect-detection rates, or superiority over accuracy, residual, or uncertainty diagnostics. It is intended for readers interested in software testing, oracle-free validation, empirical software-engineering evidence, and verification of AI systems.

Replication and transparency materials are provided with the submission. The package includes relation records, executable runners, metric ledgers, run manifests, claim boundaries, and a separate supplementary evidence file.

The submission has been prepared to follow the Journal of Systems and Software and Elsevier submission requirements. The main manuscript is compiled in the Elsevier single-column LaTeX format and is 36 pages; highlights, supplementary evidence, declarations, author biographies, open-science checklist, and editable LaTeX source files are provided as separate submission files. The supplementary file contains detailed evidence tables so that the main manuscript remains within the JSS regular-paper page guidance while the evidence boundary remains inspectable.

The manuscript is original, is not under consideration elsewhere, and all authors have approved the submission. Author contributions, competing-interest declaration, generative-AI declaration, funding statement, and data/code availability statement are included in the submission materials.

Sincerely,

Meng Li, on behalf of all authors
