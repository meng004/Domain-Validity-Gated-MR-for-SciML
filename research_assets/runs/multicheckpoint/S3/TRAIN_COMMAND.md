# Reproducible training command

```bash
PYTHONPATH=scripts python -m mcmr.cylinder_flow.train_stage_a --steps 1500 --seed 3 --t-eval 0
```

- Data: https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/train.tfrecord (Range bytes for trajectory 5, frames 100-250; sustained vortex shedding)
- Checkpoint sha256: `85eafaf1240b19342d701fa80357ef82c5695e12f21846f6e7e0397af62da96e`
