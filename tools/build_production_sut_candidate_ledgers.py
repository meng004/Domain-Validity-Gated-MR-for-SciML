"""Build P0c Task 2 MR candidate ledgers for production-grade SUT objects.

The generated ledgers are planning artifacts, not execution results. They apply
an explicit four-part admissibility predicate to candidate relations and then
fail closed behind the Task 1 feasibility gate until official production runtime,
checkpoints/data/API artifacts, raw outputs, and metric ledgers exist.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "research_assets/runs/production-grade-sut-extension"
FEASIBILITY = BASE / "feasibility_report.json"

PREDICATE_KEYS = (
    "domain_preconditions",
    "semantic_invariance",
    "output_mapping_defined",
    "numerical_floor_defined",
)


def predicate(
    *,
    domain_preconditions: bool,
    semantic_invariance: bool,
    output_mapping_defined: bool,
    numerical_floor_defined: bool,
) -> dict[str, bool]:
    return {
        "domain_preconditions": domain_preconditions,
        "semantic_invariance": semantic_invariance,
        "output_mapping_defined": output_mapping_defined,
        "numerical_floor_defined": numerical_floor_defined,
    }


def gate(decision: str, object_status: str, reason: str) -> dict[str, Any]:
    exact_candidate = decision == "admitted"
    return {
        "blocked_by": "P0c Task 1 feasibility gate",
        "reason": f"No raw production outputs or metric ledgers exist yet; {reason}",
        "object_status": object_status,
        "executable_as_exact_mr": exact_candidate,
        "planned_workflow_execution": False,
    }


def candidate(
    *,
    object_id: str,
    suffix: str,
    relation_class: str,
    source_category: str,
    basis: str,
    preconditions: list[str],
    output_mapping: str,
    metric: str,
    tolerance_floor_status: str,
    admissibility_predicate: dict[str, bool],
    decision: str,
    decision_reason: str,
    object_status: str,
) -> dict[str, Any]:
    missing_keys = set(PREDICATE_KEYS) - set(admissibility_predicate)
    if missing_keys:
        raise ValueError(f"missing predicate keys for {object_id}/{suffix}: {sorted(missing_keys)}")
    return {
        "candidate_id": f"{object_id}:{suffix}",
        "relation_class": relation_class,
        "source_category": source_category,
        "basis": basis,
        "preconditions": preconditions,
        "output_mapping": output_mapping,
        "metric": metric,
        "tolerance_floor_status": tolerance_floor_status,
        "admissibility_predicate": admissibility_predicate,
        "decision": decision,
        "decision_reason": decision_reason,
        "execution_gate": gate(decision, object_status, decision_reason),
    }


def definitions_for(object_id: str, object_status: str) -> list[dict[str, Any]]:
    common_floor = candidate(
        object_id=object_id,
        suffix="numeric-floor-calibration",
        relation_class="numerical_floor",
        source_category="protocol-calibration",
        basis="Estimate relation-specific floating-point/operator floor from repeated production inference before assigning tolerances.",
        preconditions=["Official runtime is installed", "At least two repeated source inferences can be saved as raw outputs"],
        output_mapping="Compare repeated source-output tensors or surface fields in the model's native output schema.",
        metric="repeat-run relative L2 / max absolute difference by output channel",
        tolerance_floor_status="needs_calibration",
        admissibility_predicate=predicate(
            domain_preconditions=True,
            semantic_invariance=True,
            output_mapping_defined=True,
            numerical_floor_defined=False,
        ),
        decision="deferred",
        decision_reason="Numerical floor cannot be calibrated before official runtime and raw repeated outputs exist.",
        object_status=object_status,
    )

    if object_id == "physicsnemo-mgn-vortex-shedding":
        return [
            candidate(
                object_id=object_id,
                suffix="node-order-permutation",
                relation_class="representation",
                source_category="graph-representation contract",
                basis="MeshGraphNet-style graph predictions should be equivariant to a pure node-row permutation when edge indices and node features are permuted consistently.",
                preconditions=["Graph connectivity is explicitly accessible", "Permutation preserves node and edge attributes", "Output is node-indexed"],
                output_mapping="Inverse-permute follow-up node predictions to source node order.",
                metric="relative L2 between source output and inverse-mapped follow-up output",
                tolerance_floor_status="defined",
                admissibility_predicate=predicate(
                    domain_preconditions=True,
                    semantic_invariance=True,
                    output_mapping_defined=True,
                    numerical_floor_defined=True,
                ),
                decision="admitted",
                decision_reason="Pure graph-row relabeling is an admissible exact representation relation once production graph tensors are available.",
                object_status=object_status,
            ),
            candidate(
                object_id=object_id,
                suffix="mirror-y-vortex-domain",
                relation_class="symmetry",
                source_category="physics/geometry symmetry",
                basis="Cylinder/vortex-shedding geometry may appear mirror-like, but inflow, boundary encoding, rollout state, and trained preprocessing must be audited before exact mirror-y is valid.",
                preconditions=["Geometry and boundary conditions are mirror symmetric", "Vector components are sign-mapped correctly", "Training normalization does not encode an orientation"],
                output_mapping="Reflect coordinates and flip transverse velocity components before comparing mapped fields.",
                metric="mapped-field relative L2 over velocity/pressure channels",
                tolerance_floor_status="needs_calibration",
                admissibility_predicate=predicate(
                    domain_preconditions=False,
                    semantic_invariance=False,
                    output_mapping_defined=True,
                    numerical_floor_defined=False,
                ),
                decision="downgraded",
                decision_reason="Treat as OOD stress until boundary/preprocessing symmetry and numerical floor are verified from official artifacts.",
                object_status=object_status,
            ),
            candidate(
                object_id=object_id,
                suffix="reference-relative-divergence",
                relation_class="conservation_flux",
                source_category="diagnostic conservation contract",
                basis="A learned transient surrogate can be checked against reference-relative divergence/flux drift, but absolute conservation is not implied by a black-box checkpoint.",
                preconditions=["Mesh cells/areas or graph stencils are accessible", "Reference or source-step baseline is available", "Velocity channels are mapped unambiguously"],
                output_mapping="Compute source and follow-up divergence/flux diagnostics in the same physical coordinates.",
                metric="relative change in divergence/flux diagnostic versus reference/source baseline",
                tolerance_floor_status="needs_calibration",
                admissibility_predicate=predicate(
                    domain_preconditions=True,
                    semantic_invariance=True,
                    output_mapping_defined=True,
                    numerical_floor_defined=False,
                ),
                decision="deferred",
                decision_reason="Diagnostic is plausible, but tolerance/floor and reference mapping require production raw outputs.",
                object_status=object_status,
            ),
            candidate(
                object_id=object_id,
                suffix="boundary-condition-contract",
                relation_class="boundary_contract",
                source_category="input contract audit",
                basis="Perturbations that alter inlet, wall, or obstacle boundary semantics are not exact MRs for a trained vortex-shedding surrogate.",
                preconditions=["Boundary node types are identifiable", "Perturbation preserves boundary labels and physical units"],
                output_mapping="No output mapping unless the transformed input is contract-preserving.",
                metric="rubric decision only before execution",
                tolerance_floor_status="not_applicable",
                admissibility_predicate=predicate(
                    domain_preconditions=False,
                    semantic_invariance=False,
                    output_mapping_defined=False,
                    numerical_floor_defined=True,
                ),
                decision="rejected",
                decision_reason="Boundary-changing transforms violate the SUT input contract and must not be executed as exact MRs.",
                object_status=object_status,
            ),
            common_floor,
        ]

    if object_id == "physicsnemo-aerographnet-external-aero":
        return [
            candidate(
                object_id=object_id,
                suffix="surface-node-permutation",
                relation_class="representation",
                source_category="surface graph representation contract",
                basis="AeroGraphNet surface graph outputs should be invariant/equivariant to row ordering if all graph tensors and surface attributes are permuted consistently.",
                preconditions=["Surface graph tensors are exposed", "Faces/edges and node features are permuted consistently", "Output fields are node-indexed"],
                output_mapping="Inverse-permute follow-up surface pressure/wall-shear predictions to source node order.",
                metric="relative L2 by surface field channel",
                tolerance_floor_status="defined",
                admissibility_predicate=predicate(
                    domain_preconditions=True,
                    semantic_invariance=True,
                    output_mapping_defined=True,
                    numerical_floor_defined=True,
                ),
                decision="admitted",
                decision_reason="Pure representation relabeling is exact if official graph tensors expose row-order semantics.",
                object_status=object_status,
            ),
            candidate(
                object_id=object_id,
                suffix="vehicle-mirror-y",
                relation_class="symmetry",
                source_category="external-aero geometry symmetry",
                basis="Vehicle geometries and yaw/inlet conventions are often not exactly mirror symmetric; a mirror transform can invalidate geometry or flow orientation.",
                preconditions=["Geometry is mirror symmetric", "Flow direction/yaw and boundary metadata are transformed consistently", "Surface normals and vector outputs are mapped correctly"],
                output_mapping="Reflect surface coordinates/normals and map vector wall-shear components if geometry supports it.",
                metric="mapped surface pressure/wall-shear relative L2 plus integrated coefficient drift",
                tolerance_floor_status="needs_calibration",
                admissibility_predicate=predicate(
                    domain_preconditions=False,
                    semantic_invariance=False,
                    output_mapping_defined=True,
                    numerical_floor_defined=False,
                ),
                decision="downgraded",
                decision_reason="Use only as a domain-violation/OOD-stress candidate unless exact geometry and flow symmetry are certified.",
                object_status=object_status,
            ),
            candidate(
                object_id=object_id,
                suffix="integrated-drag-consistency",
                relation_class="conservation_flux",
                source_category="integrated aerodynamic quantity diagnostic",
                basis="If pressure/wall-shear and surface normals are available, integrated force/drag consistency can check output aggregation but not solver truth.",
                preconditions=["Pressure or wall-shear output semantics are documented", "Surface normals/areas are available", "Drag direction and units are known"],
                output_mapping="Integrate mapped surface quantities over the same mesh and compare coefficient drift.",
                metric="absolute/relative drift in drag or force coefficient",
                tolerance_floor_status="needs_calibration",
                admissibility_predicate=predicate(
                    domain_preconditions=True,
                    semantic_invariance=True,
                    output_mapping_defined=True,
                    numerical_floor_defined=False,
                ),
                decision="deferred",
                decision_reason="Requires official output semantics, mesh areas, and calibrated integration floor before execution.",
                object_status=object_status,
            ),
            candidate(
                object_id=object_id,
                suffix="mesh-resolution-boundary-contract",
                relation_class="boundary_contract",
                source_category="production geometry/input contract",
                basis="Changing tessellation or geometry without preserving the model's preprocessing contract can create a new design case rather than a metamorphic follow-up.",
                preconditions=["Preprocessing accepts transformed mesh", "Geometry identity is preserved", "Boundary and feature normalization contracts are unchanged"],
                output_mapping="Only compare after the official preprocessing map defines correspondence between source and follow-up surfaces.",
                metric="contract decision before numeric metric",
                tolerance_floor_status="not_applicable",
                admissibility_predicate=predicate(
                    domain_preconditions=False,
                    semantic_invariance=False,
                    output_mapping_defined=False,
                    numerical_floor_defined=True,
                ),
                decision="rejected",
                decision_reason="Uncontrolled geometry/preprocessing changes are contract violations, not exact MRs.",
                object_status=object_status,
            ),
            common_floor,
        ]

    if object_id == "physicsnemo-domino-external-aero":
        return [
            candidate(
                object_id=object_id,
                suffix="query-order-permutation",
                relation_class="representation",
                source_category="point-cloud/query representation contract",
                basis="DoMINO-style point/query outputs may be order equivariant only if query order is semantically pure and outputs are query-indexed.",
                preconditions=["Query points are exposed", "Order has no batching/window semantics", "Output rows correspond one-to-one to query rows"],
                output_mapping="Inverse-permute follow-up query outputs to source query order.",
                metric="relative L2 by query-output channel",
                tolerance_floor_status="defined",
                admissibility_predicate=predicate(
                    domain_preconditions=True,
                    semantic_invariance=True,
                    output_mapping_defined=True,
                    numerical_floor_defined=True,
                ),
                decision="admitted",
                decision_reason="Admissible only after official API confirms query order is not semantically meaningful.",
                object_status=object_status,
            ),
            candidate(
                object_id=object_id,
                suffix="point-cloud-mirror",
                relation_class="symmetry",
                source_category="external-aero point-cloud geometry symmetry",
                basis="Mirroring a production external-aero point cloud can alter geometry, normals, flow direction, or conditioning metadata.",
                preconditions=["Geometry and flow metadata are exactly symmetric", "Normals/vectors are reflected consistently", "Conditioning variables preserve semantics"],
                output_mapping="Reflect query coordinates and vector outputs; compare mapped scalar/vector fields.",
                metric="mapped query-field relative L2 and coefficient drift if available",
                tolerance_floor_status="needs_calibration",
                admissibility_predicate=predicate(
                    domain_preconditions=False,
                    semantic_invariance=False,
                    output_mapping_defined=True,
                    numerical_floor_defined=False,
                ),
                decision="downgraded",
                decision_reason="Keep as OOD/domain-violation stress until geometry and conditioning symmetry are established.",
                object_status=object_status,
            ),
            candidate(
                object_id=object_id,
                suffix="volume-surface-flux-diagnostic",
                relation_class="conservation_flux",
                source_category="operator-output physics diagnostic",
                basis="Surface/volume predictions may support flux diagnostics, but the operator contract does not guarantee exact conservation without reference data and integration geometry.",
                preconditions=["Volume/surface output semantics are known", "Integration geometry or sampling weights are available", "Reference/source baseline is defined"],
                output_mapping="Map source/follow-up query outputs into a common physical coordinate/integration frame.",
                metric="relative flux or divergence-diagnostic drift",
                tolerance_floor_status="needs_calibration",
                admissibility_predicate=predicate(
                    domain_preconditions=True,
                    semantic_invariance=True,
                    output_mapping_defined=True,
                    numerical_floor_defined=False,
                ),
                decision="deferred",
                decision_reason="Requires official output semantics, integration weights, and numerical floor calibration.",
                object_status=object_status,
            ),
            candidate(
                object_id=object_id,
                suffix="nim-api-contract",
                relation_class="boundary_contract",
                source_category="API/container contract audit",
                basis="If DoMINO is accessed through a container/API, request schema, authentication, batching, and preprocessing are part of the SUT contract.",
                preconditions=["Official endpoint/container is available", "Request schema is documented", "Transform preserves all required metadata"],
                output_mapping="No numeric mapping until request/response schema and metadata preservation are verified.",
                metric="contract decision before numeric metric",
                tolerance_floor_status="not_applicable",
                admissibility_predicate=predicate(
                    domain_preconditions=False,
                    semantic_invariance=False,
                    output_mapping_defined=False,
                    numerical_floor_defined=True,
                ),
                decision="rejected",
                decision_reason="Schema/API-changing requests are invalid exact MRs and must fail closed.",
                object_status=object_status,
            ),
            common_floor,
        ]

    raise ValueError(f"unknown production object: {object_id}")


def selected_future_subset(candidates: list[dict[str, Any]]) -> list[str]:
    return [
        item["candidate_id"]
        for item in candidates
        if item["decision"] == "admitted" or item["relation_class"] == "numerical_floor"
    ]


def build_ledgers() -> list[Path]:
    feasibility = json.loads(FEASIBILITY.read_text(encoding="utf-8"))
    written: list[Path] = []
    for obj in feasibility["objects"]:
        object_id = obj["object_id"]
        candidates = definitions_for(object_id, obj["status"])
        ledger = {
            "record_type": "production-sut-mr-candidate-ledger",
            "schema_version": "0.1.0",
            "object_id": object_id,
            "object_name": obj["name"],
            "object_feasibility_status": obj["status"],
            "feasibility_report": "research_assets/runs/production-grade-sut-extension/feasibility_report.json",
            "official_url": obj["official_url"],
            "workflow_execution_allowed": False,
            "raw_outputs_available": False,
            "metric_ledgers_available": False,
            "current_result_claim": "none",
            "selected_future_subset": selected_future_subset(candidates),
            "candidates": candidates,
            "honesty_boundary": "This is a candidate ledger only. No production MR has been executed; Task 3--5 workflow results remain blocked until official runtime/checkpoints/data/API plus raw outputs and metric ledgers exist.",
        }
        out = BASE / object_id / "candidate_ledger.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(out)
    return written


def main() -> None:
    for path in build_ledgers():
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
