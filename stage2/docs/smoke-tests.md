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
- Reflexive fixture reaches `judge_calls=1`.
- Failure is currently `missing lean binary: lean`.

Protocol note:

- Current `pipeline/proxy.py` and the official Solo demo solvers use `{"call":"judge","verdict":...,"code":...}` and finish when the judge accepts.
- `docs/solo_mode.md` also describes a terminal `type: submit` shape. Treat the proxy and examples as the executable truth for this harness snapshot unless upstream changes the proxy.

## Current Blockers

Windows native state on this machine:

- `lean`, `lake`, `elan`, `bash`, and `docker` are not installed.
- `wsl.exe` exists, but no WSL distro is installed/configured.
- Official Marathon runner currently uses POSIX process-group behavior (`os.killpg`), so native Windows execution is not a faithful Marathon environment without a local harness patch.

Recommended next setup path:

```bash
cd /mnt/c/Users/nacho/Documents/GitHub/magma-ai/vendor/stage2-official
bash scripts/setup.sh
source .env.judge
python3 scripts/run_harness.py
python3 scripts/run_marathon_harness.py
```
