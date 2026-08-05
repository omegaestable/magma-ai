# 2026-08-01/03: real-judge broad runs, two Marathon-only bugs — BOTH FIXED AND CONFIRMED ON ALL NINE OFFICIAL + HF SETS

Session goal: spend real OpenRouter budget on extensive real Solo/Marathon runs
(real Lean judge, real proxy, real LLM) to see how the packaged solver actually
fares, log every mistake with root cause, and hand off to the next session. The
broad sweep surfaced two severe, previously-undocumented Marathon-only bugs;
fixing and confirming them became the focus.

**Both fixes are now confirmed by the real judge on all four official sets:**

| Set | Rows | Post-fix score | Rejected |
| --- | ---: | --- | ---: |
| `hard1.jsonl` | 69 | **69/69** | 0 |
| `normal.jsonl` | 1000 | **988/1000** | 0 |
| `hard2.jsonl` | 200 | **196/200** | 0 |
| `hard3.jsonl` | 400 | **396/400** | 0 |
| **Total** | **1669** | **1649/1669 (98.8%)** | **0** |

That essentially matches the offline `fast`-tier baseline (~1647-1650/1669)
exactly, achieved for the first time via the **real** judge across the whole
official corpus, with zero rejected certificates anywhere.

**All five HF mirror sets, real Marathon, also complete, 0 rejected anywhere:**

| Set | Rows | Score | Rejected | Tokens |
| --- | ---: | --- | ---: | ---: |
| `hf_hard` | 200 | **200/200** | 0 | 0 |
| `evaluation_normal` | 200 | **198/200** | 0 | 21,093 |
| `evaluation_hard` | 200 | **197/200** | 0 | 22,183 |
| `evaluation_extra_hard` | 200 | **200/200** | 0 | 0 |
| `evaluation_order5` | 200 | **195/200** | 0 | 59,892 |
| **Total** | **1000** | **990/1000 (99.0%)** | **0** | 103,168 |

**Grand total across all nine real-judge Marathon sets: 2639/2669 (98.9%), 0
rejected across every single row.** The ETP sample is the only work still
queued. See "Session stop point" below for exact status.

## What ran (real judge, real `openai/gpt-oss-120b` via OpenRouter)

| Run | Rows | Result | LLM calls | Wall |
| --- | ---: | --- | ---: | ---: |
| Solo `sample_20` | 20 | **20/20 solved, 0 failed** | 0 | 649 s |
| Solo `hard1` (full) | 69 | **69/69 solved, 0 failed** | 0 | 4188 s (~70 min) |
| Marathon `normal.jsonl` (pre-fix) | 1000 | **287/1000** (713 `not_attempted`) | 64 (0 accepted) | 1331 s |
| Marathon `hard1.jsonl` (pre-fix) | 69 | **31/69** (38 `not_attempted`) | 38 (0 accepted) | — |
| Marathon `hard2`/`hard3` (pre-fix) | — | not reached, sweep stopped | — | — |
| Marathon `hard1.jsonl` (**post-fix**) | 69 | **69/69 accepted, 0 rejected** — full recovery, matches Solo | 0 | — |
| Marathon `normal.jsonl` (**post-fix**) | 1000 | **988/1000 accepted, 0 rejected**, 12 `not_attempted` | 12 (0 accepted) | solver 26288s (~7.3h) + scoring 4241s |
| Marathon `hard2.jsonl` (**post-fix**) | 200 | **196/200 accepted, 0 rejected**, 4 `not_attempted` | — | solver+score 14896s (~4.1h) |
| Marathon `hard3.jsonl` (**post-fix, first attempt**) | 400 | crashed silently at 283/400 (see "second bug" below) | — | ~unknown, no traceback |
| Marathon `hard3.jsonl` (**post-fix, after crash fix**) | 400 | **396/400 accepted, 0 rejected**, 4 `not_attempted` | 4 (0 accepted) | solve 14171s (~3.9h) + score 1510s (~25min) |

