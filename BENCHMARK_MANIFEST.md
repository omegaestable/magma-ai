# Benchmark Manifest

This file explains the naming scheme and intended use of benchmark files under `data/benchmark/`.

## Naming Pattern

Most files follow this pattern:

`<family>_balanced<N>_true<T>_false<F>_seed<seed>[...].jsonl`

Meaning:

- `family`: difficulty family such as `normal`, `hard1`, `hard2`, `hard3`, or `control`
- `balanced<N>`: total number of problems
- `true<T>`: number of TRUE cases
- `false<F>`: number of FALSE cases
- `seed<seed>`: sampling seed used to build the dataset

## Canonical Tiers

### Warmup Normal

Use these first when validating a candidate:

- `normal_balanced10_true5_false5_seed0.jsonl`
- `normal_balanced10_true5_false5_seed1.jsonl`

### Full Normal Gate

Use these before promotion:

- `normal_balanced20_true10_false10_seed0.jsonl`
- `normal_balanced20_true10_false10_seed1.jsonl`
- `normal_balanced20_true10_false10_seed2.jsonl`

### Randomized Or Additional Normal Sets

Useful for variance and robustness checks:

- `normal_balanced20_true10_false10_seed3.jsonl`
- `normal_balanced20_true10_false10_seed61760.jsonl`
- `normal_balanced20_true10_false10_seed694.jsonl`
- `normal_balanced20_true10_false10_seed92229.jsonl`

### Rotating Official-Like Bundles

Use only after the normal gate is stable.

These are not fixed benchmark files anymore. Regenerate them from the official Hugging Face pools each time:

```powershell
C:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe make_unseen_30_30_sets.py --purge-legacy-unseen
```

The generator writes:

- `normal` 30 TRUE / 30 FALSE
- `hard` 20 TRUE / 20 FALSE
- `hard3` 10 TRUE / 10 FALSE

Use `data/benchmark/rotating_official_latest.json` as the canonical pointer to the current bundle.

### Hard Sets

Use for stress after normal safety:

- `hard1_balanced6_true3_false3_seed0.jsonl`
- `hard1_balanced14_true7_false7_seed0.jsonl`
- `hard2_balanced14_true7_false7_seed0.jsonl`
- `hard3_balanced26_true13_false13_seed0.jsonl`

### Control Sets

Use only when explicitly testing control behavior:

- `control_balanced100_25x4_seed17.jsonl`
- `control_balanced_normal100_hard20_seed17.jsonl`
- `control_hard20_seed17.jsonl`

## Recommended Default Sequence

1. warmup normal seed0 and seed1
2. full normal seed0, seed1, seed2
3. regenerate the rotating official-like bundle from Hugging Face
4. evaluate the current `normal`, `hard`, and `hard3` rotation files listed in `data/benchmark/rotating_official_latest.json`

If a candidate fails early in that sequence, stop and distill before running more benchmarks.