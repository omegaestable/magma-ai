# Sweep report: etp-sweep-100k-2026-08-25-b09

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'false': 4959, 'true': 5036}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 49, 58
- seconds: total 15939.5, mean 1.594, p50 0.004, p95 9.282, p99 9.778, slowest solved 213.95

## Route families

- `witness`: 4636
- `singleton`: 2331
- `egg_collapse`: 1341
- `completion`: 712
- `equational_closure`: 172
- `spine`: 166
- `constancy`: 133
- `linear`: 123
- `egg_bootstrap`: 74
- `derived_cp_closure`: 72
- `universal_identity`: 33
- `rewrite`: 28
- `lemma_bootstrap`: 21
- `absorption_context_bridge`: 21
- `enum_fin3`: 21
- `lemma_chain`: 18
- `tail_square_singleton`: 11
- `absorption_closure`: 9
- `constraint_fin8`: 7
- `egg_ladder`: 6
- `middle_self_collapse`: 6
- `wrapped_tail_singleton`: 4
- `egg_closure`: 4
- `repeated_prefix_product_constancy`: 4
- `front_double_self_collapse`: 3

## Failure clustering by hypothesis law

- eq1 `2923`: 2 failures
- eq1 `650`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 5, 'eq1_vars': {3: 5}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_2923_2137` [skip, label=true, 411.559s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((y ◇ y) ◇ y) ◇ (y ◇ x)`
- `etp_650_381` [skip, label=true, 381.332s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = (x ◇ z) ◇ y`
- `etp_481_2132` [skip, label=false, 304.682s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = ((y ◇ y) ◇ x) ◇ (z ◇ z)`
- `etp_650_2284` [skip, label=true, 459.84s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ (z ◇ z))) ◇ w`
- `etp_2923_3405` [skip, label=true, 304.568s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = z ◇ (y ◇ (z ◇ y))`
