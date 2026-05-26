# Motif Card: LLM Proxy DSL

Updated: 2026-05-19

## Scope

Routes covered: Solo LLM proxy, Marathon LLM proxy, `llm:true:rewrite_chain`, `llm:true:raw_code`, and `llm:false:table`.

## Principle

The submitted solver may use only the official proxy interfaces. It must not carry local secrets, make direct OpenRouter/OpenAI calls, or rely on repo-local imports. LLM output is treated as an untrusted proposal and must be checked or sanitized before it reaches the judge.

## Accepted JSON Shapes

```json
{"verdict":"true","proof_kind":"rewrite_chain","chain":["<goal lhs>","<middle>","<goal rhs>"]}
```

```json
{"verdict":"true","code":"import JudgeProblem\n\ndef submission : Goal := by\n  ..."}
```

```json
{"verdict":"false","counterexample_table":[[0,1],[1,0]]}
```

## Validation Rules

- Rewrite chains must parse and each adjacent step must be proved by solver-owned rewrite logic.
- Raw Lean must pass `sanitize_lean_code`: allowed imports, `submission` definition, size limits, no banned tokens, no Teorth theorem names.
- Raw Lean means a complete `Submission.lean` file; helper declarations above `submission` are allowed.
- Finite tables must be normalized and checked by `table_is_counterexample` before emission.

## Proxy Paths

- Solo: solver sends `{"call":"llm","context":...}` to stdout and receives a proxy response on stdin.
- Marathon: runner injects `JUDGE_MARATHON_LIB_DIR`; solver imports `marathon_llm.call_llm` and relies on official budget accounting.
- Positive-token evidence must show nonzero LLM calls and nonzero Marathon `tokens_used`.

## Evidence

- `stage2/experiments/smoke_llm_dsl.py` checks parser/sanitizer behavior without network calls.
- `stage2/experiments/run_playground_parity_llm.py` is the preferred positive-token local parity gate.
- Historical proxy transport smoke showed Solo and Marathon `1/1`, but transport-only evidence is not proof-quality evidence.

## Limits

- Raw Lean fallback is useful but riskier than solver-checked DSL forms.
- Missing local `OPENROUTER_API_KEY` is local setup/proxy evidence, not a submitted-solver protocol failure.
- Broad public positive-token sweeps should wait until targeted unresolved TRUE rows are understood.

## Regression Needs

- No-network DSL parser smoke.
- Positive-token parity run.
- Targeted unresolved TRUE run with status classification.
- Secret scan for `sk-or-v1-` shaped material before handoff.
