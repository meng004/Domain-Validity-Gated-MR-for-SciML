# 70 · Phase B Operator-Floor Soundness Artifact

> Date: 2026-07-02. Purpose: close the Phase B theory gate as far as the current evidence and mathematics support it, without converting observed topology stability into an unsupported arbitrary-mesh theorem.

## Verdict

Phase B can be partially closed with a shape-regular triangular-mesh theorem for the P1 constant-per-cell divergence operator. The theorem generalizes beyond the single structured deployment mesh, but it does not cover arbitrary degenerate meshes, arbitrary operators, discontinuous fields, boundary-condition mismatch, or non-P1 divergence estimators.

## Theorem: local P1 divergence floor on shape-regular triangles

Let \(K\) be a nondegenerate triangle with vertices \(p_i=(x_i,y_i)\), area \(|K|\), diameter \(h_K\), and P1 divergence operator

\[
\operatorname{div}_h u |_K =
  \sum_{i=0}^{2} u_x(p_i)\frac{b_i}{2|K|}
  + \sum_{i=0}^{2} u_y(p_i)\frac{c_i}{2|K|},
\]

where \(b_i=y_j-y_k\) and \(c_i=x_k-x_j\). Assume \(u\in C^2(K)^2\) and \(\nabla\cdot u=0\) on \(K\). Let

\[
M_K=\max_{\alpha\in\{x,y\}}\sup_{\xi\in K}\|\nabla^2 u_\alpha(\xi)\|_2 .
\]

Then

\[
|\operatorname{div}_h u |_K|
 \le
 \frac{M_K}{4|K|}
 \left(\max_i \|p_i-c_K\|^2\right)
 \sum_{i=0}^{2}(|b_i|+|c_i|),
\]

where \(c_K\) is the cell centroid. If the mesh family is shape-regular, so that \(|K|\ge \gamma h_K^2\) and \(|b_i|+|c_i|\le 2h_K\), then

\[
|\operatorname{div}_h u |_K|
 \le C(\gamma) M_K h_K,
\]

with \(C(\gamma)\) depending only on the shape-regularity constant.

## Proof sketch

The P1 divergence operator is exact on affine vector fields. Let \(T\) be the affine Taylor polynomial of \(u\) about \(c_K\). Since \(\nabla\cdot u=0\), the affine part contributes zero to \(\operatorname{div}_h\) up to the usual P1 exactness. The residual at each vertex is the second-order Lagrange remainder,

\[
R_{\alpha,i}
=\frac{1}{2}(p_i-c_K)^T \nabla^2 u_\alpha(\xi_{\alpha,i})(p_i-c_K),
\]

for some \(\xi_{\alpha,i}\in K\). Therefore

\[
\operatorname{div}_h u |_K
=
\frac{1}{2|K|}
\left(\sum_i R_{x,i}b_i+\sum_i R_{y,i}c_i\right).
\]

Using \(|R_{\alpha,i}|\le \frac12 M_K\|p_i-c_K\|^2\) gives the first bound. The shape-regular \(O(h_K)\) form follows from \(\max_i\|p_i-c_K\|\le h_K\), \(\sum_i(|b_i|+|c_i|)\le 6h_K\), and \(|K|\ge\gamma h_K^2\).

## Soundness implication for the admissibility gate

For any shape-regular triangular mesh family and \(C^2\) divergence-free reference field with bounded Hessian, the P1 divergence floor is not an empirical accident: it is bounded by a mesh-shape constant times \(M h\). Therefore an absolute divergence-free MR is numerically decidable only if its verdict tolerance dominates this operator floor. If the desired tolerance is below the bound, the admissibility gate must defer the absolute verdict or replace it with a reference-relative diagnostic.

This justifies the gate logic used in the manuscript:

- structured deployment mesh: C32 gives a closed-form predictor and strict a-priori bound for the concrete mesh and analytic field;
- Delaunay jittered topology: C44 gives observed first-order and same-order floor stability on a second topology;
- general shape-regular triangular class: the theorem above supplies the local \(O(h)\) bound and a soundness condition for the P1 operator;
- arbitrary unstructured/degenerate meshes: not claimed.

## Evidence and traceability

- Operator implementation: `tools/conservation_rubric.py::cell_divergence`.
- Analytic-bound implementation and report: `tools/run_operator_floor_analytic_bound.py`, `research_assets/runs/operator-floor-analytic-bound/operator_floor_analytic_bound_report.json`.
- Cross-topology observed stability: `tools/run_operator_floor_sweep_mesh2.py`, `research_assets/runs/operator-floor-sweep-mesh2/operator_floor_mesh2_report.json`.
- Existing claim boundaries: C32 and C44 in `research_assets/experiments/claim-ledger.yml`.

## Claim wording allowed

The manuscript may claim a P1 operator-floor soundness bound for shape-regular triangular meshes with \(C^2\) divergence-free reference fields and bounded Hessian. It may also claim that the concrete deployment mesh has a tighter closed-form predictor and strict a-priori bound, and that one Delaunay topology shows observed stability.

## Claim wording forbidden

- A closed-form bound for arbitrary unstructured cylinder meshes.
- A guarantee for degenerate/sliver meshes without a shape-regularity condition.
- A guarantee for non-P1 operators, flux-form operators, discontinuous fields, learned outputs, or boundary-condition mismatch.
- A model-accuracy, reliability, or fault-detection claim.
