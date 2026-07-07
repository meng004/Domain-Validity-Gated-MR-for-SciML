# Cover Letter: Information and Software Technology (regular paper)

To the Editor-in-Chief
Information and Software Technology

Dear Editor,

We submit our manuscript, "Domain-Validity-Gated Metamorphic Testing of Scientific ML Surrogates," for consideration as a regular research paper in Information and Software Technology.

**Problem and motivation.** Scientific machine-learning (SciML) surrogates, learned replacements for expensive numerical simulators, are now deployed in fluid dynamics, climate, and engineering pipelines, but validating them is an open software V&V problem: for arbitrary inputs there is no cheap exact output to test against (the oracle problem), and average rollout accuracy does not reveal whether a model preserves the physical relations it should. Metamorphic testing is the natural oracle-free response, yet a candidate relation is not automatically a valid test: its preconditions, output mapping, and the numerical floor of its scoring operator determine whether a violation is even meaningful. Treating physically motivated transformations as automatically valid relations hides exactly the assumptions that decide whether a failed test is a real defect.

**Contribution.** The paper treats MR use for SciML as a domain-validity problem. Its central idea is a measurement-floor admissibility gate: a candidate relation is admitted only when its verdict tolerance dominates the intrinsic error floor of its own discrete measurement operator, a property of the discretization fixed before any fault or SUT is considered (grounded in closed form, to within 0.5% of the measured floor, for the deployed mesh). To our knowledge this numerical-decidability test is new for learned SciML surrogates evaluated out of distribution. Built around this gate, the workflow adds a typed two-dimensional inadmissibility verdict that separates a model-level violation from an out-of-relation-domain application, and converts each admitted relation into an MR card, executable runner, and evidence ledger. As a bounded discussion implication rather than a separate claim, the admitted MR set is also used to read where detector coverage and blind spots fall; this coverage reading is stated as a qualitative, falsifiable hypothesis, not a calibrated coverage law.

**Evidence.** The workflow is exercised on two CFD tasks and two official datasets (incompressible cylinder flow across four architectures including the NVIDIA PhysicsNeMo production implementation, and compressible airfoil flow), transfers unchanged to a second PDE family (PINN/FNO on Burgers and heat), and is additionally executed end-to-end across five program types spanning parabolic, hyperbolic, stiff-ODE, conservation-law, and Monte-Carlo-transport solvers (including a real OpenMC k-eigenvalue run on CPU). This coverage hypothesis is tested adversarially: detection collapses at the boundary where a fault becomes simultaneously permutation- and mirror-symmetric, and removing an inadmissible relation on a second subject removes exactly its coverage. Every reported number is bound to a tracked artifact through a fail-closed claim ledger, and the replication package is archived on Zenodo.

**Industrial relevance.** The method turns implicit expert sanity checks into auditable, oracle-free, executable test assets with explicit validity records, directly applicable to teams deploying learned surrogates in place of trusted solvers. It complements, rather than competes with, accuracy monitoring and uncertainty quantification: the case study shows a surrogate that is accurate in-distribution yet still violates a gate-admitted physical relation by roughly an order of magnitude, a failure an output-magnitude monitor does not surface.

**Scope and honesty.** We state the boundary plainly. The paper is a V&V method paper, not a claim of superiority over accuracy- or uncertainty-based validation, and the empirical evidence is deliberately scoped (one primary task family, bounded cross-family and cross-program checks); the coverage implication is stated as a qualitative, falsifiable hypothesis with its refutation conditions made explicit. We believe this fit, a software-testing methodology contribution for an emerging and consequential class of systems, matches IST's scope and its emphasis on empirical software-engineering research.

**Declarations.** This manuscript is original, has not been published previously, and is not under consideration elsewhere. All authors have approved the submission. We declare no competing interests. Our use of generative-AI tools (restricted to code scaffolding, copy-editing, and reference cross-checking, with no AI-generated data, results, or citations) is declared in the manuscript. The work was supported by the funders acknowledged in the manuscript.

Thank you for considering our submission.

Sincerely,
Meng Li, on behalf of all authors (Xiaohua Yang, Jie Liu, Shiyu Yan)
School of Computing, University of South China, Hengyang, China
mlemon@usc.edu.cn
