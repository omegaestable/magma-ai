# Sweep report: etp-sweep-200k-2026-08-26-b14

- rows: **10000**
- solved: **9997 (99.97%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **3**
- solver-claimed verdicts: {'true': 4974, 'false': 5023}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 49, 57
- seconds: total 16474.1, mean 1.647, p50 0.005, p95 9.478, p99 10.96, slowest solved 218.544

## Route families

- `witness`: 4713
- `singleton`: 2331
- `egg_collapse`: 1259
- `completion`: 796
- `spine`: 168
- `equational_closure`: 131
- `constancy`: 129
- `linear`: 108
- `derived_cp_closure`: 71
- `egg_bootstrap`: 66
- `universal_identity`: 40
- `enum_fin3`: 22
- `rewrite`: 20
- `absorption_context_bridge`: 20
- `lemma_chain`: 18
- `lemma_bootstrap`: 17
- `outer_sandwich_singleton`: 10
- `forked_square_singleton`: 8
- `absorption_closure`: 7
- `right_projection_collapse`: 6
- `egg_ladder`: 6
- `tail_square_singleton`: 5
- `egg_closure`: 5
- `sandwich_repeat_singleton`: 4
- `crossed_pair_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 2, 2: 1}, 'eq1_ops': {4: 3}}

## Failure ledger

- `etp_650_3529` [skip, label=true, 483.423s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = x ◇ ((z ◇ x) ◇ y)`
- `etp_3051_3510` [skip, label=true, 338.361s] eq1 `x = (((x ◇ x) ◇ x) ◇ x) ◇ y` => eq2 `x ◇ y = x ◇ ((x ◇ x) ◇ z)`
- `etp_3569_4628` [skip, label=true, 332.495s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `(x ◇ x) ◇ y = (z ◇ w) ◇ u`
