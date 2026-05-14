# Stage 2 Smoke Tests

Last smoke run: 2026-05-14.

## Passing Locally

PowerShell with `.venv` Python 3.14.3:

```powershell
.\.venv\Scripts\python.exe -m py_compile stage2\solver\solver.py stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe theory\tools\smoke_problem_sets.py
.\stage2\solver\package_solver.ps1
```

Observed:

- Set `$env:PYTHONUTF8='1'` and `$env:PATH="$env:USERPROFILE\.elan\bin;$env:PATH"` for official runner checks.
- Packaged `stage2/submissions/solver.py` at 60614 bytes.
- `stage2/submissions/` must contain only `solver.py`; the official Solo runner rejects `.gitkeep`, `__pycache__`, and any other extra entries before executing the solver.
- Run the package command last before official runner invocations. `compileall stage2` can create bytecode caches under generated submission paths.
- Use explicit `--output` paths for recorded Solo smoke runs; the default `pipeline/results/submissions.json` is easy to confuse with earlier local smoke rows.
- `smoke_llm_dsl.py` exercises fake LLM DSL parsing without network or model calls.
- `smoke_problem_sets.py` verifies the official mirrors and analysis-only problem-set policy.

## Official Solo Runner Probes

Command shape from `vendor/stage2-official/`:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
$env:PYTHONUTF8='1'
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_20.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_200.json
Pop-Location
```

Observed after cleaning and packaging `stage2/submissions/`:

- Runner launches the packaged local solver.
- `sample_20`: `14/20` solved.
- `sample_200`: `165/200` solved.
- Targeted FALSE fixtures for `false_907_2534`, `false_1682_411`, and `false_3145_3481` are accepted by the official runner after the recent fixes.
- Packaged solver remains 60614 bytes and the submission directory contains only `solver.py`.

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

## Focused Hard TRUE And Hard-Mix Probes

The old `tmp_stage2_smoke/hard3_true2.jsonl` probe is now stale as an LLM-path check because `hard3_0002` is accepted deterministically by `true:absorption_closure`. Use a currently unresolved TRUE fixture when testing local no-key LLM behavior.

Command shape from `vendor/stage2-official/` for recorded hard probes:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
$env:PYTHONUTF8='1'
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems ..\..\tmp_stage2_smoke\2026-05-14-hard-mix-150.jsonl --output ..\..\tmp_stage2_smoke\2026-05-14-hard-mix-150-result-after-affine-absorption.json
Pop-Location
```

Observed:

- Same 150-row hard mix, seed `20260514`: `73/150`, up from `68/150`, no regressions.
- New hard-mix TRUE wins: `hard3_0212` and `hard3_0002`, both via `true:absorption_closure`.
- New hard-mix FALSE wins: `hard2_0169`, `hard1_0024`, and `hard3_0035` via expanded linear/affine search.
- Full hard-only reruns after the patch: `hard1 24/69`, `hard2 64/200`, `hard3 211/400`, with no regressions versus the 2026-05-12 hard artifacts.

## Evidence Boundary

The canonical full public benchmark summary remains `stage2/results/2026-05-12-public-finite-countermodels-summary.md` until the full public suite, including `normal`, is rerun. The latest hard-only local evidence is summarized in `stage2/results/2026-05-14-hard-affine-absorption-summary.md`; raw smoke files under `tmp_stage2_smoke/` are local debugging artifacts.
