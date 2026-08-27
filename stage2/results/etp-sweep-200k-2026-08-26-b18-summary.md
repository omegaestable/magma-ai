# Sweep report: etp-sweep-200k-2026-08-26-b18

- rows: **10000**
- solved: **9997 (99.97%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **3**
- solver-claimed verdicts: {'false': 4923, 'true': 5074}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 44, 52
- seconds: total 16575.0, mean 1.658, p50 0.004, p95 9.336, p99 10.235, slowest solved 214.598

## Route families

- `witness`: 4582
- `singleton`: 2380
- `egg_collapse`: 1316
- `completion`: 762
- `spine`: 187
- `equational_closure`: 151
- `constancy`: 136
- `linear`: 124
- `derived_cp_closure`: 73
- `egg_bootstrap`: 62
- `rewrite`: 29
- `universal_identity`: 27
- `absorption_context_bridge`: 24
- `lemma_bootstrap`: 22
- `egg_ladder`: 14
- `lemma_chain`: 13
- `enum_fin3`: 11
- `tail_square_singleton`: 8
- `constraint_fin8`: 6
- `egg_closure`: 6
- `deep_repeat_singleton`: 6
- `reverse_deep_repeat_singleton`: 5
- `right_projection_collapse`: 5
- `dual`: 5
- `outer_sandwich_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 3}, 'eq1_ops': {4: 3}}

## Failure ledger

- `etp_4457_4393` [skip, label=true, 495.94s] eq1 `x ◇ (y ◇ x) = (z ◇ y) ◇ y` => eq2 `x ◇ (x ◇ x) = (y ◇ z) ◇ z`
- `etp_650_2486` [skip, label=true, 423.088s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ z) ◇ z)) ◇ z`
- `etp_3067_4656` [skip, label=true, 358.575s] eq1 `x = (((x ◇ y) ◇ x) ◇ x) ◇ z` => eq2 `(x ◇ y) ◇ y = (x ◇ z) ◇ z`
