# Latest Handoff

Updated: 2026-05-14

This is the compressed team-memory note for the current Stage 2 solver state.

## What Changed

- The solver now has two new deterministic levers:
  - expanded linear/affine FALSE search over sizes `2,3,4,5,7,8,9`
  - bounded TRUE proof search via `true:absorption_closure`
- Quadratic search intentionally stays on the tighter older size policy to avoid a broad runtime jump.
- `true:absorption_closure` triggers only on non-singleton absorption hypotheses such as `x = T` or `T = x` where `x` occurs inside `T`. It reconstructs Lean with instantiated `h`, `congrArg`, `.trans`, and `.symm`.
- The answer payload contract is unchanged: submitted answers contain exactly `verdict` and `code`; route labels remain in stderr/logs.
- Packaged solver size is now `60614` bytes, still far below the 500 KB cap.

## Best Public Evidence

Canonical full public benchmark evidence still remains the 2026-05-12 generated run because `normal` has not been rerun after the 2026-05-14 patch:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`, `llm:0`
- `normal`: `743/1000` solved, `245 TRUE + 498 FALSE`, `llm:0`
- `hard1`: `17/69` solved, all `FALSE`, `llm:0`
- `hard2`: `52/200` solved, all `FALSE`, `llm:0`
- `hard3`: `186/400` solved, `3 TRUE + 183 FALSE`, `llm:0`

Public total remains `998/1669` until `normal|hard1|hard2|hard3` are refreshed together.

Latest 2026-05-14 local runner-equivalent evidence:

- composite-affine focused fixture: `14/14` accepted
- same 150-row hard mix, seed `20260514`: `73/150`, up from `68/150`
- hard-mix deltas: 2 TRUE wins via `true:absorption_closure`, 3 FALSE wins via expanded affine/linear search, no regressions
- `sample_20`: `14/20`, unchanged
- `sample_200`: `165/200`, unchanged
- full hard-only reruns:
  - `hard1`: `24/69`, up from `17/69`
  - `hard2`: `64/200`, up from `52/200`
  - `hard3`: `211/400`, up from `186/400`
- combined hard-only status after the patch: `299/669`, with `27/319` TRUE and `272/350` FALSE
- hard-only remaining misses: `292` TRUE and `78` FALSE

## Highest-Value Learnings

1. Expanded composite affine search is validated and low risk. It closed all 14 known public composite-affine candidates in the focused fixture.
2. `true:absorption_closure` is real, not speculative: it produced accepted official-runner certificates on hard TRUE rows.
3. The hard frontier is still TRUE-heavy. The next solver work should extend absorption/projection proof search before chasing broad brute-force finite search.
4. The current absorption graph is deliberately bounded. It should skip silently when it cannot certify the goal rather than emit speculative Lean.
5. Local no-key LLM failures still mean the runner proxy lacks `OPENAI_API_KEY` or `OPENROUTER_API_KEY`; they are setup noise if deterministic paths and final judge-call behavior remain clean.
6. Runner-equivalent certificate debugging should use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`, not direct `verify_answer(problem, ...)`.

## Operational Cautions

1. Do not update canonical public totals from the 2026-05-14 hard-only evidence. Rerun `normal` too.
2. `tmp_stage2_smoke/` is local scratch space. The 2026-05-14 hard-only run is summarized in `stage2/results/2026-05-14-hard-affine-absorption-summary.md`.
3. The official judge answer JSON must contain exactly `verdict` and `code`.
4. The current packaged solver is `60614` bytes, with `stage2/submissions/` containing only `solver.py`.
5. The official docs still disagree on Marathon wall-clock reference: `docs/marathon_mode.md` uses `600 s/problem`, while `rules/evaluation.md` describes `3600 s/problem`-derived budgeting. Keep local tests parameterized.
6. The imported Hugging Face `evaluation_*` subsets remain analysis-only until explicitly promoted into an official workflow.
7. Custom local Solo knobs may be stripped by the official proxy environment. Treat proxy/runner behavior as authoritative.

## Playground Readiness

Use `stage2/docs/playground-preflight.md` before upload or playground checks. The current packaged solver is deterministic-ready under the official single-file and proxy contracts: `stage2/submissions/` contains only `solver.py`, the file is below the 500 KB cap, deterministic certificates have official runner evidence, and unresolved cases use the proxy LLM protocol. Full LLM success still depends on the playground proxy being enabled and configured.

## Recommended Next Steps

1. Extend the absorption/projection TRUE proof graph with focused fixtures first, then run the hard mix again.
2. Use `stage2/results/2026-05-14-hard-affine-absorption-summary.md` as the durable local note for the hard-only patch evidence.
3. Rerun the full public suite, including `normal`, before updating canonical public totals.
4. Mine remaining hard FALSE gaps for reusable formulaic families, but prefer validated families over brute-force bound increases.
5. Rerun official harnesses before calling the upgraded solver a promotion candidate.

Useful refresh skeleton:

```powershell
$env:PYTHONUTF8='1'
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
.\stage2\solver\package_solver.ps1
Push-Location vendor\stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\normal.jsonl --output ..\..\stage2\results\YYYY-MM-DD-normal.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\hard1.jsonl --output ..\..\stage2\results\YYYY-MM-DD-hard1.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\hard2.jsonl --output ..\..\stage2\results\YYYY-MM-DD-hard2.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\hard3.jsonl --output ..\..\stage2\results\YYYY-MM-DD-hard3.json
Pop-Location
```
