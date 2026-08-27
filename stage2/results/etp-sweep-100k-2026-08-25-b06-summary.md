# Sweep report: etp-sweep-100k-2026-08-25-b06

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'true': 4899, 'false': 5097}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 43, 49
- seconds: total 16150.0, mean 1.615, p50 0.004, p95 9.338, p99 10.291, slowest solved 354.707

## Route families

- `witness`: 4772
- `singleton`: 2305
- `egg_collapse`: 1228
- `completion`: 735
- `equational_closure`: 161
- `spine`: 155
- `linear`: 130
- `constancy`: 112
- `egg_bootstrap`: 75
- `derived_cp_closure`: 75
- `universal_identity`: 38
- `rewrite`: 37
- `lemma_bootstrap`: 26
- `absorption_context_bridge`: 24
- `enum_fin3`: 23
- `lemma_chain`: 14
- `absorption_closure`: 9
- `egg_ladder`: 8
- `affine`: 6
- `nested_square_singleton`: 6
- `tail_square_singleton`: 5
- `deep_repeat_singleton`: 4
- `dual`: 4
- `middle_self_collapse`: 4
- `constraint_fin5`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {3: 3, 2: 1}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_3569_3370` [skip, label=true, 511.071s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = y ◇ (z ◇ (z ◇ x))`
- `etp_1366_3965` [skip, label=true, 410.546s] eq1 `x = y ◇ (((z ◇ y) ◇ x) ◇ x)` => eq2 `x ◇ y = (y ◇ (y ◇ y)) ◇ y`
- `etp_3051_4676` [skip, label=true, 205.458s] eq1 `x = (((x ◇ x) ◇ x) ◇ x) ◇ y` => eq2 `(x ◇ y) ◇ z = (x ◇ w) ◇ u`
- `etp_2923_4150` [skip, label=true, 502.413s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = ((x ◇ z) ◇ w) ◇ y`
