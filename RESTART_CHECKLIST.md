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

## 2. Confirm Current Artifacts

1. Active solver scaffold: `stage2/solver/solver.py`
2. Packaged output target: `stage2/submissions/solver.py`
3. Official harness: `vendor/stage2-official/`
4. Shared Teorth data: `data/exports/` and `data/teorth_cache/`
5. Stage 1 archive: `stage1/`

## 3. Confirm Python Environment

From PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

## 4. Confirm Official Lean Environment

Use WSL 2, Linux, or macOS for the official Lean setup:

```bash
cd /mnt/c/Users/nacho/Documents/GitHub/magma-ai/vendor/stage2-official
bash scripts/setup.sh
source .env.judge
python3 scripts/run_harness.py
python3 scripts/run_marathon_harness.py
```

If setup fails, fix the official harness environment before changing solver logic.

Current Windows-native blocker notes:

1. `lean`, `lake`, `elan`, `bash`, and `docker` are absent on the host.
2. `wsl.exe` exists, but no WSL distro is installed/configured yet.
3. The official Marathon runner uses POSIX process groups, so native Windows runs are not faithful without a documented local harness patch.

## 5. Package The Local Solver

```powershell
.\stage2\solver\package_solver.ps1
```

Expected output: `stage2/submissions/solver.py` with size below 500 KB.

Before official Solo runs, confirm the generated submission directory contains only `solver.py`:

```powershell
Get-ChildItem -Force stage2/submissions
```

## 6. First Smoke Runs

After official setup, run official demos first, then the local scaffold.

Solo demo:

```bash
cd vendor/stage2-official
source .env.judge
python3 -m pipeline.runner --submission examples/solo/demos/baseline --problems examples/problems/sample_20.json
```

Marathon harness:

```bash
python3 scripts/run_marathon_harness.py
```

## 7. Common Traps

1. Treating archived Stage 1 prompt results as Stage 2 proof evidence.
2. Submitting Lean code before checking it with the official judge.
3. Forgetting that official solver subprocesses do not inherit local secrets.
4. Relying on local repo imports from a single-file submission.
5. Editing `vendor/stage2-official/` without documenting upstream drift.
6. Leaving `.gitkeep`, `__pycache__`, or other extras in `stage2/submissions/`; the official Solo runner rejects the directory before executing the solver.
