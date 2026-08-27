# Sweep report: etp-sweep-10k-2026-08-25

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'true': 4996, 'false': 4999}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 45, 54
- seconds: total 16959.9, mean 1.696, p50 0.005, p95 9.52, p99 10.511, slowest solved 177.327

## Route families

- `witness`: 4687
- `singleton`: 2331
- `egg_collapse`: 1241
- `completion`: 841
- `spine`: 181
- `equational_closure`: 135
- `constancy`: 120
- `linear`: 105
- `derived_cp_closure`: 84
- `egg_bootstrap`: 52
- `universal_identity`: 41
- `absorption_context_bridge`: 27
- `rewrite`: 22
- `lemma_chain`: 16
- `enum_fin3`: 15
- `tail_square_singleton`: 13
- `lemma_bootstrap`: 10
- `absorption_closure`: 8
- `egg_ladder`: 7
- `crossed_pair_singleton`: 6
- `affine`: 4
- `bridge`: 4
- `deep_repeat_singleton`: 3
- `paired_tail_singleton`: 3
- `dual`: 3

## Failure clustering by hypothesis law

- eq1 `2923`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 4, 'eq1_vars': {3: 5}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_2923_156` [skip, label=true, 420.579s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x = (x ◇ y) ◇ (x ◇ x)`
  - engine time: constraint_countermodel 111.493s, egg_ladder_route 60.225s, egg_priority_bootstrap_route 40.025s, egg_bootstrap_route 24.027s
- `etp_481_3050` [skip, label=false, 263.822s] eq1 `x = y ◇ (x ◇ (y ◇ (z ◇ z)))` => eq2 `x = (((x ◇ x) ◇ x) ◇ x) ◇ x`
  - engine time: constraint_countermodel 227.875s, lemma_chain_bootstrap_route 8.352s, egg_bootstrap_route 7.401s, local_model_counterexample 6.0s
- `etp_3569_4143` [skip, label=true, 520.547s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = ((x ◇ z) ◇ y) ◇ z`
  - engine time: constraint_countermodel 135.532s, egg_ladder_route 60.54s, egg_priority_bootstrap_route 40.169s, egg_bootstrap_route 28.023s
- `etp_2854_4676` [skip, label=true, 289.17s] eq1 `x = ((x ◇ (x ◇ y)) ◇ x) ◇ z` => eq2 `(x ◇ y) ◇ z = (x ◇ w) ◇ u`
  - engine time: constraint_countermodel 145.072s, egg_ladder_route 61.282s, egg_bootstrap_route 16.633s, lemma_chain_bootstrap_route 10.333s
- `etp_2923_3397` [skip, label=true, 441.426s] eq1 `x = ((y ◇ (x ◇ z)) ◇ y) ◇ x` => eq2 `x ◇ y = z ◇ (y ◇ (x ◇ y))`
  - engine time: constraint_countermodel 112.68s, egg_ladder_route 60.115s, egg_priority_bootstrap_route 40.005s, egg_bootstrap_route 24.026s
