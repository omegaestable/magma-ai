# Current State

This is the short-lived operational truth for the Stage 2 lab. Update it when the active solver, harness snapshot, validation evidence, or upstream rules change.

Last updated: 2026-05-25.

## Stage

- Active competition: SAIR Equational Theories Stage 2.
- Deadline: August 31, 2026, 23:59 AoE.
- Submission artifact: one `solver.py` file, <= 500 KB.
- Preferred track focus: Marathon first, with shared logic for Solo.
- Proof standard: official Lean 4 judge acceptance.

## Current Artifacts

- Official harness snapshot: `vendor/stage2-official/` at upstream commit `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Active solver scaffold: `stage2/solver/solver.py`.
- Packaged submission: `stage2/submissions/solver.py`, last packaged at `116670` bytes.
- Latest compressed handoff: `stage2/docs/LATEST_HANDOFF.md`.
- Solver route ledger: `stage2/docs/solver-route-ledger.md`.
- Route motif cards: `stage2/docs/motif-cards/`.
- Non-destructive cleanup manifest: `stage2/docs/cleanup-manifest.md`.
- Latest public refresh summary: `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`.
- Playground preflight checklist: `stage2/docs/playground-preflight.md`.
- Theory workflow, notes, and tools: `theory/TEORTH_WORKFLOW.md`, `theory/TEORTH_NOTES.md`, `theory/tools/README.md`.
- Shared theory/provenance data: `data/exports/` and `data/teorth_cache/`.
- Stage 1 archive: `stage1/`; do not treat it as the active workflow.

## Current Solver Capability

The active solver is deterministic-first and skips unresolved rows rather than submitting speculative certificates.

1. Handles official Marathon and Solo I/O.
2. Emits TRUE certificates for reflexive problems, singleton/collapse implications, exact substitutions, projection-boundary laws, bridge/constancy chains, bounded rewrite chains, absorption closure, deep absorption, and bounded equational closure.
3. Has no active broad `true:grind` fallback after playground error-rate failures; old grind ledgers are historical discovery evidence only.
4. Escalates unresolved Solo/Marathon rows through the official LLM proxy when the runner provides an LLM path and a positive token budget; if Solo remains unresolved it makes a final schema-valid fallback judge call, while zero-token Marathon skips unresolved rows.
5. Searches FALSE finite witnesses via named compact tables, structured families, affine/linear families, quadratic families, dualized witnesses, and bounded `Fin 2..3` enumeration.
6. Current named witness set includes the recent `S4D`, `S4E`, and `S5D` additions.
7. Emits FALSE certificates with `finOpTable` and `decideFin!`; larger `Fin 7+` tables use `set_option maxRecDepth 20000`.
8. Caches repeated term metadata and path/context helper work in the solver hot paths.

## Best Evidence

Latest completed public zero-token Marathon baseline, from the post-witness refresh before the final heartbeat/path-helper optimization patch and before the grind rollback:

| Set | Solved | TRUE | FALSE | Tokens |
| --- | ---: | ---: | ---: | ---: |
| `normal` | `803/1000` | 305 | 498 | 0 |
| `hard1` | `42/69` | 6 | 36 | 0 |
| `hard2` | `92/200` | 16 | 76 | 0 |
| `hard3` | `264/400` | 63 | 201 | 0 |
| **Total** | `1201/1669` | 390 | 811 | 0 |

Answer-kind totals for that baseline:

- `false:finite`: `811` accepted.
- `true:certificate`: `356` accepted.
- `true:grind`: `34` accepted, `433` incorrect. This is now historical discovery evidence, not deployable promotion evidence.
- Remaining public misses by labels: `429` TRUE and `39` FALSE.

Latest local regression evidence after the final optimization/refactor patch:

- Current package pass produced `stage2/submissions/solver.py` at `116670` bytes, still well below the 500 KB limit.
- 2026-05-25 cleanup smoke: official Solo no-key `sample_20 = 15/20`, official Solo no-key `sample_200 = 169/200`, and official zero-token Marathon `normal_100 = 74/100` accepted in `60.6s`.
- Official harnesses passed on 2026-05-25: Solo harness had no failing buckets; Marathon harness passed `25/25` with Lean available.
- Bounded proxy transport smoke passed on 2026-05-25: Solo `1/1` with `llm_calls=1`; Marathon `1/1` with `89/4096` tokens used.
- Cleanup removed repo-side generated `__pycache__` directories; `.venv/` and scratch evidence were left in place.
- Earlier closure-route dedupe via `_closure_route_impl` preserved `normal_100 = 74/100` zero-token Marathon behavior.
- Route profile on `normal_100`: `74` deterministic candidates, `26` skips, `49.925s`.
- Official zero-token Marathon on `normal_100`: `74/100` accepted, `26` not attempted, `0` tokens, `50.5s`.
- Selected 27-row fallback reproduction: three `evaluation_extra_hard_false_*` rows now accepted by `false:witness:S4C`; the other 24 reproduce Solo fallback `TRUE` plus judge `incorrect`, while zero-token Marathon skips them.
- Exact grind ledgers reconcile to `34 accepted / 433 incorrect`.
- Accepted-grind fixture with heartbeat cap: historical discovery evidence only; the active solver no longer exposes this route.
- Compact witness fixture: `8/8` accepted.
- Positive-token LLM parity on two unresolved TRUE rows reached the official proxy paths: Solo `llm_calls=2`, Marathon `llm_calls=1`, Marathon `tokens_used=7208`; promotion still blocked by judge rejection / rejected LLM output.
- Wide public hard-set local readiness now has a dedicated playground-equivalent helper: `stage2/experiments/run_playground_public_sweeps.py` packages the single-file solver, applies the published `3600 s` / `65536 token` per-problem budget model, requires nonzero LLM usage, and writes combined gap-analysis summaries.
- Python syntax/editor diagnostics and packaged submission syntax checks pass.

Full public validation of the optimized package after the grind rollback is pending. Historical non-grind accepted count from the previous public refresh is `1167/1669`; use positive-token LLM evidence, not grind, to recover TRUE frontier coverage.

## Durable Session Outputs

- `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`
- `stage2/experiments/run_zero_token_sweeps.py`
- `stage2/experiments/analyze_zero_token_run.py`
- `stage2/experiments/extract_grind_ledger.py`
- `stage2/experiments/run_playground_parity_llm.py`
- `stage2/experiments/run_playground_public_sweeps.py`
- `stage2/docs/solver-route-ledger.md`
- `stage2/docs/motif-cards/`
- `stage2/docs/cleanup-manifest.md`
- `theory/TEORTH_NOTES.md`
- `stage2/docs/LATEST_HANDOFF.md`
- `stage2/results/2026-05-20-optimization-readiness.md`
- `stage2/results/2026-05-21-prune-refactor-and-fallback-reproduction.md`
- `stage2/results/2026-05-25-cleanup-and-smoke.md`

## Operational Notes

1. Treat `tmp_stage2_smoke/` as scratch. Promote only concise dated summaries under `stage2/results/`.
2. Do not hardcode public benchmark ids into solver policy. Pasted row lists and grind ledgers are diagnostic fixtures only; promote generalized proof or witness families.
3. The vendored Solo harness has local OpenRouter provider-normalization drift; call it out before treating local positive-token proxy output as upstream-clean.
4. For runner-equivalent certificate debugging, use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`. Direct `verify_answer(problem, ...)` omits runner proof policy.
5. Judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr, summaries, or ledgers.
6. Local `OPENAI_API_KEY` or `OPENROUTER_API_KEY` errors are transport/setup issues, not submitted-solver protocol failures. Repo-owned probe/parity entrypoints load process env first, the ignored root `.env` second, and legacy Windows User env fallback last.
7. Zero-token Marathon proves deterministic append-only behavior only and is not a playground-readiness gate; LLM readiness requires nonzero proxy calls, nonzero Marathon token usage, and classified failures.
8. Solo fallback `TRUE INCORRECT` rows and Marathon `not_attempted` rows can be the same unresolved deterministic gap under different runner policies.

## Immediate Next Work

1. Fix remaining fallback rows by adding reusable TRUE proof templates, finite witness families, or judged LLM certificate quality; do not special-case ids.
2. Run broader no-loss validation for the refactored closure helper, especially hard TRUE closure fixtures and the full public sets.
3. Fill the route fixture backlog in `stage2/docs/solver-route-ledger.md` before risky refactors.
4. Treat zero-token sweeps as optional deterministic regression only, not as the active local gate.
5. Keep HF mirror sweeps separate from public evidence.

## Non-Goals

1. Do not edit archived Stage 1 cheatsheets as active solver work.
2. Do not promote any certificate template without official judge acceptance.
3. Do not rely on Teorth theorem imports unless the official judge allowlist explicitly permits them.
4. Do not treat local secrets, network access, or repo-local imports as available to submitted solver code.
