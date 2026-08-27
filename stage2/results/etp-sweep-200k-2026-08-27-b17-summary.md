# Sweep report: etp-sweep-200k-2026-08-27-b17

- rows: **10000**
- solved: **9993 (99.93%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **7**
- solver-claimed verdicts: {'true': 5093, 'false': 4900}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 47, 57
- seconds: total 16758.7, mean 1.676, p50 0.003, p95 9.428, p99 10.409, slowest solved 175.191

## Route families

- `witness`: 4612
- `singleton`: 2463
- `egg_collapse`: 1223
- `completion`: 800
- `spine`: 167
- `equational_closure`: 147
- `constancy`: 123
- `linear`: 97
- `derived_cp_closure`: 82
- `egg_bootstrap`: 54
- `universal_identity`: 43
- `rewrite`: 29
- `absorption_context_bridge`: 25
- `enum_fin3`: 14
- `lemma_chain`: 14
- `egg_ladder`: 11
- `absorption_closure`: 8
- `lemma_bootstrap`: 8
- `tail_square_singleton`: 7
- `sandwich_repeat_singleton`: 5
- `dual`: 4
- `forked_square_singleton`: 4
- `outer_sandwich_singleton`: 4
- `nested_square_singleton`: 4
- `middle_self_collapse`: 4

## Failure clustering by hypothesis law

- eq1 `2923`: 3 failures
- eq1 `650`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 5, 'eq1_vars': {3: 6, 4: 1}, 'eq1_ops': {4: 7}}

## Failure ledger

- `etp_2923_3749` [skip, label=true, 418.012s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = (y ◇ x) ◇ (x ◇ y)`
- `etp_3569_3991` [skip, label=true, 449.162s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = (z ◇ (x ◇ x)) ◇ w`
- `etp_3577_4256` [skip, label=true, 307.155s] eq1 `x ◇ y = y ◇ ((z ◇ w) ◇ x)` => eq2 `x ◇ y = ((z ◇ w) ◇ z) ◇ u`
- `etp_650_645` [skip, label=true, 435.844s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (y ◇ ((y ◇ z) ◇ x))`
- `etp_2923_2469` [skip, label=true, 401.833s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = (x ◇ ((y ◇ y) ◇ y)) ◇ x`
- `etp_2923_3752` [skip, label=true, 348.911s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = (y ◇ x) ◇ (y ◇ y)`
- `etp_650_2870` [skip, label=true, 374.833s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ (y ◇ x)) ◇ z) ◇ z`
