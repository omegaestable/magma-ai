# 2026-05-30 Evaluation Normal TRUE-Lane LLM Session

`evaluation_normal` is analysis-only discovery data. These runs are not public
promotion evidence.

## Fixture

- Source: `data/hf_cache/evaluation_normal.jsonl`
- Helper: `stage2/experiments/build_eval_normal_true_lane.py`
- Manifest: `tmp_stage2_smoke/2026-05-30-eval-normal-true100.jsonl`
- Ledger: `tmp_stage2_smoke/2026-05-30-eval-normal-true100-ledger.jsonl`
- Meta: `tmp_stage2_smoke/2026-05-30-eval-normal-true100-meta.json`
- Selected rows: `100/100` TRUE rows
- Deterministic skips in selected rows: `67`

## Solver Changes

- TRUE-lane LLM prompt now forbids false verdicts and finite-table guessing.
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

### Zero-Token TRUE100 Baseline

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
  tokens. The prompt moved the model from false verdicts to TRUE chains, but
  all chains were unsupported by solver-owned proof checks.
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

## Required Guardrails After Patch

- TRUE100 zero-token rerun:
  - Output dir: `tmp_stage2_smoke/2026-05-30-eval-normal-true100-zero-after-patches`
  - Score: `33/100`
  - Tokens: `0`
- Official `normal_100` zero-token guardrail:
  - Output dir: `tmp_stage2_smoke/2026-05-30-normal100-zero-after-true-lane-patches`
  - Score: `75/100`
  - Tokens: `0`

## Interpretation

The session improved the LLM lane mechanics and telemetry, not the accepted
score. The important learning is that the model can be steered away from false
answers, but its TRUE chains are mostly proof sketches with unsupported jumps.
The next useful TRUE lane session should mine the recurring unsupported edge
families for one independently reconstructable local lemma before widening any
deterministic certificate route.
