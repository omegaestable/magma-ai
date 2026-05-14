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
3. exact substitution, projection-boundary laws, short bridge/constancy chains, bounded subterm rewrite chains, and bounded absorption-closure TRUE implications
4. deterministic FALSE implications from named witnesses, structured tables, expanded linear/affine families, bounded quadratic families, dualized witnesses, and bounded finite search

Countermodels are emitted as Lean certificates using `finOpTable` and `decideFin!`; larger `Fin 7+` tables set `maxRecDepth 20000`. Unresolved problems are skipped.

## Current Public Snapshot

As of the 2026-05-12 readiness pass:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`
- `normal`: `743/1000` solved, `245 TRUE + 498 FALSE`
- `hard1`: `17/69` solved, all `FALSE`
- `hard2`: `52/200` solved, all `FALSE`
- `hard3`: `186/400` solved, `3 TRUE + 183 FALSE`

Total public score: `998/1669`, with `0` LLM calls.

Latest local candidate evidence from the 2026-05-14 hard-mix session:

- `sample_20`: `14/20` solved
- `sample_200`: `165/200` solved; `S4A` and `S5A` close the remaining sample FALSE gaps, so the residual sample misses are all TRUE
- Marathon `normal_100` with zero token budget: `70/100` accepted
- packaged solver size: `60614` bytes
- composite-affine focused fixture: `14/14` accepted
- same 150-row hard mix, seed `20260514`: `73/150` accepted, up from `68/150`, with no regressions
- full hard-only reruns: `hard1 24/69`, `hard2 64/200`, `hard3 211/400`, with no regressions versus the 2026-05-12 hard artifacts

Do not replace the full public snapshot above with smoke-only numbers. Regenerate `stage2/results/` summaries first if the full public suite is rerun.
The latest hard-only local evidence is summarized in `results/2026-05-14-hard-affine-absorption-summary.md`.

Current best route learnings:

- `true:singleton` is the dominant new TRUE lane.
- `LP`, `RP`, and `C0` still dominate the compact FALSE lane.
- affine and linear finite families are paying rent; the current split keeps linear/affine sizes at `2,3,4,5,7,8,9` while leaving quadratic search on the tighter older sizes.
- `true:absorption_closure` produced accepted hard TRUE certificates, but the remaining hard-only gap is still TRUE-heavy: `292` TRUE misses versus `78` FALSE misses.
- `Fin 7` false certificates may need `set_option maxRecDepth 20000` before `decideFin!`.
- runner-equivalent certificate debugging should use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`.
- canonical full public gap counts remain the 2026-05-12 numbers until `normal|hard1|hard2|hard3` are refreshed together.

Package it with:

```powershell
.\stage2\solver\package_solver.ps1
```

The packaging script clears `stage2/submissions/` before copying `solver.py`, because the official Solo runner requires the submission directory to contain no extra files.

Before upload or playground testing, run `docs/playground-preflight.md`. It captures the single-file contract, official proxy LLM behavior, the local no-key caveat, and the smoke evidence boundary.

See `docs/smoke-tests.md` for the latest local Python, official Solo, Lean, and Windows harness status.
Use `../theory/TEORTH_WORKFLOW.md` and `../theory/tools/README.md` for graph/proof-page/paper mining workflows.

## Next Engines

1. Refresh the full public suite, including `normal`, before updating canonical `stage2/results/` totals.
2. Teorth-backed route mining for reusable proof and witness families.
3. Extend the absorption/projection TRUE proof graph before spending time on broad brute-force FALSE search.
4. Marathon budget manager and problem ordering under both 600s and 3600s reference interpretations.
5. LLM repair loop only for the small unresolved tail.

For the latest compressed handoff, read `docs/LATEST_HANDOFF.md`.
