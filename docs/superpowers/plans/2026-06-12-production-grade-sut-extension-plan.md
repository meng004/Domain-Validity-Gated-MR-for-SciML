# Plan: Production-Grade SUT Extension (P0c) — Three External CFD/SciML Objects

Date: 2026-06-12
Status: DESIGN ONLY — stop after this document; do **not** start installation/training/runs yet.
Required workflow: superpowers plan-driven execution (`docs/superpowers/plans/`), with each future implementation task tracked by checkbox.

## 0. Decision answer

Yes, adding three production-grade experimental objects is feasible and would materially strengthen the paper, but only if the paper treats them as **artifact-gated external SUT executions**, not as name-dropping. The correct next step is a staged production-grade extension: one same-physics PhysicsNeMo example, one external-aerodynamics GNN model, and one external-aerodynamics neural-operator model. The goal is to close the remaining reviewer concern that the evidence is still mostly one local MeshGraphNet family plus toy/local architectures.

The three proposed objects are:

1. **NVIDIA PhysicsNeMo MeshGraphNet for transient vortex shedding** — closest production-framework analogue to the current cylinder-flow MeshGraphNet case.
2. **NVIDIA PhysicsNeMo AeroGraphNet for external aerodynamic evaluation** — graph-based production aerodynamics object with different geometry/task scale.
3. **NVIDIA PhysicsNeMo DoMINO for external aerodynamics** — non-GNN neural-operator-style production aerodynamics object.

Primary sources checked before this plan:

- NVIDIA PhysicsNeMo documentation lists examples including “MeshGraphNet for transient vortex shedding” and CFD examples including “AeroGraphNet for external aerodynamic evaluation” and “DoMINO: Decomposable Multi-scale Iterative Neural Operator for External Aerodynamics”: <https://docs.nvidia.com/physicsnemo/latest/index.html>.
- OpenFOAM documentation confirms maintained production CFD tutorials and incompressible-flow examples, including flow around a cylinder, useful as reference-data / baseline-solver context rather than as a SciML SUT: <https://www.openfoam.com/documentation/tutorial-guide>.
- OpenFOAM Foundation technical guides show active 2026 maintenance/release context, useful for solver-reference credibility if we need external reference generation: <https://openfoam.org/guides/>.


## 0.1 Selection standard: choose objects by argument function, not by convenience

The production objects are selected to support the paper's logical burden. A candidate is acceptable only if it satisfies all mandatory criteria and adds a distinct evidential role.

### Mandatory criteria

1. **Production-grade provenance.** The object must come from a maintained external framework, service, or documented industrial/production-oriented example, with official documentation or repository references.
2. **SciML/CFD SUT status.** The object must be a learned surrogate/model or model-serving endpoint, not only a CFD solver. OpenFOAM can support reference data, but it is not counted as one of the three SciML SUTs.
3. **Artifact-gated executability.** The future run must be able to produce source input, follow-up input, source output, follow-up output, mapped output, metric ledger, and claim-limited report; if checkpoint/data/API access blocks this, the object is recorded as blocked rather than replaced by a toy model.
4. **MR-contract visibility.** The object must expose enough input/output structure to audit at least one relation class: representation ordering, geometric transform, integrated aerodynamic quantity, or conservation/flux diagnostic.
5. **Claim-boundary usefulness.** The object must help distinguish admitted, rejected, downgraded, and deferred relations without weakening the admissibility predicate.

### Diversity criteria

The set of three should jointly cover:

- **Near-domain transfer:** one object close to the current cylinder/vortex-shedding MGN setup, to test whether results port to a maintained production framework.
- **Geometry/task broadening:** one object with production external-aerodynamics geometry and integrated engineering outputs.
- **Architecture broadening:** one object whose model contract is not a MeshGraphNet-style message-passing graph, to show that the method is not a graph-equivariance trick.

### Final selection matrix

