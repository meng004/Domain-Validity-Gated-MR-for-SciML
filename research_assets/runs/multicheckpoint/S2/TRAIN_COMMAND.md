# Reproducible training command

```bash
PYTHONPATH=scripts python -m mcmr.cylinder_flow.train_stage_a --steps 1500 --seed 2 --t-eval 0
```

- Data: https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/train.tfrecord (Range bytes for trajectory 5, frames 100-250; sustained vortex shedding)
- Checkpoint sha256: `c63b5126860781012060a89b705915f2098b13a2dc35045cc07f4e52f1151477`
