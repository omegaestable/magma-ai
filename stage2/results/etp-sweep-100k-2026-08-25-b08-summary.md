# Sweep report: etp-sweep-100k-2026-08-25-b08

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'true': 5020, 'false': 4976}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 51, 58
- seconds: total 15321.1, mean 1.532, p50 0.004, p95 9.333, p99 10.309, slowest solved 133.772

## Route families

- `witness`: 4666
- `singleton`: 2310
- `egg_collapse`: 1302
- `completion`: 743
- `spine`: 168
- `equational_closure`: 156
- `constancy`: 143
- `linear`: 104
- `derived_cp_closure`: 82
- `egg_bootstrap`: 61
- `universal_identity`: 47
- `rewrite`: 34
- `absorption_context_bridge`: 26
- `enum_fin3`: 21
- `lemma_chain`: 21
- `lemma_bootstrap`: 20
- `wrapped_tail_singleton`: 8
- `dual`: 7
- `egg_ladder`: 7
- `tail_square_singleton`: 6
- `sandwich_repeat_singleton`: 6
- `forked_square_singleton`: 6
- `constraint_fin8`: 5
- `egg_closure`: 4
- `bridge`: 3

## Failure clustering by hypothesis law

- eq1 `2923`: 3 failures

Failure shapes: {'eq1_bare_variable_side': 4, 'eq1_vars': {3: 4}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_2316_4656` [skip, label=false, 303.442s] eq1 `x = (y ◇ (x ◇ (z ◇ y))) ◇ z` => eq2 `(x ◇ y) ◇ y = (x ◇ z) ◇ z`
- `etp_2923_2782` [skip, label=true, 461.205s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((y ◇ z) ◇ (x ◇ w)) ◇ x`
- `etp_2923_1075` [skip, label=true, 403.511s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ ((x ◇ (x ◇ y)) ◇ x)`
- `etp_2923_769` [skip, label=true, 399.541s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (z ◇ ((y ◇ w) ◇ x))`