| Candidate | Mandatory fit | Distinct role in proof | Main risk | Decision |
|---|---|---|---|---|
| PhysicsNeMo MeshGraphNet transient vortex shedding | Maintained PhysicsNeMo example; same CFD/vortex-shedding theme; graph contract visible | Near-domain external-framework replication of the current MGN case | Checkpoint/data/runtime availability must be audited | **Select as Object A** |
| PhysicsNeMo AeroGraphNet external aerodynamics | Maintained PhysicsNeMo external-aero example; predicts pressure/wall shear/drag-like outputs; graph contract visible | Production-scale geometry/task broadening with integrated aerodynamic quantities | Dataset access may require request or DrivAerNet setup | **Select as Object B** |
| PhysicsNeMo DoMINO / DoMINO Automotive Aero | Maintained/non-GNN external-aero model; documented point-cloud/neural-operator-style contract; NIM/pretrained route may exist | Architecture broadening beyond graph MGN/AeroGraphNet | Data/API/container access and GPU requirements | **Select as Object C** |
| OpenFOAM tutorials | Production CFD solver, not learned SciML SUT | Reference generation / sanity baseline only | Not an MR-tested SciML surrogate | Do **not** count as one of the three SUTs |
| Local PointMLP / local FNO / local PINN | Artifact-feasible but not production-grade | Already useful as local controls | Does not answer production-grade credibility objection | Do **not** use for P0c |
| Three variants from one local MGN family | Artifact-feasible | Replication within family | Fails production/external diversity criteria | Do **not** use for P0c |

This standard changes the interpretation of the three selected objects: they are not chosen because they are easy to run; they are chosen because each closes a different evidential gap. PhysicsNeMo MeshGraphNet addresses same-physics external-framework transfer, AeroGraphNet addresses production external-aerodynamics graph evidence, and DoMINO addresses non-graph production surrogate evidence.

## 1. Paper-level argumentation scheme

### 1.1 Current core argument

The paper argues that SciML metamorphic testing should be **domain-validity-gated** before execution. Its claims are not “more MRs” or “higher accuracy”; the claims are:

- **C-A: Validity gate.** An MR is executable only when physical/software basis, preconditions, boundary/output compatibility, and numerical decidability hold together.
- **C-B: MR-card-to-verdict chain.** A candidate should become an auditable test asset with source/follow-up construction, metric, tolerance, raw outputs, and relation-level verdict.
- **C-C: Two-dimensional interpretation.** A violation must be interpreted jointly with domain violation; high relation violation under high domain violation is not the same claim as a low-domain/high-relation SUT inconsistency.
- **C-D: Applicability mapping.** Running relation-indexed transformations identifies which physical/software relation breaks, not just whether prediction error is high.

### 1.2 Current weakness after S4/S5 and PointMLP

The latest evidence improves the situation but still leaves one credible reviewer objection:

- S4/S5 are same-domain MeshGraphNet configuration variants, not independent production SUTs.
- PointMLP is different architecture but light-weight and locally constructed, so it may be dismissed as a convenience surrogate rather than production-grade SciML.
- FNO/PINN evidence is useful, but outside cylinder-flow / production CFD deployment context.

### 1.3 How the three production-grade objects support the paper

| Paper claim | Current support | Added production-grade support | Why it matters |
|---|---|---|---|
| Validity gate is not MeshGraphNet-specific | MGN + PINN + FNO + PointMLP | PhysicsNeMo MGN + AeroGraphNet + DoMINO | Shows the gate applies to maintained external SciML/CFD model families. |
| MR cards are executable artifacts, not prose | Existing local runners and ledgers | Same artifact contract ported to each production object | Reviewers can inspect source/follow-up outputs and ledgers. |
| Domain-violation axis prevents overclaiming | Mirror-y downgrade and D-score | External aerodynamics will force more boundary/geometry rejection decisions | Demonstrates value of rejecting or downgrading invalid relations on real tasks. |
| Relation-indexed applicability map | MGN and synthetic extensions | Cross-object table of admitted/rejected/deferred relations | Turns the method from one-case evidence into a scoped production-object map. |
| Empirical credibility | K=6 local roster + PointMLP | Three named, maintained production examples | Addresses “toy/local surrogate” criticism without claiming broad reliability. |

The paper should **not** claim universal generality after these runs. The allowed upgraded claim is:

> The artifact-gated workflow was executed on three additional maintained production-framework CFD/SciML objects spanning graph and neural-operator model families; the same validity gate produced admitted, rejected, downgraded, and deferred relation decisions with raw source/follow-up outputs and relation-level verdicts.