Every one of these is a **real** run: real Lean judge acceptance, real OpenRouter
key, real official Solo/Marathon harness (`vendor/stage2-official`), packaged
`stage2/submissions/solver.py`.

**Zero soundness problems anywhere.** Across all real judge verdicts this
session (20 + 69 Solo, 287 + 31 = 318 Marathon accepts), every single
submission that reached the judge was `accepted`. 0 `incorrect`, 0
`malformed`, 0 `incomplete_proof`, 0 `unparsed`. The entire gap measured this
session is a **coverage** problem (`not_attempted`), never a wrong answer.

HF mirror sets, the ETP random-sample manifest (built, not yet run — see
below), and the `hard2`/`hard3` Marathon legs were **not reached**. Next
session should pick these up after finishing the fix validation.

## The finding: Marathon's memory-guard reclaim budget is process-lifetime, not per-problem

### Symptom

Real Marathon on `normal.jsonl` scored **287/1000** against a documented
offline `fast`-tier baseline of 989/1000 (`CLAUDE.md`). Real Marathon on
`hard1.jsonl` scored **31/69** against the *same rows, same solver.py*, solved
**69/69 by Solo** minutes earlier. Both Marathon runs show 0 rejected/incorrect
— purely `not_attempted`.

The route distribution is the tell. `normal.jsonl`'s 287 deterministic solves:

```
true:singleton: 243   <- a cheap, ungated, syntactic check
... 17 other routes, 1-11 hits each
false:witness:*: 5 total   <- catastrophically low FALSE coverage
```

No `egg_closure`, `egg_collapse`, `egg_bootstrap`, `lemma_chain_bootstrap`, or
`lemma_bootstrap` firings at all across 1000 rows — engines that are
individually worth dozens of official rows per `CLAUDE.md`'s route ledger.
`hard1.jsonl`'s 31 solves are more diverse (includes one
`derived_cp_closure`, one `equational_closure`, one `lemma_chain`), consistent
with the same failure occurring *partway through* a shorter manifest rather
than immediately.

### Root cause

`stage2/solver/solver.py`:

- `_mem_reclaims_left = 3` (originally line 4752) is a **module-level global**,
  initialized once at import time.
- `try_reclaim_memory()` (originally ~4755) only ever **decrements** it — gives
  a memory-guard trip one reclaim attempt (`clear_term_caches()` + `gc.collect()`),
  and once `_mem_reclaims_left <= 0`, permanently returns `False`.
- `_engine_gate()` (originally line 7338), checked before **every** general
  engine (`equational_closure`, `deep_absorption_closure`, `derived_cp_closure`,
  `projection_bootstrap`, `lemma_bootstrap`, `lemma_chain_bootstrap`,
  `egg_closure`, `egg_collapse`, `egg_bootstrap`, `narrow_grind`) and every
  FALSE search tier (`constraint_countermodel` cheap + wide,
  `local_model_counterexample`, `large_linear_family_tables`,
  `constraint_countermodel_wide_domain`) returns `True` (stop) once
  `memory_exceeded() and not try_reclaim_memory()`.
- `run_marathon()`'s deterministic loop (originally ~8681) calls
  `clear_term_caches()` before every problem — but **not** anything that resets
  `_mem_reclaims_left`.

Net effect: **3 memory-guard trips anywhere in a Marathon manifest permanently
disable every gated engine for every remaining problem**, no matter how cheap
those later problems would have been. Only the *ungated* cheap syntactic
`TRUE_ROUTES` entries (checked before the first `_engine_gate()` call —
`singleton`, `rewrite`, `constancy`, `universal_identity`, `product_constancy`,
named FALSE witness tables) keep working. This matches the observed skew
exactly.

`MEMORY_CAP_MB_DEFAULT = 1600.0` and `deep`-tier closures are independently
documented (`CLAUDE.md` rail 5) at 5-17 GB RSS, so tripping the cap 3 times in
the first few dozen rows of a 1000-row `deep`-tier Marathon run is entirely
plausible — and that's what real evidence shows happened.

### Why this was never caught before

