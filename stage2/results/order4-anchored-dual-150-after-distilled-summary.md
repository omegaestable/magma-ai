# Sweep report: order4-anchored-dual-150-after-distilled

- rows: **150**
- solved: **135 (90.0%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **15**
- solver-claimed verdicts: {'true': 135}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 0, 0
- seconds: total 1266.2, mean 8.442, p50 2.73, p95 2.875, p99 2.901, slowest solved 2.947

## Route families

- `distilled`: 135

## Failure clustering by hypothesis law

- eq1 `2923`: 10 failures
- eq1 `650`: 5 failures

Failure shapes: {'eq1_bare_variable_side': 15, 'eq1_vars': {3: 15}, 'eq1_ops': {4: 15}}

## Failure ledger

- `etp_650_3050` [skip, label=true, 59.899s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (((x ◇ x) ◇ x) ◇ x) ◇ x`
- `etp_650_3080` [skip, label=true, 59.609s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (((x ◇ y) ◇ y) ◇ y) ◇ z`
- `etp_650_3083` [skip, label=true, 59.614s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (((x ◇ y) ◇ y) ◇ z) ◇ z`
- `etp_650_3934` [skip, label=true, 59.899s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = (x ◇ (z ◇ x)) ◇ x`
- `etp_650_4522` [skip, label=true, 59.984s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ (y ◇ z) = (x ◇ w) ◇ u`
- `etp_2923_347` [skip, label=true, 59.861s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = z ◇ (y ◇ y)`
- `etp_2923_411` [skip, label=true, 59.942s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = x ◇ (x ◇ (x ◇ (x ◇ x)))`
- `etp_2923_500` [skip, label=true, 59.556s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (y ◇ (x ◇ (x ◇ x)))`
- `etp_2923_537` [skip, label=true, 59.892s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (z ◇ (x ◇ (x ◇ x)))`
- `etp_2923_566` [skip, label=true, 59.657s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (z ◇ (y ◇ (w ◇ x)))`
- `etp_2923_3405` [skip, label=true, 59.86s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = z ◇ (y ◇ (z ◇ y))`
- `etp_2923_3824` [skip, label=true, 59.864s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = (z ◇ z) ◇ (y ◇ y)`
- `etp_2923_4334` [skip, label=true, 59.893s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ (y ◇ x) = z ◇ (w ◇ x)`
- `etp_2923_4435` [skip, label=true, 59.53s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ (y ◇ x) = (x ◇ y) ◇ x`
- `etp_2923_4525` [skip, label=true, 59.572s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ (y ◇ z) = (y ◇ x) ◇ z`
