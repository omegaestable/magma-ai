# Latest Handoff

Updated: 2026-05-23

This is the short team-memory note for the current Stage 2 solver state. Use the result files for detailed evidence and `tmp_stage2_smoke/` only for raw artifacts.

## Current Solver Snapshot

- Active source: `stage2/solver/solver.py`.
- Packaged artifact: `stage2/submissions/solver.py`, last packaged at `112696` bytes.
- Submission directory should contain only `solver.py`.
- Historical public zero-token baseline: `1201/1669` from `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`, including `34` now-retired grind wins.
- Current durable May 21 summary: `stage2/results/2026-05-21-prune-refactor-and-fallback-reproduction.md`.
- Current durable May 23 route expansion summary: `stage2/results/2026-05-23-held-out-structural-route-expansion.md`.
- Full public validation after the grind rollback and May 21 refactor is still pending. Do not claim the current package preserves old grind-backed totals until a new full run exists.

## What Changed This Session

- Refactored duplicated bidirectional TRUE closure search into `_closure_route_impl`.
- Rebuilt `absorption_closure_route`, `deep_absorption_closure_route`, and `equational_closure_route` as thin wrappers over the shared helper.
- Preserved route order and timing constants, especially `ABSORPTION_TIME_BUDGET = 0.05`.
- Changed `fallback_true_certificate()` to return `reflexive_true_certificate()` instead of carrying duplicate Lean text.
- Packaged the solver and confirmed the source and packaged hashes matched after repackaging.
- Reproduced pasted public/evaluation fallback rows with a runner-equivalent direct probe and with official zero-token Marathon on the same 27-row manifest.
- Added six narrow deterministic TRUE route families from held-out structural motifs: `middle_self_collapse`, `square_twist_comm`, `front_double_self_collapse`, `alternating_front_self_collapse`, `mirrored_alternating_front_self_collapse`, and `sandwich_left_projection`.
- Preserved the local guided-chain LLM changes; Marathon raw TRUE remains disabled and deterministic certificates still run before LLM spending.

## Latest Regression Evidence

- Python syntax checks passed for source and packaged solver.
- Packaged size: `112696` bytes.
- Submission directory cleanliness: only `solver.py`.
- Route profile on public `normal_100` after the May 23 route expansion: `74` deterministic candidates, `26` skips, `47.479s`.
- Held-out hard first 80 after the May 23 route expansion: `76` deterministic candidates, `4` skips, `7.854s`.
- Official Solo harness on `sample_20`: exit `0`, no failing categories.
- Latest official zero-token Marathon on `normal_100` from the May 21 refactor package: `74/100`, `74` accepted, `26` not attempted, `0` tokens, `50.5s`.
- Analyzer agreed on that official `normal_100` run: `score=74`, gaps `{'true_template_gap': 26}`.
- Current May 23 package has profile guardrail evidence for `normal_100`; a fresh official `normal_100` Marathon run is still pending.

Focused official zero-token Marathon checks accepted these new held-out routes:

- `evaluation_hard_0004`: `true:middle_self_collapse`, `1/1`, `0` tokens.
- `evaluation_extra_hard_0034`: `true:square_twist_comm`, `1/1`, `0` tokens.
- `evaluation_hard_0010`: `true:front_double_self_collapse`, `1/1`, `0` tokens.
- `evaluation_hard_0026`: `true:alternating_front_self_collapse`, `1/1`, `0` tokens.
- `evaluation_hard_0052`: `true:mirrored_alternating_front_self_collapse`, `1/1`, `0` tokens.
- `evaluation_hard_0070`: `true:sandwich_left_projection`, `1/1`, `0` tokens.

Current held-out hard80 TRUE skips after this pass: `evaluation_hard_0072`, `evaluation_hard_0074`, `evaluation_hard_0078`, and `evaluation_hard_0080`.

## Selected-Row Reproduction

User-provided labels were normalized by removing the true/false label segment, for example `hard1_true_0065` -> `hard1_0065`.

