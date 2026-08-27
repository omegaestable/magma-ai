# Sweep report: etp-sweep-200k-2026-08-27-b12

- rows: **10000**
- solved: **9993 (99.93%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **7**
- solver-claimed verdicts: {'false': 4920, 'true': 5073}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 43, 57
- seconds: total 18423.5, mean 1.842, p50 0.006, p95 9.517, p99 11.38, slowest solved 229.524

## Route families

- `witness`: 4585
- `singleton`: 2335
- `egg_collapse`: 1246
- `completion`: 882
- `spine`: 181
- `equational_closure`: 147
- `linear`: 125
- `constancy`: 89
- `derived_cp_closure`: 82
- `egg_bootstrap`: 70
- `universal_identity`: 54
- `rewrite`: 27
- `absorption_context_bridge`: 26
- `lemma_bootstrap`: 22
- `enum_fin3`: 20
- `lemma_chain`: 16
- `egg_ladder`: 9
- `tail_square_singleton`: 8
- `nested_square_singleton`: 7
- `forked_square_singleton`: 6
- `left_projection_collapse`: 5
- `absorption_closure`: 5
- `reverse_deep_repeat_singleton`: 4
- `egg_closure`: 3
- `outer_sandwich_singleton`: 3

## Failure clustering by hypothesis law

- eq1 `650`: 2 failures
- eq1 `3569`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {3: 5, 4: 2}, 'eq1_ops': {4: 7}}

## Failure ledger

- `etp_650_3660` [skip, label=true, 419.218s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ x = (x ◇ x) ◇ (x ◇ y)`
- `etp_650_3666` [skip, label=true, 401.2s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ x = (x ◇ y) ◇ (x ◇ z)`
- `etp_3569_3981` [skip, label=true, 522.274s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = (y ◇ (z ◇ z)) ◇ z`
- `etp_3577_392` [skip, label=true, 388.178s] eq1 `x ◇ y = y ◇ ((z ◇ w) ◇ x)` => eq2 `x ◇ y = (y ◇ z) ◇ z`
- `etp_4465_4468` [skip, label=true, 320.142s] eq1 `x ◇ (y ◇ x) = (z ◇ w) ◇ y` => eq2 `x ◇ (y ◇ x) = (z ◇ w) ◇ u`
- `etp_3067_3056` [skip, label=true, 341.79s] eq1 `x = (((x ◇ y) ◇ x) ◇ x) ◇ z` => eq2 `x = (((x ◇ x) ◇ y) ◇ x) ◇ y`
- `etp_3569_405` [skip, label=true, 449.8s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = (z ◇ z) ◇ w`