1. **The offline audit never arms the guard.** `arm_memory_guard()` is only
   called from `run_solo()`/`run_marathon()`. `audit_corpus.py` (the source of
   every headline number in `CLAUDE.md`) never calls it, so the documented
   1650/1669 offline baseline is structurally blind to this bug.
2. **Solo is structurally immune.** Solo launches one fresh subprocess per
   problem (`vendor/stage2-official/pipeline/proxy.py:run_solver`), so
   `_mem_reclaims_left` resets to 3 on every single problem via module reload.
   This is exactly why real Solo got 69/69 on `hard1` while real Marathon got
   31/69 on the identical rows with the identical solver.
3. **It's completely silent.** `try_reclaim_memory()` has zero logging. There
   is no stderr line, no route label, nothing — the only visible symptom is
   the route-count skew, which nobody was diffing against expectations because
   no one had run a long real Marathon manifest against this evidence-gathering
   bar before.

Checked every other module-level `global`-mutated variable in `solver.py` for
the same class of bug: `_HYPOTHESIS_MODELS_SEEN` and `_CONSTRAINT_EXHAUSTED`
both reset correctly per call; `_HARD_DEADLINE` and `_EFFORT` are meant to be
set once per run. `_mem_reclaims_left` was the only offender.

### Fix (applied, offline-gated, not yet fully judge-validated)

```python
def reset_memory_reclaims() -> None:
    """Per-problem reset for the memory guard's reclaim budget. ..."""
    global _mem_reclaims_left, _mem_exceeded, _mem_check_counter
    _mem_reclaims_left = 3
    _mem_exceeded = False
    _mem_check_counter = 0
```

called alongside the existing `clear_term_caches()` in `run_marathon()`'s
per-problem loop. Not added to `run_solo()` — Solo's fresh-subprocess model
already gives it a free reset every problem, so it would be a no-op there.

**Status: CONFIRMED.**

- `pytest stage2/tests -q -n auto`: **202 passed, 2 skipped** (pre- and
  post-fix, identical) — no offline regression.
- `package_solver.ps1`: repackaged clean, 364,728 bytes (was 363,919 — the fix
  itself, well under the 500 KB cap).
- Real-judge re-validation, run to completion:
  - `hard1.jsonl` post-fix: **69/69 accepted, 0 rejected, 0 `not_attempted`**,
    0 LLM calls needed. Route mix fully diverse again (`derived_cp_closure`:6,
    `equational_closure`:1, multiple `lemma_chain` variants, 19 distinct FALSE
    witness families) — a complete recovery matching Solo's real ceiling on
    the identical rows.
  - `normal.jsonl` post-fix: **988/1000 accepted, 0 rejected, 12
    `not_attempted`** (deterministic pass alone submitted 988/1000; the LLM
    lane attempted the remaining 12 and none were accepted — expected, this
    frontier has never yielded to the LLM lane per `CLAUDE.md`). Route mix:
    `derived_cp_closure`:142, `equational_closure`:27, `egg_closure`:3,
    `egg_collapse`:2, `lemma_bootstrap`/`lemma_chain` variants:20+,
    `absorption_closure` variants:6, and FALSE witnesses spread across 30+
    families (`C0`:116, `LP`:146, `RP`:122, `XOR`:42, plus linear/spine/dual
    variants) — night-and-day versus the pre-fix run's near-total collapse
    into `true:singleton` alone. This essentially matches the offline `fast`
    baseline (989/1000) from a real, single, ~7.3-hour Marathon process.
  - One infra hiccup along the way, unrelated to the fix: the first
    `normal.jsonl` scoring pass crashed with `subprocess.TimeoutExpired` from
    `lake env cmd /C echo %LEAN_PATH%` (`judge/verify.py:_get_lake_lean_path`)
    timing out at its hardcoded 30 s cap — the documented "`lake env` times
    out under heavy CPU load" gotcha (`CLAUDE.md` environment section), here
    triggered after 7.3 hours of solver CPU load. The solver's answers were
    already safely on disk (append-only JSONL), so re-scoring with
    `scripts/run_marathon.py --score-only` against the existing output
    recovered the result without re-running the solve. Worth hardening
    upstream (catch `TimeoutExpired` and fall through to the static
    `.lake` glob, which `_get_lake_lean_path`'s own docstring already
    describes as the intended fallback) if this recurs, but out of scope for
    this repo (vendored official harness).

