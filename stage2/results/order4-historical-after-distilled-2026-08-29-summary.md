# Sweep report: order4-historical-after-distilled-2026-08-29

- rows: **652**
- solved: **611 (93.712%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **41**
- solver-claimed verdicts: {'true': 588, 'false': 23}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 0, 0
- seconds: total 3184.4, mean 4.884, p50 0.547, p95 3.792, p99 4.252, slowest solved 5.084

## Route families

- `distilled`: 303
- `completion`: 295
- `witness`: 13

## Failure clustering by hypothesis law

- eq1 `481`: 3 failures
- eq1 `1979`: 3 failures
- eq1 `2531`: 3 failures
- eq1 `3567`: 2 failures
- eq1 `3676`: 2 failures
- eq1 `4560`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 29, 'eq1_vars': {3: 28, 2: 10, 4: 3}, 'eq1_ops': {4: 41}}

## Failure ledger

- `etp_481_2132` [skip, label=false, 60.169s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = ((y ◇ y) ◇ x) ◇ (z ◇ z)`
- `etp_481_3050` [skip, label=false, 60.014s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = (((x ◇ x) ◇ x) ◇ x) ◇ x`
- `etp_481_3056` [skip, label=false, 59.898s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = (((x ◇ x) ◇ y) ◇ x) ◇ y`
- `etp_511_614` [skip, label=false, 60.002s] eq1 `x = y ◇ (y ◇ (y ◇ (x ◇ y)))` => eq2 `x = x ◇ (x ◇ ((x ◇ x) ◇ x))`
- `etp_707_2238` [skip, label=false, 60.077s] eq1 `x = y ◇ (y ◇ ((x ◇ y) ◇ y))` => eq2 `x = (x ◇ (x ◇ (x ◇ x))) ◇ x`
- `etp_765_4622` [skip, label=true, 60.05s] eq1 `x = y ◇ (z ◇ ((y ◇ z) ◇ x))` => eq2 `(x ◇ x) ◇ y = (z ◇ z) ◇ y`
- `etp_827_618` [skip, label=false, 59.695s] eq1 `x = x ◇ ((x ◇ y) ◇ (y ◇ z))` => eq2 `x = x ◇ (x ◇ ((x ◇ y) ◇ z))`
- `etp_1133_1668` [skip, label=false, 60.017s] eq1 `x = y ◇ ((y ◇ (z ◇ y)) ◇ x)` => eq2 `x = (x ◇ y) ◇ ((z ◇ y) ◇ x)`
- `etp_1235_1227` [skip, label=false, 60.289s] eq1 `x = x ◇ (((x ◇ y) ◇ z) ◇ y)` => eq2 `x = x ◇ (((x ◇ x) ◇ y) ◇ z)`
- `etp_1276_4332` [skip, label=false, 59.125s] eq1 `x = y ◇ (((x ◇ x) ◇ x) ◇ y)` => eq2 `x ◇ (y ◇ x) = z ◇ (y ◇ z)`
- `etp_1486_2124` [skip, label=false, 60.065s] eq1 `x = (y ◇ x) ◇ (x ◇ (z ◇ z))` => eq2 `x = ((y ◇ y) ◇ x) ◇ (x ◇ x)`
- `etp_1661_3524` [skip, label=false, 60.042s] eq1 `x = (x ◇ y) ◇ ((y ◇ z) ◇ y)` => eq2 `x ◇ y = x ◇ ((y ◇ z) ◇ x)`
- `etp_1740_1113` [skip, label=true, 60.192s] eq1 `x = (y ◇ y) ◇ ((z ◇ x) ◇ z)` => eq2 `x = y ◇ ((y ◇ (x ◇ y)) ◇ y)`
- `etp_1979_1721` [skip, label=false, 60.032s] eq1 `x = (y ◇ (z ◇ y)) ◇ (y ◇ x)` => eq2 `x = (y ◇ y) ◇ ((x ◇ y) ◇ x)`
- `etp_1979_2024` [skip, label=false, 59.998s] eq1 `x = (y ◇ (z ◇ y)) ◇ (y ◇ x)` => eq2 `x = (y ◇ (z ◇ w)) ◇ (w ◇ x)`
- `etp_1979_3952` [skip, label=false, 59.257s] eq1 `x = (y ◇ (z ◇ y)) ◇ (y ◇ x)` => eq2 `x ◇ y = (y ◇ (x ◇ x)) ◇ y`
- `etp_2000_1112` [skip, label=false, 59.529s] eq1 `x = (y ◇ (z ◇ z)) ◇ (z ◇ x)` => eq2 `x = y ◇ ((y ◇ (x ◇ y)) ◇ x)`
- `etp_2066_4599` [skip, label=false, 60.128s] eq1 `x = ((x ◇ y) ◇ y) ◇ (z ◇ x)` => eq2 `(x ◇ x) ◇ y = (x ◇ y) ◇ y`
- `etp_2308_4094` [skip, label=true, 60.174s] eq1 `x = (y ◇ (x ◇ (y ◇ z))) ◇ z` => eq2 `x ◇ x = ((y ◇ y) ◇ y) ◇ y`
- `etp_2381_1958` [skip, label=false, 60.895s] eq1 `x = (y ◇ (z ◇ (y ◇ x))) ◇ x` => eq2 `x = (y ◇ (z ◇ x)) ◇ (x ◇ x)`
- `etp_2473_2460` [skip, label=false, 60.031s] eq1 `x = (x ◇ ((y ◇ y) ◇ z)) ◇ y` => eq2 `x = (x ◇ ((y ◇ x) ◇ y)) ◇ y`
- `etp_2531_23` [skip, label=false, 59.549s] eq1 `x = (y ◇ ((y ◇ x) ◇ x)) ◇ y` => eq2 `x = (x ◇ x) ◇ x`
- `etp_2531_99` [skip, label=false, 59.649s] eq1 `x = (y ◇ ((y ◇ x) ◇ x)) ◇ y` => eq2 `x = x ◇ ((x ◇ x) ◇ x)`
- `etp_2531_1832` [skip, label=false, 59.754s] eq1 `x = (y ◇ ((y ◇ x) ◇ x)) ◇ y` => eq2 `x = (x ◇ (x ◇ x)) ◇ (x ◇ x)`
- `etp_2712_2266` [skip, label=false, 60.18s] eq1 `x = ((y ◇ x) ◇ (y ◇ z)) ◇ x` => eq2 `x = (x ◇ (y ◇ (y ◇ y))) ◇ x`
- `etp_2744_1526` [skip, label=false, 59.998s] eq1 `x = ((y ◇ y) ◇ (y ◇ x)) ◇ y` => eq2 `x = (y ◇ y) ◇ (y ◇ (x ◇ y))`
- `etp_2789_3297` [skip, label=true, 60.07s] eq1 `x = ((y ◇ z) ◇ (y ◇ x)) ◇ z` => eq2 `x ◇ x = y ◇ (z ◇ (z ◇ y))`
- `etp_2850_4585` [skip, label=true, 59.999s] eq1 `x = ((x ◇ (x ◇ x)) ◇ y) ◇ y` => eq2 `(x ◇ x) ◇ x = (x ◇ y) ◇ y`
- `etp_2856_2644` [skip, label=false, 60.168s] eq1 `x = ((x ◇ (x ◇ y)) ◇ y) ◇ y` => eq2 `x = ((x ◇ x) ◇ (x ◇ x)) ◇ x`
- `etp_3342_3862` [skip, label=false, 60.043s] eq1 `x ◇ y = y ◇ (x ◇ (x ◇ x))` => eq2 `x ◇ x = (x ◇ (x ◇ x)) ◇ x`
- `etp_3567_4013` [skip, label=true, 60.175s] eq1 `x ◇ y = y ◇ ((z ◇ x) ◇ z)` => eq2 `x ◇ y = (z ◇ (y ◇ z)) ◇ x`
- `etp_3567_4026` [skip, label=true, 59.811s] eq1 `x ◇ y = y ◇ ((z ◇ x) ◇ z)` => eq2 `x ◇ y = (z ◇ (z ◇ y)) ◇ x`
- `etp_3676_40` [skip, label=true, 60.061s] eq1 `x ◇ x = (y ◇ x) ◇ (x ◇ z)` => eq2 `x ◇ x = y ◇ y`
- `etp_3676_3705` [skip, label=true, 59.452s] eq1 `x ◇ x = (y ◇ x) ◇ (x ◇ z)` => eq2 `x ◇ x = (y ◇ z) ◇ (z ◇ w)`
- `etp_3698_3694` [skip, label=false, 58.51s] eq1 `x ◇ x = (y ◇ z) ◇ (y ◇ x)` => eq2 `x ◇ x = (y ◇ z) ◇ (x ◇ x)`
- `etp_4453_4652` [skip, label=true, 60.654s] eq1 `x ◇ (y ◇ x) = (z ◇ x) ◇ y` => eq2 `(x ◇ y) ◇ x = (z ◇ w) ◇ w`
- `etp_4457_4393` [skip, label=true, 59.797s] eq1 `x ◇ (y ◇ x) = (z ◇ y) ◇ y` => eq2 `x ◇ (x ◇ x) = (y ◇ z) ◇ z`
- `etp_4465_4468` [skip, label=true, 59.714s] eq1 `x ◇ (y ◇ x) = (z ◇ w) ◇ y` => eq2 `x ◇ (y ◇ x) = (z ◇ w) ◇ u`
- `etp_4524_4379` [skip, label=true, 60.529s] eq1 `x ◇ (y ◇ z) = (y ◇ x) ◇ y` => eq2 `x ◇ (y ◇ z) = w ◇ (u ◇ v)`
- `etp_4560_4373` [skip, label=true, 60.28s] eq1 `x ◇ (y ◇ z) = (w ◇ x) ◇ w` => eq2 `x ◇ (y ◇ z) = z ◇ (w ◇ u)`
- `etp_4560_4375` [skip, label=true, 60.039s] eq1 `x ◇ (y ◇ z) = (w ◇ x) ◇ w` => eq2 `x ◇ (y ◇ z) = w ◇ (y ◇ u)`
