# Sweep report: etp-sweep-200k-2026-08-26-b03

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'false': 5022, 'true': 4974}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 43, 57
- seconds: total 15842.7, mean 1.584, p50 0.003, p95 9.319, p99 9.884, slowest solved 216.414

## Route families

- `witness`: 4700
- `singleton`: 2347
- `egg_collapse`: 1328
- `completion`: 713
- `spine`: 158
- `equational_closure`: 150
- `linear`: 134
- `constancy`: 118
- `derived_cp_closure`: 62
- `egg_bootstrap`: 57
- `universal_identity`: 38
- `rewrite`: 30
- `absorption_context_bridge`: 20
- `enum_fin3`: 17
- `lemma_bootstrap`: 16
- `lemma_chain`: 14
- `tail_square_singleton`: 10
- `egg_ladder`: 9
- `absorption_closure`: 7
- `right_projection_collapse`: 5
- `outer_sandwich_singleton`: 5
- `alternating_front_self_collapse`: 5
- `constraint_fin8`: 5
- `nested_square_singleton`: 4
- `affine`: 4

## Failure clustering by hypothesis law

- eq1 `650`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {3: 3, 4: 1}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_650_2676` [skip, label=true, 380.249s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ y) ◇ (y ◇ z)) ◇ y`
- `etp_3983_3704` [skip, label=true, 373.101s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ x = (y ◇ z) ◇ (z ◇ z)`
- `etp_650_322` [skip, label=true, 453.412s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = x ◇ (x ◇ x)`
- `etp_3122_290` [skip, label=false, 457.112s] eq1 `x = (((y ◇ x) ◇ z) ◇ x) ◇ x` => eq2 `x = ((y ◇ z) ◇ x) ◇ x`
