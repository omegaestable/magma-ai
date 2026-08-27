# Sweep report: etp-sweep-200k-2026-08-26-b09

- rows: **10000**
- solved: **9993 (99.93%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **7**
- solver-claimed verdicts: {'true': 5019, 'false': 4974}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 63, 71
- seconds: total 17583.8, mean 1.758, p50 0.006, p95 9.482, p99 11.418, slowest solved 138.305

## Route families

- `witness`: 4657
- `singleton`: 2355
- `egg_collapse`: 1228
- `completion`: 763
- `spine`: 162
- `equational_closure`: 154
- `constancy`: 134
- `linear`: 124
- `derived_cp_closure`: 74
- `egg_bootstrap`: 65
- `universal_identity`: 45
- `absorption_context_bridge`: 30
- `rewrite`: 30
- `lemma_bootstrap`: 22
- `lemma_chain`: 20
- `enum_fin3`: 18
- `tail_square_singleton`: 12
- `egg_ladder`: 11
- `egg_closure`: 8
- `forked_square_singleton`: 6
- `outer_sandwich_singleton`: 6
- `mirrored_alternating_front_self_collapse`: 5
- `constraint_fin8`: 5
- `front_double_self_collapse`: 5
- `nested_square_singleton`: 4

## Failure clustering by hypothesis law

- eq1 `2923`: 2 failures
- eq1 `650`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 7, 'eq1_vars': {3: 5, 2: 2}, 'eq1_ops': {4: 7}}

## Failure ledger

- `etp_2923_566` [skip, label=true, 404.237s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (z ◇ (y ◇ (w ◇ x)))`
- `etp_3051_3080` [skip, label=true, 330.279s] eq1 `x = (((x ◇ x) ◇ x) ◇ x) ◇ y` => eq2 `x = (((x ◇ y) ◇ y) ◇ y) ◇ z`
- `etp_2531_99` [skip, label=false, 357.55s] eq1 `x = (y ◇ ((y ◇ x) ◇ x)) ◇ y` => eq2 `x = x ◇ ((x ◇ x) ◇ x)`
- `etp_650_2264` [skip, label=true, 419.441s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ (y ◇ x))) ◇ y`
- `etp_1789_4217` [skip, label=true, 451.012s] eq1 `x = (y ◇ z) ◇ ((z ◇ x) ◇ x)` => eq2 `x ◇ y = ((z ◇ y) ◇ z) ◇ y`
- `etp_650_2042` [skip, label=true, 389.545s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ x) ◇ y) ◇ (x ◇ z)`
- `etp_2923_3167` [skip, label=true, 433.033s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = (((y ◇ y) ◇ z) ◇ z) ◇ x`
