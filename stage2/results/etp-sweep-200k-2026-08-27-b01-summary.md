# Sweep report: etp-sweep-200k-2026-08-27-b01

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'true': 5041, 'false': 4954}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 41, 55
- seconds: total 17404.1, mean 1.74, p50 0.005, p95 9.463, p99 11.464, slowest solved 327.44

## Route families

- `witness`: 4658
- `singleton`: 2371
- `egg_collapse`: 1248
- `completion`: 787
- `spine`: 166
- `equational_closure`: 160
- `constancy`: 115
- `linear`: 110
- `egg_bootstrap`: 73
- `derived_cp_closure`: 68
- `rewrite`: 39
- `universal_identity`: 38
- `absorption_context_bridge`: 22
- `lemma_bootstrap`: 21
- `lemma_chain`: 20
- `egg_ladder`: 12
- `enum_fin3`: 12
- `wrapped_tail_singleton`: 9
- `absorption_closure`: 8
- `tail_square_singleton`: 7
- `front_double_self_collapse`: 5
- `outer_sandwich_singleton`: 5
- `right_projection_collapse`: 4
- `forked_square_singleton`: 3
- `nested_left_projection`: 3

## Failure clustering by hypothesis law

- eq1 `650`: 2 failures
- eq1 `2923`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 4, 'eq1_vars': {3: 4, 4: 1}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_650_268` [skip, label=true, 389.543s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ y) ◇ z) ◇ z`
- `etp_3983_3580` [skip, label=true, 421.632s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = y ◇ ((z ◇ w) ◇ w)`
- `etp_650_49` [skip, label=true, 418.825s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (x ◇ (y ◇ x))`
- `etp_2923_1701` [skip, label=true, 432.84s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = (y ◇ x) ◇ ((z ◇ x) ◇ x)`
- `etp_2923_3680` [skip, label=true, 375.767s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ x = (y ◇ x) ◇ (z ◇ x)`
