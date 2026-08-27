# Sweep report: etp-sweep-200k-2026-08-27-b11

- rows: **10000**
- solved: **9993 (99.93%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **7**
- solver-claimed verdicts: {'true': 5090, 'false': 4903}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 46, 56
- seconds: total 17844.1, mean 1.784, p50 0.003, p95 9.5, p99 11.371, slowest solved 204.047

## Route families

- `witness`: 4583
- `singleton`: 2426
- `egg_collapse`: 1221
- `completion`: 826
- `spine`: 164
- `constancy`: 139
- `equational_closure`: 128
- `linear`: 121
- `derived_cp_closure`: 86
- `egg_bootstrap`: 60
- `rewrite`: 37
- `universal_identity`: 31
- `absorption_context_bridge`: 29
- `enum_fin3`: 22
- `lemma_bootstrap`: 16
- `lemma_chain`: 13
- `egg_ladder`: 10
- `absorption_closure`: 8
- `tail_square_singleton`: 6
- `nested_square_singleton`: 5
- `affine`: 5
- `crossed_pair_singleton`: 4
- `right_projection_collapse`: 3
- `paired_tail_singleton`: 3
- `alternating_front_self_collapse`: 3

## Failure clustering by hypothesis law

- eq1 `2923`: 2 failures
- eq1 `650`: 2 failures
- eq1 `3569`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 5, 'eq1_vars': {3: 7}, 'eq1_ops': {4: 7}}

## Failure ledger

- `etp_2923_4080` [skip, label=true, 461.388s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ x = ((y ◇ x) ◇ x) ◇ x`
- `etp_650_4` [skip, label=true, 407.572s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ y`
- `etp_3569_4175` [skip, label=true, 520.483s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = ((y ◇ z) ◇ x) ◇ y`
- `etp_2923_761` [skip, label=true, 380.894s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (z ◇ ((y ◇ y) ◇ x))`
- `etp_650_211` [skip, label=true, 417.786s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ y)) ◇ x`
- `etp_898_861` [skip, label=false, 290.084s] eq1 `x = y ◇ ((x ◇ z) ◇ (z ◇ y))` => eq2 `x = x ◇ ((y ◇ z) ◇ (z ◇ y))`
- `etp_3569_3699` [skip, label=true, 519.58s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ x = (y ◇ z) ◇ (y ◇ y)`
