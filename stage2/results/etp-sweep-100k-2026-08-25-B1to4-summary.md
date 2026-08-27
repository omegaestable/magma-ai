# Sweep report: etp-sweep-100k-2026-08-25-B1to4

- rows: **40000**
- solved: **39985 (99.963%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **15**
- solver-claimed verdicts: {'true': 19990, 'false': 19995}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 175, 211
- seconds: total 64368.1, mean 1.609, p50 0.005, p95 9.385, p99 10.926, slowest solved 261.129

## Route families

- `witness`: 18762
- `singleton`: 9383
- `egg_collapse`: 5083
- `completion`: 3059
- `spine`: 674
- `equational_closure`: 596
- `constancy`: 526
- `linear`: 444
- `derived_cp_closure`: 275
- `egg_bootstrap`: 253
- `universal_identity`: 149
- `rewrite`: 119
- `absorption_context_bridge`: 78
- `lemma_bootstrap`: 76
- `enum_fin3`: 72
- `lemma_chain`: 53
- `egg_ladder`: 50
- `absorption_closure`: 36
- `tail_square_singleton`: 27
- `egg_closure`: 25
- `deep_repeat_singleton`: 17
- `bridge`: 16
- `paired_tail_singleton`: 15
- `local_model4`: 13
- `left_projection_collapse`: 12

## Failure clustering by hypothesis law

- eq1 `3569`: 4 failures
- eq1 `2923`: 2 failures
- eq1 `650`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 8, 'eq1_vars': {3: 11, 4: 2, 2: 2}, 'eq1_ops': {4: 15}}

## Failure ledger

- `etp_3569_4296` [skip, label=true, 515.017s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ (x ◇ y) = y ◇ (z ◇ y)`
- `etp_3983_4296` [skip, label=true, 374.227s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ (x ◇ y) = y ◇ (z ◇ y)`
- `etp_3569_4688` [skip, label=true, 326.735s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `(x ◇ y) ◇ z = (z ◇ w) ◇ u`
- `etp_2162_3877` [skip, label=false, 319.518s] eq1 `x = ((y ◇ z) ◇ x) ◇ (x ◇ y)` => eq2 `x ◇ x = (y ◇ (x ◇ x)) ◇ x`
- `etp_3051_3054` [skip, label=true, 316.556s] eq1 `x = (((x ◇ x) ◇ x) ◇ x) ◇ y` => eq2 `x = (((x ◇ x) ◇ x) ◇ y) ◇ z`
- `etp_3569_4201` [skip, label=true, 516.372s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = ((z ◇ x) ◇ z) ◇ z`
- `etp_2923_3947` [skip, label=true, 504.753s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = (x ◇ (z ◇ w)) ◇ y`
- `etp_4453_4652` [skip, label=true, 448.565s] eq1 `x ◇ (y ◇ x) = (z ◇ x) ◇ y` => eq2 `(x ◇ y) ◇ x = (z ◇ w) ◇ w`
- `etp_3569_4267` [skip, label=true, 263.592s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = ((z ◇ w) ◇ u) ◇ v`
- `etp_650_4065` [skip, label=true, 372.885s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ x = ((x ◇ x) ◇ x) ◇ x`
- `etp_2531_23` [skip, label=false, 348.232s] eq1 `x = (y ◇ ((y ◇ x) ◇ x)) ◇ y` => eq2 `x = (x ◇ x) ◇ x`
- `etp_650_3050` [skip, label=true, 332.721s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (((x ◇ x) ◇ x) ◇ x) ◇ x`
- `etp_3577_3746` [skip, label=true, 415.007s] eq1 `x ◇ y = y ◇ ((z ◇ w) ◇ x)` => eq2 `x ◇ y = (x ◇ z) ◇ (w ◇ w)`
- `etp_898_4270` [skip, label=false, 289.74s] eq1 `x = y ◇ ((x ◇ z) ◇ (z ◇ y))` => eq2 `x ◇ (x ◇ x) = x ◇ (y ◇ y)`
- `etp_2923_1115` [skip, label=true, 433.248s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ ((y ◇ (x ◇ z)) ◇ x)`
