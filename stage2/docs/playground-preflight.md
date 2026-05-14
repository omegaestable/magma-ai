# Playground Preflight

Updated: 2026-05-13

Use this checklist before trying the packaged solver in the official Stage 2 playground or calling a local candidate playground-ready.

## Contract

The playground-facing artifact is the generated single file:

```text
stage2/submissions/solver.py
```

It must satisfy the official submission contract:

1. The submission directory contains exactly one file named `solver.py`.
2. `solver.py` is below the 500 KB limit.
3. The solver uses no repo-local imports and does not read repo-local caches.
4. The solver does not require local secrets or direct network access.
5. Judge answers contain exactly `verdict` and `code`; route labels stay in stderr and result summaries.
6. LLM escalation goes only through the official Solo or Marathon proxy.
7. Unsolved Solo runs send a terminal `{"call":"done"}` message before exiting, so the playground can distinguish a clean miss from a solver crash.

Current packaged state from the latest smoke pass: `52284` bytes, with `stage2/submissions/` containing only `solver.py`.

## Proxy Reality

Local no-key failures are not, by themselves, solver protocol failures.

In Solo mode, the solver sends:

```json
{"call":"llm","context":{"round":"0","analysis":"..."}}
```

The official proxy extracts the top-level `PROMPT` constant from `solver.py`, fills the prompt placeholders, calls the model, and returns a response. The solver never sees real API keys.

In Marathon mode, the runner injects `JUDGE_MARATHON_LIB_DIR`; the solver imports `marathon_llm` from that directory and calls `marathon_llm.call_llm` only when a token budget is available.

On a local machine, the proxy still needs one upstream key in the runner environment, usually `OPENAI_API_KEY` or `OPENROUTER_API_KEY`. If neither is set, unresolved cases can fail with:

```text
OPENAI_API_KEY or OPENROUTER_API_KEY not set
```

That means local LLM plumbing reached the proxy, but the local upstream credential was absent. In a playground that provides the organizer proxy, the submitted solver does not need its own key. If a playground disables LLM access, deterministic certificates still work and unresolved TRUE cases remain unsolved.

## Required Local Check

Run from the repository root in PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
.\.venv\Scripts\python.exe -m py_compile stage2\solver\solver.py stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe theory\tools\smoke_problem_sets.py
.\stage2\solver\package_solver.ps1
Get-ChildItem -Force stage2\submissions
(Get-Item stage2\submissions\solver.py).Length
```

Keep the package command after Python syntax/smoke commands. Running
`py_compile`, `compileall`, or tests against the generated submission path can
create `__pycache__`, and the official runner rejects extra submission entries.

Then run official smokes from `vendor/stage2-official/`:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor\stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_20.json --output ..\..\tmp_stage2_smoke\sample20_playground_preflight.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_200.json --output ..\..\tmp_stage2_smoke\sample200_playground_preflight.json
..\..\.venv\Scripts\python.exe scripts\run_marathon.py --solver ..\..\stage2\submissions --manifest examples\problems\marathon\normal_100.jsonl --budget-tokens 0
Pop-Location
```

Use explicit Solo output paths when recording smoke evidence. The runner's
default `pipeline/results/submissions.json` is easy to confuse with earlier
local smoke rows.

Optional focused LLM-path check when no local key is available:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor\stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems ..\..\tmp_stage2_smoke\hard3_true2.jsonl --output ..\..\tmp_stage2_smoke\hard3_true2_result.json
Pop-Location
```

Expected current behavior: `hard3_0001` is accepted deterministically by `true:projection:right`; `hard3_0002` reaches the LLM call path, fails locally without an upstream key, then emits `{"call":"done","reason":"no accepted certificate"}`. The vendored local proxy currently logs that terminal marker as an unknown call, while the playground uses it to avoid `SOLVER_ERROR` on clean misses.

## Ready Criteria

A candidate is playground-ready when:

1. `stage2/submissions/` contains only `solver.py`.
2. The packaged size is below 500 KB.
3. Syntax and local DSL smokes pass.
4. Official Solo samples run under the vendored runner.
5. Official Marathon zero-token smoke accepts deterministic submissions without rejected certificates.
6. Any LLM failure is clearly classified as either local missing-key setup or candidate protocol breakage.
7. Unsolved Solo paths emit the terminal `done` marker instead of silently exiting.
8. Public benchmark totals are not updated from smoke-only evidence.

For the current solver, deterministic playground readiness is green under this checklist. LLM success in the playground depends on the organizer proxy being enabled and configured, but the solver uses the documented proxy protocol.
