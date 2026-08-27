# Sweep report: etp-sweep-200k-2026-08-26-b17

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'true': 4929, 'false': 5067}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 42, 49
- seconds: total 16072.6, mean 1.607, p50 0.004, p95 9.329, p99 10.276, slowest solved 225.651

## Route families

- `witness`: 4706
- `singleton`: 2298
- `egg_collapse`: 1268
- `completion`: 758
- `spine`: 207
- `equational_closure`: 145
- `constancy`: 143
- `linear`: 120
- `derived_cp_closure`: 62
- `egg_bootstrap`: 56
- `absorption_context_bridge`: 30
- `rewrite`: 29
- `universal_identity`: 29
- `enum_fin3`: 24
- `lemma_bootstrap`: 20
- `egg_ladder`: 15
- `lemma_chain`: 13
- `absorption_closure`: 11
- `crossed_pair_singleton`: 7
- `reverse_deep_repeat_singleton`: 5
- `alternating_front_self_collapse`: 4
- `forked_square_singleton`: 4
- `tail_square_singleton`: 3
- `front_double_self_collapse`: 3
- `dual`: 3

## Failure clustering by hypothesis law

- eq1 `2923`: 2 failures
- eq1 `3569`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 4}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_2923_347` [skip, label=true, 321.157s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = z ◇ (y ◇ y)`
- `etp_3569_4277` [skip, label=true, 515.466s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ (x ◇ x) = y ◇ (y ◇ z)`
- `etp_2923_2638` [skip, label=true, 335.981s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = (y ◇ ((z ◇ w) ◇ u)) ◇ x`
- `etp_3569_3448` [skip, label=true, 445.608s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = z ◇ (w ◇ (w ◇ w))`
