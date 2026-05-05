# Stage 2 Lab

This directory contains local Stage 2 solver work, submissions, experiments, and results.

## Layout

- `solver/`: active solver scaffold and packaging script.
- `submissions/`: generated single-file submission artifacts.
- `docs/`: local Stage 2 design notes, smoke-test notes, and review checklists.
- `experiments/`: local experiments that are not official harness source.
- `results/`: local result summaries and failure ledgers.

## Track Strategy

The initial architecture is Marathon-first:

1. Read all problem metadata from the manifest.
2. Solve deterministic cases before spending tokens.
3. Use shared caches and proof-family triage across problems.
4. Append accepted-looking certificates to output JSONL.
5. Keep Solo compatibility for fast single-problem proof debugging.

## Solver Scaffold

The current `solver/solver.py` is deliberately small. It solves only reflexive implications (`eq1_id == eq2_id`) and skips everything else. This is useful for testing the packaging and I/O surface before we add real certificate engines.

Package it with:

```powershell
.\stage2\solver\package_solver.ps1
```

The packaging script clears `stage2/submissions/` before copying `solver.py`, because the official Solo runner requires the submission directory to contain no extra files.

See `docs/smoke-tests.md` for the latest local Python, official Solo, Lean, and Windows harness status.

## Next Engines

1. False certificate generator for finite magma tables.
2. Teorth-backed triage index for known true/false implications.
3. True proof template generator for standalone Lean proofs.
4. Marathon budget manager and problem ordering.
5. LLM repair loop for unresolved proof attempts.
