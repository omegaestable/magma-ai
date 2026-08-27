# Sweep report: etp-sweep-200k-2026-08-27-b02

- rows: **10000**
- solved: **9993 (99.93%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **7**
- solver-claimed verdicts: {'false': 4944, 'true': 5049}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 51, 58
- seconds: total 18387.5, mean 1.839, p50 0.006, p95 9.522, p99 11.669, slowest solved 230.254

## Route families

- `witness`: 4629
- `singleton`: 2377
- `egg_collapse`: 1192
- `completion`: 824
- `spine`: 169
- `equational_closure`: 143
- `constancy`: 131
- `linear`: 112
- `derived_cp_closure`: 74
- `egg_bootstrap`: 64
- `universal_identity`: 45
- `rewrite`: 39
- `absorption_context_bridge`: 28
- `lemma_bootstrap`: 27
- `lemma_chain`: 26
- `enum_fin3`: 18
- `egg_ladder`: 9
- `absorption_closure`: 8
- `alternating_front_self_collapse`: 6
- `crossed_pair_singleton`: 6
- `middle_self_collapse`: 6
- `constraint_fin8`: 5
- `deep_repeat_singleton`: 4
- `paired_tail_singleton`: 4
- `local_model4`: 4

## Failure clustering by hypothesis law

- eq1 `2923`: 3 failures

Failure shapes: {'eq1_bare_variable_side': 6, 'eq1_vars': {3: 6, 2: 1}, 'eq1_ops': {4: 7}}

## Failure ledger

- `etp_2923_364` [skip, label=true, 461.107s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ x = (y ◇ x) ◇ x`
- `etp_650_2464` [skip, label=true, 440.294s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ x) ◇ z)) ◇ z`
- `etp_476_4065` [skip, label=false, 335.418s] eq1 `x = y ◇ (x ◇ (y ◇ (y ◇ x)))` => eq2 `x ◇ x = ((x ◇ x) ◇ x) ◇ x`
- `etp_4541_4605` [skip, label=false, 402.543s] eq1 `x ◇ (y ◇ z) = (z ◇ x) ◇ y` => eq2 `(x ◇ x) ◇ y = (y ◇ x) ◇ x`
- `etp_2923_4635` [skip, label=true, 461.003s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `(x ◇ y) ◇ x = (y ◇ x) ◇ x`
- `etp_2923_537` [skip, label=true, 379.825s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (z ◇ (x ◇ (x ◇ x)))`
- `etp_2702_2281` [skip, label=false, 377.503s] eq1 `x = ((y ◇ x) ◇ (x ◇ z)) ◇ x` => eq2 `x = (x ◇ (y ◇ (z ◇ z))) ◇ x`
