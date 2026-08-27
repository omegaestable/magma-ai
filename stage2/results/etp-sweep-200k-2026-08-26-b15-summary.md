# Sweep report: etp-sweep-200k-2026-08-26-b15

- rows: **10000**
- solved: **9999 (99.99%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **1**
- solver-claimed verdicts: {'false': 4973, 'true': 5026}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 41, 50
- seconds: total 15162.9, mean 1.516, p50 0.005, p95 9.42, p99 10.054, slowest solved 214.476

## Route families

- `witness`: 4643
- `singleton`: 2366
- `egg_collapse`: 1232
- `completion`: 772
- `equational_closure`: 167
- `spine`: 167
- `linear`: 130
- `constancy`: 128
- `derived_cp_closure`: 97
- `egg_bootstrap`: 65
- `universal_identity`: 38
- `absorption_context_bridge`: 32
- `rewrite`: 24
- `enum_fin3`: 19
- `lemma_chain`: 15
- `lemma_bootstrap`: 14
- `egg_ladder`: 8
- `absorption_closure`: 8
- `egg_closure`: 5
- `middle_self_collapse`: 4
- `bridge`: 4
- `alternating_front_self_collapse`: 4
- `paired_tail_singleton`: 4
- `constraint_fin8`: 3
- `dual`: 3

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 1, 'eq1_vars': {3: 1}, 'eq1_ops': {4: 1}}

## Failure ledger

- `etp_2923_3893` [skip, label=true, 472.918s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ x = (y ◇ (y ◇ z)) ◇ x`
