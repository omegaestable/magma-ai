# Sweep report: etp-sweep-200k-2026-08-26-b01

- rows: **10000**
- solved: **9994 (99.94%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **6**
- solver-claimed verdicts: {'false': 4957, 'true': 5037}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 43, 51
- seconds: total 16561.8, mean 1.656, p50 0.003, p95 9.356, p99 10.71, slowest solved 411.646

## Route families

- `witness`: 4667
- `singleton`: 2380
- `egg_collapse`: 1247
- `completion`: 756
- `equational_closure`: 159
- `spine`: 151
- `constancy`: 122
- `linear`: 112
- `derived_cp_closure`: 84
- `egg_bootstrap`: 71
- `universal_identity`: 52
- `rewrite`: 30
- `lemma_bootstrap`: 22
- `absorption_context_bridge`: 22
- `lemma_chain`: 18
- `enum_fin3`: 16
- `absorption_closure`: 8
- `egg_ladder`: 8
- `paired_tail_singleton`: 7
- `tail_square_singleton`: 7
- `reverse_deep_repeat_singleton`: 5
- `local_model4`: 5
- `alternating_front_self_collapse`: 5
- `middle_self_collapse`: 5
- `nested_square_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 4, 'eq1_vars': {3: 3, 2: 2, 4: 1}, 'eq1_ops': {4: 6}}

## Failure ledger

- `etp_650_4130` [skip, label=true, 411.447s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = ((x ◇ y) ◇ y) ◇ x`
- `etp_3051_3070` [skip, label=true, 321.45s] eq1 `x = (((x ◇ x) ◇ x) ◇ x) ◇ y` => eq2 `x = (((x ◇ y) ◇ x) ◇ y) ◇ z`
- `etp_3569_4107` [skip, label=true, 447.259s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ x = ((y ◇ z) ◇ y) ◇ w`
- `etp_3983_4028` [skip, label=true, 366.798s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (z ◇ (z ◇ y)) ◇ z`
- `etp_1979_1668` [skip, label=false, 311.559s] eq1 `x = (y ◇ (z ◇ y)) ◇ (y ◇ x)` => eq2 `x = (x ◇ y) ◇ ((z ◇ y) ◇ x)`
- `etp_463_491` [skip, label=true, 282.293s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x = y ◇ (x ◇ (z ◇ (z ◇ x)))`
