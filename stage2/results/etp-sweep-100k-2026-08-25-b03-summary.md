# Sweep report: etp-sweep-100k-2026-08-25-b03

- rows: **10000**
- solved: **9995 (99.95%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **5**
- solver-claimed verdicts: {'true': 4986, 'false': 5009}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 44, 56
- seconds: total 16898.1, mean 1.69, p50 0.005, p95 9.398, p99 11.412, slowest solved 261.129

## Route families

- `witness`: 4704
- `singleton`: 2321
- `egg_collapse`: 1250
- `completion`: 793
- `spine`: 175
- `equational_closure`: 153
- `constancy`: 123
- `linear`: 101
- `egg_bootstrap`: 65
- `derived_cp_closure`: 63
- `universal_identity`: 43
- `rewrite`: 33
- `absorption_context_bridge`: 25
- `lemma_bootstrap`: 21
- `enum_fin3`: 19
- `lemma_chain`: 16
- `egg_ladder`: 10
- `tail_square_singleton`: 7
- `absorption_closure`: 6
- `deep_repeat_singleton`: 5
- `egg_closure`: 5
- `forked_square_singleton`: 4
- `reverse_deep_repeat_singleton`: 4
- `local_model4`: 4
- `mirrored_alternating_front_self_collapse`: 4

## Failure clustering by hypothesis law

- eq1 `650`: 2 failures

Failure shapes: {'eq1_bare_variable_side': 3, 'eq1_vars': {3: 4, 2: 1}, 'eq1_ops': {4: 5}}

## Failure ledger

- `etp_4453_4652` [skip, label=true, 448.565s] eq1 `x ◇ (y ◇ x) = (z ◇ x) ◇ y` => eq2 `(x ◇ y) ◇ x = (z ◇ w) ◇ w`
- `etp_3569_4267` [skip, label=true, 263.592s] eq1 `x ◇ y = y ◇ ((z ◇ y) ◇ x)` => eq2 `x ◇ y = ((z ◇ w) ◇ u) ◇ v`
- `etp_650_4065` [skip, label=true, 372.885s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x ◇ x = ((x ◇ x) ◇ x) ◇ x`
- `etp_2531_23` [skip, label=false, 348.232s] eq1 `x = (y ◇ ((y ◇ x) ◇ x)) ◇ y` => eq2 `x = (x ◇ x) ◇ x`
- `etp_650_3050` [skip, label=true, 332.721s] eq1 `x = x ◇ (y ◇ ((z ◇ x) ◇ y))` => eq2 `x = (((x ◇ x) ◇ x) ◇ x) ◇ x`
