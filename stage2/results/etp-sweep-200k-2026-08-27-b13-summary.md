# Sweep report: etp-sweep-200k-2026-08-27-b13

- rows: **10000**
- solved: **9998 (99.98%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **2**
- solver-claimed verdicts: {'true': 4966, 'false': 5032}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 47, 57
- seconds: total 16055.2, mean 1.606, p50 0.005, p95 9.497, p99 11.443, slowest solved 392.542

## Route families

- `witness`: 4722
- `singleton`: 2326
- `egg_collapse`: 1225
- `completion`: 802
- `equational_closure`: 179
- `spine`: 161
- `linear`: 119
- `constancy`: 111
- `derived_cp_closure`: 65
- `egg_bootstrap`: 51
- `rewrite`: 40
- `absorption_context_bridge`: 31
- `universal_identity`: 27
- `lemma_bootstrap`: 19
- `enum_fin3`: 16
- `lemma_chain`: 13
- `egg_ladder`: 11
- `tail_square_singleton`: 9
- `wrapped_tail_singleton`: 5
- `forked_square_singleton`: 5
- `deep_repeat_singleton`: 5
- `affine`: 4
- `egg_closure`: 4
- `crossed_pair_singleton`: 4
- `local_model4`: 4

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 2}, 'eq1_ops': {4: 2}}

## Failure ledger

- `etp_1133_1167` [skip, label=false, 323.615s] eq1 `x = y ◇ ((y ◇ (z ◇ y)) ◇ x)` => eq2 `x = y ◇ ((z ◇ (y ◇ y)) ◇ x)`
- `etp_650_3080` [skip, label=true, 379.648s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (((x ◇ y) ◇ y) ◇ y) ◇ z`
