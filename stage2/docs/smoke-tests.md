# Stage 2 Smoke Tests

Last smoke run: 2026-05-13.

## Passing Locally

PowerShell with `.venv` Python 3.14.3:

```powershell
.\.venv\Scripts\python.exe -m py_compile stage2\solver\solver.py stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe theory\tools\smoke_problem_sets.py
.\stage2\solver\package_solver.ps1
```

Observed:

- Packaged `stage2/submissions/solver.py` at 52098 bytes.
- `stage2/submissions/` must contain only `solver.py`; the official Solo runner rejects `.gitkeep`, `__pycache__`, and any other extra entries before executing the solver.
- Run the package command last before official runner invocations. `compileall stage2` can create bytecode caches under generated submission paths.
- `smoke_llm_dsl.py` exercises fake LLM DSL parsing without network or model calls.
- `smoke_problem_sets.py` verifies the official mirrors and analysis-only problem-set policy.

## Official Solo Runner Probes

Command shape from `vendor/stage2-official/`:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_20.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_200.json
Pop-Location
```

Observed after cleaning and packaging `stage2/submissions/`:

- Runner launches the packaged local solver.
- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`. In the current no-key local run, the 6 unresolved TRUE rows each made one LLM call and failed with `OPENAI_API_KEY or OPENROUTER_API_KEY not set`.
- `sample_200`: `165/200` solved, with all remaining `35` misses classified as TRUE gaps.
- Targeted FALSE fixtures for `false_907_2534`, `false_1682_411`, and `false_3145_3481` are accepted by the official runner after the recent fixes.
- Packaged solver remains 52098 bytes and the submission directory contains only `solver.py`.

Recent certificate lessons:

- `false_907_2534` exposed a Lean recursion-depth failure for a `Fin 7` witness. Emitting `set_option maxRecDepth 20000` before `decideFin!` fixed the official-runner failure.
- `false_1682_411` and `false_3145_3481` needed larger named compact witnesses (`S5A` and `S4A`) and a named-witness cap independent of the bounded brute-force search cap.
- Direct `verify_answer(problem, ...)` is not runner-equivalent. Use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)` when debugging certificates inside the harness.

Protocol note:

- Current `pipeline/proxy.py` and the official Solo demo solvers use `{"call":"judge","verdict":...,"code":...}` and finish when the judge accepts.
- `docs/solo_mode.md` also describes a terminal `type: submit` shape. Treat the proxy and examples as the executable truth for this harness snapshot unless upstream changes the proxy.

## Native Windows Lean Setup

Installed and validated locally:

- Elan: `4.2.1`
- Lean: `4.30.0-rc2`, `x86_64-w64-windows-gnu`
- Lake: `5.0.0-src+3dc1a08`

Setup commands:

```powershell
winget install --id Lean.Elan -e --accept-source-agreements --accept-package-agreements
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
elan toolchain install leanprover/lean4:v4.30.0-rc2
elan default leanprover/lean4:v4.30.0-rc2
Push-Location vendor/stage2-official
lake update
lake exe cache get
lake build JudgeMagma.Magma JudgeDecide.DecideBang JudgeFinOp.MemoFinOp JudgeSupport.Inspect
Pop-Location
```

Official harness evidence on native Windows, after local patches documented in `vendor/stage2-official/UPSTREAM.md`:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor/stage2-official
c:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe scripts/run_harness.py
c:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe scripts/run_marathon_harness.py
Pop-Location
```

Observed:

- Solo/Lean harness: no failing buckets; 66/66 judge cases, 79/79 public attacks, 55/55 pipeline regressions.
- Marathon harness: 25/25 passed with Lean available.

## Marathon Smoke

Command shape from `vendor/stage2-official/`:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe scripts\run_marathon.py --solver ..\..\stage2\submissions --manifest examples\problems\marathon\normal_100.jsonl --budget-tokens 0
Pop-Location
```

Observed:

- `normal_100`: `70/100` accepted with zero token budget.
- All attempted certificates were accepted.
- Treat this as pacing/smoke evidence, not a replacement for the full `normal.jsonl` benchmark.

## Focused Hard3 TRUE Probe

Command shape from `vendor/stage2-official/` against `tmp_stage2_smoke/hard3_true2.jsonl`:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems ..\..\tmp_stage2_smoke\hard3_true2.jsonl --output ..\..\tmp_stage2_smoke\hard3_true2_result.json
Pop-Location
```

Observed:

- `hard3_0001`: accepted as TRUE via `true:projection:right`, `llm:0`, `judge:1`.
- `hard3_0002`: unresolved deterministically, made one LLM call, and failed locally with `OPENAI_API_KEY or OPENROUTER_API_KEY not set`.

## Evidence Boundary

The canonical full public benchmark summary remains `stage2/results/2026-05-12-public-finite-countermodels-summary.md` until the full public suite is rerun. Smoke-only files under `tmp_stage2_smoke/` are local debugging artifacts; promote durable evidence to `stage2/results/` before citing it as benchmark proof.
