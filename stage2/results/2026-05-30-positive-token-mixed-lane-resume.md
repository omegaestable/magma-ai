# 2026-05-30 Positive-Token Mixed-Lane Resume

This is the durable summary for the post-interruption resume. No tokenless
Marathon validation was used in this pass; active guards now require a positive
token budget.

## Solver Changes

- Removed the unsafe broad/raw TRUE Marathon behavior from the active lane.
  Marathon TRUE LLM output must now be a solver-checked `rewrite_chain` or
  `guided_chain`.
- Kept Solo/debug raw TRUE support only for complete Lean `code` files with a
  visible `submission`; legacy `proof` / `proof_body` payloads reject locally.
- Changed the Marathon LLM prompt to a mixed checked-object prompt: TRUE chains
  or FALSE finite tables only. Bare false verdicts and invalid tables are
  rejected before judge submission.
- Fixed false-search deadline handling so `time_budget=0` really means no
  local profiling search. This prevents accidental unbounded witness mining in
  budgeted experiments.
- Replaced the legacy tokenless sweep/analyzer helpers with
  `stage2/experiments/run_positive_token_sweeps.py` and
  `stage2/experiments/analyze_marathon_run.py`.

## Validation

- `py_compile`: passed for `stage2/solver/solver.py` and changed experiment
  helpers.
- `stage2/experiments/smoke_llm_dsl.py`: passed.
- `theory/tools/smoke_problem_sets.py`: passed.
- `stage2/solver/package_solver.ps1`: produced
  `stage2/submissions/solver.py` at `138939` bytes.
- Submission directory check: `stage2/submissions/` contained only `solver.py`.
- Direct deadline sanity check: `find_counterexample(..., time_budget=0)` on a
  hard false row returned `None` after the fix.

## Positive-Token Runs

`normal_100` guardrail, Lean on PATH:

- Output dir: `tmp_stage2_smoke/2026-05-30-normal100-positive-after-true-trim-leanpath`
- Score: `75/100`
- Accepted: `75`
- Not attempted: `25`
- LLM calls: `25`
- Tokens used: `47419`
- Incorrect submissions: `0`

`hard1` mixed-lane run:

- Output dir: `tmp_stage2_smoke/2026-05-30-hard1-positive-mixed-llm`
- Score: `39/69`
- Accepted: `39`
- Not attempted: `30`
- LLM calls: `30`
- Tokens used: `240164`
- Incorrect submissions: `0`

## Lessons

The mixed prompt is safer and broader, but it did not yet produce an accepted
LLM certificate. TRUE failures are still dominated by unsupported guided-chain
edges and malformed/prose output. FALSE table proposals reached the local
checker, but the observed tables did not actually separate hypothesis from
goal. The next improvement should promote only a reconstructable proof or a
checked finite-witness family, not row-id policy.
