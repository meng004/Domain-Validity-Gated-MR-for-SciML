Dear Editor-in-Chief,

We submit the manuscript "Numerical-Decidability-Gated Metamorphic Testing for SciML Surrogates" for consideration as a regular paper in the Journal of Systems and Software.

The paper addresses a software verification and validation problem that arises when scientific machine-learning surrogate software is tested with metamorphic relations. A physics-derived relation is not automatically an interpretable oracle-free test: a failure may come from a surrogate inconsistency, an invalid relation application, or a numerical artifact of the measurement operator. The manuscript therefore treats numerical decidability and physical admissibility as preconditions for relation-level verdicts.

The central contribution is a numerical-decidability gate that decides whether a candidate relation may support a relation-level software verdict. The gate is implemented through MR cards, executable runners, typed verdicts, and fail-closed claim/evidence ledgers. For P1 discrete divergence on shape-regular triangular meshes, the paper gives a local operator-floor bound and instantiates it on the cylinder-flow mesh, with additional bounded executions over MeshGraphNets, PointMLP, PINN, FNO, airfoil, periodic-advection, public-data, external issue/PR/commit-linked, and cross-program settings. These executions are used to show how detector coverage follows the admitted relation set, not to claim baseline superiority or general SciML reliability.

We keep the evidence boundary explicit. The periodic-advection workflow is an independent full-chain synthetic PDE task, and the RealPDEBench foil check is a production-adjacent public-data preflight with an inconclusive typed verdict. The purposefully screened external witness corpus contains five public issue/PR/commit-linked witnesses across DeepXDE, NeuralOperator, PhiFlow/PhiML, and JAX-CFD. The supplement reports the inclusion/exclusion logic, deferred candidates, covered software components, and evidence ladder for this curated external evidence. These materials address the concern that the method is only a self-made cylinder-flow demonstration, but they are not statistically representative and are not presented as production-CFD validation, trained-SUT correctness proof, representative defect sampling, or a real-world defect-detection rate.

The manuscript fits JSS because it presents a software-engineering method for testing and validation, combines formal/numerical reasoning with empirical execution evidence, and provides reproducible artifacts intended to make the evidence boundary auditable.

The submitted main PDF is 34 pages in the single-column Elsevier form after moving detailed claim-to-evidence, cross-program, secondary-baseline, cross-family, effective-N, primary-result, and claim-boundary tables to supplementary material. The remaining length is driven by the regular-paper contribution, primary empirical evidence, and references needed to make the empirical claims traceable.

The manuscript is original, is not under consideration elsewhere, and all authors have approved the submission. Author contributions, competing-interest declaration, generative-AI declaration, and data/code availability statements are included in the submission materials.

Sincerely,

Meng Li, on behalf of all authors
