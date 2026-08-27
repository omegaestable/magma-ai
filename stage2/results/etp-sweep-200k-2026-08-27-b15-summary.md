# Sweep report: etp-sweep-200k-2026-08-27-b15

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'true': 4934, 'false': 5062}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 47, 58
- seconds: total 15723.2, mean 1.572, p50 0.005, p95 9.445, p99 10.416, slowest solved 243.087

## Route families

- `witness`: 4721
- `singleton`: 2367
- `egg_collapse`: 1202
- `completion`: 762
- `spine`: 182
- `equational_closure`: 145
- `linear`: 124
- `constancy`: 100
- `derived_cp_closure`: 73
- `egg_bootstrap`: 70
- `rewrite`: 37
- `universal_identity`: 34
- `lemma_bootstrap`: 31
- `enum_fin3`: 23
- `absorption_context_bridge`: 20
- `lemma_chain`: 17
- `egg_ladder`: 7
- `tail_square_singleton`: 7
- `absorption_closure`: 7
- `deep_repeat_singleton`: 5
- `wrapped_tail_singleton`: 5
- `local_model4`: 5
- `forked_square_singleton`: 4
- `sandwich_repeat_singleton`: 4
- `nested_square_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 3, 4: 1}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_650_624` [skip, label=true, 440.541s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (x ◇ ((y ◇ y) ◇ z))`
- `etp_1740_1113` [skip, label=true, 312.92s] eq1 `x = (y ◇ y) ◇ ((z ◇ x) ◇ z)` => eq2 `x = y ◇ ((y ◇ (x ◇ y)) ◇ y)`
- `etp_3577_4414` [skip, label=true, 421.426s] eq1 `x ◇ y = y ◇ ((z ◇ w) ◇ x)` => eq2 `x ◇ (x ◇ y) = (y ◇ z) ◇ w`
- `etp_3569_4008` [skip, label=true, 449.331s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = (z ◇ (y ◇ x)) ◇ w`
