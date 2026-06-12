# cylinder-flow-mgn-runtime

status: PASS_WITNESS
label_scope: true_fault_class
runtime_boundary: cylinder_flow_mgn_runtime
dataset: cylinder-flow-mgn-deepmind (benchmark_equivalence_claim: true)

## Result

- SUT: `cylinder_flow_meshgraphnet` (real trained MeshGraphNet).
- Trials (eval timesteps): `0,2,4,6,8`.
- Exact `kstar`: `6`.
- Active true fault classes: `4`.
- Max fault-class signature rank: `2`.
- Collapse: `False`.
- Selected exact-cover MRs: `mr_channel_energy, mr_inflow_dirichlet, mr_rollout_direction, mr_swap_signature, mr_update_magnitude, mr_wall_noslip`.
- Active fault classes: `boundary_condition_fault, normalization_scale_fault, physical_channel_fault, temporal_rollout_fault`.
- Inactive fault classes (honest): `mesh_adjacency_fault` (not detected by the current MR battery on this model/mesh).

## Data split separation

The MeshGraphNet is trained on the DeepMind **train** split; this witness evaluates the
held-out **test** split (a separate trajectory and mesh). There is no train/test leakage.
The training data provenance (split, trajectory, frame window, npz sha256) is recorded in
the training run's `data_manifest.json`, referenced under source artifacts.

## Runtime boundary

Kill decisions come from executing the trained MeshGraphNet inference pipeline on real
DeepMind cylinder_flow data. Each MR residual is computed from model output and compared
to a fixed, physically motivated tolerance. No kill row is synthesized from labels.