Forbidden upgraded claims:

- “The method is validated for all CFD surrogates.”
- “PhysicsNeMo models are unreliable/reliable in general.”
- “Production-grade pass/fail rates are geometry-independent.”
- “OpenFOAM/PhysicsNeMo accuracy is benchmarked or improved.”

## 2. Research questions

### RQ-P1 — Portability of the validity gate

Can the same four-part admissibility predicate classify MR candidates on three production-grade CFD/SciML objects without weakening the rules?

Expected evidence:

- Count of candidates admitted / rejected / downgraded / deferred per object.
- Qualitative audit of why invalid candidates fail.
- No execution of exact MRs when preconditions fail.

### RQ-P2 — Executability of the artifact chain

For each production object, can we record source inputs, follow-up inputs, raw source outputs, raw follow-up outputs, mapped outputs, metric ledgers, thresholds, and relation verdicts?

Expected evidence:

- `full_workflow_flags` all true per object.
- Raw artifact existence guard equivalent to existing real-SUT runners.
- Reproducible command, model version/commit, checkpoint/data SHA where available.

### RQ-P3 — Cross-object relation behavior

Which relation classes remain stable across production objects, and which become out-of-domain or numerically undecidable?

Expected evidence:

- Representation relations such as node/element permutation should pass where the model representation is equivariant by construction.
- Physical symmetry relations may be rejected/downgraded when geometry or boundary conditions break symmetry.
- Conservation diagnostics may remain diagnostic/deferred unless operator floor and reference tolerance are calibrated.

### RQ-P4 — Added empirical credibility without overclaiming

Does adding production-grade objects change the paper’s evidence status from “local pilot plus local extensions” to “artifact-gated workflow demonstrated on maintained external CFD/SciML examples,” while preserving bounded claims?

Expected evidence:

- Claim-ledger entries with strict wording boundaries.
- Manuscript table separating production-object workflow evidence from reliability/accuracy claims.
- Reviewer-facing threat statement that three production objects are still not a statistical sample of all CFD/SciML systems.

## 3. Experimental objects

### Object A — PhysicsNeMo MeshGraphNet transient vortex shedding

**Role in argument:** closest external production-framework analogue to the current cylinder-flow MeshGraphNet case.

**Why this object:**

- Same broad physics class: transient vortex shedding / flow around obstacle.
- Same broad model style: mesh graph network, but in NVIDIA’s maintained PhysicsNeMo framework rather than local/sibling code.
- Best bridge between the existing cylinder-flow results and production-framework evidence.

**Candidate MRs:**

- Representation MR: node/mesh-element permutation equivariance, if data structure exposes reorderable mesh nodes and connectivity.
- Boundary/geometry validity MR: translation/reflection candidates should often be rejected unless boundary conditions and geometry support them.
- Time-step / rollout consistency diagnostic: one-step output consistency under recorded model convention.
- Conservation diagnostic: reference-relative divergence or flux diagnostic, only if mesh/operator and reference data support it.

**Expected result:**

- Node/element permutation: pass to numerical tolerance if the model is graph-equivariant and preprocessing does not inject order dependence.
- Mirror/reflection: likely admitted only for symmetric generated cases; otherwise downgraded to OOD-stress or rejected.
- Conservation: likely diagnostic/deferred unless a calibrated reference/operator floor exists.

### Object B — PhysicsNeMo AeroGraphNet external aerodynamic evaluation

**Role in argument:** production graph-based aerodynamics object on a different geometry/task scale.

**Why this object:**

- It moves beyond 2D cylinder-flow-style transient examples toward external aerodynamic evaluation.
- It tests whether MR-card admissibility still works when geometry is complex and task-specific.
- It is graph-based, so representation MRs remain relevant, but physical symmetry MRs become more demanding and likely expose the rejection/downgrade logic.

**Candidate MRs:**

- Mesh/entity permutation equivariance: reorder points/cells/faces and inverse-map predictions.
- Rigid transform / coordinate-frame contract: only admitted if model inputs/outputs and preprocessing define a coordinate-equivariant or invariant contract.
- Left-right mirror / yaw-sign relation: admitted only for paired symmetric geometry and boundary settings; otherwise rejected/downgraded.
- Integrated-force consistency diagnostic: if pressure/shear outputs and surface normals are available, mapped integrated coefficients should transform consistently under admitted rigid/mirror transforms.

