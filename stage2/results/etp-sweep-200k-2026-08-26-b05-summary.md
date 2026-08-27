# Sweep report: etp-sweep-200k-2026-08-26-b05

- rows: **10000**
- solved: **9994 (99.94%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **6**
- solver-claimed verdicts: {'false': 5034, 'true': 4960}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 44, 51
- seconds: total 16256.9, mean 1.626, p50 0.004, p95 9.348, p99 10.135, slowest solved 184.672

## Route families

- `witness`: 4738
- `singleton`: 2300
- `egg_collapse`: 1339
- `completion`: 747
- `spine`: 164
- `equational_closure`: 136
- `constancy`: 114
- `linear`: 101
- `derived_cp_closure`: 64
- `egg_bootstrap`: 61
- `absorption_context_bridge`: 36
- `universal_identity`: 32
- `lemma_bootstrap`: 24
- `rewrite`: 23
- `enum_fin3`: 16
- `lemma_chain`: 13
- `egg_ladder`: 10
- `tail_square_singleton`: 6
- `absorption_closure`: 6
- `constraint_fin8`: 5
- `deep_repeat_singleton`: 5
- `dual`: 5
- `sandwich_repeat_singleton`: 5
- `outer_sandwich_singleton`: 4
- `mirrored_alternating_front_self_collapse`: 4

## Failure clustering by hypothesis law

- eq1 `650`: 2 failures
- eq1 `3569`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {3: 6}, 'eq1_ops': {4: 6}}

## Failure ledger

- `etp_650_2667` [skip, label=true, 371.022s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ y) ◇ (x ◇ z)) ◇ z`
- `etp_3569_4667` [skip, label=true, 446.596s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `(x ◇ y) ◇ y = (z ◇ y) ◇ w`
- `etp_3569_3859` [skip, label=true, 322.011s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = (z ◇ w) ◇ (u ◇ w)`
- `etp_1384_3278` [skip, label=true, 277.078s] eq1 `x = y ◇ (((z ◇ z) ◇ x) ◇ y)` => eq2 `x ◇ x = y ◇ (y ◇ (x ◇ x))`
- `etp_3567_4013` [skip, label=true, 407.34s] eq1 `x ◇ y = y ◇ ((z ◇ x) ◇ z)` => eq2 `x ◇ y = (z ◇ (y ◇ z)) ◇ x`
- `etp_650_2874` [skip, label=true, 372.511s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ (y ◇ y)) ◇ x) ◇ z`
