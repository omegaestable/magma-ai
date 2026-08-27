# Sweep report: etp-sweep-100k-2026-08-25-b07

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'false': 4966, 'true': 5030}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 55, 63
- seconds: total 15242.3, mean 1.524, p50 0.002, p95 9.293, p99 10.329, slowest solved 214.929

## Route families

- `witness`: 4650
- `singleton`: 2404
- `egg_collapse`: 1269
- `completion`: 700
- `spine`: 172
- `equational_closure`: 143
- `constancy`: 125
- `linear`: 114
- `egg_bootstrap`: 81
- `derived_cp_closure`: 74
- `universal_identity`: 46
- `rewrite`: 32
- `absorption_context_bridge`: 29
- `lemma_chain`: 21
- `lemma_bootstrap`: 18
- `enum_fin3`: 17
- `egg_ladder`: 13
- `deep_repeat_singleton`: 8
- `absorption_closure`: 7
- `crossed_pair_singleton`: 6
- `constraint_fin8`: 6
- `mirrored_alternating_front_self_collapse`: 5
- `tail_square_singleton`: 5
- `middle_self_collapse`: 5
- `wrapped_tail_singleton`: 4

## Failure clustering by hypothesis law

- eq1 `2923`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {3: 3, 4: 1}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_2923_72` [skip, label=true, 372.465s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (y ◇ (x ◇ x))`
- `etp_3983_3963` [skip, label=true, 366.171s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (y ◇ (y ◇ x)) ◇ z`
- `etp_2923_3993` [skip, label=true, 465.754s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = (z ◇ (x ◇ y)) ◇ y`
- `etp_1789_3371` [skip, label=true, 310.756s] eq1 `x = (y ◇ z) ◇ ((z ◇ x) ◇ x)` => eq2 `x ◇ y = y ◇ (z ◇ (z ◇ y))`
