# Sweep report: etp-sweep-200k-2026-08-27-b07

- rows: **10000**
- solved: **9993 (99.93%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **7**
- solver-claimed verdicts: {'false': 4959, 'true': 5034}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 47, 59
- seconds: total 18495.8, mean 1.85, p50 0.005, p95 9.503, p99 11.457, slowest solved 174.128

## Route families

- `witness`: 4646
- `singleton`: 2336
- `egg_collapse`: 1247
- `completion`: 790
- `spine`: 173
- `equational_closure`: 138
- `constancy`: 123
- `linear`: 105
- `derived_cp_closure`: 100
- `egg_bootstrap`: 63
- `universal_identity`: 46
- `rewrite`: 32
- `absorption_context_bridge`: 25
- `enum_fin3`: 21
- `lemma_chain`: 21
- `lemma_bootstrap`: 21
- `egg_ladder`: 12
- `absorption_closure`: 10
- `egg_closure`: 9
- `local_model4`: 7
- `nested_square_singleton`: 5
- `right_projection_collapse`: 5
- `tail_square_singleton`: 5
- `front_double_self_collapse`: 4
- `mirrored_alternating_front_self_collapse`: 4

## Failure clustering by hypothesis law

- eq1 `650`: 3 failures

Failure shapes: {'eq1_bare_variable_side': 6, 'eq1_vars': {3: 6, 4: 1}, 'eq1_ops': {4: 7}}

## Failure ledger

- `etp_650_2878` [skip, label=true, 390.212s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ (y ◇ y)) ◇ z) ◇ x`
- `etp_3983_319` [skip, label=true, 379.747s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ x = y ◇ (z ◇ y)`
- `etp_650_457` [skip, label=true, 465.079s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (y ◇ (z ◇ (z ◇ w)))`
- `etp_2923_290` [skip, label=true, 434.074s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((y ◇ z) ◇ x) ◇ x`
- `etp_1368_2737` [skip, label=false, 278.897s] eq1 `x = y ◇ (((z ◇ y) ◇ x) ◇ z)` => eq2 `x = ((y ◇ y) ◇ (x ◇ y)) ◇ y`
- `etp_650_448` [skip, label=true, 433.382s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (y ◇ (z ◇ (x ◇ z)))`
- `etp_2854_4361` [skip, label=true, 376.514s] eq1 `x = ((x ◇ (x ◇ y)) ◇ x) ◇ z` => eq2 `x ◇ (y ◇ z) = x ◇ (w ◇ u)`
