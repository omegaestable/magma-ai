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

## Solver

The current `solver/solver.py` is still deliberately conservative, but it now has multiple deterministic proof lanes:

1. reflexive TRUE implications (`eq1_id == eq2_id`)
2. singleton/collapse TRUE implications
3. exact substitution and short rewrite-chain TRUE implications
4. deterministic FALSE implications from named witnesses, affine/linear families, and bounded finite search

Countermodels are emitted as Lean certificates using `finOpTable` and `decideFin!`; unresolved problems are skipped.

## Current Public Snapshot

As of the 2026-05-12 readiness pass:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`
- `normal`: `743/1000` solved, `245 TRUE + 498 FALSE`
- `hard1`: `17/69` solved, all `FALSE`
- `hard2`: `52/200` solved, all `FALSE`
- `hard3`: `186/400` solved, `3 TRUE + 183 FALSE`

Total public score: `998/1669`, with `0` LLM calls.

Current best route learnings:

- `true:singleton` is the dominant new TRUE lane.
- `LP`, `RP`, and `C0` still dominate the compact FALSE lane.
- affine and linear finite families are already paying rent and should be expanded.
- the remaining public gap is mostly TRUE-template work (`571` public TRUE misses versus `100` FALSE misses).

Package it with:

```powershell
.\stage2\solver\package_solver.ps1
```

The packaging script clears `stage2/submissions/` before copying `solver.py`, because the official Solo runner requires the submission directory to contain no extra files.

See `docs/smoke-tests.md` for the latest local Python, official Solo, Lean, and Windows harness status.

## Next Engines

1. Benchmark and tune the upgraded deterministic solver on all public problem sets.
2. Teorth-backed route mining for reusable proof and witness families.
3. More formulaic FALSE families beyond the current affine/linear lane.
4. Marathon budget manager and problem ordering under both 600s and 3600s reference interpretations.
5. LLM repair loop only for the small unresolved tail.

For the latest compressed handoff, read `docs/LATEST_HANDOFF.md`.
