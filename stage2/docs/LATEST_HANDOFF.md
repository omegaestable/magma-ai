# Latest Handoff

Updated: 2026-05-18

This is the short team-memory note for the current Stage 2 solver state. Use the result files for detailed evidence and `tmp_stage2_smoke/` only for raw artifacts.

## Current Solver Snapshot

- Active source: `stage2/solver/solver.py`.
- Packaged artifact: `stage2/submissions/solver.py`, last packaged at `70631` bytes.
- Submission directory should contain only `solver.py`.
- Public zero-token baseline to beat or preserve: `1201/1669` from `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`.
- Full public no-loss validation after the final optimization patch is still pending. Do not claim a promoted `1201/1669` for the optimized package until that check is run.

## What Changed This Session

- Added broad zero-token `true:grind` fallback as a discovery route for short absorption/congruence-shaped TRUE rows.
- Added compact named FALSE witness tables `S4D`, `S4E`, and `S5D`.
- Added reusable sweep/analysis tooling:
  - `stage2/experiments/run_zero_token_sweeps.py`
  - `stage2/experiments/analyze_zero_token_run.py`
  - `stage2/experiments/extract_grind_ledger.py`
- Built exact public `true:grind` ledgers: `34` accepted and `433` incorrect from `467` total grind attempts.
- Kept broad `grind` eligibility, but capped the emitted Lean proof with `set_option maxHeartbeats 10 in` before `grind`.
- Added behavior-preserving caches for repeated term work: term size/depth/rendering, variables, subterms, duals, boundary vars, subterm paths, path lookup, subterm replacement, and context-to-Lean rendering.
- Trimmed duplicate root expansion in `goal_term_pool` and `absorption_term_pool` while preserving existing pool order.

## Best Public Evidence

Latest completed official public zero-token Marathon refresh, before the final heartbeat/path-helper optimization patch:

| Set | Solved | TRUE | FALSE | Notes |
| --- | ---: | ---: | ---: | --- |
| `normal` | `803/1000` | 305 | 498 | salvaged via isolated `--score-only` after a Lean artifact failure |
| `hard1` | `42/69` | 6 | 36 | clean full lane |
| `hard2` | `92/200` | 16 | 76 | clean full lane |
| `hard3` | `264/400` | 63 | 201 | clean full lane |
| **Total** | `1201/1669` | 390 | 811 | `0` solver tokens |

Answer-kind totals for that baseline:

- `false:finite`: `811` accepted.
- `true:certificate`: `356` accepted.
- `true:grind`: `34` accepted, `433` incorrect.
- Remaining public misses by labels: `429` TRUE and `39` FALSE.

## Latest Regression Evidence

- Exact grind ledger extraction reconciled to `34 accepted / 433 incorrect`.
- Accepted-grind fixture with heartbeat cap: `34/34` accepted.
- Lower heartbeat probe: `hb=5` scored `33/34`, so do not lower below `10` without fresh evidence.
- Compact witness fixture: `8/8` accepted with `S4D/S4E/S5D` coverage.
- Official `normal_100` smoke after the optimization patch: `76/100`, unchanged from the immediately preceding smoke.
- Packaged optimized solver syntax check passed.

## Key Lessons

1. The frontier is TRUE-heavy. Compact witness mining still helps, but the next material lift needs explicit TRUE proof extraction.
2. `true:grind` is useful but noisy. It found `34` public TRUE wins and caused `433` incorrect attempts; the heartbeat cap is the safe timing mitigation found this session.
3. Do not tighten `grind_true_candidate` from the current ledger. Accepted and incorrect grind rows overlap heavily on absorption shape, same-LHS shape, variable counts, term sizes, and depths.
4. The next clean TRUE route should be a bounded local congruence/e-graph extractor before fallback `grind`, using existing parsing, substitution, rewrite-step, absorption-pool, and proof-chain helpers.
5. The vendored Solo harness still has local OpenRouter provider-normalization drift. This does not affect zero-token Marathon scoring, but mention it before treating harness output as upstream-clean.

## Recommended Next Steps

1. Run a full public no-loss validation when budget allows: `normal`, `hard1`, `hard2`, and `hard3` against the optimized packaged solver. Required baseline is at least `1201/1669`, with no lost accepted-grind rows.
2. If no-loss holds, update `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md` or add a new dated optimization result summary.
3. Implement proof-producing local congruence/e-graph TRUE extraction before `true:grind`; avoid heuristic grind filters unless the accepted-grind fixture stays `34/34`.
4. Keep HF mirror sweeps separate from public evidence.
5. Before upload or promotion, rerun `stage2/docs/playground-preflight.md` and the adversarial solver review checklist.

## Scratch Discipline

- `tmp_stage2_smoke/` is scratch. Promote only concise dated summaries under `stage2/results/`.
- Do not hardcode public benchmark ids in solver policy. The grind ledgers are regression fixtures only.
- Judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr, ledgers, or summaries.