- Public rows came from `vendor/stage2-official/examples/problems/`.
- Evaluation rows came from `data/hf_cache/`.
- Direct certificate verification used `verify_answer(_to_judge_problem(problem), raw_answer)`, not raw `verify_answer(problem, ...)`.

Broad 27-row direct probe:

- `evaluation_extra_hard_0045`, `evaluation_extra_hard_0043`, and `evaluation_extra_hard_0041` are now solved as `FALSE ACCEPTED` by `false:witness:S4C` in about 4-6 seconds.
- The other 24 listed rows reproduce Solo-style fallback behavior: submitted `TRUE`, judge `incorrect`, error code `LEAN_REJECTED`.
- Direct local timings for fallback rows were about 1.3-3.2 seconds because the probe bypassed live proxy waiting and checked the final fallback directly.

Official zero-token Marathon on the same manifest:

- Score: `3/27`.
- Attempted: `3`.
- Not attempted: `24`.
- Status split: `{'accepted': 3, 'not_attempted': 24}`.
- Wall time: `49.1s`.
- Tokens: `0`.
- Accepted route: `false:witness:S4C` for the three `evaluation_extra_hard_false_*` rows.

Scratch artifacts:

- `tmp_stage2_smoke/2026-05-21-fallback-batch-27.jsonl`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-direct-probe.py`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-direct-probe.jsonl`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-zero/summary.json`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-zero/run.log`

## Best Public Evidence

Latest completed official public zero-token Marathon refresh, before the final heartbeat/path-helper optimization patch and before grind retirement:

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

## Key Lessons

1. Generalize proof and witness families; do not add solver policy keyed to public or evaluation row ids.
2. Selected-row reproduction is useful for diagnosis, but promotion claims need full lanes or focused route fixtures with judge-accepted certificates.
3. Solo fallback `TRUE INCORRECT` rows and Marathon zero-token `not_attempted` rows are often the same unresolved deterministic gap viewed through different runner policies.
4. The three `evaluation_extra_hard_false_*` rows appear fixed in the current package. If they failed elsewhere, that evidence likely came from an older package or different upload.
5. `true:grind` was a discovery route, not a deployable strategy. It found `34` public TRUE wins but caused `433` incorrect attempts and is retired from active solver policy.
6. Do not use zero-token Marathon as LLM evidence. It is only deterministic append-only regression evidence.
7. Positive-token local LLM evidence must prove official proxy usage: nonzero Solo LLM calls, nonzero Marathon `llm_calls`, nonzero `tokens_used`, and classified failure outcomes.

## Recommended Next Steps

1. Continue held-out TRUE work one unseen structural family at a time; next hard80 row is `evaluation_hard_0072` (`eq1_id=86`, `eq2_id=1009`).
2. For extra-hard, first 120 rows are clean; inspect skips after row 120 from `tmp_stage2_smoke/2026-05-23-eval-extra-hard200-after-square-twist-profile.jsonl`.
3. Fix remaining fallback rows by adding reusable TRUE proof templates, finite witness families, or judged LLM certificate quality; do not special-case ids.
4. Run broader no-loss validation for the refactored closure helper and May 23 routes, especially hard TRUE closure fixtures and the full public sets.
5. Improve unresolved TRUE proof quality; the LLM proxy works, but current outputs are rejected by the solver or judge.
6. Run a full public no-loss validation when budget allows: `normal`, `hard1`, `hard2`, and `hard3` against the current packaged solver.
7. Before upload or promotion, rerun `stage2/docs/playground-preflight.md` and the adversarial solver review checklist.

## Scratch Discipline

- `tmp_stage2_smoke/` is scratch. Promote only concise dated summaries under `stage2/results/`.
- Consult `stage2/docs/cleanup-manifest.md` before deleting or moving scratch artifacts.
- Do not hardcode public benchmark ids in solver policy. Pasted row lists are regression fixtures and diagnostics only.
- Judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr, ledgers, or summaries.
