# 2026-05-18 Zero-Token Public Refresh After Witness Patch

This is official Marathon runner evidence for the packaged Stage 2 solver after adding
the compact `S4D`, `S4E`, and `S5D` finite witness tables. All solver lanes used
`--budget-tokens 0` against `stage2/submissions/`, which contained only `solver.py`
(`69553` bytes, under the 500 KB submission limit).

Raw run root:

- `tmp_stage2_smoke/2026-05-17-zero-token-sweep-after-witness/official_public/`

## Result

| Set | Problems | Solved | TRUE | FALSE | Attempted | Incorrect | Not attempted | Tokens | Wall source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `normal` | 1000 | 803 | 305 | 498 | 984 | 181 | 16 | 0* | solver run `504.9s`; score-only summary wall null |
| `hard1` | 69 | 42 | 6 | 36 | 64 | 22 | 5 | 0 | `47.5s` |
| `hard2` | 200 | 92 | 16 | 76 | 191 | 99 | 9 | 0 | `164.6s` |
| `hard3` | 400 | 264 | 63 | 201 | 395 | 131 | 5 | 0 | `319.7s` |
| **Total** | 1669 | 1201 | 390 | 811 | 1634 | 433 | 35 | 0 | - |

* `normal` was salvaged with `--score-only`, so `summary.json` has `tokens_used: null`;
  the completed solver run that produced `answers.jsonl` used budget `0` tokens and logged
  `llm_calls: 0`.

Compared with the pre-witness zero-token public Marathon sweep (`1189/1669`), this is
`+12` total:

| Set | Before | After | Delta | TRUE delta | FALSE delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `normal` | 802 | 803 | +1 | +1 | +0 |
| `hard1` | 39 | 42 | +3 | +0 | +3 |
| `hard2` | 89 | 92 | +3 | +0 | +3 |
| `hard3` | 259 | 264 | +5 | +1 | +4 |
| **Total** | 1189 | 1201 | +12 | +2 | +10 |

The `+10` FALSE delta matches the corrected marginal coverage estimate for `S4D`, `S4E`,
and `S5D`. The remaining `+2` TRUE delta is a refresh/scoring delta; the total accepted
`true:grind` count stayed at `34` while failed `true:grind` attempts fell from `437` to
`433`.

## Answer-Kind Totals

Across all four public lanes after the witness patch:

- `false:finite`: `811` accepted.
- `true:certificate`: `356` accepted.
- `true:grind`: `34` accepted, `433` incorrect.
- Official public remainder by answer labels: `429` TRUE rows and `39` FALSE rows remain
  unsolved.

Lane detail:

| Set | `false:finite` accepted | `true:certificate` accepted | `true:grind` accepted | `true:grind` incorrect |
| --- | ---: | ---: | ---: | ---: |
| `normal` | 498 | 288 | 17 | 181 |
| `hard1` | 36 | 2 | 4 | 22 |
| `hard2` | 76 | 11 | 5 | 99 |
| `hard3` | 201 | 55 | 8 | 131 |
| **Total** | 811 | 356 | 34 | 433 |

## Witness Evidence

Focused fixture:

- `tmp_stage2_smoke/2026-05-17-zero-token-sweep/candidate_false_gaps_8.jsonl`
- Official post-witness run: `8/8` accepted, `0` tokens.
- Route counts: `false:witness:S4D=5`, `false:witness:S4E=1`, `false:witness:S5D=2`.

Public refresh evidence:

- `hard1`: route counts include `S4D=2`, `S4E=1`; net `+3` FALSE accepted.
- `hard2`: route counts include `S5D=3`, `S4D=1`; net `+3` FALSE accepted.
- `hard3`: route counts were unavailable because the long solver route JSON in `run.log`
  was truncated, but the corrected marginal ids (`hard3_0344`, `hard3_0345`,
  `hard3_0346`, `hard3_0392`) all accepted in the official full lane; net `+4` FALSE
  accepted.
- `normal`: no net FALSE lift.

## Infrastructure Note

The first post-witness full refresh completed `normal` solver generation (`984` answers)
but hit a judge infrastructure artifact failure during scoring:

- `[score] normal_0067: HARNESS_ERROR - judge infrastructure error: failed to compile JudgeProblem: unknown Lean failure`

The run log was preserved as `normal/run.interrupted.log`. A clean isolated artifact dir
with `JUDGE_ARTIFACT_DIR=.../lean-artifacts-normal-scoreonly` and `--score-only`
rescored the completed `answers.jsonl` to `803/1000` with no harness errors. The hard
lanes were then run with separate isolated artifact dirs and completed cleanly.

## Learnings

1. Compact finite witness mining still has value, but the remaining public frontier is now
   strongly TRUE-heavy: `429` TRUE misses versus `39` FALSE misses.
2. Broad `grind` is useful as a discovery route but too noisy for a clean next promotion:
   `34` accepted and `433` incorrect public attempts, with slow official scoring in the
   hard lanes.
3. Widening existing closure bounds is not promising: prior focus analysis recovered only
   `4/34` public accepted-grind wins from wider existing closures.
4. Accepted `grind` wins are mostly absorption/congruence-shaped (`31/34` absorption-shaped,
   `25/34` same-LHS), so the next route should be proof-producing local congruence/e-graph
   extraction using explicit `h`, `.symm`, `.trans`, and `congrArg` Lean certificates.

## Post-Refresh Optimization Addendum

After this public refresh, the solver was lightly optimized without running another full
public sweep. The optimized package is `70631` bytes and keeps the same broad `true:grind`
eligibility, but the emitted grind proof now uses `set_option maxHeartbeats 10 in` before
`grind`. Exact grind ledgers were extracted from this refresh and reconciled to `34`
accepted and `433` incorrect `true:grind` attempts.

Regression evidence for the optimized package:

- Accepted-grind fixture: `34/34` accepted.
- Lower heartbeat probe: `hb=5` lost one accepted row (`33/34`), so keep the cap at `10`.
- Compact witness fixture: `8/8` accepted.
- `normal_100` zero-token smoke: `76/100`, unchanged from the immediate pre-patch smoke.
- Python syntax and packaged submission syntax checks passed.

The full four-lane public no-loss check for the optimized package remains pending. Treat
the table above as the latest completed public baseline, not as final promotion evidence
for the optimized package.

## Recommended Next Work

1. Run a full public no-loss validation for the optimized package when time allows. The
   required baseline is at least `1201/1669`, with no lost accepted-grind rows.
2. Implement a bounded local congruence proof extractor before broad `true:grind`. Reuse
   existing term parsing, instantiation, substitution proof, and absorption pool helpers;
   emit explicit Lean proof terms and cap pool size, instantiations, generated term size,
   and rounds.
3. Validate against
   `tmp_stage2_smoke/2026-05-17-zero-token-sweep/local_congruence_grind_focus.jsonl`, then
   run the existing witness and TRUE closure regression fixtures.
4. Keep `true:grind` as a temporary last-resort/discovery fallback until explicit proofs
   cover most of its wins. Do not tighten its structural filter from the current ledger;
   accepted and incorrect rows overlap too much.
5. Run the HF mirror sweep separately from public evidence:

```powershell
.\.venv\Scripts\python.exe stage2\experiments\run_zero_token_sweeps.py --scope hf --include-hf-core-duplicates --run-root tmp_stage2_smoke\2026-05-17-zero-token-hf-after-witness --force
```
