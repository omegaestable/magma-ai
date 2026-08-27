# Sweep report: etp-sweep-200k-2026-08-27-b09

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'false': 5096, 'true': 4899}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 43, 52
- seconds: total 16931.7, mean 1.693, p50 0.004, p95 9.473, p99 11.0, slowest solved 281.149

## Route families

- `witness`: 4772
- `singleton`: 2385
- `egg_collapse`: 1163
- `completion`: 751
- `spine`: 171
- `equational_closure`: 151
- `linear`: 120
- `constancy`: 110
- `egg_bootstrap`: 71
- `derived_cp_closure`: 68
- `universal_identity`: 37
- `absorption_context_bridge`: 26
- `enum_fin3`: 23
- `rewrite`: 22
- `lemma_bootstrap`: 21
- `lemma_chain`: 18
- `egg_ladder`: 10
- `egg_closure`: 7
- `crossed_pair_singleton`: 7
- `tail_square_singleton`: 5
- `right_projection_collapse`: 5
- `forked_square_singleton`: 4
- `mirrored_alternating_front_self_collapse`: 4
- `front_double_self_collapse`: 4
- `sandwich_repeat_singleton`: 4

## Failure clustering by hypothesis law

- eq1 `2923`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 4, 'eq1_vars': {3: 3, 2: 1, 4: 1}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_650_2481` [skip, label=true, 440.975s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ z) ◇ y)) ◇ y`
- `etp_463_4070` [skip, label=true, 313.056s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ x = ((x ◇ y) ◇ x) ◇ x`
- `etp_3295_3287` [skip, label=false, 339.571s] eq1 `x ◇ x = y ◇ (z ◇ (y ◇ w))` => eq2 `x ◇ x = y ◇ (y ◇ (z ◇ w))`
- `etp_2923_286` [skip, label=true, 434.324s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((y ◇ y) ◇ z) ◇ x`
- `etp_2923_500` [skip, label=true, 365.981s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (y ◇ (x ◇ (x ◇ x)))`
