# Latest Handoff

Updated: 2026-05-20

This is the short team-memory note for the current Stage 2 solver state. Use the result files for detailed evidence and `tmp_stage2_smoke/` only for raw artifacts.

## Current Solver Snapshot

- Active source: `stage2/solver/solver.py`.
- Packaged artifact: `stage2/submissions/solver.py`, last packaged at `76136` bytes.
- Submission directory should contain only `solver.py`.
- Historical public zero-token baseline: `1201/1669` from `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`, including `34` now-retired grind wins.
- Full public validation after the grind rollback is still pending. Do not claim the post-rollback package preserves the old grind-backed total until a new run exists; use positive-token proxy evidence for LLM-backed promotion.

## What Changed This Session

- Playground experience showed the broad `true:grind` idea is not viable: its error rate exploded under playground conditions, so grind-heavy evidence is no longer promotion evidence.
- Removed `true:grind` from active solver policy; default packaged/playground runs escalate unresolved rows to the official LLM proxy instead.
- Aligned solver-side Marathon `LLM_CONFIG` with the official proxy config shape: `max_output_tokens=65536`, `reasoning_effort=medium`, and the same `openai/gpt-oss-120b` / `deepinfra/bf16` routing hint.
- `stage2/experiments/run_playground_parity_llm.py` is now the default playground-parity gate: it can build a reproducible mixed official fixture, runs official Solo and Marathon proxy paths, and fails if local evidence records zero LLM calls, zero Marathon tokens, missing key/proxy errors, or unclassified LLM/judge failures.
- Raised the default real-solver Marathon LLM probe budget in `stage2/experiments/homelab_llm_probe.py` to clear the official max-output headroom check.
- Updated `stage2/docs/playground-preflight.md` so zero-token Marathon is optional deterministic regression only and positive-token proxy usage is the active readiness gate.
- Added `stage2/docs/solver-route-ledger.md`, route motif cards under `stage2/docs/motif-cards/`, `theory/TEORTH_NOTES.md`, and `stage2/docs/cleanup-manifest.md` for the conservative deep-polish handoff.
- Added a narrow structural `E1072`-shape collapse route in `stage2/solver/solver.py`: it derives local `E19` from `x = y ◇ ((x ◇ (x ◇ x)) ◇ x)` and composes through existing simple `E19` routes.
- Added `stage2/experiments/profile_solver_routes.py` and capped regular `true:absorption_closure` with `ABSORPTION_TIME_BUDGET = 0.05` after a zero-token `normal_100` run hit the 600s wall budget.

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
- `true:grind`: `34` accepted, `433` incorrect; historical discovery evidence only.
- Remaining public misses by labels: `429` TRUE and `39` FALSE.

## Latest Regression Evidence

- Exact grind ledger extraction reconciled to `34 accepted / 433 incorrect`.
- Accepted-grind fixture with heartbeat cap: historical discovery evidence only; the active solver no longer emits `true:grind` certificates.
- Lower heartbeat probe: `hb=5` scored `33/34`, so do not lower below `10` without fresh evidence.
- Compact witness fixture: `8/8` accepted with `S4D/S4E/S5D` coverage.
- C9 focused fixture: `hard3_0140` (`E1072 -> E1251`) accepted by official Solo with `0` LLM calls and `1` judge call; raw result at `tmp_stage2_smoke/2026-05-20-c9-hard3-0140-solo-result-after-guard.json`.
- Official `normal_100` zero-token smoke after the absorption cap: `74/100` in `56.6s`, no SIGTERM, `0` tokens. The pre-cap run hit the 600s wall limit and scored only `41/100` before termination.
- Route profiler evidence with the same cap: `normal_100` produced `74` deterministic candidates in `51.0s`; `sample_200` produced `169` deterministic candidates in `62.2s` without judge/LLM calls.
- Positive-token playground parity reached the LLM proxy paths: direct OpenRouter smokes passed, Solo recorded `llm_calls=2`, Marathon recorded `llm_calls=1` and `tokens_used=7208`. The parity gate is not promotion-clean because `hard3_0114` still failed by judge rejection / rejected LLM output.
- Packaged optimized solver syntax check passed.

## Key Lessons

1. The frontier is TRUE-heavy. Compact witness mining still helps, but the next material lift needs explicit TRUE proof extraction or judged LLM certificates.
2. `true:grind` was a discovery route, not a deployable strategy. It found `34` public TRUE wins but caused `433` incorrect attempts and failed the playground-error discipline, so it is retired from active solver policy.
3. Do not use zero-token Marathon as LLM evidence. It is only an optional deterministic append-only regression smoke.
4. Positive-token local LLM evidence must prove official proxy usage: nonzero Solo LLM calls, nonzero Marathon `llm_calls`, nonzero `tokens_used`, and classified missing-key/proxy/token/malformed/judge outcomes.
5. The vendored Solo harness still has local OpenRouter provider-normalization drift. Mention the exact local config before treating harness output as upstream-clean.

## Recommended Next Steps

1. Run broader no-loss validation for the `0.05s` absorption cap, especially hard TRUE closure fixtures and the full public sets.
2. Build the route-specific fixtures listed in `stage2/docs/solver-route-ledger.md` before attempting broad refactors.
3. Improve unresolved TRUE proof quality; the LLM proxy works, but the current targeted row still fails by judge rejection or solver rejection.
4. Run a full public no-loss validation when budget allows: `normal`, `hard1`, `hard2`, and `hard3` against the optimized packaged solver. Required deterministic baseline is at least the pre-rollback non-grind accepted set; broad grind wins are not part of active promotion.
5. Before upload or promotion, rerun `stage2/docs/playground-preflight.md` and the adversarial solver review checklist.

## Scratch Discipline

- `tmp_stage2_smoke/` is scratch. Promote only concise dated summaries under `stage2/results/`.
- Consult `stage2/docs/cleanup-manifest.md` before deleting or moving scratch artifacts; the 2026-05-19 polish pass is documentation-only for cleanup.
- Do not hardcode public benchmark ids in solver policy. The grind ledgers are regression fixtures only.
- Judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr, ledgers, or summaries.
