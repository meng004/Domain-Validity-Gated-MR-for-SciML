# Reproducible training command

```bash
PYTHONPATH=scripts python -m mcmr.cylinder_flow.train_stage_a --steps 1500 --seed 2 --t-eval 0
```

- Data: https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/train.tfrecord (Range bytes for trajectory 5, frames 100-250; sustained vortex shedding)
- Checkpoint sha256: `e41ebaf14ce19b0c5ba8e51c0826ba8ba3b44e449b8bf24586fda8155cecf562`
