# 2026-07-21 — Offline correctness harness, model finder, and effort scaling

Session goal: assess Stage 2 readiness across math / AI practices / software
practices, then act on the largest gaps. Everything below is **offline
evidence** (proof kernel + finite-model oracles). The Lean judge runs in the
cloud, so a cloud sweep is still required before promotion.

## Headline

1. **No unsound deterministic routes.** Zero oracle failures across **2,689
   problems** (1,889 official + 800 HF evaluation). The proof-construction
   math is sound; this was the largest unquantified risk.
2. **The documented baseline was badly stale.** Measured `1480/1669` on the
   official sets versus `1201/1669` in `CURRENT_STATE.md` — the critical-pair
   and hybrid work was never credited.
3. **The solver was using ~1% of its wall-clock budget.** Marathon affords
   ~1800 s per problem at the reference configuration; the engines were capped
   at 4 s (FALSE portfolio) and 8 s (critical-pair closure).

## Verdict by pillar

| Pillar | Score | Basis |
| --- | ---: | --- |
| Math / theory | 8.5 | Sound-by-construction proof engine, real KB-lite critical-pair unifier, tasteful FALSE portfolio. Gaps: no reduction order / ordered completion, no true model finder (now partly addressed). |
| AI practices | 8.0 | Chain-primary DSL with solver-side bookkeeping, seeded bidirectional closure, re-verified LLM tables, self-verifying dev loop. Gap: eval model hardcoded while officially TBD. |
| Software practices | 5.5 | Zero Stage-2 tests on 6.3k lines where ~8 shared primitives underwrite every certificate; no regression gate; stale validation. **Addressed this session.** |

## What shipped

### Offline correctness gate (`stage2/tests/`, 254 tests, ~12 s)

- `oracles.py` — an independent term parser/evaluator, a **proof-expression
  kernel** for the grammar the closure/CP builders emit
  (`h t..`, `.symm`, `.trans`, `congrArg (fun t => C)`, `rfl`), and a
  **finite-model oracle**. Shares no code with `solver.py` by design.
- `test_primitives.py` — the shared primitives, plus **mutation tests** that
  prove the oracles reject corrupted certificates (extra hypothesis argument,
  dropped `.symm`, broken `.trans`, corrupted `congrArg` context).
- `test_golden.py` — 202 route-diverse real problems across 120 routes;
  catches coverage loss, engine drift, and soundness loss.
- `package_solver.ps1` now refuses to package on gate failure.

### Local-search finite model finder

Randomized repair search over Cayley tables, run **after** the TRUE routes so
solved rows pay nothing. Every witness is re-checked by
`table_is_counterexample`, so it cannot emit an unsound answer.
**+7 rows** (`1480 → 1487`) for ~4 KB.

### Effort scaling

`EFFORT_TIERS` + `set_effort()`; Solo and Marathon select a tier from their
real budget. Raising a tier widens time *and* search caps together — the sweep
showed both bind, and widening only one leaves rows unclaimed.
`marathon_per_problem_budget` no longer hard-caps at 4 s.

## Evidence

Official sets, `fast` tier (= previous behaviour):

| Set | Solved | Previously documented |
| --- | ---: | ---: |
| `normal` | 934/1000 | 803/1000 |
| `hard1` | 59/69 | 42/69 |
| `hard2` | 150/200 | 92/200 |
| `hard3` | 344/400 | 264/400 |
| **Total** | **1487/1669** | 1201/1669 |

Frontier by ground-truth label: TRUE `659/819` (160 missed), FALSE
`821/850` (29 missed) before the model finder.

HF evaluation sets: `707/800`, zero oracle failures.

Critical-pair budget sweep on 40 TRUE misses:

| Config | Solved | Bottleneck |
| --- | ---: | --- |
| baseline 8 s | 1/40 | 28 timeout / 11 exhausted |
| 60 s | 3/40 | 23 timeout / 14 exhausted |
| 60 s + wider caps | **6/40** | 31 timeout / 3 exhausted |

Both time and search caps bind; widening only one is insufficient.

## Findings that changed the plan

1. **Aggressive de-bloat was wrong.** 29 routes that never fire on the
   official sets *do* fire on the HF evaluation sets — deleting them (as
   originally planned) would have destroyed coverage on the one local
   distribution we did not tune against. Only 3 functions are dead on both.
2. **Subsumption is not a deletion licence.** 35 routes are fully subsumed by
   the general engines, but several are cheap high-volume fast paths
   (`true:rewrite`, 52 rows). Deleting them pushes those rows onto the
   expensive CP engine — a Marathon throughput loss.
