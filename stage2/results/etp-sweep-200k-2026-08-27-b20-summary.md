# Sweep report: etp-sweep-200k-2026-08-27-b20

- rows: **10000**
- solved: **9991 (99.91%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **9**
- solver-claimed verdicts: {'true': 4927, 'false': 5064}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 49, 57
- seconds: total 17674.1, mean 1.767, p50 0.004, p95 9.298, p99 10.255, slowest solved 275.915

## Route families

- `witness`: 4757
- `singleton`: 2287
- `egg_collapse`: 1289
- `completion`: 714
- `spine`: 171
- `equational_closure`: 156
- `constancy`: 118
- `linear`: 107
- `derived_cp_closure`: 76
- `egg_bootstrap`: 75
- `universal_identity`: 37
- `rewrite`: 32
- `absorption_context_bridge`: 25
- `lemma_bootstrap`: 19
- `lemma_chain`: 17
- `enum_fin3`: 13
- `absorption_closure`: 9
- `egg_ladder`: 9
- `mirrored_alternating_front_self_collapse`: 7
- `constraint_fin8`: 7
- `crossed_pair_singleton`: 7
- `nested_square_singleton`: 5
- `forked_square_singleton`: 5
- `dual`: 4
- `front_double_self_collapse`: 3

## Failure clustering by hypothesis law

- eq1 `3569`: 3 failures
- eq1 `3983`: 3 failures

Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {3: 6, 4: 3}, 'eq1_ops': {4: 9}}

## Failure ledger

- `etp_3569_3933` [skip, label=true, 446.798s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = (x ◇ (y ◇ z)) ◇ w`
- `etp_650_3934` [skip, label=true, 332.691s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = (x ◇ (z ◇ x)) ◇ x`
- `etp_3569_4218` [skip, label=true, 510.026s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = ((z ◇ y) ◇ z) ◇ z`
- `etp_3983_3859` [skip, label=true, 294.124s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (z ◇ w) ◇ (u ◇ w)`
- `etp_3569_3775` [skip, label=true, 447.618s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = (y ◇ z) ◇ (y ◇ w)`
- `etp_3983_4338` [skip, label=true, 302.314s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ (y ◇ x) = z ◇ (w ◇ u)`
- `etp_2923_3769` [skip, label=true, 433.19s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = (y ◇ z) ◇ (x ◇ y)`
- `etp_3983_4409` [skip, label=true, 328.599s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ (x ◇ y) = (y ◇ y) ◇ y`
- `etp_1133_1912` [skip, label=false, 321.405s] eq1 `x = y ◇ ((y ◇ (z ◇ y)) ◇ x)` => eq2 `x = (y ◇ (x ◇ z)) ◇ (z ◇ x)`
