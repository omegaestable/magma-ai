# Sweep report: etp-sweep-200k-2026-08-26-b06

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'false': 5060, 'true': 4936}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 32, 38
- seconds: total 15337.8, mean 1.534, p50 0.004, p95 9.315, p99 9.733, slowest solved 201.194

## Route families

- `witness`: 4737
- `singleton`: 2329
- `egg_collapse`: 1264
- `completion`: 737
- `spine`: 146
- `equational_closure`: 144
- `linear`: 143
- `constancy`: 142
- `derived_cp_closure`: 70
- `egg_bootstrap`: 69
- `universal_identity`: 41
- `lemma_bootstrap`: 27
- `absorption_context_bridge`: 27
- `enum_fin3`: 23
- `lemma_chain`: 17
- `rewrite`: 15
- `absorption_closure`: 7
- `egg_ladder`: 6
- `reverse_deep_repeat_singleton`: 4
- `dual`: 4
- `middle_self_collapse`: 4
- `tail_square_singleton`: 4
- `left_projection_collapse`: 3
- `front_double_self_collapse`: 3
- `deep_repeat_singleton`: 3

## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 4}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_3569_3566` [skip, label=true, 510.998s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = y ◇ ((z ◇ x) ◇ y)`
- `etp_3567_4026` [skip, label=true, 409.307s] eq1 `x ◇ y = y ◇ ((z ◇ x) ◇ z)` => eq2 `x ◇ y = (z ◇ (z ◇ y)) ◇ x`
- `etp_650_2249` [skip, label=true, 430.795s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (x ◇ (x ◇ (y ◇ z))) ◇ x`
- `etp_765_4622` [skip, label=true, 310.87s] eq1 `x = y ◇ (z ◇ ((y ◇ z) ◇ x))` => eq2 `(x ◇ x) ◇ y = (z ◇ z) ◇ y`
