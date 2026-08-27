# Sweep report: etp-sweep-100k-2026-08-25-b10

- rows: **10000**
- solved: **9996 (99.96%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **4**
- solver-claimed verdicts: {'false': 5021, 'true': 4975}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 42, 47
- seconds: total 16456.0, mean 1.646, p50 0.006, p95 9.415, p99 10.925, slowest solved 229.294

## Route families

- `witness`: 4712
- `singleton`: 2355
- `egg_collapse`: 1253
- `completion`: 748
- `spine`: 165
- `equational_closure`: 138
- `linear`: 111
- `constancy`: 109
- `egg_bootstrap`: 80
- `derived_cp_closure`: 76
- `universal_identity`: 52
- `rewrite`: 27
- `absorption_context_bridge`: 24
- `enum_fin3`: 23
- `lemma_chain`: 20
- `lemma_bootstrap`: 15
- `absorption_closure`: 13
- `egg_ladder`: 10
- `egg_closure`: 6
- `outer_sandwich_singleton`: 5
- `paired_tail_singleton`: 5
- `tail_square_singleton`: 5
- `alternating_front_self_collapse`: 5
- `mirrored_alternating_front_self_collapse`: 4
- `wrapped_tail_singleton`: 4

## Failure clustering by hypothesis law

- eq1 `2923`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {4: 1, 3: 3}, 'eq1_ops': {4: 4}}

## Failure ledger

- `etp_3983_3997` [skip, label=true, 397.924s] eq1 `x ◇ y = (y ◇ (z ◇ w)) ◇ x` => eq2 `x ◇ y = (z ◇ (x ◇ z)) ◇ y`
- `etp_2923_2683` [skip, label=true, 434.55s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = ((x ◇ y) ◇ (z ◇ y)) ◇ x`
- `etp_469_583` [skip, label=true, 383.334s] eq1 `x = y ◇ (x ◇ (x ◇ (z ◇ x)))` => eq2 `x = y ◇ (z ◇ (z ◇ (w ◇ x)))`
- `etp_2923_1415` [skip, label=true, 464.814s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = y ◇ (((z ◇ w) ◇ w) ◇ x)`
