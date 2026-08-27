# Sweep report: etp-sweep-200k-2026-08-27-b18

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'true': 5029, 'false': 4967}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 41, 50
- seconds: total 16612.1, mean 1.661, p50 0.005, p95 9.445, p99 11.417, slowest solved 186.395

## Route families

- `witness`: 4641
- `singleton`: 2412
- `egg_collapse`: 1215
- `completion`: 777
- `spine`: 184
- `equational_closure`: 154
- `constancy`: 127
- `linear`: 115
- `egg_bootstrap`: 77
- `derived_cp_closure`: 61
- `universal_identity`: 36
- `rewrite`: 30
- `absorption_context_bridge`: 28
- `lemma_bootstrap`: 17
- `enum_fin3`: 16
- `lemma_chain`: 15
- `egg_ladder`: 13
- `absorption_closure`: 7
- `egg_closure`: 6
- `reverse_deep_repeat_singleton`: 5
- `front_double_self_collapse`: 5
- `outer_sandwich_singleton`: 4
- `affine`: 4
- `wrapped_tail_singleton`: 4
- `alternating_front_self_collapse`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 2, 2: 1, 4: 1}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_3569_3903` [skip, label=true, 523.923s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ x = (y ◇ (z ◇ y)) ◇ z`
- `etp_463_4040` [skip, label=true, 348.751s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ y = (z ◇ (w ◇ x)) ◇ y`
- `etp_3577_3906` [skip, label=true, 382.143s] eq1 `x ◇ y = y ◇ ((z ◇ w) ◇ x)` => eq2 `x ◇ x = (y ◇ (z ◇ z)) ◇ y`
- `etp_650_163` [skip, label=true, 425.565s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ y) ◇ (z ◇ y)`
