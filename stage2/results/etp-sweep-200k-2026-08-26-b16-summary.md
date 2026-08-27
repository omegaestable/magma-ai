# Sweep report: etp-sweep-200k-2026-08-26-b16

- rows: **10000**
- solved: **9994 (99.94%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **6**
- solver-claimed verdicts: {'false': 5000, 'true': 4994}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 36, 51
- seconds: total 16187.2, mean 1.619, p50 0.003, p95 9.302, p99 9.973, slowest solved 215.517

## Route families

- `witness`: 4673
- `singleton`: 2397
- `egg_collapse`: 1284
- `completion`: 737
- `spine`: 173
- `equational_closure`: 137
- `linear`: 120
- `constancy`: 89
- `derived_cp_closure`: 72
- `egg_bootstrap`: 65
- `universal_identity`: 43
- `rewrite`: 31
- `absorption_context_bridge`: 25
- `lemma_bootstrap`: 23
- `enum_fin3`: 19
- `lemma_chain`: 13
- `egg_ladder`: 12
- `absorption_closure`: 6
- `bridge`: 5
- `paired_tail_singleton`: 5
- `product_constancy`: 5
- `affine`: 4
- `sandwich_repeat_singleton`: 4
- `outer_sandwich_singleton`: 4
- `crossed_pair_singleton`: 4

## Failure clustering by hypothesis law

- eq1 `854`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 6, 'eq1_vars': {3: 6}, 'eq1_ops': {4: 6}}

## Failure ledger

- `etp_2923_2909` [skip, label=true, 408.265s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((y ◇ (x ◇ y)) ◇ x) ◇ x`
- `etp_2712_3180` [skip, label=false, 322.152s] eq1 `x = ((y ◇ x) ◇ (y ◇ z)) ◇ x` => eq2 `x = (((y ◇ z) ◇ x) ◇ y) ◇ x`
- `etp_650_3928` [skip, label=true, 371.274s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = (x ◇ (y ◇ y)) ◇ y`
- `etp_854_1045` [skip, label=false, 341.085s] eq1 `x = x ◇ ((y ◇ z) ◇ (x ◇ z))` => eq2 `x = x ◇ ((y ◇ (y ◇ x)) ◇ x)`
- `etp_854_1270` [skip, label=false, 351.739s] eq1 `x = x ◇ ((y ◇ z) ◇ (x ◇ z))` => eq2 `x = x ◇ (((y ◇ z) ◇ w) ◇ x)`
- `etp_686_4027` [skip, label=true, 454.82s] eq1 `x = y ◇ (x ◇ ((z ◇ x) ◇ x))` => eq2 `x ◇ y = (z ◇ (z ◇ y)) ◇ y`
