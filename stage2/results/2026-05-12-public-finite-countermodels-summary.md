# Public Finite Countermodels Summary

Date: 2026-05-12

Solver artifact: `stage2/submissions/solver.py`

| Set | Problems | Solved | TRUE | FALSE | Failed/missing | Expected TRUE | Expected FALSE | Judge calls | LLM calls | Runner time (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `normal` | 1000 | 743 | 245 | 498 | 257 | 500 | 500 | 743 | 0 | 2329.2 |
| `hard1` | 69 | 17 | 0 | 17 | 52 | 24 | 45 | 17 | 0 | 67.7 |
| `hard2` | 200 | 52 | 0 | 52 | 148 | 100 | 100 | 52 | 0 | 215.4 |
| `hard3` | 400 | 186 | 3 | 183 | 214 | 195 | 205 | 186 | 0 | 671.8 |
| **Total** | 1669 | 998 | 248 | 750 | 671 | 819 | 850 | 998 | 0 | 3284.0 |

## Accepted Route Labels

- `true:singleton`: 244
- `false:witness:LP`: 150
- `false:witness:RP`: 123
- `false:witness:C0`: 116
- `false:enum_fin3`: 89
- `false:witness:XOR`: 43
- `false:affine:z3:0,1,1`: 43
- `false:affine:z3:1,0,1`: 36
- `false:witness:T3L`: 34
- `false:linear:z5:2,4`: 15
- `false:linear:z5:4,2`: 14
- `false:affine:z2:1,0,1`: 9
- `false:linear:z5:0,2`: 9
- `false:witness:T3R`: 8
- `false:linear:z5:3,3`: 8
- `false:linear:z3:2,2`: 8
- `false:witness:A2`: 5
- `false:affine:z2:0,1,1`: 5
- `false:enum_fin2`: 5
- `false:witness:AND`: 5
- `false:linear:z5:2,2`: 5
- `false:affine:z3:2,2,1`: 4
- `false:witness:Z3A`: 4
- `false:linear:z5:2,0`: 4
- `false:linear:z3:2,1`: 3
- `true:rewrite`: 2
- `false:linear:z3:1,2`: 2
- `true:rewrite:symm`: 1
- `false:linear:z5:1,2`: 1
- `true:bridge:11`: 1
- `false:linear:z5:2,1`: 1
- `false:linear:z5:1,3`: 1

## Notes

- Public `answer` fields are used only for triage labels, not solver policy.
- Failed rows with zero judge calls are deterministic skips, not rejected Lean certificates.
- The paired failure ledger is `stage2/results/2026-05-12-public-failure-ledger.jsonl`.

## Next Families

- `true_template_gap`: 571
- `finite_countermodel_gap`: 100
