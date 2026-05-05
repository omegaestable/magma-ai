# Stage 2 Smoke Tests

Last smoke run: 2026-05-05.

## Passing Locally

PowerShell with `.venv` Python 3.14.3:

```powershell
python -m py_compile stage2/solver/solver.py
python -m compileall stage2 theory -q
python -m ruff check stage2/solver
.\stage2\solver\package_solver.ps1
```

Observed:

- Packaged `stage2/submissions/solver.py` at 3473 bytes.
- `stage2/submissions/` must contain only `solver.py`; the official Solo runner rejects `.gitkeep`, `__pycache__`, and any other extra entries before executing the solver.
- Run the package command last before official runner invocations. `compileall stage2` can create bytecode caches under generated submission paths.
- Local Solo reflexive smoke emits a judge request.
- Local Solo unsupported smoke exits without speculative output.
- Local Marathon smoke wrote two reflexive JSONL answers from a three-problem manifest.

## Official Solo Runner Probe

Command shape from `vendor/stage2-official/`:

```powershell
c:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe -m pipeline.runner --submission ../../stage2/submissions --problems ../../tmp_stage2_smoke/reflexive_problem.json
```

Observed after cleaning `stage2/submissions/`:

- Runner launches the packaged local solver.
- Reflexive fixture is solved by the official Lean judge: `1/1 solved`, `llm:0`, `judge:1`.
- Packaged solver remains 3473 bytes and the submission directory contains only `solver.py`.

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
