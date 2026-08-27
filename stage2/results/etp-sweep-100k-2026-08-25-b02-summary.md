# Sweep report: etp-sweep-100k-2026-08-25-b02

- rows: **10000**
- solved: **9997 (99.97%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **3**
- solver-claimed verdicts: {'false': 4989, 'true': 5008}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 47, 58
- seconds: total 15049.4, mean 1.505, p50 0.005, p95 9.375, p99 10.225, slowest solved 228.902

## Route families

- `witness`: 4658
- `singleton`: 2362
- `egg_collapse`: 1288
- `completion`: 740
- `spine`: 181
- `equational_closure`: 134
- `constancy`: 127
- `linear`: 121
- `derived_cp_closure`: 77
- `egg_bootstrap`: 67
- `universal_identity`: 38
- `rewrite`: 24
- `lemma_bootstrap`: 23
- `absorption_context_bridge`: 20
- `enum_fin3`: 19
- `lemma_chain`: 19
- `absorption_closure`: 12
- `egg_ladder`: 9
- `dual`: 6
- `egg_closure`: 5
- `forked_square_singleton`: 5
- `deep_repeat_singleton`: 5
- `tail_square_singleton`: 5
- `paired_tail_singleton`: 5
- `nested_square_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {2: 1, 3: 2}, 'eq1_ops': {4: 3}}

## Failure ledger

- `etp_3051_3054` [skip, label=true, 316.556s] eq1 `x = (((x ◇ x) ◇ x) ◇ x) ◇ y` => eq2 `x = (((x ◇ x) ◇ x) ◇ y) ◇ z`
- `etp_3569_4201` [skip, label=true, 516.372s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = ((z ◇ x) ◇ z) ◇ z`
- `etp_2923_3947` [skip, label=true, 504.753s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = (x ◇ (z ◇ w)) ◇ y`
