# 2026-05-26 LLM-Backed Hard TRUE Push

## Summary

Ran a real positive-token public hard sweep through the official Marathon proxy path with compression ratio `0.5`.

- Direct OpenRouter smoke passed with nonzero usage: `total_tokens=74`.
- Full hard sweep artifacts are under `tmp_stage2_smoke/playground_public_sweeps/2026-05-26-hard-public-llm-sweep/`.
- Read-only log classification gives `365/669` accepted, with `49` TRUE and `316` FALSE accepted.
- The sweep used `72` LLM calls and `359653` tokens across `hard1`, `hard2`, and `hard3`.
- No LLM candidate was accepted by the solver. All accepted rows in this sweep were deterministic.
- No generalized TRUE proof-family was promoted from LLM output because the LLM did not produce a judge-accepted proof candidate.

## Preflight

- `py_compile` passed for `stage2/solver/solver.py` and `stage2/experiments/smoke_llm_dsl.py`.
- `stage2/experiments/smoke_llm_dsl.py` passed with `fake_llm_dsl_smoke_ok`.
- `stage2/solver/package_solver.ps1` packaged `stage2/submissions/solver.py`.
- `stage2/submissions/` contained only `solver.py`.
- `stage2/experiments/homelab_llm_probe.py --key-status` found a configured key with expected shape, without printing the secret.
- `stage2/experiments/homelab_llm_probe.py --run-direct-openrouter-smoke` passed all three request shapes.

## Full Hard Sweep

Command:

```powershell
stage2/experiments/run_playground_public_sweeps.py --only hard1 hard2 hard3 --compression-ratio 0.5 --output-dir tmp_stage2_smoke/playground_public_sweeps/2026-05-26-hard-public-llm-sweep --keep-output
```

| Dataset | Accepted | TRUE accepted | FALSE accepted | Not attempted | LLM calls | Tokens | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `hard1` | `39/69` | `3` | `36` | `30` | `24` | `117795` | completed |
| `hard2` | `84/200` | `5` | `79` | `116` | `24` | `95732` | completed |
| `hard3` | `242/400` | `41` | `201` | `158` | `24` | `146126` | completed in log; summary parser artifact noted below |
| Total | `365/669` | `49` | `316` | `304` | `72` | `359653` | positive-token sweep |

The combined sweep summary initially marked `hard3` as `failed_llm_requirement` with `llm_calls=0`. Direct `run.log` parsing showed this was a reporting artifact: the solver's final Marathon summary stderr line was too long and was truncated by the runner's stderr buffer before the sweep helper parsed it. The log still contained `llm:batch_start` records and nonzero token usage for `hard3`.

## Gap Classification

Accepted deterministic:

- `49` TRUE rows.
- `316` FALSE rows.

Accepted LLM:

- `0`.

LLM rejected by solver parser or candidate checks:

- `67` rejected candidates.
- `35` `false_table_not_counterexample`.
- `21` `no_json_object`.
- `9` `guided_chain_unproved_or_bad_endpoints`.
- `2` `rewrite_chain_parse_failed`.

LLM transport/runtime errors:

- `5` `LLM request timed out (45s)`.

Not attempted or remaining gaps:

- `270` `true_template_gap`.
- `34` `finite_countermodel_gap`.
- `304` total not attempted rows across the hard sweep.

## Solver Patch

Patched `stage2/solver/solver.py` to keep Marathon stderr summaries parseable on large hard runs:

- Added chunked route-count logging as `{"route":"route_counts","routes":...}` records.
- Removed the large `routes` map from the final `marathon_summary` JSON line.
- Kept the final summary compact with `submitted_total`, `submitted_deterministic`, `llm_calls`, budget fields, and route-count metadata.

This patch is reporting-only. It does not re-enable broad `true:grind`, change answer payload shape, or add benchmark-id policy.

## Validation After Patch

Repackaged solver:

- `stage2/submissions/solver.py`
- size after patch: `117271` bytes

Positive-token hard fixture:

- Fixture: `tmp_stage2_smoke/2026-05-26-hard3-llm-summary-fixture.jsonl`
- Output: `tmp_stage2_smoke/2026-05-26-hard3-summary-fix-positive-marathon/`
- Result: `2/6`, `tokens_used=19806`, `llm_calls=4`.
- Parsed stderr records cleanly: `parse_errors=0`.
- Final summary JSON length: `222`.

Zero-token regression:

- Output: `tmp_stage2_smoke/2026-05-26-normal100-after-summary-fix-zero/`
- Result: `normal_100 = 74/100`, `tokens_used=0`, `not_attempted=26`.

## Artifacts

- Full sweep summary JSON: `tmp_stage2_smoke/playground_public_sweeps/2026-05-26-hard-public-llm-sweep/playground_public_sweep_summary.json`
- Full sweep summary Markdown: `tmp_stage2_smoke/playground_public_sweeps/2026-05-26-hard-public-llm-sweep/playground_public_sweep_summary.md`
- Hard fixture validation: `tmp_stage2_smoke/2026-05-26-hard3-summary-fix-positive-marathon/run.log`
- Zero-token regression: `tmp_stage2_smoke/2026-05-26-normal100-after-summary-fix-zero/run.log`

## Next Work

The biggest immediate blocker is LLM proof quality rather than Lean template promotion. The next iteration should focus on improving the TRUE proof DSL/prompt and adding candidate self-checks before submission, then rerun a smaller positive-token hard slice to look for accepted LLM proofs worth mining into structural deterministic routes.
