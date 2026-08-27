# Sweep report: etp-sweep-200k-2026-08-27-b16

- rows: **10000**
- solved: **9999 (99.99%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **1**
- solver-claimed verdicts: {'true': 5015, 'false': 4984}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 49, 60
- seconds: total 13566.9, mean 1.357, p50 0.004, p95 9.353, p99 9.884, slowest solved 137.232

## Route families

- `witness`: 4715
- `singleton`: 2394
- `egg_collapse`: 1251
- `completion`: 773
- `equational_closure`: 172
- `spine`: 135
- `constancy`: 110
- `linear`: 109
- `derived_cp_closure`: 62
- `egg_bootstrap`: 54
- `universal_identity`: 40
- `rewrite`: 27
- `absorption_context_bridge`: 27
- `lemma_bootstrap`: 19
- `enum_fin3`: 17
- `lemma_chain`: 10
- `absorption_closure`: 9
- `tail_square_singleton`: 7
- `deep_repeat_singleton`: 6
- `crossed_pair_singleton`: 5
- `left_projection_collapse`: 4
- `right_projection_collapse`: 4
- `paired_tail_singleton`: 4
- `middle_self_collapse`: 4
- `alternating_front_self_collapse`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 0, 'eq1_vars': {4: 1}, 'eq1_ops': {4: 1}}

## Failure ledger

- `etp_3983_4563` [skip, label=true, 410.12s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ (y ◇ z) = (w ◇ y) ◇ y`