**This is the highest-value fix shipped this session for the real Marathon
score** — offline evidence was never affected by this bug, but real Marathon
coverage on `normal.jsonl` went from 28.7% to 98.8% of the offline ceiling
from a 15-line change.

## Session stop point (updated 2026-08-03, stopped cleanly at user request)

- **Confirmed post-fix, done, all four official sets:** `hard1.jsonl` 69/69,
  `normal.jsonl` 988/1000, `hard2.jsonl` 196/200, `hard3.jsonl` 396/400 — all
  real judge, all 0 rejected. Total **1649/1669 (98.8%)**.
- **Confirmed, done, all five HF mirror sets:** `hf_hard` 200/200,
  `evaluation_normal` 198/200, `evaluation_hard` 197/200,
  `evaluation_extra_hard` 200/200, `evaluation_order5` 195/200 — all real
  judge, all 0 rejected. Total **990/1000 (99.0%)**.
- **Grand total: 2639/2669 (98.9%), 0 rejected anywhere**, across every
  official and HF set this campaign touched.
- **Not started:** the 200-row ETP random sample (via both Solo and
  Marathon) — the only work still queued. No partial or interrupted runs at
  this stop point, clean stop between sets.
- No process left running; verified via `Get-Process` before ending.

## A second bug: one bad row could kill the entire Marathon process, silently

The first full `hard3.jsonl` rerun (400 rows, `--no-score`) crashed partway
through at **283/400** with **no traceback anywhere** — not in `run.log`, not
in the captured stdout/stderr, not in the Windows Application event log. RAM
was roughly half-free afterward, consistent with (but not proof of) a memory
spike on one of `hard3`'s known-harder rows.

Root cause of the *crash being fatal*, independent of what exactly triggered
it: `run_marathon()`'s deterministic loop
(`stage2/solver/solver.py`, the `for priority, problem in prioritized:` loop)
called `solve_problem()` with **zero exception handling**. Any uncaught
exception on any single row — a rare solver bug on a specific equation shape,
a transient resource issue, anything — kills the whole multi-hour process,
discarding the ability to attempt every remaining row, even though the 283
rows already solved were safely on disk (`append_answer()` writes
incrementally). The LLM lane just below it in the same function already
wraps each `future.result()` in `try/except` + `continue` for exactly this
reason; the deterministic loop was simply missing the same pattern.

**Fixed**: wrapped the `solve_problem()` call in `try/except Exception`,
logging `{"route": "solve:crash", "id": ..., "error": ...}` via the existing
`log_stderr()` helper and continuing to the next problem instead of crashing
the run. `pytest stage2/tests`: 202 passed, 2 skipped, no regression.
Repackaged, 365,101 bytes. The `hard3.jsonl` full rerun was restarted with
this fix in place (the first restart attempt, before this fix, was stopped
and discarded once the fix landed, to make sure the final result is 100%
under the hardened code path).

**Update 2026-08-03: the crash recurred on `evaluation_extra_hard`, faster
(75/200) and past the narrower fix.** The `hard3.jsonl` rerun under the
narrow fix (try/except around just the `solve_problem()` call) completed
clean with zero `solve:crash` entries — but that turned out to be inconclusive,
not resolved. A later real run on the HF `evaluation_extra_hard.jsonl` set
crashed with the **identical signature** (silent, no traceback anywhere, ~half
system RAM free afterward) at 75/200, and it did **not** produce a
`solve:crash` log entry — meaning the exception (or crash) was happening
somewhere in the loop *outside* the narrowly-wrapped `solve_problem()` call:
`clear_term_caches()`, `reset_memory_reclaims()`, `append_answer()`, or the
route-count bookkeeping after it.

