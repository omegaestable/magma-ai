# Sweep report: etp-sweep-200k-2026-08-27-b08

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'true': 4960, 'false': 5036}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 45, 56
- seconds: total 16661.6, mean 1.666, p50 0.005, p95 9.49, p99 10.607, slowest solved 225.985

## Route families

- `witness`: 4724
- `singleton`: 2294
- `egg_collapse`: 1204
- `completion`: 822
- `spine`: 172
- `equational_closure`: 152
- `constancy`: 107
- `linear`: 103
- `derived_cp_closure`: 86
- `egg_bootstrap`: 60
- `rewrite`: 40
- `absorption_context_bridge`: 37
- `universal_identity`: 33
- `lemma_bootstrap`: 26
- `enum_fin3`: 25
- `lemma_chain`: 15
- `egg_ladder`: 14
- `wrapped_tail_singleton`: 7
- `dual`: 6
- `paired_tail_singleton`: 6
- `bridge`: 5
- `egg_closure`: 5
- `forked_square_singleton`: 4
- `absorption_closure`: 4
- `outer_sandwich_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {3: 3, 4: 1}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_2923_3694` [skip, label=true, 439.13s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ x = (y ◇ z) ◇ (x ◇ x)`
- `etp_2162_152` [skip, label=false, 331.788s] eq1 `x = ((y ◇ z) ◇ x) ◇ (x ◇ y)` => eq2 `x = (x ◇ x) ◇ (x ◇ y)`
- `etp_1806_3446` [skip, label=true, 342.345s] eq1 `x = (y ◇ z) ◇ ((w ◇ x) ◇ x)` => eq2 `x ◇ y = z ◇ (w ◇ (w ◇ y))`
- `etp_3569_3822` [skip, label=true, 451.161s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = (z ◇ z) ◇ (x ◇ w)`
