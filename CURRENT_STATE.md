# Current State

This is the short-lived operational truth for the Stage 2 lab. Update it when the active solver, harness snapshot, validation evidence, or upstream rules change.

Last updated: 2026-07-23 (session 2, playground `TRUE INCORRECT` triage).

## Read This First (2026-07-23, session 2)

A real playground Solo run returned eight `TRUE INCORRECT` rows at 400–630 s
each, all submitting the `fallback:unsolved_grind` certificate; seven were
labelled FALSE, where that verdict can never be accepted. Detail:
`stage2/results/2026-07-23-s9a-witness-gate-and-fallback-evidence.md`.

- **`LARGE_WITNESS_SHAPE_KEYS` is deleted.** It pinned the 9-element named
  witness `S9A` to the exact `(eq1, eq2)` pair it was discovered on. All seven
  FALSE rows share `eq1_id = 168` (central groupoid) with different goals, so
  the gate hid the only witness the solver had for them — and `S9A` refutes
  all eight. Ungating cost **0.021 ms/problem**. **Never gate a sound witness
  on a full equation-pair shape**: it is a hardcoded benchmark id (Operational
  Note 2), and it fails *closed* on a route that should fail open.
- **HF `754/800 → 783/800`** (+30 / −1 diffed by row id, all 30
  `false:witness:S9A`); **official sets unchanged row-for-row** at
  `1617/1669`, TRUE `789`; **0 oracle failures** across 2,469 audited rows.
  `hf_evaluation_extra_hard`: `170/200 → 200/200`, `185.3 s → 24.7 s`.
- **`Fin 9` `decideFin!` certificates are real-judge validated** — 5/5
  `accepted` via `judge.verify.verify_answer`, 14–16 s warm (judge cap 120 s),
  462 bytes (cap 10 KB). This shape had no prior judge evidence.
- **A failed FALSE search is not evidence of TRUE unless it looked.**
  `hypothesis_models_seen()` counts models of `eq1` actually inspected; on an
  `Eq168` row it is `2`, because orders ≤ 3 and every canned family contain
  **zero** models of that law. `run_solo` now emits
  `fallback:skip_no_model_evidence` and submits nothing rather than guessing
  `true` when the count is `0`.
- **Closed**: `evaluation_extra_hard_0190`, previously logged as an open FALSE
  miss with "no witness ≤ 4 exists" (correct — it lives at order 9).
  **Still open**: `evaluation_hard_0116` (TRUE, `models_seen = 3691`).
- **Noise amendment**: `evaluation_hard_0178` flipped solved/skip/solved across
  three runs of identical code. Budget-marginal TRUE routes are not run-to-run
  stable; diff row ids, never TRUE totals alone.

## Read This First (2026-07-22, session 4)

A real playground Solo run surfaced 13 `TRUE INCORRECT` + 1 `ERROR`. All 14
were reproduced and root-caused; see
`stage2/results/2026-07-22-playground-failure-fixes.md`. Non-negotiables now
built into the solver:

- **ERROR class eliminated**: Solo parses `budget.timeout_seconds`, sets a
  global hard deadline every engine deadline clamps to, banks an insurance
  judge status before the LLM loop, and always submits a final fallback
  (now a grind cert — no wrong-answer penalty exists). A **memory guard**
  (default cap 1600 MB, `MAGMA_MEMORY_CAP_MB`) models the 2048 MB sandbox:
  deep-tier closures measured 5–17 GB RSS locally, which means the
  playground was OOM-killing them. The guard is armed only in the
  Solo/Marathon entry points.
- **`true:narrow_grind` is demoted** behind the kernel-verified engines: the
  official judge rejected its cert on a shape the local judge accepts. Treat
  "local Lean accepted a grind proof" as non-evidence for the cloud judge.
- **New TRUE power**: `enumerated_lemma_library()` (~600 small laws) and
  `lemma_chain_bootstrap_route` (multi-hop: free CP-rule helpers + iterative
  harvest + pivot-or-direct-goal). Certificates are multi-`have` chain
  proofs; the offline kernel verifies them (`lemma_chain` shape, multi-
  hypothesis `ProofKernel`). 8 of the 14 playground misses now emit
  judge-accepted certs at the `fast` tier.
- **FALSE misses 0093/0123/0190 have no order ≤ 4 witness** (DFS-exhausted);
  larger orders still open.

