# 2026-05-30 Evaluation Normal TRUE-Lane LLM Session

`evaluation_normal` is analysis-only discovery data. These runs are not public
promotion evidence.

Policy update after this session: active repo validation now forbids
`--budget-tokens 0` Marathon guardrails. Historical no-LLM numbers below are
kept only to explain what happened during the session; future reruns must use
positive token budgets and record proxy outcomes.

## Fixture

- Source: `data/hf_cache/evaluation_normal.jsonl`
- Helper: `stage2/experiments/build_eval_normal_true_lane.py`
- Manifest: `tmp_stage2_smoke/2026-05-30-eval-normal-true100.jsonl`
- Ledger: `tmp_stage2_smoke/2026-05-30-eval-normal-true100-ledger.jsonl`
- Meta: `tmp_stage2_smoke/2026-05-30-eval-normal-true100-meta.json`
- Selected rows: `100/100` TRUE rows
- Deterministic skips in selected rows: `67`

## Solver Changes

- The first TRUE-lane LLM prompt forbade false verdicts and finite-table guessing; the resumed mixed-lane prompt now permits FALSE only as a solver-verified table.
- Prompt asks for concrete rewrite or guided-chain proof attempts and includes
  bounded middle-term hints from goal/hypothesis subterms plus one-step rewrites.
- LLM guided-chain validation now uses wider LLM-only bounds than deterministic
  closure routes.
- LLM reject logging now includes response previews for every reject class.
- Bare `{"verdict":"false"}` is logged as `false_verdict_without_table`.
- TRUE chains now get a precise `rewrite_chain_uses_non_goal_variables` reject
  when the model introduces variables that are not in the goal context.
- Full-reference Marathon token budgets now allow up to one LLM call per
  manifest row; compressed/default budgets keep the conservative call cap.

No deterministic TRUE motif was promoted. The LLM run did not produce an
accepted or reconstructable proof template.

## Preflight

- `py_compile`: passed for solver and experiment helpers.
- `stage2/experiments/smoke_llm_dsl.py`: passed.
- `theory/tools/smoke_problem_sets.py`: passed; confirmed `evaluation_normal`
  is `200` rows with `100` TRUE and `100` FALSE.
- `stage2/solver/package_solver.ps1`: packaged `stage2/submissions/solver.py`.
- Submission cleanliness: `stage2/submissions/` contains only `solver.py`.
- Final packaged size: `140847` bytes.
- Local proxy key shape check: key present, hidden, no whitespace, expected
  `sk-`/`sk-or-v1-` shape.

## Runs

### Archived Deterministic TRUE100 Baseline

- Output dir: `tmp_stage2_smoke/2026-05-30-eval-normal-true100-zero`
- Score: `33/100`
- Attempted: `33`
- Not attempted: `67`
- Tokens: `0`

### First Full-Reference LLM TRUE100

- Output dir: `tmp_stage2_smoke/2026-05-30-eval-normal-true100-llm`
- Score: `33/100`
- Attempted: `33`
- Not attempted: `67`
- Tokens: `104315`
- LLM calls: `64`
- Reject lesson: all `64` LLM proposals were `false_table_invalid_shape`;
  previews showed almost all responses were bare `{"verdict":"false"}`.

### Small Positive-Token Probes After Prompt Patches

- `tmp_stage2_smoke/2026-05-30-true4-after-prompt-llm`: `0/4`, `9083`
  tokens. The first prompt moved the model from false verdicts to TRUE chains,
  but all chains were unsupported by solver-owned proof checks.
- `tmp_stage2_smoke/2026-05-30-true4-after-variable-discipline-llm`: `0/4`,
  `10229` tokens. Variable-discipline telemetry isolated fresh-variable chain
  errors from unsupported proof edges.

### Post-Patch Full-Reference LLM TRUE100

- Output dir: `tmp_stage2_smoke/2026-05-30-eval-normal-true100-llm-after-patches`
- Score: `33/100`
- Attempted: `33`
- Not attempted: `67`
- Tokens: `179936`
- LLM calls: `67`
- Logged call cap: `100`
- Reject mix:
  - `guided_chain_unproved_or_bad_endpoints`: `56`
  - `rewrite_chain_uses_non_goal_variables`: `9`
  - `no_chain_supplied`: `1`
  - `no_json_object`: `1`

The official proxy emitted intermittent `ConnectionAbortedError [WinError
10053]` traces after some completed runs. The runner summaries were written and
the solver exited `rc=0`; treat this as proxy teardown noise unless it appears
before a missing summary.

## Required Guardrails After Policy Update

- TRUE red-flag positive-token official Marathon after trimming raw/grind TRUE behavior:
  - Output dir: `tmp_stage2_smoke/2026-05-30-true-redflags-llm-after-trim`
  - Score: `2/13`
  - Accepted: `2`
  - Not attempted: `11`
  - LLM calls: `11`
  - Tokens: `22764`
  - Incorrect submissions: `0`
  - Reject lesson: the dominant class stayed `guided_chain_unproved_or_bad_endpoints`; one response used non-goal variables. No raw TRUE Lean was submitted from Marathon.
- Official `normal_100` positive-token Marathon guardrail:
  - Output dir: `tmp_stage2_smoke/2026-05-30-normal100-positive-after-true-trim-leanpath`
  - Score: `75/100`
  - Accepted: `75`
  - Not attempted: `25`
  - LLM calls: `25`
  - Tokens: `47419`
  - Incorrect submissions: `0`
  - Environment note: a prior run without the Elan bin on `PATH` produced `harness_error` rows for every submitted answer because the judge could not find `lean`; do not use that run as solver evidence.
- Official `hard1` positive-token mixed-lane Marathon after resuming with both TRUE and FALSE enabled:
  - Output dir: `tmp_stage2_smoke/2026-05-30-hard1-positive-mixed-llm`
  - Score: `39/69`
  - Accepted: `39`
  - Not attempted: `30`
  - LLM calls: `30`
  - Tokens: `240164`
  - Incorrect submissions: `0`
  - Reject lesson: mixed prompting caused the model to try finite tables, but local table checking rejected them as non-counterexamples. TRUE proposals still mostly failed as unsupported guided-chain edges or malformed/prose responses; several rows timed out at the proxy.

## Interpretation

The session improved the LLM lane mechanics and telemetry, not the accepted
score. The important learning is that the model can be steered away from false
answers, but its TRUE chains are mostly proof sketches with unsupported jumps.
The next useful TRUE lane session should mine the recurring unsupported edge
families for one independently reconstructable local lemma before widening any
deterministic certificate route.
