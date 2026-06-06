# Provenance for S3

Generated at: `2026-06-06T14:57:07Z`

## Data source

- Training: https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/train.tfrecord (Range bytes for trajectory 5, frames 100-250; sustained vortex shedding)
- Committed training npz: `data/raw/cylinder_flow_deepmind/cylinder_flow_train.npz` sha256 `2b36285e73e5b7c670b733397759c1acf7957c340fe1a38ad63a4c733be7f493`
- Validation/witness (held-out): `data/raw/cylinder_flow_deepmind/cylinder_flow_eval.npz` (test split)
- Train mesh: 1804 nodes, 3374 cells, 150 frames.

## Model / checkpoint

- `scripts/mcmr/cylinder_flow/mgn.py` MeshGraphNet, config `{"hidden": 64, "num_layers": 4, "node_in": 11, "edge_in": 3, "out_dim": 2, "seed": 3, "steps": 1500, "train_steps_max": 149, "lr": 0.001}`.
- Checkpoint `checkpoint.pt` sha256 `85eafaf1240b19342d701fa80357ef82c5695e12f21846f6e7e0397af62da96e`.

## Honesty boundary

Trained on the DeepMind train split; validated by a one-step inference smoke on the held-out test split (separate trajectory and mesh). No test-split data is used in training.
