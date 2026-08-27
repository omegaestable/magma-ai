# Sweep report: etp-sweep-200k-2026-08-27-b06

- rows: **10000**
- solved: **9997 (99.97%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **3**
- solver-claimed verdicts: {'false': 5002, 'true': 4995}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 46, 52
- seconds: total 16501.7, mean 1.65, p50 0.006, p95 9.47, p99 10.936, slowest solved 315.407

## Route families

- `witness`: 4678
- `singleton`: 2345
- `egg_collapse`: 1209
- `completion`: 785
- `spine`: 176
- `equational_closure`: 158
- `linear`: 123
- `constancy`: 116
- `derived_cp_closure`: 87
- `egg_bootstrap`: 74
- `universal_identity`: 55
- `absorption_context_bridge`: 29
- `rewrite`: 28
- `lemma_bootstrap`: 21
- `enum_fin3`: 15
- `lemma_chain`: 12
- `absorption_closure`: 8
- `tail_square_singleton`: 8
- `egg_closure`: 6
- `egg_ladder`: 6
- `alternating_front_self_collapse`: 6
- `forked_square_singleton`: 4
- `nested_square_singleton`: 4
- `bridge`: 4
- `front_double_self_collapse`: 4

## Failure clustering by hypothesis law

- eq1 `650`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 2, 4: 1}, 'eq1_ops': {4: 3}}

## Failure ledger

- `etp_650_1451` [skip, label=true, 418.96s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ y) ◇ (y ◇ (x ◇ x))`
- `etp_3983_357` [skip, label=true, 422.605s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = z ◇ (w ◇ w)`
- `etp_650_307` [skip, label=true, 417.971s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ x = x ◇ (x ◇ x)`
