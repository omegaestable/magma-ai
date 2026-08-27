# Sweep report: etp-sweep-200k-2026-08-26-b04

- rows: **10000**
- solved: **9997 (99.97%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **3**
- solver-claimed verdicts: {'true': 5003, 'false': 4994}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 43, 53
- seconds: total 14608.5, mean 1.461, p50 0.004, p95 9.335, p99 9.969, slowest solved 216.169

## Route families

- `witness`: 4681
- `singleton`: 2385
- `egg_collapse`: 1286
- `completion`: 775
- `spine`: 164
- `equational_closure`: 144
- `linear`: 124
- `constancy`: 117
- `derived_cp_closure`: 63
- `egg_bootstrap`: 61
- `universal_identity`: 33
- `rewrite`: 28
- `absorption_context_bridge`: 23
- `enum_fin3`: 18
- `lemma_chain`: 12
- `lemma_bootstrap`: 12
- `tail_square_singleton`: 8
- `absorption_closure`: 6
- `nested_square_singleton`: 5
- `outer_sandwich_singleton`: 4
- `mirrored_alternating_front_self_collapse`: 4
- `repeated_prefix_product_constancy`: 3
- `crossed_pair_singleton`: 3
- `right_projection_collapse`: 3
- `dual`: 3

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {4: 1, 3: 2}, 'eq1_ops': {4: 3}}

## Failure ledger

- `etp_3983_3443` [skip, label=true, 401.905s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = z ◇ (w ◇ (z ◇ w))`
- `etp_645_52` [skip, label=false, 342.827s] eq1 `x = x ◇ (y ◇ ((y ◇ z) ◇ x))` => eq2 `x = x ◇ (y ◇ (x ◇ x))`
- `etp_469_4327` [skip, label=true, 351.105s] eq1 `x = y ◇ (x ◇ (x ◇ (z ◇ x)))` => eq2 `x ◇ (y ◇ x) = z ◇ (x ◇ x)`
