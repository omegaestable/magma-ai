# Sweep report: order4-probe-1517-one-diagnosed

- rows: **1**
- solved: **0 (0.0%)**
- soundness events (oracle failure / label mismatch): **0**
- crashes: **0**
- skips: **1**
- solver-claimed verdicts: {}
- TRUE certs with no independent verification (vacuous battery, unsupported shape): 0, 0
- seconds: total 60.1, mean 60.116, p50 0.0, p95 0.0, p99 0.0, slowest solved 0.0

## Route families


## Failure clustering by hypothesis law


Failure shapes: {'eq1_bare_variable_side': 1, 'eq1_vars': {3: 1}, 'eq1_ops': {4: 1}}

## Failure ledger

- `etp_1517_19` [skip, label=true, 60.116s] eq1 `x = (y ◇ y) ◇ (x ◇ (x ◇ z))` => eq2 `x = y ◇ (z ◇ x)`
  - engine time: lemma_chain_bootstrap_route 10.363s, derived_cp_closure_route 8.001s, projection_bootstrap_route 8.0s, lemma_bootstrap_route 6.126s
