---
name: stage2-harness
description: 'Use when: setting up or running the SAIR Stage 2 official harness, Solo runner, Marathon runner, judge tests, or checking upstream config drift.'
argument-hint: 'Specify setup, Solo run, Marathon run, harness tests, or config drift check.'
---

# Stage 2 Harness

Use this workflow for official Stage 2 environment setup, local runner checks, and upstream harness drift.

## Procedure

1. Work from `vendor/stage2-official/`.
2. Read `UPSTREAM.md`, `README.md`, `docs/solo_mode.md`, and `docs/marathon_mode.md` when the task depends on protocol details.
3. For first setup in WSL/Linux/macOS:

```bash
bash scripts/setup.sh
source .env.judge
python3 scripts/run_harness.py
python3 scripts/run_marathon_harness.py
```

4. On native Windows (PowerShell), prepend the Elan toolchain to PATH **before** any runner invocation, otherwise the Solo runner reports `missing lean binary: lean` even though the solver and judge call succeed:

```powershell
$env:PATH = "$env:USERPROFILE\.elan\bin;$env:PATH"
python vendor/stage2-official/scripts/submit.py --submission stage2/submissions --problems tmp_stage2_smoke/reflexive_problem.json
```

5. For Solo debugging, prefer a small public problem file from `examples/problems/` or `tmp_stage2_smoke/reflexive_problem.json`.
6. For Marathon debugging, verify append-only JSONL behavior, last-write-wins scoring, token budget, and timeout behavior.
7. For upload or playground readiness, run `stage2/docs/playground-preflight.md`: run syntax/local smokes first, package last, confirm `stage2/submissions/` contains only `solver.py`, check size, then run Solo and zero-token Marathon smokes.
8. Treat local `OPENAI_API_KEY or OPENROUTER_API_KEY not set` as a local proxy credential issue when the solver reached the LLM request path.
9. Do not edit official harness files unless the local patch is explicitly documented.

## Outputs

- Harness pass/fail summary.
- Runner command used.
- Result path or stderr excerpt.
- Any upstream config drift that changes solver assumptions.
- Playground readiness status: packaging, size, single-file layout, proxy LLM caveat, and smoke/full-benchmark evidence boundary.
