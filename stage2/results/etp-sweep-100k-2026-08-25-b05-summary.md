# Sweep report: etp-sweep-100k-2026-08-25-b05

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'false': 4981, 'true': 5014}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 41, 48
- seconds: total 16139.0, mean 1.614, p50 0.005, p95 9.356, p99 10.69, slowest solved 86.125

## Route families

- `witness`: 4672
- `singleton`: 2274
- `egg_collapse`: 1330
- `completion`: 779
- `spine`: 178
- `equational_closure`: 170
- `constancy`: 114
- `linear`: 104
- `derived_cp_closure`: 72
- `egg_bootstrap`: 57
- `universal_identity`: 44
- `rewrite`: 35
- `lemma_bootstrap`: 26
- `absorption_context_bridge`: 21
- `lemma_chain`: 20
- `enum_fin3`: 17
- `absorption_closure`: 9
- `right_projection_collapse`: 6
- `tail_square_singleton`: 6
- `egg_ladder`: 6
- `reverse_deep_repeat_singleton`: 5
- `egg_closure`: 5
- `outer_sandwich_singleton`: 4
- `paired_tail_singleton`: 4
- `deep_repeat_singleton`: 3

## Failure clustering by hypothesis law

- eq1 `2923`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {3: 4, 4: 1}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_650_3721` [skip, label=true, 408.362s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ y = (x ◇ y) ◇ (x ◇ x)`
- `etp_2923_3664` [skip, label=true, 411.346s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ x = (x ◇ y) ◇ (x ◇ x)`
- `etp_3983_3800` [skip, label=true, 401.29s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (z ◇ x) ◇ (w ◇ w)`
- `etp_2923_4334` [skip, label=true, 411.804s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ (y ◇ x) = z ◇ (w ◇ x)`
- `etp_3569_4370` [skip, label=true, 449.014s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ (y ◇ z) = z ◇ (y ◇ w)`
