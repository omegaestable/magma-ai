# Sweep report: etp-sweep-200k-2026-08-26-b11

- rows: **10000**
- solved: **9994 (99.94%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **6**
- solver-claimed verdicts: {'true': 4979, 'false': 5015}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 49, 51
- seconds: total 17654.6, mean 1.765, p50 0.004, p95 9.485, p99 11.301, slowest solved 303.515

## Route families

- `witness`: 4706
- `singleton`: 2331
- `egg_collapse`: 1236
- `completion`: 816
- `spine`: 170
- `equational_closure`: 157
- `constancy`: 121
- `linear`: 102
- `derived_cp_closure`: 65
- `egg_bootstrap`: 51
- `universal_identity`: 41
- `enum_fin3`: 28
- `absorption_context_bridge`: 24
- `rewrite`: 23
- `lemma_bootstrap`: 23
- `lemma_chain`: 15
- `tail_square_singleton`: 10
- `egg_ladder`: 10
- `absorption_closure`: 8
- `nested_square_singleton`: 5
- `reverse_deep_repeat_singleton`: 5
- `paired_tail_singleton`: 4
- `outer_sandwich_singleton`: 4
- `constraint_fin8`: 4
- `egg_closure`: 4

## Failure clustering by hypothesis law

- eq1 `3569`: 3 failures

Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 5, 4: 1}, 'eq1_ops': {4: 6}}

## Failure ledger

- `etp_3067_4319` [skip, label=true, 443.896s] eq1 `x = (((x ◇ y) ◇ x) ◇ x) ◇ z` => eq2 `x ◇ (y ◇ x) = x ◇ (z ◇ w)`
- `etp_3569_4458` [skip, label=true, 525.548s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ (y ◇ x) = (z ◇ y) ◇ z`
- `etp_2126_2162` [skip, label=false, 438.383s] eq1 `x = ((y ◇ y) ◇ x) ◇ (x ◇ z)` => eq2 `x = ((y ◇ z) ◇ x) ◇ (x ◇ y)`
- `etp_3569_3574` [skip, label=true, 523.903s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = y ◇ ((z ◇ z) ◇ y)`
- `etp_3569_4113` [skip, label=true, 452.561s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ x = ((y ◇ z) ◇ w) ◇ y`
- `etp_3983_4483` [skip, label=true, 341.977s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ (y ◇ y) = (y ◇ y) ◇ y`
