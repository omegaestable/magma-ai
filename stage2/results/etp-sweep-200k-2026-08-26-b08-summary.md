# Sweep report: etp-sweep-200k-2026-08-26-b08

- rows: **10000**
- solved: **9994 (99.94%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **6**
- solver-claimed verdicts: {'true': 5043, 'false': 4951}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 42, 51
- seconds: total 16941.0, mean 1.694, p50 0.004, p95 9.363, p99 9.964, slowest solved 230.39

## Route families

- `witness`: 4644
- `singleton`: 2355
- `egg_collapse`: 1261
- `completion`: 795
- `spine`: 163
- `constancy`: 157
- `equational_closure`: 145
- `linear`: 109
- `derived_cp_closure`: 72
- `egg_bootstrap`: 58
- `universal_identity`: 36
- `rewrite`: 28
- `absorption_context_bridge`: 26
- `lemma_bootstrap`: 24
- `enum_fin3`: 22
- `lemma_chain`: 14
- `absorption_closure`: 9
- `wrapped_tail_singleton`: 7
- `egg_ladder`: 6
- `mirrored_alternating_front_self_collapse`: 5
- `left_projection_collapse`: 5
- `right_projection_collapse`: 4
- `constraint_fin8`: 4
- `forked_square_singleton`: 3
- `bridge`: 3

## Failure clustering by hypothesis law

- eq1 `3983`: 2 failures
- eq1 `2923`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 4, 'eq1_vars': {2: 1, 4: 2, 3: 3}, 'eq1_ops': {4: 6}}

## Failure ledger

- `etp_463_370` [skip, label=true, 322.567s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ x = (y ◇ z) ◇ x`
- `etp_3983_4113` [skip, label=true, 419.669s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ x = ((y ◇ z) ◇ w) ◇ y`
- `etp_650_4121` [skip, label=true, 370.74s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = ((x ◇ x) ◇ y) ◇ y`
- `etp_2923_4689` [skip, label=true, 502.28s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `(x ◇ y) ◇ z = (w ◇ y) ◇ z`
- `etp_3983_3986` [skip, label=true, 399.216s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (y ◇ (z ◇ w)) ◇ w`
- `etp_2923_4435` [skip, label=true, 284.307s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ (y ◇ x) = (x ◇ y) ◇ x`
