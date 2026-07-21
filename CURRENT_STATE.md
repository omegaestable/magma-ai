# Current State

This is the short-lived operational truth for the Stage 2 lab. Update it when the active solver, harness snapshot, validation evidence, or upstream rules change.

Last updated: 2026-07-20.

## Stage

- Active competition: SAIR Equational Theories Stage 2.
- Deadline: August 31, 2026, 23:59 AoE.
- Submission artifact: one `solver.py` file, <= 500 KB.
- Preferred track focus: Marathon first, with shared logic for Solo.
- Proof standard: official Lean 4 judge acceptance.

## Current Artifacts

- Official harness snapshot: `vendor/stage2-official/` at upstream commit `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Active solver scaffold: `stage2/solver/solver.py`.
- Packaged submission: `stage2/submissions/solver.py`, last packaged at `226676` bytes on 2026-07-20 (still well under 500 KB).
- Self-verifying LLM dev loop: `stage2/experiments/dev_true_loop.py` (+ `analyze_true_loop.py`). Runs real problems through gpt-oss via OpenRouter with a repair loop and verifies every candidate with the local Lean judge. Dev-only; see `stage2/results/2026-07-20-llm-true-loop-and-prompt-v3.md`.
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
4. Escalates unresolved Solo/Marathon rows through the official LLM proxy when the runner provides an LLM path and a positive token budget; repo validation no longer uses `--budget-tokens 0` Marathon runs. The `PROMPT` is chain-primary (2026-07-20 rewrite): it leads with the guided-chain DSL, states the row is almost-certainly TRUE so the model stops guessing FALSE tables, forbids `simp`/`aesop`/`grind`, and warns ◇ is non-associative/non-commutative. Solo runs up to `LLM_MAX_ROUNDS=6` repair rounds and feeds parse-level rejects back via `{solver.feedback}`.
5. Keeps the Marathon TRUE LLM boundary narrow: solver-owned `rewrite_chain` / `guided_chain` outputs only, with raw TRUE Lean disabled for that lane. The guided-chain per-edge prover was strengthened (`LLM_GUIDED_CHAIN_MAX_DEPTH=8`, budget `1.0 s`) so the solver bridges the model's coarser waypoints.
6. Allows raw TRUE `code` in Solo/debug parsing when it is a complete Lean file (helper decls above `submission` allowed; legacy `proof`/`proof_body` unsupported). `sanitize_lean_code` no longer requires the literal `intro G _ h` shape — the local judge is the correctness gate, so the pre-filter only checks banned tokens, the import allowlist, size, and that `submission` is declared.
7. Searches FALSE finite witnesses via named compact tables, structured families, affine/linear families, quadratic families, dualized witnesses, and bounded `Fin 2..3` enumeration.
8. Current named witness set includes the recent `S4D`, `S4E`, and `S5D` additions.
9. Emits FALSE certificates with `finOpTable` and `decideFin!`; larger `Fin 7+` tables use `set_option maxRecDepth 20000`.
10. Caches repeated term metadata and path/context helper work in the solver hot paths.

## Best Evidence

Latest archived public Marathon baseline, from the post-witness refresh before the final heartbeat/path-helper optimization patch and before the grind rollback:

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

- Current package pass produced `stage2/submissions/solver.py` at `138939` bytes, still well below the 500 KB limit.
- Active TRUE boundary rails were cleaned up on 2026-05-25: helper-bearing full-file `code` payloads are accepted, and legacy `proof` / `proof_body` payloads are rejected as unsupported.
- 2026-05-25 cleanup smoke: official Solo no-key `sample_20 = 15/20` and official Solo no-key `sample_200 = 169/200`.
- Official harnesses passed on 2026-05-25: Solo harness had no failing buckets; Marathon harness passed `25/25` with Lean available.
- Bounded proxy transport smoke passed on 2026-05-25: Solo `1/1` with `llm_calls=1`; Marathon `1/1` with `89/4096` tokens used.
- Cleanup removed repo-side generated `__pycache__` directories; `.venv/` and scratch evidence were left in place.
- Earlier closure-route dedupe via `_closure_route_impl` preserved `normal_100 = 74/100` historical Marathon behavior.
- Route profile on `normal_100`: `74` deterministic candidates, `26` skips, `49.925s`.
- Selected 27-row fallback reproduction: three `evaluation_extra_hard_false_*` rows now accepted by `false:witness:S4C`; the other 24 reproduce Solo fallback `TRUE` plus judge `incorrect`.
- Exact grind ledgers reconcile to `34 accepted / 433 incorrect`.
- Accepted-grind fixture with heartbeat cap: historical discovery evidence only; the active solver no longer exposes this route.
- Compact witness fixture: `8/8` accepted.
- Positive-token LLM parity on two unresolved TRUE rows reached the official proxy paths: Solo `llm_calls=2`, Marathon `llm_calls=1`, Marathon `tokens_used=7208`; promotion still blocked by judge rejection / rejected LLM output.
- 2026-05-30 TRUE red-flag positive-token Marathon after trimming raw/grind TRUE behavior: `2/13` accepted, `11` LLM calls, `22764` tokens, and `0` incorrect submissions. The remaining proposals were rejected before judge submission by solver-owned validation.
- 2026-05-30 official `normal_100` positive-token Marathon guardrail with Lean on PATH: `75/100` accepted, `25` not attempted, `47419` tokens used, and no incorrect submissions.
- 2026-05-30 official `hard1` positive-token mixed-lane Marathon after enabling checked FALSE table proposals and fixing zero-second budget handling: `39/69` accepted, `30` not attempted, `30` LLM calls, `240164` tokens used, and no incorrect submissions.
- Wide public hard-set local readiness now has a dedicated playground-equivalent helper: `stage2/experiments/run_playground_public_sweeps.py` packages the single-file solver, applies the published `3600 s` / `65536 token` per-problem budget model, requires nonzero LLM usage, and writes combined gap-analysis summaries.
- Python syntax/editor diagnostics and packaged submission syntax checks pass.

Full public validation of the optimized package after the grind rollback is pending. Historical non-grind accepted count from the previous public refresh is `1167/1669`; use positive-token LLM evidence, not grind, to recover TRUE frontier coverage.

## Durable Session Outputs

- `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`
- `stage2/experiments/run_positive_token_sweeps.py`
- `stage2/experiments/analyze_marathon_run.py`
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
- `stage2/results/2026-05-30-positive-token-mixed-lane-resume.md`

## Operational Notes

1. Treat `tmp_stage2_smoke/` as scratch. Promote only concise dated summaries under `stage2/results/`.
2. Do not hardcode public benchmark ids into solver policy. Pasted row lists and grind ledgers are diagnostic fixtures only; promote generalized proof or witness families.
3. The vendored Solo harness has local OpenRouter provider-normalization drift; call it out before treating local positive-token proxy output as upstream-clean.
4. For runner-equivalent certificate debugging, use the official runner or `verify_answer(_to_judge_problem(problem), raw_answer)`. Direct `verify_answer(problem, ...)` omits runner proof policy.
5. Judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr, summaries, or ledgers.
6. Local `OPENAI_API_KEY` or `OPENROUTER_API_KEY` errors are transport/setup issues, not submitted-solver protocol failures. Repo-owned probe/parity entrypoints load process env first, the ignored root `.env` second, and legacy Windows User env fallback last.
7. Marathon validation with `--budget-tokens 0` is banned for active guardrails and promotion. LLM readiness requires positive-token proxy calls, nonzero Marathon token usage, and classified failures.
8. Solo fallback `TRUE INCORRECT` rows and Marathon `not_attempted` rows can be the same unresolved deterministic gap under different runner policies.
9. Treat `proof` and `proof_body` as retired local TRUE boundary shapes. The only raw TRUE payload rail is complete Lean source in `code`, with helper declarations allowed above `submission`.
10. The vendored official README still contains a stale tactic-body `proof` example. Treat that as upstream doc drift unless an explicit harness sync changes the canonical contract.

## Immediate Next Work

0. TOP PRIORITY (from the 2026-07-20 session): the LLM chain loop works (75% accepted on solvable TRUE rows) but gpt-oss-120b cannot crack the deterministic-skip frontier at low reasoning (0/18 normal, 0/20 mixed), and a big-budget deterministic closure only cracks 1/20. Best next lever: a **hybrid** — have the LLM propose candidate instantiation/middle terms and feed them into the deterministic bidirectional closure pool (`_closure_proof_expr_impl` / `absorption_term_pool`). The model is good at *which terms matter*, the solver at *exact chains*. Also try a medium-reasoning frontier sweep via `dev_true_loop.py`. See `stage2/results/2026-07-20-llm-true-loop-and-prompt-v3.md`.
1. Fix remaining fallback rows by adding reusable TRUE proof templates, finite witness families, or judged LLM certificate quality; do not special-case ids.
2. Run broader no-loss validation for the refactored closure helper, especially hard TRUE closure fixtures and the full public sets.
3. Fill the route fixture backlog in `stage2/docs/solver-route-ledger.md` before risky refactors.
4. Use positive-token official/proxy Marathon guardrails only; do not run `--budget-tokens 0` sweeps as active validation.
5. Keep HF mirror sweeps separate from public evidence.

## Non-Goals

1. Do not edit archived Stage 1 cheatsheets as active solver work.
2. Do not promote any certificate template without official judge acceptance.
3. Do not rely on Teorth theorem imports unless the official judge allowlist explicitly permits them.
4. Do not treat local secrets, network access, or repo-local imports as available to submitted solver code.