**Expected result:**

- Representation permutation should pass if graph operations are order independent.
- Many geometric symmetry candidates will be rejected because real vehicle/external-aero geometries and boundary conditions are not exactly symmetric.
- If force coefficients are available, relation-level integrated metrics may be more interpretable than pointwise field L2.

### Object C — PhysicsNeMo DoMINO external aerodynamics

**Role in argument:** production non-GNN neural-operator / multi-scale aerodynamics object.

**Why this object:**

- It is deliberately different from MeshGraphNet/AeroGraphNet representation assumptions.
- It tests whether the workflow handles non-graph model contracts, where node-permutation may not be an admissible representation MR.
- It strengthens the paper’s claim that the contribution is a validity-gated testing workflow, not a graph-model trick.

**Candidate MRs:**

- Grid/query ordering contract: if DoMINO accepts unordered query points or sampled field locations, permutation of query order should preserve inverse-mapped outputs; if it uses structured tensors with order semantics, this candidate is rejected.
- Coordinate-frame / rigid-transform relation: admitted only if documented preprocessing makes the contract equivariant/invariant.
- Mirrored-geometry relation: admitted only for paired symmetric geometry and boundary conditions.
- Conservation / flux diagnostic: reference-relative only, unless operator floor and physical tolerance can be calibrated.

**Expected result:**

- Some representation MRs may be rejected rather than executed, which is valuable evidence for the gate.
- At least one executable relation should be retained: query-order permutation if the API treats queries as a set, or a documented coordinate-contract relation if available.
- Physical relation verdicts are expected to be mixed and strongly conditioned on geometry and preprocessing.

## 4. Evaluation metrics

### 4.1 Workflow-completeness metrics

Per object:

- `trained_or_pretrained_artifact_available`: true/false.
- `dataset_artifact_available`: true/false.
- `full_workflow_flags`: rubric decisions, source/follow-up outputs, metric ledgers, relation verdicts.
- Raw-output existence count and SHA coverage.
- Number of admitted / rejected / downgraded / deferred candidates.

### 4.2 Relation-level metrics

- Relative L2 between source output and inverse-mapped follow-up output.
- Threshold-normalized violation `V/tol`.
- Operator-floor-normalized violation `V/floor` where a floor is calibrated.
- Domain-violation score `D` where measurable; otherwise explicit `not-operationalizable`.
- Integrated aerodynamic coefficient error for force/pressure relations where available.
- Conservation ratio: predicted divergence/flux diagnostic over reference diagnostic, with absolute conservation explicitly deferred unless calibrated.

### 4.3 Statistical / descriptive summaries

- Per-object relation verdict table.
- Cross-object relation class table: representation, symmetry, conservation, boundary/contract.
- Wilson intervals only for cell-level denominators, with clustering caveat.
- No independence claim unless objects/runs are genuinely independent.
- Runtime/cost recorded as reproducibility information, not as a performance claim.

## 5. Experimental method

### 5.1 Stage gate 0 — feasibility audit

For each object:

- Record official repository/documentation URL.
- Record exact version, commit, model checkpoint source, license, and data source.
- Verify installation on local environment or container.
- Run the official minimal inference example without modification.
- Write `feasibility_report.json` with status `ready`, `blocked`, or `partial`.

Stop rule: no workflow claim may be added for an object that lacks a successful inference smoke test and saved raw output.

### 5.2 Stage gate 1 — MR candidate audit

For each object:

- Enumerate 8--12 candidate relations.
- Apply the four-part admissibility predicate.
- Mark each candidate as admitted, rejected, downgraded-to-OOD-stress, or deferred.
- Select at least two executable relation assets if possible: one representation/software relation and one physics/geometry relation or diagnostic.

Stop rule: if fewer than one executable relation remains, report the object as a **validity-gate rejection case**, not as a failed SUT experiment.

### 5.3 Stage gate 2 — runner implementation

For each admitted/downgraded relation:

