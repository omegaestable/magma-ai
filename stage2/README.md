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

Latest completed public refresh, generated on 2026-05-18 before the final heartbeat/path-helper optimization patch:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`
- `normal`: `803/1000` solved, `305 TRUE + 498 FALSE`
- `hard1`: `42/69` solved, `6 TRUE + 36 FALSE`
- `hard2`: `92/200` solved, `16 TRUE + 76 FALSE`
- `hard3`: `264/400` solved, `63 TRUE + 201 FALSE`

Total public score: `1201/1669`, with `0` LLM calls.

Latest local candidate evidence after the final optimization patch:

- `sample_20`: `14/20` solved
- latest recorded `sample_200`: `165/200` solved; not rerun after the May 17 compact witness patch
- Marathon `normal_100` with zero token budget: `76/100` accepted in the latest optimized-package smoke
- packaged solver size: `70631` bytes
- composite-affine focused fixture: `14/14` accepted
- accepted-grind fixture with heartbeat cap: `34/34` accepted
- compact witness fixture: `8/8` accepted, `0` LLM calls
- fresh 150-row hard mixes with zero-token Marathon: `91/150`, `83/150`, and `72/150` on seeds `20260516`, `20260517`, and `20260518`
- bounded local OpenRouter proxy smoke: Solo `1/1` and Marathon `1/1` accepted through official proxy paths

Do not treat the optimized package as promoted until full public no-loss validation preserves at least `1201/1669`. Regenerate `stage2/results/` summaries first if the full public suite is rerun.
The latest public, hard-mix, and homelab local evidence is summarized in `results/2026-05-18-zero-token-public-refresh-after-witness.md`, `results/2026-05-17-hard-mix-witness-summary.md`, and `results/2026-05-17-homelab-openrouter-proxy-smoke.md`.

Current best route learnings:

- The frontier is now TRUE-heavy: the public remainder is mostly TRUE proof synthesis, not finite countermodels.
- `true:grind` found `34` public wins but `433` incorrect attempts; keep the heartbeat cap and prefer explicit proof extraction before adding more grind reach.
- Compact finite witnesses still pay rent, but broad brute-force bound increases are not the next best use of time.
- `true:absorption_closure` and `true:equational_closure` produced accepted hard TRUE certificates; next TRUE work should be proof-producing local congruence/e-graph extraction.
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
3. Extend proof-producing TRUE synthesis before spending time on broad brute-force FALSE search.
4. Marathon budget manager and problem ordering under both 600s and 3600s reference interpretations.
5. LLM repair loop only for the small unresolved tail.

For the latest compressed handoff, read `docs/LATEST_HANDOFF.md`.
