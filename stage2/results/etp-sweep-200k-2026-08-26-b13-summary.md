# Sweep report: etp-sweep-200k-2026-08-26-b13

- rows: **10000**
- solved: **9997 (99.97%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **3**
- solver-claimed verdicts: {'false': 4969, 'true': 5028}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 40, 51
- seconds: total 16863.3, mean 1.686, p50 0.004, p95 9.492, p99 11.609, slowest solved 214.969

## Route families

- `witness`: 4654
- `singleton`: 2377
- `egg_collapse`: 1254
- `completion`: 800
- `spine`: 173
- `equational_closure`: 142
- `constancy`: 114
- `linear`: 95
- `egg_bootstrap`: 73
- `derived_cp_closure`: 64
- `universal_identity`: 37
- `rewrite`: 31
- `enum_fin3`: 25
- `lemma_bootstrap`: 22
- `lemma_chain`: 21
- `absorption_context_bridge`: 21
- `egg_ladder`: 8
- `egg_closure`: 6
- `affine`: 6
- `dual`: 6
- `absorption_closure`: 5
- `constraint_fin8`: 4
- `outer_sandwich_singleton`: 4
- `sandwich_repeat_singleton`: 4
- `wrapped_tail_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 1, 'eq1_vars': {2: 1, 4: 1, 3: 1}, 'eq1_ops': {4: 3}}

## Failure ledger

- `etp_4167_4118` [skip, label=false, 470.127s] eq1 `x ◇ y = ((y ◇ y) ◇ y) ◇ x` => eq2 `x ◇ y = ((x ◇ x) ◇ x) ◇ y`
- `etp_3983_4058` [skip, label=true, 303.389s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (z ◇ (w ◇ w)) ◇ u`
- `etp_1979_1742` [skip, label=false, 315.221s] eq1 `x = (y ◇ (z ◇ y)) ◇ (y ◇ x)` => eq2 `x = (y ◇ y) ◇ ((z ◇ y) ◇ x)`
