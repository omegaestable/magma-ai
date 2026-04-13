# Copilot Instructions

This workspace is for SAIR Equational Theories Stage 1 cheatsheet development.

## Always-On Priorities

1. Mathematical soundness first.
2. Normal-set safety before hard-set uplift.
3. Reproducible paid-model evidence before promotion.
4. Prefer smaller, clearer edits over clever but brittle ones.

## Repo-Specific Rules

1. Cheatsheets are plain text files in `cheatsheets/`.
2. Cheatsheets may use only `{{equation1}}` and `{{equation2}}` substitution.
3. Jinja2 logic is banned in cheatsheets.
4. Do not hardcode benchmark-specific answers as policy.
5. Treat `sim_lab.py` as the canonical evaluator.
6. Treat `run_paid_eval.ps1` as the fast path for standard runs.
7. Treat `analyze_seed_failures.py` and `distill.py` as the default failure-analysis loop.

## Startup Path

On a cold start, read in this order:

1. `README.md`
2. `CURRENT_STATE.md`
3. `AGENTS.md`
4. `RESTART_CHECKLIST.md`
5. `EVAL_WORKFLOW.md`
6. `BENCHMARK_MANIFEST.md`

## Editing Priorities

1. Prefer editing docs, cheatsheets, and eval-support files over research-only scripts.
2. Do not change math or scoring logic casually.
3. If a task is about restart reliability or onboarding, start with docs and workspace instructions.
4. If a task is about benchmark performance, start with current result files and the active cheatsheet.

## Current Canonical Artifacts

- Active candidate: `cheatsheets/v26b.txt`
- Previous candidate: `cheatsheets/v26a.txt`
- Historical champion: `cheatsheets/v24j.txt`
- Next design doc: `V25A_MASTER_PROMPT.md`
- Evaluator: `sim_lab.py`
- Quick-run wrapper: `run_paid_eval.ps1`
- Score summary: `results/scoreboard.md`

## Common Failure Modes

1. Restart drift: agent follows stale plan docs instead of current landing docs.
2. Historical drift: agent starts in optional research scripts instead of the evaluate-distill-patch loop.
3. Unsafe optimization: candidate improves hard performance but regresses on normal sets.
4. Prompt brittleness: more instructions increase collapse or execution errors.

## Desired Outcome

The repo should feel like a controlled evaluation system, not a bag of experiments. Favor canonical paths and explicit evidence.