# AGENTS.md

This file is the repo-wide navigation contract for coding agents.

## Mission

Build, evaluate, and promote a Stage 2 `solver.py` for SAIR Equational Theories. The solver must produce Lean 4 proof certificates accepted by the official judge.

Stage 1 prompt-cheatsheet work is archived under `stage1/` and is not the active workflow.

## Cold-Start Read Order

Follow this order exactly:

1. `README.md`
2. `CURRENT_STATE.md`
3. `AGENTS.md`
4. `.github/copilot-instructions.md`
5. `RESTART_CHECKLIST.md`
6. `EVAL_WORKFLOW.md`
7. `BENCHMARK_MANIFEST.md`
8. `stage2/README.md`
9. `theory/README.md`
10. Only then inspect solver code, theory tools, or archived Stage 1 files.

## Current Operating Model

- Active artifact: `stage2/solver/solver.py`.
- Packaged output: `stage2/submissions/solver.py`.
- Official harness: `vendor/stage2-official/`.
- Official harness commit: `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Strategy: Marathon-first, deterministic certificates first, LLM calls second.
- Shared data: `data/exports/`, `data/teorth_cache/`, and `paper/`.
- Stage 1 archive: `stage1/`.

## Banned Approaches

1. Do not treat Stage 1 prompt accuracy as Stage 2 evidence.
2. Do not submit speculative Lean code as a solved case without judge acceptance.
3. Do not hardcode private or benchmark-specific answers as policy.
4. Do not rely on network, local secrets, or repo-local imports from the submitted solver.
5. Do not import Teorth theorem names in official certificates unless upstream allowlists them.
6. Do not edit vendored official harness files casually; document any local patch.

## Canonical Workflow

1. Read the official Stage 2 docs in `vendor/stage2-official/docs/` and examples tutorials.
2. Package the local solver with `stage2/solver/package_solver.ps1`.
3. Validate syntax and size of `stage2/submissions/solver.py`.
4. Run official Solo samples for fast certificate debugging.
5. Run official Marathon samples for pacing, triage, and append-only output behavior.
6. Distill failures into certificate-template fixes, not prompt folklore.
7. Red-team candidate behavior before promotion.

## Primary Roles

### Harness Runner

Use when the task is official setup, runner invocation, result collection, or config drift checks.

Primary files:

- `vendor/stage2-official/`
- `EVAL_WORKFLOW.md`
- `BENCHMARK_MANIFEST.md`

### Solver Engineer

Use when the task is `solver.py`, packaging, Marathon/Solo I/O, budgeting, caching, or no-secret/no-network constraints.

Primary files:

- `stage2/solver/solver.py`
- `stage2/solver/package_solver.ps1`
- `stage2/README.md`

### Lean Certificate Engineer

Use when the task is Lean proof code, judge statuses, proof dependency policy, or true-certificate templates.

Primary files:

- `vendor/stage2-official/judge/`
- `vendor/stage2-official/docs/solo_mode.md`
- `vendor/stage2-official/docs/marathon_mode.md`

### Counterexample Miner

Use when the task is finite magma search, false certificates, witness tables, or `decideFin!` proof generation.

Primary files:

- `data/teorth_cache/smallest_magma.txt`
- `data/teorth_cache/proof_page_cache/`
- `theory/tools/`

### Graph Explorer

Use when the task is Teorth implication graph navigation, random equation dives, proof provenance, shortest paths, or theory cards.

Primary files:

- `data/exports/export_raw_implications_14_3_2026.csv`
- `data/exports/equations.txt`
- `data/teorth_cache/graph.json`
- `data/teorth_cache/full_entries.json`

### Red-Team Reviewer

Use before a candidate is promoted. Focus on malformed I/O, forbidden imports/tokens, budget failures, local-vs-official drift, and Lean dependency policy.

## Active Versus Archive Paths

Active starting points:

- `README.md`
- `CURRENT_STATE.md`
- `stage2/solver/solver.py`
- `vendor/stage2-official/README.md`
- `vendor/stage2-official/examples/solo/TUTORIAL.md`
- `vendor/stage2-official/examples/marathon/TUTORIAL.md`
- `theory/README.md`

Archive paths:

- `stage1/cheatsheets/`
- `stage1/eval/`
- `stage1/analysis/`
- `stage1/results/`

Do not start from archive paths unless the task explicitly asks for Stage 1 archaeology.
