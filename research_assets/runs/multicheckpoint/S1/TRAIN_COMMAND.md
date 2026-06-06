# Reproducible training command

```bash
PYTHONPATH=scripts python -m mcmr.cylinder_flow.train_stage_a --steps 1500 --seed 1 --t-eval 0
```

- Data: https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/train.tfrecord (Range bytes for trajectory 5, frames 100-250; sustained vortex shedding)
- Checkpoint sha256: `dd69cbcce7a1474322ee03ac339093d8a75a537f41581f99988c8776a4b1b339`