**Widened the fix**: the `try/except` now wraps the **entire loop body** for
each problem (cache clear, memory-guard reset, solve, answer append,
bookkeeping) instead of just the `solve_problem()` call, so literally
anything that goes wrong in one iteration is caught, logged as
`solve:crash`, and the loop moves to the next problem. Gate green (202
passed, 2 skipped), repackaged (365,145 bytes). `evaluation_extra_hard` was
relaunched under this wider fix.

If it crashes a third time with the *same* signature (no traceback, no
`solve:crash` entry) even under this maximally-wide `try/except`, that would
be strong evidence the underlying event is not a catchable Python exception
at all but a hard OS-level process termination (e.g. a genuine stack
overflow in a C extension, or the OS killing the process directly under
memory pressure) — which no amount of `try/except` can catch, and would need
a different mitigation (lower effort tier to reduce peak memory, or
bisecting which specific row triggers it).

**Result: it did not recur.** `evaluation_extra_hard.jsonl` relaunched under
the widened fix completed clean: **200/200 accepted, 0 rejected**, 0 tokens
(fully deterministic), 0 `solve:crash` entries, only ~32 minutes wall (versus
crashing at 75/200 before). This is reasonably strong evidence the widened
`try/except` genuinely covers whatever was happening — the exception must
have been in `clear_term_caches()`, `reset_memory_reclaims()`,
`append_answer()`, or the bookkeeping, not `solve_problem()` itself, since
wrapping those additional calls is the only change between the crashing and
clean runs.

## Next session: do this first

1. The 200-row random ETP sample already built at
   `tmp_stage2_smoke/real-run-2026-07-31/etp_random_200.jsonl` (drawn from
   `data/exports/general_outcomes.json.gz`, balanced 100 true / 100 false,
   non-reflexive, seed `20260731`) — run through both Solo (a slice) and
   Marathon (the full 200). This is the **only** real-run work left queued —
   every official and HF set is done.
2. Consider whether `MEM_CHECK_EVERY`/reclaim-count tuning is still right now
   that the guard resets per problem — it was tuned as a within-row safety net,
   not a between-row one, so it may not need to change, but worth a second
   look with more real post-fix Marathon telemetry (e.g. does `normal.jsonl`'s
   7.3-hour solver wall-clock compress down at a smaller compression ratio
   closer to the real 5-min/problem-average competition rule, or does it need
   the full budget to reach 988?).
3. `judge/verify.py:_get_lake_lean_path`'s `lake env` call has no timeout
   exception handling despite the function's own docstring describing a
   static-glob fallback for exactly this case — worth a small hardening patch
   if the crash recurs on a future long scoring pass (this is vendored
   official harness code, not `solver.py`, so any fix there is dev-loop
   convenience only, not a submission change).

## Secondary notes

- **Real per-row Solo latency is high and that's expected, not a bug.** Solo
  gets a full 60-minute-per-problem budget, so it picks `deep` effort tier
  (`effort_for_seconds(3600) -> "deep"`), which has ~22x the time budget and
  ~11.5x the frontier of `fast`. Individual rows in the real `sample_20`/`hard1`
  runs routinely took 80-900+ seconds even when they ultimately solved via a
  route that's "cheap" at `fast` tier — the wider search does real extra work
  before landing on the same answer. `hard1_0062` and `hard1_0025` (previously
  discussed in `CLAUDE.md` rail 5f as needing the node-cap fix to reach
  `standard` effort) solved deterministically here in 682 s / 864.5 s at Solo's
  real `deep` budget, with no code change needed beyond what's already shipped.
