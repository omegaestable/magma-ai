# 2026-05-27 Deep Public TRUE Proof Mining

## Summary

Focused on public `hard1|hard2|hard3` TRUE gaps from the May 26 hard sweep. The session produced one promoted deterministic TRUE motif and no accepted LLM-generated proof candidates.

- New route: `true:left_row_constancy`.
- Accepted public rows: `hard3_0284`, `hard3_0285`.
- Focused official zero-token Marathon: `2/2` accepted, `0` tokens.
- Full selected 17-row public TRUE fixture after route: `2/17` accepted, `0` tokens.
- Guardrail: public `normal_100` stayed `74/100`, `0` tokens.
- Packaged solver after patch: `119994` bytes.

## LLM Proof-Mining Runs

Both LLM runs used scratch submission copies through the official Marathon proxy. No local key or network dependency was added to the real solver.

First pass, standard prompt with session knobs:

- Fixture: `tmp_stage2_smoke/2026-05-27-public-true-proof-mining-fixture.jsonl`.
- Scratch submission: `tmp_stage2_smoke/2026-05-27-public-true-proof-mining-submission/`.
- Config overrides in scratch only: `MARATHON_LLM_MAX_CALLS=32`, `LLM_MAX_OUTPUT_TOKENS=12288`.
- Observed: `16` LLM calls, `98942` tokens.
- Rejections: `12` bad false tables, `2` unproved guided chains, `1` chain parse failure, `1` timeout.
- Accepted LLM candidates: `0`.
- Scoring hit a local `lake env` timeout after solver exit, but logs and candidate output were preserved.

Second pass, TRUE-only prompt repair:

- Scratch submission: `tmp_stage2_smoke/2026-05-27-public-true-proof-mining-submission-trueonly/`.
- Observed: `16` LLM calls, `62611` tokens.
- Rejections: `13` unproved guided chains, `2` chain parse failures, `1` timeout.
- Accepted LLM candidates: `0`.
- Official Marathon scoring completed: `1/17`, from deterministic `hard3_0284` only in the scratch copy.

Total LLM spend in this session: `32` calls and `161553` observed tokens, below the `250k` cap.

## Promoted Motif

For a hypothesis of shape

```text
r = ((r ◇ p) ◇ (p ◇ q)) ◇ s
```

derive row constancy:

```lean
have hrow : ∀ a b c : G, a ◇ b = a ◇ c := by
  intro a b c
  exact (hsrc (a ◇ b) (b ◇ a) a c).trans
    (congrArg (fun t => t ◇ c) (hsrc a b a ((b ◇ a) ◇ a))).symm
```

The solver then recursively proves goals whose two sides have the same left-row skeleton. This covers:

- `hard3_0284`: `x ◇ x = x ◇ ((y ◇ x) ◇ y)`.
- `hard3_0285`: `x ◇ y = x ◇ ((x ◇ z) ◇ z)`.

Corpus scan over public `normal`, `hard1`, `hard2`, and `hard3` found only these two hits, both TRUE.

## Evidence

Preflight:

- `py_compile` passed for `stage2/solver/solver.py` and `stage2/experiments/smoke_llm_dsl.py`.
- `stage2/experiments/smoke_llm_dsl.py` passed.
- `theory/tools/smoke_problem_sets.py` passed.
- Submission directory contained only `solver.py`.

Focused validation:

- `tmp_stage2_smoke/2026-05-27-left-row-constancy-public2-zero/summary.json`: `2/2`, `0` tokens.
- `tmp_stage2_smoke/2026-05-27-public-true-proof-mining-after-left-row-zero/summary.json`: `2/17`, `0` tokens.
- `tmp_stage2_smoke/2026-05-27-normal100-after-left-row-zero/summary.json`: `74/100`, `0` tokens.

Docs updated:

- `stage2/docs/solver-route-ledger.md`.
- `stage2/docs/motif-cards/true-basic-rewrites.md`.

## Next Work

The LLM failure mode is now clearer: the model can be steered away from FALSE tables, but it mostly emits tiny unprovable guided chains. The next useful prompt/DSL repair is to request derived lemmas explicitly, then parse lemma-shaped outputs into solver-owned proof templates instead of only endpoint chains.
