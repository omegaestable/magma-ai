# Sweep report: order6-hard-pilot-500-2026-08-25

- rows: **500**
- solved: **499 (99.8%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **1**
- solver-claimed verdicts: {'false': 487, 'true': 12}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 0, 0
- seconds: total 1952.6, mean 3.905, p50 0.007, p95 0.024, p99 142.093, slowest solved 246.438

## Route families

- `witness`: 234
- `linear`: 197
- `spine`: 35
- `singleton`: 9
- `affine`: 9
- `enum_fin3`: 4
- `local_model4`: 4
- `central`: 4
- `derived_cp_closure`: 2
- `completion`: 1

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 1, 'eq1_vars': {2: 1}, 'eq1_ops': {6: 1}}

## Failure ledger

- `order6_16514_17426` [skip, label=unlabelled, 300.0s] eq1 `x = ((((x * x) * (x * x)) * x) * x) * y` => eq2 `x * x = x * (y * (((x * x) * x) * y))`
