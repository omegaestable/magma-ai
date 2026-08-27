# Sweep report: etp-sweep-100k-2026-08-25-b04

- rows: **10000**
- solved: **9997 (99.97%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **3**
- solver-claimed verdicts: {'false': 4948, 'true': 5049}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 38, 43
- seconds: total 15811.7, mean 1.581, p50 0.005, p95 9.383, p99 9.983, slowest solved 214.404

## Route families

- `witness`: 4670
- `singleton`: 2382
- `egg_collapse`: 1288
- `completion`: 773
- `equational_closure`: 159
- `spine`: 134
- `constancy`: 133
- `linear`: 115
- `derived_cp_closure`: 75
- `egg_bootstrap`: 59
- `universal_identity`: 34
- `rewrite`: 27
- `enum_fin3`: 19
- `absorption_context_bridge`: 18
- `lemma_bootstrap`: 13
- `egg_ladder`: 12
- `absorption_closure`: 10
- `lemma_chain`: 10
- `egg_closure`: 7
- `bridge`: 6
- `tail_square_singleton`: 6
- `affine`: 5
- `sandwich_repeat_singleton`: 4
- `mirrored_alternating_front_self_collapse`: 4
- `paired_tail_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {4: 1, 3: 2}, 'eq1_ops': {4: 3}}

## Failure ledger

- `etp_3577_3746` [skip, label=true, 415.007s] eq1 `x ◇ y = y ◇ ((z ◇ w) ◇ x)` => eq2 `x ◇ y = (x ◇ z) ◇ (w ◇ w)`
- `etp_898_4270` [skip, label=false, 289.74s] eq1 `x = y ◇ ((x ◇ z) ◇ (z ◇ y))` => eq2 `x ◇ (x ◇ x) = x ◇ (y ◇ y)`
- `etp_2923_1115` [skip, label=true, 433.248s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ ((y ◇ (x ◇ z)) ◇ x)`
