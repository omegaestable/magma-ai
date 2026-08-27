# Sweep report: etp-sweep-200k-2026-08-27-b05

- rows: **10000**
- solved: **9997 (99.97%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **3**
- solver-claimed verdicts: {'false': 5069, 'true': 4928}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 39, 51
- seconds: total 16586.4, mean 1.659, p50 0.005, p95 9.49, p99 10.762, slowest solved 228.671

## Route families

- `witness`: 4755
- `singleton`: 2316
- `egg_collapse`: 1196
- `completion`: 802
- `spine`: 144
- `equational_closure`: 138
- `linear`: 132
- `constancy`: 114
- `derived_cp_closure`: 85
- `egg_bootstrap`: 54
- `universal_identity`: 47
- `absorption_context_bridge`: 32
- `lemma_bootstrap`: 29
- `enum_fin3`: 27
- `rewrite`: 27
- `lemma_chain`: 14
- `absorption_closure`: 10
- `egg_ladder`: 9
- `tail_square_singleton`: 8
- `affine`: 4
- `left_projection_collapse`: 4
- `right_projection_collapse`: 4
- `front_double_self_collapse`: 4
- `constraint_fin5`: 3
- `sandwich_repeat_singleton`: 3

## Failure clustering by hypothesis law

- eq1 `650`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {4: 1, 3: 2}, 'eq1_ops': {4: 3}}

## Failure ledger

- `etp_3983_4626` [skip, label=true, 423.657s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `(x ◇ x) ◇ y = (z ◇ w) ◇ z`
- `etp_650_2863` [skip, label=true, 365.178s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = ((x ◇ (y ◇ x)) ◇ x) ◇ y`
- `etp_650_1636` [skip, label=true, 434.282s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ x) ◇ ((y ◇ x) ◇ z)`
