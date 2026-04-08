# AGENTS.md

This file is the repo-wide navigation contract for coding agents.

## Mission

Build, evaluate, and promote a single competition-ready cheatsheet for SAIR Equational Theories Stage 1.

The submission artifact is one text file in `cheatsheets/`.

## Read Order On Cold Start

Follow this order exactly:

1. `README.md`
2. `CURRENT_STATE.md`
3. `AGENTS.md`
4. `.github/copilot-instructions.md`
5. `RESTART_CHECKLIST.md`
6. `EVAL_WORKFLOW.md`
7. `BENCHMARK_MANIFEST.md`
8. Only then inspect scripts or candidate files.

## Current Operating Model

- **Champion: `cheatsheets/v24j.txt`** (8,955 bytes, 87.4% of cap)
- Previous champion: `cheatsheets/v21f_structural.txt` (historical)
- Next design document: `V25A_MASTER_PROMPT.md`
- Canonical evaluator: `sim_lab.py`
- Canonical quick wrapper: `run_paid_eval.ps1`
- Canonical failure loop: `analyze_seed_failures.py` then `distill.py`

## Banned Approaches

1. No Jinja2 logic in cheatsheets.
2. No benchmark-pair memorization as policy.
3. No promotion on hard-set uplift if normal safety regresses.
4. No guessing about proofs or counterexamples when result artifacts disagree.

## Canonical Workflow

1. Evaluate current cheatsheet on warmup normal sets.
2. Run full normal gates.
3. Distill failures.
4. Patch cheatsheet conservatively.
5. Re-run normal gates.
6. Run hard and unseen stress only after safety is stable.

## Primary Roles

### Eval Runner

Use when the task is benchmark execution, scoring, or promotion evidence.

Primary files:

- `sim_lab.py`
- `run_paid_eval.ps1`
- `scoreboard.py`
- `results/`

### Distiller

Use when the task is understanding failures and translating them into safe edits.

Primary files:

- `analyze_seed_failures.py`
- `distill.py`
- `v22_coverage_analysis.py`
- `v22_mine_sound_rules.py`

### Proof Auditor

Use when the task is provenance, theorem grounding, or proof-page mining.

Primary files:

- `fetch_teorth_data.py`
- `teorth_true_proof_agent.py`
- `proof_scraping_lab.py`
- `v21_data_infrastructure.py`

## Active Versus Optional Paths

Active starting points:

- `README.md`
- `EVAL_WORKFLOW.md`
- `cheatsheets/v24j.txt`
- `V25A_MASTER_PROMPT.md`
- `sim_lab.py`

Optional or research-only paths:

- `vnext_search_v2.py`
- `proof_atlas.py`
- `atlas_public_dev.py`
- `invoke_copilot_candidate.py`

Do not start from optional paths unless the user explicitly asks for them.

## Expected Agent Behavior

1. Prefer the simplest sound workflow.
2. Keep edits local and reversible.
3. Preserve math-grounded reasoning over prompt cleverness.
4. Surface whether a miss is a coverage gap or an execution error.
5. Use result files as evidence, not impressions from one run.