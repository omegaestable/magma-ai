# Sweep report: etp-sweep-200k-2026-08-26-b20

- rows: **10000**
- solved: **9998 (99.98%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **2**
- solver-claimed verdicts: {'false': 5015, 'true': 4983}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 47, 52
- seconds: total 14819.1, mean 1.482, p50 0.004, p95 9.33, p99 9.875, slowest solved 214.528

## Route families

- `witness`: 4694
- `singleton`: 2338
- `egg_collapse`: 1301
- `completion`: 710
- `spine`: 177
- `equational_closure`: 144
- `constancy`: 130
- `linear`: 119
- `derived_cp_closure`: 88
- `egg_bootstrap`: 71
- `universal_identity`: 41
- `rewrite`: 32
- `lemma_chain`: 20
- `absorption_context_bridge`: 18
- `enum_fin3`: 16
- `lemma_bootstrap`: 15
- `egg_ladder`: 10
- `absorption_closure`: 6
- `alternating_front_self_collapse`: 5
- `front_double_self_collapse`: 5
- `outer_sandwich_singleton`: 5
- `crossed_pair_singleton`: 5
- `mirrored_alternating_front_self_collapse`: 4
- `constraint_fin8`: 4
- `middle_self_collapse`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 1, 'eq1_vars': {3: 2}, 'eq1_ops': {4: 2}}

## Failure ledger

- `etp_898_2355` [skip, label=false, 286.892s] eq1 `x = y ◇ ((x ◇ z) ◇ (z ◇ y))` => eq2 `x = (y ◇ (y ◇ (z ◇ z))) ◇ x`
- `etp_3569_3618` [skip, label=true, 501.813s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = z ◇ ((z ◇ x) ◇ z)`
