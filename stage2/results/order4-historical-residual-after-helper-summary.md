# Sweep report: order4-historical-residual-after-helper

- rows: **652**
- solved: **326 (50.0%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **326**
- solver-claimed verdicts: {'true': 303, 'false': 23}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 0, 0
- seconds: total 19732.8, mean 30.265, p50 0.291, p95 2.315, p99 3.378, slowest solved 55.662

## Route families

- `completion`: 302
- `witness`: 13
- `distilled`: 10
- `egg_ladder`: 1

## Failure clustering by hypothesis law

- eq1 `650`: 76 failures
- eq1 `2923`: 74 failures
- eq1 `3983`: 38 failures
- eq1 `3565`: 29 failures
- eq1 `3577`: 25 failures
- eq1 `3967`: 15 failures
- eq1 `463`: 13 failures
- eq1 `3051`: 10 failures
- eq1 `3067`: 4 failures
- eq1 `481`: 3 failures
- eq1 `1979`: 3 failures
- eq1 `2531`: 3 failures
- eq1 `487`: 2 failures
- eq1 `3676`: 2 failures
- eq1 `4560`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 208, 'eq1_vars': {2: 33, 3: 227, 4: 66}, 'eq1_ops': {4: 326}}

## Failure ledger

- `etp_463_370` [skip, label=true, 60.006s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ x = (y ◇ z) ◇ x`
- `etp_463_491` [skip, label=true, 59.601s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x = y ◇ (x ◇ (z ◇ (z ◇ x)))`
- `etp_463_3877` [skip, label=true, 59.696s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ x = (y ◇ (x ◇ x)) ◇ x`
- `etp_463_3893` [skip, label=true, 60.006s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ x = (y ◇ (y ◇ z)) ◇ x`
- `etp_463_3905` [skip, label=true, 59.626s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ x = (y ◇ (z ◇ z)) ◇ x`
- `etp_463_3939` [skip, label=true, 59.573s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ y = (x ◇ (z ◇ y)) ◇ y`
- `etp_463_3947` [skip, label=true, 59.578s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ y = (x ◇ (z ◇ w)) ◇ y`
- `etp_463_4040` [skip, label=true, 60.003s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ y = (z ◇ (w ◇ x)) ◇ y`
- `etp_463_4070` [skip, label=true, 59.599s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ x = ((x ◇ y) ◇ x) ◇ x`
- `etp_463_4327` [skip, label=true, 59.463s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ (y ◇ x) = z ◇ (x ◇ x)`
- `etp_463_4360` [skip, label=true, 59.73s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `x ◇ (y ◇ z) = x ◇ (w ◇ z)`
- `etp_463_4587` [skip, label=true, 60.002s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `(x ◇ x) ◇ x = (y ◇ x) ◇ x`
- `etp_463_4625` [skip, label=true, 59.59s] eq1 `x = y ◇ (x ◇ (x ◇ (x ◇ x)))` => eq2 `(x ◇ x) ◇ y = (z ◇ w) ◇ y`
- `etp_469_583` [skip, label=true, 59.596s] eq1 `x = y ◇ (x ◇ (x ◇ (z ◇ x)))` => eq2 `x = y ◇ (z ◇ (z ◇ (w ◇ x)))`
- `etp_481_2132` [skip, label=false, 60.001s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = ((y ◇ y) ◇ x) ◇ (z ◇ z)`
- `etp_481_3050` [skip, label=false, 58.999s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = (((x ◇ x) ◇ x) ◇ x) ◇ x`
- `etp_481_3056` [skip, label=false, 58.931s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = (((x ◇ x) ◇ y) ◇ x) ◇ y`
- `etp_487_4001` [skip, label=true, 60.03s] eq1 `x = y ◇ (x ◇ (z ◇ (y ◇ x)))` => eq2 `x ◇ y = (z ◇ (x ◇ w)) ◇ y`
- `etp_487_4118` [skip, label=true, 59.212s] eq1 `x = y ◇ (x ◇ (z ◇ (y ◇ x)))` => eq2 `x ◇ y = ((x ◇ x) ◇ x) ◇ y`
- `etp_511_614` [skip, label=false, 59.211s] eq1 `x = y ◇ (y ◇ (y ◇ (x ◇ y)))` => eq2 `x = x ◇ (x ◇ ((x ◇ x) ◇ x))`
- `etp_650_4` [skip, label=true, 60.006s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ y`
- `etp_650_49` [skip, label=true, 59.207s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (x ◇ (y ◇ x))`
- `etp_650_163` [skip, label=true, 59.084s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ y) ◇ (z ◇ y)`
- `etp_650_211` [skip, label=true, 59.075s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ y)) ◇ x`
- `etp_650_213` [skip, label=true, 60.006s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ y)) ◇ z`
- `etp_650_216` [skip, label=true, 59.097s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ z)) ◇ z`
- `etp_650_268` [skip, label=true, 59.048s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ y) ◇ z) ◇ z`
- `etp_650_307` [skip, label=true, 59.043s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ x = x ◇ (x ◇ x)`
- `etp_650_322` [skip, label=true, 60.004s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = x ◇ (x ◇ x)`
- `etp_650_381` [skip, label=true, 59.113s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = (x ◇ z) ◇ y`
- `etp_650_418` [skip, label=true, 59.062s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (x ◇ (y ◇ (x ◇ z)))`
- `etp_650_423` [skip, label=true, 59.161s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (x ◇ (y ◇ (z ◇ y)))`
- `etp_650_448` [skip, label=true, 60.007s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (y ◇ (z ◇ (x ◇ z)))`
- `etp_650_457` [skip, label=true, 59.116s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (y ◇ (z ◇ (z ◇ w)))`
- `etp_650_624` [skip, label=true, 59.12s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (x ◇ ((y ◇ y) ◇ z))`
- `etp_650_645` [skip, label=true, 59.074s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (y ◇ ((y ◇ z) ◇ x))`
- `etp_650_660` [skip, label=true, 60.007s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (y ◇ ((z ◇ z) ◇ w))`
- `etp_650_828` [skip, label=true, 59.135s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ ((x ◇ y) ◇ (z ◇ x))`
- `etp_650_854` [skip, label=true, 59.084s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ ((y ◇ z) ◇ (x ◇ z))`
- `etp_650_855` [skip, label=true, 59.041s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ ((y ◇ z) ◇ (x ◇ w))`
- `etp_650_862` [skip, label=true, 60.008s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ ((y ◇ z) ◇ (z ◇ z))`
- `etp_650_1231` [skip, label=true, 59.117s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (((x ◇ y) ◇ y) ◇ x)`
- `etp_650_1248` [skip, label=true, 59.147s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (((y ◇ y) ◇ x) ◇ x)`
- `etp_650_1430` [skip, label=true, 59.121s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ x) ◇ (x ◇ (y ◇ z))`
- `etp_650_1451` [skip, label=true, 60.01s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ y) ◇ (y ◇ (x ◇ x))`
- `etp_650_1473` [skip, label=true, 59.136s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ y) ◇ (z ◇ (w ◇ x))`
- `etp_650_1632` [skip, label=true, 59.096s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ x) ◇ ((x ◇ y) ◇ y)`
- `etp_650_1636` [skip, label=true, 59.093s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ x) ◇ ((y ◇ x) ◇ z)`
- `etp_650_1641` [skip, label=true, 60.006s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ x) ◇ ((y ◇ z) ◇ y)`
- `etp_650_1670` [skip, label=true, 59.199s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ y) ◇ ((z ◇ y) ◇ z)`
- `etp_650_1832` [skip, label=true, 59.119s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (x ◇ x)) ◇ (x ◇ x)`
- `etp_650_1871` [skip, label=true, 59.074s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ z)) ◇ (y ◇ x)`
- `etp_650_2042` [skip, label=true, 60.006s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ x) ◇ y) ◇ (x ◇ z)`
- `etp_650_2078` [skip, label=true, 59.147s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ y) ◇ z) ◇ (z ◇ x)`
- `etp_650_2249` [skip, label=true, 59.145s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (x ◇ (y ◇ z))) ◇ x`
- `etp_650_2264` [skip, label=true, 59.088s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ (y ◇ x))) ◇ y`
- `etp_650_2268` [skip, label=true, 60.011s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ (y ◇ y))) ◇ z`
- `etp_650_2284` [skip, label=true, 59.147s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (y ◇ (z ◇ z))) ◇ w`
- `etp_650_2457` [skip, label=true, 59.104s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ x) ◇ x)) ◇ y`
- `etp_650_2464` [skip, label=true, 59.107s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ x) ◇ z)) ◇ z`
- `etp_650_2473` [skip, label=true, 58.97s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ y) ◇ z)) ◇ y`
- `etp_650_2477` [skip, label=true, 59.219s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ z) ◇ x)) ◇ y`
- `etp_650_2480` [skip, label=true, 59.283s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ z) ◇ y)) ◇ x`
- `etp_650_2481` [skip, label=true, 59.251s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ z) ◇ y)) ◇ y`
- `etp_650_2486` [skip, label=true, 59.609s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ z) ◇ z)) ◇ z`
- `etp_650_2667` [skip, label=true, 59.222s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ y) ◇ (x ◇ z)) ◇ z`
- `etp_650_2676` [skip, label=true, 59.409s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ y) ◇ (y ◇ z)) ◇ y`
- `etp_650_2692` [skip, label=true, 59.35s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ y) ◇ (z ◇ w)) ◇ y`
- `etp_650_2863` [skip, label=true, 60.025s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ (y ◇ x)) ◇ x) ◇ y`
- `etp_650_2870` [skip, label=true, 59.625s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ (y ◇ x)) ◇ z) ◇ z`
- `etp_650_2874` [skip, label=true, 59.679s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ (y ◇ y)) ◇ x) ◇ z`
- `etp_650_2878` [skip, label=true, 58.906s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ (y ◇ y)) ◇ z) ◇ x`
- `etp_650_2883` [skip, label=true, 59.995s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ (y ◇ z)) ◇ x) ◇ y`
- `etp_650_3050` [skip, label=true, 59.645s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (((x ◇ x) ◇ x) ◇ x) ◇ x`
- `etp_650_3080` [skip, label=true, 59.624s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (((x ◇ y) ◇ y) ◇ y) ◇ z`
- `etp_650_3083` [skip, label=true, 59.412s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (((x ◇ y) ◇ y) ◇ z) ◇ z`
- `etp_650_3307` [skip, label=true, 59.773s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = x ◇ (x ◇ (x ◇ z))`
- `etp_650_3311` [skip, label=true, 59.304s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = x ◇ (x ◇ (z ◇ x))`
- `etp_650_3514` [skip, label=true, 59.356s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = x ◇ ((x ◇ z) ◇ x)`
- `etp_650_3529` [skip, label=true, 59.32s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = x ◇ ((z ◇ x) ◇ y)`
- ... 246 more in the ledger jsonl
