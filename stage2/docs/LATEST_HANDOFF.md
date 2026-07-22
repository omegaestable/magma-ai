# Latest Handoff

Updated: 2026-07-21

This is the short team-memory note for the current Stage 2 solver state. Use the result files for detailed evidence and `tmp_stage2_smoke/` only for raw artifacts.

## 2026-07-21 session (most recent)

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
- Packaged artifact: `stage2/submissions/solver.py`, ~251 KB (limit 500 KB).
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

1. Keep the new LLM rails fixed: solver-owned TRUE rewrite/guided chains, verified FALSE finite tables, no Marathon raw TRUE Lean, and no local reintroduction of proof-body wrapping.
2. Continue held-out TRUE work one unseen structural family at a time; next hard80 row is `evaluation_hard_0072` (`eq1_id=86`, `eq2_id=1009`).
3. For extra-hard, first 120 rows are clean; inspect skips after row 120 from `tmp_stage2_smoke/2026-05-23-eval-extra-hard200-after-square-twist-profile.jsonl`.
4. Fix remaining fallback rows by adding reusable TRUE proof templates, finite witness families, or judged LLM certificate quality; do not special-case ids.
5. Run broader no-loss validation for the refactored closure helper and May 23 routes, especially hard TRUE closure fixtures and the full public sets.
6. Improve unresolved TRUE proof quality; the LLM proxy works, but current outputs are still rejected by the solver or judge.
7. Run a full public positive-token validation when budget allows: `normal`, `hard1`, `hard2`, and `hard3` against the current packaged solver.
8. Before upload or promotion, rerun `stage2/docs/playground-preflight.md` and the adversarial solver review checklist.

## Scratch Discipline

- `tmp_stage2_smoke/` is scratch. Promote only concise dated summaries under `stage2/results/`.
- Consult `stage2/docs/cleanup-manifest.md` before deleting or moving scratch artifacts.
- Do not hardcode public benchmark ids in solver policy. Pasted row lists are regression fixtures and diagnostics only.
- Judge answer JSON must contain exactly `verdict` and `code`; route labels belong in stderr, ledgers, or summaries.
