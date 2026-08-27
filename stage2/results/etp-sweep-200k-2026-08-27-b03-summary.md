# Sweep report: etp-sweep-200k-2026-08-27-b03

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'false': 4982, 'true': 5013}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 46, 57
- seconds: total 16769.5, mean 1.677, p50 0.006, p95 9.481, p99 10.365, slowest solved 230.44

## Route families

- `witness`: 4681
- `singleton`: 2339
- `egg_collapse`: 1260
- `completion`: 808
- `spine`: 164
- `equational_closure`: 145
- `constancy`: 118
- `linear`: 114
- `derived_cp_closure`: 70
- `egg_bootstrap`: 69
- `rewrite`: 35
- `universal_identity`: 34
- `absorption_context_bridge`: 21
- `lemma_bootstrap`: 17
- `enum_fin3`: 16
- `lemma_chain`: 16
- `egg_ladder`: 9
- `forked_square_singleton`: 8
- `egg_closure`: 7
- `right_projection_collapse`: 7
- `alternating_front_self_collapse`: 6
- `tail_square_singleton`: 5
- `absorption_closure`: 5
- `paired_tail_singleton`: 4
- `constraint_fin8`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 4, 'eq1_vars': {3: 4, 2: 1}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_3067_3314` [skip, label=true, 441.675s] eq1 `x = (((x ◇ y) ◇ x) ◇ x) ◇ z` => eq2 `x ◇ y = x ◇ (x ◇ (z ◇ w))`
- `etp_3051_3460` [skip, label=true, 336.64s] eq1 `x = (((x ◇ x) ◇ x) ◇ x) ◇ y` => eq2 `x ◇ x = x ◇ ((x ◇ y) ◇ z)`
- `etp_481_3056` [skip, label=false, 295.774s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = (((x ◇ x) ◇ y) ◇ x) ◇ y`
- `etp_3569_4651` [skip, label=true, 450.119s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `(x ◇ y) ◇ x = (z ◇ w) ◇ z`
- `etp_650_2692` [skip, label=true, 411.676s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ y) ◇ (z ◇ w)) ◇ y`
