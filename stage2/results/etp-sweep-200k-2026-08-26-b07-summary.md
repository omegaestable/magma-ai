# Sweep report: etp-sweep-200k-2026-08-26-b07

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'true': 4944, 'false': 5051}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 49, 62
- seconds: total 16001.4, mean 1.6, p50 0.002, p95 8.972, p99 9.826, slowest solved 216.23

## Route families

- `witness`: 4700
- `singleton`: 2328
- `egg_collapse`: 1307
- `completion`: 692
- `spine`: 210
- `constancy`: 142
- `equational_closure`: 136
- `linear`: 107
- `derived_cp_closure`: 75
- `egg_bootstrap`: 54
- `universal_identity`: 35
- `rewrite`: 29
- `absorption_context_bridge`: 24
- `enum_fin3`: 20
- `lemma_bootstrap`: 18
- `lemma_chain`: 18
- `tail_square_singleton`: 10
- `absorption_closure`: 9
- `egg_ladder`: 8
- `middle_self_collapse`: 5
- `paired_tail_singleton`: 5
- `affine`: 4
- `outer_sandwich_singleton`: 4
- `nested_square_singleton`: 4
- `crossed_pair_singleton`: 4

## Failure clustering by hypothesis law

- eq1 `2923`: 3 failures
- eq1 `650`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 5, 'eq1_vars': {3: 5}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_650_660` [skip, label=true, 461.41s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ (y ◇ ((z ◇ z) ◇ w))`
- `etp_2923_806` [skip, label=true, 401.672s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (z ◇ ((w ◇ w) ◇ x))`
- `etp_2923_2499` [skip, label=true, 424.5s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = (y ◇ ((x ◇ x) ◇ z)) ◇ x`
- `etp_650_4629` [skip, label=true, 458.023s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `(x ◇ y) ◇ x = (x ◇ y) ◇ y`
- `etp_2923_302` [skip, label=true, 462.919s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((y ◇ z) ◇ w) ◇ x`
