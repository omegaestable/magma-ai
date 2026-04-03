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
- `normal_balanced10_true5_false5_randmix_seed0_unseen_20260324.jsonl`
- `normal_balanced10_true5_false5_randmix_seed1_unseen_20260324.jsonl`
- `normal_balanced10_true5_false5_randmix_seed2_unseen_20260324.jsonl`

### Unseen Normal Sets

Use only after the normal gate is stable:

- `normal_balanced60_true30_false30_seed20260401_unseen_20260401.jsonl`
- `normal_balanced60_true30_false30_seed20260402_unseen_20260401.jsonl`
- `normal_balanced60_true30_false30_seed20260403_unseen_20260401.jsonl`
- `normal_balanced60_true30_false30_unseen_20260324.jsonl`

### Hard Sets

Use for stress after normal safety:

- `hard1_balanced6_true3_false3_seed0.jsonl`
- `hard1_balanced14_true7_false7_seed0.jsonl`
- `hard2_balanced14_true7_false7_seed0.jsonl`
- `hard3_balanced26_true13_false13_seed0.jsonl`
- `hard3_balanced40_true20_false20_seed41_unseen_20260401.jsonl`
- `hard3_balanced40_true20_false20_seed99_unseen_20260401.jsonl`
- `hard3_balanced60_true30_false30_seed20260401_unseen_20260401.jsonl`
- `hard3_balanced60_true30_false30_seed20260402_unseen_20260401.jsonl`
- `hard3_balanced60_true30_false30_seed20260403_unseen_20260401.jsonl`

### Control Sets

Use only when explicitly testing control behavior:

- `control_balanced100_25x4_seed17.jsonl`
- `control_balanced_normal100_hard20_seed17.jsonl`
- `control_hard20_seed17.jsonl`

## Recommended Default Sequence

1. warmup normal seed0 and seed1
2. full normal seed0, seed1, seed2
3. unseen normal sets
4. hard3 stress sets

If a candidate fails early in that sequence, stop and distill before running more benchmarks.