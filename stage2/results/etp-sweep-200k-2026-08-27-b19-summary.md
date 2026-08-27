# Sweep report: etp-sweep-200k-2026-08-27-b19

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'false': 5049, 'true': 4947}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 36, 44
- seconds: total 15828.6, mean 1.583, p50 0.004, p95 9.351, p99 9.888, slowest solved 216.103

## Route families

- `witness`: 4726
- `singleton`: 2293
- `egg_collapse`: 1263
- `completion`: 769
- `spine`: 193
- `equational_closure`: 158
- `constancy`: 121
- `linear`: 106
- `derived_cp_closure`: 73
- `egg_bootstrap`: 66
- `rewrite`: 41
- `universal_identity`: 35
- `absorption_context_bridge`: 26
- `lemma_bootstrap`: 24
- `lemma_chain`: 16
- `enum_fin3`: 14
- `absorption_closure`: 8
- `egg_ladder`: 8
- `deep_repeat_singleton`: 5
- `middle_self_collapse`: 4
- `right_projection_collapse`: 4
- `sandwich_repeat_singleton`: 3
- `tail_square_singleton`: 3
- `reverse_deep_repeat_singleton`: 3
- `mirrored_alternating_front_self_collapse`: 3

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {4: 1, 3: 3}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_3983_4250` [skip, label=true, 410.1s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = ((z ◇ w) ◇ y) ◇ w`
- `etp_650_3737` [skip, label=true, 393.276s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = (x ◇ z) ◇ (y ◇ z)`
- `etp_3569_3406` [skip, label=true, 501.871s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = z ◇ (y ◇ (z ◇ z))`
- `etp_2923_791` [skip, label=true, 400.1s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (z ◇ ((w ◇ x) ◇ x))`
