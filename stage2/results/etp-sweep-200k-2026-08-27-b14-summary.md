# Sweep report: etp-sweep-200k-2026-08-27-b14

- rows: **10000**
- solved: **9998 (99.98%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **2**
- solver-claimed verdicts: {'false': 5072, 'true': 4926}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 39, 54
- seconds: total 15536.1, mean 1.554, p50 0.006, p95 9.485, p99 11.594, slowest solved 122.061

## Route families

- `witness`: 4731
- `singleton`: 2306
- `egg_collapse`: 1232
- `completion`: 760
- `spine`: 177
- `equational_closure`: 159
- `linear`: 127
- `constancy`: 121
- `derived_cp_closure`: 76
- `egg_bootstrap`: 58
- `universal_identity`: 41
- `rewrite`: 30
- `lemma_chain`: 24
- `enum_fin3`: 23
- `absorption_context_bridge`: 23
- `lemma_bootstrap`: 16
- `absorption_closure`: 8
- `egg_ladder`: 8
- `egg_closure`: 7
- `right_projection_collapse`: 7
- `local_model4`: 6
- `deep_repeat_singleton`: 5
- `wrapped_tail_singleton`: 5
- `outer_sandwich_singleton`: 4
- `nested_square_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 1, 'eq1_vars': {3: 1, 4: 1}, 'eq1_ops': {4: 2}}

## Failure ledger

- `etp_2923_205` [skip, label=true, 419.183s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = (x ◇ (x ◇ y)) ◇ x`
- `etp_3983_4181` [skip, label=true, 421.149s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = ((y ◇ z) ◇ y) ◇ w`
