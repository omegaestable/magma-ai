# Sweep report: etp-sweep-200k-2026-08-26-b12

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'false': 4976, 'true': 5019}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 45, 53
- seconds: total 17027.0, mean 1.703, p50 0.005, p95 9.459, p99 10.852, slowest solved 161.618

## Route families

- `witness`: 4698
- `singleton`: 2355
- `egg_collapse`: 1258
- `completion`: 744
- `equational_closure`: 177
- `spine`: 149
- `constancy`: 124
- `linear`: 101
- `derived_cp_closure`: 81
- `egg_bootstrap`: 64
- `universal_identity`: 47
- `rewrite`: 30
- `enum_fin3`: 20
- `lemma_bootstrap`: 20
- `absorption_context_bridge`: 19
- `egg_ladder`: 16
- `lemma_chain`: 14
- `tail_square_singleton`: 13
- `absorption_closure`: 11
- `paired_tail_singleton`: 7
- `forked_square_singleton`: 5
- `middle_self_collapse`: 4
- `wrapped_tail_singleton`: 4
- `egg_closure`: 4
- `right_projection_collapse`: 3

## Failure clustering by hypothesis law

- eq1 `2923`: 4 failures

Failure shapes: {'eq1_bare_variable_side': 4, 'eq1_vars': {3: 4, 4: 1}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_2923_1552` [skip, label=true, 401.663s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = (y ◇ z) ◇ (x ◇ (x ◇ x))`
- `etp_2923_964` [skip, label=true, 390.233s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ ((z ◇ y) ◇ (y ◇ x))`
- `etp_2923_2050` [skip, label=true, 419.205s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((x ◇ y) ◇ x) ◇ (x ◇ x)`
- `etp_2923_1207` [skip, label=true, 464.514s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ ((z ◇ (w ◇ z)) ◇ x)`
- `etp_3983_4223` [skip, label=true, 418.893s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = ((z ◇ y) ◇ w) ◇ w`
