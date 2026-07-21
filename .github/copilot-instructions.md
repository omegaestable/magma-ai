# Copilot Instructions

This workspace is for SAIR Equational Theories Stage 2 solver development.

## Always-On Priorities

1. Lean judge acceptance first.
2. Deterministic certificates before LLM spending.
3. Marathon budget discipline before broad prompt tuning.
4. Reproducible local harness evidence before promotion.
5. Preserve mathematical provenance from Teorth and papers.

## Repo-Specific Rules

1. The Stage 2 submission artifact is a single `solver.py` file, <= 500 KB.
2. Treat `vendor/stage2-official/` as the canonical local copy of the official judge and runners.
3. Treat `stage2/solver/solver.py` as the active local scaffold.
4. Treat `data/exports/` and `data/teorth_cache/` as shared theory/provenance data.
5. Treat `stage1/` as historical archive only.
6. Do not modify official harness files casually; document any local patch or upstream sync.
7. Do not rely on local secrets, network access, or repo-local imports from submitted solver code.

## Startup Path

On a cold start, read in this order:

1. `README.md`
2. `CURRENT_STATE.md`
3. `AGENTS.md`
4. `RESTART_CHECKLIST.md`
5. `EVAL_WORKFLOW.md`
6. `BENCHMARK_MANIFEST.md`
7. `stage2/README.md`
8. `stage2/docs/playground-preflight.md`
9. `theory/README.md`
10. `theory/TEORTH_WORKFLOW.md`
11. `theory/tools/README.md`
12. `stage2/docs/LATEST_HANDOFF.md`

## Editing Priorities

1. Prefer solver, certificate, docs, and harness-support work over archived Stage 1 edits.
2. Keep official judge assumptions explicit and evidence-backed.
3. If a task is about setup or onboarding, start with docs and reproducibility.
4. If a task is about performance, start with official runner outputs and judge statuses.
5. If a task is about theory, start with Teorth data, proof pages, and paper notes.

## Current Canonical Artifacts

- Active solver scaffold: `stage2/solver/solver.py`
- Packaged output: `stage2/submissions/solver.py`
- Self-verifying LLM dev loop (OpenRouter gpt-oss + local judge): `stage2/experiments/dev_true_loop.py` (+ `analyze_true_loop.py`); latest run `stage2/results/2026-07-20-llm-true-loop-and-prompt-v3.md`
- Official harness: `vendor/stage2-official/`
- Latest public benchmark summary: `stage2/results/2026-05-12-public-finite-countermodels-summary.md`
- Latest competition preflight: `stage2/results/2026-05-12-competition-preflight.md`
- Playground preflight: `stage2/docs/playground-preflight.md`
- Theory extraction workflow: `theory/TEORTH_WORKFLOW.md`
- Theory tool index: `theory/tools/README.md`
- Stage 1 archive: `stage1/`
- Theory tools: `theory/tools/`
- Shared implication data: `data/exports/`
- Shared Teorth cache: `data/teorth_cache/`

## Common Failure Modes

1. Restart drift into archived Stage 1 prompt-cheatsheet workflows.
2. Lean code that looks plausible but is not judge-accepted.
3. False certificates with a bad magma table or wrong equation evaluation.
4. True certificates that depend on unavailable Teorth theorem names.
5. Solver logic that works locally only because it reads files or secrets unavailable in the official subprocess.
6. Marathon strategies that solve easy cases but waste the shared budget.
7. Attempting to include route labels or metadata in the judge answer JSON; the judge expects exactly `verdict` and `code`.
8. Direct `judge.verify.verify_answer(problem, ...)` checks that omit the pipeline default proof policy; use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)` for runner-equivalent certificate debugging.
9. Mistaking a local missing upstream LLM key for a submitted-solver playground protocol failure.

## Desired Outcome

The repo should feel like a controlled Stage 2 proof lab: official harness pinned, solver packaged reproducibly, theory data indexed, certificates validated, and every promotion backed by adversarial review.