- Build source input.
- Build follow-up input.
- Run SUT on both.
- Map follow-up output back to source coordinates/order.
- Save raw source/follow-up/mapped outputs before scoring.
- Score metric and write ledger only after raw outputs exist.

Stop rule: ledger writer must fail closed when raw outputs are absent.

### 5.4 Stage gate 3 — aggregate reporting

Create per-object reports:

- `physicsnemo-mgn-production-workflow/production_workflow_report.json`
- `physicsnemo-aerographnet-production-workflow/production_workflow_report.json`
- `physicsnemo-domino-production-workflow/production_workflow_report.json`

Create aggregate report:

- `research_assets/runs/production-grade-sut-extension/production_grade_sut_extension_report.json`

The aggregate report should include:

- Object-level workflow flags.
- Relation counts by decision type.
- Verdict denominators.
- Raw artifact references.
- Claim limitations.
- Production-object evidence summary for manuscript tables.

## 6. Expected results and interpretation

### 6.1 Expected positive result

The ideal result is not that every MR passes or fails. The ideal result is that the gate produces a useful mix:

- Representation relations pass where the model contract supports them.
- Physical symmetry candidates are rejected/downgraded when geometry/boundaries break preconditions.
- Conservation relations are admitted only when numerical floors/tolerances are measurable; otherwise they remain diagnostics/deferred.
- At least one production object yields a low-domain/high-relation violation, strengthening the SUT-inconsistency interpretation.

### 6.2 Expected manuscript upgrade

If all three objects reach Stage 3, the manuscript can add:

> We executed the same artifact-gated MR workflow on three maintained production-framework CFD/SciML examples: PhysicsNeMo MeshGraphNet transient vortex shedding, PhysicsNeMo AeroGraphNet external aerodynamics, and PhysicsNeMo DoMINO external aerodynamics. Across these objects, the workflow produced admitted, rejected, downgraded, and deferred relation decisions, with raw source/follow-up outputs and relation-level ledgers. This broadens the evidence from local/sibling surrogates to maintained production examples while preserving bounded claims.

### 6.3 Expected risk result

If one or more objects are blocked by installation, checkpoint licensing, dataset access, GPU requirements, or API instability, that is still useful if reported honestly:

- `blocked_by_installation`
- `blocked_by_checkpoint_access`
- `blocked_by_dataset_license`
- `blocked_by_gpu_memory`
- `blocked_by_no_inference_api`

Blocked production objects should be reported in the experiment ledger, not silently replaced by toy alternatives.

## 7. Why these objects, not three arbitrary local models

1. **Maintained production framework.** PhysicsNeMo is a maintained NVIDIA framework with documented CFD examples; this directly addresses the “local toy code” concern.
2. **Coverage of model families.** MeshGraphNet / AeroGraphNet / DoMINO cover graph and non-graph neural-operator-style contracts.
3. **Coverage of CFD task scale.** Vortex shedding is close to the current cylinder-flow case; external aerodynamics broadens geometry and output semantics.
4. **MR validity pressure.** Complex geometry forces the method to reject/downgrade invalid physical symmetry relations, demonstrating the value of the gate.
5. **Artifact feasibility.** The examples are documented and therefore more likely to provide reproducible commands than undocumented one-off checkpoints.
6. **Honest fallback.** OpenFOAM can provide reference simulations or sanity baselines if data generation is needed, but it should not be counted as a SciML SUT unless wrapped by a trained surrogate.

## 8. Superpowers execution plan

