# Stage 2 Lab

This directory contains local Stage 2 solver work, submissions, experiments, and results.

## Layout

- `solver/`: active solver scaffold and packaging script.
- `submissions/`: generated single-file submission artifacts.
- `docs/`: local Stage 2 design notes, route ledger, motif cards, smoke-test notes, cleanup manifest, and review checklists.
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

Countermodels are emitted as Lean certificates using `finOpTable` and `decideFin!`; larger `Fin 7+` tables set `maxRecDepth 20000`. Unresolved problems are skipped unless the official Solo/Marathon proxy supplies a positive-token LLM path. The broad `true:grind` fallback has been removed from active solver policy after playground error-rate failures.

## Current Public Snapshot

Latest completed public refresh, generated on 2026-05-18 before the final heartbeat/path-helper optimization patch and before the default grind rollback:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`
- `normal`: `803/1000` solved, `305 TRUE + 498 FALSE`
- `hard1`: `42/69` solved, `6 TRUE + 36 FALSE`
- `hard2`: `92/200` solved, `16 TRUE + 76 FALSE`
- `hard3`: `264/400` solved, `63 TRUE + 201 FALSE`

Total public score: `1201/1669`, with `0` LLM calls. This is historical zero-token evidence; `34` of those wins came from `true:grind`, which is now retired from active solver policy.

Latest local candidate evidence after the final optimization patch:

- `sample_20`: `14/20` solved
- latest recorded `sample_200`: `165/200` solved; not rerun after the May 17 compact witness patch
- Marathon `normal_100` with zero token budget after the absorption time-cap optimization: `74/100` accepted in `56.6s`
- packaged solver size: `85173` bytes after the latest local package pass
- May 21 prune/refactor evidence: `_closure_route_impl` dedupe preserved `normal_100 = 74/100` zero-token Marathon behavior; selected fallback reproduction is summarized in `results/2026-05-21-prune-refactor-and-fallback-reproduction.md`
- composite-affine focused fixture: `14/14` accepted
- accepted-grind fixture with heartbeat cap: historical discovery evidence only; the active solver no longer exposes this route
- compact witness fixture: `8/8` accepted, `0` LLM calls
- fresh 150-row hard mixes with zero-token Marathon: `91/150`, `83/150`, and `72/150` on seeds `20260516`, `20260517`, and `20260518`
- positive-token local proxy evidence: direct OpenRouter smokes passed; targeted parity recorded Solo `llm_calls=2`, Marathon `llm_calls=1`, and Marathon `tokens_used=7208`, but unresolved TRUE proof quality still failed

Do not treat the optimized package as promoted from zero-token evidence alone. The default local gate is now positive-token playground parity through `stage2/experiments/run_playground_parity_llm.py`; zero-token sweeps are optional deterministic regression only.
Selected row lists are diagnostic fixtures; generalize them into reusable proof/witness families instead of hardcoding ids. The latest public, hard-mix, homelab, optimization, and fallback-reproduction evidence is summarized in `results/2026-05-18-zero-token-public-refresh-after-witness.md`, `results/2026-05-17-hard-mix-witness-summary.md`, `results/2026-05-17-homelab-openrouter-proxy-smoke.md`, `results/2026-05-20-optimization-readiness.md`, and `results/2026-05-21-prune-refactor-and-fallback-reproduction.md`.

Current best route learnings:

- The frontier is now TRUE-heavy: the public remainder is mostly TRUE proof synthesis, not finite countermodels.
- `true:grind` found `34` public wins but `433` incorrect attempts and failed playground error discipline; it is historical evidence only, not an active route.
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

Before upload or playground testing, run `docs/playground-preflight.md`. It captures the single-file contract, official proxy LLM behavior, the local no-key caveat, failure classification, and the positive-token parity runner.

See `docs/smoke-tests.md` for the latest local Python, official Solo, Lean, and Windows harness status.
Use `docs/solver-route-ledger.md` and `docs/motif-cards/` before changing a route, and use `docs/cleanup-manifest.md` before touching scratch artifacts.
Use `../theory/TEORTH_WORKFLOW.md`, `../theory/TEORTH_NOTES.md`, and `../theory/tools/README.md` for graph/proof-page/paper mining workflows.

## Next Engines

1. Run broader no-loss validation for the `0.05s` absorption cap, especially hard TRUE closure fixtures and the full public sets.
2. Build the small route fixtures listed in `docs/solver-route-ledger.md`.
3. Improve unresolved TRUE proof quality; proxy transport works, but targeted parity still fails by judge rejection / rejected LLM output.
4. Extend proof-producing TRUE synthesis before spending time on broad brute-force FALSE search.
5. Refresh the full public suite, including `normal`, before updating canonical `stage2/results/` totals.

For the latest compressed handoff, read `docs/LATEST_HANDOFF.md`.