## Read This First (2026-07-22, session 3)

0. **Three new TRUE routes shipped** — `true:universal_identity`,
   `true:projection_bootstrap`, `true:lemma_bootstrap` — taking official TRUE
   rows `659 → 706`. All rest on one fact worth internalising: **proof-search
   cost scales with goal size, so a small law that implies the goal can be
   reachable when the goal is not.** The LLM lane can now propose such a lemma
   too (`{"verdict":"true","lemma":"..."}`); the solver proves it and the
   kernel checks it, so nothing the model says is trusted. Detail:
   `stage2/results/2026-07-22-universal-identity-route-and-cache-bound.md`.
1. There is an **offline correctness gate**: `pytest stage2/tests` (273
   tests, ~27 s). It proof-checks certificates with an independent kernel and
   model-checks every TRUE verdict, with no Lean required.
   `package_solver.ps1` refuses to package if it fails. See
   `stage2/tests/README.md`.
1b. **Spot-check harness** (new 2026-07-22): `stage2/experiments/spotcheck.py`
   runs randomized balanced batches (default 5 TRUE + 5 FALSE per source) across
   the 8 distinct benchmark sets **and** an `etp` source drawn from the
   Equational Theories Project matrix (`data/exports/`, ~22M validated labelled
   pairs the solver has never been trained on). Any mistake it catches — wrong
   verdict, unsound certificate, or crash — is auto-pinned to the git-tracked
   `stage2/fixtures/spotcheck_failures.jsonl` and replayed forever by
   `test_spotcheck_regressions.py` in the gate above. Skips are safe (coverage,
   not accuracy). First run: **1,189 distinct rows, 100% accuracy, 0 mistakes**
   (2026-07-22 session 3), plus a heavy Fin4 sweep of the one model-check-only
   surface. Run it every session; a coverage ledger steers each batch toward
   untested rows (`--pure-random` to disable). Design: `stage2/docs/spotcheck.md`;
   evidence: `stage2/results/2026-07-22-spotcheck-baseline-and-soundness-sweep.md`.
2. **The old baselines in this file were stale by ~280 rows.** Measured
   `1487/1669` on the official sets (was documented `1201/1669`), with **zero
   oracle failures across 2,689 problems**. Numbers below are updated.
3. **HF evaluation sets are now first-class evidence.** They caught 29 routes
   that look dead on the official sets but are live there; never make a
   deletion or refactor decision without running them.
4. **Do not bulk-delete "unused" routes.** Subsumption by a general engine is
   not a deletion licence: several subsumed routes are cheap high-volume fast
   paths whose removal would push rows onto the expensive CP engine.
5. **The `PROMPT` used to forbid counterexample tables** while the parser
   verified them, so the LLM answered "true" on 47/50 genuinely-FALSE rows
   (0% FALSE accuracy). Fixed. If you touch `PROMPT`, keep it consistent with
   `candidate_from_llm_text_with_reason`, which accepts and re-verifies
   `verdict:false` tables.
6. **Never run LLM calls and certificate verification in the same
   `ThreadPoolExecutor`** — verification is CPU-bound and the GIL serialises
   it. `llm_balanced_eval.py` is the reference two-phase shape (threads for
   network, processes for verification): ~10x faster.
7. Full detail: `stage2/results/2026-07-21-correctness-harness-and-budget-scaling.md`.

## Stage

- Active competition: SAIR Equational Theories Stage 2.
- Deadline: August 31, 2026, 23:59 AoE.
- Submission artifact: one `solver.py` file, <= 500 KB.
- Preferred track focus: Marathon first, with shared logic for Solo.
- Proof standard: official Lean 4 judge acceptance.

## Current Artifacts

- Official harness snapshot: `vendor/stage2-official/` at upstream commit `6805e2323018fbd8a85f41ca09fc33d74d5a02a5`.
- Active solver scaffold: `stage2/solver/solver.py`.
- Packaged submission: `stage2/submissions/solver.py`, last packaged at `333007` bytes on 2026-07-23 session 2 (gate: 196 passed, 2 skipped; still well under 500 KB).
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

## Effort Scaling (new 2026-07-21)

The engines were tuned as if wall-clock were scarce and used roughly **1%** of
the available budget: `marathon_per_problem_budget` was hard-capped at `4.0 s`
and the critical-pair closure at `8.0 s`, while Marathon's reference
configuration affords ~`1800 s` per problem.

