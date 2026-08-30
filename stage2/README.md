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

Countermodels are emitted as Lean certificates using `finOpTable` (order ≤ 10) or an inlined `List.getD` lookup (above it) plus `decideFin!`; `maxRecDepth 20000` is set when the decide cost `n ** variables` exceeds 4,096, not merely when the order does — a `Fin 6` table against a 5-variable goal needs it (rail 3b-iii in `CLAUDE.md`). Unresolved problems are skipped unless the official Solo/Marathon proxy supplies a positive-token LLM path. Active Marathon validation in this repo must use positive token budgets; do not run `--budget-tokens 0` as a guardrail. The broad `true:grind` fallback has been removed from active solver policy after playground error-rate failures.

Current TRUE boundary rails are narrower than some historical prompt snippets: Marathon TRUE LLM submissions must be solver-owned `rewrite_chain` or `guided_chain` outputs. Raw TRUE Lean is disabled for Marathon and remains only a Solo/debug rail as `{"verdict":"true","code":"<complete Lean file>"}`. The Lean file may declare helper theorems, defs, lemmas, namespaces, or notation above `submission`. Legacy body-only `proof` / `proof_body` payloads are intentionally unsupported locally, even though an older vendored README prompt snippet still shows them.

## Current Public Snapshot

Latest completed public refresh, generated on 2026-05-18 before the final heartbeat/path-helper optimization patch and before the default grind rollback:

- `sample_20`: `14/20` solved, `4 TRUE + 10 FALSE`
- `normal`: `803/1000` solved, `305 TRUE + 498 FALSE`
- `hard1`: `42/69` solved, `6 TRUE + 36 FALSE`
- `hard2`: `92/200` solved, `16 TRUE + 76 FALSE`
- `hard3`: `264/400` solved, `63 TRUE + 201 FALSE`

Total public score for that 2026-05-18 refresh: `1201/1669`, with `0` LLM calls. **Historical only** — `34` of those wins came from `true:grind`, retired since. Current measured state lives in `CLAUDE.md`.

The May and June bullets that used to live here are historical discovery
evidence, not current package state. The current artifact is **456,604 bytes**
as of 2026-08-29; current coverage and judge evidence live only in `../CLAUDE.md`
and the dated files linked from `docs/LATEST_HANDOFF.md`.

Do not promote a package without positive-token official/proxy evidence. The
current preflight is `docs/playground-preflight.md`, and active Marathon
validation must use a positive token budget.
For standard local LLM runs, store the rotated upstream key in the ignored
repo-root `.env` with `stage2/experiments/set_openrouter_repo_env.ps1`. The
repo-owned probe and parity entrypoints load process env first, then `.env`,
then legacy Windows User env fallback.
Selected row lists are diagnostic fixtures; generalize them into reusable proof/witness families instead of hardcoding ids. The latest public, hard-mix, homelab, optimization, fallback-reproduction, cleanup-smoke, and positive-token mixed-lane evidence is summarized in `results/2026-05-18-zero-token-public-refresh-after-witness.md`, `results/2026-05-17-hard-mix-witness-summary.md`, `results/2026-05-17-homelab-openrouter-proxy-smoke.md`, `results/2026-05-20-optimization-readiness.md`, `results/2026-05-21-prune-refactor-and-fallback-reproduction.md`, `results/2026-05-25-cleanup-and-smoke.md`, and `results/2026-05-30-positive-token-mixed-lane-resume.md`.

Historical route learnings (kept for rationale):

- The frontier is now TRUE-heavy: the public remainder is mostly TRUE proof synthesis, not finite countermodels.
- `true:grind` found `34` public wins but `433` incorrect attempts and failed playground error discipline; it is historical evidence only, not an active route.
- Compact finite witnesses still pay rent, but broad brute-force bound increases are not the next best use of time.
- `true:absorption_closure` and `true:equational_closure` produced accepted hard TRUE certificates; next TRUE work should be proof-producing local congruence/e-graph extraction.
- False certificates may need `set_option maxRecDepth 20000` before `decideFin!` — keyed on the decide cost `n ** variables`, not on the order alone.
- runner-equivalent certificate debugging should use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`.
- Austin research: `docs/DEEP_SESSION_8_AUSTIN_HANDOVER.md` and
  `experiments/austin/automata/gen/LEMMA_LIBRARY.md`.
- Order-4 frontier: `docs/ORDER4_MISS_ELIMINATION_PLAN.md` and the 2026-08-29
  result summaries.
- Current benchmark numbers and rails: `../CLAUDE.md`; historical numbers stay
  in dated result files rather than being recopied here.

Package it with:

```powershell
.\stage2\solver\package_solver.ps1
```

The packaging script minifies to a temp file, checks the 500,000-byte cap, and only then swaps the result into `stage2/submissions/`; it removes a stale `__pycache__` and then asserts the directory holds nothing but `solver.py`, because the official Solo runner refuses to run otherwise. It used to wipe the directory *before* building, so a failed build left no artifact at all — and the directory is gitignored, so there was no copy to fall back on (fixed 2026-08-13).

Before upload or playground testing, run `docs/playground-preflight.md`. It captures the single-file contract, the code-only raw TRUE boundary rails, official proxy LLM behavior, the local no-key caveat, failure classification, the small positive-token parity runner, and the wide public playground-equivalent sweep helper.

See `docs/smoke-tests.md` for the latest local Python, official Solo, Lean, and Windows harness status.
Use `docs/solver-route-ledger.md` and `docs/motif-cards/` before changing a route, and use `docs/cleanup-manifest.md` before touching scratch artifacts.
Use `../theory/TEORTH_WORKFLOW.md`, `../theory/TEORTH_NOTES.md`, and `../theory/tools/README.md` for graph/proof-page/paper mining workflows.

## Next Engines

The next-engine queue is intentionally maintained in the audit addendum at the
top of `docs/LATEST_HANDOFF.md`. This README is a stable navigation page, not a
second backlog or metrics ledger.

For the latest compressed handoff, read `docs/LATEST_HANDOFF.md`.
