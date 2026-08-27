# Sweep report: etp-sweep-200k-2026-08-27-b10

- rows: **10000**
- solved: **9999 (99.99%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **1**
- solver-claimed verdicts: {'true': 5025, 'false': 4974}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 47, 55
- seconds: total 15271.7, mean 1.527, p50 0.006, p95 9.499, p99 11.479, slowest solved 217.434

## Route families

- `witness`: 4642
- `singleton`: 2346
- `egg_collapse`: 1223
- `completion`: 817
- `spine`: 186
- `equational_closure`: 148
- `constancy`: 138
- `linear`: 119
- `derived_cp_closure`: 89
- `egg_bootstrap`: 49
- `universal_identity`: 37
- `rewrite`: 27
- `lemma_bootstrap`: 25
- `absorption_context_bridge`: 25
- `lemma_chain`: 20
- `enum_fin3`: 13
- `egg_ladder`: 9
- `tail_square_singleton`: 7
- `absorption_closure`: 7
- `nested_square_singleton`: 6
- `bridge`: 6
- `affine`: 5
- `mirrored_alternating_front_self_collapse`: 5
- `egg_closure`: 4
- `wrapped_tail_singleton`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 1, 'eq1_vars': {3: 1}, 'eq1_ops': {4: 1}}

## Failure ledger

- `etp_650_2480` [skip, label=true, 432.958s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ ((y ◇ z) ◇ y)) ◇ x`