`EFFORT_TIERS` + `set_effort()` now scale time *and* search caps together
(a budget sweep showed both bind; widening one alone leaves rows unclaimed).
Solo and Marathon pick a tier from their real budget via
`effort_for_seconds()`; `fast` reproduces the previous behaviour exactly.

| Tier | CP time | frontier | fills | pool | depth |
| --- | ---: | ---: | ---: | ---: | ---: |
| `fast` | 8 s | 2600 | 1200 | 16 | 4 |
| `standard` | 60 s | 11959 | 3960 | 22 | 4 |
| `deep` | 176 s | 29900 | 7920 | 26 | 5 |

The Marathon deterministic pass is capped at `MARATHON_DETERMINISTIC_SHARE`
(0.6) of the run so the hungrier engines cannot starve the LLM lane.

## Current Solver Capability

The active solver is deterministic-first and skips unresolved rows rather than submitting speculative certificates.

1. Handles official Marathon and Solo I/O.
2. Emits TRUE certificates for reflexive problems, singleton/collapse implications, exact substitutions, projection-boundary laws, bridge/constancy chains, bounded rewrite chains, absorption closure, deep absorption, equational closure, **derived critical-pair closure**, and **LLM hybrid seeded closure**.
3. Has no active broad `true:grind` fallback after playground error-rate failures; old grind ledgers are historical discovery evidence only.
4. Escalates unresolved Solo/Marathon rows through the official LLM proxy when the runner provides an LLM path and a positive token budget; repo validation no longer uses `--budget-tokens 0` Marathon runs. The `PROMPT` is chain-primary (2026-07-20 rewrite): it leads with the guided-chain DSL, states the row is almost-certainly TRUE so the model stops guessing FALSE tables, forbids `simp`/`aesop`/`grind`, and warns ◇ is non-associative/non-commutative. Solo runs up to `LLM_MAX_ROUNDS=6` repair rounds and feeds parse-level rejects back via `{solver.feedback}`.
5. Keeps the Marathon TRUE LLM boundary narrow: solver-owned `rewrite_chain` / `guided_chain` outputs only, with raw TRUE Lean disabled for that lane. The guided-chain per-edge prover was strengthened (`LLM_GUIDED_CHAIN_MAX_DEPTH=8`, budget `1.0 s`) so the solver bridges the model's coarser waypoints.
6. Allows raw TRUE `code` in Solo/debug parsing when it is a complete Lean file (helper decls above `submission` allowed; legacy `proof`/`proof_body` unsupported). `sanitize_lean_code` no longer requires the literal `intro G _ h` shape — the local judge is the correctness gate, so the pre-filter only checks banned tokens, the import allowlist, size, and that `submission` is declared.
7. Searches FALSE finite witnesses via named compact tables, structured families, affine/linear families, quadratic families, dualized witnesses, and bounded `Fin 2..3` enumeration.
7b. Falls back to `local_model_counterexample`, a randomized repair search over
   Cayley tables (`Fin 4..6`), run **after** the TRUE routes so solved rows pay
   nothing. Gated by `table_is_counterexample`, so it cannot emit an unsound
   witness. Worth `+7` rows on the official sets.
8. Current named witness set includes the recent `S4D`, `S4E`, and `S5D` additions.
9. Emits FALSE certificates with `finOpTable` and `decideFin!`; larger `Fin 7+` tables use `set_option maxRecDepth 20000`.
10. Caches repeated term metadata and path/context helper work in the solver hot paths.

## Best Evidence

Current measured baseline (2026-07-23 **session 2**, `fast` effort tier,
offline oracles; regenerate with `stage2/experiments/audit_corpus.py --all`):

| Set | Solved | 2026-07-23 s1 (egg) | 2026-07-22 s4 |
| --- | ---: | ---: | ---: |
| `normal` | `989/1000` | `989/1000` | `984/1000` |
| `hard1` | `64/69` | `64/69` | `64/69` |
| `hard2` | `177/200` | `177/200` | `172/200` |
| `hard3` | `387/400` | `387/400` | `381/400` |
| **Total** | **`1617/1669`** | `1617/1669` | `1601/1669` |

Official TRUE count: **`789`**, unchanged from session 1 and **identical row
for row** (the session-2 fix targets FALSE witnesses, and the `Eq168` family
lives in the HF sets).

