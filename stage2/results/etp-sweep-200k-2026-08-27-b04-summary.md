# Sweep report: etp-sweep-200k-2026-08-27-b04

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'true': 4974, 'false': 5021}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 65, 73
- seconds: total 16912.2, mean 1.691, p50 0.006, p95 9.499, p99 10.4, slowest solved 224.919

## Route families

- `witness`: 4691
- `singleton`: 2300
- `egg_collapse`: 1220
- `completion`: 831
- `spine`: 167
- `equational_closure`: 146
- `linear`: 128
- `constancy`: 126
- `derived_cp_closure`: 75
- `egg_bootstrap`: 62
- `rewrite`: 39
- `universal_identity`: 36
- `enum_fin3`: 26
- `absorption_context_bridge`: 19
- `lemma_bootstrap`: 17
- `lemma_chain`: 17
- `forked_square_singleton`: 9
- `tail_square_singleton`: 9
- `deep_repeat_singleton`: 8
- `egg_closure`: 7
- `nested_square_singleton`: 5
- `middle_self_collapse`: 5
- `alternating_front_self_collapse`: 5
- `crossed_pair_singleton`: 4
- `reverse_deep_repeat_singleton`: 4

## Failure clustering by hypothesis law

- eq1 `650`: 3 failures

Failure shapes: {'eq1_bare_variable_side': 4, 'eq1_vars': {3: 5}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_3569_4148` [skip, label=true, 451.152s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = ((x ◇ z) ◇ z) ◇ w`
- `etp_650_1473` [skip, label=true, 464.52s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ y) ◇ (z ◇ (w ◇ x))`
- `etp_650_1430` [skip, label=true, 439.935s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ x) ◇ (x ◇ (y ◇ z))`
- `etp_650_216` [skip, label=true, 433.877s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ z)) ◇ z`
- `etp_2923_856` [skip, label=true, 383.472s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = x ◇ ((y ◇ z) ◇ (y ◇ x))`
