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

4. For Solo debugging, prefer a small public problem file from `examples/problems/`.
5. For Marathon debugging, verify append-only JSONL behavior, last-write-wins scoring, token budget, and timeout behavior.
6. Do not edit official harness files unless the local patch is explicitly documented.

## Outputs

- Harness pass/fail summary.
- Runner command used.
- Result path or stderr excerpt.
- Any upstream config drift that changes solver assumptions.
