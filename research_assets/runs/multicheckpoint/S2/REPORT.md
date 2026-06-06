# S2

status: STAGE_A_TRAINED
dataset: cylinder-flow-mgn-deepmind
benchmark_equivalence_claim: true
split: train (validation/witness reserved for the held-out test split)

## Runtime asset chain

- torch: 2.12.0+cpu
- Checkpoint exists: True (`checkpoint.pt`, 176386 params)
- Training data (train split): True (`data/raw/cylinder_flow_deepmind/cylinder_flow_train.npz`, 150 frames)
- Inference smoke on HELD-OUT test split: true (`data/raw/cylinder_flow_deepmind/cylinder_flow_eval.npz`, pair t=0->1)
- One-step RMSE: 0.0114532; persistence RMSE: 0.0150756; skill x1.32
- Training loss: 1.556 -> 0.02306

## Acceptance

Stage A passes: real checkpoint trained on the DeepMind train split, real held-out test-split inference smoke, committed training npz, documented source.