HF evaluation sets: **`783/800`** (was `754/800`), TRUE `383`. The `+30 / −1`
is diffed by row id: all 30 gains are `false:witness:S9A` on
`hf_evaluation_extra_hard` (`170/200 → 200/200`, `185.3 s → 24.7 s`); the one
loss is wall-clock noise on a budget-marginal `projection_bootstrap` row, not
a code effect.

Zero oracle failures. Evidence:
`stage2/results/2026-07-23-s9a-witness-gate-and-fallback-evidence.md`,
`audit-2026-07-23-s9a.json`, `audit-hf-2026-07-23-s9a.json`.

`false:witness:S9A` (`Fin 9`, `decideFin!`) is the first cert of that size with
**real Lean judge evidence**: 5/5 `accepted` via `judge.verify.verify_answer`,
14–16 s warm against the judge's `LEAN_TIMEOUT_SECONDS = 120`, 462 bytes
against `MAX_FALSE_CERT_BYTES = 10_000`.

**Compare TRUE counts, not solved counts.** The FALSE search is wall-clock
bounded, so solved totals carry a run-to-run noise band of roughly ±7 on the
official sets at this tier — the 2026-07-21 session quoted `1487` from one run
while its own stored `audit-2026-07-21.json` says `1480`. The TRUE column is
stable and is the number to quote for a route change.

Frontier by ground-truth label (before the model finder): TRUE `706/819`
(113 missed, was 160), FALSE `828/850`. The frontier remains TRUE-heavy.

The 2026-07-22 gain (**+47 official TRUE**) comes from three new routes —
`true:universal_identity`, `true:projection_bootstrap`, `true:lemma_bootstrap`
— all exploiting one fact: **proof-search cost scales with goal size, so a
small law that implies the goal can be reachable when the goal is not.** See
`stage2/results/2026-07-22-universal-identity-route-and-cache-bound.md`.

This is **offline** evidence (proof kernel + finite-model oracles), an upper
bound on judge acceptance. A cloud judge sweep is still required before
promotion. The superseded pre-2026-07-21 archived Marathon baseline was
`1201/1669` with `34` accepted `true:grind` rows.

Answer-kind totals for that baseline:

- `false:finite`: `811` accepted.
- `true:certificate`: `356` accepted.
- `true:grind`: `34` accepted, `433` incorrect. This is now historical discovery evidence, not deployable promotion evidence.
- Remaining public misses by labels: `429` TRUE and `39` FALSE.

Latest local regression evidence after the final optimization/refactor patch:

- Current package pass (2026-07-22 session 2) produced `stage2/submissions/solver.py` at `277918` bytes, still well below the 500 KB limit.
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

0. **SHIPPED 2026-07-22 session 4**: Solo hard-deadline + memory guard +
   insurance judge call (ERROR class eliminated); `narrow_grind` demotion;
   enumerated lemma library + multi-hop `lemma_chain` route (+67 official
   TRUE, +22 HF TRUE, zero losses). See
   `stage2/results/2026-07-22-playground-failure-fixes.md`.
1. Open playground rows: TRUE `normal_0582` (trivializer — ETP says
   Eq1923 ⇒ x = y; chain still can't harvest a first helper), `hard2_0178`,
   `evaluation_normal_0040`; FALSE `hard2_0093`/`hard2_0123`/
   `evaluation_extra_hard_0190` (no witness ≤ 4 exists — try ETP
   explicit-ancestor countermodel tables, which need fetching upstream).
2. Rerun the playground simulation to confirm the field results match the
   local evidence (expected: the 8 fixed rows accept; 0 ERRORs).
3. Fix remaining fallback rows by adding reusable TRUE proof templates,
   finite witness families, or judged LLM certificate quality; do not
   special-case ids.
4. Use positive-token official/proxy Marathon guardrails only; do not run
   `--budget-tokens 0` sweeps as active validation.
5. Keep HF mirror sweeps separate from public evidence.

## Non-Goals

1. Do not edit archived Stage 1 cheatsheets as active solver work.
2. Do not promote any certificate template without official judge acceptance.
3. Do not rely on Teorth theorem imports unless the official judge allowlist explicitly permits them.
4. Do not treat local secrets, network access, or repo-local imports as available to submitted solver code.
