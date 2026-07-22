# Latest Handoff

Updated: 2026-07-22

This is the short team-memory note for the current Stage 2 solver state. Use the result files for detailed evidence and `tmp_stage2_smoke/` only for raw artifacts.

## 2026-07-22 session 2 (most recent)

Focus: executed starters 1 and 2 from the session below, plus a third route the
theory produced. All shipped. Full detail:
`stage2/results/2026-07-22-universal-identity-route-and-cache-bound.md`.

**Headline: official TRUE rows `659 → 706` (+47), official solved
`1480 → 1534`, HF solved `707 → 727`. Zero oracle failures across all 2,689
problems.**

One idea drives all three new routes: **proof-search cost scales with goal
size, so a small law that implies the goal can be reachable when the goal is
not.** A projection law (`a ◇ b = a`) is the extreme case — it collapses the
theory, closing any goal whose two sides share a boundary variable, while being
the smallest non-trivial equation there is.

- **`true:universal_identity` (starter 2, solved).** The missing algebra: from
  `x = x ◇ A(ȳ)` (`x ∉ A`), every `A(ā)` is a right identity; instantiating
  `A`'s *own* variables with an identity element `E` collapses `A` to a bare
  variable, which upgrades the hypothesis to the left projection law. Mirror
  shape gives right projection. **+14 official / +4 HF TRUE.** Certificates are
  in the kernel-checkable `exact_expr` shape.
- **`true:projection_bootstrap` (new).** When the algebra fails, point the
  existing critical-pair closure at the *projection lemma* as its goal instead
  of the real goal. It lands in **milliseconds** on rows where the same engine
  cannot prove the goal at any budget. 30 firings. Gated by a free syntactic
  check (`projection_from_lemma_goal_proof` returns `None` unless a projection
  law could close the goal), and placed **last** in `solve_problem`.
- **`true:lemma_bootstrap` (new).** Same move over a six-entry library of small
  laws. 16 firings, **all via `a = b`** — it generalises the syntactic
  `singleton_route` into "the closure *proves* eq1 forces a one-element magma".
  The other five entries earned nothing but cost nothing (the cheap gate
  rejects them), which is the design point.
- **LLM lemma lane.** `{"verdict":"true","lemma":"a ◇ b = a"}` (or `"lemmas"`)
  is now accepted and documented in `PROMPT`. The model supplies only *which
  law to aim at*; the solver proves the lemma from eq1, the goal from the
  lemma, and the kernel re-checks both. See the LLM findings below.
- **`oracles.py` strengthened, not bypassed.** The `have hlem : …` shape used
  to classify as `other` (model-check only). New `check_true_lemma_certificate`
  reads the lemma statement back out of the certificate and runs `ProofKernel`
  twice — lemma body against eq1, goal body against the stated lemma — so a
  builder that proves one law and applies another cannot pass. Wired into both
  `test_golden.py` and `audit_corpus.py`.
- **Control run: 16 of the 19 rows route 1 wins are unreachable at `standard`
  effort** (26-145 s/row on the pre-change solver); the other 3 cost 27-56 s and
  are now microseconds. New coverage, not re-labelled work.
