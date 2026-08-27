# Sweep report: order4-2026-08-25-ALL

- rows: **110000**
- solved: **109954 (99.958%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **46**
- solver-claimed verdicts: {'true': 54960, 'false': 54994}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 501, 588
- seconds: total 176576.0, mean 1.605, p50 0.005, p95 9.369, p99 10.523, slowest solved 354.707

## Route families

- `witness`: 51557
- `singleton`: 25693
- `egg_collapse`: 14047
- `completion`: 8317
- `spine`: 1859
- `equational_closure`: 1671
- `constancy`: 1382
- `linear`: 1235
- `derived_cp_closure`: 810
- `egg_bootstrap`: 733
- `universal_identity`: 450
- `rewrite`: 334
- `absorption_context_bridge`: 250
- `lemma_bootstrap`: 212
- `enum_fin3`: 209
- `lemma_chain`: 183
- `egg_ladder`: 107
- `absorption_closure`: 93
- `tail_square_singleton`: 78
- `egg_closure`: 52
- `deep_repeat_singleton`: 40
- `paired_tail_singleton`: 37
- `constraint_fin8`: 33
- `crossed_pair_singleton`: 32
- `bridge`: 32

## Failure clustering by hypothesis law

- eq1 `2923`: 16 failures
- eq1 `3569`: 7 failures
- eq1 `650`: 5 failures
- eq1 `3983`: 4 failures
- eq1 `481`: 2 failures
- eq1 `3051`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 33, 'eq1_vars': {3: 38, 4: 5, 2: 3}, 'eq1_ops': {4: 46}}

## Failure ledger

- `etp_2923_156` [skip, label=true, 420.579s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = (x ◇ y) ◇ (x ◇ x)`
- `etp_481_3050` [skip, label=false, 263.822s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = (((x ◇ x) ◇ x) ◇ x) ◇ x`
- `etp_3569_4143` [skip, label=true, 520.547s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = ((x ◇ z) ◇ y) ◇ z`
- `etp_2854_4676` [skip, label=true, 289.17s] eq1 `x = ((x ◇ (x ◇ y)) ◇ x) ◇ z` => eq2 `(x ◇ y) ◇ z = (x ◇ w) ◇ u`
- `etp_2923_3397` [skip, label=true, 441.426s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = z ◇ (y ◇ (x ◇ y))`
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
- `etp_650_3721` [skip, label=true, 408.362s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = (x ◇ y) ◇ (x ◇ x)`
- `etp_2923_3664` [skip, label=true, 411.346s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ x = (x ◇ y) ◇ (x ◇ x)`
- `etp_3983_3800` [skip, label=true, 401.29s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (z ◇ x) ◇ (w ◇ w)`
- `etp_2923_4334` [skip, label=true, 411.804s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ (y ◇ x) = z ◇ (w ◇ x)`
- `etp_3569_4370` [skip, label=true, 449.014s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ (y ◇ z) = z ◇ (y ◇ w)`
- `etp_3569_3370` [skip, label=true, 511.071s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = y ◇ (z ◇ (z ◇ x))`
- `etp_1366_3965` [skip, label=true, 410.546s] eq1 `x = y ◇ (((z ◇ y) ◇ x) ◇ x)` => eq2 `x ◇ y = (y ◇ (y ◇ y)) ◇ y`
- `etp_3051_4676` [skip, label=true, 205.458s] eq1 `x = (((x ◇ x) ◇ x) ◇ x) ◇ y` => eq2 `(x ◇ y) ◇ z = (x ◇ w) ◇ u`
- `etp_2923_4150` [skip, label=true, 502.413s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = ((x ◇ z) ◇ w) ◇ y`
- `etp_2923_72` [skip, label=true, 372.465s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (y ◇ (x ◇ x))`
- `etp_3983_3963` [skip, label=true, 366.171s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (y ◇ (y ◇ x)) ◇ z`
- `etp_2923_3993` [skip, label=true, 465.754s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = (z ◇ (x ◇ y)) ◇ y`
- `etp_1789_3371` [skip, label=true, 310.756s] eq1 `x = (y ◇ z) ◇ ((z ◇ x) ◇ x)` => eq2 `x ◇ y = y ◇ (z ◇ (z ◇ y))`
- `etp_2316_4656` [skip, label=false, 303.442s] eq1 `x = (y ◇ (x ◇ (z ◇ y))) ◇ z` => eq2 `(x ◇ y) ◇ y = (x ◇ z) ◇ z`
- `etp_2923_2782` [skip, label=true, 461.205s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((y ◇ z) ◇ (x ◇ w)) ◇ x`
- `etp_2923_1075` [skip, label=true, 403.511s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ ((x ◇ (x ◇ y)) ◇ x)`
- `etp_2923_769` [skip, label=true, 399.541s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (z ◇ ((y ◇ w) ◇ x))`
- `etp_2923_2137` [skip, label=true, 411.559s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((y ◇ y) ◇ y) ◇ (y ◇ x)`
- `etp_650_381` [skip, label=true, 381.332s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = (x ◇ z) ◇ y`
- `etp_481_2132` [skip, label=false, 304.682s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = ((y ◇ y) ◇ x) ◇ (z ◇ z)`
- `etp_650_2284` [skip, label=true, 459.84s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ (z ◇ z))) ◇ w`
- `etp_2923_3405` [skip, label=true, 304.568s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = z ◇ (y ◇ (z ◇ y))`
- `etp_3983_3997` [skip, label=true, 397.924s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (z ◇ (x ◇ z)) ◇ y`
- `etp_2923_2683` [skip, label=true, 434.55s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((x ◇ y) ◇ (z ◇ y)) ◇ x`
- `etp_469_583` [skip, label=true, 383.334s] eq1 `x = y ◇ (x ◇ (x ◇ (z ◇ x)))` => eq2 `x = y ◇ (z ◇ (z ◇ (w ◇ x)))`
- `etp_2923_1415` [skip, label=true, 464.814s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (((z ◇ w) ◇ w) ◇ x)`