3. **File size is not binding.** 251 KB of a 500 KB limit. De-bloat buys
   maintainability, not points; effort was redirected to the frontier.
4. **Route selection is wall-clock nondeterministic.** Which variant wins can
   flip under CPU load, so a slower evaluation machine can skip rows that
   solve locally. The golden gate compares engine families rather than exact
   route labels; converting the engines to step-count budgets remains open.

## Real-LLM balanced evaluation (OpenRouter, gpt-oss-120b)

`stage2/experiments/llm_balanced_eval.py` runs the **shipped** pipeline end to
end against the real model: `solver.PROMPT` -> gpt-oss-120b -> the solver's own
`candidate_from_llm_text_with_reason` -> offline oracles -> ground-truth label.
50 TRUE + 50 FALSE sampled from `normal`/`hard1`/`hard2`.

Baseline (pre-fix prompt, medium reasoning, 100 rows):

| Class | Correct |
| --- | ---: |
| TRUE | 14/50 (28%) |
| FALSE | **0/50 (0%)** |
| **Overall** | **14/100** |
| Wrong verdicts *submitted* | **0** |

The 0% on FALSE was a prompt bug, not a model failure: on **47 of 50** FALSE
rows the model answered "true", because `PROMPT` asserted the row was "almost
certainly TRUE" and explicitly said *"Do not return a counterexample table"* —
while `candidate_from_llm_text_with_reason` has always supported and
re-verified `verdict:false` tables. The prompt forbade the one answer shape
that could win those rows.

The safety net held: 0 wrong verdicts reached submission, and 47 verdict errors
were caught before the judge.

### Fixes

1. **Prompt/parser contradiction.** `PROMPT` and `solver_analysis` now state
   the countermodel search is thorough but *not exhaustive*, and invite a
   verified Cayley table. Zero risk: `table_is_counterexample` re-checks every
   table exhaustively, so a wrong table is discarded and a right one wins a row
   that was previously lost.
2. **Guided-chain edge prover was fixed at 1.0 s** while Solo affords 3600 s.
   Now effort-scaled (`_eff_time`/`_eff_depth`), so bridging the model's coarse
   waypoints gets ~7.5x (standard) or ~22x (deep) longer. This was the dominant
   reject: `guided_chain_unproved_or_bad_endpoints` was 71/86 of all rejects.
3. **Harness throughput bug (mine, not the API's).** LLM calls and CPU-bound
   closure verification shared one `ThreadPoolExecutor`, so the GIL serialised
   the "parallel" workers. Split into phase 1 (network, threads) and phase 2
   (verification, processes), plus parallel deterministic probing during
   sampling. ~10x faster: 20 rows in 157 s versus 30+ min for 100 before.

### After fixes (same 100 rows, same seed, low reasoning, standard effort)

| Class | Before | After |
| --- | ---: | ---: |
| TRUE | 14/50 (28%) | **17/50 (34%)** |
| FALSE | **0/50 (0%)** | **8/50 (16%)** |
| **Overall** | **14/100** | **25/100** |
| Wrong verdicts submitted | 0 | **0** |

The FALSE gain is the substantive one: 8 rows that were previously unwinnable
*by construction*. Still 40 verdict errors caught before submission, zero fatal.

Runtime `646 s` for 100 problems (466 s fetch + 150 s verify) versus 30+ min
before the two-phase split. One straggler call took ~300 s on its own.

### Where the remaining headroom is

`guided_chain_unproved_or_bad_endpoints` is **57 of 75** rejects: the model
proposes plausible waypoints the bridging search cannot close. That is a
solver-side search problem, not a model problem, and it is the next lever —
the effort tiers make more budget available but the search itself needs to be
smarter (see the reduction-order item below).

A secondary cluster, `rewrite_chain_uses_non_goal_variables` (14), is a prompt
issue: the model introduces variables not in the goal.

**Caveat:** ~90% of randomly sampled rows are already solved deterministically,
so these percentages measure the LLM lane *standalone*, not its marginal
contribution to the frontier. Use `--unresolved-only` for the frontier number.

## Open / next

- Cloud judge sweep to convert this offline evidence into accepted counts.
- Step-count budgets for reproducibility (engines currently wall-clock bound).
- Reduction order (LPO-lite) to orient derived rules toward real completion.
- Remaining FALSE misses resist random search (≤1/22 even at 20 s); they
  likely need larger or algebraically structured models.
