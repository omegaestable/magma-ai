# Restart Checklist

Use this file when returning to the repo after time away or when a new agent starts from scratch.

## 1. Orient

Read these first:

1. `README.md`
2. `CURRENT_STATE.md`
3. `AGENTS.md`
4. `.github/copilot-instructions.md`
5. `EVAL_WORKFLOW.md`
6. `BENCHMARK_MANIFEST.md`
7. `stage2/README.md`
8. `theory/README.md`
9. `theory/TEORTH_WORKFLOW.md`
10. `theory/tools/README.md`
11. `stage2/docs/LATEST_HANDOFF.md`

If present, also glance at the latest generated evidence before touching the solver:

- `stage2/results/2026-05-12-public-finite-countermodels-summary.md`
- `stage2/results/2026-05-12-competition-preflight.md`

## 2. Confirm Current Artifacts

1. Active solver scaffold: `stage2/solver/solver.py`
2. Packaged output target: `stage2/submissions/solver.py`
3. Official harness: `vendor/stage2-official/`
4. Shared Teorth data: `data/exports/` and `data/teorth_cache/`
5. Stage 1 archive: `stage1/`
6. Theory workflow: `theory/TEORTH_WORKFLOW.md` and `theory/tools/README.md`

## 3. Confirm Python Environment

From PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## 4. Confirm Official Lean Environment

Native Windows setup, from PowerShell:

```powershell
winget install --id Lean.Elan -e --accept-source-agreements --accept-package-agreements
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
elan toolchain install leanprover/lean4:v4.30.0-rc2
elan default leanprover/lean4:v4.30.0-rc2
```

Build the pinned Lean project:

```powershell
Push-Location vendor/stage2-official
lake update
lake exe cache get
lake build JudgeMagma.Magma JudgeDecide.DecideBang JudgeFinOp.MemoFinOp JudgeSupport.Inspect
Pop-Location
```

Then run the official gates:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor/stage2-official
c:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe scripts/run_harness.py
c:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe scripts/run_marathon_harness.py
Pop-Location
```

The vendored harness has documented local Windows compatibility patches in `vendor/stage2-official/UPSTREAM.md`. Re-check that file before syncing upstream.

WSL 2, Linux, or macOS setup remains useful for comparison:

```bash
cd /mnt/c/Users/nacho/Documents/GitHub/magma-ai/vendor/stage2-official
bash scripts/setup.sh
source .env.judge
python3 scripts/run_harness.py
python3 scripts/run_marathon_harness.py
```

If setup fails, fix the official harness environment before changing solver logic.

## 5. Package The Local Solver

```powershell
.\stage2\solver\package_solver.ps1
```

Expected output: `stage2/submissions/solver.py` with size below 500 KB.

Before official Solo runs, confirm the generated submission directory contains only `solver.py`:

```powershell
Get-ChildItem -Force stage2/submissions
```

Current expected packaged size after the 2026-05-13 smoke pass: `49483` bytes, still far below the 500 KB limit.

## 6. First Smoke Runs

After official setup, run official demos first, then the local scaffold.

Solo demo:

```bash
cd vendor/stage2-official
source .env.judge
python3 -m pipeline.runner --submission examples/solo/demos/baseline --problems examples/problems/sample_20.json
```

Marathon harness:

```powershell
Push-Location vendor/stage2-official
c:/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe scripts/run_marathon_harness.py
Pop-Location
```

Current fast local smoke probes:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
.\.venv\Scripts\python.exe -m py_compile stage2\solver\solver.py stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe stage2\experiments\smoke_llm_dsl.py
.\.venv\Scripts\python.exe theory\tools\smoke_problem_sets.py
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_20.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\sample_200.json
..\..\.venv\Scripts\python.exe scripts\run_marathon.py --solver ..\..\stage2\submissions --manifest examples\problems\marathon\normal_100.jsonl --budget-tokens 0
Pop-Location
```

Latest smoke-only outcomes: `sample_20 = 14/20`, `sample_200 = 165/200` with all remaining misses TRUE, and Marathon `normal_100 = 70/100` accepted with zero tokens.

Public benchmark refresh and team-memory regeneration:

```powershell
$env:PYTHONUTF8='1'
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
Push-Location vendor/stage2-official
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\normal.jsonl --output ..\..\stage2\results\2026-05-12-normal-finite-countermodels.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\hard1.jsonl --output ..\..\stage2\results\2026-05-12-hard1-finite-countermodels.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\hard2.jsonl --output ..\..\stage2\results\2026-05-12-hard2-finite-countermodels.json
..\..\.venv\Scripts\python.exe -m pipeline.runner --submission ..\..\stage2\submissions --problems examples\problems\hard3.jsonl --output ..\..\stage2\results\2026-05-12-hard3-finite-countermodels.json
Pop-Location
.\.venv\Scripts\python.exe stage2\experiments\summarize_public_benchmarks.py
.\.venv\Scripts\python.exe stage2\experiments\competition_preflight.py
```

## 7. Common Traps

1. Treating archived Stage 1 prompt results as Stage 2 proof evidence.
2. Submitting Lean code before checking it with the official judge.
3. Forgetting that official solver subprocesses do not inherit local secrets.
4. Relying on local repo imports from a single-file submission.
5. Editing `vendor/stage2-official/` without documenting upstream drift.
6. Leaving `.gitkeep`, `__pycache__`, or other extras in `stage2/submissions/`; the official Solo runner rejects the directory before executing the solver.
7. Forgetting that route labels cannot be added to the judge answer JSON; the judge accepts exactly `verdict` and `code`, so route labels must live in stderr/log-derived summaries.
8. Debugging certificates with direct `verify_answer(problem, ...)` and forgetting the pipeline proof policy; use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`.
9. Treating `tmp_stage2_smoke/` or live Teorth scrape output as durable evidence before promoting it to `stage2/results/`.
