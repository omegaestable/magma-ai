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
3. exact substitution, projection-boundary laws, short bridge/constancy chains, and bounded subterm rewrite-chain TRUE implications
4. deterministic FALSE implications from named witnesses, structured tables, affine/quadratic families, dualized witnesses, and bounded finite search

Countermodels are emitted as Lean certificates using `finOpTable` and `decideFin!`; larger `Fin 7+` tables set `maxRecDepth 20000`. Unresolved problems are skipped.

## Current Public Snapshot

As of the 2026-05-12 readiness pass:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`
- `normal`: `743/1000` solved, `245 TRUE + 498 FALSE`
- `hard1`: `17/69` solved, all `FALSE`
- `hard2`: `52/200` solved, all `FALSE`
- `hard3`: `186/400` solved, `3 TRUE + 183 FALSE`

Total public score: `998/1669`, with `0` LLM calls.

Latest local smoke-only evidence from the 2026-05-13 housekeeping run:

- `sample_20`: `14/20` solved
- `sample_200`: `165/200` solved; `S4A` and `S5A` close the remaining sample FALSE gaps, so the residual sample misses are all TRUE
- Marathon `normal_100` with zero token budget: `70/100` accepted
- packaged solver size: `52629` bytes
- hard3 TRUE final-judge smoke: `hard3_0001` accepted via `true:projection:right`; unresolved local no-key hard3 TRUE misses make a final schema-valid judge call instead of silently exiting or emitting a verdict-less `done` marker

Do not replace the full public snapshot above with smoke-only numbers. Regenerate `stage2/results/` summaries first if the full public suite is rerun.

Current best route learnings:

- `true:singleton` is the dominant new TRUE lane.
- `LP`, `RP`, and `C0` still dominate the compact FALSE lane.
- affine and linear finite families are already paying rent and should be expanded.
- `Fin 7` false certificates may need `set_option maxRecDepth 20000` before `decideFin!`.
- runner-equivalent certificate debugging should use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`.
- the remaining public gap is mostly TRUE-template work (`571` public TRUE misses versus `100` FALSE misses).

Package it with:

```powershell
.\stage2\solver\package_solver.ps1
```

The packaging script clears `stage2/submissions/` before copying `solver.py`, because the official Solo runner requires the submission directory to contain no extra files.

Before upload or playground testing, run `docs/playground-preflight.md`. It captures the single-file contract, official proxy LLM behavior, the local no-key caveat, and the smoke evidence boundary.

See `docs/smoke-tests.md` for the latest local Python, official Solo, Lean, and Windows harness status.
Use `../theory/TEORTH_WORKFLOW.md` and `../theory/tools/README.md` for graph/proof-page/paper mining workflows.

## Next Engines

1. Benchmark and tune the upgraded deterministic solver on all public problem sets.
2. Teorth-backed route mining for reusable proof and witness families.
3. More formulaic FALSE families beyond the current affine/linear lane.
4. Marathon budget manager and problem ordering under both 600s and 3600s reference interpretations.
5. LLM repair loop only for the small unresolved tail.

For the latest compressed handoff, read `docs/LATEST_HANDOFF.md`.