> **For future agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans` or `superpowers:subagent-driven-development`. Execute task-by-task, update checkboxes, and stop at the first blocked gate unless the block has a documented fallback approved by the user.

### Task 1 — Production-object feasibility audit

- [x] Create `tools/audit_production_sut_feasibility.py`.
- [x] Create `tests/test_production_sut_feasibility_plan.py`.
- [x] For each object, record official URL, repository, version, model/checkpoint availability, data availability, hardware need, license note, and expected command.
- [x] Attempt official minimal inference smoke test for PhysicsNeMo MeshGraphNet transient vortex shedding.
- [x] Attempt official minimal inference smoke test for PhysicsNeMo AeroGraphNet.
- [x] Attempt official minimal inference smoke test for PhysicsNeMo DoMINO.
- [x] Write `research_assets/runs/production-grade-sut-extension/feasibility_report.json`.
- [x] Add claim-ledger entries only as `planned` or `blocked` until raw outputs exist.

Acceptance:

- Each object has `ready`, `partial`, or `blocked` status with reason.
- No manuscript result wording is added at this stage.

Task 1 execution note (2026-06-12): `tools/audit_production_sut_feasibility.py` wrote `research_assets/runs/production-grade-sut-extension/feasibility_report.json`. All three selected PhysicsNeMo objects are currently `blocked`: official documentation URLs were reachable; CPU `torch` is now importable for the repository test suite, but `physicsnemo` remains not importable, the `nvidia-physicsnemo==2.1.1` dry-run shows a heavy CUDA/Torch runtime stack, and official checkpoints/data/API artifacts have not been staged. Therefore Task 3--5 production workflow claims remain blocked.

### Task 2 — MR candidate ledgers

- [x] Create per-object candidate ledgers under `research_assets/runs/production-grade-sut-extension/<object>/candidate_ledger.json`.
- [x] List candidate relations by class: representation, symmetry, conservation/flux, boundary/contract, numerical floor.
- [x] Apply the four-part admissibility predicate.
- [x] Select executable relation subset per object.
- [x] Record rejected/deferred candidates with reasons.

Acceptance:

- Each candidate has source category, basis, preconditions, output mapping, metric, tolerance/floor status, and decision.
- Tests fail if an exact MR is executed after a rejected/downgraded decision.

Task 2 execution note (2026-06-12): `tools/build_production_sut_candidate_ledgers.py` wrote per-object candidate ledgers for PhysicsNeMo MGN vortex shedding, AeroGraphNet, and DoMINO. Each ledger covers representation, symmetry, conservation/flux, boundary/contract, and numerical-floor candidates with the four-part admissibility predicate. Because Task 1 remains blocked, selected candidates are a future subset only; no production MR has been executed and Task 3--5 workflow claims remain blocked.

### Task 2.5 — PhysicsNeMo runtime staging preflight

- [x] Install/stage the Python package/runtime import gate for `nvidia-physicsnemo==2.1.1` with CPU-compatible `torch`/`torchvision` in this environment.
- [x] Create `tools/stage_physicsnemo_runtime.py`.
- [x] Create `tests/test_physicsnemo_runtime_staging.py`.
- [x] Write `research_assets/runs/production-grade-sut-extension/physicsnemo_runtime_staging_report.json`.
- [x] Probe PhysicsNeMo core, MeshGraphNet, vortex-shedding datapipe, and DoMINO datapipe imports.
- [x] Record official example source reachability and remaining per-object data/checkpoint/API blockers.

Acceptance:

- PhysicsNeMo package/runtime import gate is now partially staged.
- Task 3--5 workflow execution remains blocked until official data, checkpoint/API artifacts, raw outputs, and metric ledgers exist.

Task 2.5 execution note (2026-06-12): `tools/stage_physicsnemo_runtime.py` wrote `research_assets/runs/production-grade-sut-extension/physicsnemo_runtime_staging_report.json`. PhysicsNeMo package/runtime import gate is now partially staged: `physicsnemo`, MeshGraphNet modules, the vortex-shedding datapipe, and the DoMINO datapipe import under CPU `torch`/`torchvision`; CUDA/GPU is unavailable and all three objects still lack staged official data, checkpoints/API credentials, raw outputs, and metric ledgers. Therefore Task 3--5 production workflows remain blocked.

### Task 2.6 — PhysicsNeMo MGN official data/checkpoint staging attempt

- [x] Attempt official DeepMind/PhysicsNeMo `cylinder_flow` data staging for Object A.
- [x] Create `tools/stage_physicsnemo_mgn_assets.py`.
- [x] Create `tests/test_physicsnemo_mgn_asset_staging.py`.
- [x] Write `research_assets/runs/production-grade-sut-extension/physicsnemo_mgn_asset_staging_report.json`.
- [x] Record complete-data, checkpoint, raw-output, and metric-ledger blockers before Task 3.

Acceptance:

- The report distinguishes public-data reachability from complete staged data.
- Task 3 remains unchecked unless complete official data, checkpoint, raw outputs, and metric ledgers exist.

Task 2.6 execution note (2026-06-12): official cylinder_flow data download was attempted from the public DeepMind MeshGraphNets GCS source. The download proved large in this environment and was stopped after partial external staging to avoid wasting time/storage; no staged official/new PhysicsNeMo MGN checkpoint, raw outputs, or metric ledgers exist. `tools/stage_physicsnemo_mgn_assets.py` wrote `research_assets/runs/production-grade-sut-extension/physicsnemo_mgn_asset_staging_report.json`; Task 3 remains blocked.

### Task 2.7 — official access/source staging for all three production objects

- [x] Probe/stage official source access for Object A/B/C after runtime and Object-A asset attempts.
- [x] Download the public NGC cylinder-flow archive for the PhysicsNeMo vortex-shedding family into external workspace storage.
- [x] Record why the NGC archive is not sufficient for Task 3 MGN workflow execution by itself.
- [x] Record AeroGraphNet full-dataset access and DoMINO NIM/API/container blockers.
- [x] Write `research_assets/runs/production-grade-sut-extension/official_access_staging_report.json`.

Acceptance:

- The report distinguishes staged official source archives from complete workflow prerequisites, and records the official access staging boundary.
- Task 3--5 remain unchecked unless complete official data, checkpoint/API artifacts, raw outputs, and metric ledgers exist.

Task 2.7 execution note (2026-06-12): `tools/stage_production_sut_official_access.py` wrote `research_assets/runs/production-grade-sut-extension/official_access_staging_report.json`. The public NGC `modulus_datasets_cylinder-flow` zip was downloaded to external workspace storage and its nested `dataset.zip` was inspected; this is official cylinder-flow data, but it is not the complete DeepMind train/valid/test TFRecord bundle required for the selected PhysicsNeMo MGN Task 3 workflow. AeroGraphNet remains blocked by NVIDIA/full-dataset access and checkpoint availability, while DoMINO remains blocked by NGC API key/container/GPU endpoint requirements. No production raw outputs or metric ledgers exist, so Task 3--5 workflows remain blocked.

### Task 2.8 — complete official DeepMind TFRecord data staging for Object A

- [x] Download complete official DeepMind `cylinder_flow` `meta.json`, `train.tfrecord`, `valid.tfrecord`, and `test.tfrecord` to external workspace storage.
- [x] Re-run `tools/stage_physicsnemo_mgn_assets.py` so the report distinguishes closed data blocker from remaining checkpoint/raw-output/ledger blockers.
- [x] Re-run `tools/stage_production_sut_official_access.py` so the all-object official access report records the complete Object-A TFRecord bundle.
- [x] Keep Task 3 blocked until a PhysicsNeMo checkpoint/API plus raw outputs and metric ledgers exist.

Acceptance:

- `physicsnemo_mgn_asset_staging_report.json` records `official_data_staged: true` and no `complete_official_data` blocker.
- Task 3 remains unchecked because checkpoint/API, raw outputs, and metric ledgers are still absent.

Task 2.8 execution note (2026-06-12): the complete DeepMind TFRecord bundle; the complete official DeepMind TFRecord data bundle for Object A is staged externally under `/workspace/physicsnemo_staged_assets/mgn/cylinder_flow` and totals more than 16 GB. This closes the Object-A data-staging blocker only. No official/new PhysicsNeMo MGN checkpoint, GPU-backed workflow execution, production raw outputs, or metric ledgers exist, so Task 3 remains blocked.

### Task 3 — PhysicsNeMo MeshGraphNet workflow

- [x] Implement `tools/run_physicsnemo_mgn_smoke_workflow.py` for the CPU-executable Object-A smoke subset.
- [x] Stage first-record official DeepMind `cylinder_flow` train/test TFRecord trajectories outside git for smoke execution.
- [x] Train and save a new NVIDIA PhysicsNeMo `MeshGraphNet` checkpoint for the smoke subset.
- [x] Save source/follow-up/mapped raw outputs.
- [x] Write relation metric ledgers.
- [x] Generate `research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-vortex-shedding/physicsnemo_mgn_smoke_workflow_report.json`.
- [x] Add tests for denominator counts, raw output existence, and honesty boundary.
- [ ] Stage and execute the full-scale production PhysicsNeMo MGN workflow over the complete train/valid/test bundle before making production-scale pass/fail-rate claims.

Acceptance:

- At least one representation relation executed or explicitly blocked.
- At least one physics/geometry relation admitted, downgraded, or deferred with evidence.
- Full-scale production claims remain forbidden until the complete-bundle workflow is executed.

Task 3 execution note (2026-06-12): `tools/run_physicsnemo_mgn_smoke_workflow.py` now trains a new NVIDIA PhysicsNeMo `MeshGraphNet` checkpoint on a CPU-executable first-record slice of the official DeepMind `cylinder_flow` TFRecord data, then writes raw source/follow-up outputs and metric ledgers under `research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-vortex-shedding/`. This closes the Object-A checkpoint/raw-output/metric-ledger gap for a minimal PhysicsNeMo MeshGraphNet CPU smoke workflow only. It is not a full production-scale PhysicsNeMo benchmark, and Task 4--5 remain blocked by external AeroGraphNet/DoMINO data, checkpoint/API, GPU/container, and access constraints.

### Task 4 — PhysicsNeMo AeroGraphNet workflow

- [ ] Implement `tools/run_physicsnemo_aerographnet_primary_workflow.py`.
- [ ] Prefer representation permutation and integrated-force/pressure relation if outputs support them.
- [ ] Save raw outputs and ledgers.
- [ ] Generate `research_assets/runs/physicsnemo-aerographnet-production-workflow/production_workflow_report.json`.
- [ ] Add tests for raw output existence, mapping correctness, and no overclaiming.

Acceptance:

- Report contains admitted/rejected/downgraded/deferred decision counts.
- Integrated aerodynamic metric is used only if the output semantics support it.

### Task 5 — PhysicsNeMo DoMINO workflow

- [ ] Implement `tools/run_physicsnemo_domino_primary_workflow.py`.
- [ ] Determine whether query-order permutation is admissible; reject if order is semantically meaningful.
- [ ] Save raw outputs and ledgers.
- [ ] Generate `research_assets/runs/physicsnemo-domino-production-workflow/production_workflow_report.json`.
- [ ] Add tests for query/order contract and honesty boundary.

Acceptance:

- At least one relation decision is executable or the object is documented as a validity-gate rejection case.
- No graph-specific MR is forced onto a non-graph contract.

### Task 6 — Aggregate production extension report

- [ ] Create `tools/run_production_grade_sut_extension_aggregate.py`.
- [ ] Aggregate object-level workflow flags, relation decisions, verdict counts, and limitations.
- [ ] Write `research_assets/runs/production-grade-sut-extension/production_grade_sut_extension_report.json`.
- [ ] Add claim-ledger entries with allowed/forbidden wording.
- [ ] Update evidence package and manuscript tables only after reports exist.

Acceptance:

- Aggregate report distinguishes `observed`, `blocked`, and `partial` objects.
- Manuscript wording stays within claim-ledger boundaries.

### Task 7 — Review-gate rerun

- [ ] Run targeted workflow tests.
- [ ] Run `python3 -m pytest tests -q`.
- [ ] Run academic review panel only after all production artifacts and manuscript updates are committed.
- [ ] Compare v6/v7 empirical-rigor and novelty deltas.

Acceptance:

- No failing tests.
- Review report explicitly states whether production objects closed the empirical-base concern or only reduced it.

## 9. Cost / risk control

| Risk | Mitigation |
|---|---|
| GPU requirement too high | First run official smallest inference; if blocked, record `blocked_by_gpu` and stop. |
| Checkpoint unavailable | Record as blocked; do not fabricate or replace with local toy model. |
| Dataset license/access issue | Use official sample data only; otherwise blocked. |
| Model API changes | Pin version/commit; record environment. |
| Relation not admissible | Treat rejection as evidence for the gate; do not weaken preconditions. |
| Word-count pressure | Keep manuscript update table-first; detailed production reports stay in artifacts. |

## 10. Stop condition for this session

This session stops after writing this plan document. No installation, training, data download, or workflow implementation should be started until the user approves the production-object execution plan.
