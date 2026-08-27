# Sweep report: etp-sweep-200k-2026-08-26-b19

- rows: **10000**
- solved: **9999 (99.99%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **1**
- solver-claimed verdicts: {'false': 5018, 'true': 4981}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 54, 65
- seconds: total 14913.1, mean 1.491, p50 0.004, p95 9.316, p99 10.205, slowest solved 233.835

## Route families

- `witness`: 4672
- `singleton`: 2327
- `egg_collapse`: 1280
- `completion`: 734
- `spine`: 190
- `equational_closure`: 163
- `constancy`: 120
- `linear`: 119
- `derived_cp_closure`: 75
- `egg_bootstrap`: 53
- `universal_identity`: 43
- `absorption_context_bridge`: 26
- `rewrite`: 25
- `enum_fin3`: 22
- `lemma_bootstrap`: 20
- `lemma_chain`: 20
- `absorption_closure`: 13
- `egg_ladder`: 9
- `egg_closure`: 6
- `tail_square_singleton`: 6
- `mirrored_alternating_front_self_collapse`: 5
- `paired_tail_singleton`: 5
- `dual`: 5
- `nested_square_singleton`: 5
- `right_projection_collapse`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 1, 'eq1_vars': {3: 1}, 'eq1_ops': {4: 1}}

## Failure ledger

- `etp_2789_3297` [skip, label=true, 250.087s] eq1 `x = ((y ◇ z) ◇ (y ◇ x)) ◇ z` => eq2 `x ◇ x = y ◇ (z ◇ (z ◇ y))`
