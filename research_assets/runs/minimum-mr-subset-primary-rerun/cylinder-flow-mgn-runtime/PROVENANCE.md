# Provenance for cylinder-flow-mgn-runtime

Generated at: `2026-06-12T00:45:09Z`

## Runtime command

```bash
PYTHONPATH=scripts python -m mcmr.cylinder_flow.witness_stage_b \
  --checkpoint runs/cylinder-flow-mgn-training-20260605T021147Z/checkpoint.pt \
  --data-npz data/raw/cylinder_flow_deepmind/cylinder_flow_eval.npz \
  --training-run runs/cylinder-flow-mgn-training-20260605T021147Z \
  --trials 0,2,4,6,8 --outdir research_assets/runs/minimum-mr-subset-primary-rerun/cylinder-flow-mgn-runtime
```

## Source artifacts

- `scripts/mcmr/cylinder_flow/mgn.py`
- `scripts/mcmr/cylinder_flow/dm_dataset.py`
- `scripts/mcmr/cylinder_flow/witness_stage_b.py`
- `runs/cylinder-flow-mgn-training-20260605T021147Z/checkpoint.pt`
- `data/raw/cylinder_flow_deepmind/cylinder_flow_eval.npz`
- `data/raw/cylinder_flow_deepmind/meta.json`
- `data/raw/cylinder_flow_deepmind/cylinder_flow_train.npz`
- `runs/cylinder-flow-mgn-training-20260605T021147Z/data_manifest.json`

## Honesty boundary

Real DeepMind benchmark; real trained weights; real inference. PASS only if the runtime
kill matrix satisfies fault_classes_active>=3, max_fault_class_signature_rank>1, and
kstar>fault_classes_active. Otherwise the run is recorded as DEGRADED_WITNESS.