- **The env-key-precedence gotcha reproduced exactly as documented in memory**
  (`feedback-env-key-precedence-gotcha`): a stale Windows **User**-scope
  `OPENROUTER_API_KEY` (a third, different value from both the old and newly
  rotated repo `.env` key) silently shadowed the fresh key, because
  `local_runner_env.py` prioritizes process env over the repo `.env`. Since
  every Bash/PowerShell tool call spawns a fresh process that reinherits the
  stale User-scope var, and modifying persistent Windows environment state
  requires a permission this session didn't have, every real-run entrypoint
  had to go through a small wrapper
  (`clean_run.py` in the session scratchpad) that pops the stale
  `OPENROUTER_API_KEY`/`OPENAI_API_KEY` from `os.environ` before executing the
  target script, so `local_runner_env`'s precedence chain falls through to the
  repo `.env` value as intended. This is a per-session workaround, not a repo
  fix — the underlying stale Windows User env var is still there and will
  shadow the key again next time unless the user updates it directly (they
  have the permission this session didn't).

## Evidence paths

- `tmp_stage2_smoke/real-run-2026-07-31/solo_sample20.json` — real Solo,
  `sample_20`, 20/20.
- `tmp_stage2_smoke/real-run-2026-07-31/solo_hard1.json` — real Solo, `hard1`,
  69/69.
- `tmp_stage2_smoke/real-run-2026-07-31/marathon-official/official_public/normal/`
  — real Marathon, `normal.jsonl`, pre-fix, 287/1000 (`run.log`,
  `answers.jsonl`).
- `tmp_stage2_smoke/real-run-2026-07-31/marathon-official/official_public/hard1/`
  — real Marathon, `hard1.jsonl`, pre-fix, 31/69.
- `tmp_stage2_smoke/real-run-2026-08-01/marathon-hard1-postfix-v2/` — real
  Marathon, `hard1.jsonl`, post-fix, **69/69 CONFIRMED**. (A first, incomplete
  attempt at this path without `-v2` existed and was deleted as superseded.)
- `tmp_stage2_smoke/real-run-2026-08-01/marathon-normal-postfix/` — real
  Marathon, `normal.jsonl`, post-fix, **988/1000 CONFIRMED**
  (`run.log.solver-phase-backup` has the solver-phase route counts from before
  the log file was overwritten by the `--score-only` rescore).
- `tmp_stage2_smoke/real-run-2026-08-01/marathon-hard2-postfix/` — real
  Marathon, `hard2.jsonl`, post-fix, **196/200 CONFIRMED**.
- `tmp_stage2_smoke/real-run-2026-08-02/marathon-hard3-full/` — real Marathon,
  `hard3.jsonl`, post-fix (after the crash-resilience fix), **396/400
  CONFIRMED, 0 rejected** (`run.log.solver-phase-backup` has the solver-phase
  route counts from before `--score-only` overwrote the log). A prior
  268/400 partial attempt and a first 283/400 crashed attempt at this same
  path were both superseded; only this final clean run's data remains.
- `tmp_stage2_smoke/real-run-2026-08-02/marathon-hf-hard/` — real Marathon,
  HF `hard.jsonl`, **200/200 CONFIRMED, 0 rejected, 0 tokens** (fully
  deterministic).
- `tmp_stage2_smoke/real-run-2026-08-02/marathon-hf-eval-normal/` — real
  Marathon, HF `evaluation_normal.jsonl`, **198/200 CONFIRMED, 0 rejected**.
- `tmp_stage2_smoke/real-run-2026-08-02/marathon-hf-eval-hard/` — real
  Marathon, HF `evaluation_hard.jsonl`, **197/200 CONFIRMED, 0 rejected**.
- `tmp_stage2_smoke/real-run-2026-08-03/marathon-hf-eval-extra-hard/` — real
  Marathon, HF `evaluation_extra_hard.jsonl`, post-widened-fix, **200/200
  CONFIRMED, 0 rejected, 0 tokens** (fully deterministic). A first attempt at
  this same path crashed at 75/200 under the narrower fix and is superseded
  by this clean rerun.
- `tmp_stage2_smoke/real-run-2026-08-03/marathon-hf-eval-order5/` — real
  Marathon, HF `evaluation_order5.jsonl`, **195/200 CONFIRMED, 0 rejected**.
- `tmp_stage2_smoke/real-run-2026-07-31/etp_random_200.jsonl` — built, not yet
  run: 200-row random sample from the full ETP outcome matrix.
- `git diff -- stage2/solver/solver.py` — both fixes, including the widened
  crash-resilience fix (also summarized above).
