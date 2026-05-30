# Motif Card: LLM Proxy DSL

Updated: 2026-05-30

## Scope

Routes covered: Solo LLM proxy, Marathon LLM proxy, `llm:true:rewrite_chain`, `llm:true:guided_chain`, Solo/debug-only `llm:true:raw_code`, and `llm:false:table`.

## Principle

The submitted solver may use only the official proxy interfaces. It must not carry local secrets, make direct OpenRouter/OpenAI calls, or rely on repo-local imports. LLM output is treated as an untrusted proposal and must be checked or sanitized before it reaches the judge.

## Accepted JSON Shapes

```json
{"verdict":"true","proof_kind":"rewrite_chain","chain":["<goal lhs>","<middle>","<goal rhs>"]}
```

```json
{"verdict":"true","proof_kind":"guided_chain","chain":["<goal lhs>","<middle>","<goal rhs>"],"lemmas":["optional sketch"]}
```

```json
{"verdict":"true","code":"import JudgeProblem\n\ndef submission : Goal := by\n  ..."}
```

```json
{"verdict":"false","counterexample_table":[[0,1],[1,0]]}
```

## Validation Rules

- Rewrite chains must parse and each adjacent step must be proved by solver-owned rewrite logic.
- Guided chains use the same endpoint and goal-variable checks, then allow a slightly wider solver-owned closure check per adjacent edge.
- TRUE chain terms may use only goal variables; extra hypothesis variables must be instantiated before the chain is written.
- Marathon TRUE LLM submissions disable raw Lean and must be solver-checked chains.
- Raw Lean, where used by Solo/debug tooling, must pass `sanitize_lean_code`: allowed imports, `submission` definition, size limits, no banned tokens, no Teorth theorem names.
- Raw Lean means a complete `Submission.lean` file; helper declarations above `submission` are allowed in that Solo/debug rail.
- Finite tables must be normalized and checked by `table_is_counterexample` before emission.
- The mixed Marathon prompt permits verified FALSE finite tables, but bare false verdicts and invalid tables are rejected before judge submission.

## Proxy Paths

- Solo: solver sends `{"call":"llm","context":...}` to stdout and receives a proxy response on stdin.
- Marathon: runner injects `JUDGE_MARATHON_LIB_DIR`; solver imports `marathon_llm.call_llm` and relies on official budget accounting.
- Positive-token evidence must show nonzero LLM calls and nonzero Marathon `tokens_used`; `--budget-tokens 0` Marathon validation is banned for active repo gates.
- Full-reference token budgets allow up to one Marathon LLM call per manifest row; compressed/default budgets retain the conservative cap.

## Evidence

- `stage2/experiments/smoke_llm_dsl.py` checks parser/sanitizer behavior without network calls.
- `stage2/experiments/run_playground_parity_llm.py` is the preferred positive-token local parity gate.
- Historical proxy transport smoke showed Solo and Marathon `1/1`, but transport-only evidence is not proof-quality evidence.
- 2026-05-30 analysis-only `evaluation_normal` TRUE100 full-reference proxy run: `33/100`, `67` LLM calls, `179936` tokens, `0` LLM-accepted certificates. Reject mix: `56` unsupported guided-chain edges, `9` non-goal-variable chains, `1` empty TRUE verdict, `1` malformed JSON.
- 2026-05-30 TRUE red-flag positive-token run after raw/grind TRUE trim: `2/13`, `11` LLM calls, `22764` tokens, and `0` incorrect submissions. Remaining proposals were rejected before judge submission.
- 2026-05-30 official `normal_100` positive-token guardrail: `75/100`, `25` LLM calls, `47419` tokens, and `0` incorrect submissions.
- 2026-05-30 official `hard1` positive-token mixed-lane run: `39/69`, `30` LLM calls, `240164` tokens, and `0` incorrect submissions. FALSE table proposals reached the local checker but were rejected as non-counterexamples; TRUE proposals remained unsupported chain sketches or malformed/prose output.

## Limits

- Raw Lean fallback is useful for Solo/debug experiments but is disabled in the Marathon TRUE lane.
- Missing local `OPENROUTER_API_KEY` is local setup/proxy evidence, not a submitted-solver protocol failure.
- Broad public positive-token sweeps should wait until targeted unresolved TRUE rows produce at least one reconstructable proof motif.
- Do not promote a deterministic TRUE route from LLM sketches unless the chain or Lean proof is accepted or independently reconstructed.

## Regression Needs

- No-network DSL parser smoke.
- Positive-token parity run.
- Targeted unresolved TRUE run with status classification.
- Secret scan for `sk-or-v1-` shaped material before handoff.
