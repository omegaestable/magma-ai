# Sweep report: etp-sweep-200k-2026-08-26-b10

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'false': 4985, 'true': 5010}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 56, 65
- seconds: total 16697.7, mean 1.67, p50 0.006, p95 9.485, p99 11.401, slowest solved 170.748

## Route families

- `witness`: 4678
- `singleton`: 2263
- `egg_collapse`: 1254
- `completion`: 825
- `equational_closure`: 162
- `spine`: 159
- `constancy`: 127
- `linear`: 109
- `derived_cp_closure`: 88
- `egg_bootstrap`: 66
- `universal_identity`: 40
- `rewrite`: 39
- `absorption_context_bridge`: 31
- `enum_fin3`: 27
- `lemma_bootstrap`: 16
- `lemma_chain`: 15
- `absorption_closure`: 8
- `egg_closure`: 6
- `mirrored_alternating_front_self_collapse`: 6
- `paired_tail_singleton`: 6
- `middle_self_collapse`: 5
- `affine`: 5
- `egg_ladder`: 5
- `tail_square_singleton`: 5
- `deep_repeat_singleton`: 5

## Failure clustering by hypothesis law

- eq1 `3569`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 2, 'eq1_vars': {3: 4, 4: 1}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_3569_3910` [skip, label=true, 451.26s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ x = (y ◇ (z ◇ w)) ◇ y`
- `etp_650_854` [skip, label=true, 439.632s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = x ◇ ((y ◇ z) ◇ (x ◇ z))`
- `etp_1485_1483` [skip, label=false, 326.505s] eq1 `x = (y ◇ x) ◇ (x ◇ (z ◇ y))` => eq2 `x = (y ◇ x) ◇ (x ◇ (y ◇ z))`
- `etp_3569_3651` [skip, label=true, 449.416s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = z ◇ ((w ◇ w) ◇ w)`
- `etp_3983_4577` [skip, label=true, 298.164s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ (y ◇ z) = (w ◇ u) ◇ x`