- **Term caches bounded (starter 1, shipped).** `clear_term_caches()` clears all
  13 module-level `@lru_cache(maxsize=None)` term utilities once per problem in
  `run_marathon()`. Measured on `hard2`: without clearing 15.4 M cached entries
  after 50 problems, 25.8 M after 100, still climbing (the mechanism behind this
  morning's 11.2 GB RSS); with clearing the peak is flat at 4.18 M across all
  200 rows. Kept unbounded (not `maxsize=N`) so the hot path stays fast;
  clearing between problems is free because problems essentially never share
  `Term` tuples.
- **Real-LLM result — first accepted LLM TRUE proofs in this project, but the
  frontier still holds.** `llm_balanced_eval.py --per-class 20
  --unresolved-only`, real tokens, gpt-oss-120b: 5 accepted TRUE proofs, **all
  via `llm:true:lemma`**, 0 via chain/guided_chain, 0 wrong verdicts. Against
  0 LLM TRUE accepts in each of the three prior sessions. **But all 7 correct
  rows were rows the deterministic lane already solves; on the 17 genuinely
  unresolved rows the LLM scored 0.** The +47 headline is entirely
  deterministic work.
- **The LLM failure mode moved, usefully.** `guided_chain_unproved_or_bad_endpoints`
  is no longer dominant (7); `lemma_not_derivable_from_hypothesis` is (13). Of
  16 parsed proposals, 14 passed the "does this imply the goal" gate — the
  model proposes goal-relevant laws. Attribution of the 13: **6 were
  demonstrably FALSE** (an eq1-model refutes them) and **0 of the 7 survivors
  became derivable with 22x the budget**. So: do *not* raise the LLM lemma
  budget (measured dead), and filter before proving — `lemma_survives_models`
  now rejects refutable lemmas in milliseconds. That filter lost 0 rows, gained
  3, and cut audit wall-clock ~25%.
- All 5 rows in
  `stage2/fixtures/universal_one_sided_identity_misses_2026-07-22.jsonl` are now
  solved and double-verified. Golden regenerated (213 entries / 126 routes);
  `pytest stage2/tests`: **273 passed**. Packaged at 277,918 bytes.
- **The pre-package gate was flaky under CPU load and is now stable.** Two rows
  drifted between interchangeable general closure engines racing a wall-clock
  budget. `test_golden.py` now collapses `absorption_closure` /
  `equational_closure` / `derived_cp_closure` into one family and tolerates a
  bespoke route drifting *onto* a general engine; every other drift, coverage
  loss and soundness check still fails hard. Step-count budgets remain the real
  fix.
- **Read the TRUE column, not the solved column.** Official Δ solved is +53 but
  Δ TRUE is +47 — the difference is FALSE rows flipping on wall-clock timing
  (rail 4 below). Quote +47.

## 2026-07-22 session 1

Focus: hard1/hard2/evaluation_normal deep dive + a real Marathon LLM-lane
simulation (official proxy, positive tokens, gpt-oss-120b). No solver.py
changes shipped. Full detail:
`stage2/results/2026-07-22-hard1-hard2-evalnormal-marathon-session.md`.

- **Real Marathon LLM lane confirmed still near-zero on this frontier.** hard1
  (10 calls), hard2 (51 calls), and evaluation_normal (22 calls) all scored
  identically with and without the LLM lane — real tokens spent
  (129,806 / 791,519 / 263,165), zero accepts across 83 total LLM attempts.
  Dominant reject: `guided_chain_unproved_or_bad_endpoints`, matching the
  2026-05-30 session exactly. This is a solver-side bridging-search
  limitation, not a prompt problem.
- **Deep-tier budget alone (no code change) recovers 4/76 known misses** via
  the existing `derived_cp_closure` engine (`hard2_0120`, `hard2_0154`,
  `evaluation_normal_0096`, `evaluation_normal_0172`), oracle-verified sound.
  The other 72/76 do not yield to more budget — reconfirms the 2026-07-20
  finding that this frontier resists brute-force search scaling.
- **New scalability risk found, not yet fixed**: solver.py's module-level
  `@lru_cache(maxsize=None)` term-utility caches never clear across problems
  within one Marathon process. Observed 11.2 GB RSS / 1086+ CPU-seconds
  partway through a 200-row real run. Fix before any large-N real validation:
  bound the caches or clear them per-problem in `run_marathon()`.
- Found and fixed two session-blocking infra issues along the way: a
  self-inflicted token-budget miscalculation (402 errors), and a genuinely
  invalid/revoked OpenRouter key (401 "User not found") that needed the user
  to rotate — plus a stale-process-env gotcha where the rotated `.env` key was
  shadowed by an old value already set in the shell environment.
- **New TRUE-route lead, not shipped**: a "universal one-sided identity"
  equation family (`x = A(...) ◇ x`) appears in ~9% of TRUE misses; worked out
  by hand that the fact alone doesn't trivially close the goal, so it needs
  real proof derivation next session, not a quick pattern match.

## 2026-07-21 session

Focus: readiness audit across math / AI / software, then act on the biggest gaps.
Full detail: `stage2/results/2026-07-21-correctness-harness-and-budget-scaling.md`.

**Shipped**

- **Offline correctness gate** — `pytest stage2/tests` (262 tests, ~12 s), no Lean
  needed. An independent proof kernel evaluates the Lean grammar the closure/CP
  builders emit and checks each certificate proves exactly `eq2.lhs = eq2.rhs`;
  a finite-model oracle independently refutes unsound TRUE verdicts; mutation
  tests prove the oracles reject corrupted certificates. `package_solver.ps1`
  refuses to package on failure. See `stage2/tests/README.md`.
- **Local-search finite model finder** (`local_model_counterexample`), run after
  the TRUE routes so solved rows pay nothing; gated by `table_is_counterexample`
  so it cannot emit an unsound witness. **+7 rows**.
- **Effort scaling** (`EFFORT_TIERS`, `set_effort`, `effort_for_seconds`). The
  engines were using ~1% of the available clock: `marathon_per_problem_budget`
  was hard-capped at 4 s and the CP closure at 8 s while Marathon affords
  ~1800 s/problem. `fast` reproduces old behaviour exactly.
  `MARATHON_DETERMINISTIC_SHARE=0.6` stops the hungrier engines starving the LLM lane.
- **Prompt/parser fix** — `PROMPT` used to forbid counterexample tables while the
  parser verified them; the model answered "true" on 47/50 FALSE rows (0% FALSE).
  Now it states the search is non-exhaustive and invites a verified table.
- **Guided-chain edge prover** was fixed at 1.0 s; now effort-scaled.

**Measured**

- Zero oracle failures across **2,689 problems** (1,889 official + 800 HF).
- Official sets **1487/1669** (docs previously claimed `1201/1669` — stale by ~280).
  `standard` tier: hard1 60/69, hard2 154/200. This is offline evidence; a cloud
  judge sweep is still required before promotion.
- Frontier by label: TRUE 659/819 (160 missed), FALSE 821/850 (29 missed).
- Real-LLM balanced eval (gpt-oss-120b): baseline 14/100 (TRUE 28%, FALSE 0%),
  **0 wrong verdicts submitted**, 47 verdict errors caught pre-submission.
  After fixes on a 20-row check: TRUE 50%, FALSE 10%, overall 30%.

**Rails learned the hard way**

1. **HF evaluation sets are first-class evidence.** 29 routes look dead on the
   official sets but are live on HF. Never delete or refactor without them.
2. **Subsumption is not a deletion licence.** 35 routes are subsumed by the
   general engines, but several are cheap high-volume fast paths (`true:rewrite`,
   52 rows) whose removal would push rows onto the 8 s CP engine.
3. **File size is not binding** — 251 KB of 500 KB. De-bloat buys maintainability,
   not points. The aggressive-deletion plan was abandoned on evidence.
4. **Route selection is wall-clock nondeterministic**, so a slower eval machine
   can skip rows that solve locally. The golden gate compares engine *families*.
   Step-count budgets remain open.
5. **Never mix LLM calls and certificate verification in one `ThreadPoolExecutor`**
   — verification is CPU-bound and the GIL serialises it. Use the two-phase shape
   in `llm_balanced_eval.py` (threads for network, processes for verify): ~10x.

## 2026-07-20 session

Focus: a self-verifying LLM TRUE-proof loop with `openai/gpt-oss-120b` via OpenRouter.

- New durable tools: `stage2/experiments/dev_true_loop.py` (repair loop: gpt-oss →
  solver chain/parse → **local Lean judge verify** → feed the error back) and
  `stage2/experiments/analyze_true_loop.py`. Dev-only; the shipped solver still only
  reaches the organizer proxy. Secret-safe; prefers the fresh repo `.env` key.
- Solver changes (all shipped, packaged at 226 676 bytes): `PROMPT` rewritten
  chain-primary (stops FALSE-guessing, forbids `simp`/`aesop`/`grind`, warns ◇ is
  non-associative); `sanitize_lean_code` no longer requires literal `intro G _ h`
  (judge is the gate); guided-chain edge prover `LLM_GUIDED_CHAIN_MAX_DEPTH=8`/`1.0 s`;
  `LLM_MAX_ROUNDS=6`; `run_solo` feeds parse rejects back via `{solver.feedback}`.
- Findings: the loop works (A/B on a solvable set: **25% → 75%** accepted; chain
  renderer is reliable) but gpt-oss cannot yet crack the deterministic-skip frontier
  at low reasoning (`0/20` mixed, `0/18` normal); big-budget deterministic closure
  cracks only `1/20`. The model gets endpoints right but botches exact instantiation
  and assumes associativity.
- Next lever: hybrid — LLM proposes middle/instantiation terms that seed the
  deterministic closure pool. Full detail: `stage2/results/2026-07-20-llm-true-loop-and-prompt-v3.md`.

## Current Solver Snapshot

- Active source: `stage2/solver/solver.py`.
- **Before any solver change: run `pytest stage2/tests` (it is also the
  pre-package gate). After an intentional route change, regenerate the golden
  fixture with `stage2/experiments/audit_corpus.py` + `make_golden.py`.**
- Packaged artifact: `stage2/submissions/solver.py`, `277918` bytes (limit 500 KB).
- Submission directory should contain only `solver.py`.
- Historical public no-LLM baseline: `1201/1669` from `stage2/results/2026-05-18-zero-token-public-refresh-after-witness.md`, including `34` now-retired grind wins.
- Active validation policy now forbids `--budget-tokens 0` Marathon guardrails. Use positive-token official/proxy runs and record LLM calls, token usage, and rejection classes.
- Current durable May 21 summary: `stage2/results/2026-05-21-prune-refactor-and-fallback-reproduction.md`.
- Current durable May 23 route expansion summary: `stage2/results/2026-05-23-held-out-structural-route-expansion.md`.
- Current durable May 25 cleanup/smoke summary: `stage2/results/2026-05-25-cleanup-and-smoke.md`.
- Current durable May 30 positive-token mixed-lane summary: `stage2/results/2026-05-30-positive-token-mixed-lane-resume.md`.
- Full public validation after the grind rollback and May 21 refactor is still pending. Do not claim the current package preserves old grind-backed totals until a new full run exists.

## Current Boundary Rails

- Preferred TRUE LLM outputs remain solver-owned `rewrite_chain` or `guided_chain` JSON.
- Marathon LLM may also propose FALSE only as `{"verdict":"false","counterexample_table":[...]}`; the solver checks the table before any judge submission.
- Raw TRUE Lean is disabled in Marathon and remains only a Solo/debug parser rail as `{"verdict":"true","code":"<complete Lean file>"}`.
- The raw `code` field may contain helper theorems, defs, lemmas, namespaces, or notation above `def submission : Goal := ...`.
- Legacy body-only `proof` and `proof_body` payloads are retired from the active local boundary and now reject as `proof_body_unsupported`.
- The vendored official README still contains an older `{"verdict": "true", "proof": "<tactic body>"}` prompt snippet. Treat that as upstream doc drift; the canonical local and judge-facing contract is full Lean source in `code`.

## What Changed This Session

- Retired the broad/raw TRUE Marathon behavior that produced playground errors; Marathon TRUE now accepts only solver-checked chains.
- Updated the LLM prompt for the mixed lane: TRUE proof-chain proposals are still checked locally, and FALSE is allowed only as a finite table that passes `table_is_counterexample`.
- Fixed the false-search deadline checks so a zero-second local profiling budget is honored instead of silently expanding into an unbounded search.
- Replaced the old tokenless sweep/analyzer helpers with positive-token Marathon helpers that fail closed on nonpositive budgets.
- Refreshed the no-network LLM smoke, package artifact, route ledger, LLM motif card, and durable result summaries to match the current rails.

## Latest Regression Evidence

- Python syntax checks passed for source, experiment helpers, and packaged solver.
- Packaged size: `138939` bytes.
- `stage2/experiments/smoke_llm_dsl.py` now accepts helper-bearing full-file TRUE `code` payloads and rejects `proof` / `proof_body` payloads.
- `theory/tools/smoke_problem_sets.py` passed and confirmed public/HF mirror counts.
- 2026-05-25 no-key Solo smoke: `sample_20 = 15/20`, `sample_200 = 169/200`.
- 2026-05-25 bounded proxy smoke: Solo `1/1` with `llm_calls=1`; Marathon `1/1` with `89/4096` tokens used.
- 2026-05-30 official `normal_100` positive-token Marathon guardrail with Lean on PATH: `75/100`, `25` not attempted, `47419` tokens used, no incorrect submissions.
- 2026-05-30 TRUE red-flag positive-token Marathon after raw/grind TRUE trim: `2/13`, `11` LLM calls, `22764` tokens, no incorrect submissions.
- 2026-05-30 official `hard1` positive-token mixed-lane Marathon: `39/69`, `30` not attempted, `30` LLM calls, `240164` tokens used, no incorrect submissions.
- Repo-side generated `__pycache__` directories were removed; `.venv/` bytecode was left alone as ignored local environment state.
- Submission directory cleanliness: only `solver.py`.
- Route profile on public `normal_100` after the May 23 route expansion: `74` deterministic candidates, `26` skips, `47.479s`.
- Held-out hard first 80 after the May 23 route expansion: `76` deterministic candidates, `4` skips, `7.854s`.
- Official Solo harness on `sample_20`: exit `0`, no failing categories.
- Current package has positive-token official guardrail evidence for `normal_100`; broader full-public positive-token validation is still pending.
- Current held-out hard80 TRUE skips after the May route pass: `evaluation_hard_0072`, `evaluation_hard_0074`, `evaluation_hard_0078`, and `evaluation_hard_0080`.

## Selected-Row Reproduction

User-provided labels were normalized by removing the true/false label segment, for example `hard1_true_0065` -> `hard1_0065`.

- Public rows came from `vendor/stage2-official/examples/problems/`.
- Evaluation rows came from `data/hf_cache/`.
- Direct certificate verification used `verify_answer(_to_judge_problem(problem), raw_answer)`, not raw `verify_answer(problem, ...)`.

Broad 27-row direct probe:

- `evaluation_extra_hard_0045`, `evaluation_extra_hard_0043`, and `evaluation_extra_hard_0041` are now solved as `FALSE ACCEPTED` by `false:witness:S4C` in about 4-6 seconds.
- The other 24 listed rows reproduce Solo-style fallback behavior: submitted `TRUE`, judge `incorrect`, error code `LEAN_REJECTED`.
- Direct local timings for fallback rows were about 1.3-3.2 seconds because the probe bypassed live proxy waiting and checked the final fallback directly.

Historical Marathon reproduction on the same manifest, archived before the current positive-token policy, accepted the three `evaluation_extra_hard_false_*` rows via `false:witness:S4C` and left the other `24` rows unresolved. Use it only as fallback-reproduction history.

Scratch artifacts:

- `tmp_stage2_smoke/2026-05-21-fallback-batch-27.jsonl`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-direct-probe.py`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-direct-probe.jsonl`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-zero/summary.json`
- `tmp_stage2_smoke/2026-05-21-fallback-batch-zero/run.log`

## Best Public Evidence

Latest completed official public no-LLM Marathon refresh, before the final heartbeat/path-helper optimization patch and before grind retirement:

| Set | Solved | TRUE | FALSE | Notes |
| --- | ---: | ---: | ---: | --- |
| `normal` | `803/1000` | 305 | 498 | salvaged via isolated `--score-only` after a Lean artifact failure |
| `hard1` | `42/69` | 6 | 36 | clean full lane |
| `hard2` | `92/200` | 16 | 76 | clean full lane |
| `hard3` | `264/400` | 63 | 201 | clean full lane |
| **Total** | `1201/1669` | 390 | 811 | `0` solver tokens |

Answer-kind totals for that baseline:

- `false:finite`: `811` accepted.
- `true:certificate`: `356` accepted.
- `true:grind`: `34` accepted, `433` incorrect; historical discovery evidence only.
- Remaining public misses by labels: `429` TRUE and `39` FALSE.

## Key Lessons

1. Generalize proof and witness families; do not add solver policy keyed to public or evaluation row ids.
2. Selected-row reproduction is useful for diagnosis, but promotion claims need full lanes or focused route fixtures with judge-accepted certificates.
3. Solo fallback `TRUE INCORRECT` rows and positive-token Marathon local LLM rejects can be the same unresolved proof-quality gap viewed through different runner policies.
4. The three `evaluation_extra_hard_false_*` rows appear fixed in the current package. If they failed elsewhere, that evidence likely came from an older package or different upload.
5. `true:grind` was a discovery route, not a deployable strategy. It found `34` public TRUE wins but caused `433` incorrect attempts and is retired from active solver policy.
6. Do not run or cite `--budget-tokens 0` Marathon as active validation; positive-token official/proxy runs are the guardrail lane.
7. Positive-token local LLM evidence must prove official proxy usage: nonzero Solo LLM calls, nonzero Marathon `llm_calls`, nonzero `tokens_used`, and classified failure outcomes.
8. Do not reopen the legacy `proof` / `proof_body` TRUE rail locally. Raw TRUE now means full Lean source in `code`.
9. Full-file TRUE `code` may declare helper theorems, defs, lemmas, namespaces, or notation above `submission`; this is part of the supported local boundary.
10. Treat the stale vendored `proof` example as doc drift unless an upstream sync explicitly changes the judge contract.

## Recommended Next Steps

All three 2026-07-22 session-1 starters are **done**, plus the lemma-library
generalisation and the LLM lemma lane. Remaining, ranked by evidence:

1. **Make small lemmas derivable — the single blocking problem.** Measured
   today: of the lemmas gpt-oss proposed that survive finite-model checking,
   **0 of 7 became derivable with 22x the search budget.** The closure is not
   narrowly missing them; it is structurally unable to reach them, and more
   time provably does not help. This is the same wall as
   `guided_chain_unproved_or_bad_endpoints` (dominant across 3 sessions), but
   now exposed on targets small enough to derive by hand. **Take one of the 7
   and work it out manually** — that is exactly how `universal_identity` was
   found today, and it converted a 3-session dead end into +47 rows.
2. **Mine the lemma library from data.** Five of six library entries earned
   nothing; every win came from `a = b`. Instead of guessing more laws, for
   each unsolved row enumerate small laws that hold in every finite model of
   eq1 *and* imply the goal; recurring ones are evidence-backed candidates.
   Both halves reuse machinery that now exists (`lemma_survives_models`,
   `lemma_applies_to_goal`).
3. **Step-count budgets** instead of wall-clock, so route selection is
   deterministic and the golden gate can go back to strict equality.
4. Re-run the LLM lemma lane after (1) — its ceiling is set by what the closure
   can derive, not by the prompt.

Older items (LLM rails discipline, no raw-TRUE Marathon Lean, no proof-body
rewrapping) remain true as ongoing constraints, not active TODOs — see
"Current Boundary Rails" above.

## Scratch Discipline

- `tmp_stage2_smoke/` is scratch. Promote only concise dated summaries under `stage2/results/`.
- Consult `stage2/docs/cleanup-manifest.md` before deleting or moving scratch artifacts.
- Do not hardcode public benchmark ids in solver policy. Pasted row lists are regression fixtures and diagnostics only.
- Judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr, ledgers, or summaries.
