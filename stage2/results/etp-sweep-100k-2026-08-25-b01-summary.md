# Sweep report: etp-sweep-100k-2026-08-25-b01

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'true': 4947, 'false': 5049}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 46, 54
- seconds: total 16608.9, mean 1.661, p50 0.003, p95 9.376, p99 11.331, slowest solved 166.232

## Route families

- `witness`: 4730
- `singleton`: 2318
- `egg_collapse`: 1257
- `completion`: 753
- `spine`: 184
- `equational_closure`: 150
- `constancy`: 143
- `linear`: 107
- `egg_bootstrap`: 62
- `derived_cp_closure`: 60
- `rewrite`: 35
- `universal_identity`: 34
- `egg_ladder`: 19
- `lemma_bootstrap`: 19
- `absorption_context_bridge`: 15
- `enum_fin3`: 15
- `tail_square_singleton`: 9
- `egg_closure`: 8
- `lemma_chain`: 8
- `absorption_closure`: 8
- `local_model4`: 7
- `left_projection_collapse`: 5
- `outer_sandwich_singleton`: 4
- `alternating_front_self_collapse`: 4
- `deep_repeat_singleton`: 4

## Failure clustering by hypothesis law

- eq1 `3569`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 1, 'eq1_vars': {3: 3, 4: 1}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_3569_4296` [skip, label=true, 515.017s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ (x ◇ y) = y ◇ (z ◇ y)`
- `etp_3983_4296` [skip, label=true, 374.227s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ (x ◇ y) = y ◇ (z ◇ y)`
- `etp_3569_4688` [skip, label=true, 326.735s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `(x ◇ y) ◇ z = (z ◇ w) ◇ u`
- `etp_2162_3877` [skip, label=false, 319.518s] eq1 `x = ((y ◇ z) ◇ x) ◇ (x ◇ y)` => eq2 `x ◇ x = (y ◇ (x ◇ x)) ◇ x`
